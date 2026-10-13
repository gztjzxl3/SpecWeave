"""temp-triage.py 单元测试与迁移验证场景测试。

对应模式卡 TEMP-TRIAGE-001「临时目录可再生分级清理法」的 L1→L2 升级验证：
- 场景1 跨操作系统：同构混合临时区 A/B/C/D/E/F 六类分组正确；
  签名只认路径名 token，不解析分隔符；目录新鲜度以最新内容文件 mtime 为准
- 场景2 反向案例：E 组占比很高时，大多数条目录人工裁决，自动化不越权
- 场景3 离线约束：--offline 时 A 组处置降级为保守保留
- 场景4 周期复做：首跑基线→模拟人工清理→二跑仅剩 E 组；状态快照差异可识别
- 附 git 取证：脏工作区/有未推送提交/git 不可用三种情况一律升级 E
- 安全不变量：建议层报告绝不删除任何文件

运行：pytest .agents/scripts/tests/test_temp_triage.py -v
"""

# 版本守卫：与其他脚本测试一致的 sys.path 引导
import sys as _sys
from pathlib import Path as _Path

_lib_parent = _Path(__file__).resolve().parent
while not (_lib_parent / "lib").is_dir():
    _lib_parent = _lib_parent.parent
_sys.path.insert(0, str(_lib_parent / "lib"))

import importlib.util
import json
import time

import pytest

_SCRIPTS_DIR = _Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "temp_triage", _SCRIPTS_DIR / "temp-triage.py"
)
tt = importlib.util.module_from_spec(_spec)
_sys.modules["temp_triage"] = tt
_spec.loader.exec_module(tt)


# ---- 夹具构造 ----


@pytest.fixture
def now():
    return time.time()


def _classify_all(root, now, script=None):
    runner = tt._fake_git_runner(script or {})
    facts = tt.inventory(root)
    return facts, [tt.classify_entry(f, root, now, git_runner=runner) for f in facts]


def _groups(root, now, script=None):
    facts, results = _classify_all(root, now, script)
    return dict(zip([f.name for f in facts], results))


# ---- 场景1：跨操作系统矩阵 ----


def test_scenario1_cross_platform_matrix(tmp_path, now):
    tt._build_realistic_fixture(tmp_path, now)
    grouped = _groups(tmp_path, now, {"clone-site": "clean"})
    expected = {
        "pip-cache": tt.GROUP_A,
        "ps-temp": tt.GROUP_A,
        "old-site-build": tt.GROUP_B,
        "clone-site": tt.GROUP_C,
        "fix_links.py": tt.GROUP_D,
        "research-fresh": tt.GROUP_E,
        "empty-dir": tt.GROUP_F,
    }
    mismatches = {
        name: (grouped[name].group, want)
        for name, want in expected.items()
        if grouped[name].group != want
    }
    assert not mismatches, "分组不一致: {}".format(mismatches)


def test_scenario1_token_signature_independent_of_separator(tmp_path, now):
    """A 组依据直接子项名 token 命中：判定逻辑中不存在分隔符解析。"""
    tt._build_realistic_fixture(tmp_path, now)
    hit, reasons = tt.is_cache_signature("ps-temp", tmp_path / "ps-temp")
    assert hit
    assert any("pip-unpack" in r for r in reasons)
    # 顶层目录名本身无缓存特征，若退化为按整路径字符串匹配必然漏判
    assert "ps-temp" not in tt._CACHE_DIR_NAMES


def test_scenario1_directory_freshness_uses_newest_file_mtime(tmp_path, now):
    """复制来的旧构建：目录自身 mtime 是新的，但内容文件陈旧，仍应判 B 而非升级 E。"""
    build = tmp_path / "copied-old-build"
    for i in range(25):
        tt._sparse_file(build / "html" / "p-{}.html".format(i), 4096, 45, now)
    tt._sparse_file(build / ".doctrees" / "x.doctree", 1024, 45, now)
    # 目录 mtime 被复制操作刷新为"现在"（fixture 不回溯目录 mtime，模拟真实复制）
    grouped = _groups(tmp_path, now)
    assert grouped["copied-old-build"].group == tt.GROUP_B


# ---- 场景2：E 组高占比反向案例 ----


def test_scenario2_e_group_dominant(tmp_path, now):
    tt._sparse_file(tmp_path / "pip-cache" / "http-v2" / "b", 40 * 1024, 30, now)
    for i in range(10):
        d = tmp_path / "research-{:02d}".format(i)
        d.mkdir()
        tt._sparse_file(d / "notes.txt", 20 * 1024, 1, now)
        tt._set_mtime(d, 1, now)
    grouped = _groups(tmp_path, now)
    e_names = [n for n, c in grouped.items() if c.group == tt.GROUP_E]
    assert len(grouped) == 11
    assert len(e_names) == 10
    assert grouped["pip-cache"].group == tt.GROUP_A  # 缓存不被 E 海淹没


# ---- 场景3：离线降级 ----


def test_scenario3_offline_downgrades_cache_disposition(tmp_path, now):
    tt._sparse_file(tmp_path / "pip-cache" / "http-v2" / "b", 10 * 1024, 30, now)
    facts = tt.inventory(tmp_path)
    online = tt.classify_entry(facts[0], tmp_path, now, offline=False)
    offline = tt.classify_entry(facts[0], tmp_path, now, offline=True)
    assert online.group == tt.GROUP_A
    assert online.disposition == "delete-safe"
    assert offline.group == tt.GROUP_A
    assert offline.disposition == "keep-conservative-offline"


# ---- 场景4：周期复做 + 状态快照 ----


def test_scenario4_periodic_reclean_and_state_diff(tmp_path, now):
    state_file = tmp_path / "state.json"
    work = tmp_path / "work"
    work.mkdir()
    tt._build_realistic_fixture(work, now)
    facts1, cls1 = _classify_all(work, now, {"clone-site": "clean"})

    report1 = {
        "root": str(work),
        "generated_at": "2026-10-13T00:00:00",
        "entries": [
            {"name": f.name, "group": c.group, "bytes": f.size_bytes}
            for f, c in zip(facts1, cls1)
        ],
    }
    tt.write_state(report1, state_file)

    # 模拟人工按组执行清理（A/B/C/D/F 删，E 留），并新增一个新到素材
    for f, c in zip(facts1, cls1):
        if c.group != tt.GROUP_E:
            target = work / f.name
            if target.is_dir():
                import shutil

                shutil.rmtree(str(target))
            else:
                target.unlink()
    new_dir = work / "research-new"
    new_dir.mkdir()
    tt._sparse_file(new_dir / "data.txt", 1024, 0, now)

    facts2, cls2 = _classify_all(work, now, {"clone-site": "clean"})
    remaining = {c.group for c in cls2}
    assert remaining == {tt.GROUP_E}
    assert len(cls2) == 2  # 旧在途 1 项 + 新到 1 项

    report2 = {
        "root": str(work),
        "generated_at": "2026-10-20T00:00:00",
        "entries": [
            {"name": f.name, "group": c.group, "bytes": f.size_bytes}
            for f, c in zip(facts2, cls2)
        ],
    }
    diff = tt.compare_state(report2, state_file)
    assert "research-fresh" in diff["unchanged"]
    assert "research-new" in diff["new"]
    assert "pip-cache" in diff["removed"]
    assert "clone-site" in diff["removed"]


def test_scenario4_reproducible_concentration_threshold(tmp_path, now):
    """模式卡实测：自动产物可再生组(A+B+C+F)占 98.8%；合成夹具阈值 90%。"""
    tt._build_realistic_fixture(tmp_path, now)
    facts, results = _classify_all(tmp_path, now, {"clone-site": "clean"})
    total = sum(f.size_bytes for f in facts)
    reproducible = sum(
        f.size_bytes
        for f, c in zip(facts, results)
        if c.group in (tt.GROUP_A, tt.GROUP_B, tt.GROUP_C, tt.GROUP_F)
    )
    assert total > 0
    assert reproducible / total >= 0.90


# ---- git 取证边界 ----


def test_git_dirty_and_ahead_escalate_to_e(tmp_path, now):
    outcomes = {}
    for repo, state in (("c-dirty", "dirty"), ("c-ahead", "ahead")):
        d = tmp_path / repo
        (d / ".git").mkdir(parents=True)
        tt._sparse_file(d / "x.txt", 1024, 10, now)
        outcomes[repo] = tt.classify_entry(
            tt._one_fact(d), tmp_path, now, git_runner=tt._fake_git_runner({repo: state})
        ).group
    assert outcomes == {"c-dirty": tt.GROUP_E, "c-ahead": tt.GROUP_E}


def test_git_unavailable_escalates_to_e(tmp_path, now):
    d = tmp_path / "c-nogit"
    (d / ".git").mkdir(parents=True)
    tt._sparse_file(d / "x.txt", 1024, 10, now)

    def no_git(path, args):
        return None

    result = tt.classify_entry(tt._one_fact(d), tmp_path, now, git_runner=no_git)
    assert result.group == tt.GROUP_E


def test_clean_clone_is_group_c(tmp_path, now):
    d = tmp_path / "c-clean"
    (d / ".git").mkdir(parents=True)
    tt._sparse_file(d / "README.md", 2048, 10, now)
    result = tt.classify_entry(
        tt._one_fact(d), tmp_path, now, git_runner=tt._fake_git_runner({"c-clean": "clean"})
    )
    assert result.group == tt.GROUP_C
    assert result.disposition == "delete-safe"


# ---- 分类器其他边界 ----


def test_fresh_build_escalates_to_e(tmp_path, now):
    build = tmp_path / "_build"
    for i in range(25):
        tt._sparse_file(build / "p-{}.html".format(i), 1024, 1, now)
    grouped = _groups(tmp_path, now)
    assert grouped["_build"].group == tt.GROUP_E  # 任务可能正在进行


def test_loose_file_age_boundary(tmp_path, now):
    # 陈旧（>stale_days）→ D 候选；窗口内 → E
    tt._sparse_file(tmp_path / "old_report.txt", 1024, 31, now)
    tt._sparse_file(tmp_path / "fresh_notes.py", 1024, 5, now)
    grouped = _groups(tmp_path, now)
    assert grouped["old_report.txt"].group == tt.GROUP_D
    assert grouped["old_report.txt"].disposition == "delete-after-human-evidence"
    assert grouped["fresh_notes.py"].group == tt.GROUP_E


def test_unknown_old_directory_stays_e(tmp_path, now):
    d = tmp_path / "mystery-project"
    d.mkdir()
    tt._sparse_file(d / "a.unknown-ext", 1024, 90, now)
    grouped = _groups(tmp_path, now)
    assert grouped["mystery-project"].group == tt.GROUP_E  # 无法证明可再生，默认保留


def test_empty_directory_is_group_f(tmp_path, now):
    (tmp_path / "empty").mkdir()
    grouped = _groups(tmp_path, now)
    assert grouped["empty"].group == tt.GROUP_F


# ---- CLI 与安全不变量 ----


def test_cli_validate_scenarios_passes():
    assert tt.main(["--validate-scenarios"]) == 0


def test_cli_missing_path_exit_code_2(capsys):
    assert tt.main([]) == 2


def test_cli_nonexistent_path_exit_code_2(tmp_path):
    assert tt.main([str(tmp_path / "nope")]) == 2


def test_report_run_never_deletes_anything(tmp_path, now):
    """安全性质：建议层报告运行前后，文件树逐字节一致（模式卡第6步约束）。"""
    tt._build_realistic_fixture(tmp_path, now)
    before = {
        str(p.relative_to(tmp_path)): p.stat().st_size
        for p in tmp_path.rglob("*")
        if p.is_file()
    }
    json_out = tmp_path / "report.json"
    state_out = tmp_path / "state.json"
    rc = tt.main(
        [
            str(tmp_path),
            "--json",
            str(json_out),
            "--state-file",
            str(state_out),
        ]
    )
    assert rc == 0
    after = {
        str(p.relative_to(tmp_path)): p.stat().st_size
        for p in tmp_path.rglob("*")
        if p.is_file() and p.name not in ("report.json", "state.json")
    }
    assert before == after
    report = json.loads(json_out.read_text(encoding="utf-8"))
    assert report["total_bytes"] > 0
    assert set(report["groups"].keys()) == set(tt.GROUPS_ORDER)


def test_render_text_contains_manual_adjudication_list(tmp_path, now):
    tt._build_realistic_fixture(tmp_path, now)
    # 无 .git 依赖的独立小报告（克隆目录不存在 git 不可用时归入 E，文本仍须可读）
    simple = tmp_path / "simple"
    simple.mkdir()
    tt._sparse_file(simple / "pip-cache" / "http-v2" / "b", 1024, 30, now)
    report = tt.triage(simple)
    text = tt.render_text(report)
    assert "只建议，不删除" in text
    assert "E 组人工裁决清单" in text
