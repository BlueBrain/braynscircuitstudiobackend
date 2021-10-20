"""Websocket server.

This server will accept only one client and will communicate with
jsonrpc protocol version 2.0.
This is an asynchronous protocol. The client sends a request with a unique ID.
Later the server send back a result with this same ID.
"""
import asyncio
import json
import socket
import traceback
from json import JSONDecodeError
from typing import Any, Dict, List, Optional

import websockets
from entrypoint import EntryPoint


class Server:
    """Websocket server.

    Available entrypoints are given as a list to the constructor.
    Except for the special one "help".
    If "help" is called without any parameter, it will return the
    list of all available entrypoint names (except "help").
    If a name if given as unique parameter, the docstring of this
    entrypoint is returned.
    """

    client = None
    entrypoints: Dict[str, EntryPoint] = {}
    entrypoint_names: List[str] = []

    def __init__(self, entrypoints: List[EntryPoint]):
        """Constructor.

        Args:
            entrypoints: list of available entrypoints.
        """
        self.entrypoint_names = [x.name for x in entrypoints]
        self.entrypoints = dict(zip(self.entrypoint_names, entrypoints))
        self.entrypoint_names.sort()
        print(f"Available entry points: help, {', '.join(self.entrypoint_names)}.")
        host = socket.gethostbyname("localhost")
        port = 4321
        # pylint: disable=no-member
        start_server = websockets.serve(self.__server, "localhost", port)
        print(f"Listening on {host}:{port}")

        # Start and run websocket server forever
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    async def __send(
        self,
        websocket=None,
        query_id: str = None,
        method: str = None,
        result=None,
        err_num: int = None,
        err_msg: str = None,
    ):
        """Send a message in JSON-RPC format.

        Args:
            websocket (WebSocketClientProtocol): if undefined, we use the currently connected client
            query_id (string): id of the request this message is an answer of
            method (string): name of the method we are replying to
            result (any): data produced by the called method
            err_num (int): error code
            err_msg (string): error message
        """
        data = {"jsonrpc": "2.0"}
        if id is not None:
            data["id"] = query_id
        if method is not None:
            data["method"] = method
        if result is not None:
            data["result"] = result
        if err_num is not None:
            data["error"] = {"code": err_num, "message": str(err_msg)}
        websocket = self.client if websocket is None else websocket
        if websocket is None:
            print("[ERROR] No client connected yet!")
            return
        await websocket.send(json.dumps(data))

    async def __callback_success(self, query_id: str, result: Any):
        await self.__send(query_id=query_id, result=result)

    async def __callback_failure(self, query_id: str, code: int, message: str):
        await self.__send(query_id=query_id, err_num=code, err_msg=message)

    async def __server(self, websocket, path):
        send = self.__send
        if self.client is not None:
            await send(
                websocket=websocket, err_num=-1, err_msg="There is already a client connected!"
            )
            return
        self.client = websocket
        print("[LOG] Client connected:", path)
        while True:
            try:
                msg = await websocket.recv()
                print(f"[MSG] {msg}")
                data = json.loads(msg)
                if not isinstance(data, dict):
                    await send(err_num=-2, err_msg="A JSON object was expected!")
                elif "jsonrpc" not in data or data["jsonrpc"] != "2.0":
                    await send(err_num=-3, err_msg="JSON-RPC version 2.0 was expected!")
                else:
                    query_id = None if "id" not in data else data["id"]
                    method = None if "method" not in data else data["method"]
                    params = None if "params" not in data else data["params"]
                    if not isinstance(query_id, str):
                        await send(err_num=-4, err_msg="Invalid format: attribute 'id' is missing!")
                        continue
                    if not isinstance(method, str):
                        await send(
                            err_num=-4, err_msg="Invalid format: attribute 'method' is missing!"
                        )
                        continue
                    if method == "help":
                        await self.__callback_help(query_id, params)
                        continue
                    if method not in self.entrypoints:
                        await send(err_num=-6, err_msg=f'Unknown entrypoint "{method}"!')
                        continue
                    entrypoint = self.entrypoints[method]
                    asyncio.create_task(
                        entrypoint.callback(
                            query_id=query_id,
                            params=params,
                            success=self.__callback_success,
                            failure=self.__callback_failure,
                        )
                    )
            except JSONDecodeError as ex:
                print(f"[ERROR] {str(ex)}")
                await send(
                    err_num=-5,
                    err_msg=f"Invalid JSON at line {ex.lineno} and pos {ex.colno}: {ex.msg}",
                )
            except Exception as ex:  # pylint: disable=broad-except
                print(f"[ERROR] Unknown exception: {str(ex)}")
                print(print(traceback.format_exc()))
                await send(err_num=-9, err_msg="Unknown exception!")

    async def __callback_help(self, query_id: str, entrypoint_name: Optional[str]):
        """Send back API documentation.

        If `entrypoint_name` is not defined or if it is not the name of
        an available entrypoint, we return the list of available entrypoints.
        Otherwise, we return the docstring of the entrypoint.
        """
        if entrypoint_name is None or entrypoint_name not in self.entrypoints:
            await self.__callback_success(query_id, self.entrypoint_names)
        else:
            entrypoint = self.entrypoints[entrypoint_name]
            await self.__callback_success(query_id, entrypoint.__doc__)
