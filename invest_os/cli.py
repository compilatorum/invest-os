from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

from invest_os import __version__, __description__
from invest_os.models.schemas import (
    InvestorConfig, CapitalType, Action, RiskProfile, InvestorProfile,
)
from invest_os.core.metrics import calculate_all_metrics
from invest_os.core.capital_grid import CapitalGrid, interpret_rhi
from invest_os.pipeline.cognitive import CognitivePipeline
from invest_os.governance.engine import OstromEngine, GoodhartShield

console = Console()


@click.group()
@click.version_option(version=__version__)
def main():
    """🧬 InvestmentOS — Protocolo Cognitivo de Suporte ao Investidor Web3"""
    pass


@main.command()
@click.option("--market-cap", "-m", default=1e9, help="Market Cap do ativo")
@click.option("--volume", "-v", default=1e7, help="Transaction volume 24h")
@click.option("--realized-cap", "-r", default=8e8, help="Realized Cap")
@click.option("--returns", "-R", default=None, help="Retornos 90d (JSON list)")
@click.option("--shannon-h", "-s", default=0.0, type=float, help="Índice Shannon H'")
@click.option("--gini", "-g", default=0.0, type=float, help="Coeficiente Gini")
@click.option("--p1", default=100.0, type=float, help="Preço entrada")
@click.option("--p2", default=120.0, type=float, help="Preço saída")
@click.option("--json-output", "-j", is_flag=True, help="Output em JSON")
def analyze(market_cap, volume, realized_cap, returns, shannon_h, gini, p1, p2, json_output):
    """📊 Analisa um ativo com métricas financeiras + grid de capitais"""
    returns_list = None
    if returns:
        returns_list = json.loads(returns)

    metrics = calculate_all_metrics(
        market_cap=market_cap,
        transaction_volume=volume,
        realized_cap=realized_cap,
        returns_90d=returns_list,
        p1=p1, p2=p2,
        volume_24h=volume,
        fee_tier=0.003,
        liquidity=market_cap * 0.1,
        portfolio_weights=[0.4, 0.3, 0.2, 0.1],
        volatility_24h=0.05,
        exposure_pct=0.1,
    )

    cm = CapitalGrid()
    capital_scores = CapitalGrid.score_from_metrics(
        market_cap=market_cap,
        tvl=market_cap * 0.3,
        revenue=market_cap * 0.02,
        github_stars=500,
        github_forks=100,
        contributors=20,
        community_size=10000,
        governance_participation=0.15,
        carbon_offset_tco2=500,
        has_audit=True,
        years_active=3,
    )
    grid = cm.evaluate(capital_scores, shannon_h=shannon_h, gini=gini)
    nivel, faixa, desc = interpret_rhi(grid.rhi_estimated)

    if json_output:
        result = {
            "metrics": {k: v for k, v in metrics.items() if k != "alertas"},
            "alertas": metrics.get("alertas", []),
            "capital_grid": grid.model_dump(),
            "rhi": grid.rhi_estimated,
            "nivel_arquetipo": nivel,
        }
        console.print_json(data=result)
        return

    console.print(Panel(f"[bold cyan]🧬 InvestmentOS — Análise de Ativo[/bold cyan]\n{__description__}"))
    console.print()

    tab = Table(title="📊 Métricas Financeiras")
    tab.add_column("Métrica", style="cyan")
    tab.add_column("Valor", style="yellow")
    tab.add_column("Sinal", style="green")
    for k in ["nvt", "mvrv", "sopr", "sharpe_90d", "il_break_even", "hhi", "entropy", "temperature"]:
        v = metrics.get(k)
        if v is not None:
            tab.add_row(k.upper(), f"{v:.4f}", "")
    console.print(tab)

    if metrics.get("alertas"):
        console.print("[red]⚠️ Alertas:[/red]")
        for a in metrics["alertas"]:
            console.print(f"  • {a}")

    console.print()
    tab2 = Table(title="🌿 Grid KAIROS — 8 Capitais")
    tab2.add_column("Capital", style="cyan")
    tab2.add_column("Score", style="yellow")
    tab2.add_column("Status")
    for cs in grid.scores:
        ico = "🟢" if cs.score > 0.5 else "🟡" if cs.score > 0.3 else "🔴"
        tab2.add_row(cs.type.value.capitalize(), f"{cs.score:.2%}", ico)
    console.print(tab2)

    console.print(f"\n[bold]RHI Estimado:[/bold] {grid.rhi_estimated:.2%}")
    console.print(f"[bold]Nível Arquetípico:[/bold] {nivel.upper()} ({faixa}) — {desc}")

    if grid.bloqueio:
        console.print(f"\n[red]🚫 BLOQUEIO: {grid.bloqueio}[/red]")

    console.print()
    console.print(Panel(
        "[dim]Dica: use `invest-os pipeline` para executar o pipeline cognitivo completo[/dim]"
    ))


@main.command()
@click.option("--ativo", "-a", default="BTC", help="Nome do ativo/protocolo")
@click.option("--perfil", "-p", default="semeador", type=click.Choice([p.value for p in InvestorProfile]))
@click.option("--risco", "-r", default="moderado", type=click.Choice([r.value for r in RiskProfile]))
@click.option("--tese", "-t", default="", help="Tese de impacto")
@click.option("--capital", "-c", default=300.0, type=float, help="Capital disponível em BRL")
@click.option("--market-cap", "-m", default=1e9, type=float)
@click.option("--volume", "-v", default=1e7, type=float)
@click.option("--realized-cap", default=8e8, type=float)
@click.option("--shannon-h", "-s", default=0.0, type=float)
@click.option("--gini", "-g", default=0.0, type=float)
@click.option("--json-output", "-j", is_flag=True)
@click.option("--feedback", "-f", default=None, help="Feedback pós-decisão (JSON)")
def pipeline(ativo, perfil, risco, tese, capital, market_cap, volume,
             realized_cap, shannon_h, gini, json_output, feedback):
    """⚙️ Executa o pipeline cognitivo completo (5 camadas)"""
    perfil_enum = InvestorProfile(perfil)
    risco_enum = RiskProfile(risco)

    config = InvestorConfig(
        nome="investidor",
        perfil=perfil_enum,
        risco=risco_enum,
        tese_impacto=tese,
        capital_disponivel_brl=capital,
    )

    pipe = CognitivePipeline(config=config)

    feedback_dict = None
    if feedback:
        feedback_dict = json.loads(feedback)

    result = pipe.run(
        ativo=ativo,
        metrics_input={
            "market_cap": market_cap,
            "transaction_volume": volume,
            "realized_cap": realized_cap,
        },
        capital_scores_kwargs={"shannon_h": shannon_h, "gini": gini},
        feedback=feedback_dict,
    )

    if json_output:
        console.print_json(data=result.state.model_dump())
        return

    s = result.state

    console.print(Panel(f"[bold cyan]🧬 Pipeline Cognitivo — {ativo}[/bold cyan]"))
    console.print(f"[dim]Completado em {result.elapsed_ms:.0f}ms[/dim]")

    console.print(f"\n[bold]👤 Perfil:[/bold] {s.config.perfil.value.upper()} | Risco: {s.config.risco.value}")
    console.print(f"[bold]💰 Capital:[/bold] R$ {s.config.capital_disponivel_brl:,.2f}")
    if s.config.tese_impacto:
        console.print(f"[bold]🎯 Tese:[/bold] {s.config.tese_impacto}")

    console.print("\n[bold cyan]📍 Camada 1 — Percepção[/bold cyan]")
    console.print(f"  NVT: {s.metrics.nvt:.2f}" if s.metrics.nvt else "")
    console.print(f"  MVRV: {s.metrics.mvrv:.2f}" if s.metrics.mvrv else "")
    console.print(f"  Sharpe 90d: {s.metrics.sharpe_90d:.4f}" if s.metrics.sharpe_90d else "")

    console.print(f"\n[bold cyan]📍 Camada 2 — Semiose[/bold cyan]")
    if s.capital_grid:
        console.print(f"  RHI: {s.capital_grid.rhi_estimated:.2%}")
        nivel, faixa, _ = interpret_rhi(s.capital_grid.rhi_estimated)
        console.print(f"  Nível: {nivel.upper()} ({faixa})")
        if s.capital_grid.bloqueio:
            console.print(f"  🚫 {s.capital_grid.bloqueio}")

    console.print(f"\n[bold cyan]📍 Camada 3 — Interpretação[/bold cyan]")
    if s.semiotic:
        console.print(f"  Coerência: {s.semiotic.coherence:.2f}")
        console.print(f"  Ruído: {s.semiotic.noise:.2f}")
        console.print(f"  Fase: {s.semiotic.phase.value}")

    console.print(f"\n[bold cyan]📍 Camada 4 — Decisão[/bold cyan]")
    if s.decision:
        acao_ico = {"comprar": "🟢", "aguardar": "🟡", "rebalancear": "🔶", "evitar": "🔴"}
        console.print(f"  Ação: {acao_ico.get(s.decision.acao.value, '❓')} {s.decision.acao.value.upper()}")
        console.print(f"  Score Composto: {s.decision.score_composto:.2%}")
        console.print(f"  Posição: {s.decision.tamanho_posicao:.1%}")
        if s.decision.gate_humano:
            console.print(f"  ⚠️ Gate Humano Obrigatório")
        console.print(f"  Narrativa: {s.decision.narrativa}")

    console.print(f"\n[bold cyan]📍 Camada 5 — Registro[/bold cyan]")
    console.print(f"  Previsão: {s.history[-1].previsao if s.history else 'N/A'}")
    console.print(f"  Realidade: {s.history[-1].realidade if s.history else 'pendente'}")

    console.print()
    console.print(Panel(
        "[dim]Meta-prompt chain disponível em `invest-os prompts`[/dim]"
    ))


@main.command()
@click.option("--ativo", "-a", default="BTC", help="Ativo para gerar chain")
@click.option("--perfil", "-p", default="semeador", type=click.Choice([p.value for p in InvestorProfile]))
@click.option("--nivel", "-n", default="all", help="Nível específico (0-5) ou 'all'")
@click.option("--output", "-o", default=None, help="Salvar em arquivo")
def prompts(ativo, perfil, nivel, output):
    """🧠 Gera a meta-prompt chain (5 níveis de deep research)"""
    from invest_os.prompts.engine import PromptEngine
    from invest_os.core.capital_grid import CapitalGrid

    config = InvestorConfig(perfil=InvestorProfile(perfil))
    engine = PromptEngine()
    grid = CapitalGrid()
    cg = grid.evaluate({t: 0.5 for t in CapitalType})

    from invest_os.models.schemas import DecisionOutput, Action, RlhfLog

    decision = DecisionOutput(acao=Action.AGUARDAR, tamanho_posicao=0.05, score_composto=0.55)
    log = RlhfLog()

    chain = engine.run_full_chain(ativo, config, {}, cg, decision, log)

    levels = {f"level{i}_{name}": chain[f"level{i}_{name}"]
              for i, name in enumerate(["context", "financial_dd", "regenerative_dd", "semiotic", "axiological", "rlhf"])}

    if nivel != "all":
        lid = int(nivel)
        keys = list(levels.keys())
        if 0 <= lid < len(keys):
            levels = {keys[lid]: levels[keys[lid]]}

    full = ""
    for name, content in levels.items():
        full += f"---\n\n## {name}\n\n{content}\n\n"

    if output:
        Path(output).write_text(full)
        console.print(f"[green]✓[/green] Prompt chain salva em {output}")
    else:
        console.print(Markdown(full))


@main.command()
@click.option("--has-sbt", is_flag=True, help="Token-gating via SBT")
@click.option("--local-config", is_flag=True, help="Configuração local (sub-DAOs)")
@click.option("--voting", is_flag=True, help="Votação habilitada")
@click.option("--oracles", is_flag=True, help="Oráculos híbridos")
@click.option("--slashing", is_flag=True, help="Slashing progressivo")
@click.option("--dispute", is_flag=True, help="Resolução de conflitos")
@click.option("--legal", is_flag=True, help="Framework legal")
@click.option("--dao-of-daos", is_flag=True, help="Estrutura aninhada")
@click.option("--json-output", "-j", is_flag=True)
def governance(has_sbt, local_config, voting, oracles, slashing,
               dispute, legal, dao_of_daos, json_output):
    """🏛️ Avalia governança algorítmica (Ostrom + Goodhart Shield)"""
    context = {
        "has_sbt": has_sbt,
        "local_config": local_config,
        "voting_enabled": voting,
        "has_oracles": oracles,
        "has_slashing": slashing,
        "has_dispute_resolution": dispute,
        "has_legal_framework": legal,
        "is_dao_of_daos": dao_of_daos,
    }

    ostrom = OstromEngine()
    score, failed = ostrom.evaluate_score(context)

    if json_output:
        console.print_json(data={
            "score": score,
            "principios_atendidos": 8 - len(failed),
            "principios_total": 8,
            "failed": failed,
        })
        return

    tab = Table(title=f"🏛️ Governança Ostrom — Score: {score:.0%}")
    tab.add_column("Princípio", style="cyan")
    tab.add_column("Status")
    for principle, passed in ostrom.check_governance(context).items():
        ico = "✅" if passed else "❌"
        tab.add_row(principle, ico)
    console.print(tab)

    if failed:
        console.print(f"\n[red]❌ Princípios não atendidos: {len(failed)}/8[/red]")
        for f in failed:
            console.print(f"  • {f}")

    shield = GoodhartShield()
    test_val = shield.apply("rhi", 0.65)
    console.print(f"\n[bold]Goodhart Shield:[/bold] RHI 0.65 → {test_val:.4f} (com ruído)")

    console.print()
    console.print(Panel(
        "[dim]Dica: ative flags para simular diferentes configurações de governança[/dim]"
    ))


@main.command()
@click.option("--tipo", "-t", default="gbm", type=click.Choice(["gbm", "lotka", "bonding", "conviction"]))
@click.option("--steps", "-s", default=100, type=int)
@click.option("--dt", default=0.01, type=float)
@click.option("--json-output", "-j", is_flag=True)
def simulate(tipo, steps, dt, json_output):
    """⚛️ Executa simulação econofísica (GBM, Lotka-Volterra, Bonding Curves)"""
    from invest_os.utils.math_tools import (
        geometric_brownian_motion, lotka_volterra,
        price_from_bonding_curve, conviction_vote,
    )

    if tipo == "gbm":
        path = geometric_brownian_motion(100, 0.05, 0.2, dt, steps)
        if json_output:
            console.print_json(data={"type": "gbm", "path": [round(p, 4) for p in path]})
            return
        console.print(f"[bold cyan]📈 GBM — Geometric Brownian Motion[/bold cyan]\n")
        console.print(f"  S₀ = 100 | μ = 5% | σ = 20% | {steps} steps")
        console.print(f"  Final: {path[-1]:.4f}")
        console.print(f"  Min: {min(path):.4f} | Max: {max(path):.4f} | Ret: {(path[-1]/path[0]-1)*100:.2f}%")

    elif tipo == "lotka":
        v, f = lotka_volterra(0.5, 0.01, 0.01, 0.3, 40, 10, dt, steps)
        if json_output:
            console.print_json(data={"type": "lotka", "vivo": [round(x, 4) for x in v], "financeiro": [round(x, 4) for x in f]})
            return
        console.print(f"[bold cyan]🦌 Lotka-Volterra (Capital Vivo × Financeiro)[/bold cyan]\n")
        console.print(f"  α=0.5 β=0.01 δ=0.01 γ=0.3 | V₀=40 F₀=10")
        console.print(f"  Final — Vivo: {v[-1]:.2f} | Financeiro: {f[-1]:.2f}")
        console.print(f"  Vivo max: {max(v):.2f} | Financeiro max: {max(f):.2f}")

    elif tipo == "bonding":
        if json_output:
            prices = {s: price_from_bonding_curve(s, 50000, 0.5) for s in range(100, 1100, 100)}
            console.print_json(data={"type": "bonding", "prices": prices})
            return
        console.print(f"[bold cyan]🔗 Bonding Curve[/bold cyan]\n")
        console.print(f"  Supply vs Preço (Reserve Ratio = 0.5):")
        for s in range(100, 1100, 100):
            p = price_from_bonding_curve(s, 50000, 0.5)
            console.print(f"    Supply {s:4d} → Preço {p:8.4f}")

    elif tipo == "conviction":
        conv = 0
        alpha = 0.9
        if json_output:
            for voto in [10, 5, 20, 8, 15]:
                conv = conviction_vote(conv, alpha, voto)
            console.print_json(data={"type": "conviction", "final": conv, "approved": conv >= 50})
            return
        console.print(f"[bold cyan]🗳️ Conviction Voting[/bold cyan]\n")
        console.print(f"  α={alpha} | votos=[10, 5, 20, 8, 15] | limiar=50")
        for i, voto in enumerate([10, 5, 20, 8, 15]):
            conv = conviction_vote(conv, alpha, voto)
            status = "✅ APROVADA" if conv >= 50 else "⏳"
            console.print(f"    Passo {i+1}: convicção={conv:.2f} {status}")


@main.command()
def version():
    """📋 Mostra versão e info do sistema"""
    console.print(f"[bold]🧬 InvestmentOS[/bold] v{__version__}")
    console.print(f"[dim]{__description__}[/dim]")
    console.print()
    console.print("  [cyan]Módulos:[/cyan]")
    console.print("    • 📊 core/metrics — NVT, MVRV, SOPR, Sharpe, HHI, ...")
    console.print("    • 🌿 core/capital_grid — KAIROS 8 capitais, RHI")
    console.print("    • 🧠 prompts/engine — Meta-prompt chain 5 níveis")
    console.print("    • ⚙️  pipeline/cognitive — Pipeline cognitivo 5 camadas")
    console.print("    • 🏛️  governance/engine — Ostrom + Goodhart Shield")
    console.print("    • ⚛️  utils/math_tools — Econofísica, GBM, Lotka-Volterra")
    console.print()
    console.print("  [cyan]Comandos CLI:[/cyan]")
    console.print("    invest-os analyze     📊 Análise completa de ativo")
    console.print("    invest-os pipeline    ⚙️  Pipeline cognitivo completo")
    console.print("    invest-os prompts     🧠 Meta-prompt chain")
    console.print("    invest-os governance  🏛️  Governança algorítmica")
    console.print("    invest-os simulate    ⚛️  Simulação econofísica")


if __name__ == "__main__":
    main()
