# Development

## Running as Docker Compose services

After cloning this repo run `docker-compose up` to start developing.

You may want to customize some environment variables like ports or paths. Refer to `.env-sample` file,
copy and rename it to `.env` so that it will be loaded during compose process.

Then you should be able to connect via Websocket on `ws://127.0.0.1:8000/`
or elsewhere if you changed the default configuration.

## Manually build the image

Manually build the image and push it to Gitlab registry:

```
docker build -t bbpgitlab.epfl.ch:5050/viz/brayns/braynscircuitstudiobackend:manual .
```

Push it

```
docker push bbpgitlab.epfl.ch:5050/viz/brayns/braynscircuitstudiobackend:manual
```

The tag `manual` should be used sporadically for testing/debugging purposes.

## Test the circuit information endpoint

```json
{
    "id": "1",
    "method": "ci-get-general-info",
    "params": {
        "path": "/gpfs/bbp.cscs.ch/project/proj3/TestData/install/share/BBPTestData/circuitBuilding_1000neurons/BlueConfig"
    }
}
```
