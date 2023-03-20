import uuid
import requests
from requests.auth import HTTPBasicAuth

basic_auth = HTTPBasicAuth('test', 'test')
uuid_string = str(uuid.uuid4())

while True:
    message = input("Your message: ")
    response = requests.post(
        "http://127.0.0.1:5000/chat",
        auth=basic_auth,
        json={
            "message": message,
            "conversationIdentifier": uuid_string,
            "retrievalMethod": "embedding_retrieval"
        }
    )
    print(response.json())