# Dicionário de dados da base sintética

| Campo | Tipo | Descrição e uso de auditoria |
|---|---|---|
| asset_id | texto | Identificador artificial único do ativo ou componente. |
| record_sequence | inteiro | Sequência de geração; auxilia a identificação do lançamento posterior em duplicidades. |
| entity | texto | Entidade ficticiamente atribuída dentro da estrutura pública do grupo. |
| plant_city | texto | Cidade da unidade, usada para escopo de componentes e inspeção planejada. |
| state_region | texto | Estado ou região. |
| country | texto | País, usado em riscos de moeda e auditoria de grupo. |
| functional_currency | texto | BRL, USD ou EUR. |
| asset_class | texto | Classe conciliável à Nota 13. |
| asset_description | texto | Descrição artificial do componente. |
| cost_center | texto | Centro de custo artificial. |
| custodian_area | texto | Área responsável artificial. |
| book_status | texto | Ativo ou em andamento. |
| acquisition_date | data | Data simulada de aquisição. |
| control_transfer_date | data | Data simulada em que controle/direitos são transferidos; usada no teste de corte. |
| in_service_date | data | Data disponível para uso. |
| depreciation_start_date | data | Data de início da depreciação. |
| posting_date | data | Data simulada de contabilização. |
| useful_life_months | inteiro | Vida útil em meses; zero para terreno e obras em andamento. |
| residual_value_brl | inteiro | Valor residual estimado em reais. |
| book_cost_brl | inteiro | Custo contábil de fechamento. |
| accumulated_depreciation_brl | inteiro | Depreciação acumulada positiva para apresentação analítica. |
| net_book_value_brl | inteiro | Custo menos depreciação acumulada. |
| additions_2025_brl | inteiro | Adições simuladas ancoradas ao total público da classe. |
| depreciation_expense_2025_brl | inteiro | Despesa simulada ancorada ao total público da classe. |
| impairment_recognized_2025_brl | inteiro | Perda simuladamente distribuída, fechando o impairment público por classe. |
| expected_monthly_depreciation_brl | decimal | Depreciação mensal calculada com custo, residual e vida útil. |
| book_monthly_depreciation_brl | decimal | Depreciação mensal registrada na simulação; usada no teste de taxa. |
| supplier_id | texto | Fornecedor artificial. |
| invoice_id | texto | Documento fiscal artificial; usado no teste de duplicidade. |
| support_status | texto | Situação do documento-suporte. |
| capex_approval_id | texto | Aprovação artificial de CAPEX; deve existir para adições. |
| physical_tag | texto | Plaqueta artificial. |
| physical_status | texto | Situação física simulada. |
| last_inventory_date | data | Data artificial do último inventário. |
| impairment_indicator | texto | Indica presença de gatilho de recuperabilidade. |
| impairment_assessment_status | texto | Situação da avaliação de impairment. |
| recoverable_amount_brl | inteiro | Valor recuperável artificial usado no teste E04. |
| capitalized_nature | texto | Natureza do gasto capitalizado. |
| closing_fx_rate_brl | decimal | Taxa sintética de fechamento por moeda. |
| applied_fx_rate_brl | decimal | Taxa aplicada no registro sintético. |
| local_cost_functional_currency | decimal | Custo na moeda funcional artificial. |
| pledged_as_collateral | texto | Indicação artificial de garantia. Não reconcilia individualmente os R$ 620 milhões divulgados. |
| insured | texto | Situação artificial de seguro. |
| source_system | texto | Sistema-fonte artificial. |

O arquivo `gabarito_erros_inseridos.csv.gz` acrescenta código e descrição do erro, assertiva, classificação, distorção, valor esperado e regra de detecção. Ele deve permanecer separado da base durante a execução dos testes.
