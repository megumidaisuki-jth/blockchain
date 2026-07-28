"""Planning-only drift interpolation preflight on the frozen 2026 projection."""
from __future__ import annotations
import argparse, csv, hashlib, json, math, platform, time
from pathlib import Path
import matplotlib as mpl
import matplotlib.pyplot as plt
import networkx as nx
import numba, numpy as np, scipy
from lightning_current_2026_preflight import plan_formal_repetitions
from lightning_mapping_simulation import simulate_paired_proxy_compiled
from lightning_real_topology_formal import block_difference_summary
from lightning_real_topology_preflight import summarize_preflight_cell
from lightning_topology_mapping import build_interpolated_snapshot_kernel, build_snapshot_kernel, extract_connected_subgraph, load_mempool_channels_geo, snapshot_sha256

WEIGHTS=(0.0,0.25,0.5,0.75,1.0); MODES=("primary","hub"); SCALE=40; BLOCK_COUNT=40; COMPARISONS=10; SEED_BASE=202607280000


def _write_csv(path, rows):
    with path.open("w",encoding="utf-8",newline="") as h:
        w=csv.DictWriter(h,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def _plot(rows, path):
    mpl.rcParams.update({"font.family":"sans-serif","font.sans-serif":["Arial","Helvetica","DejaVu Sans"],"font.size":7,"axes.spines.right":False,"axes.spines.top":False})
    fig,axes=plt.subplots(1,2,figsize=(183/25.4,62/25.4),constrained_layout=True)
    colors={"primary":"#4C78A8","hub":"#F28E2B"}
    for mode in MODES:
        part=[r for r in rows if r["mode"]==mode]; x=np.array([r["hotspot_weight"] for r in part]); y=np.array([r["block_mean_difference"] for r in part]); hw=np.array([r["block_ci_halfwidth"] for r in part])
        axes[0].errorbar(x,y,yerr=hw,marker="o",ms=3,lw=1,capsize=2,color=colors[mode],label=mode)
        axes[1].plot(x,[r["maximum_absolute_drift"] for r in part],marker="o",ms=3,lw=1,color=colors[mode],label=mode)
    axes[0].axhline(0,color="black",lw=.7); axes[0].set(xlabel="Hotspot weight λ",ylabel="Normalized stopping-time effect",title="a  Planning effect curve")
    axes[1].set(xlabel="Hotspot weight λ",ylabel="Maximum absolute channel drift",title="b  Controlled affine drift"); axes[0].legend(); axes[1].legend()
    fig.savefig(path,dpi=600,bbox_inches="tight"); plt.close(fig)


def run(source:Path,output:Path,repetitions:int=2000):
    if repetitions%BLOCK_COUNT or repetitions<80: raise ValueError("repetitions must be divisible by 40 and at least 80")
    output.mkdir(parents=True,exist_ok=True)
    if any(output.iterdir()): raise ValueError("output directory must be absent or empty")
    digest=snapshot_sha256(source)
    if digest!="fbddddc486a8bb644520c373fd9588dc3811a6414c77185f0b2e8740e338637b": raise ValueError("source hash mismatch")
    graph,_=load_mempool_channels_geo(source,expected_records=10000)
    warm=nx.path_graph(("a","b","c"))
    for i,e in enumerate(warm.edges): warm.edges[e]["scid"]=str(i)
    wk,_=build_snapshot_kernel(warm,demand_kind="uniform"); simulate_paired_proxy_compiled(wk,scale=1,repetitions=2,seed=1)
    rows=[]; blocks=[]; started=time.perf_counter(); block_size=repetitions//BLOCK_COUNT
    for mi,mode in enumerate(MODES):
        sub=extract_connected_subgraph(graph,digest,mode=mode,node_count=31)
        reference=None
        for wi,weight in enumerate(WEIGHTS):
            kernel,meta=build_interpolated_snapshot_kernel(sub,hotspot_weight=weight)
            signature=hashlib.sha256(kernel.increments.tobytes()).hexdigest()
            reference=reference or signature
            if signature!=reference: raise AssertionError("route increments changed across interpolation")
            seed=SEED_BASE+mi*100+wi; t0=time.perf_counter(); sample=simulate_paired_proxy_compiled(kernel,scale=SCALE,repetitions=repetitions,seed=seed); runtime=time.perf_counter()-t0
            summary=summarize_preflight_cell(sample.correlated_times,sample.proxy_times,scale=SCALE,comparisons=COMPARISONS)
            means,bsummary=block_difference_summary(sample.correlated_times,sample.proxy_times,scale=SCALE,block_size=block_size,comparisons=COMPARISONS)
            row={"cell_id":f"2026-07-22-{mode}-lambda{weight:g}-N40","mode":mode,"hotspot_weight":weight,"scale":SCALE,"seed":seed,"repetitions":repetitions,"maximum_absolute_drift":meta["maximum_absolute_drift"],"increment_sha256":signature,**summary,**bsummary,"censored_count":0,"runtime_seconds":runtime}; rows.append(row)
            for bi,value in enumerate(means): blocks.append({"cell_id":row["cell_id"],"block_index":bi,"normalized_mean_difference":float(value)})
            print(f"[{len(rows):02d}/10] {row['cell_id']} runtime={runtime:.2f}s effect={row['block_mean_difference']:.5f}",flush=True)
    maxhw=max(float(r["block_ci_halfwidth"]) for r in rows); planned=plan_formal_repetitions(maxhw,pilot_repetitions=repetitions)
    metadata={"artifact_kind":"drift-interpolation-preflight-planning-only","cell_count":10,"repetitions_per_cell":repetitions,"block_count":40,"scale":40,"censored_count":0,"maximum_block_ci_halfwidth":maxhw,"planned_formal_repetitions_per_cell":planned,"precision_target":0.03,"total_runtime_seconds":time.perf_counter()-started,"software":{"python":platform.python_version(),"numpy":np.__version__,"scipy":scipy.__version__,"numba":numba.__version__}}
    _write_csv(output/"drift-interpolation-preflight.csv",rows); _write_csv(output/"drift-interpolation-preflight-blocks.csv",blocks); (output/"metadata.json").write_text(json.dumps(metadata,indent=2)+"\n",encoding="utf-8"); _plot(rows,output/"drift-interpolation-preflight.png")
    files=sorted(p for p in output.iterdir() if p.name!="SHA256SUMS.txt"); (output/"SHA256SUMS.txt").write_text("\n".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}" for p in files)+"\n",encoding="utf-8")
    return metadata


def main():
    p=argparse.ArgumentParser(); p.add_argument("--source",type=Path,default=Path("data/raw/mempool-lightning-2026-07-22/channels-geo.json")); p.add_argument("--output",type=Path,default=Path("results/lightning-drift-interpolation-preflight")); p.add_argument("--repetitions",type=int,default=2000); a=p.parse_args(); print(json.dumps(run(a.source,a.output,a.repetitions),indent=2))


if __name__=="__main__": main()
