from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class CapitalDimension(BaseModel):
    name: str
    weight: float = Field(ge=0.0, le=1.0, default=0.125)
    metric: str = ""
    threshold: Optional[float] = None
    score: float = Field(ge=0.0, le=1.0, default=0.5)
    bloqueio_msg: str = ""


class DimensionRegistry(BaseModel):
    dimensions: dict[str, CapitalDimension] = {}

    def add(self, name: str, weight: float = 0.125, metric: str = "",
            threshold: Optional[float] = None, score: float = 0.5,
            bloqueio_msg: str = "") -> CapitalDimension:
        dim = CapitalDimension(
            name=name, weight=weight, metric=metric,
            threshold=threshold, score=score, bloqueio_msg=bloqueio_msg,
        )
        self.dimensions[name] = dim
        return dim

    def remove(self, name: str) -> None:
        self.dimensions.pop(name, None)

    def get(self, name: str) -> Optional[CapitalDimension]:
        return self.dimensions.get(name)

    @property
    def names(self) -> list[str]:
        return list(self.dimensions.keys())

    def to_dict(self) -> dict:
        return {k: v.model_dump() for k, v in self.dimensions.items()}

    @classmethod
    def from_dict(cls, data: dict) -> DimensionRegistry:
        reg = cls()
        for name, params in data.items():
            reg.add(**params)
        return reg

    @classmethod
    def defaults(cls) -> DimensionRegistry:
        reg = cls()
        reg.add("financeiro", 0.20, metric="mvrv", threshold=3.5)
        reg.add("vivo", 0.15, metric="shannon_h", threshold=1.2,
                bloqueio_msg="Monocultura — Shannon H' < 1.2")
        reg.add("material", 0.10)
        reg.add("social", 0.15, metric="gini", threshold=0.5,
                bloqueio_msg="Plutocracia — Gini > 0.5")
        reg.add("intelectual", 0.15)
        reg.add("experiencial", 0.10)
        reg.add("cultural", 0.10)
        reg.add("espiritual", 0.05)
        return reg
