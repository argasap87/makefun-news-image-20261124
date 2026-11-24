// make.fun news-image-20261124 — "One Tuesday, Eight Fault Lines".
// The entry image lives in this repository as entry.png; this program
// just copies it to the output path make.fun gives us, so both runs
// write byte-identical output. No network, no randomness.
import { copyFileSync, mkdirSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "out";
const target = join(outDir, "entry.png");

mkdirSync(outDir, { recursive: true });
copyFileSync(join(here, "entry.png"), target);
console.log(`wrote ${target} (${statSync(target).size} bytes)`);
