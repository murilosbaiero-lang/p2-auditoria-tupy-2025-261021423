#!/usr/bin/env python3
"""Gera a base sintética de imobilizado usada no dossiê acadêmico da Tupy.

Os totais publicados são reais e vêm da Nota 13 das demonstrações financeiras
consolidadas de 2025. Todos os registros individualizados, documentos, controles
e erros inseridos são artificiais. A semente fixa torna a geração reproduzível.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


SEED = 261_021_423
N_ROWS = 520_000
ROOT = Path(__file__).resolve().parents[1]
BASE_DIR = ROOT / "base_simulada"
OUT_DIR = ROOT / "saidas"


# Valores em reais. A fonte pública apresenta esses montantes em R$ mil.
CLASSES = {
    "Máquinas, instalações e equipamentos": {
        "count": 280_000,
        "gross": 6_313_083_000,
        "accum_dep": 5_296_122_000,
        "additions": 327_427_000,
        "impairment": 208_472_000,
        "dep_2025": 254_864_000,
        "life_months": (84, 240),
        "min_cost": 500,
        "sigma": 1.55,
    },
    "Edificações": {
        "count": 15_000,
        "gross": 1_649_811_000,
        "accum_dep": 1_118_646_000,
        "additions": 32_150_000,
        "impairment": 60_411_000,
        "dep_2025": 50_350_000,
        "life_months": (300, 600),
        "min_cost": 5_000,
        "sigma": 1.45,
    },
    "Terrenos": {
        "count": 800,
        "gross": 360_107_000,
        "accum_dep": 0,
        "additions": 0,
        "impairment": 0,
        "dep_2025": 0,
        "life_months": (0, 0),
        "min_cost": 10_000,
        "sigma": 1.25,
    },
    "Veículos": {
        "count": 10_000,
        "gross": 48_003_000,
        "accum_dep": 27_819_000,
        "additions": 4_158_000,
        "impairment": 2_036_000,
        "dep_2025": 4_170_000,
        "life_months": (60, 144),
        "min_cost": 500,
        "sigma": 1.15,
    },
    "Móveis, utensílios e outros": {
        "count": 145_000,
        "gross": 123_303_000,
        "accum_dep": 107_095_000,
        "additions": 9_269_000,
        "impairment": 10_252_000,
        "dep_2025": 8_912_000,
        "life_months": (60, 180),
        "min_cost": 50,
        "sigma": 1.25,
    },
    "Direito de uso de ativos": {
        "count": 34_200,
        "gross": 130_633_000,
        "accum_dep": 99_572_000,
        "additions": 43_422_000,
        "impairment": 6_564_000,
        "dep_2025": 40_724_000,
        "life_months": (24, 180),
        "min_cost": 250,
        "sigma": 1.30,
    },
    "Imobilizações em andamento": {
        "count": 35_000,
        "gross": 549_471_000,
        "accum_dep": 0,
        "additions": 44_984_000,
        "impairment": 37_056_000,
        "dep_2025": 0,
        "life_months": (0, 0),
        "min_cost": 1_000,
        "sigma": 1.60,
    },
}


ENTITIES = [
    ("Tupy S.A.", "Joinville", "SC", "Brasil", "BRL", 1.000000),
    ("Tupy Minas Gerais Ltda.", "Betim", "MG", "Brasil", "BRL", 1.000000),
    ("MWM - Tupy do Brasil Ltda.", "São Paulo", "SP", "Brasil", "BRL", 1.000000),
    ("Tupy Agroenergética Ltda.", "Ouro Verde do Oeste", "PR", "Brasil", "BRL", 1.000000),
    ("Tupy México Saltillo, S.A. de C.V.", "Saltillo", "COA", "México", "USD", 5.193200),
    ("Technocast, S.A. de C.V.", "Ramos Arizpe", "COA", "México", "USD", 5.193200),
    ("FUNFRAP - Fundição Portuguesa, S.A.", "Aveiro", "AVE", "Portugal", "EUR", 5.401700),
    ("Tupy Materials & Components B.V.", "Roterdã", "ZH", "Países Baixos", "EUR", 5.401700),
]

ENTITY_WEIGHTS = np.array([0.35, 0.14, 0.15, 0.015, 0.17, 0.095, 0.07, 0.01])


ERROR_SPECS = [
    ("E01", "Fatura duplicada", 120, 6_500_000, "superavaliação", "existência/ocorrência"),
    ("E02", "Início tardio da depreciação", 150, 4_200_000, "superavaliação", "avaliação/alocação"),
    ("E03", "Bem sucateado sem baixa", 80, 8_800_000, "superavaliação", "existência e avaliação"),
    ("E04", "Indicador de impairment sem teste", 80, 14_000_000, "superavaliação", "avaliação/alocação"),
    ("E05", "Conversão cambial inconsistente", 120, 2_500_000, "superavaliação", "exatidão e avaliação"),
    ("E06", "Depreciação acima da política", 100, -4_000_000, "subavaliação", "avaliação/alocação"),
    ("E07", "Manutenção rotineira capitalizada", 120, 11_000_000, "superavaliação", "classificação e ocorrência"),
    ("E08", "Adição reconhecida antes da transferência de controle", 100, 10_000_000, "superavaliação", "corte e direitos"),
    ("E09", "Adição sem aprovação de CAPEX", 600, 0, "sem quantificação direta", "ocorrência/autorização"),
    ("E10", "Documento-suporte ausente", 750, 0, "sem quantificação direta", "existência/ocorrência"),
]


def allocate_integer(total: int, weights: np.ndarray, minimum: int = 0, caps: np.ndarray | None = None) -> np.ndarray:
    """Aloca um total inteiro exatamente, respeitando mínimo e limites."""
    n = len(weights)
    if n == 0:
        if total != 0:
            raise ValueError("Não há elementos para alocar o total")
        return np.array([], dtype=np.int64)
    result = np.full(n, minimum, dtype=np.int64)
    remaining = int(total - minimum * n)
    if remaining < 0:
        raise ValueError("Total inferior ao mínimo agregado")
    if caps is None:
        # Um limite finito evita overflow ao somar a capacidade de vetores grandes.
        caps = np.full(n, max(int(total), minimum), dtype=np.int64)
    else:
        caps = np.asarray(caps, dtype=np.int64)
    capacity = caps - result
    if remaining > int(capacity.sum()):
        raise ValueError("Capacidade insuficiente para a alocação")
    active = capacity > 0
    weights = np.asarray(weights, dtype=float)
    weights = np.where(np.isfinite(weights) & (weights > 0), weights, 1.0)
    while remaining:
        idx = np.flatnonzero(active)
        w = weights[idx]
        raw = remaining * w / w.sum()
        add = np.floor(raw).astype(np.int64)
        add = np.minimum(add, capacity[idx])
        used = int(add.sum())
        if used:
            result[idx] += add
            capacity[idx] -= add
            remaining -= used
        if not remaining:
            break
        idx = np.flatnonzero(capacity > 0)
        if len(idx) == 0:
            raise ValueError("Capacidade esgotada antes de fechar a alocação")
        # Distribui o resíduo pelos maiores restos fracionários e depois por capacidade.
        frac = raw - np.floor(raw) if len(raw) == len(np.flatnonzero(active)) else np.ones(len(idx))
        if len(frac) == len(idx):
            order = idx[np.argsort(-frac, kind="stable")]
        else:
            order = idx[np.argsort(-capacity[idx], kind="stable")]
        take = min(remaining, len(order))
        result[order[:take]] += 1
        capacity[order[:take]] -= 1
        remaining -= take
        active = capacity > 0
    return result


def random_dates(rng: np.random.Generator, n: int, start: str, end: str) -> pd.Series:
    lo = np.datetime64(start, "D").astype(int)
    hi = np.datetime64(end, "D").astype(int)
    vals = rng.integers(lo, hi + 1, size=n)
    return pd.Series(pd.to_datetime(vals, unit="D", origin="1970-01-01"))


def build_population() -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    parts: list[pd.DataFrame] = []
    running = 1

    for asset_class, cfg in CLASSES.items():
        n = cfg["count"]
        weights = rng.lognormal(mean=0.0, sigma=cfg["sigma"], size=n)
        costs = allocate_integer(cfg["gross"], weights, minimum=cfg["min_cost"])

        # Idade sintética e depreciação acumulada coerente com o custo, fechando o total publicado.
        if cfg["accum_dep"]:
            life = rng.integers(cfg["life_months"][0], cfg["life_months"][1] + 1, size=n)
            age_ratio = rng.beta(3.2, 1.25, size=n)
            dep_weights = costs * np.clip(age_ratio, 0.02, 1.0)
            accum_dep = allocate_integer(cfg["accum_dep"], dep_weights, caps=costs)
            residual = np.minimum(
                (costs * rng.choice([0.0, 0.02, 0.05, 0.10], p=[0.70, 0.10, 0.15, 0.05], size=n)).astype(np.int64),
                np.maximum(costs - 1, 0),
            )
        else:
            life = np.zeros(n, dtype=np.int64)
            accum_dep = np.zeros(n, dtype=np.int64)
            residual = np.zeros(n, dtype=np.int64)

        net = costs - accum_dep
        entity_idx = rng.choice(len(ENTITIES), size=n, p=ENTITY_WEIGHTS)
        entity = np.array([ENTITIES[i][0] for i in entity_idx], dtype=object)
        city = np.array([ENTITIES[i][1] for i in entity_idx], dtype=object)
        state = np.array([ENTITIES[i][2] for i in entity_idx], dtype=object)
        country = np.array([ENTITIES[i][3] for i in entity_idx], dtype=object)
        currency = np.array([ENTITIES[i][4] for i in entity_idx], dtype=object)
        fx_rate = np.array([ENTITIES[i][5] for i in entity_idx], dtype=float)

        if asset_class == "Imobilizações em andamento":
            acquisition = random_dates(rng, n, "2021-01-01", "2025-12-31")
            in_service = pd.Series(pd.NaT, index=np.arange(n), dtype="datetime64[ns]")
            dep_start = pd.Series(pd.NaT, index=np.arange(n), dtype="datetime64[ns]")
            physical = np.full(n, "EM_CONSTRUCAO", dtype=object)
            status = np.full(n, "EM_ANDAMENTO", dtype=object)
        else:
            acquisition = random_dates(rng, n, "1985-01-01", "2025-12-15")
            delay = pd.to_timedelta(rng.integers(0, 181, size=n), unit="D")
            in_service = acquisition + delay
            in_service = in_service.where(in_service <= pd.Timestamp("2025-12-31"), pd.Timestamp("2025-12-31"))
            dep_start = in_service.copy()
            physical = np.full(n, "LOCALIZADO", dtype=object)
            status = np.full(n, "ATIVO", dtype=object)

        additions = np.zeros(n, dtype=np.int64)
        if cfg["additions"]:
            candidates = np.flatnonzero((acquisition >= pd.Timestamp("2024-07-01")).to_numpy())
            if len(candidates) < 500:
                candidates = np.argsort(-costs)[: max(500, n // 20)]
            add_caps = np.maximum(costs[candidates], 1)
            chosen = candidates[np.argsort(-add_caps)[: max(500, len(candidates) // 2)]]
            additions[chosen] = allocate_integer(
                cfg["additions"],
                costs[chosen].astype(float),
                # O valor adicionado no exercício pode superar o saldo final do
                # componente após transferências, baixas, câmbio e impairment.
                caps=np.maximum(costs[chosen] * 20, costs[chosen]),
            )

        impairment = np.zeros(n, dtype=np.int64)
        if cfg["impairment"]:
            betim = np.flatnonzero(entity == "Tupy Minas Gerais Ltda.")
            chosen = betim[np.argsort(-costs[betim])[: max(250, len(betim) // 3)]]
            impairment[chosen] = allocate_integer(
                cfg["impairment"], costs[chosen].astype(float), caps=np.maximum(costs[chosen] * 3, costs[chosen])
            )

        dep_expense = np.zeros(n, dtype=np.int64)
        if cfg["dep_2025"]:
            eligible = np.flatnonzero(costs > 0)
            dep_expense[eligible] = allocate_integer(cfg["dep_2025"], costs[eligible].astype(float))

        ids = np.arange(running, running + n)
        running += n
        base_seq = ids.astype(str)
        posting_date = acquisition.where(acquisition >= pd.Timestamp("2025-01-01"), pd.Timestamp("2025-01-02"))
        posting_date = posting_date.where(posting_date <= pd.Timestamp("2025-12-31"), pd.Timestamp("2025-12-31"))
        local_cost = np.round(costs / fx_rate, 2)
        monthly_expected = np.where(
            life > 0,
            np.round(np.maximum(costs - residual, 0) / np.maximum(life, 1), 2),
            0.0,
        )

        df = pd.DataFrame(
            {
                "asset_id": [f"AT-{x:07d}" for x in ids],
                "record_sequence": ids,
                "entity": entity,
                "plant_city": city,
                "state_region": state,
                "country": country,
                "functional_currency": currency,
                "asset_class": asset_class,
                "asset_description": [f"{asset_class.split(',')[0]} - componente {x:07d}" for x in ids],
                "cost_center": [f"CC-{x:05d}" for x in rng.integers(1, 9000, size=n)],
                "custodian_area": rng.choice(
                    ["Produção", "Manutenção", "Logística", "Qualidade", "Engenharia", "Administrativo"], size=n
                ),
                "book_status": status,
                "acquisition_date": acquisition,
                "control_transfer_date": acquisition,
                "in_service_date": in_service,
                "depreciation_start_date": dep_start,
                "posting_date": posting_date,
                "useful_life_months": life,
                "residual_value_brl": residual,
                "book_cost_brl": costs,
                "accumulated_depreciation_brl": accum_dep,
                "net_book_value_brl": net,
                "additions_2025_brl": additions,
                "depreciation_expense_2025_brl": dep_expense,
                "impairment_recognized_2025_brl": impairment,
                "expected_monthly_depreciation_brl": monthly_expected,
                "book_monthly_depreciation_brl": monthly_expected.copy(),
                "supplier_id": [f"FORN-{x:06d}" for x in rng.integers(1, 70_000, size=n)],
                "invoice_id": [f"NF-{2025 if a.year == 2025 else a.year}-{x:09d}" for a, x in zip(acquisition, ids)],
                "support_status": np.full(n, "COMPLETO", dtype=object),
                "capex_approval_id": [f"CAPEX-{x:08d}" if a else "N/A" for x, a in zip(ids, additions > 0)],
                "physical_tag": [f"TAG-{x:08d}" for x in ids],
                "physical_status": physical,
                "last_inventory_date": random_dates(rng, n, "2025-01-01", "2025-12-20"),
                "impairment_indicator": np.where(impairment > 0, "SIM", "NAO"),
                "impairment_assessment_status": np.where(impairment > 0, "AVALIADO_E_RECONHECIDO", "NAO_APLICAVEL"),
                "recoverable_amount_brl": net.copy(),
                "capitalized_nature": np.full(n, "ATIVO_QUALIFICAVEL", dtype=object),
                "closing_fx_rate_brl": fx_rate,
                "applied_fx_rate_brl": fx_rate.copy(),
                "local_cost_functional_currency": local_cost,
                "pledged_as_collateral": rng.choice(["SIM", "NAO"], p=[0.018, 0.982], size=n),
                "insured": np.where(asset_class == "Terrenos", "NAO_APLICAVEL", "SIM"),
                "source_system": rng.choice(["SAP_ECC", "SAP_S4", "MAXIMO", "LEASE_SYSTEM"], p=[0.42, 0.37, 0.17, 0.04], size=n),
            }
        )
        parts.append(df)

    population = pd.concat(parts, ignore_index=True)
    if len(population) != N_ROWS:
        raise AssertionError(f"Quantidade inesperada: {len(population):,}")
    return population


def inject_errors(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(SEED + 99)
    available = np.ones(len(df), dtype=bool)
    errors: list[pd.DataFrame] = []

    def select_rows(count: int, mask: np.ndarray | None = None) -> np.ndarray:
        eligible = available.copy()
        if mask is not None:
            eligible &= mask
        candidates = np.flatnonzero(eligible)
        if len(candidates) < count:
            raise ValueError(f"Candidatos insuficientes: {len(candidates)} para {count}")
        # Mistura tamanho monetário e aleatoriedade; isso permite que a MUS encontre alguns casos.
        score = df.loc[candidates, "net_book_value_brl"].to_numpy() * rng.uniform(0.85, 1.15, len(candidates))
        selected = candidates[np.argsort(-score)[:count]]
        available[selected] = False
        return selected

    for code, label, count, target, direction, assertion in ERROR_SPECS:
        mask = (df["net_book_value_brl"].to_numpy() > 10_000)
        if code == "E05":
            mask &= df["functional_currency"].isin(["USD", "EUR"]).to_numpy()
        if code in {"E08", "E09"}:
            mask &= (df["additions_2025_brl"].to_numpy() > 0)
        if code == "E06":
            mask &= (df["accumulated_depreciation_brl"].to_numpy() > 50_000)
        selected = select_rows(count, mask)

        if target > 0:
            caps = np.maximum((df.loc[selected, "net_book_value_brl"].to_numpy() * 0.85).astype(np.int64), 1)
            amounts = allocate_integer(target, df.loc[selected, "net_book_value_brl"].to_numpy().astype(float), caps=caps)
        elif target < 0:
            caps = np.maximum((df.loc[selected, "accumulated_depreciation_brl"].to_numpy() * 0.50).astype(np.int64), 1)
            amounts = -allocate_integer(-target, df.loc[selected, "accumulated_depreciation_brl"].to_numpy().astype(float), caps=caps)
        else:
            amounts = np.zeros(count, dtype=np.int64)

        if code == "E01":
            donors = select_rows(count, (df["net_book_value_brl"].to_numpy() > 1_000))
            # Doadores são registros legítimos; voltam à população disponível para outros testes.
            available[donors] = True
            df.loc[selected, "supplier_id"] = df.loc[donors, "supplier_id"].to_numpy()
            df.loc[selected, "invoice_id"] = df.loc[donors, "invoice_id"].to_numpy()
            df.loc[donors, "posting_date"] = pd.Timestamp("2025-01-02")
            df.loc[selected, "posting_date"] = pd.Timestamp("2025-12-31")
            detection = "duplicidade de supplier_id + invoice_id; o registro posterior é a exceção"
        elif code == "E02":
            old_service = pd.to_datetime(df.loc[selected, "in_service_date"]).where(
                pd.to_datetime(df.loc[selected, "in_service_date"]) < pd.Timestamp("2025-01-01"),
                pd.Timestamp("2024-01-01"),
            )
            df.loc[selected, "in_service_date"] = old_service.to_numpy()
            df.loc[selected, "depreciation_start_date"] = pd.Timestamp("2025-07-01")
            detection = "depreciation_start_date posterior à in_service_date em mais de 30 dias"
        elif code == "E03":
            df.loc[selected, "physical_status"] = "SUCATEADO_NAO_BAIXADO"
            detection = "physical_status sucateado com net_book_value_brl positivo"
        elif code == "E04":
            df.loc[selected, "impairment_indicator"] = "SIM"
            df.loc[selected, "impairment_assessment_status"] = "NAO_REALIZADO"
            df.loc[selected, "recoverable_amount_brl"] = np.clip(
                df.loc[selected, "net_book_value_brl"].to_numpy() - amounts, 0, None
            )
            detection = "indicador SIM e assessment NAO_REALIZADO"
        elif code == "E05":
            factor = np.where(df.loc[selected, "functional_currency"].to_numpy() == "USD", 1.08, 1.06)
            df.loc[selected, "applied_fx_rate_brl"] = df.loc[selected, "closing_fx_rate_brl"].to_numpy() * factor
            detection = "diferença superior a 2% entre taxa aplicada e taxa de fechamento"
        elif code == "E06":
            df.loc[selected, "book_monthly_depreciation_brl"] = (
                df.loc[selected, "expected_monthly_depreciation_brl"].to_numpy() * 1.35
            ).round(2)
            detection = "depreciação mensal registrada superior a 110% da política"
        elif code == "E07":
            df.loc[selected, "capitalized_nature"] = "MANUTENCAO_ROTINEIRA"
            detection = "natureza manutenção rotineira em registro capitalizado"
        elif code == "E08":
            df.loc[selected, "control_transfer_date"] = pd.Timestamp("2026-01-15")
            detection = "transferência de controle posterior a 31/12/2025 para adição reconhecida em 2025"
        elif code == "E09":
            df.loc[selected, "capex_approval_id"] = ""
            detection = "adição positiva sem capex_approval_id"
        elif code == "E10":
            df.loc[selected, "support_status"] = "AUSENTE"
            detection = "support_status ausente"
        else:
            raise AssertionError(code)

        err = pd.DataFrame(
            {
                "asset_id": df.loc[selected, "asset_id"].to_numpy(),
                "error_code": code,
                "error_description": label,
                "assertion": assertion,
                "classification": direction,
                "book_net_value_brl": df.loc[selected, "net_book_value_brl"].to_numpy(),
                "misstatement_brl_book_minus_audit": amounts,
                "audit_expected_net_value_brl": df.loc[selected, "net_book_value_brl"].to_numpy() - amounts,
                "detection_rule": detection,
                "didactic_only": "SIM",
            }
        )
        errors.append(err)

    return df, pd.concat(errors, ignore_index=True)


def validate_and_export(df: pd.DataFrame, errors: pd.DataFrame) -> None:
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Conciliação com a Nota 13.
    recon = (
        df.groupby("asset_class", sort=False)[
            [
                "book_cost_brl",
                "accumulated_depreciation_brl",
                "net_book_value_brl",
                "additions_2025_brl",
                "depreciation_expense_2025_brl",
                "impairment_recognized_2025_brl",
            ]
        ]
        .sum()
        .reset_index()
    )
    recon["public_gross_brl"] = recon["asset_class"].map({k: v["gross"] for k, v in CLASSES.items()})
    recon["public_accum_dep_brl"] = recon["asset_class"].map({k: v["accum_dep"] for k, v in CLASSES.items()})
    recon["public_net_brl"] = recon["asset_class"].map({k: v["gross"] - v["accum_dep"] for k, v in CLASSES.items()})
    recon["difference_net_brl"] = recon["net_book_value_brl"] - recon["public_net_brl"]
    total = pd.DataFrame(
        {
            "asset_class": ["TOTAL"],
            **{c: [int(recon[c].sum())] for c in recon.columns if c != "asset_class"},
        }
    )
    recon = pd.concat([recon, total], ignore_index=True)
    if int(recon.iloc[-1]["net_book_value_brl"]) != 2_525_157_000:
        raise AssertionError("A base não fecha com o saldo consolidado publicado")
    if int(recon.iloc[-1]["difference_net_brl"]) != 0:
        raise AssertionError("Há diferença na conciliação da base")
    if int(errors["misstatement_brl_book_minus_audit"].sum()) != 53_000_000:
        raise AssertionError("Distorção sintética líquida inesperada")

    date_cols = [
        "acquisition_date",
        "control_transfer_date",
        "in_service_date",
        "depreciation_start_date",
        "posting_date",
        "last_inventory_date",
    ]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col]).dt.strftime("%Y-%m-%d").replace("NaT", "")

    base_path = BASE_DIR / "imobilizado_sintetico_tupy_2025.csv.gz"
    df.to_csv(base_path, index=False, compression={"method": "gzip", "compresslevel": 6, "mtime": 0})
    errors.to_csv(BASE_DIR / "gabarito_erros_inseridos.csv.gz", index=False, compression={"method": "gzip", "compresslevel": 6, "mtime": 0})
    recon.to_csv(OUT_DIR / "conciliacao_imobilizado.csv", index=False)

    # Amostra pequena para inspeção sem descompactar a base inteira.
    sample = df.sample(n=1_000, random_state=SEED).sort_values("asset_id")
    sample.to_csv(BASE_DIR / "amostra_1000_registros.csv", index=False)

    summary = (
        errors.groupby(["error_code", "error_description", "assertion", "classification"], as_index=False)
        .agg(
            records=("asset_id", "count"),
            net_misstatement_brl=("misstatement_brl_book_minus_audit", "sum"),
            absolute_misstatement_brl=("misstatement_brl_book_minus_audit", lambda s: int(s.abs().sum())),
        )
    )
    summary.to_csv(OUT_DIR / "resumo_erros_inseridos.csv", index=False)

    controls = {
        "seed": SEED,
        "records": int(len(df)),
        "published_balance_brl": 2_525_157_000,
        "generated_balance_brl": int(df["net_book_value_brl"].sum()),
        "gross_cost_brl": int(df["book_cost_brl"].sum()),
        "accumulated_depreciation_brl": int(df["accumulated_depreciation_brl"].sum()),
        "inserted_exception_records": int(len(errors)),
        "inserted_net_misstatement_brl": int(errors["misstatement_brl_book_minus_audit"].sum()),
        "inserted_absolute_misstatement_brl": int(errors["misstatement_brl_book_minus_audit"].abs().sum()),
        "reconciliation_difference_brl": int(df["net_book_value_brl"].sum() - 2_525_157_000),
        "source": "Tupy S.A., Demonstrações Financeiras 2025, Nota 13, páginas 46 a 48",
        "nature": "Registros individualizados e erros inteiramente sintéticos; totais agregados ancorados em fonte pública.",
    }
    (OUT_DIR / "controles_geracao.json").write_text(json.dumps(controls, ensure_ascii=False, indent=2), encoding="utf-8")

    sha_lines = []
    for path in sorted([base_path, BASE_DIR / "gabarito_erros_inseridos.csv.gz", BASE_DIR / "amostra_1000_registros.csv"]):
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        sha_lines.append(f"{sha}  {path.name}")
    (BASE_DIR / "hashes_sha256.txt").write_text("\n".join(sha_lines) + "\n", encoding="utf-8")


def main() -> None:
    population = build_population()
    population, errors = inject_errors(population)
    validate_and_export(population, errors)
    print(json.dumps({
        "records": len(population),
        "net_book_value_brl": int(population["net_book_value_brl"].sum()),
        "error_records": len(errors),
        "net_misstatement_brl": int(errors["misstatement_brl_book_minus_audit"].sum()),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
