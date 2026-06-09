from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class SignalType(str, Enum):
    MARKET = "market"
    SOCIAL = "social"
    CODE = "code"
    GOVERNANCE = "governance"


class Signal(BaseModel):
    type: SignalType
    source: str
    value: float
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    metadata: dict = {}


class MarketSignal(Signal):
    type: SignalType = SignalType.MARKET
    market_cap: float = 0.0
    transaction_volume: float = 0.0
    realized_cap: float = 0.0


class SocialSignal(Signal):
    type: SignalType = SignalType.SOCIAL
    community_size: int = 0
    governance_participation: float = Field(ge=0.0, le=1.0, default=0.0)


class CodeSignal(Signal):
    type: SignalType = SignalType.CODE
    github_stars: int = 0
    github_forks: int = 0
    contributors: int = 0


class GovernanceSignal(Signal):
    type: SignalType = SignalType.GOVERNANCE
    has_sbt: bool = False
    voting_enabled: bool = False
    has_oracles: bool = False


class NormalizedSignal(BaseModel):
    type: SignalType
    source: str
    normalized_value: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    raw: Signal


def normalize_market(signal: MarketSignal) -> NormalizedSignal:
    mc = getattr(signal, 'market_cap', 0)
    tv = getattr(signal, 'transaction_volume', 1)
    rc = getattr(signal, 'realized_cap', 1)
    nvt = (mc / max(tv, 1)) / 200.0
    nvt = min(max(nvt, 0.0), 1.0)
    mvrv = (mc / max(rc, 1)) / 5.0
    mvrv = min(max(mvrv, 0.0), 1.0)
    val = 1.0 - ((nvt + mvrv) / 2.0)
    return NormalizedSignal(
        type=signal.type, source=signal.source,
        normalized_value=round(val, 4),
        raw=signal,
    )


def normalize_social(signal: SocialSignal) -> NormalizedSignal:
    sz = min(signal.community_size / 100000.0, 1.0)
    gp = signal.governance_participation
    val = (sz * 0.4 + gp * 0.6)
    return NormalizedSignal(
        type=signal.type, source=signal.source,
        normalized_value=round(min(val, 1.0), 4),
        raw=signal,
    )


def normalize_code(signal: CodeSignal) -> NormalizedSignal:
    stars = min(signal.github_stars / 5000.0, 1.0)
    forks = min(signal.github_forks / 1000.0, 1.0)
    contribs = min(signal.contributors / 100.0, 1.0)
    val = stars * 0.4 + forks * 0.3 + contribs * 0.3
    return NormalizedSignal(
        type=signal.type, source=signal.source,
        normalized_value=round(min(val, 1.0), 4),
        raw=signal,
    )


def normalize_governance(signal: GovernanceSignal) -> NormalizedSignal:
    val = 0.0
    if signal.has_sbt:
        val += 0.35
    if signal.voting_enabled:
        val += 0.35
    if signal.has_oracles:
        val += 0.3
    return NormalizedSignal(
        type=signal.type, source=signal.source,
        normalized_value=round(val, 4),
        raw=signal,
    )


NORMALIZERS: dict[SignalType, callable] = {
    SignalType.MARKET: normalize_market,
    SignalType.SOCIAL: normalize_social,
    SignalType.CODE: normalize_code,
    SignalType.GOVERNANCE: normalize_governance,
}

NORMALIZER_TYPES = {
    SignalType.MARKET: MarketSignal,
    SignalType.SOCIAL: SocialSignal,
    SignalType.CODE: CodeSignal,
    SignalType.GOVERNANCE: GovernanceSignal,
}


def normalize(signal: Signal) -> NormalizedSignal:
    expected_type = NORMALIZER_TYPES.get(signal.type)
    if expected_type is not None and not isinstance(signal, expected_type):
        return NormalizedSignal(
            type=signal.type, source=signal.source,
            normalized_value=0.5, raw=signal,
        )
    fn = NORMALIZERS.get(signal.type)
    return fn(signal)
