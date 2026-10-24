#!/usr/bin/env python3
"""Valida integridade, cobertura e conciliações do repositório."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []
CHECKS: list[str] = []


def ok(condition: bool, message: str) -> None:
    if condition:
        CHECKS.append(message)
    else:
        ERRORS.append(message)


def count_gzip_csv(path: Path) -> tuple[int, dict[str, int]]:
    totals = {
        "book_cost_brl": 0,
        "accumulated_depreciation_brl": 0,
        "net_book_value_brl": 0,
        "additions_2025_brl": 0,
        "depreciation_expense_2025_brl": 0,
        "impairment_recognized_2025_brl": 0,
    }
    rows = 0
    with gzip.open(path, "rt", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            rows += 1
            for key in totals:
                totals[key] += int(row[key])
    return rows, totals


def workbook_sheets(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as zf:
        xml = zf.read("xl/workbook.xml")
    root = ET.fromstring(xml)
    ns = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    return [node.attrib["name"] for node in root.findall("x:sheets/x:sheet", ns)]


def validate() -> int:
    required = [
        "README.md",
        "requirements.txt",
        "executar_tudo.sh",
        "dossie/Dossie_Auditoria_Tupy_2025_261021423.docx",
        "dossie/Dossie_Auditoria_Tupy_2025_261021423.pdf",
        "planilhas/calculos_auditoria_tupy_2025.xlsx",
        "base_simulada/imobilizado_sintetico_tupy_2025.csv.gz",
        "base_simulada/gabarito_erros_inseridos.csv.gz",
        "base_simulada/dicionario_dados.md",
        "base_simulada/hashes_sha256.txt",
        "fontes/fontes.csv",
        "docs/matriz_cobertura_nbcta.md",
        "docs/conclusao_integrada.md",
    ]
    for rel in required:
        ok((ROOT / rel).is_file(), f"Arquivo obrigatório: {rel}")

    expected_pts = {
        "EC", "200", "210", "220", "230", "240", "250", "260", "265", "300", "315", "320", "330",
        "402", "450", "500", "501", "505", "510", "520", "530", "540", "550", "560", "570", "580", "600",
    }
    actual_pts = {p.stem.removeprefix("PT-") for p in (ROOT / "papeis_trabalho").glob("PT-*.md")}
    ok(actual_pts == expected_pts, "Conjunto exato de 27 papéis de trabalho")

    required_sections = [
        "## Identificação", "## Objetivo", "## Conta, escopo e assertivas", "## Riscos relevantes",
        "## População e seleção", "## Procedimentos, evidências e resultados", "## Síntese dos resultados",
        "## Exceções e assuntos pendentes", "## Conclusão", "## Limitações", "## Referências cruzadas",
    ]
    for pt in sorted((ROOT / "papeis_trabalho").glob("PT-*.md")):
        text = pt.read_text(encoding="utf-8")
        ok(all(section in text for section in required_sections), f"Estrutura completa: {pt.name}")

    base_path = ROOT / "base_simulada" / "imobilizado_sintetico_tupy_2025.csv.gz"
    if base_path.is_file():
        rows, totals = count_gzip_csv(base_path)
        ok(rows == 520_000, "Base sintética contém 520.000 registros")
        expected = {
            "book_cost_brl": 9_174_411_000,
            "accumulated_depreciation_brl": 6_649_254_000,
            "net_book_value_brl": 2_525_157_000,
            "additions_2025_brl": 461_410_000,
            "depreciation_expense_2025_brl": 359_020_000,
            "impairment_recognized_2025_brl": 324_791_000,
        }
        for key, value in expected.items():
            ok(totals[key] == value, f"Conciliação da base: {key} = {value}")

    results_path = ROOT / "saidas" / "resultados_testes_100_percento.csv"
    if results_path.is_file():
        with results_path.open("r", encoding="utf-8", newline="") as fh:
            tests = list(csv.DictReader(fh))
        ok(len(tests) == 10, "Dez testes automatizados documentados")
        ok(all(row["test_result"] == "CONCILIADO" for row in tests), "Todos os testes de 100% conciliados")
        ok(all(int(row["false_positives"]) == 0 and int(row["false_negatives"]) == 0 for row in tests), "Gabarito sem falsos positivos ou negativos")

    mus_path = ROOT / "saidas" / "avaliacao_MUS.json"
    if mus_path.is_file():
        mus = json.loads(mus_path.read_text(encoding="utf-8"))
        ok(mus["actual_unique_sample_size"] == 299, "Amostra MUS contém 299 itens")
        ok(mus["conclusion"] == "NÃO ACEITAR A POPULAÇÃO", "Conclusão MUS da população artificial")

    hash_file = ROOT / "base_simulada" / "hashes_sha256.txt"
    if hash_file.is_file():
        for line in hash_file.read_text(encoding="utf-8").splitlines():
            digest, filename = line.split(maxsplit=1)
            target = ROOT / "base_simulada" / filename.strip()
            if target.is_file():
                actual = hashlib.sha256(target.read_bytes()).hexdigest()
                ok(actual == digest, f"Hash SHA-256: {target.name}")

    xlsx = ROOT / "planilhas" / "calculos_auditoria_tupy_2025.xlsx"
    if xlsx.is_file():
        sheets = workbook_sheets(xlsx)
        expected_sheets = [
            "Resumo", "Materialidade", "Demonstrações", "Indicadores", "Riscos", "Ciclos", "Imobilizado",
            "Testes 100%", "Distorções", "MUS", "Continuidade", "Fontes", "Leia-me",
        ]
        ok(sheets == expected_sheets, "Planilha contém as 13 abas previstas, na ordem")

    pdf = ROOT / "dossie" / "Dossie_Auditoria_Tupy_2025_261021423.pdf"
    if pdf.is_file():
        reader = PdfReader(str(pdf))
        ok(len(reader.pages) == 89, "Dossiê PDF contém 89 páginas")

    sources = ROOT / "fontes" / "fontes.csv"
    if sources.is_file():
        with sources.open("r", encoding="utf-8", newline="") as fh:
            source_rows = list(csv.DictReader(fh))
        ok(len(source_rows) >= 15, "Matriz de fontes contém pelo menos 15 referências")
        ok(all(r["url"] and r["access_date"] and r["purpose"] for r in source_rows), "Fontes têm URL, data de acesso e finalidade")

    print(f"Validações aprovadas: {len(CHECKS)}")
    for item in CHECKS:
        print(f"[OK] {item}")
    if ERRORS:
        print(f"\nFalhas: {len(ERRORS)}", file=sys.stderr)
        for item in ERRORS:
            print(f"[ERRO] {item}", file=sys.stderr)
        return 1
    print("\nREPOSITÓRIO VALIDADO SEM FALHAS")
    return 0


if __name__ == "__main__":
    raise SystemExit(validate())
