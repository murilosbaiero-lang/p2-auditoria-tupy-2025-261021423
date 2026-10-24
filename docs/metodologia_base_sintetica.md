# Metodologia da base sintética de imobilizado

## Objetivo e natureza

A base foi criada para demonstrar procedimentos de auditoria sobre o maior saldo do ativo consolidado da Tupy S.A. em 31 de dezembro de 2025: o imobilizado, com valor contábil líquido de R$ 2.525.157.000. Os registros individualizados não são registros da Tupy. Identificadores, fornecedores, faturas, datas, controles, localizações por ativo e exceções são fictícios.

Os únicos elementos ancorados em informação pública são os totais agregados da Nota 13: custo, depreciação acumulada, valor líquido, adições, depreciação do exercício e impairment por classe. A geração utiliza a semente `261021423`, correspondente à matrícula do aluno, para permitir reprodução independente.

## População e reconciliação

- Quantidade: 520.000 registros de ativos ou componentes.
- Unidade monetária: real brasileiro, sem centavos nos saldos contábeis.
- Data-base: 31/12/2025.
- Custo total: R$ 9.174.411.000.
- Depreciação acumulada: R$ 6.649.254.000.
- Valor contábil líquido: R$ 2.525.157.000.
- Diferença para a Nota 13: R$ 0.

As quantidades por classe foram definidas para representar uma companhia industrial multinacional com controle por componentes. Os custos seguem distribuição lognormal, apropriada para uma população com muitos itens de menor valor e poucos equipamentos de alto valor. A depreciação acumulada foi alocada sob o limite do custo individual e ajustada, por classe, para fechar exatamente os totais públicos.

## Erros inseridos

Foram inseridos dez tipos de exceção em 2.220 registros. O gabarito fica separado da base principal para que os testes possam ser executados sem uma coluna que revele a resposta. Oito tipos têm efeito monetário; dois representam desvios de controle sem quantificação direta.

| Código | Exceção | Registros | Distorção líquida |
|---|---|---:|---:|
| E01 | Fatura duplicada | 120 | R$ 6.500.000 |
| E02 | Início tardio da depreciação | 150 | R$ 4.200.000 |
| E03 | Bem sucateado sem baixa | 80 | R$ 8.800.000 |
| E04 | Indicador de impairment sem teste | 80 | R$ 14.000.000 |
| E05 | Conversão cambial inconsistente | 120 | R$ 2.500.000 |
| E06 | Depreciação acima da política | 100 | R$ (4.000.000) |
| E07 | Manutenção rotineira capitalizada | 120 | R$ 11.000.000 |
| E08 | Adição antes da transferência de controle | 100 | R$ 10.000.000 |
| E09 | Adição sem aprovação de CAPEX | 600 | Não quantificada |
| E10 | Documento-suporte ausente | 750 | Não quantificada |
| **Total** |  | **2.220** | **R$ 53.000.000** |

A distorção é definida como valor contábil menos valor esperado pela auditoria. Valor positivo indica superavaliação; valor negativo, subavaliação. O total absoluto das distorções monetárias é R$ 61.000.000.

## Testes executados

Os scripts executam dez verificações sobre 100% da população: duplicidades, lógica de datas, condição física, impairment, câmbio, depreciação, natureza do gasto, corte, aprovação de CAPEX e existência de suporte. Os resultados detectaram exatamente todos os casos inseridos, sem falsos positivos ou falsos negativos dentro das regras artificiais.

Também foi aplicada amostragem por unidade monetária, com risco de amostragem de 5%, fator de confiança de 3,0, materialidade tolerável igual à materialidade de execução, distorção esperada de R$ 5 milhões e fator de expansão de 1,5. A amostra resultou em 299 itens. O limite superior de erro deve ser lido como resultado didático da população artificial, não como inferência sobre o cadastro real da companhia.

## Reprodutibilidade

Execute, a partir da raiz do repositório:

```bash
python3 codigo/01_gerar_base_imobilizado.py
python3 codigo/02_executar_testes_auditoria.py
```

Os hashes SHA-256 permitem conferir a integridade dos arquivos gerados. Alterações de versão de bibliotecas podem afetar compressão ou ordenação de empates; os controles monetários e a semente devem permanecer constantes.

## Limitações

Uma base simulada não substitui razão auxiliar, notas fiscais, laudos, inventário físico, contratos, registros de manutenção, trilhas de aprovação, arquivos de câmbio ou acesso a sistemas. Os resultados servem apenas para demonstrar desenho, execução e documentação de procedimentos acadêmicos.
