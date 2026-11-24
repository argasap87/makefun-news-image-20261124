// main.ts — entry point for make.fun news-image-20261124.
//
// Rebuilds the front page with draw.py (Pillow) and copies the finished
// entry.png to the output directory the harness expects. No network is
// used: the hero art lives in assets/ and every story line is baked into
// draw.py, so repeated runs produce identical bytes.
//
// Usage:
//   MAKEFUN_OUTPUT_DIR=out node main.ts
// (defaults to /output when the variable is unset, matching the
// competition harness.)

import { spawnSync } from "node:child_process";
import { copyFileSync, existsSync, mkdirSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = dirname(fileURLToPath(import.meta.url));
const source = join(repoRoot, "entry.png");
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const target = join(outDir, "entry.png");

function runDraw(): void {
  const py = spawnSync("python3", ["draw.py"], {
    cwd: repoRoot,
    stdio: "inherit",
  });
  if (py.status !== 0) {
    throw new Error(`draw.py exited with status ${py.status}`);
  }
}

function main(): void {
  runDraw();
  if (!existsSync(source)) {
    throw new Error(`draw.py did not produce ${source}`);
  }
  mkdirSync(outDir, { recursive: true });
  copyFileSync(source, target);
  const sourceBytes = statSync(source).size;
  const bytes = statSync(target).size;
  if (bytes !== sourceBytes) {
    throw new Error(
      `copied entry.png is ${bytes} bytes, expected ${sourceBytes}`
    );
  }
  if (bytes > 1048576) {
    throw new Error(`entry.png is ${bytes} bytes, over the 1 MiB limit`);
  }
  console.log(`entry.png -> ${target} (${bytes} bytes)`);
}

main();
