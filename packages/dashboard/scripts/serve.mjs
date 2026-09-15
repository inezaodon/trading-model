#!/usr/bin/env node
/**
 * Tiny static server for the dashboard.
 * Serves package dist/ (or public/) and optionally repo artifacts/ under /artifacts/.
 */
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const pkgRoot = path.resolve(__dirname, "..");

function findRepoRoot(start) {
  let dir = start;
  for (;;) {
    const pkg = path.join(dir, "package.json");
    if (fs.existsSync(pkg)) {
      try {
        const j = JSON.parse(fs.readFileSync(pkg, "utf8"));
        if (j.name === "trading-model" || Array.isArray(j.workspaces)) return dir;
      } catch {
        /* continue */
      }
    }
    const parent = path.dirname(dir);
    if (parent === dir) return start;
    dir = parent;
  }
}

const repoRoot = findRepoRoot(path.resolve(pkgRoot, "../.."));
const staticRoot = fs.existsSync(path.join(pkgRoot, "dist", "index.html"))
  ? path.join(pkgRoot, "dist")
  : path.join(pkgRoot, "public");
const artifactsDir = path.join(repoRoot, "artifacts");
const port = Number(process.env.PORT || 4173);

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
};

function send(res, status, body, type = "text/plain; charset=utf-8") {
  res.writeHead(status, {
    "Content-Type": type,
    "Cache-Control": "no-store",
  });
  res.end(body);
}

function safeJoin(root, reqPath) {
  const cleaned = path.normalize(decodeURIComponent(reqPath)).replace(/^(\.\.[/\\])+/, "");
  const full = path.join(root, cleaned);
  if (!full.startsWith(root)) return null;
  return full;
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url || "/", `http://127.0.0.1:${port}`);
  let pathname = url.pathname;

  if (pathname === "/artifacts" || pathname.startsWith("/artifacts/")) {
    const rel = pathname === "/artifacts" || pathname === "/artifacts/"
      ? ""
      : pathname.slice("/artifacts/".length);
    if (!rel) {
      // directory listing of artifact filenames
      if (!fs.existsSync(artifactsDir)) {
        return send(res, 200, "[]", MIME[".json"]);
      }
      const files = fs.readdirSync(artifactsDir).filter((f) => f.endsWith(".json"));
      return send(res, 200, JSON.stringify(files), MIME[".json"]);
    }
    const file = safeJoin(artifactsDir, rel);
    if (!file || !fs.existsSync(file) || !fs.statSync(file).isFile()) {
      return send(res, 404, JSON.stringify({ error: "not found" }), MIME[".json"]);
    }
    return send(res, 200, fs.readFileSync(file), MIME[".json"]);
  }

  if (pathname === "/") pathname = "/index.html";
  const file = safeJoin(staticRoot, pathname);
  if (!file || !fs.existsSync(file) || !fs.statSync(file).isFile()) {
    return send(res, 404, "Not found");
  }
  const ext = path.extname(file);
  send(res, 200, fs.readFileSync(file), MIME[ext] || "application/octet-stream");
});

server.listen(port, () => {
  console.log(`dashboard listening on http://127.0.0.1:${port}`);
  console.log(`static: ${staticRoot}`);
  console.log(`artifacts: ${artifactsDir}`);
});
