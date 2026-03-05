"""Common models shared across API domains."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, Field, ConfigDict


class CamundaModel(BaseModel):
    """Base model with camelCase alias support."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda field_name: "".join(
            word.capitalize() if i > 0 else word
            for i, word in enumerate(field_name.split("_"))
        ),
    )


class PageInfo(CamundaModel):
    """Pagination info from search responses."""

    total_items: int | None = None
    start_cursor: str | None = None
    end_cursor: str | None = None


T = TypeVar("T", bound=CamundaModel)


class SearchResult(CamundaModel, Generic[T]):
    """Generic search result wrapper."""

    items: list[T]
    page: PageInfo = Field(default_factory=PageInfo)


class SortOrder(CamundaModel):
    """Sort specification for search queries."""

    field: str
    order: str = "ASC"
