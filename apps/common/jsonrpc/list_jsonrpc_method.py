from common.jsonrpc.jsonrpc_method import JSONRPCMethod
from common.utils.pagination import get_paginated_queryset_results


class ListJSONRPCMethod(JSONRPCMethod):
    async def run(self):
        return await get_paginated_queryset_results(
            self.get_queryset(),
            limit=self.get_request_param("limit"),
            offset=self.get_request_param("offset"),
        )

    def get_queryset(self):
        raise NotImplementedError
