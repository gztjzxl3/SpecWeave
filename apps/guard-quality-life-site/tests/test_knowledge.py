"""知识树数据层测试：域数量、寻址、搜索。"""

from gqlsite.knowledge import (
    all_domains,
    domain_count,
    get_domain,
    get_entry,
    search,
)


def test_domain_count_at_least_10():
    assert domain_count() >= 10
    assert len(all_domains()) >= 10


def test_all_domains_expected_ids_present():
    ids = {d.id for d in all_domains()}
    for expected in (
        "home",
        "health",
        "diet",
        "sleep",
        "efficiency",
        "finance",
        "relation",
        "mind",
        "travel",
        "digital",
        "safety",
    ):
        assert expected in ids, f"缺少域 {expected}"


def test_get_domain_returns_domain():
    d = get_domain("health")
    assert d is not None
    assert d.name == "健康"
    assert d.summary
    assert d.entries


def test_get_domain_missing_returns_none():
    assert get_domain("nope") is None


def test_get_entry_returns_domain_and_entry():
    found = get_entry("sleep", "sleep-fixed-wakeup")
    assert found is not None
    domain, entry = found
    assert domain.id == "sleep"
    assert entry.title
    assert entry.purpose
    assert entry.steps
    assert entry.cost_benefit
    assert entry.evidence_level in ("A", "B", "C")
    assert entry.evidence_source
    assert entry.caveat


def test_get_entry_missing_returns_none():
    assert get_entry("home", "nope") is None
    assert get_entry("nope", "nope") is None


def test_search_match_by_title():
    hits = search("餐盘")
    assert any(e.title == "餐盘法：半蔬一蛋白一主食" for _, e in hits)


def test_search_match_by_purpose_case_insensitive():
    # ASCII 词大小写不敏感
    hits = search("INBOX")
    assert hits and hits[0][1].id == "efficiency-inbox-zero"


def test_search_empty_and_nomatch():
    assert search("") == []
    assert search("   ") == []
    assert search("绝对不存在的词xyzq") == []