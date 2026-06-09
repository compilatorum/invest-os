import pytest
from invest_os.prompts.router import PromptRouter, IntentType


class TestPromptRouter:
    def test_route_default(self):
        router = PromptRouter()
        route = router.route(IntentType.INVESTMENT)
        assert route == "level0_context"

    def test_route_governance(self):
        router = PromptRouter()
        route = router.route(IntentType.GOVERNANCE)
        assert route == "level1_financial_dd"

    def test_add_route(self):
        router = PromptRouter()
        router.add_route(IntentType.INVESTMENT, "custom_level")
        assert router.route(IntentType.INVESTMENT) == "custom_level"

    def test_list_routes(self):
        router = PromptRouter()
        routes = router.list_routes()
        assert "investment" in routes
        assert len(routes) == 5
