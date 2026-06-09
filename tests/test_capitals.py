import pytest
from invest_os.capitals.grid import CapitalGrid
from invest_os.capitals.dimensions import CapitalDimension, DimensionRegistry
from invest_os.models.schemas import CapitalType, Action


class TestConfigurableKAIROS:
    def test_default_dimensions(self):
        grid = CapitalGrid()
        assert len(grid.registry.dimensions) == 8

    def test_add_dimension(self):
        grid = CapitalGrid()
        grid.add_dimension("ecological", 0.15, metric="shannon_h", threshold=1.2)
        assert "ecological" in grid.registry.dimensions
        assert grid.registry.get("ecological").weight == 0.15

    def test_remove_dimension(self):
        grid = CapitalGrid()
        grid.remove_dimension("vivo")
        assert "vivo" not in grid.registry.dimensions

    def test_custom_dimension_affects_rhi(self):
        grid = CapitalGrid()
        grid.add_dimension("custom", 0.5, metric="test")
        scores = {t: 0.5 for t in CapitalType}
        result = grid.evaluate(scores, shannon_h=2.0, gini=0.1)
        assert result.rhi_estimated == 0.5

    def test_dimension_registry_defaults(self):
        reg = DimensionRegistry.defaults()
        assert len(reg.dimensions) == 8
        assert reg.get("financeiro").weight == 0.20

    def test_dimension_registry_to_from_dict(self):
        reg = DimensionRegistry.defaults()
        d = reg.to_dict()
        assert "financeiro" in d
        reg2 = DimensionRegistry.from_dict(d)
        assert reg2.get("financeiro").weight == 0.20

    def test_evaluate_with_custom_block(self):
        grid = CapitalGrid()
        grid.add_dimension("risk", 0.1, metric="test", threshold=0.3,
                           bloqueio_msg="Risco alto")
        scores = {CapitalType.FINANCEIRO: 0.2}
        result = grid.evaluate(scores, shannon_h=2.0, gini=0.1)
        assert result.rhi_estimated > 0

    def test_dimension_names(self):
        reg = DimensionRegistry.defaults()
        names = reg.names
        assert "financeiro" in names
        assert len(names) == 8

    def test_remove_nonexistent(self):
        reg = DimensionRegistry.defaults()
        reg.remove("nonexistent")
        assert len(reg.dimensions) == 8
