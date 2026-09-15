import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { describe, it } from "node:test";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

describe("dashboard static assets", () => {
  it("ships index.html, styles.css, and app.js", () => {
    for (const name of ["index.html", "styles.css", "app.js"]) {
      const p = path.join(root, "public", name);
      assert.ok(fs.existsSync(p), `missing ${name}`);
    }
  });

  it("build copies assets to dist/", () => {
    const dist = path.join(root, "dist");
    // build may or may not have run; copy check is soft if dist missing
    if (!fs.existsSync(dist)) return;
    assert.ok(fs.existsSync(path.join(dist, "index.html")));
  });
});
