# JSON-RPC protocol

This backend is a WebSocket server which expects JSON queries from its clients.

Queries must have this type:

```ts
{
    jsonrpc: "2.0"
    id: string
    method: string
    params?: any
}
```

And there are two kind of messages the backend can send to the client: __responses__ and __errors__.

A __response__ is of this type:

```ts
{
    jsonrpc: "2.0"
    id: string
    result: any
}
```

And an __error__ of this type:

```ts
{
    jsonrpc: "2.0"
    id: string
    error: {
        code: number
        message: string
    }
}
```

## Example 1

Suppose a client wants to know the version of the backend.
It will then send this JSON message to it:

```json
{
    "jsonrpc": "2.0",
    "id": "hX47h2bb",
    "method": "version"
}
```

`"id"` is the identifier of the query. It must be unique for the client.
We use it because the communication is asynchronous. That means that the client
will receive the following JSON message at some time
(maybe after it has received other messages):

```json
{
    "jsonrpc": "2.0",
    "id": "hX47h2bb",
    "result": "1.0.0"
}
```

This '"id"' is what tells the client to what query this answer is related.

## Example 2

Now, let's assume the client ask for an unknown entrypoint __foobar__ :

```json
{
    "jsonrpc": "2.0",
    "id": "42",
    "method": "foobar",
    "params": { "name": "status", "value": "RUN" }
}
```

The backend will send (later) this message back:

```json
{
    "jsonrpc": "2.0",
    "id": "42",
    "error": {
        "code": -6,
        "message": "Unknown entrypoint \"foobar\"!"
    }
}
```
