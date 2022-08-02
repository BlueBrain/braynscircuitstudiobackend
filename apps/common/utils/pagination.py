from typing import Type

from channels.db import database_sync_to_async
from django.db.models import QuerySet, Model


@database_sync_to_async
def get_paginated_queryset_results(
    queryset: QuerySet,
    limit: int = 100,
    offset: int = 0,
):
    total_results = queryset.count()
    model_class = queryset.model
    results = list(queryset[offset:limit])
    return PaginatedResults(results, total_results, offset, limit, model_class=model_class)


class PaginatedResults:
    def __init__(
        self,
        results,
        total_count,
        offset,
        limit,
        model_class: Type[Model],
    ):
        self.results = results
        self.total_count = total_count
        self.offset = offset
        self.limit = limit
        self.model_class = model_class

    @property
    def model_type(self):
        return self.model_class.__name__
