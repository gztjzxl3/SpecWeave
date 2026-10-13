# 版本校验：相对导入共享库（depth=1）
from ..python310_version_check import enforce_python310

enforce_python310()

# docs-as-product 常量定义：
# 集中维护 Diátaxis 四型映射、质量门定义、元数据稳定字段白名单与默认路径，
# 支持通过配置覆盖（见 config 加载逻辑）。

# ── Diátaxis 四型 ───────────────────────────────────────────

DIATAXIS_TYPES = ("tutorial", "how-to", "reference", "explanation")

# 目录名（小写归一后）→ 四型；含英文别名与中文目录名
DIATAXIS_DIR_ALIASES: dict[str, str] = {
    "tutorial": "tutorial",
    "tutorials": "tutorial",
    "教程": "tutorial",
    "入门": "tutorial",
    "how-to": "how-to",
    "howto": "how-to",
    "how_tos": "how-to",
    "howtos": "how-to",
    "guide": "how-to",
    "guides": "how-to",
    "操作指南": "how-to",
    "指南": "how-to",
    "reference": "reference",
    "references": "reference",
    "api": "reference",
    "参考": "reference",
    "参考手册": "reference",
    "explanation": "explanation",
    "explanations": "explanation",
    "concept": "explanation",
    "concepts": "explanation",
    "background": "explanation",
    "解释": "explanation",
    "概念": "explanation",
    "背景": "explanation",
}

# frontmatter 中显式声明四型的字段名
DIATAXIS_TYPE_FIELDS = ("diataxis", "doc_type", "doctype", "content_type")

# 未被任何规则识别的类型
TYPE_UNCLASSIFIED = "unclassified"

# ── 质量门 G1–G4 + V 门 ─────────────────────────────────────

# kind: builtin = 纯 Python 内置检查；external = 依赖外部工具
GATE_DEFINITIONS: tuple[dict[str, str], ...] = (
    {
        "id": "G1",
        "name": "事实与文风",
        "kind": "external",
        "tool": "vale",
        "command": "vale --output=line {path}",
        "hint": "安装：https://vale.sh ；配置 .vale.ini",
    },
    {
        "id": "G2",
        "name": "结构（首段与标题层级）",
        "kind": "builtin",
        "tool": "",
        "command": "",
        "hint": "",
    },
    {
        "id": "G3",
        "name": "组件复用",
        "kind": "builtin",
        "tool": "",
        "command": "",
        "hint": "",
    },
    {
        "id": "G4",
        "name": "原子性（一文件一单元）",
        "kind": "builtin",
        "tool": "",
        "command": "",
        "hint": "",
    },
    {
        "id": "V",
        "name": "V 门（警告即失败 + doctest + lint）",
        "kind": "external",
        "tool": "sphinx-build",
        "command": "sphinx-build -W --keep-going -b doctest docs docs/_build/doctest",
        "hint": "安装：pip install sphinx sphinx-lint ；需要 docs/conf.py",
    },
)

EXTERNAL_TOOLS: dict[str, str] = {
    "vale": "vale --version",
    "sphinx-build": "sphinx-build --version",
    "sphinx-lint": "sphinx-lint --version",
}

# V 门的三个外部检查命令
VGATE_COMMANDS: tuple[dict[str, str], ...] = (
    {
        "id": "sphinx-build",
        "command": "sphinx-build -W --keep-going -b html {docs} {out}/html",
        "tool": "sphinx-build",
    },
    {
        "id": "doctest",
        "command": "sphinx-build -b doctest {docs} {out}/doctest",
        "tool": "sphinx-build",
    },
    {
        "id": "sphinx-lint",
        "command": "sphinx-lint {docs}",
        "tool": "sphinx-lint",
    },
)

# ── 元数据稳定字段（F-021） ─────────────────────────────────

# 跨版本稳定、允许出现在页面 head/frontmatter 中的字段白名单
STABLE_METADATA_FIELDS: frozenset[str] = frozenset({
    "title",
    "slug",
    "url",
    "domain",
    "canonical",
    "id",
    "source",
    "maturity",
    "abstract_level",
    "related_patterns",
    "tags",
    "x-toml-ref",
})

# 漂移字段特征：命中即判为 F-021（环境/构建期信息，不应写入页面）
DRIFT_FIELD_HINTS: frozenset[str] = frozenset({
    "version",
    "published-at",
    "published_at",
    "deployment-id",
    "deployment_id",
    "build-id",
    "build_id",
    "release-id",
    "release_id",
    "qw-pages:version",
})

# HTML <meta name="..."> 中典型的漂移名
DRIFT_META_NAMES: frozenset[str] = frozenset({
    "qw-pages:version",
    "deployment-id",
    "published-at",
    "build-id",
    "release-id",
})

# ── 读者契约 ────────────────────────────────────────────────

# 四类读者
READER_TYPES = ("tutorial", "how-to", "reference", "explanation")

# 读者契约默认文件候选（相对 docs 根）
CONTRACT_FILE_CANDIDATES = (
    "reader-contract.md",
    "contract.md",
    "about/reader-contract.md",
)

# Tutorial 时长上限（分钟）
TUTORIAL_MAX_MINUTES = 15

# Reference docstring 覆盖率下限
REFERENCE_DOCSTRING_MIN = 90

# ── 指标 M1–M5 ──────────────────────────────────────────────

METRICS_DEFINITIONS: tuple[dict[str, str], ...] = (
    {
        "id": "M1",
        "name": "任务完成率",
        "definition": "读者按文档完成目标任务的成功比例",
        "collect": "验收任务回访问卷 / 完成埋点",
        "unit": "%",
    },
    {
        "id": "M2",
        "name": "首次响应时间",
        "definition": "读者从进入页面到找到可执行答案的时间",
        "collect": "copybutton / 停留与滚动埋点",
        "unit": "s",
    },
    {
        "id": "M3",
        "name": "搜索命中率与零结果率",
        "definition": "站内搜索有结果点击的比例；零结果查询报表",
        "collect": "搜索日志聚合",
        "unit": "%",
    },
    {
        "id": "M4",
        "name": "文档回滚率",
        "definition": "发布后因内容问题回滚或紧急修订的比例",
        "collect": "发布/回滚记录",
        "unit": "%",
    },
    {
        "id": "M5",
        "name": "AI 引用命中率",
        "definition": "/llms.txt 与文档内容被 AI 工具正确引用的比例",
        "collect": "AI 引用抽检 / llms.txt 可达性",
        "unit": "%",
    },
)

# ── 默认路径与扫描 ──────────────────────────────────────────

DEFAULT_DOCS_DIR = "docs"
DEFAULT_BUILD_DIR = "docs/_build"
DEFAULT_METRICS_DIR = "docs/metrics"

# 入口/索引文件名（不含扩展名），豁免 toctree 挂载检查
INDEX_FILE_STEMS = frozenset({"index", "README", "readme"})

# 扫描时排除的目录名
EXCLUDED_DIRS = frozenset({
    "_build",
    "_static",
    "_templates",
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
})

# 支持的文档扩展名
DOC_SUFFIXES = frozenset({".md", ".rst"})
