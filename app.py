#!/usr/bin/env python

# WS server that sends messages at random intervals

import asyncio
import datetime
import random
import websockets
import http
import json
import logging

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

connections = set()


async def process_request(path, request_headers):
    logger.info("request path=%s headers:\n%s", path, request_headers)
    if path == "/websocket":
        return
    elif path == "/healthz":
        return http.HTTPStatus.OK, [], b"OK\n"
    with open("index.html", "rb") as in_file:
        return http.HTTPStatus.OK, [("Content-Type", "text/html")], in_file.read()


async def ws_handler(websocket: websockets.WebSocketServerProtocol, path):
    logger.info("connect remote_address=%s:%d path=%s headers:\n%s",
                websocket.remote_address[0], websocket.remote_address[1], path, websocket.request_headers)
    connections.add(websocket)

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
        logger.info("end of messages remote_address=%s:%d path=%s",
                    websocket.remote_address[0], websocket.remote_address[1], path)

    async def time():
        while websocket in connections:
            await websocket.send(json.dumps({
                "time": datetime.datetime.utcnow().isoformat() + "Z",
                "event": "time"
            }))
            await asyncio.sleep(1)
        logger.info("exiting time loop remote_address=%s:%d path=%s",
                    websocket.remote_address[0], websocket.remote_address[1], path)

    async def wait_closed():
        await websocket.wait_closed()
        connections.remove(websocket)
        logger.info("disconnect remote_address=%s:%d path=%s",
                    websocket.remote_address[0], websocket.remote_address[1], path)

    await asyncio.gather(echo(), time(), wait_closed())

start_server = websockets.serve(
    ws_handler, "0.0.0.0", 8080, process_request=process_request)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
