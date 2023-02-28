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


## Manual deployment

```
docker build -t bbpgitlab.epfl.ch:5050/viz/brayns/braynscircuitstudiobackend:manual .
docker push bbpgitlab.epfl.ch:5050/viz/brayns/braynscircuitstudiobackend:manual
```

```
module load unstable
module load apptainer
apptainer pull --dir ~/brayns-circuit-studio-backend/ --disable-cache --docker-login docker://bbpgitlab.epfl.ch:5050/viz/brayns/braynscircuitstudiobackend:manual
```
