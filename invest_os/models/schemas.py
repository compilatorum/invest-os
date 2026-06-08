from __future__ import annotations
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class InvestorProfile(str, Enum):
    SEMEADOR = "semeador"
    BROTADOR = "brotador"
    CULTIVADOR = "cultivador"
    GUARDIAO = "guardiao"
    SABIO = "sabio"


class RiskProfile(str, Enum):
    CONSERVADOR = "conservador"
    MODERADO = "moderado"
    ARROJADO = "arrojado"


class Action(str, Enum):
    COMPRAR = "comprar"
    AGUARDAR = "aguardar"
    REBALANCEAR = "rebalancear"
    EVITAR = "evitar"


class AlchemicalPhase(str, Enum):
    NIGREDO = "nigredo"
    ALBEDO = "albedo"
    RUBEDO = "rubedo"


class CapitalType(str, Enum):
    FINANCEIRO = "financeiro"
    VIVO = "vivo"
    MATERIAL = "material"
    SOCIAL = "social"
    INTELECTUAL = "intelectual"
    EXPERIENCIAL = "experiencial"
    CULTURAL = "cultural"
    ESPIRITUAL = "espiritual"


CAPITAL_WEIGHTS = {
    CapitalType.FINANCEIRO: 0.20,
    CapitalType.VIVO: 0.15,
    CapitalType.MATERIAL: 0.10,
    CapitalType.SOCIAL: 0.15,
    CapitalType.INTELECTUAL: 0.15,
    CapitalType.EXPERIENCIAL: 0.10,
    CapitalType.CULTURAL: 0.10,
    CapitalType.ESPIRITUAL: 0.05,
}


class FinancialMetrics(BaseModel):
    nvt: Optional[float] = None
    mvrv: Optional[float] = None
    sopr: Optional[float] = None
    sharpe_90d: Optional[float] = None
    il_break_even: Optional[float] = None
    fee_apy: Optional[float] = None
    hhi: Optional[float] = None
    ps_ratio: Optional[float] = None
    temperature: Optional[float] = None
    entropy: Optional[float] = None


class CapitalScore(BaseModel):
    type: CapitalType
    score: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    evidence: list[str] = []


class CapitalGridResult(BaseModel):
    scores: list[CapitalScore]
    rhi_estimated: float = Field(ge=0.0, le=1.0)
    shannon_h: Optional[float] = None
    gini: Optional[float] = None
    bloqueio: Optional[str] = None


class SemioticAnalysis(BaseModel):
    sign: str = ""
    object: str = ""
    interpretant: list[str] = []
    coherence: float = Field(ge=0.0, le=1.0)
    noise: float = Field(ge=0.0, le=1.0)
    phase: AlchemicalPhase = AlchemicalPhase.NIGREDO


class CognitiveMap(BaseModel):
    tecnica: dict = {}
    semiotica: dict = {}
    ontologica: dict = {}
    flags_iniciais: list[str] = []


class DecisionOutput(BaseModel):
    acao: Action
    tamanho_posicao: float = Field(ge=-1.0, le=1.0)
    score_composto: float = Field(ge=0.0, le=1.0)
    narrativa: str = ""
    metadata_nft: dict = {}
    gate_humano: bool = False


class RlhfLog(BaseModel):
    previsao: str = ""
    realidade: str = ""
    delta_capital: dict = {}
    prompt_melhoria: str = ""
    rhi_real: Optional[float] = None
    rhi_estimado: Optional[float] = None
    level_up: bool = False


class InvestorConfig(BaseModel):
    nome: str = "investidor"
    perfil: InvestorProfile = InvestorProfile.SEMEADOR
    risco: RiskProfile = RiskProfile.MODERADO
    tese_impacto: str = ""
    capital_disponivel_brl: float = 0.0
    modo_linguagem: str = "hibrido"

    @property
    def gate_timeout(self) -> int:
        return {RiskProfile.CONSERVADOR: 3600, RiskProfile.MODERADO: 3600, RiskProfile.ARROJADO: 3600}[self.risco]

    @property
    def gate_default(self) -> str:
        return {RiskProfile.CONSERVADOR: "REJEITAR", RiskProfile.MODERADO: "MANTER_ESTADO", RiskProfile.ARROJADO: "EXECUTAR"}[self.risco]

    @property
    def limite_autonomo_brl(self) -> float:
        return {RiskProfile.CONSERVADOR: 0.0, RiskProfile.MODERADO: 15.0, RiskProfile.ARROJADO: 50.0}[self.risco]


class SystemState(BaseModel):
    config: InvestorConfig = InvestorConfig()
    metrics: FinancialMetrics = FinancialMetrics()
    capital_grid: Optional[CapitalGridResult] = None
    semiotic: Optional[SemioticAnalysis] = None
    decision: Optional[DecisionOutput] = None
    history: list[RlhfLog] = []
