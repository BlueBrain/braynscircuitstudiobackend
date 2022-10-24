# Brayns Circuit Studio Backend

Brayns Circuit Studio Backend (BCSB)
are backend services for Brayns Circuit Studio software.


# Development

For development manual, go [here](development.md).

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

# Quick introduction

Connect to BCSB via Websocket to `wss://backend.braynscircuitstudio.kcp.bbp.epfl.ch/ws/`

```json
{
    "id": "1",
    "method": "start-new-session"
}
```

