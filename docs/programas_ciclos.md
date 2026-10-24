# Programas de auditoria por ciclo

Todos os procedimentos estão rotulados. “Planejado” significa que nenhuma evidência foi obtida; “simulado” se refere apenas à base artificial; “público” se limita aos documentos catalogados.

## Receita, clientes e recebimentos

| ID | Assertiva | Procedimento | Classificação | Evidência esperada ou referência |
|---|---|---|---|---|
| REC-01 | Ocorrência e corte | Entender pedido, aprovação de crédito, expedição, aceite, faturamento e contabilização por segmento e país. | Planejado por falta de acesso | Walkthrough, telas, documentos e trilhas. |
| REC-02 | Ocorrência | Testar desenho e implementação do bloqueio de faturamento sem entrega/aceite. | Planejado por falta de acesso | Configuração e amostra de transações. |
| REC-03 | Corte | Selecionar documentos antes e depois de 31/12/2025 e rastrear entrega, transferência de controle e razão. | Planejado por falta de acesso | Conhecimento de transporte, NF e contrato. |
| REC-04 | Existência | Confirmar saldos de clientes, mantendo controle sobre pedidos e respostas. | Planejado por falta de acesso | Confirmações e alternativas. |
| REC-05 | Avaliação | Testar recebimentos subsequentes, aging, disputas, devoluções e perda esperada. | Planejado por falta de acesso | Extratos, aging e notas de crédito. |
| REC-06 | Exatidão | Analisar receita mensal, preço, volume, mix e margem contra expectativa independente. | Planejado por falta de acesso | Dados mensais e contratos. |
| REC-07 | Apresentação | Reconciliar Nota 27 e segmentos à DRE consolidada. | Realizado com evidência pública | F01, DRE e Notas 27/33. |
| REC-08 | Fraude | Testar lançamentos manuais em receita, fins de período, usuários privilegiados e combinações incomuns. | Planejado por falta de acesso | Razão e logs. |

## Caixa, financiamentos e derivativos

| ID | Assertiva | Procedimento | Classificação | Evidência esperada ou referência |
|---|---|---|---|---|
| TES-01 | Existência/direitos | Confirmar 100% dos bancos, saldos, aplicações, dívidas, garantias e derivativos. | Planejado por falta de acesso | Respostas diretas das instituições. |
| TES-02 | Exatidão | Reexecutar conciliações bancárias e verificar itens em trânsito subsequentes. | Planejado por falta de acesso | Extratos e razão. |
| TES-03 | Completude | Pesquisar passivos financeiros não registrados em extratos, atas, jurídico e pagamentos. | Planejado por falta de acesso | Documentos externos/internos. |
| TES-04 | Classificação | Inspecionar contratos e waivers e recalcular vencimentos e covenants. | Planejado por falta de acesso | Instrumentos assinados. |
| TES-05 | Avaliação | Recalcular custo amortizado, juros, câmbio e valor justo; testar dados observáveis. | Planejado por falta de acesso | Curvas e contratos. |
| TES-06 | Apresentação | Conciliar dívida, liquidez e risco financeiro às notas. | Realizado com evidência pública | F01, Notas 17, 18 e 38. |
| TES-07 | Continuidade | Testar projeções de caixa, headroom e sensibilidade. | Planejado por falta de acesso | Orçamento aprovado e cenários. |
| TES-08 | Eventos posteriores | Separar fatos até 19/03/2026 dos fatos conhecidos depois do relatório. | Realizado com evidência pública | PT-560; F01, F06 e F07. |

## Estoques, produção e custo dos produtos vendidos

| ID | Assertiva | Procedimento | Classificação | Evidência esperada ou referência |
|---|---|---|---|---|
| EST-01 | Existência | Observar contagens em locais materiais e imprevisíveis, executar contagens e controlar folhas. | Planejado por falta de acesso | Inventário físico. |
| EST-02 | Completude | Rastrear chão ao registro e registro ao chão; conciliar etiquetas e razão. | Planejado por falta de acesso | Listagens finais. |
| EST-03 | Corte | Testar entradas/saídas próximas à data-base e mercadorias em trânsito/terceiros. | Planejado por falta de acesso | NFs, recebimentos e expedições. |
| EST-04 | Avaliação | Testar matérias-primas a notas, custo padrão a real, absorção e capacidade normal. | Planejado por falta de acesso | Fichas, ordens e variações. |
| EST-05 | Avaliação | Recalcular provisão de giro lento, obsolescência e valor realizável líquido. | Planejado por falta de acesso | Aging, vendas e engenharia. |
| EST-06 | Analítico | Comparar estoque, CPV, volumes e margens; investigar redução de 21,7%. | Realizado com evidência pública | A-07/A-08; F01. |
| EST-07 | Apresentação | Reconciliar saldo e políticas às Notas 5 e 28. | Realizado com evidência pública | F01. |

## Imobilizado, CAPEX, depreciação e impairment

| ID | Assertiva | Procedimento | Classificação | Evidência esperada ou referência |
|---|---|---|---|---|
| IMO-01 | Completude/exatidão | Conciliar razão auxiliar ao razão geral, balanço e Nota 13 por classe. | Simulado para fins didáticos | A-03; diferença R$ 0 na base artificial. |
| IMO-02 | Ocorrência | Testar adições a aprovação, pedido, NF, recebimento, pagamento e natureza capitalizável. | Simulado para fins didáticos | E07/E09/E10 na base; real planejado. |
| IMO-03 | Corte/direitos | Comparar transferência de controle e data de registro. | Simulado para fins didáticos | E08 detectado; contratos reais não obtidos. |
| IMO-04 | Existência | Inspecionar fisicamente ativos selecionados e rastrear tags em ambas as direções. | Planejado por falta de acesso | Visita e cadastro real. |
| IMO-05 | Avaliação | Recalcular depreciação com custo, residual, vida útil e data disponível. | Simulado para fins didáticos | E02/E06 detectados. |
| IMO-06 | Existência/avaliação | Testar baixas a autorização, alienação e condição física. | Simulado para fins didáticos | E03 detectado. |
| IMO-07 | Avaliação | Avaliar UGC, método, dados, taxa, orçamento, sensibilidade e viés do impairment de Betim. | Planejado por falta de acesso | Modelo e especialista. |
| IMO-08 | Avaliação | Pesquisar indicadores sem teste e comparar valor recuperável. | Simulado para fins didáticos | E04 detectado. |
| IMO-09 | Apresentação | Recalcular rollforward agregado, garantias e vidas úteis. | Realizado com evidência pública | F01, pp. 46-48. |
| IMO-10 | Amostragem | Aplicar MUS/PPS e avaliar limite superior de erro. | Simulado para fins didáticos | A-05; população artificial não aceita. |

## Compras, fornecedores, dívidas e outros passivos

| ID | Assertiva | Procedimento | Classificação | Evidência esperada ou referência |
|---|---|---|---|---|
| PAS-01 | Completude | Pesquisar passivos não registrados em pagamentos posteriores, NFs pendentes, recebimentos e jurídico. | Planejado por falta de acesso | Razão e documentos. |
| PAS-02 | Ocorrência | Testar três documentos e alçadas de compras/pagamentos. | Planejado por falta de acesso | Pedido, recebimento e NF. |
| PAS-03 | Corte | Testar compras e serviços antes/depois de 31/12. | Planejado por falta de acesso | Documentação e razão. |
| PAS-04 | Existência/completude | Confirmar fornecedores materiais e com saldo zero/atividade relevante. | Planejado por falta de acesso | Respostas diretas. |
| PAS-05 | Classificação | Testar dívidas correntes/não correntes à luz de direitos existentes na data-base. | Planejado por falta de acesso | Contratos e waivers. |
| PAS-06 | Analítico | Comparar fornecedores, passivos e giro com 2024. | Realizado com evidência pública | A-07/A-08. |
| PAS-07 | Apresentação | Reconciliar Notas 16-25 e divulgações de liquidez. | Realizado com evidência pública | F01. |

## Estimativas contábeis

| ID | Estimativa | Procedimento | Classificação | Evidência esperada ou referência |
|---|---|---|---|---|
| ESTIM-01 | Todas | Entender processo, controles, método, dados, premissas e incerteza. | Planejado por falta de acesso | Walkthrough e documentação. |
| ESTIM-02 | Todas | Fazer revisão retrospectiva de estimativas anteriores. | Planejado por falta de acesso | Previsão versus realizado. |
| ESTIM-03 | Impairment | Testar UGC Betim, fluxos, taxa, orçamento, ativos excluídos e sensibilidade. | Planejado por falta de acesso | Modelo integral e especialista. |
| ESTIM-04 | Tributo diferido | Testar projeções de lucros tributáveis, prazo fiscal, consistência e sensibilidade. | Planejado por falta de acesso | Estudos por entidade. |
| ESTIM-05 | Estoques/recebíveis | Testar modelos de perda, segmentação, históricos e dados subsequentes. | Planejado por falta de acesso | Bases e recebimentos/vendas. |
| ESTIM-06 | Provisões | Confrontar jurídico, probabilidade, faixa e pagamentos subsequentes. | Planejado por falta de acesso | Cartas de advogados. |
| ESTIM-07 | Benefícios | Avaliar atuário, população, taxa de desconto, mortalidade e sensibilidade. | Planejado por falta de acesso | Laudo atuarial. |
| ESTIM-08 | Identificação | Identificar estimativas, saldos e duas KAMs nas fontes. | Realizado com evidência pública | PT-540; F01. |

## Cobertura complementar

Os ciclos tributário, folha/benefícios, provisões, consolidação, partes relacionadas, patrimônio líquido, fechamento e TI estão mapeados em `saidas/ciclos_auditoria.csv` e nos PT-250, PT-315, PT-402, PT-540, PT-550 e PT-600.
