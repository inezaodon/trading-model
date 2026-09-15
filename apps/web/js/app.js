/* Shared client for Trading Model umbrella web */

const API_BASE = window.TM_API_BASE || "";

const PROJECTS = [
  { slug: "gbm", title: "GBM Simulator", short: "Geometric Brownian Motion paths" },
  { slug: "mc-options", title: "MC Options", short: "European call/put Monte Carlo" },
  { slug: "brownian", title: "Brownian", short: "Wiener & random walks" },
  { slug: "ou", title: "OU Mean Reversion", short: "Ornstein–Uhlenbeck spreads" },
  { slug: "heston", title: "Heston SV", short: "Stochastic volatility" },
  { slug: "var", title: "MC VaR", short: "Portfolio Value-at-Risk" },
  { slug: "rough-vol", title: "Rough Vol", short: "Rough Bergomi" },
];

const TEAL_PALETTE = [
  "#2dd4bf",
  "#5eead4",
  "#99f6e4",
  "#14b8a6",
  "#0d9488",
  "#67e8f9",
  "#22d3ee",
  "#a5f3fc",
];

function qs(sel, el = document) {
  return el.querySelector(sel);
}

function mountHeader(activeSlug = null) {
  const header = qs("#site-header");
  if (!header) return;
  const links = PROJECTS.map(
    (p) =>
      `<a href="/projects/${p.slug}" class="${p.slug === activeSlug ? "active" : ""}">${p.title}</a>`
  ).join("");
  header.innerHTML = `
    <div class="inner">
      <a class="brand" href="/"><span class="brand-mark" aria-hidden="true"></span>Trading Model</a>
      <button class="nav-toggle" type="button" aria-label="Menu">Menu</button>
      <nav class="nav" id="main-nav">
        <a href="/" class="${activeSlug ? "" : "active"}">Home</a>
        ${links}
      </nav>
    </div>`;
  const toggle = qs(".nav-toggle", header);
  const nav = qs("#main-nav", header);
  toggle?.addEventListener("click", () => nav.classList.toggle("open"));
}

function mountFooter() {
  const el = qs("#site-footer");
  if (!el) return;
  el.innerHTML = `
    <p>Educational / research only — not investment advice. No live order routing.</p>
    <p>Integration status: <code>docs/PROGRESS.md</code> in the repository.</p>`;
}

async function apiGet(path) {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
  return res.json();
}

async function apiRun(slug, params) {
  const res = await fetch(`${API_BASE}/api/v1/${slug}/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ params }),
  });
  if (!res.ok) {
    let detail = await res.text();
    try {
      detail = JSON.parse(detail).detail || detail;
    } catch (_) {}
    throw new Error(detail || `HTTP ${res.status}`);
  }
  return res.json();
}

function readForm(form) {
  const data = {};
  const fd = new FormData(form);
  for (const [k, v] of fd.entries()) {
    if (v === "") continue;
    const num = Number(v);
    data[k] = Number.isFinite(num) && String(v).trim() !== "" && !/^[a-zA-Z]/.test(v) ? num : v;
    // keep option strings as strings
    if (k === "option" || k === "scheme") data[k] = String(v);
  }
  // weights as CSV
  if (typeof data.weights === "string" && data.weights.includes(",")) {
    data.weights = data.weights.split(",").map((x) => Number(x.trim()));
  }
  if (typeof data.tickers === "string" && data.tickers.includes(",")) {
    data.tickers = data.tickers.split(",").map((x) => x.trim()).filter(Boolean);
  }
  return data;
}

function renderMetrics(el, metrics) {
  if (!el || !metrics) return;
  el.innerHTML = Object.entries(metrics)
    .filter(([, v]) => v !== null && v !== undefined)
    .map(([k, v]) => {
      const display =
        typeof v === "number"
          ? Math.abs(v) >= 1000
            ? v.toLocaleString(undefined, { maximumFractionDigits: 2 })
            : v.toPrecision(4)
          : String(v);
      return `<div class="metric"><div class="k">${k}</div><div class="v">${display}</div></div>`;
    })
    .join("");
}

function destroyChart(chartRef) {
  if (chartRef.current) {
    chartRef.current.destroy();
    chartRef.current = null;
  }
}

function chartPaths(canvas, result, chartRef, opts = {}) {
  destroyChart(chartRef);
  const times = result.series?.times || [];
  const paths = result.series?.paths || [];
  const datasets = paths.map((p, i) => ({
    label: `path ${i + 1}`,
    data: p.map((y, j) => ({ x: times[j], y })),
    borderColor: TEAL_PALETTE[i % TEAL_PALETTE.length],
    borderWidth: i === 0 ? 2 : 1.25,
    pointRadius: 0,
    tension: 0.05,
    fill: false,
  }));

  if (result.series?.mean) {
    datasets.push({
      label: "mean",
      data: result.series.mean.map((y, j) => ({ x: times[j], y })),
      borderColor: "#f0b429",
      borderWidth: 2,
      borderDash: [5, 4],
      pointRadius: 0,
      fill: false,
    });
  }
  if (result.series?.theta_line) {
    datasets.push({
      label: "θ",
      data: result.series.theta_line.map((y, j) => ({ x: times[j], y })),
      borderColor: "#f07178",
      borderWidth: 1.5,
      borderDash: [2, 3],
      pointRadius: 0,
      fill: false,
    });
  }
  if (result.series?.quadratic_variation) {
    datasets.push({
      label: "QV",
      data: result.series.quadratic_variation.map((y, j) => ({ x: times[j], y })),
      borderColor: "#f0b429",
      borderWidth: 1.5,
      pointRadius: 0,
      yAxisID: opts.qvAxis ? "y1" : "y",
      fill: false,
    });
  }

  const scales = {
    x: {
      type: "linear",
      title: { display: true, text: "t", color: "#8fa3b0" },
      ticks: { color: "#8fa3b0" },
      grid: { color: "rgba(120,160,180,0.12)" },
    },
    y: {
      title: { display: true, text: opts.yLabel || "value", color: "#8fa3b0" },
      ticks: { color: "#8fa3b0" },
      grid: { color: "rgba(120,160,180,0.12)" },
    },
  };
  if (opts.qvAxis) {
    scales.y1 = {
      position: "right",
      title: { display: true, text: "QV", color: "#f0b429" },
      ticks: { color: "#f0b429" },
      grid: { drawOnChartArea: false },
    };
  }

  chartRef.current = new Chart(canvas, {
    type: "line",
    data: { datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 550 },
      plugins: {
        legend: { display: paths.length <= 6, labels: { color: "#8fa3b0", boxWidth: 12 } },
      },
      scales,
    },
  });
}

function chartDual(canvas, result, chartRef) {
  destroyChart(chartRef);
  const times = result.series?.times || [];
  const paths = result.series?.paths || [];
  const variance = result.series?.variance || [];
  const datasets = [
    ...paths.slice(0, 3).map((p, i) => ({
      label: `S ${i + 1}`,
      data: p.map((y, j) => ({ x: times[j], y })),
      borderColor: TEAL_PALETTE[i % TEAL_PALETTE.length],
      borderWidth: 1.5,
      pointRadius: 0,
      yAxisID: "y",
      fill: false,
    })),
    ...variance.slice(0, 2).map((p, i) => ({
      label: `v ${i + 1}`,
      data: p.map((y, j) => ({ x: times[j], y })),
      borderColor: ["#f0b429", "#f07178"][i],
      borderWidth: 1.25,
      borderDash: [4, 3],
      pointRadius: 0,
      yAxisID: "y1",
      fill: false,
    })),
  ];
  chartRef.current = new Chart(canvas, {
    type: "line",
    data: { datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 550 },
      plugins: { legend: { labels: { color: "#8fa3b0", boxWidth: 12 } } },
      scales: {
        x: {
          type: "linear",
          title: { display: true, text: "t", color: "#8fa3b0" },
          ticks: { color: "#8fa3b0" },
          grid: { color: "rgba(120,160,180,0.12)" },
        },
        y: {
          title: { display: true, text: "S", color: "#2dd4bf" },
          ticks: { color: "#2dd4bf" },
          grid: { color: "rgba(120,160,180,0.12)" },
        },
        y1: {
          position: "right",
          title: { display: true, text: "v", color: "#f0b429" },
          ticks: { color: "#f0b429" },
          grid: { drawOnChartArea: false },
        },
      },
    },
  });
}

function chartHistogram(canvas, result, chartRef, opts = {}) {
  destroyChart(chartRef);
  const edges = result.series?.hist_edges || [];
  const counts = result.series?.hist_counts || [];
  const labels = [];
  for (let i = 0; i < counts.length; i++) {
    const mid = (edges[i] + edges[i + 1]) / 2;
    labels.push(mid);
  }
  chartRef.current = new Chart(canvas, {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: opts.label || "count",
          data: counts,
          backgroundColor: "rgba(45, 212, 191, 0.45)",
          borderColor: "#2dd4bf",
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 450 },
      plugins: { legend: { display: false } },
      scales: {
        x: {
          title: { display: true, text: opts.xLabel || "value", color: "#8fa3b0" },
          ticks: {
            color: "#8fa3b0",
            callback(v, i) {
              const x = labels[i];
              return typeof x === "number" ? x.toFixed(0) : x;
            },
            maxTicksLimit: 8,
          },
          grid: { color: "rgba(120,160,180,0.12)" },
        },
        y: {
          title: { display: true, text: "count", color: "#8fa3b0" },
          ticks: { color: "#8fa3b0" },
          grid: { color: "rgba(120,160,180,0.12)" },
        },
      },
    },
  });
}

function wireRunner({ slug, formId, canvasId, statusId, metricsId, mode }) {
  const form = qs(`#${formId}`);
  const canvas = qs(`#${canvasId}`);
  const status = qs(`#${statusId}`);
  const metrics = qs(`#${metricsId}`);
  const chartRef = { current: null };
  if (!form || !canvas) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    status.className = "status";
    status.textContent = "Running…";
    try {
      const params = readForm(form);
      const result = await apiRun(slug, params);
      if (mode === "dual") chartDual(canvas, result, chartRef);
      else if (mode === "hist") chartHistogram(canvas, result, chartRef, { xLabel: mode === "hist" ? "value" : "" });
      else if (mode === "brownian") chartPaths(canvas, result, chartRef, { yLabel: "W_t", qvAxis: true });
      else chartPaths(canvas, result, chartRef, { yLabel: "S_t" });
      renderMetrics(metrics, result.metrics);
      status.className = "status ok";
      status.textContent = `Engine: ${result.engine || "ok"}`;
    } catch (err) {
      status.className = "status error";
      status.textContent = String(err.message || err);
    }
  });
}

window.TM = {
  PROJECTS,
  mountHeader,
  mountFooter,
  apiGet,
  apiRun,
  wireRunner,
  chartPaths,
  chartDual,
  chartHistogram,
  renderMetrics,
};
