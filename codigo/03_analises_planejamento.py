#!/usr/bin/env python3
"""Gera análises públicas, indicadores, ciclos e matriz de riscos do dossiê."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "saidas"


FINANCIAL_DATA = [
    ("Receitas", "DRE", 9_692_948_000, 10_665_110_000, "DF 2025, p. 20"),
    ("Custo dos produtos vendidos", "DRE", -8_469_797_000, -8_738_519_000, "DF 2025, p. 20"),
    ("Lucro bruto", "DRE", 1_223_151_000, 1_926_591_000, "DF 2025, p. 20"),
    ("Resultado antes do financeiro e tributos", "DRE", -156_481_000, 559_667_000, "DF 2025, p. 20"),
    ("Despesas financeiras", "DRE", -442_547_000, -400_941_000, "DF 2025, p. 20"),
    ("Lucro (prejuízo) líquido", "DRE", -654_552_000, 82_440_000, "DF 2025, p. 20"),
    ("Caixa e equivalentes", "Ativo", 1_853_156_000, 2_376_203_000, "DF 2025, p. 18"),
    ("Contas a receber", "Ativo", 1_597_455_000, 1_837_435_000, "DF 2025, p. 18"),
    ("Estoques", "Ativo", 1_721_952_000, 2_197_704_000, "DF 2025, p. 18"),
    ("Ativo circulante", "Ativo", 5_947_055_000, 7_460_379_000, "DF 2025, p. 18"),
    ("Ativo imobilizado", "Ativo", 2_525_157_000, 2_940_751_000, "DF 2025, p. 18 e Nota 13"),
    ("Ativo fiscal diferido líquido", "Ativo", 680_079_000, 846_275_000, "DF 2025, p. 18 e Nota 9"),
    ("Ativo total", "Ativo", 9_391_641_000, 11_510_863_000, "DF 2025, p. 18"),
    ("Fornecedores", "Passivo", 1_137_117_000, 1_482_620_000, "DF 2025, p. 19"),
    ("Passivo circulante", "Passivo", 2_478_815_000, 3_390_939_000, "DF 2025, p. 19"),
    ("Passivo não circulante", "Passivo", 4_399_450_000, 4_620_577_000, "DF 2025, p. 19"),
    ("Patrimônio líquido", "Patrimônio líquido", 2_513_376_000, 3_499_347_000, "DF 2025, p. 19"),
    ("Caixa operacional", "DFC", 915_137_000, 1_353_491_000, "DF 2025, p. 23"),
    ("Endividamento bruto ajustado", "Indicador não GAAP", 4_096_546_000, 4_792_385_000, "Relatório anual 2025, p. 15"),
    ("Endividamento líquido ajustado", "Indicador não GAAP", 2_211_687_000, 2_342_357_000, "Relatório anual 2025, p. 15"),
]


RISKS = [
    ("R01", "Imobilizado: impairment da UGC Betim e depreciação", "Ativo imobilizado", 5, 5, "SIM", "Avaliação/alocação; apresentação", "Premissas de valor recuperável, perda de R$ 324,791 milhões e saldo de R$ 2,525 bilhões", "Especialista; recálculo; sensibilidade; teste de dados; inspeção documental e física planejada", "NBC TA 315/330/540; CPC 01/CPC 27"),
    ("R02", "Realização de ativos fiscais diferidos", "Tributos diferidos", 5, 4, "SIM", "Avaliação; apresentação", "Projeções de lucros tributáveis; R$ 399,861 milhões ligados a prejuízos fiscais e base negativa", "Testar orçamento aprovado, premissas, histórico de acurácia, prazo de uso e divulgações", "NBC TA 315/330/540"),
    ("R03", "Reconhecimento de receita e corte", "Receitas e contas a receber", 5, 4, "SIM", "Ocorrência; corte; exatidão", "Presunção de risco de fraude em receita e contratos em múltiplas jurisdições", "Testes de corte, contratos, notas fiscais, recebimentos subsequentes, analíticos e lançamentos manuais", "NBC TA 240/315/330/500"),
    ("R04", "Existência e avaliação de estoques", "Estoques e CPV", 4, 4, "SIM", "Existência; avaliação; direitos", "Saldo de R$ 1,722 bilhão, múltiplas plantas, obsolescência e absorção de custos", "Observação física planejada, custo padrão versus real, obsolescência, corte e conciliação", "NBC TA 501/330/540"),
    ("R05", "Liquidez, covenants, classificação e continuidade", "Dívidas e divulgações", 5, 4, "SIM", "Classificação; completude; apresentação", "Waivers em dezembro, dívida líquida/EBITDA de 3,35x e garantias de R$ 620 milhões", "Inspecionar contratos/waivers, confirmar bancos, recalcular covenants e testar fluxo de caixa", "NBC TA 570/505/560"),
    ("R06", "Burla de controles pela administração", "Todas as contas", 5, 5, "SIM", "Todas, sobretudo ocorrência e classificação", "Risco obrigatório de fraude; estimativas relevantes e lançamentos de fechamento", "Testar lançamentos, estimativas tendenciosas e transações fora do curso normal", "NBC TA 240"),
    ("R07", "Conversão cambial e consolidação internacional", "Consolidação e ORA", 4, 4, "SIM", "Exatidão; completude; apresentação", "Componentes no México, Portugal e Países Baixos; USD e EUR; eliminações intragrupo", "Recalcular conversão, testar eliminações, pacotes de reporte e instruções a componentes", "NBC TA 315/600"),
    ("R08", "Provisões e passivos contingentes", "Provisões", 4, 4, "SIM", "Completude; avaliação; apresentação", "R$ 400,125 milhões entre curto e longo prazo, com julgamento jurídico", "Cartas a assessores jurídicos, atas, pagamentos subsequentes e avaliação de probabilidade", "NBC TA 501/505/540"),
    ("R09", "Integridade de sistemas e organizações de serviços", "Processamento contábil", 3, 4, "NAO", "Completude; exatidão", "Ambiente multicompanhia e múltiplos sistemas; dependência de controles gerais de TI", "Entender interfaces, acessos e mudanças; obter relatório tipo 2 quando aplicável", "NBC TA 315/402"),
    ("R10", "Partes relacionadas e transações não usuais", "Partes relacionadas", 3, 4, "NAO", "Completude; apresentação; ocorrência", "Estrutura de grupo, joint venture e acionistas relevantes", "Pesquisar atas/cadastros, conciliar saldos, revisar termos e obter representação formal", "NBC TA 550/580"),
    ("R11", "Benefícios a empregados e folha", "Salários e benefícios", 3, 4, "NAO", "Completude; avaliação; corte", "Obrigações de aposentadoria de R$ 120,418 milhões e operações em várias jurisdições", "Recalcular amostra, testar premissas atuariais, elegibilidade, folha e encargos", "NBC TA 540/500"),
    ("R12", "Caixa, derivativos e dívida", "Instrumentos financeiros", 3, 4, "NAO", "Existência; direitos; avaliação", "Caixa de R$ 1,853 bilhão, dívida e derivativos expostos a moeda e juros", "Confirmações externas, conciliações, valorização independente e revisão de hedge", "NBC TA 505/540"),
]


CYCLES = [
    ("C01", "Imobilizado, CAPEX, depreciação e impairment", "Imobilizado; adições; depreciação; impairment; garantias", "R01; R05", "Aprovação de CAPEX; segregação compra/recebimento/capitalização; inventário físico; revisão de vida útil; teste de impairment", "Existência; direitos; avaliação; corte; apresentação", "Crítica"),
    ("C02", "Receitas, clientes e recebimentos", "Receita; contas a receber; adiantamentos; perdas esperadas", "R03", "Cadastro e crédito; pedido-entrega-faturamento; bloqueios; conciliação de recebimentos; aprovação de notas manuais", "Ocorrência; corte; exatidão; existência", "Crítica"),
    ("C03", "Produção, estoques e custo", "Matéria-prima; produtos; CPV; obsolescência; ferramental", "R04", "Inventário cíclico; fechamento de ordens; custo padrão; análise de variações; provisão de obsolescência", "Existência; avaliação; completude; direitos", "Alta"),
    ("C04", "Tesouraria, financiamentos e derivativos", "Caixa; aplicações; empréstimos; debêntures; juros; derivativos", "R05; R12", "Conciliação bancária; dupla aprovação; limites; monitoramento de covenants; valorização independente", "Existência; direitos; avaliação; completude; apresentação", "Crítica"),
    ("C05", "Tributos correntes e diferidos", "Tributos a recuperar/pagar; IR/CS; ativo fiscal diferido", "R02", "Revisão fiscal; conciliação ECF; aprovação de projeções; rastreamento de créditos", "Avaliação; completude; apresentação", "Crítica"),
    ("C06", "Jurídico, provisões e contingências", "Provisões tributárias, cíveis, previdenciárias e trabalhistas", "R08", "Cadastro jurídico; conciliação jurídico-contábil; revisão por probabilidade; governança de acordos", "Completude; avaliação; apresentação", "Alta"),
    ("C07", "Pessoal e benefícios", "Folha; encargos; participação; aposentadoria e saúde", "R11", "Integração RH-folha; aprovação de alterações; conciliação de encargos; revisão atuarial", "Ocorrência; completude; avaliação; corte", "Alta"),
    ("C08", "Compras, fornecedores e pagamentos", "Compras; fornecedores; títulos a pagar", "R06", "Alçadas; três documentos; segregação; cadastro de fornecedores; dupla aprovação de pagamento", "Completude; ocorrência; corte; classificação", "Alta"),
    ("C09", "Consolidação e operações no exterior", "Pacotes; conversão; eliminações; participação de não controladores", "R07", "Plano de contas uniforme; validações do pacote; taxas aprovadas; eliminações e revisão central", "Completude; exatidão; apresentação", "Crítica"),
    ("C10", "Partes relacionadas, investimentos e patrimônio líquido", "Saldos intragrupo; dividendos; capital; ações em tesouraria", "R10", "Cadastro de partes; aprovação por governança; conciliações bilaterais; revisão de divulgações", "Completude; ocorrência; apresentação", "Alta"),
    ("C11", "Fechamento financeiro, TI e lançamentos", "Razão geral; lançamentos; interfaces; demonstrações e notas", "R06; R09", "Calendário de fechamento; acessos; gestão de mudanças; aprovação de lançamentos; checklist de divulgação", "Todas", "Crítica"),
]


def make_financial_tables() -> None:
    df = pd.DataFrame(FINANCIAL_DATA, columns=["line_item", "statement", "fy2025_brl", "fy2024_brl", "source"])
    df["absolute_change_brl"] = df["fy2025_brl"] - df["fy2024_brl"]
    df["percentage_change"] = df["absolute_change_brl"] / df["fy2024_brl"].abs()
    df.to_csv(OUT / "dados_financeiros_publicos.csv", index=False)

    v = {row[0]: {2025: row[2], 2024: row[3]} for row in FINANCIAL_DATA}
    liabilities_2025 = v["Passivo circulante"][2025] + v["Passivo não circulante"][2025]
    liabilities_2024 = v["Passivo circulante"][2024] + v["Passivo não circulante"][2024]
    indicators = [
        ("Liquidez corrente", v["Ativo circulante"][2025] / v["Passivo circulante"][2025], v["Ativo circulante"][2024] / v["Passivo circulante"][2024], "vezes"),
        ("Liquidez seca", (v["Ativo circulante"][2025] - v["Estoques"][2025]) / v["Passivo circulante"][2025], (v["Ativo circulante"][2024] - v["Estoques"][2024]) / v["Passivo circulante"][2024], "vezes"),
        ("Caixa sobre passivo circulante", v["Caixa e equivalentes"][2025] / v["Passivo circulante"][2025], v["Caixa e equivalentes"][2024] / v["Passivo circulante"][2024], "vezes"),
        ("Passivos sobre ativos", liabilities_2025 / v["Ativo total"][2025], liabilities_2024 / v["Ativo total"][2024], "%"),
        ("Imobilizado sobre ativos", v["Ativo imobilizado"][2025] / v["Ativo total"][2025], v["Ativo imobilizado"][2024] / v["Ativo total"][2024], "%"),
        ("Margem bruta", v["Lucro bruto"][2025] / v["Receitas"][2025], v["Lucro bruto"][2024] / v["Receitas"][2024], "%"),
        ("Margem operacional antes do financeiro e tributos", v["Resultado antes do financeiro e tributos"][2025] / v["Receitas"][2025], v["Resultado antes do financeiro e tributos"][2024] / v["Receitas"][2024], "%"),
        ("Margem líquida", v["Lucro (prejuízo) líquido"][2025] / v["Receitas"][2025], v["Lucro (prejuízo) líquido"][2024] / v["Receitas"][2024], "%"),
        ("Caixa operacional sobre receita", v["Caixa operacional"][2025] / v["Receitas"][2025], v["Caixa operacional"][2024] / v["Receitas"][2024], "%"),
        ("Dívida líquida sobre EBITDA ajustado", 3.35, 1.81, "vezes (indicador divulgado)"),
        ("Dívida bruta sobre EBITDA ajustado", 6.20, 3.70, "vezes (indicador divulgado)"),
    ]
    ind = pd.DataFrame(indicators, columns=["indicator", "fy2025", "fy2024", "unit"])
    ind["change"] = ind["fy2025"] - ind["fy2024"]
    ind.to_csv(OUT / "indicadores_financeiros.csv", index=False)


def make_risk_and_cycle_tables() -> None:
    risk = pd.DataFrame(
        RISKS,
        columns=["risk_id", "risk", "account_cycle", "impact", "likelihood", "significant_risk", "critical_assertions", "public_basis", "audit_response", "standards"],
    )
    risk["inherent_score"] = risk["impact"] * risk["likelihood"]
    risk["risk_level"] = pd.cut(risk["inherent_score"], bins=[0, 8, 14, 19, 25], labels=["Baixo", "Moderado", "Alto", "Crítico"])
    risk.to_csv(OUT / "matriz_riscos.csv", index=False)

    cycles = pd.DataFrame(
        CYCLES,
        columns=["cycle_id", "cycle", "transactions_balances", "linked_risks", "key_controls_to_test", "critical_assertions", "priority"],
    )
    cycles.to_csv(OUT / "ciclos_auditoria.csv", index=False)


def make_going_concern_table() -> None:
    rows = [
        ("Indicador adverso", "Prejuízo líquido consolidado", -654_552_000, "2025", "DF 2025, p. 20", "Pressiona patrimônio e cobertura de obrigações."),
        ("Indicador adverso", "Resultado antes do financeiro e tributos", -156_481_000, "2025", "DF 2025, p. 20", "Evidencia perda operacional no exercício."),
        ("Indicador adverso", "Dívida líquida/EBITDA ajustado", 3.35, "2025", "Relatório anual 2025, p. 15", "Aumento frente a 1,81x em 2024."),
        ("Indicador adverso", "Waivers e garantias de imobilizado", 620_000_000, "Q4 2025 a Q3 2027", "DF 2025, Nota 13e e Nota 17h", "Exige inspeção dos termos, classificação e projeções."),
        ("Fator mitigante", "Caixa e equivalentes", 1_853_156_000, "31/12/2025", "DF 2025, p. 18", "Reserva de liquidez relevante."),
        ("Fator mitigante", "Caixa gerado nas atividades operacionais", 915_137_000, "2025", "DF 2025, p. 23", "Geração operacional positiva."),
        ("Fator mitigante", "Liquidez corrente", 2.3992, "31/12/2025", "Cálculo a partir das DFs", "Ativo circulante excede o passivo circulante."),
        ("Fator mitigante", "Adimplência com cláusulas restritivas", 1, "31/12/2025", "DF 2025, Nota 17h", "Administração declara cumprimento após waivers."),
        ("Informação posterior ao relatório", "Financiamento BNDES contratado", 600_000_000, "27/07/2026", "ITR 2T26, Nota 31", "Não integra a evidência disponível em 19/03/2026; usado apenas como acompanhamento posterior."),
    ]
    pd.DataFrame(rows, columns=["classification", "factor", "amount_or_ratio", "period", "source", "audit_relevance"]).to_csv(
        OUT / "avaliacao_continuidade.csv", index=False
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    make_financial_tables()
    make_risk_and_cycle_tables()
    make_going_concern_table()
    print("Análises de planejamento geradas.")


if __name__ == "__main__":
    main()
