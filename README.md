# Brayns Circuit Studio Backend

Brayns Circuit Studio Backend (BCSB)
are backend services for Brayns Circuit Studio software.


# Development

## Running as Docker Compose services

After cloning this repo run `docker-compose up` to start developing. You can limit
the logs to the backend app only by running `docker-compose up app`. Other services
depend on it so they will be launched anyway.

You may want to customize some environment variables like ports or paths. Refer to `.env-sample` file, 
copy and rename it to `.env` so that it will be loaded during compose process.

If everything runs smoothly, you should see following logs:

```
app_1       | Performing system checks...
app_1       | 
app_1       | System check identified no issues (0 silenced).
app_1       | 
app_1       | You have 18 unapplied migration(s). Your project may not work properly until you apply the migrations for app(s): admin, auth, contenttypes, sessions.
app_1       | Run 'python manage.py migrate' to apply them.
app_1       | November 22, 2021 - 12:31:18
app_1       | Django version 3.2.9, using settings 'bcsb.settings'
app_1       | Starting ASGI/Channels version 3.0.4 development server at http://0.0.0.0:8000/
app_1       | Quit the server with CONTROL-C.
app_1       | HTTP/2 support not enabled (install the http2 and tls Twisted extras)
app_1       | Configuring endpoint tcp:port=8000:interface=0.0.0.0
app_1       | Listening on TCP address 0.0.0.0:8000
```

Then you should be able to connect via Websocket on `ws://127.0.0.1:8000/ws/` or
elsewhere if you changed the default configuration.


## Version endpoint

All requests should be sent using JSONRPC 2.0 protocol.

Send following request (using some Websocket connector):

```json
{"id": "1", "method": "version"}
```

and you should receive following answer:

```json
{
    "jsonrpc": "2.0",
    "id": "1",
    "result": {
        "version": "0.1.0"
    }
}
```
