import json


def handler(event, context):
    print(event)
    records = event["Records"]
    for rec in records:
        print("Received {} event for key: {}".format(
            rec["eventName"], rec["dynamodb"]["Keys"]["ID"]))
        if "NewImage" in rec["dynamodb"]:
            print("New value: {}".format(
                json.dumps(rec["dynamodb"]["NewImage"])))
        if "OldImage" in rec["dynamodb"]:
            print("Old value: {}".format(
                json.dumps(rec["dynamodb"]["OldImage"])))
        print("----------")
