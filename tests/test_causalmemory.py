import pytest

from causalmemory import Fact, KnowledgeNet


def test_fact_basic():
    fact = Fact("rain", "causes", "wet")
    assert fact.as_tuple() == ("rain", "causes", "wet")


def test_add_and_len():
    net = KnowledgeNet()
    assert net.add_cause("rain", "wet") is True
    assert len(net) == 1


def test_query_pattern():
    net = KnowledgeNet()
    net.add_cause("rain", "wet")
    net.add("rain", "implies", "clouds")
    assert len(net.query(predicate="causes")) == 1


# --- causal queries (CausalMemory-specific) ---


def test_effects_of_direct():
    net = KnowledgeNet()
    net.add_cause("rain", "wet")
    net.add_cause("rain", "cold")
    assert net.effects_of("rain") == ["cold", "wet"]


def test_effects_of_transitive():
    net = KnowledgeNet()
    net.add_cause("a", "b")
    net.add_cause("b", "c")
    net.add_cause("c", "d")
    assert net.effects_of("a", transitive=True) == ["b", "c", "d"]
    assert net.effects_of("a") == ["b"]


def test_causes_of_direct_and_transitive():
    net = KnowledgeNet()
    net.add_cause("a", "b")
    net.add_cause("b", "c")
    assert net.causes_of("c") == ["b"]
    assert net.causes_of("c", transitive=True) == ["a", "b"]


def test_causal_chain_and_cycles():
    net = KnowledgeNet()
    net.add_cause("a", "b")
    net.add_cause("b", "c")
    assert net.causal_chain("a") == ["b", "c"]
    net.add_cause("c", "a")
    assert net.causal_chain("a") == ["b", "c"]


def test_unknown_node_empty():
    net = KnowledgeNet()
    net.add_cause("a", "b")
    assert net.effects_of("zzz") == []
    assert net.causes_of("zzz") == []