"""Compare and pool formal/replication drift-interpolation gradients."""
from __future__ import annotations
import argparse,csv,hashlib,json,math,platform
from pathlib import Path
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
from scipy.stats import t as student_t
from lightning_real_topology_comparison import welch_block_comparison

ANCHORS=8; BLOCKS=40; WEIGHTS=(0.0,.25,.5,.75,1.0); PRECISION=.03


def _sha(path):
    h=hashlib.sha256(); h.update(Path(path).read_bytes()); return h.hexdigest()


def _manifest(root):
    lines=(root/'SHA256SUMS.txt').read_text().splitlines()
    for line in lines:
        h,n=line.split('  ',1)
        if _sha(root/n)!=h: raise ValueError(f"manifest mismatch: {root/n}")
    return len(lines)


def _rows(path):
    with Path(path).open(encoding='utf-8',newline='') as f: return list(csv.DictReader(f))


def _group(rows,key,value):
    out={}
    for r in rows: out.setdefault(r[key],[]).append((int(r['block_index']),float(r[value])))
    result={}
    for k,v in out.items():
        v.sort()
        if [i for i,_ in v]!=list(range(len(v))): raise ValueError(f"noncontiguous blocks: {k}")
        result[k]=np.array([x for _,x in v])
    return result


def pooled_summary(formal,replication,*,comparisons=ANCHORS):
    f=np.asarray(formal,float); r=np.asarray(replication,float)
    if f.shape!=(BLOCKS,) or r.shape!=(BLOCKS,) or not np.all(np.isfinite(f)) or not np.all(np.isfinite(r)): raise ValueError("pooled inputs must be finite 40-block vectors")
    x=np.concatenate([f,r]); mean=float(x.mean()); se=float(x.std(ddof=1)/math.sqrt(len(x))); critical=float(student_t.ppf(1-.05/(2*comparisons),len(x)-1)); hw=critical*se
    return {"pooled_slope":mean,"pooled_standard_error":se,"pooled_critical":critical,"pooled_ci_low":mean-hw,"pooled_ci_high":mean+hw,"pooled_ci_halfwidth":hw,"pooled_precision_gate_pass":hw<=PRECISION}


def _plot(comparison,curves,path):
    mpl.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Arial','Helvetica','DejaVu Sans'],'font.size':7,'axes.spines.right':False,'axes.spines.top':False,'svg.fonttype':'none','pdf.fonttype':42})
    blue,orange,grey='#4C78A8','#F28E2B','#777777'; fig,ax=plt.subplots(2,2,figsize=(183/25.4,122/25.4),constrained_layout=True)
    y=np.arange(len(comparison)); labels=[f"{d[:4]} {m}" for d,m in zip(comparison.date,comparison['mode'])]
    ax[0,0].errorbar(comparison.formal_slope,y-.08,xerr=comparison.formal_slope_ci_halfwidth,fmt='o',ms=3,capsize=2,color=blue,label='Formal')
    ax[0,0].errorbar(comparison.replication_slope,y+.08,xerr=comparison.replication_slope_ci_halfwidth,fmt='o',ms=3,capsize=2,color=orange,label='Replication')
    ax[0,0].axvline(0,color='black',lw=.7); ax[0,0].set_yticks(y,labels); ax[0,0].invert_yaxis(); ax[0,0].set_xlabel('Effect gradient per unit λ'); ax[0,0].set_title('a  Anchor gradients',loc='left',fontweight='bold'); ax[0,0].legend()
    ax[0,1].errorbar(curves.hotspot_weight,curves.pooled_mean,yerr=curves.pooled_ci_halfwidth,fmt='o-',ms=3,capsize=2,color=blue); ax[0,1].axhline(0,color='black',lw=.7); ax[0,1].set(xlabel='Hotspot weight λ',ylabel='Mean normalized effect',title='b  Fixed-anchor pooled curve')
    lo=min(comparison.formal_slope.min(),comparison.replication_slope.min())-.005; hi=max(comparison.formal_slope.max(),comparison.replication_slope.max())+.005; ax[1,0].plot([lo,hi],[lo,hi],'--',color=grey,lw=.8); ax[1,0].scatter(comparison.formal_slope,comparison.replication_slope,color=blue,s=18); ax[1,0].set(xlabel='Formal gradient',ylabel='Replication gradient',title='c  Replication consistency'); ax[1,0].set_aspect('equal',adjustable='box')
    for i,row in comparison.reset_index(drop=True).iterrows(): ax[1,1].scatter([i-.18,i,i+.18],[row.formal_slope_ci_halfwidth,row.replication_slope_ci_halfwidth,row.pooled_ci_halfwidth],c=[blue,orange,grey],s=14)
    ax[1,1].axhline(PRECISION,color='#C44E52',ls='--',lw=1,label='Target 0.03'); ax[1,1].set_xticks(range(len(labels)),[x.split()[0]+'\n'+x.split()[1] for x in labels],rotation=30,ha='right'); ax[1,1].set_ylabel('Simultaneous CI half-width'); ax[1,1].set_title('d  Precision audit',loc='left',fontweight='bold'); ax[1,1].legend()
    fig.savefig(path,dpi=600,bbox_inches='tight'); plt.close(fig)


def run(formal_dir,replication_dir,output):
    formal_dir=Path(formal_dir); replication_dir=Path(replication_dir); output=Path(output)
    if output.exists() and any(output.iterdir()): raise ValueError('output must be empty or absent')
    output.mkdir(parents=True,exist_ok=True); fm=_manifest(formal_dir); rm=_manifest(replication_dir)
    fs=pd.read_csv(formal_dir/'drift-interpolation-formal-slopes.csv'); rs=pd.read_csv(replication_dir/'drift-interpolation-replication-slopes.csv')
    if list(fs.anchor_id)!=list(rs.anchor_id) or len(fs)!=ANCHORS: raise ValueError('slope grids mismatch')
    fb=_group(_rows(formal_dir/'drift-interpolation-formal-slope-blocks.csv'),'anchor_id','slope'); rb=_group(_rows(replication_dir/'drift-interpolation-replication-slope-blocks.csv'),'anchor_id','slope')
    fseeds={int(r['seed']) for r in _rows(formal_dir/'drift-interpolation-formal.csv')}; rseeds={int(r['seed']) for r in _rows(replication_dir/'drift-interpolation-replication.csv')}
    if not fseeds.isdisjoint(rseeds): raise ValueError('stage seeds overlap')
    rows=[]
    for _,fr in fs.iterrows():
        aid=fr.anchor_id; rr=rs[rs.anchor_id==aid].iloc[0]; direct=welch_block_comparison(fb[aid],rb[aid],comparisons=ANCHORS); pooled=pooled_summary(fb[aid],rb[aid])
        rows.append({'anchor_id':aid,'date':fr.date,'mode':fr['mode'],'formal_slope':fr.slope,'formal_slope_ci_low':fr.slope_ci_low,'formal_slope_ci_high':fr.slope_ci_high,'formal_slope_ci_halfwidth':fr.slope_ci_halfwidth,'replication_slope':rr.slope,'replication_slope_ci_low':rr.slope_ci_low,'replication_slope_ci_high':rr.slope_ci_high,'replication_slope_ci_halfwidth':rr.slope_ci_halfwidth,**direct,**pooled})
    comp=pd.DataFrame(rows)
    fcell=_group(_rows(formal_dir/'drift-interpolation-formal-blocks.csv'),'cell_id','normalized_mean_difference'); rcell=_group(_rows(replication_dir/'drift-interpolation-replication-blocks.csv'),'cell_id','normalized_mean_difference')
    curves=[]
    for w in WEIGHTS:
        suffix=f'lambda{w:g}-N40'; fa=[v for k,v in fcell.items() if k.endswith(suffix)]; ra=[v for k,v in rcell.items() if k.endswith(suffix)]
        if len(fa)!=ANCHORS or len(ra)!=ANCHORS: raise ValueError('curve cell coverage mismatch')
        blocks=np.concatenate([np.mean(np.stack(fa),axis=0),np.mean(np.stack(ra),axis=0)]); mean=float(blocks.mean()); se=float(blocks.std(ddof=1)/math.sqrt(80)); crit=float(student_t.ppf(1-.05/(2*5),79)); hw=crit*se; curves.append({'hotspot_weight':w,'pooled_mean':mean,'pooled_standard_error':se,'pooled_ci_low':mean-hw,'pooled_ci_high':mean+hw,'pooled_ci_halfwidth':hw})
    curves=pd.DataFrame(curves)
    formal_grand=np.mean(np.stack(list(fb.values())),axis=0); replication_grand=np.mean(np.stack(list(rb.values())),axis=0); pooled_grand=pooled_summary(formal_grand,replication_grand,comparisons=1); direct_grand=welch_block_comparison(formal_grand,replication_grand,comparisons=1)
    metadata={'artifact_kind':'drift-interpolation-replication-comparison-and-pooled-sensitivity','anchor_count':ANCHORS,'formal_manifest_entries':fm,'replication_manifest_entries':rm,'seeds_disjoint':True,'all_direct_anchor_intervals_contain_zero':bool(comp.contains_zero.all()),'direct_anchor_failure_count':int((~comp.contains_zero).sum()),'formal_precision_gate_pass':bool((comp.formal_slope_ci_halfwidth<=PRECISION).all()),'replication_precision_gate_pass':bool((comp.replication_slope_ci_halfwidth<=PRECISION).all()),'pooled_precision_gate_pass':bool(comp.pooled_precision_gate_pass.all()),'formal_negative_anchor_count':int((comp.formal_slope<0).sum()),'replication_negative_anchor_count':int((comp.replication_slope<0).sum()),'pooled_negative_anchor_count':int((comp.pooled_slope<0).sum()),'formal_replication_slope_correlation':float(np.corrcoef(comp.formal_slope,comp.replication_slope)[0,1]),'fixed_anchor_direct_comparison':direct_grand,'fixed_anchor_pooled_sensitivity':pooled_grand,'claim_boundary':'finite average over eight frozen topology anchors; simulation uncertainty only','software':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__}}
    comp.to_csv(output/'drift-interpolation-replication-comparison.csv',index=False); curves.to_csv(output/'drift-interpolation-pooled-curves.csv',index=False); (output/'metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); _plot(comp,curves,output/'drift-interpolation-formal-replication.png'); files=sorted(p for p in output.iterdir() if p.name!='SHA256SUMS.txt'); (output/'SHA256SUMS.txt').write_text(''.join(f'{_sha(p)}  {p.name}\n' for p in files),encoding='utf-8'); return metadata


def main():
    p=argparse.ArgumentParser(); p.add_argument('--formal-dir',type=Path,default=Path('results/lightning-drift-interpolation-formal')); p.add_argument('--replication-dir',type=Path,default=Path('results/lightning-drift-interpolation-replication')); p.add_argument('--output',type=Path,default=Path('results/lightning-drift-interpolation-comparison')); a=p.parse_args(); print(json.dumps(run(a.formal_dir,a.replication_dir,a.output),ensure_ascii=False,indent=2))


if __name__=='__main__': main()
