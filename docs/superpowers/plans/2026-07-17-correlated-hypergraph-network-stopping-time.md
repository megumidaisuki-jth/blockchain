# Correlated Hypergraph Network First-Depletion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建成一个可复核的相关超图支付通道网络停止时间研究最小闭环：正式化 T16–T18、实现独立的精确解与 Monte Carlo、验证相关性效应，并把结论同步进论文权威文档。

**Architecture:** 以冻结的路由字母表生成有界相关增量核，精确求解器在完整乘积单纯形内部状态上构造吸收链，Monte Carlo 使用另一套状态更新代码。理论层以有限状态吸收、三分区极限和独立代理边界为三个证明模块；证据层只在自动测试、数值交叉验证和文献审计都通过后同步主审计与标题判断。

**Tech Stack:** Python 3.10+、NumPy、SciPy sparse、标准库 `unittest`/`dataclasses`/`hashlib`/`json`/`csv`，Node.js + 现有 `render_research_html.mjs`，Markdown + BibTeX。

## Global Constraints

- 主停止事件固定为 `min_{(e,v)} X_{e,v}=0` 的首次时刻；不得写成首次支付失败、永久关闭或网络断连。
- 固定有限超图、固定有限简单路由字母表、单位支付、无费用；一条路由中每条超边至多出现一次。
- 同一节点在不同超边上的余额是不同坐标；每条超边分别守恒。
- 路由分布是外生 i.i.d.，不依赖余额、历史失败、拥塞或重路由。
- 精确求解器与 Monte Carlo 不得调用现有单超边生产模拟器，也不得共享状态转移实现。
- T16 必须显式验证有限状态耗尽可达性，不能从渐近协方差非退化倒推吸收。
- T17 的 `\alpha<1`、`\alpha=1`、`\alpha>1` 三段必须分别闭合尾界/FCLT/矩收敛证明；任一证明义务未闭合即降级为 conjecture 或 numerical observation。
- T18 正式拆成“零跨块协方差的充分条件”和“非零跨块的显式反例”；不得声称非零相关误差具有统一符号。
- 不修改冻结 v4 经验公式、拟合系数或历史验证数据。
- 不下载 Barnett 1964 正文或附件；该访问仍受先前未回答的“正文/附件”授权门约束。
- 当前目录没有 `.git`。每个任务结束先保存 QA 检查点；只有执行时位于 Git worktree 内才运行计划中的提交命令。
- 所有论文级数字必须可由冻结脚本重建，并同时保存种子、软件版本、配置和 SHA-256。

## File Map

### Create

- `network_model.py`：超图、路由、增量核、漂移与协方差的唯一模型实现。
- `network_exact.py`：完整内部状态枚举、耗尽可达性检查、稀疏 Poisson 方程和精确生存函数。
- `network_simulation.py`：与精确求解器独立的批量路径模拟和统计摘要。
- `network_topologies.py`：重叠链、重叠星、固定规模随机连通超图与最短超路径目录。
- `network_phase_validation.py`：漂移三分区、相关/独立代理配对比较及结果导出。
- `test_network_model.py`：模型、精确解、模拟、拓扑和证据元数据的自动测试入口。
- `outputs/researchwrite/hypergraph-stopping-time/13_correlated_network_proof_package.md`：T16–T18 的证明工作稿与失败降级规则。
- `outputs/researchwrite/hypergraph-stopping-time/14_correlated_network_external_review_packet.md`：外部概率论复核签核表。
- `outputs/researchwrite/hypergraph-stopping-time/sources/correlated_network_prior_art_audit_2026-07-17.md`：网络相关停止时间先行工作审计。
- `outputs/researchwrite/hypergraph-stopping-time/qa_logs/2026-07-17_correlated_network_model_qa.md`：本计划执行证据。
- `results/network/`：CSV/JSON 结果及哈希清单。

### Modify

- `outputs/researchwrite/hypergraph-stopping-time/12_correlated_hypergraph_network_model_and_theorem_contract.md`
- `outputs/researchwrite/hypergraph-stopping-time/sources/references.bib`
- `outputs/researchwrite/hypergraph-stopping-time/00_scope.md`
- `outputs/researchwrite/hypergraph-stopping-time/01_research_canon.md`
- `outputs/researchwrite/hypergraph-stopping-time/02_evidence_table.md`
- `outputs/researchwrite/hypergraph-stopping-time/03_argument_map.md`
- `outputs/researchwrite/hypergraph-stopping-time/04_section_contracts.md`
- `outputs/researchwrite/hypergraph-stopping-time/06_theorem_proof_gap_register.md`
- `outputs/researchwrite/hypergraph-stopping-time/exports/项目进展审计_超图支付通道停止时间_2026-07-17.md`
- `outputs/researchwrite/hypergraph-stopping-time/state.json`
- `README.md`
- `项目进展审计_超图支付通道停止时间_2026-07-17.html`

---

### Task 1: Freeze the approved contract and verified source metadata

**Files:**

- Modify: `outputs/researchwrite/hypergraph-stopping-time/12_correlated_hypergraph_network_model_and_theorem_contract.md`
- Modify: `outputs/researchwrite/hypergraph-stopping-time/sources/references.bib`
- Create: `outputs/researchwrite/hypergraph-stopping-time/sources/correlated_network_prior_art_audit_2026-07-17.md`

**Interfaces:**

- Consumes: 用户确认的路线 A 设计合同；Crossref、ACM、IEEE、SIAM、arXiv 官方元数据。
- Produces: 后续证明与主稿只能引用的五条网络级来源，以及 T18 的形式化边界。

- [ ] **Step 1: Write a failing metadata/control-character check**

在 `test_network_model.py` 写入：

```python
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent
PROJECT = ROOT / "outputs" / "researchwrite" / "hypergraph-stopping-time"


class AuthorityDocumentTests(unittest.TestCase):
    def test_contract_has_no_control_characters(self) -> None:
        text = (PROJECT / "12_correlated_hypergraph_network_model_and_theorem_contract.md").read_text(encoding="utf-8")
        bad = [ch for ch in text if ord(ch) < 32 and ch not in "\n\r\t"]
        self.assertEqual(bad, [])
        self.assertIn(r"\Gamma^{1/2}", text)
        self.assertEqual(text.count(r"\frac{\tau_N^{\mathrm{net}}}{N^2}"), 4)

    def test_required_network_references_are_unique(self) -> None:
        bib = (PROJECT / "sources" / "references.bib").read_text(encoding="utf-8")
        for doi in (
            "10.1109/TNSM.2024.3456229",
            "10.1145/3702248",
            "10.1137/15M1010737",
            "10.48550/arXiv.2512.11775",
            "10.48550/arXiv.2601.04835",
        ):
            self.assertEqual(bib.lower().count(doi.lower()), 1, doi)
```

- [ ] **Step 2: Run the check and confirm that bibliography coverage fails**

Run: `python -m unittest test_network_model.AuthorityDocumentTests -v`

Expected: control-character test passes after the already approved formatting correction; reference test fails because the five DOI entries are not yet all present exactly once.

- [ ] **Step 3: Add the verified BibTeX records**

Append exactly these records to `references.bib` after checking that the keys do not exist:

```bibtex
@article{PodiatchevOrdaRottenstreich2024Survivable,
  author  = {Podiatchev, Yekaterina and Orda, Ariel and Rottenstreich, Ori},
  title   = {Survivable Payment Channel Networks},
  journal = {IEEE Transactions on Network and Service Management},
  year    = {2024},
  volume  = {21},
  number  = {6},
  pages   = {6218--6232},
  doi     = {10.1109/TNSM.2024.3456229}
}

@article{CorcoranLewis2025PathPlanning,
  author  = {Corcoran, Padraig and Lewis, Rhyd},
  title   = {Path Planning in Payment Channel Networks with Multi-Party Channels},
  journal = {Distributed Ledger Technologies: Research and Practice},
  year    = {2025},
  volume  = {4},
  number  = {4},
  pages   = {1--14},
  doi     = {10.1145/3702248}
}

@misc{NainwalKambleAwathare2026COALESCE,
  author        = {Nainwal, Ayush and Kamble, Atharva and Awathare, Nitin},
  title         = {Hypergraph based Multi-Party Payment Channel},
  year          = {2026},
  eprint        = {2512.11775},
  archivePrefix = {arXiv},
  primaryClass  = {cs.DC},
  doi           = {10.48550/arXiv.2512.11775},
  note          = {Version 2, revised 2 June 2026}
}

@misc{Pickhardt2026MathematicalTheory,
  author        = {Pickhardt, Rene},
  title         = {A Mathematical Theory of Payment Channel Networks},
  year          = {2026},
  eprint        = {2601.04835},
  archivePrefix = {arXiv},
  primaryClass  = {cs.NI},
  doi           = {10.48550/arXiv.2601.04835}
}

@article{PatelCarronBullo2016Hitting,
  author  = {Patel, Rushabh and Carron, Andrea and Bullo, Francesco},
  title   = {The Hitting Time of Multiple Random Walks},
  journal = {SIAM Journal on Matrix Analysis and Applications},
  year    = {2016},
  volume  = {37},
  number  = {3},
  pages   = {933--954},
  doi     = {10.1137/15M1010737}
}
```

- [ ] **Step 4: Write the prior-art boundary as claims, evidence, and exclusions**

The audit must contain this conclusion verbatim:

```markdown
## 可辩护结论

本轮有界多源检索确认：独立 PCN 通道首次耗尽已有直接先行工作，超图 PCN、
超图支付路径和跨超边原子结算语义也已有直接先行工作。当前未检出同时满足
“固定超图 + 外生随机多超边路由 + 相关余额增量 + 首次耗尽 + 多项式漂移
三分区 + 全矩收敛”的直接论文；这只支持“在已检索范围内未发现直接同构
结果”，不支持“全球首次”。

T13 仅是 Podiatchev–Orda–Rottenstreich 独立通道网络分析的复现基线。
T16 的 Poisson 方程和 Patel–Carron–Bullo 的乘积链方法是标准工具。
候选贡献必须落在路由诱导跨超边相关性、乘积单纯形退出相图及其可复核误差
诊断的组合上。
```

为每篇来源记录：官方 URL、检索日期、模型对象、停止事件、依赖结构、可支持表述、不可支持表述。

- [ ] **Step 5: Narrow T18 to a proposition plus counterexample contract**

Replace any universal converse wording with:

```markdown
T18a（充分条件）：若极限 Brownian 运动按超边分块，且所有跨超边协方差块
为零，则高斯性蕴含各超边块独立，网络退出时间是各块退出时间的最小值，
其生存函数为边际生存函数乘积。

T18b（反例/诊断）：非零跨块协方差不自动给出统一误差符号。本文只对冻结
拓扑和需求族给出显式非因子化反例、相关强度、配对均值/分位数/生存曲线
差及不确定性。
```

- [ ] **Step 6: Re-run authority tests**

Run: `python -m unittest test_network_model.AuthorityDocumentTests -v`

Expected: 2 tests pass.

- [ ] **Step 7: Save a task checkpoint**

If inside a Git worktree:

```powershell
git add test_network_model.py outputs/researchwrite/hypergraph-stopping-time/12_correlated_hypergraph_network_model_and_theorem_contract.md outputs/researchwrite/hypergraph-stopping-time/sources/references.bib outputs/researchwrite/hypergraph-stopping-time/sources/correlated_network_prior_art_audit_2026-07-17.md
git commit -m "docs: freeze correlated network model contract"
```

Otherwise record the passing command and timestamp in the QA log created in Task 8.

---

### Task 2: Implement the route-correlated network kernel

**Files:**

- Create: `network_model.py`
- Modify: `test_network_model.py`

**Interfaces:**

- Consumes: `HypergraphSpec`, `Route`, route probabilities.
- Produces: `NetworkKernel(spec, routes, probabilities, coordinates, increments, drift, covariance)`; later tasks import only this public interface.

- [ ] **Step 1: Write failing conservation, validation, and covariance tests**

Add:

```python
import numpy as np

from network_model import (
    HypergraphSpec,
    Route,
    build_kernel,
    two_overlapping_triads_uniform,
    validate_phase_kernel,
)


class NetworkKernelTests(unittest.TestCase):
    def test_two_triad_kernel_matches_frozen_diagnostics(self) -> None:
        kernel = two_overlapping_triads_uniform()
        self.assertEqual(kernel.increments.shape, (20, 6))
        np.testing.assert_allclose(kernel.drift, 0.0, atol=1e-15)
        for edge_index in range(2):
            block = kernel.edge_slice(edge_index)
            np.testing.assert_array_equal(kernel.increments[:, block].sum(axis=1), 0)
        cross = kernel.covariance[kernel.edge_slice(0), kernel.edge_slice(1)]
        self.assertAlmostEqual(float(np.linalg.norm(cross, ord="fro")), 0.6, places=12)
        positive = np.linalg.eigvalsh(kernel.covariance)
        positive = positive[positive > 1e-12]
        np.testing.assert_allclose(positive, [0.3, 0.5, 0.5, 1.5], atol=1e-12)

    def test_reverse_route_cancels_increment(self) -> None:
        kernel = two_overlapping_triads_uniform()
        lookup = {(r.nodes, r.edges): x for r, x in zip(kernel.routes, kernel.increments)}
        for route, increment in zip(kernel.routes, kernel.increments):
            reverse = (tuple(reversed(route.nodes)), tuple(reversed(route.edges)))
            np.testing.assert_array_equal(lookup[reverse], -increment)

    def test_invalid_routes_are_rejected(self) -> None:
        spec = HypergraphSpec(edges=((0, 1, 2), (2, 3, 4)), capacity_units=(3, 3))
        with self.assertRaisesRegex(ValueError, "repeats a hyperedge"):
            build_kernel(spec, (Route((0, 1, 2), (0, 0)),), np.array([1.0]))
        with self.assertRaisesRegex(ValueError, "not contained"):
            build_kernel(spec, (Route((0, 4), (0,)),), np.array([1.0]))
        with self.assertRaisesRegex(ValueError, "sum to one"):
            build_kernel(spec, (Route((0, 1), (0,)),), np.array([0.9]))

    def test_phase_kernel_rejects_degenerate_faces(self) -> None:
        spec = HypergraphSpec(edges=((0, 1, 2),), capacity_units=(3,))
        kernel = build_kernel(
            spec,
            (Route((0, 1), (0,)), Route((1, 0), (0,))),
            np.array([0.5, 0.5]),
        )
        with self.assertRaisesRegex(ValueError, "normal variance"):
            validate_phase_kernel(kernel)

    def test_single_edge_routes_have_zero_cross_covariance(self) -> None:
        spec = HypergraphSpec(edges=((0, 1), (2, 3)), capacity_units=(2, 2))
        routes = (
            Route((0, 1), (0,)), Route((1, 0), (0,)),
            Route((2, 3), (1,)), Route((3, 2), (1,)),
        )
        kernel = build_kernel(spec, routes, np.full(4, 0.25))
        np.testing.assert_allclose(
            kernel.covariance[kernel.edge_slice(0), kernel.edge_slice(1)],
            0.0,
            atol=1e-15,
        )
```

- [ ] **Step 2: Run tests and confirm the module is absent**

Run: `python -m unittest test_network_model.NetworkKernelTests -v`

Expected: FAIL with `ModuleNotFoundError: No module named 'network_model'`.

- [ ] **Step 3: Implement the immutable model objects and increment construction**

`network_model.py` must expose these exact signatures:

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class HypergraphSpec:
    edges: tuple[tuple[int, ...], ...]
    capacity_units: tuple[int, ...]

    def __post_init__(self) -> None:
        if not self.edges or len(self.edges) != len(self.capacity_units):
            raise ValueError("edges and capacity_units must have the same nonzero length")
        if any(len(edge) < 2 or len(set(edge)) != len(edge) for edge in self.edges):
            raise ValueError("each hyperedge must contain at least two distinct nodes")
        if any((not isinstance(c, int)) or c <= 0 for c in self.capacity_units):
            raise ValueError("capacity units must be positive integers")

    @property
    def coordinates(self) -> tuple[tuple[int, int], ...]:
        return tuple((edge_index, node) for edge_index, edge in enumerate(self.edges) for node in edge)

    def edge_slice(self, edge_index: int) -> slice:
        start = sum(len(edge) for edge in self.edges[:edge_index])
        return slice(start, start + len(self.edges[edge_index]))


@dataclass(frozen=True)
class Route:
    nodes: tuple[int, ...]
    edges: tuple[int, ...]


@dataclass(frozen=True)
class NetworkKernel:
    spec: HypergraphSpec
    routes: tuple[Route, ...]
    probabilities: np.ndarray
    increments: np.ndarray
    drift: np.ndarray
    covariance: np.ndarray

    def edge_slice(self, edge_index: int) -> slice:
        return self.spec.edge_slice(edge_index)


def _validate_route(spec: HypergraphSpec, route: Route) -> None:
    if len(route.nodes) != len(route.edges) + 1 or not route.edges:
        raise ValueError("route must alternate nodes and at least one hyperedge")
    if len(set(route.nodes)) != len(route.nodes):
        raise ValueError("simple route repeats a node")
    if len(set(route.edges)) != len(route.edges):
        raise ValueError("simple route repeats a hyperedge")
    for left, edge_index, right in zip(route.nodes, route.edges, route.nodes[1:]):
        if left == right or edge_index < 0 or edge_index >= len(spec.edges):
            raise ValueError("invalid route hop")
        if left not in spec.edges[edge_index] or right not in spec.edges[edge_index]:
            raise ValueError("route hop endpoints are not contained in the selected hyperedge")


def route_increment(spec: HypergraphSpec, route: Route) -> np.ndarray:
    _validate_route(spec, route)
    index = {coordinate: i for i, coordinate in enumerate(spec.coordinates)}
    increment = np.zeros(len(index), dtype=np.int8)
    for left, edge_index, right in zip(route.nodes, route.edges, route.nodes[1:]):
        increment[index[(edge_index, left)]] -= 1
        increment[index[(edge_index, right)]] += 1
    return increment


def build_kernel(spec: HypergraphSpec, routes: Sequence[Route], probabilities: np.ndarray) -> NetworkKernel:
    routes = tuple(routes)
    probabilities = np.asarray(probabilities, dtype=np.float64)
    if probabilities.shape != (len(routes),) or np.any(probabilities <= 0.0):
        raise ValueError("route probabilities must be positive and match the route count")
    if not np.isclose(probabilities.sum(), 1.0, atol=1e-14):
        raise ValueError("route probabilities must sum to one")
    increments = np.stack([route_increment(spec, route) for route in routes])
    drift = probabilities @ increments
    centered = increments - drift
    covariance = centered.T @ (centered * probabilities[:, None])
    return NetworkKernel(spec, routes, probabilities, increments, drift, covariance)


def validate_phase_kernel(kernel: NetworkKernel, variance_tolerance: float = 1e-12) -> None:
    diagonal = np.diag(kernel.covariance)
    bad = [kernel.spec.coordinates[i] for i, value in enumerate(diagonal) if value <= variance_tolerance]
    if bad:
        raise ValueError(f"phase theorem requires positive normal variance on every face: {bad}")
```

- [ ] **Step 4: Implement the frozen two-triad fixture**

Use the exact routing rule below; the route order is lexicographic in `(source, target)` and therefore stable for hashes:

```python
def two_overlapping_triads_uniform() -> NetworkKernel:
    spec = HypergraphSpec(edges=((0, 1, 2), (2, 3, 4)), capacity_units=(3, 3))
    left, right = {0, 1}, {3, 4}
    routes: list[Route] = []
    for source in range(5):
        for target in range(5):
            if source == target:
                continue
            if source in left and target in right:
                route = Route((source, 2, target), (0, 1))
            elif source in right and target in left:
                route = Route((source, 2, target), (1, 0))
            elif source in spec.edges[0] and target in spec.edges[0]:
                route = Route((source, target), (0,))
            elif source in spec.edges[1] and target in spec.edges[1]:
                route = Route((source, target), (1,))
            else:
                raise AssertionError((source, target))
            routes.append(route)
    return build_kernel(spec, routes, np.full(len(routes), 1.0 / len(routes)))
```

- [ ] **Step 5: Run kernel tests**

Run: `python -m unittest test_network_model.NetworkKernelTests -v`

Expected: 5 tests pass; cross-block Frobenius norm is exactly `0.6` within `1e-12`, tangent-space rank is 4, and degenerate phase kernels are rejected explicitly.

- [ ] **Step 6: Save a task checkpoint**

If inside Git:

```powershell
git add network_model.py test_network_model.py
git commit -m "feat: add correlated hypergraph route kernel"
```

---

### Task 3: Implement the exact absorbing-chain baseline

**Files:**

- Create: `network_exact.py`
- Modify: `test_network_model.py`

**Interfaces:**

- Consumes: `NetworkKernel`, scale `N`, optional interior initial state.
- Produces: `ExactNetworkResult(mean, state_count, max_abs_residual, survival)` and a constructive finite-state reachability certificate.

- [ ] **Step 1: Write failing exact-solver tests**

```python
from network_exact import enumerate_internal_states, solve_exact


class ExactNetworkTests(unittest.TestCase):
    def test_product_composition_state_count(self) -> None:
        kernel = two_overlapping_triads_uniform()
        self.assertEqual(len(enumerate_internal_states(kernel.spec, 1)), 1)
        self.assertEqual(len(enumerate_internal_states(kernel.spec, 2)), 100)
        self.assertEqual(len(enumerate_internal_states(kernel.spec, 3)), 784)

    def test_n1_stops_after_one_route(self) -> None:
        result = solve_exact(two_overlapping_triads_uniform(), 1, survival_horizon=3)
        self.assertEqual(result.state_count, 1)
        self.assertAlmostEqual(result.mean, 1.0, places=14)
        np.testing.assert_allclose(result.survival, [1.0, 0.0, 0.0, 0.0])

    def test_small_network_poisson_residual_and_absorption(self) -> None:
        result = solve_exact(two_overlapping_triads_uniform(), 2, survival_horizon=20)
        self.assertEqual(result.state_count, 100)
        self.assertLess(result.max_abs_residual, 1e-10)
        self.assertTrue(result.all_states_reach_boundary)
        self.assertGreater(result.mean, 1.0)

    def test_single_triad_recovers_known_n_squared_mean(self) -> None:
        spec = HypergraphSpec(edges=((0, 1, 2),), capacity_units=(3,))
        routes = tuple(Route((i, j), (0,)) for i in range(3) for j in range(3) if i != j)
        kernel = build_kernel(spec, routes, np.full(6, 1.0 / 6.0))
        self.assertAlmostEqual(solve_exact(kernel, 2).mean, 4.0, places=12)

    def test_noninternal_initial_state_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "internal state"):
            solve_exact(two_overlapping_triads_uniform(), 2, initial=(0, 3, 3, 2, 2, 2))
```

- [ ] **Step 2: Run tests and confirm the solver is absent**

Run: `python -m unittest test_network_model.ExactNetworkTests -v`

Expected: FAIL with `ModuleNotFoundError: No module named 'network_exact'`.

- [ ] **Step 3: Implement independent state enumeration**

`network_exact.py` must not import `run_experiments.positive_compositions`:

```python
from __future__ import annotations

from dataclasses import dataclass
from itertools import product

import numpy as np
from scipy.sparse import csr_matrix, eye
from scipy.sparse.linalg import spsolve

from network_model import HypergraphSpec, NetworkKernel


def positive_compositions(total: int, parts: int):
    if parts == 1:
        if total >= 1:
            yield (total,)
        return
    for first in range(1, total - parts + 2):
        for tail in positive_compositions(total - first, parts - 1):
            yield (first,) + tail


def enumerate_internal_states(spec: HypergraphSpec, scale: int) -> tuple[tuple[int, ...], ...]:
    if not isinstance(scale, int) or scale <= 0:
        raise ValueError("scale N must be a positive integer")
    blocks = [tuple(positive_compositions(scale * c, len(edge))) for edge, c in zip(spec.edges, spec.capacity_units)]
    return tuple(tuple(value for block in blocks_state for value in block) for blocks_state in product(*blocks))


@dataclass(frozen=True)
class ExactNetworkResult:
    mean: float
    state_count: int
    max_abs_residual: float
    all_states_reach_boundary: bool
    survival: np.ndarray
```

- [ ] **Step 4: Build `Q`, prove constructive reachability, and solve `(I-Q)u=1`**

Implementation requirements:

```python
def build_transient_matrix(kernel: NetworkKernel, scale: int):
    states = enumerate_internal_states(kernel.spec, scale)
    index = {state: i for i, state in enumerate(states)}
    rows: list[int] = []
    cols: list[int] = []
    data: list[float] = []
    reverse: list[list[int]] = [[] for _ in states]
    leaks = np.zeros(len(states), dtype=bool)
    for row, state in enumerate(states):
        x = np.asarray(state, dtype=np.int64)
        for probability, increment in zip(kernel.probabilities, kernel.increments):
            nxt = x + increment
            if np.any(nxt == 0):
                leaks[row] = True
                continue
            col = index[tuple(int(value) for value in nxt)]
            rows.append(row)
            cols.append(col)
            data.append(float(probability))
            reverse[col].append(row)
    q = csr_matrix((data, (rows, cols)), shape=(len(states), len(states)))
    reachable = leaks.copy()
    stack = list(np.flatnonzero(leaks))
    while stack:
        child = stack.pop()
        for parent in reverse[child]:
            if not reachable[parent]:
                reachable[parent] = True
                stack.append(parent)
    return states, index, q, bool(np.all(reachable))


def balanced_initial_state(spec: HypergraphSpec, scale: int) -> tuple[int, ...]:
    blocks: list[int] = []
    for edge, capacity in zip(spec.edges, spec.capacity_units):
        total = scale * capacity
        if total % len(edge):
            raise ValueError("balanced initial state is not integral")
        blocks.extend([total // len(edge)] * len(edge))
    return tuple(blocks)


def solve_exact(kernel: NetworkKernel, scale: int, initial=None, survival_horizon: int = 0) -> ExactNetworkResult:
    states, index, q, reachable = build_transient_matrix(kernel, scale)
    if not reachable:
        raise ValueError("finite-state depletion reachability fails")
    initial = balanced_initial_state(kernel.spec, scale) if initial is None else tuple(initial)
    if initial not in index:
        raise ValueError("initial state must be a positive internal state with the declared edge capacities")
    matrix = eye(len(states), format="csr") - q
    rhs = np.ones(len(states))
    solution = spsolve(matrix, rhs)
    residual = matrix @ solution - rhs
    mass = np.zeros(len(states))
    mass[index[initial]] = 1.0
    survival = [1.0]
    for _ in range(survival_horizon):
        mass = mass @ q
        survival.append(float(mass.sum()))
    return ExactNetworkResult(
        mean=float(solution[index[initial]]),
        state_count=len(states),
        max_abs_residual=float(np.max(np.abs(residual))),
        all_states_reach_boundary=reachable,
        survival=np.asarray(survival),
    )
```

- [ ] **Step 5: Run exact tests**

Run: `python -m unittest test_network_model.ExactNetworkTests -v`

Expected: 5 tests pass; N=2 system has 100 states, the single-triad result is 4, and the residual is below `1e-10`.

- [ ] **Step 6: Save a task checkpoint**

If inside Git:

```powershell
git add network_exact.py test_network_model.py
git commit -m "feat: add exact correlated-network stopping solver"
```

---

### Task 4: Implement an independent Monte Carlo engine and exact cross-check

**Files:**

- Create: `network_simulation.py`
- Modify: `test_network_model.py`

**Interfaces:**

- Consumes: `NetworkKernel`, `N`, initial state, repetitions, seed.
- Produces: trajectory-level stopping times and boundary coordinate indices; `summarize_times` returns mean, SD, SE and 95% CI.

- [ ] **Step 1: Write failing reproducibility and exact-coverage tests**

```python
from network_simulation import simulate_network, summarize_times


class NetworkSimulationTests(unittest.TestCase):
    def test_n1_all_trajectories_stop_at_one(self) -> None:
        sample = simulate_network(two_overlapping_triads_uniform(), 1, 200, seed=20260717)
        np.testing.assert_array_equal(sample.stopping_times, 1)

    def test_seed_is_reproducible(self) -> None:
        kernel = two_overlapping_triads_uniform()
        first = simulate_network(kernel, 2, 500, seed=17)
        second = simulate_network(kernel, 2, 500, seed=17)
        np.testing.assert_array_equal(first.stopping_times, second.stopping_times)
        np.testing.assert_array_equal(first.boundary_coordinates, second.boundary_coordinates)

    def test_mc_interval_covers_n2_exact_mean(self) -> None:
        kernel = two_overlapping_triads_uniform()
        exact = solve_exact(kernel, 2).mean
        summary = summarize_times(simulate_network(kernel, 2, 30000, seed=2026071702).stopping_times)
        self.assertLessEqual(summary.ci_low, exact)
        self.assertGreaterEqual(summary.ci_high, exact)

    def test_nonpositive_initial_balance_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "strictly positive"):
            simulate_network(
                two_overlapping_triads_uniform(),
                2,
                20,
                seed=1,
                initial=(0, 3, 3, 2, 2, 2),
            )
```

- [ ] **Step 2: Run tests and confirm the simulator is absent**

Run: `python -m unittest test_network_model.NetworkSimulationTests -v`

Expected: FAIL with `ModuleNotFoundError: No module named 'network_simulation'`.

- [ ] **Step 3: Implement state initialization and batch simulation without exact-solver imports**

```python
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import numpy as np

from network_model import NetworkKernel


@dataclass(frozen=True)
class NetworkSample:
    stopping_times: np.ndarray
    boundary_coordinates: np.ndarray
    seed: int


@dataclass(frozen=True)
class TimeSummary:
    mean: float
    sd: float
    standard_error: float
    ci_low: float
    ci_high: float


def initial_balances(kernel: NetworkKernel, scale: int) -> np.ndarray:
    values: list[int] = []
    for edge, capacity in zip(kernel.spec.edges, kernel.spec.capacity_units):
        total = scale * capacity
        if total % len(edge):
            raise ValueError("balanced initial state is not integral")
        values.extend([total // len(edge)] * len(edge))
    return np.asarray(values, dtype=np.int32)


def validate_initial(kernel: NetworkKernel, scale: int, initial: Sequence[int]) -> np.ndarray:
    balances = np.asarray(initial, dtype=np.int64)
    if balances.shape != (len(kernel.spec.coordinates),) or np.any(balances <= 0):
        raise ValueError("initial balances must be strictly positive and match all coordinates")
    for edge_index, capacity in enumerate(kernel.spec.capacity_units):
        if int(balances[kernel.edge_slice(edge_index)].sum()) != scale * capacity:
            raise ValueError("initial balances must match every declared edge capacity")
    return balances.astype(np.int32)


def simulate_network(
    kernel: NetworkKernel,
    scale: int,
    repetitions: int,
    seed: int,
    initial: Sequence[int] | None = None,
    max_steps: int | None = None,
) -> NetworkSample:
    if repetitions <= 1:
        raise ValueError("repetitions must exceed one")
    rng = np.random.default_rng(seed)
    starting = initial_balances(kernel, scale) if initial is None else validate_initial(kernel, scale, initial)
    balances = np.repeat(starting[None, :], repetitions, axis=0)
    times = np.zeros(repetitions, dtype=np.int64)
    boundary = np.full(repetitions, -1, dtype=np.int32)
    active = np.arange(repetitions)
    while active.size:
        route_ids = rng.choice(len(kernel.routes), size=active.size, p=kernel.probabilities)
        balances[active] += kernel.increments[route_ids]
        times[active] += 1
        depleted_mask = np.any(balances[active] == 0, axis=1)
        depleted_rows = active[depleted_mask]
        if depleted_rows.size:
            boundary[depleted_rows] = np.argmin(balances[depleted_rows], axis=1)
        active = active[~depleted_mask]
        if max_steps is not None and active.size and int(times[active].max()) >= max_steps:
            raise RuntimeError("max_steps reached before all trajectories depleted")
    return NetworkSample(times, boundary, seed)


def summarize_times(stopping_times: np.ndarray) -> TimeSummary:
    sample = np.asarray(stopping_times, dtype=np.float64)
    mean = float(sample.mean())
    sd = float(sample.std(ddof=1))
    se = sd / math.sqrt(sample.size)
    half = 1.959963984540054 * se
    return TimeSummary(mean, sd, se, mean - half, mean + half)
```

- [ ] **Step 4: Run simulation tests twice**

Run: `python -m unittest test_network_model.NetworkSimulationTests -v` twice.

Expected: all 4 tests pass both times with identical deterministic results.

- [ ] **Step 5: Save a task checkpoint**

If inside Git:

```powershell
git add network_simulation.py test_network_model.py
git commit -m "feat: add independent network Monte Carlo"
```

---

### Task 5: Add topology families, drift laws, and the correlated/independent proxy comparison

**Files:**

- Create: `network_topologies.py`
- Create: `network_phase_validation.py`
- Modify: `network_model.py`
- Modify: `test_network_model.py`

**Interfaces:**

- Consumes: fixed topology, uniform or hotspot ordered-pair demand, `NetworkKernel`.
- Produces: reproducible topology/route catalogs, `pi_N = pi_0 + N^{-alpha} h`, and paired correlated/proxy stopping samples.

- [ ] **Step 1: Write failing topology and drift-law tests**

```python
from network_model import perturb_route_probabilities
from network_topologies import (
    overlap_chain_triads,
    overlap_star_triads,
    random_connected_triads,
    shortest_route_kernel,
)
from network_phase_validation import block_marginals, simulate_paired_proxy


class NetworkPhaseTests(unittest.TestCase):
    def test_topology_families_are_connected_and_reproducible(self) -> None:
        chain = overlap_chain_triads(3)
        star = overlap_star_triads(3)
        self.assertEqual(chain.edges, ((0, 1, 2), (2, 3, 4), (4, 5, 6)))
        self.assertEqual(star.edges, ((0, 1, 2), (0, 3, 4), (0, 5, 6)))
        self.assertEqual(random_connected_triads(4, seed=7), random_connected_triads(4, seed=7))
        self.assertEqual(shortest_route_kernel(chain).probabilities.sum(), 1.0)

    def test_polynomial_perturbation_has_declared_drift(self) -> None:
        base = two_overlapping_triads_uniform()
        forward = next(i for i, r in enumerate(base.routes) if r.nodes == (0, 2, 3))
        reverse = next(i for i, r in enumerate(base.routes) if r.nodes == (3, 2, 0))
        perturbed = perturb_route_probabilities(base, 25, 0.5, forward, reverse, amplitude=0.01)
        expected = 2.0 * 0.01 * base.increments[forward] / (25 ** 0.5)
        np.testing.assert_allclose(perturbed.drift, expected, atol=1e-14)

    def test_independent_proxy_preserves_each_edge_marginal(self) -> None:
        kernel = two_overlapping_triads_uniform()
        marginals = block_marginals(kernel)
        for edge_index, (increments, probabilities) in enumerate(marginals):
            block = kernel.edge_slice(edge_index)
            mean = probabilities @ increments
            np.testing.assert_allclose(mean, kernel.drift[block], atol=1e-14)

    def test_paired_proxy_is_reproducible_and_nonidentical(self) -> None:
        first = simulate_paired_proxy(two_overlapping_triads_uniform(), 10, 2000, seed=7717)
        second = simulate_paired_proxy(two_overlapping_triads_uniform(), 10, 2000, seed=7717)
        np.testing.assert_array_equal(first.correlated_times, second.correlated_times)
        np.testing.assert_array_equal(first.proxy_times, second.proxy_times)
        self.assertGreater(np.mean(first.correlated_times != first.proxy_times), 0.1)
```

- [ ] **Step 2: Run the tests and confirm missing interfaces**

Run: `python -m unittest test_network_model.NetworkPhaseTests -v`

Expected: FAIL because topology, perturbation and proxy functions do not yet exist.

- [ ] **Step 3: Implement deterministic topology constructors and shortest-route enumeration**

`network_topologies.py` must use a node–hyperedge BFS. For each ordered source–target pair, enumerate all shortest simple alternating paths, sort paths by `(edge sequence, node sequence)`, and divide the pair's demand mass equally across ties. Required constructors:

```python
from __future__ import annotations

import numpy as np

from network_model import HypergraphSpec, NetworkKernel, Route, build_kernel


def overlap_chain_triads(edge_count: int) -> HypergraphSpec:
    if edge_count < 2:
        raise ValueError("edge_count must be at least two")
    edges = tuple((2 * j, 2 * j + 1, 2 * j + 2) for j in range(edge_count))
    return HypergraphSpec(edges=edges, capacity_units=(3,) * edge_count)


def overlap_star_triads(edge_count: int) -> HypergraphSpec:
    if edge_count < 2:
        raise ValueError("edge_count must be at least two")
    edges = tuple((0, 2 * j + 1, 2 * j + 2) for j in range(edge_count))
    return HypergraphSpec(edges=edges, capacity_units=(3,) * edge_count)


def random_connected_triads(edge_count: int, seed: int) -> HypergraphSpec:
    if edge_count < 2:
        raise ValueError("edge_count must be at least two")
    rng = np.random.default_rng(seed)
    edges: list[tuple[int, int, int]] = [(0, 1, 2)]
    existing = [0, 1, 2]
    next_node = 3
    for _ in range(1, edge_count):
        connector = int(rng.choice(existing))
        edge = (connector, next_node, next_node + 1)
        edges.append(edge)
        existing.extend((next_node, next_node + 1))
        next_node += 2
    return HypergraphSpec(edges=tuple(edges), capacity_units=(3,) * edge_count)


def _shortest_routes(spec: HypergraphSpec, source: int, target: int) -> tuple[Route, ...]:
    from collections import deque

    queue = deque([(source, (source,), ())])
    best_hops: int | None = None
    found: list[Route] = []
    while queue:
        node, used_nodes, used_edges = queue.popleft()
        if best_hops is not None and len(used_edges) >= best_hops:
            continue
        for edge_index, edge in enumerate(spec.edges):
            if node not in edge or edge_index in used_edges:
                continue
            for neighbor in sorted(edge):
                if neighbor == node or neighbor in used_nodes:
                    continue
                nodes = used_nodes + (neighbor,)
                edges = used_edges + (edge_index,)
                if neighbor == target:
                    best_hops = len(edges) if best_hops is None else best_hops
                    if len(edges) == best_hops:
                        found.append(Route(nodes, edges))
                elif best_hops is None or len(edges) < best_hops:
                    queue.append((neighbor, nodes, edges))
    if not found:
        raise ValueError(f"no hypergraph route from {source} to {target}")
    return tuple(sorted(set(found), key=lambda route: (route.edges, route.nodes)))


def shortest_route_kernel(spec: HypergraphSpec, demand: dict[tuple[int, int], float] | None = None) -> NetworkKernel:
    nodes = tuple(sorted({node for edge in spec.edges for node in edge}))
    if demand is None:
        pairs = tuple((source, target) for source in nodes for target in nodes if source != target)
        demand = {pair: 1.0 / len(pairs) for pair in pairs}
    if any(source == target or mass <= 0.0 for (source, target), mass in demand.items()):
        raise ValueError("demand must contain positive mass on distinct source-target pairs")
    if not np.isclose(sum(demand.values()), 1.0, atol=1e-14):
        raise ValueError("demand probabilities must sum to one")
    weighted: list[tuple[Route, float]] = []
    for pair, mass in sorted(demand.items()):
        alternatives = _shortest_routes(spec, *pair)
        weighted.extend((route, mass / len(alternatives)) for route in alternatives)
    routes = tuple(route for route, _ in weighted)
    probabilities = np.asarray([mass for _, mass in weighted], dtype=np.float64)
    return build_kernel(spec, routes, probabilities)
```

Reject disconnected source–target pairs and any demand map whose positive mass does not sum to one.

- [ ] **Step 4: Implement the frozen polynomial perturbation family**

Add to `network_model.py`:

```python
def perturb_route_probabilities(
    base: NetworkKernel,
    scale: int,
    alpha: float,
    forward_index: int,
    reverse_index: int,
    amplitude: float,
) -> NetworkKernel:
    if scale <= 0 or alpha < 0 or amplitude <= 0:
        raise ValueError("invalid perturbation parameter")
    delta = amplitude * scale ** (-alpha)
    probabilities = base.probabilities.copy()
    probabilities[forward_index] += delta
    probabilities[reverse_index] -= delta
    if np.any(probabilities <= 0):
        raise ValueError("perturbation leaves the probability simplex")
    return build_kernel(base.spec, base.routes, probabilities)
```

The exact limiting drift is `beta = amplitude * (xi_forward - xi_reverse)`.

- [ ] **Step 5: Implement edge marginals and a genuine common-random-number proxy**

In `network_phase_validation.py`, aggregate identical block increments before sampling. At each global time and trajectory generate `U=(U_0,...,U_{|E|-1})`; the correlated route uses `U_0`, while proxy block `e` uses `U_e`. Both processes receive the same uniform cube and are advanced until each separately hits a boundary.

```python
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from network_model import NetworkKernel


@dataclass(frozen=True)
class PairedProxySample:
    correlated_times: np.ndarray
    proxy_times: np.ndarray
    seed: int


def block_marginals(kernel: NetworkKernel) -> tuple[tuple[np.ndarray, np.ndarray], ...]:
    result = []
    for edge_index in range(len(kernel.spec.edges)):
        block = kernel.edge_slice(edge_index)
        grouped: dict[tuple[int, ...], float] = {}
        for probability, row in zip(kernel.probabilities, kernel.increments[:, block]):
            key = tuple(int(value) for value in row)
            grouped[key] = grouped.get(key, 0.0) + float(probability)
        keys = sorted(grouped)
        result.append((np.asarray(keys, dtype=np.int8), np.asarray([grouped[key] for key in keys])))
    return tuple(result)


def simulate_paired_proxy(kernel: NetworkKernel, scale: int, repetitions: int, seed: int) -> PairedProxySample:
    """Vectorized paired simulation using a common uniform cube per step."""
    from network_simulation import initial_balances

    if repetitions <= 1:
        raise ValueError("repetitions must exceed one")
    rng = np.random.default_rng(seed)
    edge_count = len(kernel.spec.edges)
    correlated = np.repeat(initial_balances(kernel, scale)[None, :], repetitions, axis=0)
    proxy = correlated.copy()
    correlated_times = np.zeros(repetitions, dtype=np.int64)
    proxy_times = np.zeros(repetitions, dtype=np.int64)
    correlated_active = np.ones(repetitions, dtype=bool)
    proxy_active = np.ones(repetitions, dtype=bool)
    route_cdf = np.cumsum(kernel.probabilities)
    route_cdf[-1] = 1.0
    marginals = block_marginals(kernel)
    marginal_cdfs = tuple(np.cumsum(probabilities) for _, probabilities in marginals)
    for cdf in marginal_cdfs:
        cdf[-1] = 1.0

    while np.any(correlated_active) or np.any(proxy_active):
        uniforms = rng.random((repetitions, edge_count))
        corr_rows = np.flatnonzero(correlated_active)
        if corr_rows.size:
            route_ids = np.searchsorted(route_cdf, uniforms[corr_rows, 0], side="right")
            correlated[corr_rows] += kernel.increments[route_ids]
            correlated_times[corr_rows] += 1
            correlated_active[corr_rows[np.any(correlated[corr_rows] == 0, axis=1)]] = False

        proxy_rows = np.flatnonzero(proxy_active)
        if proxy_rows.size:
            for edge_index, ((increments, _), cdf) in enumerate(zip(marginals, marginal_cdfs)):
                draw_ids = np.searchsorted(cdf, uniforms[proxy_rows, edge_index], side="right")
                proxy[proxy_rows, kernel.edge_slice(edge_index)] += increments[draw_ids]
            proxy_times[proxy_rows] += 1
            proxy_active[proxy_rows[np.any(proxy[proxy_rows] == 0, axis=1)]] = False

    return PairedProxySample(correlated_times, proxy_times, seed)
```

The proxy must sample each edge block independently from its exact marginal, preserve each edge's drift and covariance block, and stop on its own first zero. Do not label it as a realizable routed payment process.

- [ ] **Step 6: Run phase tests**

Run: `python -m unittest test_network_model.NetworkPhaseTests -v`

Expected: 4 tests pass.

- [ ] **Step 7: Save a task checkpoint**

If inside Git:

```powershell
git add network_model.py network_topologies.py network_phase_validation.py test_network_model.py
git commit -m "feat: add correlated network phase validation"
```

---

### Task 6: Produce frozen exact, Monte Carlo, phase, and dependence evidence

**Files:**

- Modify: `network_phase_validation.py`
- Create: `results/network/network-exact.csv`
- Create: `results/network/network-mc-exact-check.csv`
- Create: `results/network/network-phase-scaling.csv`
- Create: `results/network/network-correlated-vs-proxy.csv`
- Create: `results/network/network-survival-curves.csv`
- Create: `results/network/network-run-metadata.json`
- Create: `results/network/SHA256SUMS.txt`

**Interfaces:**

- Consumes: Tasks 2–5 public APIs.
- Produces: every numerical claim required by T16/T18 and a diagnostic, not proof, for T17.

- [ ] **Step 1: Add a quick-mode evidence schema test**

```python
class NetworkEvidenceTests(unittest.TestCase):
    def test_quick_run_has_required_metadata(self) -> None:
        from network_phase_validation import run_validation
        output = ROOT / ".tmp" / "network-validation-test"
        metadata = run_validation(output, quick=True)
        self.assertEqual(metadata["model"], "network-first-depletion")
        self.assertEqual(metadata["stop_event"], "first balance coordinate equal to zero")
        for key in ("seed", "python", "numpy", "scipy", "config_sha256", "files"):
            self.assertIn(key, metadata)
        self.assertTrue(all(Path(path).exists() for path in metadata["files"]))
```

- [ ] **Step 2: Run the test and confirm `run_validation` is absent**

Run: `python -m unittest test_network_model.NetworkEvidenceTests -v`

Expected: FAIL with an import error for `run_validation`.

- [ ] **Step 3: Implement the exact experiment grid**

Use only the two-triad topology with `N in {1,2,3}`. Save state count, exact mean, residual, reachability flag and survival values. Acceptance gates:

- `N=1` exact mean is 1;
- state counts are `1, 100, 784`;
- every residual is `<1e-10`;
- every reachability flag is true.

- [ ] **Step 4: Implement independent MC-to-exact cross-validation**

Full mode uses 50,000 trajectories for `N=1,2,3`; quick mode uses 5,000. Save seed, mean, SD, SE, 95% CI, exact mean and standardized difference `(mc-exact)/SE`. Acceptance gates:

- N=1 is exact;
- N=2 and N=3 have `abs(z) <= 2.58` (99% single-check tolerance);
- report the raw z-score even when the gate fails; do not silently rerun with another seed.

- [ ] **Step 5: Implement the three-regime scaling diagnostic**

For the two-triad forward/reverse perturbation with amplitude `0.01`, run:

```python
PHASE_GRID = {
    0.5: (10, 20, 40, 80),
    1.0: (10, 20, 40, 80),
    1.5: (10, 20, 40, 80),
}
```

Full mode uses 20,000 trajectories per cell; quick mode uses 2,000. Save `mean/N**(1+alpha)` for `alpha=0.5`, and `mean/N**2` for `alpha in {1,1.5}`, together with quantiles 0.1/0.5/0.9. Treat stabilization as descriptive evidence only; do not fit or claim a convergence rate.

- [ ] **Step 6: Implement paired correlation diagnostics**

For the uniform two-triad topology use `N in {10,20,40}` and full-mode 50,000 paired trajectories. Save paired differences for mean, median, 0.1/0.9 quantiles and survival probabilities on a frozen normalized grid. For the mean difference use:

```python
difference = correlated_times / (N * N) - proxy_times / (N * N)
mean_difference = float(difference.mean())
paired_se = float(difference.std(ddof=1) / np.sqrt(difference.size))
ci_low = mean_difference - 1.959963984540054 * paired_se
ci_high = mean_difference + 1.959963984540054 * paired_se
```

Report the sign observed at each N; do not generalize it to all topologies.

- [ ] **Step 7: Write metadata and hashes atomically through normal Python file APIs**

`network-run-metadata.json` must contain the resolved grids, all seeds, dependency versions, exact stop-event sentence, input route/probability SHA-256 and output file list. `SHA256SUMS.txt` contains one lower-case digest and POSIX-style relative path per result file, sorted by path.

- [ ] **Step 8: Run quick then full evidence generation**

Run:

```powershell
python network_phase_validation.py --quick --output results/network-quick
python -m unittest test_network_model.NetworkEvidenceTests -v
python network_phase_validation.py --output results/network
```

Expected: quick test passes; full run writes seven evidence files and exits zero. If any fixed-seed statistical gate fails, preserve outputs and investigate before any rerun.

- [ ] **Step 9: Save a task checkpoint**

If inside Git, commit code and the compact CSV/JSON/hash outputs; do not commit oversized raw trajectory arrays.

---

### Task 7: Close the T16–T18 proof package with explicit downgrade rules

**Files:**

- Create: `outputs/researchwrite/hypergraph-stopping-time/13_correlated_network_proof_package.md`
- Create: `outputs/researchwrite/hypergraph-stopping-time/14_correlated_network_external_review_packet.md`

**Interfaces:**

- Consumes: approved contract, exact reachability certificate, finite-step kernel assumptions, prior single-edge proof packages 07/10/11.
- Produces: a theorem-ready internal proof draft and a reviewer-ready independent signoff interface.

- [ ] **Step 1: Write T16 as a complete finite-state proposition**

The proof must explicitly establish:

1. the state count product of positive-composition counts;
2. every internal transition is executable under unit payments;
3. the assumed positive-probability route word gives a path to the boundary from each state;
4. finiteness implies no closed interior communicating class;
5. hence `Q_N^m -> 0`, `rho(Q_N)<1`, `(I-Q_N)^{-1}=sum_m Q_N^m`, and `u=(I-Q_N)^{-1}1`;
6. the code's reverse-reachability certificate checks the finite-N hypothesis but does not replace the mathematical assumption.

- [ ] **Step 2: Write the drift-dominated T17A proof with constants**

For every fixed epsilon, define the early time `(1-epsilon)t*` and late time `(1+epsilon)t*`. Use the freely extended process and maximal Azuma for the finite coordinate union. Record the deterministic margin after using `N^alpha d_N -> beta`; it must be at least `c_epsilon N` for all large N. For the late tail select one minimizing negative-drift coordinate. Extend the late-tail bound over geometric time blocks to prove a uniform exponential moment of `tau/t*`, then derive all fixed positive moments by uniform integrability.

Downgrade T17A to a concentration conjecture if the long-tail block estimate or its uniform constants are not written explicitly.

- [ ] **Step 3: Write the FCLT and exit-map proof for T17B/C**

The proof must include:

- triangular-array centering and covariance convergence on the product tangent space;
- deterministic drift term `N d_N` on the `N^2` clock;
- Donsker/Lindeberg verification from bounded increments;
- a lemma that every first-hit face has positive normal variance and Brownian paths cross its supporting hyperplane immediately after first contact;
- an argument covering simultaneous first hits of multiple faces;
- the continuous mapping conclusion for the exit time.

If the simultaneous-face lemma is not closed, state only process convergence and label exit-time convergence unresolved.

- [ ] **Step 4: Prove a uniform O(N^2) mean bound and exponential tail blocks**

For nonzero critical drift, use a negative coordinate and truncated optional stopping. For zero/vanishing drift, use

```text
V_N(x) = sum_{e,v} (x_{e,v} - N c_e/k_e)^2
E[Delta V_N | x] = E||xi||^2 + 2 <x-center, d_N>.
```

Bound `max_x V_N(x)` by a constant times `N^2`, show the drift perturbation is `o(1)` for `alpha>1`, and obtain a uniform positive increment lower bound. Apply the strong Markov property in blocks of `K N^2` to get a geometric tail, a uniform exponential moment, and all fixed positive moment convergence.

Do not claim the same potential proof for `alpha=1, beta != 0`; that case uses the negative-coordinate argument.

- [ ] **Step 5: Formalize T18a and T18b**

T18a proof: block-zero covariance + joint Gaussianity implies independent Brownian edge blocks; therefore `T=min_e T_e` and `P(T>t)=prod_e P(T_e>t)`.

T18b evidence statement: cite the frozen two-triad kernel, nonzero cross block and paired diagnostics. State that it is an explicit non-factorization counterexample/measurement, not a universal analytic ordering theorem.

- [ ] **Step 6: Add a 14-item independent review packet**

The packet must require separate yes/no/signature fields for: model semantics, reachability, spectral argument, early tail, late tail, exponential moments, FCLT, tangent-space covariance, single-face crossing, multi-face crossing, critical mean bound, vanishing-drift potential, T18 Gaussian independence, and claim/literature boundary. Add a failure action beside every item.

- [ ] **Step 7: Run a proof-package completeness scan**

Run:

```powershell
rg -n "TBD|TODO|待补|显然|不难|全球首次" outputs/researchwrite/hypergraph-stopping-time/13_correlated_network_proof_package.md outputs/researchwrite/hypergraph-stopping-time/14_correlated_network_external_review_packet.md
```

Expected: no placeholder or prohibited novelty language. Chinese phrases such as “待外部独立复核” are allowed only in the status banner, not in place of a proof step.

- [ ] **Step 8: Save a task checkpoint**

If inside Git: commit the proof package and review packet separately from numerical outputs.

---

### Task 8: Synchronize research authority documents without overstating completion

**Files:**

- Modify: `outputs/researchwrite/hypergraph-stopping-time/00_scope.md`
- Modify: `outputs/researchwrite/hypergraph-stopping-time/01_research_canon.md`
- Modify: `outputs/researchwrite/hypergraph-stopping-time/02_evidence_table.md`
- Modify: `outputs/researchwrite/hypergraph-stopping-time/03_argument_map.md`
- Modify: `outputs/researchwrite/hypergraph-stopping-time/04_section_contracts.md`
- Modify: `outputs/researchwrite/hypergraph-stopping-time/06_theorem_proof_gap_register.md`
- Modify: `outputs/researchwrite/hypergraph-stopping-time/exports/项目进展审计_超图支付通道停止时间_2026-07-17.md`
- Modify: `outputs/researchwrite/hypergraph-stopping-time/state.json`
- Modify: `README.md`

**Interfaces:**

- Consumes: actual Task 1–7 outcomes and gate results.
- Produces: one consistent project status; no document may claim a stronger theorem status than the proof register.

- [ ] **Step 1: Correct T13's novelty classification everywhere**

Use exactly: “独立通道/超边生存函数乘积是 Podiatchev–Orda–Rottenstreich (2024) 直接覆盖的基线；本项目只复现并用作相关网络对照。” Remove any wording that presents T13 as a project contribution.

- [ ] **Step 2: Add T16–T18 to the proof register with evidence-conditioned status**

Use this table logic:

```markdown
| T16 | 相关网络有限状态吸收与 Poisson 方程 | 有限状态耗尽可达性 | 13 证明包；精确求解残差 | A only if proof and reachability gates pass; otherwise B |
| T17 | 相关网络多项式漂移三分区及全矩极限 | 12 合同第 6 节 | 13 证明包；数值仅诊断 | A only if all four proof modules close; otherwise split and downgrade |
| T18a | 零跨块协方差下的扩散级独立聚合 | 联合 Gaussian 极限 | block independence proof | A after proof |
| T18b | 非零相关性的显式反例与误差诊断 | 冻结拓扑/需求/代理 | paired MC + exact baseline | E; not a universal sign theorem |
```

- [ ] **Step 3: Replace the old scope sentence conditionally**

Only if T16/T17 internal proof gates and Task 6 evidence pass, change the scope to:

```markdown
论文主线现扩展为“固定超图支付通道网络在外生随机多超边路由下的首次余额
耗尽时间”。网络级精确方程、相关扩散极限与漂移相图已形成内部证明工作稿，
但仍需未参与推导者独立复核；在该复核完成前不得表述为已同行评审结果。
```

Otherwise retain the single-channel title and list network theory as an active work package.

- [ ] **Step 4: Update `outputs/researchwrite/hypergraph-stopping-time/state.json` without invented score improvements**

Set:

```json
{
  "phase": "correlated_hypergraph_network_first_depletion",
  "status": "internal_draft",
  "updated": "2026-07-17",
  "last_completed": "correlated_network_model_proof_and_validation_package",
  "recommended_track": "theory_first_correlated_fixed_hypergraph_network"
}
```

Preserve the existing scores unless a written rubric recomputation is added. Remove `dependent_hyperedge_network_not_modeled` only if Tasks 2–6 pass; replace it with `correlated_network_theorems_require_external_independent_probability_audit`. Preserve all unrelated technical debts.

- [ ] **Step 5: Update the main progress audit conclusion first**

The new conclusion must distinguish four levels:

1. established prior baseline;
2. internally closed project proof work;
3. reproducible numerical evidence;
4. remaining publication gates.

It must name the remaining gates: external probability review, broader database novelty audit, T18 cross-topology robustness, manuscript assembly, and target-journal formatting.

- [ ] **Step 6: Repair README encoding and add reproducible commands**

Save `README.md` as UTF-8 and add:

```powershell
python -m unittest test_network_model -v
python network_phase_validation.py --quick --output results/network-quick
python network_phase_validation.py --output results/network
node render_research_html.mjs "outputs/researchwrite/hypergraph-stopping-time/exports/项目进展审计_超图支付通道停止时间_2026-07-17.md" "项目进展审计_超图支付通道停止时间_2026-07-17.html" "超图支付通道停止时间研究：项目进展审计与论文推进路线"
```

- [ ] **Step 7: Run cross-document forbidden-claim checks**

Run:

```powershell
rg -n "首次提出超图|首次研究.*depletion|全球首次|相关误差总是|等同于网络断连|等同于支付失败" README.md outputs/researchwrite/hypergraph-stopping-time
```

Expected: zero unsupported claims. Any match in a “forbidden claims” list must be visibly negated.

- [ ] **Step 8: Save a task checkpoint**

If inside Git: commit authority-document synchronization after reviewing the diff independently of code.

---

### Task 9: Run end-to-end verification, create QA evidence, and render the audit HTML

**Files:**

- Create: `outputs/researchwrite/hypergraph-stopping-time/qa_logs/2026-07-17_correlated_network_model_qa.md`
- Modify: `项目进展审计_超图支付通道停止时间_2026-07-17.html`

**Interfaces:**

- Consumes: all previous tasks.
- Produces: final internal handoff with exact pass/fail evidence and explicit publication blockers.

- [ ] **Step 1: Run the complete Python regression suite**

Run:

```powershell
python -m unittest test_hyperedge test_final_formula test_drift test_network_model -v
```

Expected: all legacy tests and all new network tests pass. Record the exact test count and runtime; do not summarize as “tests pass” without numbers.

- [ ] **Step 2: Re-run frozen full network evidence and verify hashes**

Run:

```powershell
python network_phase_validation.py --output results/network
Get-FileHash -Algorithm SHA256 results/network/* | Sort-Object Path
```

Expected: computed hashes match `results/network/SHA256SUMS.txt` and the exact linear residual gate remains below `1e-10`.

- [ ] **Step 3: Validate JSON, CSV schemas, BibTeX keys, and Markdown links**

Use a read-only Python check that:

- parses `outputs/researchwrite/hypergraph-stopping-time/state.json` and every result JSON;
- opens every CSV with `csv.DictReader` and checks required columns;
- rejects duplicate BibTeX keys/DOIs;
- resolves every relative Markdown link under the research project;
- rejects control characters outside newline/tab/carriage return.

Expected: zero parse errors, zero duplicate keys/DOIs, zero broken local links, zero invalid control characters.

- [ ] **Step 4: Render and inspect the HTML**

Run:

```powershell
node render_research_html.mjs "outputs/researchwrite/hypergraph-stopping-time/exports/项目进展审计_超图支付通道停止时间_2026-07-17.md" "项目进展审计_超图支付通道停止时间_2026-07-17.html" "超图支付通道停止时间研究：项目进展审计与论文推进路线"
```

Verify that the HTML contains UTF-8 Chinese text, T16–T18, the current title recommendation, and MathJax delimiters; open it for visual inspection and check tables, equations and links.

- [ ] **Step 5: Write the QA log as evidence, not narrative**

The log must contain:

```markdown
## Verification ledger

| Gate | Command/input | Expected | Observed | Status | Artifact/hash |
|---|---|---|---|---|---|
| Model invariants | unittest selector | conservation/covariance values | exact output | PASS/FAIL | file hash |
| Exact solver | N=1,2,3 | residual < 1e-10 | maximum residual | PASS/FAIL | CSV hash |
| MC vs exact | frozen seeds | abs(z) <= 2.58 | each z | PASS/FAIL | CSV hash |
| Phase diagnostics | frozen grid | outputs complete | cell count | PASS/FAIL | CSV hash |
| Paired proxy | N=10,20,40 | CI reported | estimates/CIs | PASS/FAIL | CSV hash |
| Proof completeness | T16–T18 scan | no placeholders | matches | PASS/FAIL | Markdown hash |
| Authority consistency | cross-file scan | no unsupported claims | matches | PASS/FAIL | file list |
| HTML render | visual + structural | readable | observed | PASS/FAIL | HTML hash |
```

End with `Publication status: not submission-ready` until an independent probability reviewer signs Task 7's packet and the broader novelty search is completed.

- [ ] **Step 6: Apply failure policy before any completion claim**

- A deterministic invariant/residual/hash failure blocks authority-document promotion.
- A fixed-seed MC coverage failure triggers diagnosis and a predeclared higher-repetition sensitivity run; never seed shopping.
- A proof gap downgrades only the affected T17 subregime, not unrelated exact results.
- A literature conflict narrows the contribution statement before any manuscript drafting.
- A render/link issue blocks delivery of the HTML but does not invalidate mathematical results.

- [ ] **Step 7: Save the final checkpoint**

If inside Git:

```powershell
git add .
git status --short
git commit -m "feat: validate correlated hypergraph network stopping time"
```

Before committing, remove unrelated paths from the index and verify no large raw trajectory file is staged.

---

## Completion Definition

This implementation plan is complete only when:

- all deterministic model/exact/hash checks pass;
- the independent MC crosses the predeclared exact-value gates without seed changes;
- T16 has a closed proof;
- each T17 subregime is either fully proved or explicitly downgraded;
- T18 is stated as a Gaussian sufficient condition plus frozen counterexample/diagnostic, not a universal sign claim;
- the authority documents agree on theorem status and prior-art boundaries;
- the audit HTML is visually verified;
- the external-review packet exists, while submission readiness remains false until it is independently signed.
