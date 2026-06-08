/**
 * SellerVision AI — PDF generation utility
 * jspdf is loaded via dynamic import so it never enters the SSR bundle.
 * All public functions are async — call them from onClick handlers only.
 */

/* ── Palette ─────────────────────────────────────────────────────────── */
const C = {
  brand:   [109, 40,  217] as [number, number, number],
  black:   [10,  10,  20]  as [number, number, number],
  dark:    [30,  27,  50]  as [number, number, number],
  muted:   [100, 100, 120] as [number, number, number],
  faint:   [230, 228, 240] as [number, number, number],
  white:   [255, 255, 255] as [number, number, number],
  rowAlt:  [245, 244, 250] as [number, number, number],
  success: [16,  185, 129] as [number, number, number],
  danger:  [239, 68,  68]  as [number, number, number],
  warning: [245, 158, 11]  as [number, number, number],
};

const PAGE_W  = 210;
const PAGE_H  = 297;
const MARGIN  = 14;
const CONTENT = PAGE_W - MARGIN * 2;

/* ── Helpers (doc typed as any — jsPDF loaded at runtime) ────────────── */
function drawHeader(doc: any, title: string, subtitle?: string): number {
  doc.setFillColor(...C.brand);
  doc.rect(0, 0, PAGE_W, 18, "F");

  doc.setFont("helvetica", "bold");
  doc.setFontSize(11);
  doc.setTextColor(...C.white);
  doc.text("SellerVision AI", MARGIN, 11.5);

  doc.setFont("helvetica", "normal");
  doc.setFontSize(9);
  doc.setTextColor(200, 185, 255);
  doc.text("AI-Powered E-Commerce Intelligence", MARGIN + 44, 11.5);

  const dateStr = new Date().toLocaleDateString("en-US", {
    year: "numeric", month: "long", day: "numeric",
  });
  doc.text(`Generated ${dateStr}`, PAGE_W - MARGIN, 11.5, { align: "right" });

  doc.setFont("helvetica", "bold");
  doc.setFontSize(16);
  doc.setTextColor(...C.black);
  doc.text(title, MARGIN, 30);

  if (subtitle) {
    doc.setFont("helvetica", "normal");
    doc.setFontSize(9);
    doc.setTextColor(...C.muted);
    doc.text(subtitle, MARGIN, 37);
  }

  doc.setDrawColor(...C.faint);
  doc.setLineWidth(0.3);
  doc.line(MARGIN, subtitle ? 41 : 34, PAGE_W - MARGIN, subtitle ? 41 : 34);

  return subtitle ? 46 : 39;
}

function drawFooter(doc: any, pageNum: number, totalPages: number) {
  doc.setFont("helvetica", "normal");
  doc.setFontSize(7);
  doc.setTextColor(...C.muted);
  doc.text("SellerVision AI — Confidential", MARGIN, PAGE_H - 8);
  doc.text(`Page ${pageNum} of ${totalPages}`, PAGE_W - MARGIN, PAGE_H - 8, { align: "right" });
  doc.setDrawColor(...C.faint);
  doc.setLineWidth(0.2);
  doc.line(MARGIN, PAGE_H - 11, PAGE_W - MARGIN, PAGE_H - 11);
}

/* ── Public types ────────────────────────────────────────────────────── */
export interface TableColumn {
  header: string;
  key: string;
  width?: number;
  align?: "left" | "right" | "center";
  format?: (val: any) => string;
  color?: (val: any) => [number, number, number] | null;
}

export interface PdfTableOptions {
  title: string;
  subtitle?: string;
  columns: TableColumn[];
  rows: Record<string, any>[];
  filename: string;
  summaryRows?: { label: string; value: string }[];
}

/* ── Data table PDF ──────────────────────────────────────────────────── */
export async function downloadPDF(opts: PdfTableOptions) {
  const { jsPDF } = await import("jspdf");
  const doc = new jsPDF({ unit: "mm", format: "a4", orientation: "portrait" });

  let y = drawHeader(doc, opts.title, opts.subtitle);

  if (opts.summaryRows && opts.summaryRows.length > 0) {
    const colW = CONTENT / opts.summaryRows.length;
    opts.summaryRows.forEach((s, i) => {
      const x = MARGIN + i * colW;
      doc.setFillColor(240, 237, 255);
      doc.roundedRect(x, y, colW - 2, 14, 2, 2, "F");
      doc.setFont("helvetica", "bold");
      doc.setFontSize(12);
      doc.setTextColor(...C.brand);
      doc.text(s.value, x + colW / 2 - 1, y + 7, { align: "center" });
      doc.setFont("helvetica", "normal");
      doc.setFontSize(7);
      doc.setTextColor(...C.muted);
      doc.text(s.label, x + colW / 2 - 1, y + 12, { align: "center" });
    });
    y += 20;
  }

  const totalFrac = opts.columns.reduce((s, c) => s + (c.width ?? 1), 0);
  const colWidths = opts.columns.map((c) => ((c.width ?? 1) / totalFrac) * CONTENT);

  const ROW_H    = 7;
  const HEADER_H = 8;

  const drawTableHeader = (startY: number) => {
    doc.setFillColor(...C.dark);
    doc.rect(MARGIN, startY, CONTENT, HEADER_H, "F");
    let hx = MARGIN;
    opts.columns.forEach((col, i) => {
      doc.setFont("helvetica", "bold");
      doc.setFontSize(7.5);
      doc.setTextColor(...C.white);
      const tx = col.align === "right" ? hx + colWidths[i] - 2 : hx + 2;
      doc.text(col.header.toUpperCase(), tx, startY + 5.5, {
        align: col.align === "right" ? "right" : "left",
      });
      hx += colWidths[i];
    });
    return startY + HEADER_H;
  };

  y = drawTableHeader(y);

  let pageCount = 1;
  opts.rows.forEach((row, rowIdx) => {
    if (y + ROW_H > PAGE_H - 18) {
      drawFooter(doc, pageCount, 1);
      doc.addPage();
      pageCount++;
      y = drawHeader(doc, opts.title, opts.subtitle);
      y = drawTableHeader(y);
    }

    if (rowIdx % 2 === 1) {
      doc.setFillColor(...C.rowAlt);
      doc.rect(MARGIN, y, CONTENT, ROW_H, "F");
    }

    doc.setDrawColor(...C.faint);
    doc.setLineWidth(0.1);
    doc.line(MARGIN, y + ROW_H, MARGIN + CONTENT, y + ROW_H);

    let xCursor = MARGIN;
    opts.columns.forEach((col, i) => {
      const raw  = row[col.key];
      const text = col.format ? col.format(raw) : String(raw ?? "—");
      const clr  = col.color ? col.color(raw) : null;

      doc.setFont("helvetica", "normal");
      doc.setFontSize(8);
      doc.setTextColor(...(clr ?? C.dark));

      const tx = col.align === "right" ? xCursor + colWidths[i] - 2 : xCursor + 2;
      doc.text(text, tx, y + ROW_H - 2, {
        align: col.align === "right" ? "right" : "left",
        maxWidth: colWidths[i] - 4,
      });
      xCursor += colWidths[i];
    });
    y += ROW_H;
  });

  const total = doc.getNumberOfPages();
  for (let p = 1; p <= total; p++) {
    doc.setPage(p);
    drawFooter(doc, p, total);
  }

  doc.save(opts.filename);
}

/* ── Executive briefing PDF ──────────────────────────────────────────── */
export async function downloadBriefingPDF(opts: {
  period: string;
  kpis: { label: string; value: string; change: string; positive: boolean }[];
  recommendations: { priority: string; action: string; impact: string }[];
  agentStatus: { name: string; status: string; runs: number }[];
  filename?: string;
}) {
  const { jsPDF } = await import("jspdf");
  const doc = new jsPDF({ unit: "mm", format: "a4", orientation: "portrait" });

  const subtitle = `Period: Last ${opts.period} · ${new Date().toLocaleDateString("en-US", {
    weekday: "long", year: "numeric", month: "long", day: "numeric",
  })}`;
  let y = drawHeader(doc, "AI CEO Executive Briefing", subtitle);

  // KPI boxes
  const kpiCols = Math.min(opts.kpis.length, 4);
  const kpiW    = CONTENT / kpiCols;
  opts.kpis.slice(0, 4).forEach((kpi, i) => {
    const x = MARGIN + i * kpiW;
    doc.setFillColor(240, 237, 255);
    doc.roundedRect(x, y, kpiW - 2, 18, 2, 2, "F");
    doc.setFont("helvetica", "bold");
    doc.setFontSize(14);
    doc.setTextColor(...C.brand);
    doc.text(kpi.value, x + kpiW / 2 - 1, y + 9, { align: "center" });
    doc.setFont("helvetica", "normal");
    doc.setFontSize(7);
    doc.setTextColor(...C.muted);
    doc.text(kpi.label, x + kpiW / 2 - 1, y + 14, { align: "center" });
    if (kpi.change) {
      doc.setTextColor(...(kpi.positive ? C.success : C.danger));
      doc.text(kpi.change, x + kpiW / 2 - 1, y + 17.5, { align: "center" });
    }
  });
  y += 24;

  // Recommendations
  if (opts.recommendations.length > 0) {
    doc.setFont("helvetica", "bold");
    doc.setFontSize(11);
    doc.setTextColor(...C.black);
    doc.text("AI Recommendations", MARGIN, y);
    doc.setDrawColor(...C.brand);
    doc.setLineWidth(0.5);
    doc.line(MARGIN, y + 1, MARGIN + 44, y + 1);
    y += 7;

    opts.recommendations.slice(0, 5).forEach((rec) => {
      if (y + 16 > PAGE_H - 18) { doc.addPage(); y = 20; }
      const pc = rec.priority === "high" ? C.danger : rec.priority === "medium" ? C.warning : C.success;
      doc.setFillColor(...pc);
      doc.circle(MARGIN + 3, y + 4, 2, "F");
      doc.setFillColor(248, 247, 252);
      doc.roundedRect(MARGIN + 7, y, CONTENT - 7, 14, 1.5, 1.5, "F");
      doc.setFont("helvetica", "bold");
      doc.setFontSize(8.5);
      doc.setTextColor(...C.black);
      doc.text(rec.action, MARGIN + 10, y + 5.5, { maxWidth: CONTENT - 20 });
      doc.setFont("helvetica", "normal");
      doc.setFontSize(7.5);
      doc.setTextColor(...C.muted);
      doc.text(`Impact: ${rec.impact}`, MARGIN + 10, y + 11);
      doc.setFont("helvetica", "bold");
      doc.setFontSize(7);
      doc.setTextColor(...pc);
      doc.text(rec.priority.toUpperCase(), MARGIN + CONTENT - 4, y + 5.5, { align: "right" });
      y += 17;
    });
    y += 3;
  }

  // Agent status
  if (opts.agentStatus.length > 0) {
    if (y + 50 > PAGE_H - 18) { doc.addPage(); y = 20; }
    doc.setFont("helvetica", "bold");
    doc.setFontSize(11);
    doc.setTextColor(...C.black);
    doc.text("Agent Fleet Status", MARGIN, y);
    doc.setDrawColor(...C.brand);
    doc.setLineWidth(0.5);
    doc.line(MARGIN, y + 1, MARGIN + 38, y + 1);
    y += 7;

    doc.setFillColor(...C.dark);
    doc.rect(MARGIN, y, CONTENT, 7, "F");
    doc.setFont("helvetica", "bold");
    doc.setFontSize(7);
    doc.setTextColor(...C.white);
    doc.text("AGENT",      MARGIN + 2,           y + 5);
    doc.text("STATUS",     MARGIN + 90,           y + 5);
    doc.text("TOTAL RUNS", MARGIN + CONTENT - 2,  y + 5, { align: "right" });
    y += 7;

    opts.agentStatus.forEach((agent, i) => {
      if (i % 2 === 1) {
        doc.setFillColor(...C.rowAlt);
        doc.rect(MARGIN, y, CONTENT, 6.5, "F");
      }
      doc.setFont("helvetica", "normal");
      doc.setFontSize(8);
      doc.setTextColor(...C.dark);
      doc.text(agent.name, MARGIN + 2, y + 4.5);
      const sc = agent.status === "running" ? C.success : agent.status === "alert" ? C.danger : C.muted;
      doc.setTextColor(...sc);
      doc.text(agent.status.toUpperCase(), MARGIN + 90, y + 4.5);
      doc.setTextColor(...C.dark);
      doc.text(agent.runs.toLocaleString(), MARGIN + CONTENT - 2, y + 4.5, { align: "right" });
      doc.setDrawColor(...C.faint);
      doc.setLineWidth(0.1);
      doc.line(MARGIN, y + 6.5, MARGIN + CONTENT, y + 6.5);
      y += 6.5;
    });
  }

  const total = doc.getNumberOfPages();
  for (let p = 1; p <= total; p++) {
    doc.setPage(p);
    drawFooter(doc, p, total);
  }

  doc.save(opts.filename ?? `sv-briefing-${opts.period}-${Date.now()}.pdf`);
}
