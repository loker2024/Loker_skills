---
name: humanize-report-writing
description: Polish and humanize Chinese lab reports, experiment summaries, coursework documents, Markdown/DOCX text, and academic or technical writing. Use when asked to 润色实验报告/文档, 去除 AI 味/AI 腔/机器味, 降低 AIGC 痕迹, make writing more natural, less generic, more teacher-readable, or closer to a student's own voice while preserving meaning, data, formulas, citations, and structure.
---

# Humanize Report Writing

## Overview

Use this skill to revise reports so they read like careful student or professional writing rather than generic generated text. Preserve the document's factual content and academic seriousness; the goal is naturalness and specificity, not casualization.

## Workflow

1. Identify the target text, file type, audience, and required output format. If the user gives a file, preserve the original by default and write a new copy unless they explicitly ask for in-place edits.
2. Read enough surrounding context to understand the experiment, method, data, results, and course requirements before rewriting. Do not polish isolated sentences in a way that conflicts with the full report.
3. Keep hard facts unchanged: data, units, formulas, experimental steps, citations, figure/table numbers, conclusions supported by results, and required headings.
4. Remove AI-flavored phrasing by replacing generic claims with document-grounded wording, varying sentence rhythm, and cutting inflated transitions.
5. Return either the revised file path or the polished text. Include a short change note only when useful; do not over-explain the editing philosophy.

## Humanizing Rules

Prefer concrete, report-specific phrasing:

- Replace broad claims like "具有重要意义" with the actual purpose, measurement, or observation from the report.
- Replace "通过本次实验, 我深刻认识到" with a specific learning point, difficulty, error source, or implementation detail.
- Replace repeated "首先、其次、最后" chains with natural paragraph flow.
- Replace "显著提高、充分体现、有效验证、具有较高的准确性" with measured results or restrained wording.
- Keep appropriate first-person reflection when the report requires "心得体会", but avoid exaggerated emotion.
- Let limitations remain visible when supported by the experiment, such as measurement error, sample size, calibration, implementation constraints, or unstable observations.

Avoid common AI texture:

- Symmetric paragraph templates where every section has the same rhythm.
- Empty summary sentences that restate the title without adding information.
- Excessive "不仅...而且...", "综上所述", "由此可见", "可以看出" transitions.
- Grand conclusions unsupported by data.
- Over-polished academic diction that a student would not naturally write.
- Invented details added only to make the writing sound richer.

## Editing Depth

Choose the lightest edit that satisfies the request:

- Light polish: fix awkward wording, punctuation, paragraph flow, and obvious AI phrases.
- Humanize: rewrite generic sections into more specific, natural prose while preserving structure.
- Deep revision: reorganize paragraphs, merge repetitive sections, strengthen logic, and flag missing evidence instead of inventing it.

When the user asks to "去 AI 味", default to Humanize unless the document is already strong and only needs light polish.

## File Handling

For Markdown or plain text, produce a new file next to the source with a clear suffix such as `_润色版` unless the user specifies a target path.

For DOCX, preserve formatting where possible. If the documents skill is available and the task requires Word rendering or comments, use it together with this skill.

For PDF input, extract or convert text first when possible. If the PDF is a source reference rather than the editable report, use it only to verify facts and terminology.

## Output Standards

The revised result should:

- Sound natural in Chinese academic/coursework style.
- Keep the author's original meaning and viewpoint.
- Preserve section requirements from the assignment or teacher.
- Avoid fabricated data, sources, screenshots, procedures, or personal experience.
- Be specific enough that it appears written from the actual experiment, not from a generic template.
