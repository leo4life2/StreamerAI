# StreamerAI

## Usage

1. Set OpenAI API Key
2. `pip install -e .`
3. `python3 app.py` or `gunicorn app:app --bind 0.0.0.0:$PORT`

## Testing

1. python -m src.streaming.main --product_index 1 --room_id '33'
2. python src/streaming/streamchat_fake.py 33
