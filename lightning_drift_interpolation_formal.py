"""Checkpointed formal and replication drift-interpolation experiments."""
from __future__ import annotations

import argparse, csv, hashlib, json, math, platform, time
from pathlib import Path
import networkx as nx
import numba, numpy as np, scipy
from scipy.stats import t as student_t

from lightning_mapping_simulation import simulate_paired_proxy_compiled
from lightning_mapping_validation import SNAPSHOTS
from lightning_real_topology_formal import block_difference_summary
from lightning_real_topology_preflight import summarize_preflight_cell
from lightning_topology_mapping import build_interpolated_snapshot_kernel, build_snapshot_kernel, extract_connected_subgraph, load_mempool_channels_geo, load_snapshot, snapshot_sha256

WEIGHTS=(0.0,0.25,0.5,0.75,1.0); MODES=("primary","hub"); SCALE=40
BLOCK_COUNT=40; CELL_COUNT=40; ANCHOR_COUNT=8; SOURCE_2026_SHA="fbddddc486a8bb644520c373fd9588dc3811a6414c77185f0b2e8740e338637b"
SEED_BASES={"formal":202607290000,"replication":202607300000}


def _sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()


def _write_csv(path:Path,rows:list[dict[str,object]])->None:
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def linear_slope_weights()->np.ndarray:
    x=np.asarray(WEIGHTS,dtype=float); return (x-x.mean())/np.sum((x-x.mean())**2)


def summarize_anchor_slope(block_matrix:np.ndarray,*,comparisons:int=ANCHOR_COUNT)->tuple[np.ndarray,dict[str,float|int]]:
    matrix=np.asarray(block_matrix,dtype=float)
    if matrix.shape!=(len(WEIGHTS),BLOCK_COUNT) or not np.all(np.isfinite(matrix)): raise ValueError("block_matrix must have shape (5, 40) and be finite")
    slopes=linear_slope_weights()@matrix; mean=float(slopes.mean()); se=float(slopes.std(ddof=1)/math.sqrt(BLOCK_COUNT)); critical=float(student_t.ppf(1-.05/(2*comparisons),BLOCK_COUNT-1)); hw=critical*se
    return slopes,{"slope":mean,"slope_standard_error":se,"slope_simultaneous_critical":critical,"slope_ci_low":mean-hw,"slope_ci_high":mean+hw,"slope_ci_halfwidth":hw}


def _load_or_run(path:Path,kernel,*,repetitions:int,seed:int,source_sha:str,increment_sha:str,weight:float)->tuple[np.ndarray,np.ndarray,float,bool]:
    if path.exists():
        with np.load(path,allow_pickle=False) as z:
            if int(z["scale"])!=SCALE or int(z["repetitions"])!=repetitions or int(z["seed"])!=seed or str(z["source_sha256"])!=source_sha or str(z["increment_sha256"])!=increment_sha or float(z["hotspot_weight"])!=weight: raise ValueError(f"checkpoint configuration mismatch: {path}")
            c=z["correlated_times"]; p=z["proxy_times"]; runtime=float(z["runtime_seconds"])
        if c.shape!=(repetitions,) or p.shape!=(repetitions,): raise ValueError(f"checkpoint shape mismatch: {path}")
        return c,p,runtime,True
    t=time.perf_counter(); sample=simulate_paired_proxy_compiled(kernel,scale=SCALE,repetitions=repetitions,seed=seed); runtime=time.perf_counter()-t; tmp=path.with_suffix(".tmp.npz")
    np.savez_compressed(tmp,correlated_times=sample.correlated_times,proxy_times=sample.proxy_times,scale=np.int64(SCALE),repetitions=np.int64(repetitions),seed=np.int64(seed),source_sha256=np.asarray(source_sha),increment_sha256=np.asarray(increment_sha),hotspot_weight=np.float64(weight),runtime_seconds=np.float64(runtime)); tmp.replace(path)
    return sample.correlated_times,sample.proxy_times,runtime,False


def _sources(snapshot_root:Path,current_source:Path):
    for date_index,(filename,declared) in enumerate(SNAPSHOTS.items()):
        path=snapshot_root/filename; digest=snapshot_sha256(path); graph=load_snapshot(path,expected_nodes=int(declared["nodes"]),expected_edges=int(declared["channels"])); yield date_index,declared["date"],filename,digest,graph,"historical public topology; synthetic interpolated demand"
    digest=snapshot_sha256(current_source)
    if digest!=SOURCE_2026_SHA: raise ValueError("2026 source hash mismatch")
    graph,_=load_mempool_channels_geo(current_source,expected_records=10000); yield 3,"2026-07-22",current_source.name,digest,graph,"current filtered projection; synthetic interpolated demand"


def run_stage(snapshot_root:Path,current_source:Path,output:Path,*,stage:str,repetitions:int=36560,block_size:int=914)->dict[str,object]:
    if stage not in SEED_BASES: raise ValueError("stage must be formal or replication")
    if type(repetitions) is not int or repetitions<80 or repetitions%BLOCK_COUNT or block_size!=repetitions//BLOCK_COUNT: raise ValueError("repetitions must form 40 equal blocks and block_size must match")
    if (output/"SHA256SUMS.txt").exists(): raise ValueError("completed output must not be overwritten")
    output.mkdir(parents=True,exist_ok=True); unexpected=[p for p in output.iterdir() if p.name!="raw"]
    if unexpected: raise ValueError("incomplete output may contain only raw checkpoints")
    raw=output/"raw"; raw.mkdir(exist_ok=True)
    warm=nx.path_graph(("a","b","c"))
    for i,e in enumerate(warm.edges): warm.edges[e]["scid"]=str(i)
    wk,_=build_snapshot_kernel(warm,demand_kind="uniform"); simulate_paired_proxy_compiled(wk,scale=1,repetitions=2,seed=1)
    started=time.perf_counter(); rows=[]; block_rows=[]; slope_rows=[]; slope_blocks=[]; hits=0; cell_no=0
    for date_index,date,source_name,source_sha,graph,boundary in _sources(snapshot_root,current_source):
        for mode_index,mode in enumerate(MODES):
            sub=extract_connected_subgraph(graph,source_sha,mode=mode,node_count=31); anchor_block=[]; anchor_drifts=[]; increment_reference=None; hotspot_drift=None
            for weight_index,weight in enumerate(WEIGHTS):
                cell_no+=1; kernel,meta=build_interpolated_snapshot_kernel(sub,hotspot_weight=weight); increment_sha=hashlib.sha256(kernel.increments.tobytes()).hexdigest(); increment_reference=increment_reference or increment_sha
                if increment_sha!=increment_reference: raise AssertionError("increments changed across lambda")
                if weight==1: hotspot_drift=kernel.drift.copy()
                anchor_drifts.append(kernel.drift.copy())
                seed=SEED_BASES[stage]+date_index*1000+mode_index*100+weight_index; cell_id=f"{date}-{mode}-lambda{weight:g}-N40"; checkpoint=raw/f"{cell_no:02d}-{cell_id}.npz"
                c,p,runtime,reused=_load_or_run(checkpoint,kernel,repetitions=repetitions,seed=seed,source_sha=source_sha,increment_sha=increment_sha,weight=weight); hits+=int(reused)
                path_summary=summarize_preflight_cell(c,p,scale=SCALE,comparisons=CELL_COUNT); means,bsummary=block_difference_summary(c,p,scale=SCALE,block_size=block_size,comparisons=CELL_COUNT); anchor_block.append(means)
                row={"cell_id":cell_id,"date":date,"mode":mode,"source":source_name,"source_sha256":source_sha,"claim_boundary":boundary,"hotspot_weight":weight,"scale":SCALE,"seed":seed,"repetitions":repetitions,"node_count":sub.number_of_nodes(),"channel_count":sub.number_of_edges(),"route_count":meta["route_count"],"increment_sha256":increment_sha,"maximum_absolute_drift":meta["maximum_absolute_drift"],**path_summary,**bsummary,"censored_count":0,"runtime_seconds":runtime,"raw_file":checkpoint.relative_to(output).as_posix(),"raw_sha256":_sha256(checkpoint)}; rows.append(row)
                for bi,v in enumerate(means): block_rows.append({"cell_id":cell_id,"block_index":bi,"normalized_mean_difference":float(v)})
                print(f"[{cell_no:02d}/{CELL_COUNT}] {stage} {cell_id} runtime={runtime:.2f}s reused={reused} effect={bsummary['block_mean_difference']:.5f}",flush=True)
            matrix=np.stack(anchor_block); slopes,summary=summarize_anchor_slope(matrix); anchor_id=f"{date}-{mode}"
            affine_residual=max(float(np.max(np.abs((w*hotspot_drift)-drift))) for w,drift in zip(WEIGHTS,anchor_drifts))
            slope_rows.append({"anchor_id":anchor_id,"date":date,"mode":mode,"block_count":BLOCK_COUNT,**summary,"affine_drift_residual":affine_residual})
            for bi,v in enumerate(slopes): slope_blocks.append({"anchor_id":anchor_id,"block_index":bi,"slope":float(v)})
    if len(rows)!=CELL_COUNT or len(slope_rows)!=ANCHOR_COUNT: raise AssertionError("formal interpolation grid incomplete")
    prefix=f"drift-interpolation-{stage}"; _write_csv(output/f"{prefix}.csv",rows); _write_csv(output/f"{prefix}-blocks.csv",block_rows); _write_csv(output/f"{prefix}-slopes.csv",slope_rows); _write_csv(output/f"{prefix}-slope-blocks.csv",slope_blocks)
    max_slope_hw=max(float(r["slope_ci_halfwidth"]) for r in slope_rows); grand=np.mean(np.stack([np.array([r["slope"] for r in slope_blocks if r["anchor_id"]==a["anchor_id"]]) for a in slope_rows]),axis=0); gm=float(grand.mean()); gse=float(grand.std(ddof=1)/math.sqrt(BLOCK_COUNT)); gc=float(student_t.ppf(.975,BLOCK_COUNT-1)); gh=gc*gse
    metadata={"artifact_kind":f"drift-interpolation-{stage}","cell_count":CELL_COUNT,"anchor_count":ANCHOR_COUNT,"repetitions_per_cell":repetitions,"block_size":block_size,"block_count":BLOCK_COUNT,"checkpoint_hits":hits,"censored_count":0,"unique_seed_count":len({r['seed'] for r in rows}),"maximum_anchor_slope_ci_halfwidth":max_slope_hw,"slope_precision_target":.03,"slope_precision_gate_pass":max_slope_hw<=.03,"fixed_anchor_mean_slope":gm,"fixed_anchor_mean_slope_ci_low":gm-gh,"fixed_anchor_mean_slope_ci_high":gm+gh,"maximum_affine_drift_residual":max(r["affine_drift_residual"] for r in slope_rows),"sum_cell_runtime_seconds":sum(r["runtime_seconds"] for r in rows),"wall_runtime_seconds":time.perf_counter()-started,"software":{"python":platform.python_version(),"numpy":np.__version__,"scipy":scipy.__version__,"networkx":nx.__version__,"numba":numba.__version__}}
    (output/f"{prefix}-metadata.json").write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); files=sorted(p for p in output.rglob("*") if p.is_file()); (output/"SHA256SUMS.txt").write_text("".join(f"{_sha256(p)}  {p.relative_to(output).as_posix()}\n" for p in files),encoding="utf-8"); return metadata


def main():
    p=argparse.ArgumentParser(); p.add_argument("--stage",choices=tuple(SEED_BASES),required=True); p.add_argument("--snapshot-root",type=Path,default=Path("data/raw/ln-geolocated-2019-2023/selected_snapshots")); p.add_argument("--current-source",type=Path,default=Path("data/raw/mempool-lightning-2026-07-22/channels-geo.json")); p.add_argument("--output",type=Path,required=True); p.add_argument("--repetitions",type=int,default=36560); p.add_argument("--block-size",type=int,default=914); a=p.parse_args(); print(json.dumps(run_stage(a.snapshot_root,a.current_source,a.output,stage=a.stage,repetitions=a.repetitions,block_size=a.block_size),ensure_ascii=False,indent=2))


if __name__=="__main__": main()
