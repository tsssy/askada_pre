import os
from datetime import datetime, timezone

import re
from urllib.parse import urlparse

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


@app.post('/api/visit')
def create_visit(payload: VisitIn, request: Request):
    subreddit = (payload.subreddit or '').strip().lower()
    referer = request.headers.get('referer', '')
    referer_host = ''
    referer_url = referer
    if referer:
        try:
            parsed_referer = urlparse(referer)
            if parsed_referer.scheme and parsed_referer.netloc:
                referer_host = f'{parsed_referer.scheme}://{parsed_referer.netloc}'
            else:
                referer_host = parsed_referer.hostname or ''
        except ValueError:
            referer_host = ''
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
        'created_at': datetime.now(timezone.utc)
    })

    display_name = subreddit if subreddit.startswith('r/') else f'r/{subreddit}'

    return {
        'subreddit': display_name,
        'visitor_index': visitor_index
    }
