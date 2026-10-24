#!/usr/bin/env python3
"""Reconstrói a base sintética pré-gerada a partir das partes publicadas."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / "base_simulada" / "partes"
OUTPUT = ROOT / "base_simulada" / "imobilizado_sintetico_tupy_2025.csv.gz"
EXPECTED_SHA256 = "97ac63d74b5c8abf90c94bb548cbde453b8dbbff72b3cf10cc6cfc5a786d9f7f"


def main() -> None:
    parts = sorted(PARTS.glob("imobilizado_sintetico_tupy_2025.csv.gz.part-*.part"))
    if not parts:
        raise SystemExit(f"Nenhuma parte encontrada em {PARTS}")

    digest = hashlib.sha256()
    with OUTPUT.open("wb") as target:
        for part in parts:
            with part.open("rb") as source:
                while chunk := source.read(1024 * 1024):
                    target.write(chunk)
                    digest.update(chunk)

    actual = digest.hexdigest()
    if actual != EXPECTED_SHA256:
        OUTPUT.unlink(missing_ok=True)
        raise SystemExit(f"SHA-256 divergente: {actual}")

    print(f"Base reconstruída em {OUTPUT}")
    print(f"SHA-256 verificado: {actual}")


if __name__ == "__main__":
    main()

