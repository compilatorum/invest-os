from __future__ import annotations

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class EntityType(str, Enum):
    PERSON = "person"
    PROJECT = "project"
    COMMUNITY = "community"
    ORGANIZATION = "organization"
    DAO = "dao"
    FUND = "fund"


class Entity(BaseModel):
    id: str = ""
    type: EntityType = EntityType.PROJECT
    name: str = "unknown"
    metadata: dict = {}

    def capital_score(self, grid) -> float:
        from invest_os.models.schemas import CapitalType
        scores = {}
        for t in CapitalType:
            key = t.value
            scores[t] = self.metadata.get(f"score_{key}", 0.5)
        result = grid.evaluate(scores)
        return result.rhi_estimated


class Person(Entity):
    type: EntityType = EntityType.PERSON
    roles: list[str] = []
    reputation: float = Field(ge=0.0, le=1.0, default=0.5)


class Project(Entity):
    type: EntityType = EntityType.PROJECT
    github_stars: int = 0
    contributors: int = 0
    years_active: float = 0.0


class Community(Entity):
    type: EntityType = EntityType.COMMUNITY
    member_count: int = 0
    governance_participation: float = Field(ge=0.0, le=1.0, default=0.0)


class Organization(Entity):
    type: EntityType = EntityType.ORGANIZATION
    founded_year: int = 2024
    has_audit: bool = False


class DAO(Entity):
    type: EntityType = EntityType.DAO
    tvl: float = 0.0
    voting_enabled: bool = False
    has_sbt: bool = False


class Fund(Entity):
    type: EntityType = EntityType.FUND
    aum: float = 0.0
    strategy: str = ""
    vintage: int = 2024
