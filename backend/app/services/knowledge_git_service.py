"""Git 同步服务：clone / pull 知识库仓库到本地 vault 目录"""
import asyncio
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_GIT_TIMEOUT = 120  # 秒


class GitSyncError(Exception):
    pass


async def _run_git(args: list[str], cwd: str | Path | None = None, timeout: int = _GIT_TIMEOUT) -> str:
    cmd = ["git"] + args
    logger.info("[Git] 执行: %s | cwd=%s", " ".join(cmd), cwd or "(default)")
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(cwd) if cwd else None,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        stdout_bytes, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        output = (stdout_bytes or b"").decode("utf-8", errors="replace").strip()
    except asyncio.TimeoutError as exc:
        raise GitSyncError(f"git 命令超时（{timeout}s）: {' '.join(cmd)}") from exc
    except FileNotFoundError as exc:
        raise GitSyncError("未找到 git 命令，请确认服务器已安装 Git 并在 PATH 中") from exc

    if proc.returncode != 0:
        logger.warning("[Git] 非零返回码 %s | output=%s", proc.returncode, output[:500])
        raise GitSyncError(f"git 命令失败（exit {proc.returncode}）: {output[:500]}")

    logger.info("[Git] 输出: %s", output[:300] if output else "(empty)")
    return output


async def git_sync(vault_path: str, repo_url: str, branch: str = "main") -> dict[str, Any]:
    """
    将远程仓库同步到 vault_path。

    - 如果 vault_path 不存在或为空目录 → git clone
    - 如果 vault_path 已有 .git → git fetch + checkout + pull
    - 如果 vault_path 存在且非空、但没有 .git → 报错
    """
    vault = Path(vault_path)
    result: dict[str, Any] = {
        "action": "",
        "repo_url": repo_url,
        "branch": branch,
        "vault_path": str(vault),
        "output": "",
    }

    logger.info("[Git] 开始同步 | repo=%s branch=%s vault=%s", repo_url, branch, vault)

    if not repo_url or not repo_url.strip():
        raise GitSyncError("Git 仓库地址为空，请先在知识源配置中填写 Git Repo URL")

    is_empty_dir = vault.is_dir() and not any(vault.iterdir())
    has_git = (vault / ".git").is_dir()

    if not vault.exists() or is_empty_dir:
        # clone
        logger.info("[Git] 目标目录不存在或为空，执行 clone")
        vault.mkdir(parents=True, exist_ok=True)
        output = await _run_git(["clone", "--branch", branch, "--single-branch", "--depth", "1", repo_url, str(vault)])
        result["action"] = "clone"
        result["output"] = output

    elif has_git:
        # fetch + checkout + pull
        logger.info("[Git] 目标目录已有 .git，执行 fetch + checkout + pull")
        await _run_git(["fetch", "--all", "--prune"], cwd=vault)
        try:
            await _run_git(["checkout", branch], cwd=vault)
        except GitSyncError:
            await _run_git(["checkout", "-b", branch, f"origin/{branch}"], cwd=vault)
        output = await _run_git(["pull", "origin", branch], cwd=vault)
        result["action"] = "pull"
        result["output"] = output

    else:
        raise GitSyncError(
            f"目标目录 {vault} 已存在且非空，但不是 Git 仓库。"
            " 请手动清空该目录，或在知识源配置中修改 Vault 路径后重试。"
        )

    logger.info("[Git] 同步完成 | action=%s vault=%s", result["action"], vault)
    return result
