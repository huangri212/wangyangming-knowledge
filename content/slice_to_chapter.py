#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE_FILE = ROOT / "传习录.md"
OUTPUT_ROOT = ROOT / "导览" / "传习录"

SECTION_LINE_RE = re.compile(r"^#\s+(.+?)\s*$", re.M)
APPENDIX_SECTION_LINE_RE = re.compile(r"^###\s+(.+?)\s*$")
SUBSECTION_LINE_RE = re.compile(r"^####\s+([一二三四五六七八九十百千]+)\s+(.+?)\s*$")
FRONTMATTER_RE = re.compile(r"^---\n.*?\n---\n", re.S)

CHAPTERS = [
    {
        "folder": "前言",
        "children": [],
    },
    {
        "folder": "传习录上",
        "children": [
            "传习录序",
            "徐爱录　凡十四则",
            "陆澄录　凡七十三则",
            "薛侃录　凡三十五则",
        ],
    },
    {
        "folder": "传习录中",
        "children": [
            "钱德洪序",
            "答顾东桥书　凡十二则",
            "答周道通书　凡七则",
            "答陆原静书　凡四则",
            "答欧阳崇一　凡四则",
            "答罗整庵少宰书　凡四则",
            "答聂文蔚　凡七则",
            "答聂文蔚二　凡九则",
            "训蒙大意示教读刘伯颂等",
            "教约",
        ],
    },
    {
        "folder": "传习录下",
        "children": [
            "陈九川录　凡十四则",
            "黄直录　凡十二则",
            "黄修易录　凡十一则",
            "黄省曾录　凡十一则",
            "钱德洪录　凡四十八则",
            "黄以方录　凡二十五则",
            "钱德洪跋",
            "传习录附录",
        ],
    },
]


def slugify(name: str) -> str:
    name = re.sub(r"[\/:*?\"<>|]+", "", name.strip())
    return name


def strip_frontmatter(text: str) -> str:
    return FRONTMATTER_RE.sub("", text, count=1)


def split_top_sections(text: str) -> list[tuple[str, str]]:
    matches = list(SECTION_LINE_RE.finditer(text))
    sections: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[start:end].strip() + "\n"
        sections.append((title, body))
    return sections


def split_preface_into_subsections(content: str) -> list[tuple[str, str]]:
    lines = content.splitlines()
    subsection_indices: list[tuple[int, str]] = []
    for idx, line in enumerate(lines):
        matched = SUBSECTION_LINE_RE.match(line)
        if matched:
            subsection_indices.append((idx, matched.group(2).strip()))

    if not subsection_indices:
        return [("前言", content.strip() + "\n")]

    result: list[tuple[str, str]] = []
    for i, (line_index, title) in enumerate(subsection_indices):
        end = subsection_indices[i + 1][0] if i + 1 < len(subsection_indices) else len(lines)
        body = "\n".join(lines[line_index:end]).strip() + "\n"
        result.append((title, body))
    return result


def split_appendix_into_sections(content: str) -> list[tuple[str, str]]:
    lines = content.splitlines()
    section_indices: list[tuple[int, str]] = []
    for idx, line in enumerate(lines):
        matched = APPENDIX_SECTION_LINE_RE.match(line)
        if matched:
            section_indices.append((idx, matched.group(1).strip()))

    if not section_indices:
        return [("传习录附录", content.strip() + "\n")]

    result: list[tuple[str, str]] = []
    for i, (line_index, title) in enumerate(section_indices):
        end = section_indices[i + 1][0] if i + 1 < len(section_indices) else len(lines)
        body = "\n".join(lines[line_index:end]).strip() + "\n"
        result.append((title, body))
    return result


def build_folder_index(folder: str, generated_files: list[str]) -> str:
    lines = [f"# {folder}", ""]
    for file_name in generated_files:
        title = file_name.removesuffix(".md")
        lines.append(f"- [[{folder}/{title}|{title}]]")
    lines.append("")
    return "\n".join(lines)


def write_root_index() -> None:
    lines = ["# 传习录", ""]
    for chapter in CHAPTERS:
        folder = chapter["folder"]
        lines.append(f"- [[导览/传习录/{folder}/index|{folder}]]")
    lines.append("")
    (OUTPUT_ROOT / "index.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    source_text = strip_frontmatter(SOURCE_FILE.read_text(encoding="utf-8"))
    top_sections = dict(split_top_sections(source_text))

    if OUTPUT_ROOT.exists():
        shutil.rmtree(OUTPUT_ROOT)
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    preface_content = source_text.split("# 传习录上", 1)[0].strip()
    if not preface_content:
        raise ValueError("未找到《传习录上》之前的前言内容")

    for chapter in CHAPTERS:
        chapter_dir = OUTPUT_ROOT / chapter["folder"]
        chapter_dir.mkdir(parents=True, exist_ok=True)
        generated_files: list[str] = []

        if chapter["folder"] == "前言":
            for title, body in split_preface_into_subsections(preface_content):
                file_name = f"{slugify(title)}.md"
                (chapter_dir / file_name).write_text(body, encoding="utf-8")
                generated_files.append(file_name)
        else:
            for child in chapter["children"]:
                body = top_sections.get(child)
                if not body:
                    raise ValueError(f"未找到章节：{child}")

                if child == "传习录附录":
                    for appendix_title, appendix_body in split_appendix_into_sections(body):
                        file_name = f"{slugify(appendix_title)}.md"
                        (chapter_dir / file_name).write_text(appendix_body, encoding="utf-8")
                        generated_files.append(file_name)
                    continue

                file_name = f"{slugify(child)}.md"
                (chapter_dir / file_name).write_text(body, encoding="utf-8")
                generated_files.append(file_name)

        (chapter_dir / "index.md").write_text(
            build_folder_index(chapter["folder"], generated_files),
            encoding="utf-8",
        )

    write_root_index()
    print(f"已生成：{OUTPUT_ROOT}")


if __name__ == "__main__":
    main()