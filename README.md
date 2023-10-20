# Brayns Circuit Studio Backend

Brayns Circuit Studio Backend (BCSB) is a backend service for Brayns Circuit
Studio software.


## Installation

Go to the root of the repo.

```bash
cd path/to/braynscircuitstudiobackend
```

Optional (but recommended), create a Python virtual environment (requires Python
installed >= 3.10).

```bash
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

Install for running only:

```bash
pip install -r requirements.txt
pip install .
```

Install for developping (testing and formatting):

```bash
pip install -r requirements-dev.txt
```

## Command line

The package automatically add a script ``bcsb`` to the PATH once installed.

Check usage with:

```bash
bcsb --help
```

Get version with:

```bash
bcsb --version
```

Run with:

```bash
bcsb
```

BCSB package also has an entrypoint:

```bash
python -m bcsb {command line args}
```

## Endpoints

BCSB is a websocket server using a JSON-RPC protocol.

It also supports an HTTP GET to /healthz to perform a healthcheck.

Example request (using some Websocket connector):

```json
{"id": "1", "method": "version"}
```

Possible response:

```json
{
    "jsonrpc": "2.0",
    "id": "1",
    "result": {
        "version": "0.1.0"
    }
}
```

Check available endpoints with:

```json
{"id": "1", "method": "registry"}
```

Check endpoint schema with:

```json
{"id": "1", "method": "schema", "params": {"endpoint": "version"}}
```
