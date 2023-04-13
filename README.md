# StreamerAI

## Setup

1. Set OpenAI API Key environment variable via `export OPENAI_API_KEY=<key here>`
2. Set Pinecone API Key environment variable via `export PINECONE_API_KEY=<key here>`
3. `pip install -e .`

## Web Server Usage

`python3 app.py` or `gunicorn app:app --bind 0.0.0.0:$PORT`

## Streamer Usage

1. Start main script `python -m src.streaming.main --room_id '33'`
2. Use testing script to insert comments `python src/streaming/streamchat_fake.py --room_id 33`
3. To use live comments, add `--live` to the main script, like so `python -m src.streaming.main --room_id '33' --live`
