import jwt
import json

def handler(event, context):
    if not "token" in event:
        return "No token"
    token = event["token"]
    key = "test"
    payload = jwt.decode(token, key, algorithms="HS256")
    print(json.dumps(payload))
    return True
