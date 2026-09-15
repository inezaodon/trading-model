import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");
const src = path.join(root, "public");
const dist = path.join(root, "dist");

fs.mkdirSync(dist, { recursive: true });

for (const name of fs.readdirSync(src)) {
  fs.copyFileSync(path.join(src, name), path.join(dist, name));
}

console.log(`dashboard: copied public/ → dist/ (${fs.readdirSync(dist).join(", ")})`);
