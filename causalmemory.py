# CausalMemory - Cause-effect chains derived at query time
# Part of the Kapildhinwa2010-dev Toolkit.

"""CausalMemory - cause-effect chains derived at query time.

Lineage: reserv.dean-part-2 (HELIX). On top of the shared triple store
this repo focuses on CAUSALITY: ``add_cause`` stores "causes" edges,
``effects_of``/``causes_of`` walk them forwards or backwards (optionally
transitively), and ``causal_chain`` follows the first causal path.

HONEST LIMITATION: "causes" edges are asserted facts, not discovered
causality - this module organizes and walks what you store; it cannot
validate that the causal claims are true.
"""

from __future__ import annotations

from collections import defaultdict

__all__ = ["Fact", "KnowledgeNet"]


class Fact:
    """A single (subject, predicate, object) triple."""

    __slots__ = ("subject", "predicate", "object")

    def __init__(self, subject: str, predicate: str, obj: str) -> None:
        for value in (subject, predicate, obj):
            if not isinstance(value, str) or not value:
                raise ValueError("subject, predicate and object must be non-empty strings")
        self.subject = subject
        self.predicate = predicate
        self.object = obj

    def as_tuple(self):
        return (self.subject, self.predicate, self.object)

    def __eq__(self, other) -> bool:
        return isinstance(other, Fact) and self.as_tuple() == other.as_tuple()

    def __hash__(self) -> int:
        return hash(self.as_tuple())

    def __repr__(self) -> str:
        return "Fact({!r}, {!r}, {!r})".format(*self.as_tuple())


class KnowledgeNet:
    """Fact store with indexed direct and reverse queries."""

    def __init__(self) -> None:
        self._facts: set = set()
        self._by_subject: dict = defaultdict(list)
        self._by_object: dict = defaultdict(list)

    def add(self, subject: str, predicate: str, obj: str) -> bool:
        """Add a fact; returns False if it already exists."""
        fact = Fact(subject, predicate, obj)
        if fact in self._facts:
            return False
        self._facts.add(fact)
        self._by_subject[fact.subject].append(fact)
        self._by_object[fact.object].append(fact)
        return True

    def facts(self):
        return sorted(self._facts, key=lambda f: f.as_tuple())

    def __len__(self) -> int:
        return len(self._facts)

    def query(self, subject=None, predicate=None, obj=None):
        """Return facts matching the given pattern (None = wildcard)."""
        results = self._facts
        if subject is not None:
            results = [f for f in results if f.subject == subject]
        if predicate is not None:
            results = [f for f in results if f.predicate == predicate]
        if obj is not None:
            results = [f for f in results if f.object == obj]
        return sorted(results, key=lambda f: f.as_tuple())

    def derive_aliases(self) -> dict:
        """Transitive closure of ``same_as`` equality facts."""
        adjacency: dict = defaultdict(set)
        for fact in self._facts:
            if fact.predicate == "same_as":
                adjacency[fact.subject].add(fact.object)
                adjacency[fact.object].add(fact.subject)
        aliases: dict = {}
        for node in list(adjacency):
            if node in aliases:
                continue
            component = set()
            stack = [node]
            while stack:
                current = stack.pop()
                if current in component:
                    continue
                component.add(current)
                stack.extend(adjacency[current] - component)
            canonical = min(component)
            for member in component:
                aliases[member] = canonical
        return aliases

    def chain(self, start: str, predicate: str, max_hops: int = 4) -> list:
        """Multi-hop walk following ``predicate`` from ``start``."""
        if max_hops < 1:
            raise ValueError("max_hops must be >= 1")
        hops = []
        current = start
        seen = {start}
        for _ in range(max_hops):
            nxt = [f.object for f in self._by_subject.get(current, []) if f.predicate == predicate]
            if not nxt:
                break
            # Stop BEFORE revisiting a node (cycle): do not append the repeated node.
            if nxt[0] in seen:
                break
            hops.append(nxt[0])
            seen.add(nxt[0])
            current = nxt[0]
        return hops

    def add_cause(self, cause: str, effect: str) -> bool:
        """Store a ``cause`` --causes--> ``effect`` edge."""
        return self.add(cause, "causes", effect)

    def _forward_reach(self, start: str, max_hops: int = 16) -> list:
        seen: set = set()
        frontier = [start]
        for _ in range(max_hops):
            nxt = []
            for node in frontier:
                for f in self._by_subject.get(node, []):
                    if f.predicate == "causes" and f.object not in seen:
                        seen.add(f.object)
                        nxt.append(f.object)
            if not nxt:
                break
            frontier = nxt
        return sorted(seen)

    def _backward_reach(self, start: str, max_hops: int = 16) -> list:
        seen: set = set()
        frontier = [start]
        for _ in range(max_hops):
            nxt = []
            for node in frontier:
                for f in self._by_object.get(node, []):
                    if f.predicate == "causes" and f.subject not in seen:
                        seen.add(f.subject)
                        nxt.append(f.subject)
            if not nxt:
                break
            frontier = nxt
        return sorted(seen)

    def effects_of(self, cause: str, transitive: bool = False) -> list:
        """Direct (or transitive) effects of ``cause``."""
        if transitive:
            return self._forward_reach(cause)
        return sorted({f.object for f in self._by_subject.get(cause, []) if f.predicate == "causes"})

    def causes_of(self, effect: str, transitive: bool = False) -> list:
        """Direct (or transitive) causes of ``effect``."""
        if transitive:
            return self._backward_reach(effect)
        return sorted({f.subject for f in self._by_object.get(effect, []) if f.predicate == "causes"})

    def causal_chain(self, start: str, max_hops: int = 8) -> list:
        """First causal path from ``start`` (cycle-safe)."""
        return self.chain(start, "causes", max_hops=max_hops)
