#!/usr/bin/env python3
"""Reconstrói a base sintética pré-gerada a partir das partes publicadas."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / "base_simulada" / "partes"
OUTPUT = ROOT / "base_simulada" / "imobilizado_sintetico_tupy_2025.csv.gz"
HASHES = ROOT / "base_simulada" / "hashes_sha256.txt"


def expected_sha256() -> str:
    """Lê o hash da versão efetivamente publicada da base."""
    for line in HASHES.read_text(encoding="utf-8").splitlines():
        digest, filename = line.split(maxsplit=1)
        if Path(filename).name == OUTPUT.name:
            return digest
    raise SystemExit(f"Hash de {OUTPUT.name} não encontrado em {HASHES}")


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
    expected = expected_sha256()
    if actual != expected:
        OUTPUT.unlink(missing_ok=True)
        raise SystemExit(f"SHA-256 divergente: obtido {actual}; esperado {expected}")

    print(f"Base reconstruída em {OUTPUT}")
    print(f"SHA-256 verificado: {actual}")


if __name__ == "__main__":
    main()

