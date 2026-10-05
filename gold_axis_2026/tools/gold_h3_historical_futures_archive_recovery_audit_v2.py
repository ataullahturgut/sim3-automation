from __future__ import annotations
import io, json, os, re, subprocess, zipfile
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
OUTJ=AX/"GOLD_H3_HISTORICAL_FUTURES_ARCHIVE_RECOVERY_AUDIT_V2_2026-10-05.json"
OUTM=AX/"GOLD_H3_HISTORICAL_FUTURES_ARCHIVE_RECOVERY_AUDIT_V2_2026-10-05.md"

CHANNELS=["GC","SI","NQ","ZN","CL"]
DATA_EXT={".csv",".tsv",".json",".txt"}
MAX_BLOB=25_000_000
MAX_ART=80_000_000
DATE_RX=re.compile(r"202[34]-\d\d-\d\d")

def sh(*args,timeout=180):
    p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,timeout=timeout)
    return p.returncode,p.stdout,p.stderr

def channel_hits_header(head):
    # Accept canonical raw-panel names or derived-prefixed names, but all five must exist.
    hits=[]
    for c in CHANNELS:
        if re.search(rf'(^|[,;"\s_]){c}([,;"\s_]|$)',head,re.I) or re.search(rf'(^|[,;"\s_]){c}_(close|price|r1|r3|r6|volume)',head,re.I):
            hits.append(c)
    return hits

def data_signature(txt):
    head=txt[:12000]
    hits=channel_hits_header(head)
    dates=DATE_RX.findall(txt)
    old23=any(d.startswith("2023-") for d in dates)
    old24=any(d.startswith("2024-") for d in dates)
    # A real old panel should have many dated records, not just one date in metadata.
    data_like=len(dates)>=20 and len(hits)>=5
    return {"channel_hits":hits,"date_count_2023_2024":len(dates),
            "has_2023":old23,"has_2024":old24,"data_like":data_like}

def scan_git():
    rc,_,err=sh("git","fetch","origin","+refs/heads/*:refs/remotes/origin/*","--prune",timeout=180)
    fetch_ok=rc==0
    rc,obj,err=sh("git","rev-list","--all","--objects",timeout=180)
    if rc!=0: raise RuntimeError(err[-1000:])
    blobs={}
    for line in obj.splitlines():
        parts=line.split(" ",1)
        if len(parts)<2: continue
        sha,path=parts
        ext=Path(path).suffix.lower()
        if ext in DATA_EXT:
            blobs.setdefault(sha,set()).add(path)
    candidates=[]; lfs_pointers=[]
    for sha,paths in blobs.items():
        rc,sz,_=sh("git","cat-file","-s",sha,timeout=20)
        if rc: continue
        try:size=int(sz.strip())
        except:continue
        if size>MAX_BLOB: continue
        rc,txt,_=sh("git","cat-file","-p",sha,timeout=60)
        if rc: continue
        if txt.startswith("version https://git-lfs.github.com/spec/v1"):
            lfs_pointers.append({"blob":sha,"paths":sorted(paths)[:10],"size":size})
            continue
        sig=data_signature(txt)
        if sig["data_like"]:
            candidates.append({"blob":sha,"paths":sorted(paths)[:20],"size":size,**sig,
                               "head":txt[:1000]})
    return {"fetch_all_branches_ok":fetch_ok,"data_blobs_scanned":len(blobs),
            "old_five_channel_data_candidates":candidates,
            "lfs_pointer_candidates":lfs_pointers}

def headers():
    tok=os.environ["GITHUB_TOKEN"]
    return {"Authorization":f"Bearer {tok}","Accept":"application/vnd.github+json",
            "X-GitHub-Api-Version":"2022-11-28","User-Agent":"gold-h3-archive-v2/1.0"}

def list_artifacts():
    repo=os.environ["GITHUB_REPOSITORY"]; h=headers(); out=[]
    for page in range(1,30):
        r=requests.get(f"https://api.github.com/repos/{repo}/actions/artifacts",headers=h,
                       params={"per_page":100,"page":page},timeout=45)
        r.raise_for_status()
        b=r.json().get("artifacts") or []; out.extend(b)
        if len(b)<100: break
    return out

def inspect_artifact(a):
    rec={"id":a.get("id"),"name":a.get("name"),"expired":a.get("expired"),
         "size_in_bytes":a.get("size_in_bytes"),"created_at":a.get("created_at"),
         "head_branch":(a.get("workflow_run") or {}).get("head_branch"),
         "strong_members":[]}
    r=requests.get(a["archive_download_url"],headers=headers(),timeout=90)
    rec["http"]=r.status_code
    if r.status_code!=200: return rec
    try:z=zipfile.ZipFile(io.BytesIO(r.content))
    except Exception:return rec
    rec["members_n"]=len(z.namelist())
    for name in z.namelist():
        ext=Path(name).suffix.lower()
        if ext not in DATA_EXT: continue
        info=z.getinfo(name)
        if info.file_size>MAX_BLOB: continue
        try:txt=z.read(name).decode("utf-8","ignore")
        except:continue
        sig=data_signature(txt)
        if sig["data_like"]:
            rec["strong_members"].append({"name":name,"size":info.file_size,**sig,"head":txt[:1000]})
    return rec

def scan_artifacts():
    arts=list_artifacts()
    selected=[]
    strong_rx=re.compile(r"(hour|1h|llrs|ifbc|futures|backfill|source.?bridge)",re.I)
    h3_rx=re.compile(r"gold-h3",re.I)
    for a in arts:
        if a.get("expired"): continue
        if int(a.get("size_in_bytes") or 0)>MAX_ART: continue
        name=str(a.get("name") or "")
        branch=str((a.get("workflow_run") or {}).get("head_branch") or "")
        created=str(a.get("created_at") or "")
        if strong_rx.search(name+" "+branch) or (h3_rx.search(branch) and created>="2026-10-02"):
            selected.append(a)
    # inspect all tightly selected artifacts; if huge, newest 300
    selected=sorted(selected,key=lambda a:str(a.get("created_at") or ""),reverse=True)[:300]
    inspected=[]; found=[]
    for a in selected:
        rec=inspect_artifact(a); inspected.append(rec)
        for m in rec.get("strong_members",[]):
            found.append({"artifact_id":rec["id"],"artifact_name":rec["name"],
                          "head_branch":rec["head_branch"],**m})
    return {"repo_artifact_total":len(arts),"selected_nonexpired":len(selected),
            "inspected":len(inspected),"old_five_channel_data_candidates":found,
            "selected_metadata":[{"id":a.get("id"),"name":a.get("name"),
                                  "created_at":a.get("created_at"),
                                  "head_branch":(a.get("workflow_run") or {}).get("head_branch"),
                                  "size_in_bytes":a.get("size_in_bytes")} for a in selected]}

def main():
    g=scan_git(); a=scan_artifacts()
    found=g["old_five_channel_data_candidates"]+a["old_five_channel_data_candidates"]
    conclusion="RAW_2023_2024_FIVE_CHANNEL_PANEL_FOUND_REQUIRES_SOURCE_VALIDATION" if found else "NO_RAW_2023_2024_FIVE_CHANNEL_PANEL_FOUND"
    out={"schema":"GOLD_H3_HISTORICAL_FUTURES_ARCHIVE_RECOVERY_AUDIT_V2",
         "date":"2026-10-05","conclusion":conclusion,"git":g,"artifacts":a}
    OUTJ.write_text(json.dumps(out,indent=2,default=str)+"\n")
    lines=["# GOLD H3 — Historical Futures Archive Recovery Audit V2","",
           f"**Conclusion:** **{conclusion}**","",
           "V2 corrects V1 false positives by excluding source code/docs and requiring a data-like file with all five channel names plus at least 20 dated 2023/2024 records.","",
           "## Git history",
           f"- all branches fetched: **{g['fetch_all_branches_ok']}**",
           f"- unique CSV/TSV/JSON/TXT blobs scanned: **{g['data_blobs_scanned']}**",
           f"- raw old five-channel candidates: **{len(g['old_five_channel_data_candidates'])}**",
           f"- LFS pointer candidates: **{len(g['lfs_pointer_candidates'])}**"]
    for x in g["old_five_channel_data_candidates"][:30]:
        lines.append(f"- {x['paths']} channels={x['channel_hits']} dates={x['date_count_2023_2024']} 2023={x['has_2023']} 2024={x['has_2024']}")
    lines += ["","## Retained Actions artifacts",
              f"- repository artifacts enumerated: **{a['repo_artifact_total']}**",
              f"- tightly relevant non-expired artifacts selected: **{a['selected_nonexpired']}**",
              f"- inspected: **{a['inspected']}**",
              f"- raw old five-channel members found: **{len(a['old_five_channel_data_candidates'])}**"]
    for x in a["old_five_channel_data_candidates"][:30]:
        lines.append(f"- artifact {x['artifact_id']} {x['artifact_name']} / {x['name']} channels={x['channel_hits']} dates={x['date_count_2023_2024']}")
    lines += ["","## Scientific interpretation",
              "- Python scripts that merely mention GC=F/SI=F/NQ=F/ZN=F/CL=F are not counted as data.",
              "- A candidate is counted only when the actual stored data body has all five channels and repeated 2023/2024 date records.",
              "- No model thresholds or DPTC rules are changed by this audit."]
    OUTM.write_text("\n".join(lines)+"\n")
    print(OUTM.read_text())

if __name__=="__main__":
    main()
