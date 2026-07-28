import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";

const require = createRequire(import.meta.url);
const markedPath = require.resolve("marked");
const { marked } = await import(pathToFileURL(markedPath).href);

const [, , inputArg, outputArg, titleArg] = process.argv;
if (!inputArg || !outputArg) {
  throw new Error("usage: node render_research_html.mjs INPUT.md OUTPUT.html [TITLE]");
}

const inputPath = path.resolve(inputArg);
const outputPath = path.resolve(outputArg);
const title = titleArg || path.basename(outputPath, path.extname(outputPath));
const markdown = fs.readFileSync(inputPath, "utf8");

// Marked treats the backslashes in \(...\) and \[...\] as Markdown escapes.
// Protect complete TeX spans before parsing, then restore them as escaped HTML
// text so MathJax receives the original delimiters and expressions.
const mathSpans = [];
const protectedMarkdown = markdown.replace(
  /\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\)/g,
  (span) => {
    const token = `MATHPLACEHOLDER${mathSpans.length}X`;
    mathSpans.push(span);
    return token;
  },
);

let body = marked.parse(protectedMarkdown, { gfm: true, breaks: false });
body = body.replace(/MATHPLACEHOLDER(\d+)X/g, (_, index) =>
  mathSpans[Number(index)]
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;"),
);

// Markdown links are relative to the source file. Rebase them when the HTML
// artifact is emitted into a different directory.
body = body.replace(/\b(href|src)="([^"]+)"/g, (match, attribute, target) => {
  if (
    target.startsWith("#") ||
    target.startsWith("/") ||
    target.startsWith("\\") ||
    /^[a-zA-Z][a-zA-Z0-9+.-]*:/.test(target)
  ) {
    return match;
  }

  const fragmentIndex = target.search(/[?#]/);
  const pathname = fragmentIndex >= 0 ? target.slice(0, fragmentIndex) : target;
  const suffix = fragmentIndex >= 0 ? target.slice(fragmentIndex) : "";
  const absoluteTarget = path.resolve(path.dirname(inputPath), pathname);
  let rebased = path.relative(path.dirname(outputPath), absoluteTarget).replaceAll("\\", "/");
  if (!rebased.startsWith(".")) rebased = `./${rebased}`;
  return `${attribute}="${rebased}${suffix}"`;
});

const css = `
:root{--ink:#17202a;--line:#dfe5eb;--accent:#145da0;--soft:#f4f8fb}
*{box-sizing:border-box}body{margin:0;background:#f5f7f9;color:var(--ink);font:16px/1.72 -apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",Arial,sans-serif}
main{max-width:1080px;margin:32px auto;padding:48px 64px;background:#fff;box-shadow:0 10px 35px rgba(23,32,42,.08);border-radius:12px}
h1{font-size:2.15rem;line-height:1.25;margin:0 0 1.4rem;color:#0f2740}h2{font-size:1.55rem;margin:2.2rem 0 .9rem;padding-bottom:.35rem;border-bottom:2px solid #e7eef5;color:#103b62}h3{font-size:1.22rem;margin:1.7rem 0 .65rem;color:#174f7d}h4{font-size:1.05rem;margin:1.4rem 0 .5rem}
p{margin:.6rem 0 1rem}ul,ol{padding-left:1.5rem}li{margin:.25rem 0}a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}img{max-width:100%;height:auto}
blockquote{margin:1rem 0;padding:.8rem 1.1rem;border-left:4px solid #4b8bbd;background:var(--soft);color:#31465a}blockquote p{margin:.2rem 0}
table{width:100%;border-collapse:collapse;margin:1rem 0 1.4rem;font-size:.94rem;display:block;overflow-x:auto}th,td{border:1px solid var(--line);padding:.65rem .75rem;vertical-align:top;min-width:110px}th{background:#edf4fa;text-align:left;color:#173b59}tr:nth-child(even) td{background:#fbfcfd}
code{font-family:Consolas,"SFMono-Regular",monospace;background:#eef2f5;border-radius:4px;padding:.12rem .3rem}pre{overflow:auto;background:#18212b;color:#eef4f8;padding:1rem;border-radius:8px}pre code{background:transparent;padding:0}
hr{border:0;border-top:1px solid var(--line);margin:2rem 0}.MathJax{overflow-x:auto;overflow-y:hidden}
@media(max-width:760px){main{margin:0;padding:28px 20px;border-radius:0}h1{font-size:1.7rem}h2{font-size:1.35rem}}
@media print{body{background:#fff}main{box-shadow:none;margin:0;max-width:none;padding:0}a{color:inherit}}
`;

const html = `<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>${title}</title><style>${css}</style>
<script>window.MathJax={tex:{inlineMath:[["\\\\(","\\\\)"]],displayMath:[["\\\\[","\\\\]"]]},svg:{fontCache:"global"}};</script>
<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script></head>
<body><main>${body}</main></body></html>
`;

fs.writeFileSync(outputPath, html, "utf8");
