#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"

cd "$PROJECT_DIR"

"$PYTHON_BIN" codigo/01_gerar_base_imobilizado.py
"$PYTHON_BIN" codigo/02_executar_testes_auditoria.py
"$PYTHON_BIN" codigo/03_analises_planejamento.py
"$PYTHON_BIN" codigo/04_gerar_papeis_trabalho.py
"$PYTHON_BIN" codigo/06_criar_dossie.py

if command -v libreoffice >/dev/null 2>&1; then
  libreoffice --headless --convert-to pdf --outdir dossie \
    dossie/Dossie_Auditoria_Tupy_2025_261021423.docx >/dev/null
elif command -v soffice >/dev/null 2>&1; then
  soffice --headless --convert-to pdf --outdir dossie \
    dossie/Dossie_Auditoria_Tupy_2025_261021423.docx >/dev/null
fi

"$PYTHON_BIN" codigo/07_validar_repositorio.py

