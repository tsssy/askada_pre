# Askada landing + tracker

## Backend

1. Start local MongoDB (default `mongodb://localhost:27017`).
2. Run the API:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 6666
```

Environment variables (optional):
- `MONGODB_URI` (default `mongodb://localhost:27017`)
- `MONGODB_DB` (default `red_user`)

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit:
- `http://localhost:5173/?subreddit=askada`

## Data

MongoDB database: `red_user`
- `visits` collection stores each visit with `subreddit`, `visitor_index`, `referer_host`, and `referer_url`.
- `counters` collection stores per-subreddit sequence counters.
