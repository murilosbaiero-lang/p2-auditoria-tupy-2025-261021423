import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = process.env.PROJECT_ROOT;
if (!root) throw new Error("Defina PROJECT_ROOT com a raiz do projeto");
const outDir = path.join(root, "planilhas");
const qaDir = path.join(root, "tmp", "qa_xlsx");

function parseCsv(text) {
  const rows = [];
  let row = [], field = "", quoted = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (quoted) {
      if (ch === '"' && text[i + 1] === '"') { field += '"'; i++; }
      else if (ch === '"') quoted = false;
      else field += ch;
    } else {
      if (ch === '"') quoted = true;
      else if (ch === ',') { row.push(field); field = ""; }
      else if (ch === '\n') { row.push(field.replace(/\r$/, "")); rows.push(row); row = []; field = ""; }
      else field += ch;
    }
  }
  if (field.length || row.length) { row.push(field.replace(/\r$/, "")); rows.push(row); }
  const headers = rows.shift();
  return rows.filter(r => r.some(v => v !== "")).map(r => Object.fromEntries(headers.map((h, i) => [h, r[i] ?? ""])));
}

async function readCsv(rel) {
  return parseCsv(await fs.readFile(path.join(root, rel), "utf8"));
}

const wb = Workbook.create();
const navy = "#17365D", blue = "#D9EAF7", pale = "#F3F6F9", gray = "#D9D9D9", red = "#FCE8E6", amber = "#FFF2CC", green = "#E2F0D9";

function addSheet(name, tabColor = navy) {
  const sh = wb.worksheets.add(name);
  sh.showGridLines = false;
  sh.tabColor = tabColor;
  return sh;
}

function applyTitle(sh, title, subtitle, width = "H") {
  const bar = sh.getRange(`A1:${width}1`);
  bar.format.fill = navy;
  bar.format.font = { color: "#FFFFFF", bold: true, size: 16, name: "Arial" };
  bar.format.rowHeight = 28;
  sh.getRange("A1").values = [[title]];
  sh.getRange("A2").values = [[subtitle]];
  sh.getRange(`A2:${width}2`).format.font = { color: "#595959", italic: true, size: 10, name: "Arial" };
  sh.getRange(`A1:${width}2`).format.verticalAlignment = "center";
}

function styleHeader(range) {
  range.format.fill = navy;
  range.format.font = { color: "#FFFFFF", bold: true, size: 10, name: "Arial" };
  range.format.borders = { preset: "all", style: "thin", color: gray };
  range.format.wrapText = true;
  range.format.verticalAlignment = "center";
  range.format.horizontalAlignment = "center";
  range.format.rowHeight = 30;
}

function styleBody(range) {
  range.format.font = { color: "#000000", size: 10, name: "Arial" };
  range.format.borders = { preset: "all", style: "thin", color: gray };
  range.format.verticalAlignment = "center";
}

function formatMoney(range) { range.format.numberFormat = '#,##0;[Red](#,##0);-'; }
function formatPercent(range) { range.format.numberFormat = '0.0%;[Red](0.0%);-'; }
function formatRatio(range) { range.format.numberFormat = '0.00x;[Red](0.00x);-'; }

// 1. Resumo
const summary = addSheet("Resumo", "#1F4E78");
applyTitle(summary, "Auditoria acadêmica Tupy 2025", "Resumo executivo dos cálculos, riscos e resultados simulados", "L");
summary.getRange("A4:F4").values = [["Materialidade global", "", "Materialidade de execução", "", "Imobilizado líquido", ""]];
summary.getRange("A4:F4").format.fill = blue;
summary.getRange("A4:F4").format.font = { bold: true, color: navy, size: 10, name: "Arial" };
summary.getRange("A5").formulas = [["=Materialidade!B6"]];
summary.getRange("C5").formulas = [["=Materialidade!B8"]];
summary.getRange("E5").formulas = [["=Imobilizado!I12"]];
formatMoney(summary.getRange("A5:F5"));
summary.getRange("A5:F5").format.font = { bold: true, size: 14, color: navy, name: "Arial" };
summary.getRange("A7:F7").values = [["Distorção líquida simulada", "", "Limite superior MUS", "", "Conclusão MUS", ""]];
summary.getRange("A7:F7").format.fill = blue;
summary.getRange("A7:F7").format.font = { bold: true, color: navy, size: 10, name: "Arial" };
summary.getRange("A8").formulas = [["=Distorções!F15"]];
summary.getRange("C8").formulas = [["=MUS!B20"]];
summary.getRange("E8").formulas = [["=MUS!B21"]];
formatMoney(summary.getRange("A8:D8"));
summary.getRange("A8:F8").format.font = { bold: true, size: 13, color: "#9C0006", name: "Arial" };
summary.getRange("A10:L10").values = [["Limite de interpretação", "", "", "", "", "", "", "", "", "", "", ""]];
summary.getRange("A10:L10").format.fill = pale;
summary.getRange("A10").format.font = { bold: true, color: navy, name: "Arial" };
summary.getRange("A11:L11").values = [["Os registros e erros do imobilizado são artificiais. Resultados simulados não são constatações sobre a Tupy e este arquivo não emite opinião independente.", "", "", "", "", "", "", "", "", "", "", ""]];
summary.mergeCells("A11:L11");
summary.getRange("A11:L11").format.wrapText = true;
summary.getRange("A11:L11").format.rowHeight = 36;
summary.getRange("A13:C18").values = [
  ["Métrica", "2024 (R$ milhões)", "2025 (R$ milhões)"],
  ["Receita", 10665.110, 9692.948],
  ["Lucro bruto", 1926.591, 1223.151],
  ["Resultado operacional", 559.667, -156.481],
  ["Resultado líquido", 82.440, -654.552],
  ["Caixa operacional", 1353.491, 915.137],
];
styleHeader(summary.getRange("A13:C13")); styleBody(summary.getRange("A14:C18"));
summary.getRange("B14:C18").format.numberFormat = '#,##0.0;[Red](#,##0.0);-';
try {
  const chart = summary.charts.add("column", summary.getRange("A13:C18"));
  chart.titleText = "Desempenho consolidado 2024 e 2025 (R$ milhões)";
  chart.hasLegend = true;
  chart.legend.position = "bottom";
  chart.setPosition("E13", "L29");
} catch (e) {
  // A tabela permanece como representação exata se o mecanismo de gráfico não estiver disponível.
}
summary.getRange("A:L").format.columnWidth = 14;
summary.getRange("A:A").format.columnWidth = 24;
summary.getRange("E:E").format.columnWidth = 22;

// 2. Materialidade
const mat = addSheet("Materialidade", "#70AD47");
applyTitle(mat, "Materialidade de auditoria", "Benchmark, percentuais e limites em reais", "F");
mat.getRange("A4:C4").values = [["Parâmetro", "Valor", "Justificativa"]]; styleHeader(mat.getRange("A4:C4"));
mat.getRange("A5:C10").values = [
  ["Ativo total consolidado", 9391641000, "Saldo público em 31/12/2025"],
  ["Materialidade global", null, "0,5% do ativo total"],
  ["Percentual de execução", 0.70, "Julgamento: riscos significativos e grupo internacional"],
  ["Materialidade de execução", null, "70% da materialidade global"],
  ["Percentual claramente trivial", 0.05, "5% da materialidade global"],
  ["Limite claramente trivial", null, "Limiar para acumulação de distorções"],
];
mat.getRange("B6").formulas = [["=B5*0.5%"]];
mat.getRange("B8").formulas = [["=B6*B7"]];
mat.getRange("B10").formulas = [["=B6*B9"]];
styleBody(mat.getRange("A5:C10")); formatMoney(mat.getRange("B5:B6")); formatPercent(mat.getRange("B7")); formatMoney(mat.getRange("B8")); formatPercent(mat.getRange("B9")); formatMoney(mat.getRange("B10"));
mat.getRange("A12:C15").values = [
  ["Benchmark alternativo", "Cálculo", "Leitura"],
  ["0,5% da receita", 48464740, "Próximo ao ativo; não escolhido"],
  ["Resultado líquido", -654552000, "Inadequado por prejuízo e volatilidade"],
  ["Conclusão", 46958205, "Ativo é mais estável e relevante para entidade intensiva em ativos"],
];
styleHeader(mat.getRange("A12:C12")); styleBody(mat.getRange("A13:C15")); formatMoney(mat.getRange("B13:B15"));
mat.getRange("A:A").format.columnWidth = 30; mat.getRange("B:B").format.columnWidth = 20; mat.getRange("C:C").format.columnWidth = 64; mat.getRange("C5:C15").format.wrapText = true;

// 3. Demonstrações
const financial = addSheet("Demonstrações", "#5B9BD5");
applyTitle(financial, "Dados financeiros públicos", "Valores consolidados em reais; fontes e variações", "G");
const financialRows = await readCsv("saidas/dados_financeiros_publicos.csv");
financial.getRange("A4:G4").values = [["Linha", "Demonstração", "2025", "2024", "Variação", "Variação %", "Fonte"]]; styleHeader(financial.getRange("A4:G4"));
const finVals = financialRows.map(r => [r.line_item, r.statement, Number(r.fy2025_brl), Number(r.fy2024_brl), null, null, r.source]);
financial.getRange(`A5:G${4+finVals.length}`).values = finVals;
financial.getRange("E5").formulas = [["=C5-D5"]]; financial.getRange(`E5:E${4+finVals.length}`).fillDown();
financial.getRange("F5").formulas = [["=IFERROR(E5/ABS(D5),0)"]]; financial.getRange(`F5:F${4+finVals.length}`).fillDown();
styleBody(financial.getRange(`A5:G${4+finVals.length}`)); formatMoney(financial.getRange(`C5:E${4+finVals.length}`)); formatPercent(financial.getRange(`F5:F${4+finVals.length}`));
financial.freezePanes.freezeRows(4);
financial.getRange("A:A").format.columnWidth = 38; financial.getRange("B:B").format.columnWidth = 20; financial.getRange("C:F").format.columnWidth = 18; financial.getRange("G:G").format.columnWidth = 30;

// 4. Indicadores
const indicators = addSheet("Indicadores", "#5B9BD5");
applyTitle(indicators, "Indicadores financeiros", "Comparação de 2025 com 2024", "E");
const indRows = await readCsv("saidas/indicadores_financeiros.csv");
indicators.getRange("A4:E4").values = [["Indicador", "2025", "2024", "Variação", "Unidade"]]; styleHeader(indicators.getRange("A4:E4"));
indicators.getRange(`A5:E${4+indRows.length}`).values = indRows.map(r => [r.indicator, Number(r.fy2025), Number(r.fy2024), Number(r.change), r.unit]);
styleBody(indicators.getRange(`A5:E${4+indRows.length}`));
for (let i=0;i<indRows.length;i++) {
  const row=5+i, unit=indRows[i].unit;
  if (unit === "%") formatPercent(indicators.getRange(`B${row}:D${row}`)); else formatRatio(indicators.getRange(`B${row}:D${row}`));
}
indicators.getRange("A:A").format.columnWidth = 48; indicators.getRange("B:D").format.columnWidth = 16; indicators.getRange("E:E").format.columnWidth = 28;

// 5. Riscos
const risks = addSheet("Riscos", "#C00000");
applyTitle(risks, "Matriz de riscos de auditoria", "Avaliação acadêmica; não representa achados ou ratings da companhia", "K");
const riskRows = await readCsv("saidas/matriz_riscos.csv");
risks.getRange("A4:K4").values = [["ID", "Risco", "Conta/ciclo", "Impacto", "Probabilidade", "Escore", "Nível", "Significativo", "Assertivas", "Resposta", "Normas"]]; styleHeader(risks.getRange("A4:K4"));
risks.getRange(`A5:K${4+riskRows.length}`).values = riskRows.map(r => [r.risk_id,r.risk,r.account_cycle,Number(r.impact),Number(r.likelihood),Number(r.inherent_score),r.risk_level,r.significant_risk,r.critical_assertions,r.audit_response,r.standards]);
styleBody(risks.getRange(`A5:K${4+riskRows.length}`)); risks.getRange(`B5:C${4+riskRows.length}`).format.wrapText = true; risks.getRange(`H5:K${4+riskRows.length}`).format.wrapText = true;
risks.getRange(`F5:F${4+riskRows.length}`).conditionalFormats.add("cellIs", {operator:"greaterThanOrEqual", formula:20, format:{fill:red,font:{bold:true,color:"#9C0006"}}});
risks.getRange(`F5:F${4+riskRows.length}`).conditionalFormats.add("cellIs", {operator:"between", formula:[15,19], format:{fill:amber,font:{bold:true,color:"#7F6000"}}});
risks.freezePanes.freezeRows(4); risks.freezePanes.freezeColumns(1);
risks.getRange("A:A").format.columnWidth=9; risks.getRange("B:B").format.columnWidth=44; risks.getRange("C:C").format.columnWidth=23; risks.getRange("D:F").format.columnWidth=12; risks.getRange("G:H").format.columnWidth=15; risks.getRange("I:I").format.columnWidth=28; risks.getRange("J:J").format.columnWidth=55; risks.getRange("K:K").format.columnWidth=24;

// 6. Ciclos
const cycles = addSheet("Ciclos", "#C55A11");
applyTitle(cycles, "Ciclos de auditoria", "Transações, riscos, controles e assertivas", "G");
const cycleRows = await readCsv("saidas/ciclos_auditoria.csv");
cycles.getRange("A4:G4").values = [["ID", "Ciclo", "Transações e saldos", "Riscos", "Controles-chave", "Assertivas", "Prioridade"]]; styleHeader(cycles.getRange("A4:G4"));
cycles.getRange(`A5:G${4+cycleRows.length}`).values = cycleRows.map(r=>[r.cycle_id,r.cycle,r.transactions_balances,r.linked_risks,r.key_controls_to_test,r.critical_assertions,r.priority]);
styleBody(cycles.getRange(`A5:G${4+cycleRows.length}`)); cycles.getRange(`B5:F${4+cycleRows.length}`).format.wrapText=true;
cycles.freezePanes.freezeRows(4); cycles.getRange("A:A").format.columnWidth=9; cycles.getRange("B:B").format.columnWidth=38; cycles.getRange("C:C").format.columnWidth=42; cycles.getRange("D:D").format.columnWidth=14; cycles.getRange("E:E").format.columnWidth=62; cycles.getRange("F:F").format.columnWidth=36; cycles.getRange("G:G").format.columnWidth=13;

// 7. Imobilizado
const ppe = addSheet("Imobilizado", "#8064A2");
applyTitle(ppe, "Conciliação do imobilizado sintético", "Fechamento por classe à Nota 13 da Tupy S.A. em 31/12/2025", "M");
const reconRows = await readCsv("saidas/conciliacao_imobilizado.csv");
ppe.getRange("A4:M4").values = [["Classe", "Custo público", "Custo base", "Dif. custo", "Deprec. pública", "Deprec. base", "Dif. deprec.", "Líquido público", "Líquido base", "Dif. líquido", "Adições 2025", "Deprec. 2025", "Impairment 2025"]]; styleHeader(ppe.getRange("A4:M4"));
ppe.getRange(`A5:M${4+reconRows.length}`).values = reconRows.map(r=>[r.asset_class,Number(r.public_gross_brl),Number(r.book_cost_brl),null,Number(r.public_accum_dep_brl),Number(r.accumulated_depreciation_brl),null,Number(r.public_net_brl),Number(r.net_book_value_brl),null,Number(r.additions_2025_brl),Number(r.depreciation_expense_2025_brl),Number(r.impairment_recognized_2025_brl)]);
ppe.getRange("D5").formulas=[["=C5-B5"]]; ppe.getRange(`D5:D${4+reconRows.length}`).fillDown();
ppe.getRange("G5").formulas=[["=F5-E5"]]; ppe.getRange(`G5:G${4+reconRows.length}`).fillDown();
ppe.getRange("J5").formulas=[["=I5-H5"]]; ppe.getRange(`J5:J${4+reconRows.length}`).fillDown();
styleBody(ppe.getRange(`A5:M${4+reconRows.length}`)); formatMoney(ppe.getRange(`B5:M${4+reconRows.length}`));
ppe.getRange(`A${4+reconRows.length}:M${4+reconRows.length}`).format.fill=blue; ppe.getRange(`A${4+reconRows.length}:M${4+reconRows.length}`).format.font={bold:true,color:navy,name:"Arial"};
ppe.freezePanes.freezeRows(4); ppe.getRange("A:A").format.columnWidth=40; ppe.getRange("B:M").format.columnWidth=17;

// 8. Testes 100%
const tests = addSheet("Testes 100%", "#8064A2");
applyTitle(tests, "Testes automatizados da população", "Execução sobre 520.000 registros artificiais", "K");
const testRows = await readCsv("saidas/resultados_testes_100_percento.csv");
tests.getRange("A4:K4").values = [["Código", "Procedimento", "População", "Esperadas", "Detectadas", "VP", "FP", "FN", "Distorção", "Resultado", "Classificação"]]; styleHeader(tests.getRange("A4:K4"));
tests.getRange(`A5:K${4+testRows.length}`).values = testRows.map(r=>[r.test_code,r.procedure,Number(r.population_records),Number(r.expected_exceptions),Number(r.detected_exceptions),Number(r.true_positives),Number(r.false_positives),Number(r.false_negatives),Number(r.detected_misstatement_brl),r.test_result,r.procedure_classification]);
styleBody(tests.getRange(`A5:K${4+testRows.length}`)); formatMoney(tests.getRange(`I5:I${4+testRows.length}`)); tests.getRange(`B5:B${4+testRows.length}`).format.wrapText=true; tests.getRange(`J5:J${4+testRows.length}`).format.fill=green;
tests.getRange("A:A").format.columnWidth=10; tests.getRange("B:B").format.columnWidth=64; tests.getRange("C:I").format.columnWidth=14; tests.getRange("J:J").format.columnWidth=16; tests.getRange("K:K").format.columnWidth=28;

// 9. Distorções
const mis = addSheet("Distorções", "#8064A2");
applyTitle(mis, "Distorções e exceções artificiais", "Sinal positivo significa superavaliação do valor contábil", "H");
const misRows = await readCsv("saidas/resumo_erros_inseridos.csv");
mis.getRange("A4:H4").values = [["Código", "Descrição", "Assertiva", "Classificação", "Registros", "Distorção líquida", "Distorção absoluta", "% materialidade"]]; styleHeader(mis.getRange("A4:H4"));
mis.getRange(`A5:H${4+misRows.length}`).values = misRows.map(r=>[r.error_code,r.error_description,r.assertion,r.classification,Number(r.records),Number(r.net_misstatement_brl),Number(r.absolute_misstatement_brl),null]);
mis.getRange("H5").formulas=[["=ABS(F5)/Materialidade!$B$6"]]; mis.getRange(`H5:H${4+misRows.length}`).fillDown();
styleBody(mis.getRange(`A5:H${4+misRows.length}`)); formatMoney(mis.getRange(`F5:G${4+misRows.length}`)); formatPercent(mis.getRange(`H5:H${4+misRows.length}`));
const totalRow=5+misRows.length;
mis.getRange(`A${totalRow}:H${totalRow}`).values=[["TOTAL","","","",null,null,null,null]];
mis.getRange(`E${totalRow}`).formulas=[[`=SUM(E5:E${totalRow-1})`]]; mis.getRange(`F${totalRow}`).formulas=[[`=SUM(F5:F${totalRow-1})`]]; mis.getRange(`G${totalRow}`).formulas=[[`=SUM(G5:G${totalRow-1})`]]; mis.getRange(`H${totalRow}`).formulas=[[`=ABS(F${totalRow})/Materialidade!$B$6`]];
styleBody(mis.getRange(`A${totalRow}:H${totalRow}`)); mis.getRange(`A${totalRow}:H${totalRow}`).format.fill=blue; mis.getRange(`A${totalRow}:H${totalRow}`).format.font={bold:true,color:navy,name:"Arial"}; formatMoney(mis.getRange(`F${totalRow}:G${totalRow}`)); formatPercent(mis.getRange(`H${totalRow}`));
mis.getRange("A:A").format.columnWidth=10; mis.getRange("B:B").format.columnWidth=48; mis.getRange("C:D").format.columnWidth=28; mis.getRange("E:H").format.columnWidth=18;

// 10. MUS
const mus = addSheet("MUS", "#8064A2");
applyTitle(mus, "Amostragem por unidade monetária", "Planejamento e avaliação sobre a população artificial", "D");
const musData = JSON.parse(await fs.readFile(path.join(root,"saidas","avaliacao_MUS.json"),"utf8"));
const musRows = [
  ["Valor da população", musData.population_value_brl, "Entrada"],
  ["Risco de amostragem", musData.sampling_risk, "Entrada"],
  ["Fator de confiança", musData.confidence_factor_planning, "Entrada"],
  ["Distorção tolerável", musData.tolerable_misstatement_brl, "Entrada"],
  ["Distorção esperada", musData.expected_misstatement_brl, "Entrada"],
  ["Fator de expansão", musData.expansion_factor, "Entrada"],
  ["Tamanho planejado", musData.planned_sample_size, "Cálculo"],
  ["Tamanho efetivo", musData.actual_unique_sample_size, "Resultado"],
  ["Intervalo sistemático", musData.systematic_interval_brl, "Cálculo"],
  ["Início aleatório", musData.random_start_brl, "Cálculo"],
  ["Itens com erro", musData.sample_error_items, "Resultado"],
  ["Distorção observada assinada", musData.actual_signed_sample_misstatement_brl, "Resultado"],
  ["Distorção absoluta projetada", musData.projected_absolute_misstatement_brl, "Resultado"],
  ["Precisão básica", musData.basic_precision_brl, "Resultado"],
  ["Margem incremental", musData.incremental_allowance_brl, "Resultado"],
  ["Limite superior de erro", musData.upper_error_limit_brl, "Resultado"],
  ["Conclusão", musData.conclusion, "Resultado"],
];
mus.getRange("A4:C4").values=[["Parâmetro","Valor","Natureza"]]; styleHeader(mus.getRange("A4:C4")); mus.getRange(`A5:C${4+musRows.length}`).values=musRows; styleBody(mus.getRange(`A5:C${4+musRows.length}`));
formatMoney(mus.getRange("B5")); formatPercent(mus.getRange("B6")); formatMoney(mus.getRange("B8:B9")); formatMoney(mus.getRange("B13:B20"));
mus.getRange("B21").format.fill=red; mus.getRange("B21").format.font={bold:true,color:"#9C0006",name:"Arial"};
mus.getRange("A:A").format.columnWidth=42; mus.getRange("B:B").format.columnWidth=28; mus.getRange("C:C").format.columnWidth=18;
mus.getRange("A23:C24").values=[["Limitação","", ""],[musData.limitation,"",""]]; mus.getRange("A24:C24").format.wrapText=true; mus.getRange("A24:C24").format.rowHeight=42;

// 11. Continuidade
const going = addSheet("Continuidade", "#C00000");
applyTitle(going, "Continuidade operacional", "Indicadores adversos, fatores mitigantes e informação posterior", "F");
const goingRows=await readCsv("saidas/avaliacao_continuidade.csv");
going.getRange("A4:F4").values=[["Classificação","Fator","Valor/índice","Período","Fonte","Relevância"]]; styleHeader(going.getRange("A4:F4"));
going.getRange(`A5:F${4+goingRows.length}`).values=goingRows.map(r=>[r.classification,r.factor,Number(r.amount_or_ratio),r.period,r.source,r.audit_relevance]); styleBody(going.getRange(`A5:F${4+goingRows.length}`));
going.getRange(`A5:F${4+goingRows.length}`).format.wrapText=true; going.getRange(`A5:A${4+goingRows.length}`).conditionalFormats.add("containsText",{text:"Indicador adverso",format:{fill:red,font:{bold:true,color:"#9C0006"}}}); going.getRange(`A5:A${4+goingRows.length}`).conditionalFormats.add("containsText",{text:"Fator mitigante",format:{fill:green,font:{bold:true,color:"#006100"}}});
going.getRange("A:A").format.columnWidth=29; going.getRange("B:B").format.columnWidth=44; going.getRange("C:C").format.columnWidth=20; going.getRange("D:D").format.columnWidth=18; going.getRange("E:E").format.columnWidth=30; going.getRange("F:F").format.columnWidth=58;

// 12. Fontes
const sources = addSheet("Fontes", "#A5A5A5");
applyTitle(sources, "Matriz de fontes", "Documentos primários, período, páginas, URL e finalidade", "I");
const sourceRows=await readCsv("fontes/fontes.csv");
sources.getRange("A4:I4").values=[["ID","Documento","Emissor","Período/versão","Publicação","Acesso","Páginas","URL","Finalidade"]]; styleHeader(sources.getRange("A4:I4"));
sources.getRange(`A5:I${4+sourceRows.length}`).values=sourceRows.map(r=>[r.source_id,r.document,r.issuer,r.period_or_version,r.publication_or_submission_date,r.access_date,r.pages_used,r.url,r.purpose]); styleBody(sources.getRange(`A5:I${4+sourceRows.length}`)); sources.getRange(`B5:I${4+sourceRows.length}`).format.wrapText=true;
sources.freezePanes.freezeRows(4); sources.getRange("A:A").format.columnWidth=8; sources.getRange("B:B").format.columnWidth=42; sources.getRange("C:C").format.columnWidth=30; sources.getRange("D:G").format.columnWidth=20; sources.getRange("H:H").format.columnWidth=72; sources.getRange("I:I").format.columnWidth=52;

// 13. Leia-me
const readme = addSheet("Leia-me", "#A5A5A5");
applyTitle(readme, "Como usar esta planilha", "Cálculos acadêmicos de auditoria para o exercício de 2025", "F");
readme.getRange("A4:B12").values=[
  ["Tema","Orientação"],
  ["Escopo","Tupy S.A. e controladas, 31/12/2025."],
  ["Unidade","Valores financeiros armazenados em reais; a fonte pública apresenta R$ mil."],
  ["Entradas públicas","Demonstrações, notas, CVM, B3, RI e Formulário de Referência."],
  ["Base sintética","520.000 registros artificiais; somente os totais agregados vêm da Nota 13."],
  ["Cores de fórmulas","Fórmulas internas em preto; links entre abas em verde quando aplicável."],
  ["Resultado MUS","Aplica-se somente à população artificial."],
  ["Revisão","Campo de revisor permanece em branco; não foi fabricada segunda revisão."],
  ["Limite","A planilha não constitui auditoria, opinião, recomendação de investimento ou parecer jurídico."],
];
styleHeader(readme.getRange("A4:B4")); styleBody(readme.getRange("A5:B12")); readme.getRange("B5:B12").format.wrapText=true; readme.getRange("A:A").format.columnWidth=25; readme.getRange("B:B").format.columnWidth=92;

for (const sh of wb.worksheets.items) {
  const used = sh.getUsedRange();
  if (used) used.format.verticalAlignment = "center";
}

wb.recalculate();
const check1 = await wb.inspect({kind:"table", range:"Resumo!A1:L29", include:"values,formulas", tableMaxRows:30, tableMaxCols:12});
console.log(check1.ndjson);
const check2 = await wb.inspect({kind:"table", range:"Materialidade!A1:C15", include:"values,formulas", tableMaxRows:20, tableMaxCols:6});
console.log(check2.ndjson);
const errors = await wb.inspect({kind:"match", searchTerm:"#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!", options:{useRegex:true,maxResults:300}, summary:"final formula error scan"});
console.log(errors.ndjson);

await fs.mkdir(outDir,{recursive:true}); await fs.mkdir(qaDir,{recursive:true});
for (const sh of wb.worksheets.items) {
  const image = await wb.render({sheetName:sh.name, autoCrop:"all", scale:1});
  await fs.writeFile(path.join(qaDir, `${sh.name.replace(/[^A-Za-z0-9_-]/g,"_")}.png`), new Uint8Array(await image.arrayBuffer()));
}
const xlsx = await SpreadsheetFile.exportXlsx(wb);
await xlsx.save(path.join(outDir,"calculos_auditoria_tupy_2025.xlsx"));
console.log(`Workbook salvo em ${path.join(outDir,"calculos_auditoria_tupy_2025.xlsx")}`);
