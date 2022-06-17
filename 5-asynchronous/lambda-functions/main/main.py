import random

def handler(event, context):
    print("Event received. Starting...")
    status = bool(random.getrandbits(1))
    print("Random status returns {}".format(status))
    if status:
        return True
    else:
        raise Exception("This is a failed request.")

