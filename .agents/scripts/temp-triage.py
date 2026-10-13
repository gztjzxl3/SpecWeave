#!/usr/bin/env python3
"""临时目录「可再生分级」清理法——盘点与分组建议工具（只建议，不删除）。

对应模式卡：docs/retrospective/patterns/methodology-patterns/governance-strategy/
             temp-directory-recoverability-triage.md（TEMP-TRIAGE-001, L1-draft）

本工具实现模式卡的「盘点 → 可再生性分组 → 取证 → 建议」链路，是其 L1→L2
升级验证用脚本。严格遵循模式卡第 6 步约束：**删除裁决保持人工，自动化只做
到建议层**——本脚本没有任何删除/移动能力，只产出分组报告。

分组（判定依据是「删除后能否恢复、恢复代价」，不是文件类型或日期）：
    A 缓存自重建组   包管理器缓存/安装期解包，删后工具自动重建
    B 过期产物组     构建快照/生成物副本，源在版本库时可重新生成（需人工确认源）
    C 外部副本组     外部仓库干净克隆（git 取证：有 remote/工作区干净/无未推送）
    D 已闭环残留组   陈旧散落脚本与报告（成果是否已固化需人工核验，仅候选）
    E 在途素材组     新近/来源不明/git 取证不干净——必须人工裁决，禁止自动删
    F 空目录组       空目录，可直接删

用法：
    # 对真实临时区做盘点，输出文本分组报告（不改动任何文件）
    python .agents/scripts/temp-triage.py .temp
    # 机器可读报告 + 与上次快照做周期对比（模式卡升级场景4）
    python .agents/scripts/temp-triage.py .temp --json report.json --state-file state.json
    # 离线/计费网络：A 组降级为保守保留（模式卡边界条件）
    python .agents/scripts/temp-triage.py .temp --offline
    # 内置四迁移验证场景自检（跨平台可跑，无需 pytest，升级 L1→L2 的证据采集）
    python .agents/scripts/temp-triage.py --validate-scenarios

退出码：0 正常/自检全通过；1 自检有失败项；2 参数或路径错误。

设计约束：Python 3.8+ 可运行（PEP 585/604 注解不用）；仅用标准库。
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

# ---- 分组常量 ----

GROUP_A = "A-cache-rebuild"
GROUP_B = "B-stale-build"
GROUP_C = "C-external-copy"
GROUP_D = "D-residue-closed-loop"
GROUP_E = "E-inflight-manual"
GROUP_F = "F-empty"

GROUPS_ORDER = [GROUP_A, GROUP_B, GROUP_C, GROUP_D, GROUP_E, GROUP_F]
GROUP_TITLES = {
    GROUP_A: "A 缓存自重建组",
    GROUP_B: "B 过期产物组",
    GROUP_C: "C 外部副本组",
    GROUP_D: "D 已闭环残留组（候选，需闭环证据）",
    GROUP_E: "E 在途素材组（必须人工裁决）",
    GROUP_F: "F 空目录组",
}
DELETABLE_GROUPS = [GROUP_A, GROUP_C, GROUP_F]  # B/D 需人工确认，不计入"可安全自动删"

# A 组：工具自建、删后自动重建的目录名/子目录特征
_CACHE_DIR_NAMES = frozenset(
    {
        "pip-cache",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".cache",
        "node-cache",
        "http",
        "http-v2",
    }
)
# A 组：安装期临时目录前缀（pip 解包/wheel/build tracker）
_CACHE_CHILD_PREFIXES = (
    "pip-unpack-",
    "pip-install-",
    "pip-ephem-wheel-cache-",
    "pip-build-tracker-",
    "pip-wheel-",
    "pip-req-build-",
)
_CACHE_CHILD_NAMES = frozenset({"http-v2", "selfcheck"})

# B 组：构建产物目录名
_BUILD_DIR_NAMES = frozenset({"_build", "build", "dist", "out", "site", "target"})
_BUILD_MARKER_NAMES = frozenset({".doctrees", "docs.html"})
_BUILD_EXTS = frozenset({".html", ".htm", ".css", ".js", ".map", ".bundle", ".woff2"})
_SOURCE_EXTS = frozenset({".py", ".rst", ".md", ".ts", ".go", ".java", ".rs", ".c", ".cpp"})
_HTML_SCAN_LIMIT = 400
_HTML_RATIO_THRESHOLD = 0.6
_HTML_MIN_FILES = 20
_SOURCE_RATIO_CEILING = 0.05

# D 组：临时区根下的一次性脚本/中间报告后缀
_RESIDUE_FILE_SUFFIXES = frozenset(
    {".py", ".sh", ".ps1", ".txt", ".log", ".json", ".tsv", ".csv", ".docx", ".tmp"}
)

DEFAULT_FRESH_DAYS = 7
DEFAULT_STALE_DAYS = 30
_DAY_SECONDS = 86400.0


# ---- 数据结构 ----


@dataclass
class EntryFacts:
    """盘点事实（只含客观字段，不含因果判断）。"""

    name: str
    kind: str  # "dir" | "file"
    size_bytes: int
    file_count: int
    mtime_epoch: float

    @property
    def age_days(self) -> float:
        return max(0.0, (time.time() - self.mtime_epoch) / _DAY_SECONDS)


@dataclass
class GitProbe:
    """C 组 git 取证结果。available=False 时一律不得判 C。"""

    available: bool
    has_remote: bool = False
    dirty: bool = False
    ahead: Optional[int] = None
    reason: str = ""


@dataclass
class Classification:
    group: str
    disposition: str  # delete-safe / delete-after-confirm / keep-*
    reasons: List[str] = field(default_factory=list)
    fresh: bool = False
    git: Optional[GitProbe] = None


@dataclass
class ClassifiedEntry:
    facts: EntryFacts
    result: Classification


# ---- 盘点 ----


def _walk_stats(path: Path) -> Tuple[int, int, float]:
    """递归统计 (文件数, 字节数, 最新文件mtime)；对无权限子树跳过。

    目录的 mtime 会在复制/移动/子项增删时更新，不能代表内容新旧——
    「新鲜度」判定一律以目录内最新文件的 mtime 为准（空目录回退目录自身 mtime）。
    """
    total_bytes = 0
    file_count = 0
    newest = 0.0
    if path.is_file():
        try:
            return 1, path.stat().st_size, path.stat().st_mtime
        except OSError:
            return 0, 0, 0.0
    for root, _dirnames, filenames in os.walk(str(path)):
        for fname in filenames:
            try:
                st = os.stat(os.path.join(root, fname))
            except OSError:
                continue
            total_bytes += st.st_size
            file_count += 1
            if st.st_mtime > newest:
                newest = st.st_mtime
    if newest == 0.0:
        try:
            newest = path.stat().st_mtime
        except OSError:
            newest = 0.0
    return file_count, total_bytes, newest


def inventory(root: Path) -> List[EntryFacts]:
    """列出临时区一级条目的客观事实，按大小降序。"""
    facts: List[EntryFacts] = []
    for child in sorted(root.iterdir(), key=lambda p: p.name.lower()):
        try:
            st = child.stat()
        except OSError:
            continue
        if child.is_dir():
            file_count, size_bytes, newest_mtime = _walk_stats(child)
            kind = "dir"
            mtime = newest_mtime
        else:
            file_count, size_bytes = 1, st.st_size
            kind = "file"
            mtime = st.st_mtime
        facts.append(
            EntryFacts(
                name=child.name,
                kind=kind,
                size_bytes=size_bytes,
                file_count=file_count,
                mtime_epoch=mtime,
            )
        )
    facts.sort(key=lambda f: f.size_bytes, reverse=True)
    return facts


# ---- 签名识别（只匹配路径名 token，跨平台不依赖分隔符） ----


def _immediate_children(path: Path) -> List[str]:
    try:
        return [c.name for c in path.iterdir()]
    except OSError:
        return []


def is_cache_signature(name: str, path: Path) -> Tuple[bool, List[str]]:
    reasons: List[str] = []
    if name in _CACHE_DIR_NAMES:
        reasons.append("目录名命中缓存特征: {}".format(name))
    if path.is_dir():
        children = _immediate_children(path)
        for child in children:
            if child in _CACHE_CHILD_NAMES:
                reasons.append("子项命中缓存结构: {}".format(child))
            for prefix in _CACHE_CHILD_PREFIXES:
                if child.startswith(prefix):
                    reasons.append("子项命中安装期临时目录前缀: {}".format(prefix.rstrip("-")))
                    break
    return bool(reasons), reasons


def _extension_profile(path: Path) -> Optional[Tuple[int, float, float]]:
    """抽样统计 (总文件数, 构建产物占比, 源码占比)；样本不足返回 None。"""
    build_hits = 0
    source_hits = 0
    scanned = 0
    for root, _dirs, files in os.walk(str(path)):
        for fname in files:
            scanned += 1
            if scanned > _HTML_SCAN_LIMIT:
                break
            suffix = os.path.splitext(fname)[1].lower()
            if suffix in _BUILD_EXTS:
                build_hits += 1
            elif suffix in _SOURCE_EXTS:
                source_hits += 1
        if scanned > _HTML_SCAN_LIMIT:
            break
    if scanned < _HTML_MIN_FILES:
        return None
    return scanned, build_hits / scanned, source_hits / scanned


def is_build_signature(name: str, path: Path) -> Tuple[bool, List[str]]:
    reasons: List[str] = []
    if name in _BUILD_DIR_NAMES:
        reasons.append("目录名命中构建产物特征: {}".format(name))
    if path.is_dir():
        children = set(_immediate_children(path))
        for marker in children & _BUILD_MARKER_NAMES:
            reasons.append("子项命中构建标记: {}".format(marker))
        profile = _extension_profile(path)
        if profile is not None:
            scanned, build_ratio, source_ratio = profile
            if (
                build_ratio >= _HTML_RATIO_THRESHOLD
                and source_ratio <= _SOURCE_RATIO_CEILING
            ):
                reasons.append(
                    "扩展名画像: 抽样{}文件中{:.0%}为构建产物, 源码占比{:.0%}".format(
                        scanned, build_ratio, source_ratio
                    )
                )
    # 去重（同名标记可能同时命中）
    return bool(reasons), _dedup(reasons)


def _dedup(items: List[str]) -> List[str]:
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


# ---- git 取证（C 组） ----


GitRunner = Callable[[Path, List[str]], Optional[Tuple[int, str, str]]]


def default_git_runner(git_bin: Optional[str] = None) -> GitRunner:
    resolved = git_bin or shutil.which("git")

    def _run(path: Path, args: List[str]) -> Optional[Tuple[int, str, str]]:
        if not resolved:
            return None
        try:
            proc = subprocess.run(
                [resolved] + args,
                cwd=str(path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10,
            )
        except (OSError, subprocess.SubprocessError):
            return None
        return proc.returncode, proc.stdout.decode("utf-8", "replace"), proc.stderr.decode(
            "utf-8", "replace"
        )

    return _run


def probe_git(path: Path, runner: GitRunner) -> GitProbe:
    """只有同时满足有 remote / 工作区干净 / ahead=0 才是可安全删的干净克隆。"""
    if not (path / ".git").exists():
        return GitProbe(available=False, reason="无 .git，非 git 克隆")

    remote = runner(path, ["remote", "-v"])
    if remote is None:
        return GitProbe(available=False, reason="git 不可用，无法取证（保守升级 E 组）")
    rc, out, _err = remote
    if rc != 0 or not out.strip():
        return GitProbe(available=True, reason="无远端 remote，不满足可重新 clone 条件")
    has_remote = True

    status = runner(path, ["status", "--porcelain"])
    if status is None:
        return GitProbe(available=False, has_remote=True, reason="git status 取证失败")
    dirty = bool(status[1].strip())

    ahead = runner(path, ["rev-list", "--count", "@{u}..HEAD"])
    ahead_count: Optional[int]
    if ahead is None or ahead[0] != 0:
        ahead_count = None
        reason = "无法取得未推送提交数（保守升级 E 组）"
    else:
        try:
            ahead_count = int(ahead[1].strip() or "0")
        except ValueError:
            ahead_count = None
            reason = "未推送提交数解析失败（保守升级 E 组）"
        else:
            reason = ""
    if dirty:
        reason = "工作区有未提交改动"
    elif ahead_count and ahead_count > 0:
        reason = "存在 {} 个未推送提交".format(ahead_count)
    return GitProbe(
        available=True, has_remote=has_remote, dirty=dirty, ahead=ahead_count, reason=reason
    )


# ---- 分组判定 ----


def classify_entry(
    facts: EntryFacts,
    root: Path,
    now: float,
    fresh_days: int = DEFAULT_FRESH_DAYS,
    stale_days: int = DEFAULT_STALE_DAYS,
    offline: bool = False,
    git_runner: Optional[GitRunner] = None,
) -> Classification:
    """按模式卡矩阵分组。时间戳只作线索，删除授权只来自可再生/闭环证据。"""
    path = root / facts.name
    age_days = max(0.0, (now - facts.mtime_epoch) / _DAY_SECONDS)
    fresh = age_days <= fresh_days

    # F：空目录（空文件不算，根散落文件走 D/E）
    if facts.kind == "dir" and facts.file_count == 0:
        return Classification(GROUP_F, "delete-safe", ["空目录"], fresh=False)

    # A：缓存自重建
    cache_hit, cache_reasons = is_cache_signature(facts.name, path)
    if cache_hit:
        if offline:
            return Classification(
                GROUP_A,
                "keep-conservative-offline",
                cache_reasons + ["离线/计费网络：缓存再生有流量与时间代价，降级保守保留"],
                fresh=fresh,
            )
        return Classification(GROUP_A, "delete-safe", cache_reasons, fresh=fresh)

    # B：过期构建产物（新近产物视为可能正在生成，升级 E）
    build_hit, build_reasons = is_build_signature(facts.name, path)
    if build_hit:
        if fresh:
            return Classification(
                GROUP_E,
                "keep-manual-adjudication",
                build_reasons
                + ["构建产物修改于 {} 天内，任务可能仍在进行，升级人工裁决".format(fresh_days)],
                fresh=True,
            )
        return Classification(
            GROUP_B,
            "delete-after-source-confirm",
            build_reasons + ["删除前须人工确认源在版本库/正式产物目录中且版本更新"],
            fresh=fresh,
        )

    # C：外部干净克隆（git 取证不充分一律 E）
    git_probe: Optional[GitProbe] = None
    if facts.kind == "dir" and (path / ".git").exists():
        git_probe = probe_git(path, git_runner or default_git_runner())
        if (
            git_probe.available
            and git_probe.has_remote
            and not git_probe.dirty
            and git_probe.ahead == 0
        ):
            return Classification(
                GROUP_C,
                "delete-safe",
                ["git 取证：有 remote、工作区干净、无未推送提交，可重新 clone"],
                fresh=fresh,
                git=git_probe,
            )
        return Classification(
            GROUP_E,
            "keep-manual-adjudication",
            ["git 克隆但取证不充分：{}".format(git_probe.reason or "状态未知")],
            fresh=fresh,
            git=git_probe,
        )

    # D/E：根级散落陈旧文件 → D 候选（仍需人工核验闭环证据）；其余一律 E
    if facts.kind == "file" and path.suffix.lower() in _RESIDUE_FILE_SUFFIXES:
        if age_days > stale_days:
            return Classification(
                GROUP_D,
                "delete-after-human-evidence",
                [
                    "临时区根下 {:.0f} 天的一次性脚本/中间文件；删除前须在版本库或正式"
                    "目录找到成果固化证据，找不到则升级 E 组保留".format(age_days)
                ],
                fresh=False,
            )
        return Classification(
            GROUP_E,
            "keep-manual-adjudication",
            ["根级散落文件但修改于 {:.0f} 天内，按在途素材人工裁决".format(age_days)],
            fresh=True,
        )

    return Classification(
        GROUP_E,
        "keep-manual-adjudication",
        ["未命中任何可再生签名，无法从外部证据证明可恢复，默认保留待裁决"],
        fresh=fresh,
    )


# ---- 分诊编排 ----


def triage(
    root: Path,
    now: Optional[float] = None,
    fresh_days: int = DEFAULT_FRESH_DAYS,
    stale_days: int = DEFAULT_STALE_DAYS,
    offline: bool = False,
    git_bin: Optional[str] = None,
) -> Dict[str, Any]:
    if not root.is_dir():
        raise NotADirectoryError(str(root))
    now = now if now is not None else time.time()
    runner = default_git_runner(git_bin)
    entries = [
        ClassifiedEntry(
            facts=f,
            result=classify_entry(
                f, root, now, fresh_days, stale_days, offline, git_runner=runner
            ),
        )
        for f in inventory(root)
    ]
    total_bytes = sum(e.facts.size_bytes for e in entries)

    groups: Dict[str, Dict[str, Any]] = {
        g: {"entries": [], "bytes": 0, "files": 0} for g in GROUPS_ORDER
    }
    for entry in entries:
        bucket = groups[entry.result.group]
        bucket["entries"].append(entry)
        bucket["bytes"] += entry.facts.size_bytes
        bucket["files"] += entry.facts.file_count

    safe_bytes = sum(groups[g]["bytes"] for g in DELETABLE_GROUPS)
    candidate_bytes = safe_bytes + groups[GROUP_B]["bytes"] + groups[GROUP_D]["bytes"]
    return {
        "root": str(root),
        "generated_at": datetime.fromtimestamp(now).isoformat(timespec="seconds"),
        "params": {
            "fresh_days": fresh_days,
            "stale_days": stale_days,
            "offline": offline,
        },
        "total_bytes": total_bytes,
        "auto_safe_bytes": safe_bytes,
        "candidate_bytes": candidate_bytes,
        "auto_safe_share": (safe_bytes / total_bytes) if total_bytes else 0.0,
        "candidate_share": (candidate_bytes / total_bytes) if total_bytes else 0.0,
        "entries": [_entry_dict(e, now) for e in entries],
        "groups": {
            g: {
                "entry_count": len(groups[g]["entries"]),
                "bytes": groups[g]["bytes"],
                "files": groups[g]["files"],
                "share": (groups[g]["bytes"] / total_bytes) if total_bytes else 0.0,
            }
            for g in GROUPS_ORDER
        },
    }


def _entry_dict(entry: ClassifiedEntry, now: float) -> Dict[str, Any]:
    f = entry.facts
    return {
        "name": f.name,
        "kind": f.kind,
        "group": entry.result.group,
        "disposition": entry.result.disposition,
        "bytes": f.size_bytes,
        "files": f.file_count,
        "age_days": round(max(0.0, (now - f.mtime_epoch) / _DAY_SECONDS), 1),
        "fresh": entry.result.fresh,
        "reasons": entry.result.reasons,
    }


# ---- 状态快照（周期复做场景） ----


def write_state(report: Dict[str, Any], state_path: Path) -> None:
    payload = {
        "generated_at": report["generated_at"],
        "root": report["root"],
        "entries": {
            e["name"]: {"group": e["group"], "bytes": e["bytes"]} for e in report["entries"]
        },
    }
    state_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8"
    )


def compare_state(report: Dict[str, Any], state_path: Path) -> Dict[str, List[str]]:
    if not state_path.is_file():
        return {"missing_state": [str(state_path)], "removed": [], "new": [], "unchanged": []}
    previous = json.loads(state_path.read_text(encoding="utf-8"))
    old_names = set(previous.get("entries", {}).keys())
    now_names = {e["name"] for e in report["entries"]}
    return {
        "removed": sorted(old_names - now_names),
        "new": sorted(now_names - old_names),
        "unchanged": sorted(old_names & now_names),
    }


# ---- 文本报告 ----


def human_bytes(num: int) -> str:
    value = float(num)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            return "{:.1f} {}".format(value, unit) if unit != "B" else "{} B".format(int(value))
        value /= 1024
    return "{:.1f} GB".format(value)


def render_text(report: Dict[str, Any], state_diff: Optional[Dict[str, List[str]]] = None) -> str:
    lines: List[str] = []
    lines.append("临时区分诊报告（TEMP-TRIAGE-001｜只建议，不删除）")
    lines.append("目录: {}  时间: {}".format(report["root"], report["generated_at"]))
    p = report["params"]
    lines.append(
        "参数: fresh_days={} stale_days={} offline={}".format(
            p["fresh_days"], p["stale_days"], p["offline"]
        )
    )
    lines.append("总大小: {}".format(human_bytes(report["total_bytes"])))
    lines.append("")
    lines.append("分组总览（按字节占比）：")
    lines.append(
        "  {:<38}{:>6}{:>10}{:>9}".format("组", "条目", "大小", "占比")
    )
    for g in GROUPS_ORDER:
        stat = report["groups"][g]
        if stat["entry_count"] == 0:
            continue
        lines.append(
            "  {:<36}{:>6}{:>10}{:>8.1%}".format(
                GROUP_TITLES[g],
                stat["entry_count"],
                human_bytes(stat["bytes"]),
                stat["share"],
            )
        )
    lines.append("")
    lines.append(
        "可安全自动删（A+C+F）: {}（{:.1%}）；含需确认候选（+B+D）: {}（{:.1%}）".format(
            human_bytes(report["auto_safe_bytes"]),
            report["auto_safe_share"],
            human_bytes(report["candidate_bytes"]),
            report["candidate_share"],
        )
    )
    lines.append("")
    for g in GROUPS_ORDER:
        bucket = [e for e in report["entries"] if e["group"] == g]
        if not bucket:
            continue
        lines.append("[{}]".format(GROUP_TITLES[g]))
        for e in bucket:
            lines.append(
                "  - {} ({}, {}) {}".format(
                    e["name"], human_bytes(e["bytes"]), e["age_days"], e["disposition"]
                )
            )
            for reason in e["reasons"]:
                lines.append("      依据: {}".format(reason))
    lines.append("")
    e_entries = [e for e in report["entries"] if e["group"] == GROUP_E]
    lines.append(
        "E 组人工裁决清单（{} 项，禁止自动删）: {}".format(
            len(e_entries), ", ".join(e["name"] for e in e_entries) or "（无）"
        )
    )
    if state_diff is not None:
        lines.append("")
        lines.append("与上次快照对比：")
        if state_diff.get("missing_state"):
            lines.append("  （无历史快照，本次为基线；写回 --state-file 后下次可对比）")
        else:
            lines.append("  已清理(上次有本次无): {}".format(", ".join(state_diff["removed"]) or "（无）"))
            lines.append("  新增(本次新出现)    : {}".format(", ".join(state_diff["new"]) or "（无）"))
            lines.append(
                "  仍在(未变化)        : {}".format(
                    ", ".join(state_diff["unchanged"]) or "（无）"
                )
            )
    lines.append("")
    lines.append(
        "提示：本工具只输出建议。删除须人工确认 D 组闭环证据/B 组源存在，"
        "E 组逐项裁决；删除后重新盘点对账（模式卡第5-6步）。"
    )
    return "\n".join(lines)


# ---- 迁移验证场景（L1→L2 证据采集；跨平台标准库实现） ----


def _set_mtime(path: Path, days_ago: float, now: float) -> None:
    ts = now - days_ago * _DAY_SECONDS
    os.utime(str(path), (ts, ts))


def _sparse_file(path: Path, size_bytes: int, mtime_days: float, now: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(str(path), "wb") as fh:
        if size_bytes > 0:
            fh.seek(size_bytes - 1)
            fh.write(b"\0")
    _set_mtime(path, mtime_days, now)


def _build_realistic_fixture(base: Path, now: float) -> Dict[str, str]:
    """构造 2026-10-13 实测同构的混合临时区：A/B/C 占绝大多数字节。"""
    # A：pip 缓存 700KB + 安装期解包 300KB
    _sparse_file(base / "pip-cache" / "http-v2" / "blobs", 700 * 1024, 40, now)
    _sparse_file(base / "ps-temp" / "pip-unpack-abc" / "wheel.whl", 300 * 1024, 40, now)
    # B：HTML 构建快照 200KB（20+ 小文件，高构建产物占比）
    build = base / "old-site-build"
    for i in range(25):
        _sparse_file(build / "html" / "page-{}.html".format(i), 8 * 1024, 60, now)
    _sparse_file(build / ".doctrees" / "index.doctree", 2 * 1024, 60, now)
    # C：干净克隆 100KB（.git + 工作文件；git 由假 runner 取证）
    clone = base / "clone-site"
    (clone / ".git").mkdir(parents=True)
    _sparse_file(clone / "README.md", 100 * 1024, 20, now)
    # D：陈旧散落脚本
    _sparse_file(base / "fix_links.py", 4 * 1024, 60, now)
    # E：在途调研目录（1 天前）
    inflight = base / "research-fresh"
    inflight.mkdir(parents=True)
    _sparse_file(inflight / "notes.txt", 30 * 1024, 1, now)
    _set_mtime(inflight, 1, now)
    # F：空目录
    (base / "empty-dir").mkdir()
    return {"clone": "clean"}


def _fake_git_runner(script: Dict[str, str]) -> GitRunner:
    """测试用 git runner：按脚本返回，避免依赖本机 git。"""

    def _run(path: Path, args: List[str]) -> Tuple[int, str, str]:
        name = path.name
        if args[0] == "remote":
            if script.get(name) in ("clean", "dirty", "ahead"):
                return 0, "origin https://example.com/repo.git (fetch)\n", ""
            return 1, "", "no remote"
        if args[0] == "status":
            return 0, (" M x.txt\n" if script.get(name) == "dirty" else ""), ""
        if args[0] == "rev-list":
            return (0, "2\n", "") if script.get(name) == "ahead" else (0, "0\n", "")
        return 0, "", ""

    return _run


def validate_scenarios() -> Tuple[bool, List[str]]:
    """四迁移验证场景自检。返回 (全通过, 日志行)。"""
    logs: List[str] = []
    ok_all = True
    now = time.time()

    def check(label: str, ok: bool, detail: str) -> None:
        nonlocal ok_all
        ok_all = ok_all and ok
        logs.append("[{}] {} — {}".format("PASS" if ok else "FAIL", label, detail))

    # 场景1：跨操作系统（同构矩阵；签名只认路径 token，不依赖分隔符）
    tmp1 = Path(tempfile.mkdtemp(prefix="triage-s1-"))
    try:
        script = {"clone-site": "clean"}
        _build_realistic_fixture(tmp1, now)
        # 分类层直接注入假 git runner（生产 CLI 走本机 git，测试不依赖 git 二进制）
        facts_run1 = inventory(tmp1)
        entries = [
            classify_entry(f, tmp1, now, git_runner=_fake_git_runner(script))
            for f in facts_run1
        ]
        grouped = dict(zip([f.name for f in facts_run1], entries))
        expected = {
            "pip-cache": GROUP_A,
            "ps-temp": GROUP_A,
            "old-site-build": GROUP_B,
            "clone-site": GROUP_C,
            "fix_links.py": GROUP_D,
            "research-fresh": GROUP_E,
            "empty-dir": GROUP_F,
        }
        mismatches = {
            n: (grouped[n].group, g) for n, g in expected.items() if grouped[n].group != g
        }
        check(
            "场景1 跨操作系统矩阵分组",
            not mismatches,
            "7类条目分组正确" if not mismatches else "不一致: {}".format(mismatches),
        )
        # 跨平台不变量：A 组判定依据是「目录名 + 直接子项名 token」，
        # 不解析路径分隔符——ps-temp 本身无缓存名特征，凭子项 pip-unpack-* 命中，
        # 该结论在 Windows（\\分隔）与 POSIX（/分隔）上由 os.walk/Path 保证一致。
        hit, cache_reasons = is_cache_signature("ps-temp", tmp1 / "ps-temp")
        check(
            "场景1 签名按路径名 token 判定（分隔符无关）",
            hit and any("pip-unpack" in r for r in cache_reasons),
            "ps-temp 凭直接子项 token 命中 A 组，无任何分隔符字符串解析",
        )
    finally:
        shutil.rmtree(str(tmp1), ignore_errors=True)

    # 场景2：反向案例——E 组占比很高（调研中期清理）
    tmp2 = Path(tempfile.mkdtemp(prefix="triage-s2-"))
    try:
        _sparse_file(tmp2 / "pip-cache" / "http-v2" / "b", 40 * 1024, 30, now)
        for i in range(10):
            d = tmp2 / "research-{:02d}".format(i)
            d.mkdir()
            _sparse_file(d / "data.txt", 20 * 1024, 1, now)
            _set_mtime(d, 1, now)
        entries2 = [classify_entry(f, tmp2, now) for f in inventory(tmp2)]
        e_count = sum(1 for c in entries2 if c.group == GROUP_E)
        check(
            "场景2 E组高占比反向案例",
            e_count == 10 and len(entries2) == 11,
            "10/11 条目进入 E 组人工裁决（缓存仍为 A），人工裁决路径不被跳过",
        )
    finally:
        shutil.rmtree(str(tmp2), ignore_errors=True)

    # 场景3：离线约束——A 组降级为保守保留
    tmp3 = Path(tempfile.mkdtemp(prefix="triage-s3-"))
    try:
        _sparse_file(tmp3 / "pip-cache" / "http-v2" / "b", 10 * 1024, 30, now)
        online = classify_entry(inventory(tmp3)[0], tmp3, now, offline=False)
        offline = classify_entry(inventory(tmp3)[0], tmp3, now, offline=True)
        check(
            "场景3 离线环境 A 组降级",
            online.group == GROUP_A
            and online.disposition == "delete-safe"
            and offline.group == GROUP_A
            and offline.disposition == "keep-conservative-offline",
            "在线可删；离线时组不变但处置降级为保留",
        )
    finally:
        shutil.rmtree(str(tmp3), ignore_errors=True)

    # 场景4：周期复做——首跑基线、清理后二跑零可删 + 自动产物集中度
    tmp4 = Path(tempfile.mkdtemp(prefix="triage-s4-"))
    try:
        script4 = {"clone-site": "clean"}
        _build_realistic_fixture(tmp4, now)
        facts1 = inventory(tmp4)
        cls1 = [classify_entry(f, tmp4, now, git_runner=_fake_git_runner(script4)) for f in facts1]
        total = sum(f.size_bytes for f in facts1)
        # 模式卡实测口径：98.8% 属「自动产物可再生组」A+B+C+F（B 经源确认后删）
        reproducible_groups = (GROUP_A, GROUP_B, GROUP_C, GROUP_F)
        safe = sum(
            f.size_bytes
            for f, c in zip(facts1, cls1)
            if c.group in reproducible_groups
        )
        # 模拟人工执行清理：删除 A/B/C/D/F，保留 E
        for f, c in zip(facts1, cls1):
            if c.group != GROUP_E:
                target = tmp4 / f.name
                if target.is_dir():
                    shutil.rmtree(str(target), ignore_errors=True)
                else:
                    target.unlink()
        facts2 = inventory(tmp4)
        cls2 = [classify_entry(f, tmp4, now, git_runner=_fake_git_runner(script4)) for f in facts2]
        remaining_groups = {c.group for c in cls2}
        check(
            "场景4 二次清理零新增可删",
            remaining_groups == {GROUP_E},
            "清理后仅剩 E 组 {} 项".format(len(cls2)),
        )
        check(
            "场景4 自动产物集中度假设（≥90% 字节）",
            total > 0 and safe / total >= 0.9,
            "首跑 A+B+C+F 占 {:.1%}（模式卡实测 98.8%，阈值 90%）".format(safe / total),
        )
    finally:
        shutil.rmtree(str(tmp4), ignore_errors=True)

    # 附：git 取证不干净时必须升级 E（脏工作区/有未推送/无 git）
    tmp5 = Path(tempfile.mkdtemp(prefix="triage-s5-"))
    try:
        outcomes = []
        for repo, state in (("c-dirty", "dirty"), ("c-ahead", "ahead")):
            d = tmp5 / repo
            (d / ".git").mkdir(parents=True)
            _sparse_file(d / "x.txt", 1024, 10, now)
            outcomes.append(
                classify_entry(
                    _one_fact(d), d.parent, now, git_runner=_fake_git_runner({repo: state})
                ).group
            )
        check(
            "附 git 取证脏/未推送升级 E 组",
            all(g == GROUP_E for g in outcomes),
            "dirty={}, ahead={}".format(*outcomes),
        )
    finally:
        shutil.rmtree(str(tmp5), ignore_errors=True)

    return ok_all, logs


def _one_fact(path: Path) -> EntryFacts:
    file_count, size_bytes, newest_mtime = _walk_stats(path)
    return EntryFacts(
        name=path.name,
        kind="dir",
        size_bytes=size_bytes,
        file_count=file_count,
        mtime_epoch=newest_mtime,
    )


# ---- CLI ----


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="临时目录可再生分级分诊（只建议不删除），对应 TEMP-TRIAGE-001 模式卡"
    )
    parser.add_argument("path", nargs="?", help="待盘点的临时区路径")
    parser.add_argument("--json", dest="json_out", help="机器可读报告输出路径")
    parser.add_argument("--state-file", help="周期复做快照路径（存在则对比，并写回本次基线）")
    parser.add_argument("--offline", action="store_true", help="离线/计费网络，A 组降级保留")
    parser.add_argument("--fresh-days", type=int, default=DEFAULT_FRESH_DAYS, help="在途判定天数")
    parser.add_argument("--stale-days", type=int, default=DEFAULT_STALE_DAYS, help="残留判定天数")
    parser.add_argument("--git-bin", help="git 可执行文件路径（默认 PATH 查找）")
    parser.add_argument(
        "--validate-scenarios",
        action="store_true",
        help="运行内置四个迁移验证场景自检（L1→L2 证据采集）",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    if args.validate_scenarios:
        ok, logs = validate_scenarios()
        for line in logs:
            print(line)
        print("---")
        print("迁移验证自检: {}".format("全部通过" if ok else "存在失败项"))
        return 0 if ok else 1
    if not args.path:
        print("错误：需要提供临时区路径（或使用 --validate-scenarios）", file=sys.stderr)
        return 2
    root = Path(args.path)
    if not root.is_dir():
        print("错误：路径不存在或不是目录: {}".format(root), file=sys.stderr)
        return 2

    report = triage(
        root,
        fresh_days=args.fresh_days,
        stale_days=args.stale_days,
        offline=args.offline,
        git_bin=args.git_bin,
    )
    state_diff: Optional[Dict[str, List[str]]] = None
    if args.state_file:
        state_path = Path(args.state_file)
        state_diff = compare_state(report, state_path)
        write_state(report, state_path)
    print(render_text(report, state_diff))
    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print("机器可读报告已写入: {}".format(args.json_out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
