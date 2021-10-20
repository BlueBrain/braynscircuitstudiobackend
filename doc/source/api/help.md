# help

```ts
help(): string[]
help(entrypointName: string): string
```

Get some help about the API.

## Without arguments

If called without any arguments, returns the list of available entrypoint names (`string[]`).

## With a `string` argument

If the sole argument is the name of an existing entrypoint, returns its docstring.
If no entrypoint exists with this name, acts like if no arguments were given.
