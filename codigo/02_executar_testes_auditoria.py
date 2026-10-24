#!/usr/bin/env python3
"""Executa testes automatizados e amostragem MUS sobre a base sintética."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


SEED = 261_021_423
ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = ROOT / "base_simulada" / "imobilizado_sintetico_tupy_2025.csv.gz"
ERROR_PATH = ROOT / "base_simulada" / "gabarito_erros_inseridos.csv.gz"
OUT_DIR = ROOT / "saidas"

OVERALL_MATERIALITY = 46_958_205  # 0,5% do ativo total consolidado de R$ 9.391.641 mil
PERFORMANCE_MATERIALITY = 32_870_744  # 70% da materialidade global, arredondada
CLEARLY_TRIVIAL = 2_347_910  # 5% da materialidade global, arredondada
SAMPLING_RISK = 0.05
CONFIDENCE_FACTOR = 3.0
EXPECTED_MISSTATEMENT = 5_000_000
EXPANSION_FACTOR = 1.5


TESTS = {
    "E01": "Faturas duplicadas por fornecedor e número do documento",
    "E02": "Início de depreciação mais de 30 dias após a disponibilidade para uso",
    "E03": "Bens sucateados com valor contábil líquido positivo",
    "E04": "Indicadores de impairment sem avaliação documentada",
    "E05": "Taxa de conversão aplicada com desvio superior a 2%",
    "E06": "Depreciação mensal superior a 110% da política calculada",
    "E07": "Manutenção rotineira registrada como ativo",
    "E08": "Adições antes da transferência de controle até a data-base",
    "E09": "Adições sem aprovação de CAPEX",
    "E10": "Registros sem documento-suporte",
}


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    date_cols = ["in_service_date", "depreciation_start_date", "control_transfer_date", "posting_date"]
    df = pd.read_csv(BASE_PATH, low_memory=False, parse_dates=date_cols)
    errors = pd.read_csv(ERROR_PATH)
    return df, errors


def detect_exceptions(df: pd.DataFrame) -> dict[str, np.ndarray]:
    dup_mask = df.duplicated(["supplier_id", "invoice_id"], keep=False)
    dup = df.loc[dup_mask, ["supplier_id", "invoice_id", "posting_date", "record_sequence"]].copy()
    dup = dup.sort_values(["supplier_id", "invoice_id", "posting_date", "record_sequence"])
    later = dup.groupby(["supplier_id", "invoice_id"], sort=False).tail(1).index

    return {
        "E01": df.loc[later, "asset_id"].to_numpy(),
        "E02": df.loc[
            (df["depreciation_start_date"] - df["in_service_date"]).dt.days > 30, "asset_id"
        ].to_numpy(),
        "E03": df.loc[
            (df["physical_status"] == "SUCATEADO_NAO_BAIXADO") & (df["net_book_value_brl"] > 0), "asset_id"
        ].to_numpy(),
        "E04": df.loc[
            (df["impairment_indicator"] == "SIM") & (df["impairment_assessment_status"] == "NAO_REALIZADO"), "asset_id"
        ].to_numpy(),
        "E05": df.loc[
            ((df["applied_fx_rate_brl"] / df["closing_fx_rate_brl"]) - 1).abs() > 0.02, "asset_id"
        ].to_numpy(),
        "E06": df.loc[
            (df["expected_monthly_depreciation_brl"] > 0)
            & (df["book_monthly_depreciation_brl"] > 1.10 * df["expected_monthly_depreciation_brl"]),
            "asset_id",
        ].to_numpy(),
        "E07": df.loc[df["capitalized_nature"] == "MANUTENCAO_ROTINEIRA", "asset_id"].to_numpy(),
        "E08": df.loc[
            (df["additions_2025_brl"] > 0) & (df["control_transfer_date"] > pd.Timestamp("2025-12-31")), "asset_id"
        ].to_numpy(),
        "E09": df.loc[(df["additions_2025_brl"] > 0) & (df["capex_approval_id"].fillna("") == ""), "asset_id"].to_numpy(),
        "E10": df.loc[df["support_status"] == "AUSENTE", "asset_id"].to_numpy(),
    }


def run_full_population_tests(df: pd.DataFrame, errors: pd.DataFrame) -> pd.DataFrame:
    detected = detect_exceptions(df)
    error_lookup = errors.set_index(["error_code", "asset_id"])["misstatement_brl_book_minus_audit"]
    rows = []
    exception_rows = []
    for code, description in TESTS.items():
        found = set(detected[code].tolist())
        expected = set(errors.loc[errors["error_code"] == code, "asset_id"].tolist())
        tp = found & expected
        fp = found - expected
        fn = expected - found
        amount = sum(int(error_lookup.get((code, asset_id), 0)) for asset_id in tp)
        rows.append(
            {
                "test_code": code,
                "procedure": description,
                "population_records": len(df),
                "expected_exceptions": len(expected),
                "detected_exceptions": len(found),
                "true_positives": len(tp),
                "false_positives": len(fp),
                "false_negatives": len(fn),
                "detected_misstatement_brl": amount,
                "test_result": "CONCILIADO" if not fp and not fn else "DIVERGENCIA",
                "procedure_classification": "Simulado para fins didáticos",
            }
        )
        for asset_id in sorted(found):
            exception_rows.append(
                {
                    "test_code": code,
                    "asset_id": asset_id,
                    "procedure": description,
                    "in_inserted_error_log": "SIM" if asset_id in expected else "NAO",
                    "misstatement_brl": int(error_lookup.get((code, asset_id), 0)),
                }
            )
    results = pd.DataFrame(rows)
    pd.DataFrame(exception_rows).to_csv(
        OUT_DIR / "excecoes_detectadas_100_percento.csv.gz",
        index=False,
        compression={"method": "gzip", "compresslevel": 6, "mtime": 0},
    )
    results.to_csv(OUT_DIR / "resultados_testes_100_percento.csv", index=False)
    if (results["test_result"] != "CONCILIADO").any():
        raise AssertionError("Os testes não reproduziram exatamente o gabarito")
    return results


def poisson_factor(error_count: int, confidence: float = 0.95) -> float:
    try:
        from scipy.stats import chi2

        return float(0.5 * chi2.ppf(confidence, 2 * (error_count + 1)))
    except Exception:
        fallback = [2.996, 4.744, 6.296, 7.754, 9.154, 10.513, 11.842, 13.148, 14.435, 15.705]
        return fallback[min(error_count, len(fallback) - 1)]


def run_mus(df: pd.DataFrame, errors: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    pop = int(df["net_book_value_brl"].sum())
    denominator = PERFORMANCE_MATERIALITY - EXPECTED_MISSTATEMENT * EXPANSION_FACTOR
    planned_size = int(math.ceil(pop * CONFIDENCE_FACTOR / denominator))
    preliminary_interval = pop / planned_size

    certainty_mask = df["net_book_value_brl"] >= preliminary_interval
    certainty = df.loc[certainty_mask].copy()
    remainder = df.loc[~certainty_mask].sort_values("asset_id").copy()
    systematic_count = max(planned_size - len(certainty), 1)
    interval = remainder["net_book_value_brl"].sum() / systematic_count

    rng = np.random.default_rng(SEED + 530)
    random_start = float(rng.uniform(0, interval))
    cumulative = remainder["net_book_value_brl"].cumsum().to_numpy()
    points = random_start + interval * np.arange(systematic_count)
    positions = np.searchsorted(cumulative, points, side="left")
    positions = np.clip(positions, 0, len(remainder) - 1)
    systematic = remainder.iloc[np.unique(positions)].copy()
    sample = pd.concat([certainty, systematic], ignore_index=True).drop_duplicates("asset_id")
    sample["selection_type"] = np.where(sample["net_book_value_brl"] >= preliminary_interval, "Certeza", "Sistemática MUS")

    error_by_asset = errors.groupby("asset_id", as_index=False)["misstatement_brl_book_minus_audit"].sum()
    sample = sample.merge(error_by_asset, on="asset_id", how="left")
    sample["misstatement_brl_book_minus_audit"] = sample["misstatement_brl_book_minus_audit"].fillna(0).astype(np.int64)
    sample["absolute_misstatement_brl"] = sample["misstatement_brl_book_minus_audit"].abs()
    sample["tainting"] = np.where(
        sample["net_book_value_brl"] > 0,
        sample["absolute_misstatement_brl"] / sample["net_book_value_brl"],
        0.0,
    )
    sample["projected_misstatement_brl"] = np.where(
        sample["selection_type"] == "Certeza",
        sample["absolute_misstatement_brl"],
        sample["tainting"] * interval,
    )

    taintings = sorted(sample.loc[sample["tainting"] > 0, "tainting"].tolist(), reverse=True)
    basic_precision = interval * poisson_factor(0)
    incremental_allowance = 0.0
    previous = poisson_factor(0)
    for i, taint in enumerate(taintings, start=1):
        current = poisson_factor(i)
        incremental_allowance += (current - previous) * interval * taint
        previous = current
    certainty_misstatement = float(
        sample.loc[sample["selection_type"] == "Certeza", "absolute_misstatement_brl"].sum()
    )
    upper_error_limit = basic_precision + incremental_allowance + certainty_misstatement
    projected = float(sample["projected_misstatement_brl"].sum())
    actual_signed = int(sample["misstatement_brl_book_minus_audit"].sum())

    evaluation = {
        "method": "Amostragem por unidade monetária (MUS/PPS), seleção sistemática com itens de certeza",
        "population_value_brl": pop,
        "sampling_risk": SAMPLING_RISK,
        "confidence": 1 - SAMPLING_RISK,
        "confidence_factor_planning": CONFIDENCE_FACTOR,
        "tolerable_misstatement_brl": PERFORMANCE_MATERIALITY,
        "expected_misstatement_brl": EXPECTED_MISSTATEMENT,
        "expansion_factor": EXPANSION_FACTOR,
        "planned_sample_size": planned_size,
        "certainty_items": int(len(certainty)),
        "systematic_unique_items": int(len(systematic)),
        "actual_unique_sample_size": int(len(sample)),
        "preliminary_interval_brl": preliminary_interval,
        "systematic_interval_brl": interval,
        "random_start_brl": random_start,
        "sample_error_items": int((sample["absolute_misstatement_brl"] > 0).sum()),
        "actual_signed_sample_misstatement_brl": actual_signed,
        "projected_absolute_misstatement_brl": projected,
        "basic_precision_brl": basic_precision,
        "incremental_allowance_brl": incremental_allowance,
        "certainty_actual_misstatement_brl": certainty_misstatement,
        "upper_error_limit_brl": upper_error_limit,
        "conclusion": "NÃO ACEITAR A POPULAÇÃO" if upper_error_limit > PERFORMANCE_MATERIALITY else "ACEITAR A POPULAÇÃO",
        "limitation": "Resultado exclusivamente didático, calculado sobre registros e erros artificiais; não constitui evidência sobre ativos reais da Tupy.",
    }

    keep = [
        "asset_id",
        "entity",
        "plant_city",
        "asset_class",
        "book_cost_brl",
        "accumulated_depreciation_brl",
        "net_book_value_brl",
        "selection_type",
        "misstatement_brl_book_minus_audit",
        "absolute_misstatement_brl",
        "tainting",
        "projected_misstatement_brl",
    ]
    sample[keep].sort_values(["selection_type", "asset_id"]).to_csv(OUT_DIR / "amostra_MUS.csv", index=False)
    (OUT_DIR / "avaliacao_MUS.json").write_text(json.dumps(evaluation, ensure_ascii=False, indent=2), encoding="utf-8")
    return sample, evaluation


def export_materiality() -> None:
    rows = [
        {
            "metric": "Ativo total consolidado",
            "basis_brl": 9_391_641_000,
            "percentage": 1.0,
            "amount_brl": 9_391_641_000,
            "rationale": "Saldo público em 31/12/2025",
        },
        {
            "metric": "Materialidade global",
            "basis_brl": 9_391_641_000,
            "percentage": 0.005,
            "amount_brl": OVERALL_MATERIALITY,
            "rationale": "0,5% do ativo total; entidade industrial intensiva em ativos e resultado líquido volátil/prejuízo",
        },
        {
            "metric": "Materialidade de execução",
            "basis_brl": OVERALL_MATERIALITY,
            "percentage": 0.70,
            "amount_brl": PERFORMANCE_MATERIALITY,
            "rationale": "70% da materialidade global, considerando riscos significativos e dispersão internacional",
        },
        {
            "metric": "Limite claramente trivial",
            "basis_brl": OVERALL_MATERIALITY,
            "percentage": 0.05,
            "amount_brl": CLEARLY_TRIVIAL,
            "rationale": "5% da materialidade global para acumulação de distorções",
        },
    ]
    pd.DataFrame(rows).to_csv(OUT_DIR / "materialidade.csv", index=False)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df, errors = load_data()
    results = run_full_population_tests(df, errors)
    _, mus = run_mus(df, errors)
    export_materiality()
    print(json.dumps({
        "full_population_tests": len(results),
        "all_tests_reconciled": bool((results["test_result"] == "CONCILIADO").all()),
        "mus_planned_sample_size": mus["planned_sample_size"],
        "mus_actual_sample_size": mus["actual_unique_sample_size"],
        "mus_upper_error_limit_brl": round(mus["upper_error_limit_brl"], 2),
        "mus_conclusion": mus["conclusion"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
