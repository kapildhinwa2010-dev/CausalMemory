# CausalMemory

[![CI](https://github.com/kapildhinwa2010-dev/CausalMemory/actions/workflows/ci.yml/badge.svg)](https://github.com/kapildhinwa2010-dev/CausalMemory/actions/workflows/ci.yml) [![CodeQL](https://github.com/kapildhinwa2010-dev/CausalMemory/actions/workflows/codeql.yml/badge.svg)](https://github.com/kapildhinwa2010-dev/CausalMemory/actions/workflows/codeql.yml)

CausalMemory is a small Python library for keeping string-valued facts in an in-memory triple store and traversing explicitly recorded `causes` relationships. It is an early-stage utility (version 0.1.0), not a causal-inference system: the library stores and queries claims supplied by the caller and does not discover or validate causality.

## Features

- `Fact` represents a non-empty `(subject, predicate, object)` string triple.
- `KnowledgeNet` stores unique facts, supports pattern queries with optional subject, predicate, or object filters, and returns facts in sorted order.
- `add_cause(cause, effect)` records a directed `causes` fact. `effects_of()` and `causes_of()` return direct neighbors or, when `transitive=True`, traverse reachable causes/effects.
- `causal_chain(start, max_hops=8)` follows one causal path and stops before revisiting a node. At each step it follows only the first matching outgoing edge in insertion order; it does not enumerate alternate paths.
- `chain(start, predicate, max_hops=4)` provides the same first-edge walk for another predicate. `derive_aliases()` computes connected components of `same_as` facts and maps each member to the lexicographically smallest name in its component.

## Requirements

Python 3.9 or later. The project metadata declares NumPy 1.24 or later as a runtime dependency. Pytest 7.4 or later is listed in `requirements.txt` for development and tests.

## Install

From the repository root:

```bash
python -m pip install .
```

For development and tests, install the listed requirements as well:

```bash
python -m pip install -r requirements.txt
```

## Example

```python
from causalmemory import KnowledgeNet

net = KnowledgeNet()
net.add_cause("rain", "wet_road")
net.add_cause("wet_road", "slow_traffic")

print(net.effects_of("rain"))  # ['wet_road']
print(net.effects_of("rain", transitive=True))  # ['slow_traffic', 'wet_road']
print(net.causes_of("slow_traffic", transitive=True))  # ['rain', 'wet_road']
print(net.causal_chain("rain"))  # ['wet_road', 'slow_traffic']
```

The store is in memory only; the repository does not implement persistence or a command-line interface.

## Tests and CI

On the current repository commit, `python -m pytest -q` passed all 8 tests, and `python -m compileall -q causalmemory.py tests` completed successfully. A local `python -m pip install --no-deps --target /tmp/readme95-repos/043-CausalMemory-install .` package-install check also succeeded. These are local checks, not a claim about a hosted CI run. The CI workflow is configured to run pytest, compile the module/tests, and perform an import smoke test on Python 3.10, 3.11, and 3.12; hosted workflow results were not checked for this README draft.

The repository contains no benchmark suite or benchmark measurements.

## Limitations

- `causes` edges are asserted by the caller; no causal discovery, statistical analysis, or truth-checking is implemented.
- The graph is an in-memory set of facts with no persistence, database backend, or CLI.
- Causal and generic chain walks choose one outgoing edge at each step, rather than exploring or ranking all possible paths. Transitive cause/effect searches use a fixed maximum of 16 hops in the current implementation.
- The API accepts non-empty strings and does not provide typed entities, confidence scores, temporal semantics, negation handling, or contradiction resolution.

## License

The repository's `LICENSE` file specifies the MIT License, with copyright notice `Copyright (c) 2026 Kapildhinwa2010-dev`. See [LICENSE](LICENSE) for the full terms.
