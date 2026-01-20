import os
from datetime import datetime, timezone

import re
from typing import Optional
from urllib.parse import parse_qs, urlparse

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pymongo import MongoClient, ReturnDocument

MONGO_URI = os.getenv(
    'MONGODB_URI',
    'mongodb://root:6b8f966a7b0448f8@47.84.177.254:27017/?authSource=admin'
)
DB_NAME = os.getenv('MONGODB_DB', 'red_user')

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
visits = db['visits']
counters = db['counters']

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


class VisitIn(BaseModel):
    subreddit: str = Field(default='unknown', max_length=200)
    source: Optional[str] = Field(default=None, max_length=200)
    page_url: Optional[str] = Field(default=None, max_length=2000)


def _extract_subreddit_from_referer(referer: str) -> str:
    if not referer:
        return ''
    try:
        parsed = urlparse(referer)
        path = parsed.path or ''
    except ValueError:
        return ''

    match = re.search(r'/r/([^/]+)/', path)
    if match:
        return match.group(1)
    return ''


def _extract_source_from_params(params) -> str:
    for key in ('source', 'utm_source', 'ref', 'referrer'):
        value = params.get(key)
        if value:
            return value
    return ''


@app.post('/api/visit')
def create_visit(payload: VisitIn, request: Request):
    subreddit = (payload.subreddit or '').strip().lower()
    referer = request.headers.get('referer', '')
    referer_host = ''
    referer_url = referer
    origin = request.headers.get('origin', '')
    page_url = (payload.page_url or '').strip()
    source_tag = (payload.source or '').strip()
    source_param = ''
    if referer:
        try:
            parsed_referer = urlparse(referer)
            if parsed_referer.scheme and parsed_referer.netloc:
                referer_host = f'{parsed_referer.scheme}://{parsed_referer.netloc}'
            else:
                referer_host = parsed_referer.hostname or ''
        except ValueError:
            referer_host = ''
    if not source_tag:
        source_param = _extract_source_from_params(request.query_params)
        if not source_param and page_url:
            try:
                parsed_page = urlparse(page_url)
                page_params = parse_qs(parsed_page.query or '')
                source_param = _extract_source_from_params({
                    key: values[0] for key, values in page_params.items() if values
                })
            except ValueError:
                source_param = ''
        source_tag = source_param
    if not subreddit or subreddit == 'unknown':
        subreddit = _extract_subreddit_from_referer(referer).strip().lower() or 'unknown'

    counter = counters.find_one_and_update(
        {'_id': subreddit},
        {'$inc': {'seq': 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    visitor_index = counter['seq']

    visits.insert_one({
        'subreddit': subreddit,
        'visitor_index': visitor_index,
        'referer_host': referer_host,
        'referer_url': referer_url,
        'origin': origin,
        'page_url': page_url,
        'source_tag': source_tag,
        'source_param': source_param,
        'created_at': datetime.now(timezone.utc)
    })

    display_name = subreddit if subreddit.startswith('r/') else f'r/{subreddit}'

    return {
        'subreddit': display_name,
        'visitor_index': visitor_index
    }
