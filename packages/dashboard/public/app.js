/**
 * Trading Model dashboard — reads orchestrator artifacts and charts paths / variance / PnL.
 */

const $ = (sel) => document.querySelector(sel);

function fmt(n, digits = 2) {
  if (n == null || Number.isNaN(n)) return "—";
  return Number(n).toLocaleString(undefined, {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

async function fetchJson(url) {
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error(`${url} → ${res.status}`);
  return res.json();
}

async function loadArtifacts() {
  const files = await fetchJson("/artifacts").catch(() => []);
  const want = ["report.json", "paths.json", "backtest.json", "surface.json"];
  const data = {};
  await Promise.all(
    want.map(async (name) => {
      if (Array.isArray(files) && files.length && !files.includes(name)) return;
      try {
        data[name.replace(".json", "")] = await fetchJson(`/artifacts/${name}`);
      } catch {
        /* optional */
      }
    }),
  );
  return data;
}

function spotSeries(paths) {
  if (!paths) return null;
  if (paths.paths?.[0]?.S) return paths.paths[0].S;
  if (paths.spot) return paths.spot;
  return null;
}

function varSeries(paths) {
  if (!paths) return null;
  if (paths.paths?.[0]?.v) return paths.paths[0].v;
  if (paths.variance) return paths.variance;
  return null;
}

function pnlSeries(backtest) {
  if (!backtest) return null;
  if (Array.isArray(backtest.equityCurve) && backtest.equityCurve.length) {
    return backtest.equityCurve.map((p) => p.equity);
  }
  if (Array.isArray(backtest.pnl)) {
    const out = [];
    let s = 0;
    for (const x of backtest.pnl) {
      s += x;
      out.push(s);
    }
    return out;
  }
  return null;
}

function surfaceSpot(surface) {
  return surface?.spot ?? surface?.surface?.stockpx;
}

function surfaceIv30(surface) {
  return surface?.iv30 ?? surface?.surface?.iv30;
}

function drawSeries(canvas, series, color, opts = {}) {
  const ctx = canvas.getContext("2d");
  const dpr = window.devicePixelRatio || 1;
  const cssW = canvas.clientWidth || 900;
  const cssH = 280;
  canvas.width = Math.floor(cssW * dpr);
  canvas.height = Math.floor(cssH * dpr);
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

  const w = cssW;
  const h = cssH;
  const pad = { t: 16, r: 16, b: 28, l: 48 };

  ctx.clearRect(0, 0, w, h);
  ctx.fillStyle = "#0e1619";
  ctx.fillRect(0, 0, w, h);

  if (!series || series.length < 2) {
    ctx.fillStyle = "#7a8f96";
    ctx.font = "12px IBM Plex Mono, monospace";
    ctx.fillText("No series data — run npm run demo", pad.l, h / 2);
    return;
  }

  const min = Math.min(...series);
  const max = Math.max(...series);
  const span = max - min || 1;
  const innerW = w - pad.l - pad.r;
  const innerH = h - pad.t - pad.b;

  ctx.strokeStyle = "#243238";
  ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i++) {
    const y = pad.t + (innerH * i) / 4;
    ctx.beginPath();
    ctx.moveTo(pad.l, y);
    ctx.lineTo(w - pad.r, y);
    ctx.stroke();
    const val = max - (span * i) / 4;
    ctx.fillStyle = "#7a8f96";
    ctx.font = "10px IBM Plex Mono, monospace";
    ctx.textAlign = "right";
    ctx.fillText(fmt(val, opts.digits ?? 2), pad.l - 6, y + 3);
  }

  const xAt = (i) => pad.l + (innerW * i) / (series.length - 1);
  const yAt = (v) => pad.t + innerH * (1 - (v - min) / span);

  if (opts.fill) {
    const grad = ctx.createLinearGradient(0, pad.t, 0, h - pad.b);
    grad.addColorStop(0, color + "55");
    grad.addColorStop(1, color + "00");
    ctx.beginPath();
    ctx.moveTo(xAt(0), yAt(series[0]));
    for (let i = 1; i < series.length; i++) ctx.lineTo(xAt(i), yAt(series[i]));
    ctx.lineTo(xAt(series.length - 1), h - pad.b);
    ctx.lineTo(xAt(0), h - pad.b);
    ctx.closePath();
    ctx.fillStyle = grad;
    ctx.fill();
  }

  ctx.beginPath();
  ctx.moveTo(xAt(0), yAt(series[0]));
  for (let i = 1; i < series.length; i++) ctx.lineTo(xAt(i), yAt(series[i]));
  ctx.strokeStyle = color;
  ctx.lineWidth = 1.75;
  ctx.lineJoin = "round";
  ctx.stroke();

  if (opts.zeroLine && min < 0 && max > 0) {
    const y0 = yAt(0);
    ctx.setLineDash([4, 4]);
    ctx.strokeStyle = "#5a6e74";
    ctx.beginPath();
    ctx.moveTo(pad.l, y0);
    ctx.lineTo(w - pad.r, y0);
    ctx.stroke();
    ctx.setLineDash([]);
  }
}

function renderSummary(data) {
  const el = $("#summary");
  const report = data.report;
  const surface = data.surface;
  const paths = data.paths;
  const backtest = data.backtest;
  const s = report?.summary || {};
  const spot = s.spot ?? surfaceSpot(surface);
  const iv30 = s.iv30 ?? surfaceIv30(surface);
  const finalSpot = s.finalSpot ?? spotSeries(paths)?.at?.(-1);
  const termVar = s.terminalVariance ?? varSeries(paths)?.at?.(-1);
  const cumPnl =
    s.cumulativePnl ??
    (typeof backtest?.pnl === "number" ? backtest.pnl : backtest?.metrics?.totalReturn);
  const sharpe = s.sharpe ?? backtest?.metrics?.sharpe ?? backtest?.sharpe;

  const rows = [
    ["Symbol", report?.symbol || surface?.symbol || "—", false],
    ["Spot", fmt(spot), false],
    ["IV30", iv30 != null ? fmt(iv30 * 100, 1) + "%" : "—", false],
    ["Final S", fmt(finalSpot), false],
    ["Term. var", fmt(termVar, 4), false],
    ["Cum. PnL", fmt(cumPnl), cumPnl < 0],
    ["Sharpe", fmt(sharpe), false],
  ];

  el.innerHTML = rows
    .map(
      ([label, value, neg]) =>
        `<div class="stat"><span class="label">${label}</span><span class="value${neg ? " neg" : ""}">${value}</span></div>`,
    )
    .join("");
}

function setStatus(kind, text) {
  const box = $("#status");
  box.classList.remove("ok", "err");
  if (kind) box.classList.add(kind);
  $("#status-text").textContent = text;
}

async function refresh() {
  setStatus(null, "loading artifacts…");
  try {
    const data = await loadArtifacts();
    const hasAny = Object.keys(data).length > 0;
    if (!hasAny) {
      setStatus("err", "no artifacts — run npm run demo");
      $("#summary").innerHTML =
        `<div class="empty">No artifacts found. From repo root: npm run demo</div>`;
      drawSeries($("#spot-chart"), null, "#2dd4bf");
      drawSeries($("#var-chart"), null, "#d4a017");
      drawSeries($("#pnl-chart"), null, "#e85d4c");
      return;
    }

    renderSummary(data);
    const paths = data.paths;
    const backtest = data.backtest;
    const spot = spotSeries(paths);
    const variance = varSeries(paths);
    const pnl = pnlSeries(backtest);

    drawSeries($("#spot-chart"), spot, "#2dd4bf", { fill: true, digits: 2 });
    $("#spot-meta").textContent = paths
      ? `${paths.model || "model"} · n=${spot?.length ?? "?"} · ${paths.mock ? "mock" : "sim"}`
      : "missing paths.json";

    drawSeries($("#var-chart"), variance, "#d4a017", { fill: true, digits: 4 });
    $("#var-meta").textContent = variance
      ? `v₀=${fmt(variance[0], 4)} → v_T=${fmt(variance.at(-1), 4)}`
      : "—";

    drawSeries($("#pnl-chart"), pnl, "#5eead4", {
      fill: true,
      zeroLine: true,
      digits: 2,
    });
    const cum =
      typeof backtest?.pnl === "number"
        ? backtest.pnl
        : backtest?.metrics?.totalReturn;
    $("#pnl-meta").textContent = backtest
      ? `${backtest.strategy || "strategy"} · cum=${fmt(cum)}`
      : "missing backtest.json";

    const mock = data.report?.mock || paths?.mock || backtest?.mock;
    setStatus("ok", mock ? "artifacts loaded (mock)" : "artifacts loaded");
  } catch (err) {
    setStatus("err", err.message || "load failed");
  }
}

$("#reload").addEventListener("click", () => refresh());
window.addEventListener("resize", () => {
  // debounce via rAF
  cancelAnimationFrame(window.__tmResize);
  window.__tmResize = requestAnimationFrame(() => refresh());
});
refresh();
