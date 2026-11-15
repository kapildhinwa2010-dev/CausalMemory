# CausalMemory

[![CI](https://github.com/kapildhinwa2010-dev/CausalMemory/actions/workflows/ci.yml/badge.svg)](https://github.com/kapildhinwa2010-dev/CausalMemory/actions/workflows/ci.yml)
[![CodeQL](https://github.com/kapildhinwa2010-dev/CausalMemory/actions/workflows/codeql.yml/badge.svg)](https://github.com/kapildhinwa2010-dev/CausalMemory/actions/workflows/codeql.yml)


Cause-effect chains over asserted "causes" edges, derived at query time.

**Part of the [Kapildhinwa2010-dev Toolkit](https://github.com/kapildhinwa2010-dev/Kapildhinwa2010-dev).**

## What it does

CausalMemory is the CAUSALITY layer of the fact-tool family.
add_cause() stores "causes" edges; effects_of()/causes_of() walk them
forwards or backwards (optionally transitively); causal_chain()
follows the first causal path. HONEST LIMITATION (also in the
docstring): "causes" edges are asserted facts, not discovered
causality - this module organizes what you store; it cannot validate
that causal claims are true.

## Install

```bash
pip install -r requirements.txt
```

## Quick start

```python
from causalmemory import KnowledgeNet

net = KnowledgeNet()
net.add_cause("rain", "wet_road")
net.add_cause("wet_road", "slow_traffic")
print(net.effects_of("rain", transitive=True))  # ["slow_traffic", "wet_road"]
```

## API

- add / query / facts / chain - shared triple store
- add_cause(cause, effect) - store a causes edge
- effects_of(cause, transitive) / causes_of(effect, transitive)
- causal_chain(start, max_hops) - first causal path, cycle-safe

## Honest results and limitations

- No causal discovery: edges are what you asserted, nothing is
  inferred or tested against data.
- causal_chain() follows only the FIRST causal edge per hop.
- No negation or contradiction handling - the source experiments
  showed negation is confidently wrong in this family.

## License

MIT - see [LICENSE](LICENSE).
