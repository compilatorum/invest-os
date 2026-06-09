import pytest
from invest_os.entities.base import (
    Entity, EntityType, Person, Project, Community, Organization, DAO, Fund,
)
from invest_os.capitals.grid import CapitalGrid


class TestEntities:
    def test_entity_defaults(self):
        e = Entity()
        assert e.type == EntityType.PROJECT
        assert e.name == "unknown"

    def test_person(self):
        p = Person(name="Alice", roles=["investor", "curator"], reputation=0.8)
        assert p.type == EntityType.PERSON
        assert p.reputation == 0.8

    def test_project(self):
        p = Project(name="Uniswap", github_stars=5000, contributors=100, years_active=4)
        assert p.github_stars == 5000

    def test_community(self):
        c = Community(name="ReFi DAO", member_count=5000, governance_participation=0.3)
        assert c.member_count == 5000

    def test_dao(self):
        d = DAO(name="MolochDAO", tvl=1e7, voting_enabled=True, has_sbt=True)
        assert d.tvl == 1e7
        assert d.voting_enabled is True

    def test_fund(self):
        f = Fund(name="Test Fund", aum=5e6, strategy="regenerative", vintage=2025)
        assert f.aum == 5e6
        assert f.strategy == "regenerative"

    def test_organization(self):
        org = Organization(name="ACME", founded_year=2020, has_audit=True)
        assert org.has_audit is True

    def test_capital_score(self):
        p = Project(name="Test", metadata={"score_financeiro": 0.8, "score_vivo": 0.6})
        grid = CapitalGrid()
        score = p.capital_score(grid)
        assert 0 <= score <= 1
