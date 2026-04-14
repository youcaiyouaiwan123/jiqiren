import re
from hashlib import sha1
from pathlib import Path
from typing import Any

import yaml

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*(?:\n|$)", re.S)
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")


def _normalize_text(raw: str) -> str:
    return raw.replace("\r\n", "\n").replace("\r", "\n").lstrip("\ufeff")


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    normalized = _normalize_text(text)
    match = _FRONTMATTER_RE.match(normalized)
    if not match:
        return {}, normalized
    meta = yaml.safe_load(match.group(1)) or {}
    if not isinstance(meta, dict):
        meta = {}
    return meta, normalized[match.end():]


def _coerce_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        values = re.split(r"[,|\n]", value)
    elif isinstance(value, list):
        values = value
    else:
        return []
    result: list[str] = []
    for item in values:
        text = str(item).strip()
        if text and text not in result:
            result.append(text)
    return result


def _split_long_text(text: str, max_chars: int) -> list[str]:
    content = text.strip()
    if not content:
        return []
    if len(content) <= max_chars:
        return [content]
    pieces: list[str] = []
    start = 0
    while start < len(content):
        end = min(len(content), start + max_chars)
        if end < len(content):
            pivot = max(
                content.rfind("\n", start, end),
                content.rfind("。", start, end),
                content.rfind("！", start, end),
                content.rfind("？", start, end),
                content.rfind(".", start, end),
            )
            if pivot > start + max_chars // 2:
                end = pivot + 1
        piece = content[start:end].strip()
        if piece:
            pieces.append(piece)
        start = end
    return pieces


def _chunk_paragraphs(title: str, text: str, max_chars: int = 900) -> list[dict[str, str]]:
    paragraphs = [part.strip() for part in re.split(r"\n{2,}", text) if part.strip()]
    if not paragraphs:
        return []
    chunks: list[dict[str, str]] = []
    buffer: list[str] = []
    length = 0
    for paragraph in paragraphs:
        for piece in _split_long_text(paragraph, max_chars):
            extra = len(piece) + (2 if buffer else 0)
            if buffer and length + extra > max_chars:
                chunks.append({"title": title, "content": "\n\n".join(buffer)})
                buffer = [piece]
                length = len(piece)
            else:
                buffer.append(piece)
                length += extra
    if buffer:
        chunks.append({"title": title, "content": "\n\n".join(buffer)})
    return chunks


def _build_sections(body: str, doc_title: str) -> list[dict[str, str]]:
    lines = _normalize_text(body).split("\n")
    sections: list[dict[str, str]] = []
    current_heading = ""
    current_lines: list[str] = []
    for raw_line in lines:
        stripped = raw_line.strip()
        match = _HEADING_RE.match(stripped)
        if match:
            level = len(match.group(1))
            heading = match.group(2).strip()
            if level == 1:
                if not doc_title and heading:
                    doc_title = heading
                continue
            if heading:
                title = doc_title if not current_heading else f"{doc_title} > {current_heading}"
                content = "\n".join(current_lines).strip()
                if content:
                    sections.extend(_chunk_paragraphs(title, content))
                current_heading = heading
                current_lines = []
                continue
        current_lines.append(raw_line)
    title = doc_title if not current_heading else f"{doc_title} > {current_heading}"
    content = "\n".join(current_lines).strip()
    if content:
        sections.extend(_chunk_paragraphs(title, content))
    return sections


def load_knowledge_chunks(vault_path: str | Path) -> tuple[list[dict[str, Any]], dict[str, int]]:
    root = Path(vault_path)
    if not root.exists():
        return [], {"files": 0, "published_files": 0, "skipped_files": 0, "chunks": 0}

    chunks: list[dict[str, Any]] = []
    files = 0
    published_files = 0
    skipped_files = 0

    for md_file in sorted(root.rglob("*.md")):
        if ".obsidian" in md_file.parts:
            continue
        files += 1
        try:
            text = md_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = md_file.read_text(encoding="utf-8-sig", errors="ignore")
        meta, body = _parse_frontmatter(text)
        status = str(meta.get("status", "published")).strip().lower()
        if status and status != "published":
            skipped_files += 1
            continue
        published_files += 1
        doc_title = str(meta.get("title") or md_file.stem).strip() or md_file.stem
        sections = _build_sections(body, doc_title)
        if not sections:
            sections = _chunk_paragraphs(doc_title, body)
        tags = _coerce_list(meta.get("tags"))
        aliases = _coerce_list(meta.get("aliases"))
        source_file = md_file.relative_to(root).as_posix()
        for index, section in enumerate(sections, start=1):
            content = section["content"].strip()
            if not content:
                continue
            chunk_key = f"{source_file}:{index}:{section['title']}"
            chunks.append(
                {
                    "id": sha1(chunk_key.encode("utf-8")).hexdigest(),
                    "title": section["title"],
                    "content": content,
                    "source_file": source_file,
                    "source_title": doc_title,
                    "tags": tags,
                    "aliases": aliases,
                }
            )

    return chunks, {
        "files": files,
        "published_files": published_files,
        "skipped_files": skipped_files,
        "chunks": len(chunks),
    }
