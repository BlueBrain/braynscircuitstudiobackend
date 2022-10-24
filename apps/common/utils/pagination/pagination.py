from typing import Type, Optional

from channels.db import database_sync_to_async
from django.db.models import QuerySet, Model


@database_sync_to_async
def get_paginated_queryset_results(
    queryset: QuerySet,
    offset: int,
    limit: int = None,
):
    total_results = queryset.count()
    model_class = queryset.model
    slice_start = offset
    slice_end = offset + limit if limit is not None else None
    results = list(queryset[slice_start:slice_end])
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

    @property
    def next_offset(self) -> Optional[int]:
        if self.limit is not None and self.offset + self.limit < self.total_count:
            return self.offset + self.limit
        else:
            return None

    @property
    def prev_offset(self) -> Optional[int]:
        if self.limit is not None and self.offset > self.limit:
            return self.offset - self.limit
        else:
            return None
