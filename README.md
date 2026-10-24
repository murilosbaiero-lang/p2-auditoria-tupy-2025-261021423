# Dossiê acadêmico de auditoria — Tupy S.A. (2025)

**Murilo Sena Baiero · matrícula 261021423 · trabalho individual P2**  
**Data-base da pesquisa:** 24/10/2026

> **Aviso essencial.** Este é um trabalho acadêmico elaborado com informações públicas e dados artificiais. Não houve contato com a Tupy, com seus auditores, administradores, empregados, clientes, fornecedores, bancos ou advogados. A base de 520.000 registros e todas as exceções nela inseridas são sintéticas. O repositório não constitui auditoria real, asseguração, opinião independente, recomendação de investimento ou alegação sobre a companhia.

## Entrega principal

| Arquivo ou pasta | Conteúdo |
|---|---|
| `dossie/Dossie_Auditoria_Tupy_2025_261021423.pdf` | Dossiê consolidado e paginado, com 89 páginas |
| `dossie/Dossie_Auditoria_Tupy_2025_261021423.docx` | Versão editável do dossiê |
| `papeis_trabalho/PT-*.md` | 27 papéis de trabalho editáveis: EC e NBC TA 200 a 600 |
| `planilhas/calculos_auditoria_tupy_2025.xlsx` | Materialidade, DFs, indicadores, riscos, ciclos, conciliações, distorções, MUS, continuidade e fontes |
| `base_simulada/partes/` | População sintética completa, dividida em partes para publicação; reconstrução preserva o hash original |
| `base_simulada/gabarito_erros_inseridos.csv.gz` | Gabarito transparente das exceções artificiais |
| `codigo/` | Scripts de geração, testes, análises, documentação e validação |
| `saidas/` | Resultados estruturados dos procedimentos automatizados |
| `fontes/fontes.csv` | Matriz de fontes com URL, data de acesso, documento, período, páginas e finalidade |
| `docs/` | Metodologia, programas por ciclo, minutas, versões normativas, referências e conclusão |

## Escopo e referencial

O dossiê documenta o planejamento acadêmico de auditoria das demonstrações consolidadas da Tupy S.A. e controladas para o exercício findo em 31/12/2025. A cobertura inclui a Estrutura Conceitual e os seguintes papéis: NBC TA 200, 210, 220, 230, 240, 250, 260, 265, 300, 315, 320, 330, 402, 450, 500, 501, 505, 510, 520, 530, 540, 550, 560, 570, 580 e 600.

As versões consideradas aplicáveis ao exercício de 2025 estão registradas em [`docs/versoes_normas.md`](docs/versoes_normas.md). As revisões NBC TA 240 (R2) e NBC TA 570 (R1), com vigência para períodos iniciados em ou após 01/01/2027, não foram aplicadas retroativamente.

Cada procedimento está classificado como:

1. **Realizado com evidência pública** — análise efetivamente executada sobre documento público identificado;
2. **Planejado por falta de acesso** — procedimento necessário em auditoria real, mas não executado; ou
3. **Simulado para fins didáticos** — teste sobre dados artificiais, sem inferência sobre registros reais.

## Visão financeira e riscos priorizados

Valores públicos consolidados de 2025 utilizados no planejamento:

| Métrica | Valor |
|---|---:|
| Ativo total | R$ 9,392 bilhões |
| Receita | R$ 9,693 bilhões |
| Resultado líquido | R$ (654,552) milhões |
| Caixa gerado nas atividades operacionais | R$ 915,137 milhões |
| Imobilizado líquido | R$ 2,525 bilhões |
| Materialidade global acadêmica | R$ 46,958 milhões |
| Materialidade de execução | R$ 32,871 milhões |
| Limite claramente trivial | R$ 2,348 milhões |

O planejamento prioriza imobilizado e impairment, realização de ativos fiscais diferidos, reconhecimento e corte da receita, estoques, dívida e covenants, continuidade operacional, burla de controles pela administração, provisões, partes relacionadas e consolidação internacional. A matriz completa R01–R12 está em [`saidas/matriz_riscos.csv`](saidas/matriz_riscos.csv).

## Base sintética do imobilizado

O imobilizado foi selecionado por ser a maior conta individual do ativo. A população contém 520.000 registros artificiais e concilia exatamente aos totais públicos da Nota 13:

| Grandeza | Total reconciliado |
|---|---:|
| Custo | R$ 9.174.411.000 |
| Depreciação acumulada | R$ 6.649.254.000 |
| Saldo líquido | R$ 2.525.157.000 |
| Adições em 2025 | R$ 461.410.000 |
| Depreciação de 2025 | R$ 359.020.000 |
| Impairment de 2025 | R$ 324.791.000 |

A base usa semente determinística `261021423`. Foram inseridas 2.220 exceções didáticas em dez tipologias, incluindo duplicidade, início tardio ou excesso de depreciação, ativo sucateado não baixado, impairment sem teste, manutenção capitalizada, corte, autorização e suporte. Os testes de 100% reproduziram o gabarito sem falsos positivos ou falsos negativos.

A distorção líquida artificial é de R$ 53,0 milhões. A amostra MUS contém 299 itens e produziu limite superior de erro de R$ 92,0 milhões, acima da distorção tolerável. A conclusão “não aceitar a população” refere-se exclusivamente à simulação.

## Reproduzir as análises

Requisitos sugeridos: Python 3.11 ou superior, aproximadamente 2 GB de memória livre e espaço para a base descompactada em memória.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
bash executar_tudo.sh
```

O comando regenera a base, executa os testes, refaz matrizes e papéis, cria o DOCX e valida os produtos. Se o LibreOffice estiver instalado, também exporta o PDF. A planilha final está versionada; o script `codigo/05_criar_planilha.mjs` registra sua construção com o mecanismo de planilhas utilizado no ambiente de elaboração.

Para recompor diretamente o arquivo pré-gerado publicado em partes:

```bash
python codigo/00_reconstruir_base.py
```

O resultado será `base_simulada/imobilizado_sintetico_tupy_2025.csv.gz`, com o mesmo SHA-256 informado em `base_simulada/hashes_sha256.txt`.

Verificações de integridade:

```bash
sha256sum -c base_simulada/hashes_sha256.txt --ignore-missing
python codigo/07_validar_repositorio.py
```

## Fontes públicas principais

- [DFP 2025 — CVM, sequência 155493](https://www.rad.cvm.gov.br/ENET/frmGerenciaPaginaFRE.aspx?CodigoTipoInstituicao=1&NumeroSequencialDocumento=155493)
- [DFP 2024 — CVM, sequência 145865](https://www.rad.cvm.gov.br/ENET/frmGerenciaPaginaFRE.aspx?CodigoTipoInstituicao=1&NumeroSequencialDocumento=145865)
- [Formulário de Referência 2025 — CVM, sequência 157961](https://www.rad.cvm.gov.br/ENET/frmGerenciaPaginaFRE.aspx?CodigoTipoInstituicao=1&NumeroSequencialDocumento=157961)
- [Tupy — Central de Resultados](https://ri.tupy.com.br/informacoes-financeiras/central-de-resultados/)
- [Tupy na B3](https://sistemaswebb3-listados.b3.com.br/listedCompaniesPage/main/6343/CODBOLSA/overview?language=pt-br)
- [CFC — normas de auditoria independente](https://cfc.org.br/tecnica/normas-brasileiras-de-contabilidade/nbc-ta-de-auditoria-independente/)

A matriz integral, incluindo ITRs de 2025 e 2026, documentos de governança, normas e páginas consultadas, está em [`fontes/fontes.csv`](fontes/fontes.csv).

## Limitações

Não foram realizados walkthroughs, testes em sistemas internos, observação de inventário, inspeção física, confirmações externas, circularização jurídica, entrevistas, reexecução dos modelos reais, testes de lançamentos do razão, obtenção de representações formais ou comunicação com a governança. Por isso, o trabalho não conclui sobre efetividade de controles, razoabilidade final de estimativas, existência física, completude de passivos, continuidade operacional ou opinião de auditoria.

O relatório público do auditor independente sobre 2025 foi utilizado apenas como fonte. Sua opinião e seus principais assuntos de auditoria não são reproduzidos como conclusão do aluno.

