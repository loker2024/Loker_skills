---
name: convert-md-to-docx
description: Convert Markdown (.md/.markdown) files to DOCX while preserving the source file, extracting Mermaid/Graphviz/PlantUML diagrams and local images into a related assets directory with strict simple numeric filenames such as 001.png and 002.png, and inserting visible figure-position labels in the converted DOCX. Use when asked to 将 md 转换成 docx, Markdown 转 Word, export Markdown to DOCX, render Mermaid diagrams for Word, save diagram images separately, or mark image/diagram locations in the DOCX.
---

# Convert MD to DOCX

## Overview

Use this skill to convert Markdown into DOCX with reliable handling for diagrams and images. Keep the original Markdown unchanged, create a prepared Markdown file, save every generated/copied visual asset in a sibling assets directory, and ensure the final DOCX visibly marks where each figure belongs.

## Default Workflow

1. Use available filesystem and command permissions to complete the conversion end to end.
2. Keep the source `.md` unchanged.
3. Run `scripts/convert_md_to_docx.py` on the source Markdown.
4. Save visual assets in `<markdown-stem>_docx_assets/` unless the user specifies another directory.
5. Use simple strict numbering for image files: `001.png`, `002.png`, `003.jpg`, etc. Diagram source files use the same number, such as `001.mmd`.
6. Insert visible labels before each visual in the prepared Markdown so the DOCX contains markers like `[图位 FIG-001 | 类型: mermaid | 文件: ...]`.
7. Return the DOCX path, assets directory, prepared Markdown path, and figure manifest path.

## Conversion Script

Run from the skill directory or call it by absolute path:

```bash
python3 /Users/tujiajun/.codex/skills/convert-md-to-docx/scripts/convert_md_to_docx.py input.md
```

Useful options:

```bash
python3 /Users/tujiajun/.codex/skills/convert-md-to-docx/scripts/convert_md_to_docx.py input.md -o output.docx
python3 /Users/tujiajun/.codex/skills/convert-md-to-docx/scripts/convert_md_to_docx.py input.md --assets-dir output_assets
python3 /Users/tujiajun/.codex/skills/convert-md-to-docx/scripts/convert_md_to_docx.py input.md --reference-doc template.docx
python3 /Users/tujiajun/.codex/skills/convert-md-to-docx/scripts/convert_md_to_docx.py input.md --no-pandoc
```

The script creates:

- A DOCX output file.
- A prepared Markdown file named `<stem>_docx_prepared.md`.
- An assets directory named `<stem>_docx_assets/`.
- A manifest named `figure_manifest.csv` inside the assets directory.

## Diagram Handling

For fenced diagram blocks, extract the source and try to render a PNG:

- ` ```mermaid ` or ` ```mmd ` -> `001.mmd` and `001.png`
- ` ```dot ` or ` ```graphviz ` -> `001.dot` and `001.png`
- ` ```puml ` or ` ```plantuml ` -> `001.puml` and `001.png`

Use these renderers when available:

- Mermaid: `mmdc`, or `npx -y @mermaid-js/mermaid-cli`
- Graphviz: `dot`
- PlantUML: `plantuml`

For Mermaid, the bundled script automatically points Mermaid CLI at an installed local Chrome, Edge, or Chromium browser when available, avoiding the usual puppeteer Chrome-cache failure.

If rendering fails, keep the diagram source in the prepared Markdown, write a visible failure note at the figure position, and report the issue. Use `--strict` only when the user wants the conversion to fail instead of keeping placeholders.

## Image Handling

Copy local Markdown images into the assets directory and rename them with simple numbering while preserving the original extension, such as `002.png` or `003.jpg`.

Leave remote images, data URIs, anchors, and missing local files unchanged, then mention them in the final response if they may affect the DOCX.

## DOCX Verification

After conversion, verify the key outputs exist:

```bash
ls -la output.docx output_docx_assets
```

When possible, inspect `figure_manifest.csv` to confirm every diagram/image has a figure id, output filename, and status. If the task is layout-sensitive, use the documents skill to render or inspect the DOCX after creation.
