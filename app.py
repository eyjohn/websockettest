#!/usr/bin/env python

# WS server that sends messages at random intervals

import asyncio
import datetime
import random
import websockets
import http

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
    while True:
        now = datetime.datetime.utcnow().isoformat() + "Z"
        await websocket.send(now)
        await asyncio.sleep(random.random() * 3)

start_server = websockets.serve(ws_handler, "0.0.0.0", 8080, process_request=process_request)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()