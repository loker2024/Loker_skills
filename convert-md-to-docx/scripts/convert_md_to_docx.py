#!/usr/bin/env python3
"""Prepare Markdown diagrams/assets and convert the result to DOCX with Pandoc."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path


DIAGRAM_EXTENSIONS = {
    "mermaid": ".mmd",
    "mmd": ".mmd",
    "graphviz": ".dot",
    "dot": ".dot",
    "plantuml": ".puml",
    "puml": ".puml",
}

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
BROWSER_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
]


def parse_image_target(raw_target: str) -> tuple[str, str]:
    target = raw_target.strip()
    title = ""
    if " " in target and not target.startswith("<"):
        match = re.match(r"([^ ]+)\s+(.+)$", target)
        if match:
            target, title = match.group(1), match.group(2)
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    return target, title


def is_remote_or_special(target: str) -> bool:
    lowered = target.lower()
    return (
        "://" in lowered
        or lowered.startswith("data:")
        or lowered.startswith("#")
        or lowered.startswith("mailto:")
    )


def relative_markdown_path(path: Path, base_dir: Path) -> str:
    try:
        return path.resolve().relative_to(base_dir.resolve()).as_posix()
    except ValueError:
        return os.path.relpath(path.resolve(), base_dir.resolve()).replace(os.sep, "/")


def run_command(command: list[str], timeout: int | None = None) -> tuple[bool, str]:
    try:
        proc = subprocess.Popen(
            command,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
        stdout, stderr = proc.communicate(timeout=timeout)
    except FileNotFoundError as exc:
        return False, str(exc)
    except subprocess.TimeoutExpired as exc:
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except Exception:
            proc.kill()
        stdout, stderr = proc.communicate()
        output = "\n".join(part for part in (stdout.strip(), stderr.strip()) if part)
        suffix = f"\n{output}" if output else ""
        return False, f"Command timed out after {timeout} seconds.{suffix}"
    output = "\n".join(part for part in (stdout.strip(), stderr.strip()) if part)
    return proc.returncode == 0, output


def find_browser_executable() -> str | None:
    env_path = os.environ.get("PUPPETEER_EXECUTABLE_PATH")
    if env_path and Path(env_path).exists():
        return env_path
    for candidate in BROWSER_CANDIDATES:
        if Path(candidate).exists():
            return candidate
    return None


def mermaid_puppeteer_args() -> tuple[list[str], Path | None]:
    browser = find_browser_executable()
    if not browser:
        return [], None
    config = {
        "executablePath": browser,
        "args": ["--no-sandbox", "--disable-setuid-sandbox"],
    }
    handle = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    with handle:
        json.dump(config, handle)
    config_path = Path(handle.name)
    return ["-p", str(config_path)], config_path


def render_diagram(kind: str, source_file: Path, image_file: Path, timeout: int) -> tuple[bool, str]:
    normalized = "mermaid" if kind in {"mermaid", "mmd"} else kind

    if normalized == "mermaid":
        puppet_args, config_path = mermaid_puppeteer_args()
        try:
            if shutil.which("mmdc"):
                return run_command(["mmdc", "-i", str(source_file), "-o", str(image_file), "-b", "transparent", *puppet_args], timeout)
            if shutil.which("npx"):
                return run_command(
                    [
                        "npx",
                        "-y",
                        "@mermaid-js/mermaid-cli",
                        "-i",
                        str(source_file),
                        "-o",
                        str(image_file),
                        "-b",
                        "transparent",
                        *puppet_args,
                    ],
                    timeout,
                )
            return False, "Missing Mermaid renderer: install mmdc or npx."
        finally:
            if config_path:
                config_path.unlink(missing_ok=True)

    if normalized in {"graphviz", "dot"}:
        if shutil.which("dot"):
            return run_command(["dot", "-Tpng", str(source_file), "-o", str(image_file)], timeout)
        return False, "Missing Graphviz renderer: install dot."

    if normalized in {"plantuml", "puml"}:
        if not shutil.which("plantuml"):
            return False, "Missing PlantUML renderer: install plantuml."
        ok, output = run_command(["plantuml", "-tpng", str(source_file)], timeout)
        generated = source_file.with_suffix(".png")
        if ok and generated.exists():
            generated.replace(image_file)
            return True, output
        return False, output or "PlantUML did not produce a PNG."

    return False, f"Unsupported diagram type: {kind}"


class Converter:
    def __init__(self, args: argparse.Namespace) -> None:
        self.input_md = Path(args.input_md).expanduser().resolve()
        if not self.input_md.exists():
            raise FileNotFoundError(f"Markdown file not found: {self.input_md}")
        if self.input_md.suffix.lower() not in {".md", ".markdown"}:
            raise ValueError("Input file should be .md or .markdown")

        self.output_docx = Path(args.output).expanduser().resolve() if args.output else self.input_md.with_suffix(".docx")
        self.work_dir = self.output_docx.parent
        self.work_dir.mkdir(parents=True, exist_ok=True)

        default_assets = self.work_dir / f"{self.input_md.stem}_docx_assets"
        self.assets_dir = Path(args.assets_dir).expanduser().resolve() if args.assets_dir else default_assets
        self.assets_dir.mkdir(parents=True, exist_ok=True)

        self.prepared_md = Path(args.prepared_md).expanduser().resolve() if args.prepared_md else self.work_dir / f"{self.input_md.stem}_docx_prepared.md"
        self.manifest = self.assets_dir / "figure_manifest.csv"
        self.reference_doc = Path(args.reference_doc).expanduser().resolve() if args.reference_doc else None
        self.no_pandoc = args.no_pandoc
        self.strict = args.strict
        self.render_timeout = args.render_timeout
        self.pandoc_args = args.pandoc_arg or []
        self.figure_index = 0
        self.rows: list[dict[str, str]] = []

    def next_figure(self, kind: str, suffix: str) -> tuple[str, Path]:
        self.figure_index += 1
        fig_id = f"FIG-{self.figure_index:03d}"
        file_path = self.assets_dir / f"{self.figure_index:03d}{suffix}"
        return fig_id, file_path

    def add_manifest_row(
        self,
        *,
        fig_id: str,
        kind: str,
        source_file: Path | None,
        image_file: Path | None,
        status: str,
        caption: str,
        original_ref: str,
        note: str,
    ) -> None:
        self.rows.append(
            {
                "figure_id": fig_id,
                "kind": kind,
                "source_file": relative_markdown_path(source_file, self.work_dir) if source_file else "",
                "image_file": relative_markdown_path(image_file, self.work_dir) if image_file else "",
                "status": status,
                "caption": caption,
                "original_ref": original_ref,
                "note": note,
            }
        )

    def process_diagram_block(self, fence: str, info: str, body: list[str]) -> list[str]:
        kind = info.strip().split()[0].lower() if info.strip() else ""
        if kind not in DIAGRAM_EXTENSIONS:
            return [fence + info.rstrip() + "\n", *body, fence + "\n"]

        source_ext = DIAGRAM_EXTENSIONS[kind]
        fig_id, source_file = self.next_figure(kind, source_ext)
        image_file = source_file.with_suffix(".png")
        source_file.write_text("".join(body).rstrip() + "\n", encoding="utf-8")

        ok, render_note = render_diagram(kind, source_file, image_file, self.render_timeout)
        rel_source = relative_markdown_path(source_file, self.work_dir)
        rel_image = relative_markdown_path(image_file, self.work_dir)
        display_kind = "mermaid" if kind == "mmd" else kind

        if ok and image_file.exists():
            status = "rendered"
            note = render_note
            self.add_manifest_row(
                fig_id=fig_id,
                kind=display_kind,
                source_file=source_file,
                image_file=image_file,
                status=status,
                caption=fig_id,
                original_ref=f"fenced:{display_kind}",
                note=note,
            )
            return [
                f"\n**[图位 {fig_id} | 类型: {display_kind} | 文件: {rel_image} | 源文件: {rel_source}]**\n\n",
                f"![{fig_id}: {display_kind}]({rel_image})\n\n",
            ]

        status = "render_failed"
        if self.strict:
            raise RuntimeError(f"{fig_id} {display_kind} render failed: {render_note}")
        self.add_manifest_row(
            fig_id=fig_id,
            kind=display_kind,
            source_file=source_file,
            image_file=None,
            status=status,
            caption=fig_id,
            original_ref=f"fenced:{display_kind}",
            note=render_note,
        )
        return [
            f"\n**[图位 {fig_id} | 类型: {display_kind} | 图片未生成 | 源文件: {rel_source}]**\n\n",
            f"> {render_note}\n\n",
            f"```{display_kind}\n",
            *body,
            "```\n\n",
        ]

    def copy_image(self, alt: str, target: str, title: str) -> tuple[str, str | None]:
        if is_remote_or_special(target):
            return f"![{alt}]({target}{(' ' + title) if title else ''})", None

        source = (self.input_md.parent / target).resolve()
        if not source.exists() or source.suffix.lower() not in IMAGE_EXTENSIONS:
            return f"![{alt}]({target}{(' ' + title) if title else ''})", None

        fig_id, asset_path = self.next_figure("image", source.suffix.lower())
        shutil.copy2(source, asset_path)
        rel_asset = relative_markdown_path(asset_path, self.work_dir)
        self.add_manifest_row(
            fig_id=fig_id,
            kind="image",
            source_file=source,
            image_file=asset_path,
            status="copied",
            caption=alt or fig_id,
            original_ref=target,
            note="local image copied into strict assets directory",
        )
        caption = alt or "image"
        replacement = f"![{fig_id}: {caption}]({rel_asset})"
        return replacement, f"**[图位 {fig_id} | 类型: image | 文件: {rel_asset} | 原文件: {target}]**"

    def process_image_line(self, line: str) -> list[str]:
        annotations: list[str] = []

        def repl(match: re.Match[str]) -> str:
            alt = match.group(1)
            raw_target = match.group(2)
            target, title = parse_image_target(raw_target)
            replacement, annotation = self.copy_image(alt, target, title)
            if annotation:
                annotations.append(annotation)
            return replacement

        new_line = IMAGE_RE.sub(repl, line)
        if not annotations:
            return [new_line]
        return ["\n", *[annotation + "\n\n" for annotation in annotations], new_line]

    def prepare_markdown(self) -> None:
        lines = self.input_md.read_text(encoding="utf-8").splitlines(keepends=True)
        output: list[str] = []
        i = 0
        while i < len(lines):
            line = lines[i]
            match = re.match(r"^( {0,3})(`{3,}|~{3,})([^\n]*)\n?$", line)
            if not match:
                output.extend(self.process_image_line(line))
                i += 1
                continue

            indent, fence, info = match.groups()
            body: list[str] = []
            i += 1
            close_re = re.compile(rf"^{re.escape(indent)}{re.escape(fence)}\s*$")
            while i < len(lines) and not close_re.match(lines[i].rstrip("\n")):
                body.append(lines[i])
                i += 1
            if i < len(lines):
                i += 1
            output.extend(self.process_diagram_block(indent + fence, info, body))

        self.prepared_md.write_text("".join(output), encoding="utf-8")
        with self.manifest.open("w", newline="", encoding="utf-8") as handle:
            fieldnames = ["figure_id", "kind", "source_file", "image_file", "status", "caption", "original_ref", "note"]
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.rows)

    def convert_with_pandoc(self) -> None:
        if self.no_pandoc:
            return
        if not shutil.which("pandoc"):
            raise RuntimeError("Pandoc is required for DOCX conversion. Install pandoc or rerun with --no-pandoc.")

        command = [
            "pandoc",
            str(self.prepared_md),
            "--from",
            "markdown+pipe_tables+tex_math_dollars+tex_math_single_backslash",
            "--to",
            "docx",
            "--standalone",
            "--resource-path",
            f"{self.work_dir}{os.pathsep}{self.assets_dir}{os.pathsep}{self.input_md.parent}",
            "-o",
            str(self.output_docx),
        ]
        if self.reference_doc:
            command.extend(["--reference-doc", str(self.reference_doc)])
        command.extend(self.pandoc_args)

        ok, output = run_command(command)
        if not ok:
            raise RuntimeError(f"Pandoc conversion failed:\n{output}")

    def run(self) -> None:
        self.prepare_markdown()
        self.convert_with_pandoc()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert Markdown to DOCX while extracting diagrams and local images.")
    parser.add_argument("input_md", help="Input .md/.markdown file")
    parser.add_argument("-o", "--output", help="Output DOCX path. Defaults to input path with .docx suffix.")
    parser.add_argument("--assets-dir", help="Directory for extracted/rendered figure assets. Defaults to <stem>_docx_assets near the DOCX.")
    parser.add_argument("--prepared-md", help="Prepared Markdown path. Defaults to <stem>_docx_prepared.md near the DOCX.")
    parser.add_argument("--reference-doc", help="Optional Pandoc reference DOCX template.")
    parser.add_argument("--pandoc-arg", action="append", help="Extra argument passed to Pandoc. Repeat for multiple arguments.")
    parser.add_argument("--no-pandoc", action="store_true", help="Only prepare Markdown/assets/manifest; do not create DOCX.")
    parser.add_argument("--strict", action="store_true", help="Fail if any diagram cannot be rendered.")
    parser.add_argument("--render-timeout", type=int, default=120, help="Seconds to wait for each diagram renderer before keeping a placeholder.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        converter = Converter(args)
        converter.run()
    except Exception as exc:  # noqa: BLE001 - CLI should present concise failure text.
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Prepared Markdown: {converter.prepared_md}")
    print(f"Assets directory: {converter.assets_dir}")
    print(f"Figure manifest: {converter.manifest}")
    if not converter.no_pandoc:
        print(f"DOCX output: {converter.output_docx}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
