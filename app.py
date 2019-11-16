#!/usr/bin/env python

# WS server that sends messages at random intervals

import asyncio
import datetime
import random
import websockets
import http
import json


async def process_request(path, request_headers):
    print(f"process_request path={path} headers:\n{request_headers}")
    if path == "/websocket":
        return
    elif path == "/healthz":
        return http.HTTPStatus.OK, [], b"OK\n"
    with open("index.html", "rb") as in_file:
        return http.HTTPStatus.OK, [("Content-Type", "text/html")], in_file.read()


async def ws_handler(websocket, path):
    print(f"ws_handler path={path} headers:\n{websocket.request_headers}")

    async def echo():
        async for message in websocket:
            data = json.loads(message)
            if data['event'] == "echo":
                await websocket.send(json.dumps({
                    "time": datetime.datetime.utcnow().isoformat() + "Z",
                    "event": "echo",
                    "message": json.loads(message)['message']
                }))
            elif data['event'] == "sync":
                await websocket.send(json.dumps({
                    "time": datetime.datetime.utcnow().isoformat() + "Z",
                    "event": "sync",
                    "message": json.loads(message)['message']
                }))

    async def time():
        while True:
            await websocket.send(json.dumps({
                "time": datetime.datetime.utcnow().isoformat() + "Z",
                "event": "time"
            }))
            await asyncio.sleep(1)

    await asyncio.gather(echo(), time())

start_server = websockets.serve(
    ws_handler, "0.0.0.0", 8080, process_request=process_request)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
