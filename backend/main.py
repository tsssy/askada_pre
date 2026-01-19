import os
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pymongo import MongoClient, ReturnDocument

MONGO_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
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
    subreddit: str = Field(min_length=1, max_length=200)


@app.post('/api/visit')
def create_visit(payload: VisitIn):
    subreddit = payload.subreddit.strip().lower()
    if not subreddit:
        subreddit = 'unknown'

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
        'created_at': datetime.now(timezone.utc)
    })

    display_name = subreddit if subreddit.startswith('r/') else f'r/{subreddit}'

    return {
        'subreddit': display_name,
        'visitor_index': visitor_index
    }
