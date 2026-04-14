import re
from datetime import datetime
from pathlib import Path
from typing import Any, Sequence

import yaml

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*(?:\n|$)", re.S)


def _normalize_text(raw: str) -> str:
    return raw.replace("\r\n", "\n").replace("\r", "\n").lstrip("\ufeff")


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    normalized = _normalize_text(text)
    match = _FRONTMATTER_RE.match(normalized)
    if not match:
        return {}, normalized
    try:
        meta = yaml.safe_load(match.group(1)) or {}
    except Exception:
        meta = {}
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


def _build_summary(text: str, limit: int = 160) -> str:
    collapsed = " ".join(line.strip() for line in _normalize_text(text).split("\n") if line.strip())
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[: limit - 3].rstrip() + "..."


def _normalize_relative_path(relative_path: str, *, allow_empty: bool = False) -> str:
    raw = str(relative_path or "").strip().replace("\\", "/")
    while "//" in raw:
        raw = raw.replace("//", "/")
    raw = raw.lstrip("/")
    if not raw:
        if allow_empty:
            return ""
        raise ValueError("文件路径不能为空")
    path = Path(raw)
    if path.is_absolute():
        raise ValueError("文件路径必须是知识库目录内的相对路径")
    parts = [part for part in raw.split("/") if part not in {"", "."}]
    if not parts:
        if allow_empty:
            return ""
        raise ValueError("文件路径不能为空")
    if any(part == ".." for part in parts):
        raise ValueError("文件路径不合法")
    if ".obsidian" in parts:
        raise ValueError("不支持操作 .obsidian 目录")
    return "/".join(parts)


def _normalize_target_dir(target_dir: str | None) -> str:
    normalized = _normalize_relative_path(target_dir or "", allow_empty=True)
    if normalized.lower().endswith(".md"):
        raise ValueError("导入目录必须是文件夹路径")
    return normalized


def _resolve_root(vault_path: str | Path) -> Path:
    root = Path(vault_path).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def _resolve_md_file(vault_path: str | Path, relative_path: str) -> tuple[Path, str, Path]:
    root = _resolve_root(vault_path)
    normalized = _normalize_relative_path(relative_path)
    if not normalized.lower().endswith(".md"):
        raise ValueError("仅支持 .md 文件")
    file_path = (root / normalized).resolve()
    if not file_path.is_relative_to(root):
        raise ValueError("文件路径超出知识库目录")
    return root, normalized, file_path


def _read_text(file_path: Path) -> str:
    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return file_path.read_text(encoding="utf-8-sig", errors="ignore")


def _cleanup_empty_dirs(root: Path, current: Path):
    while current != root and current.is_relative_to(root):
        try:
            next(current.iterdir())
            return
        except StopIteration:
            current.rmdir()
            current = current.parent
        except FileNotFoundError:
            current = current.parent


def _serialize_file(root: Path, file_path: Path) -> dict[str, Any]:
    text = _read_text(file_path)
    meta, body = _parse_frontmatter(text)
    stat = file_path.stat()
    return {
        "path": file_path.relative_to(root).as_posix(),
        "name": file_path.name,
        "title": str(meta.get("title") or file_path.stem).strip() or file_path.stem,
        "status": str(meta.get("status") or "published").strip().lower() or "published",
        "tags": _coerce_list(meta.get("tags")),
        "aliases": _coerce_list(meta.get("aliases")),
        "summary": _build_summary(body),
        "size": stat.st_size,
        "updated_at": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
    }


def list_knowledge_files(vault_path: str | Path) -> list[dict[str, Any]]:
    root = _resolve_root(vault_path)
    result: list[dict[str, Any]] = []
    for md_file in sorted(root.rglob("*.md")):
        if ".obsidian" in md_file.parts:
            continue
        result.append(_serialize_file(root, md_file))
    return result


def get_knowledge_file_detail(vault_path: str | Path, relative_path: str) -> dict[str, Any]:
    root, normalized, file_path = _resolve_md_file(vault_path, relative_path)
    if not file_path.exists():
        raise FileNotFoundError(normalized)
    result = _serialize_file(root, file_path)
    result["content"] = _read_text(file_path)
    return result


def create_knowledge_file(vault_path: str | Path, relative_path: str, content: str) -> dict[str, Any]:
    if not str(content or "").strip():
        raise ValueError("文档内容不能为空")
    _, normalized, file_path = _resolve_md_file(vault_path, relative_path)
    if file_path.exists():
        raise FileExistsError(normalized)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(_normalize_text(content), encoding="utf-8")
    return get_knowledge_file_detail(vault_path, normalized)


def update_knowledge_file(vault_path: str | Path, relative_path: str, content: str, new_path: str | None = None) -> dict[str, Any]:
    if not str(content or "").strip():
        raise ValueError("文档内容不能为空")
    root, normalized, file_path = _resolve_md_file(vault_path, relative_path)
    if not file_path.exists():
        raise FileNotFoundError(normalized)
    target_path = file_path
    target_relative_path = normalized
    if str(new_path or "").strip():
        _, next_relative_path, next_path = _resolve_md_file(vault_path, new_path or "")
        if next_relative_path != normalized:
            if next_path.exists():
                raise FileExistsError(next_relative_path)
            next_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.replace(next_path)
            _cleanup_empty_dirs(root, file_path.parent)
            target_path = next_path
            target_relative_path = next_relative_path
    target_path.write_text(_normalize_text(content), encoding="utf-8")
    return get_knowledge_file_detail(vault_path, target_relative_path)


def delete_knowledge_file(vault_path: str | Path, relative_path: str) -> dict[str, str]:
    root, normalized, file_path = _resolve_md_file(vault_path, relative_path)
    if not file_path.exists():
        raise FileNotFoundError(normalized)
    file_path.unlink()
    _cleanup_empty_dirs(root, file_path.parent)
    return {"path": normalized}


def import_knowledge_files(vault_path: str | Path, files: Sequence[dict[str, Any]], target_dir: str | None = None, overwrite: bool = False) -> dict[str, Any]:
    if not files:
        raise ValueError("请选择要导入的 Markdown 文件")
    root = _resolve_root(vault_path)
    normalized_target_dir = _normalize_target_dir(target_dir)
    imported: list[str] = []
    skipped: list[dict[str, str]] = []
    for item in files:
        filename = Path(str(item.get("filename") or "")).name
        if not filename:
            skipped.append({"filename": "", "reason": "文件名为空"})
            continue
        if not filename.lower().endswith(".md"):
            skipped.append({"filename": filename, "reason": "仅支持导入 .md 文件"})
            continue
        relative_path = f"{normalized_target_dir}/{filename}" if normalized_target_dir else filename
        _, normalized, file_path = _resolve_md_file(root, relative_path)
        if file_path.exists() and not overwrite:
            skipped.append({"filename": filename, "path": normalized, "reason": "文件已存在，请开启覆盖导入或修改文件名"})
            continue
        raw_content = item.get("content") or b""
        if isinstance(raw_content, bytes):
            try:
                text = raw_content.decode("utf-8")
            except UnicodeDecodeError:
                text = raw_content.decode("utf-8-sig", errors="ignore")
        else:
            text = str(raw_content)
        normalized_text = _normalize_text(text)
        if not normalized_text.strip():
            skipped.append({"filename": filename, "reason": "文件内容为空"})
            continue
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(normalized_text, encoding="utf-8")
        imported.append(normalized)
    return {
        "target_dir": normalized_target_dir,
        "total": len(files),
        "imported_count": len(imported),
        "skipped_count": len(skipped),
        "imported": imported,
        "skipped": skipped,
    }
