
async def do(req_data):
    print("req_data: %s" % (req_data), flush=True)
    print("Got id: %s" % (req_data["id"]))

    return {"whoami": "www"}
