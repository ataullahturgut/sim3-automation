from __future__ import annotations
import io, json, os, re, subprocess, time, zipfile
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
OUTJ=AX/"GOLD_H3_HISTORICAL_FUTURES_ARCHIVE_RECOVERY_AUDIT_2026-10-05.json"
OUTM=AX/"GOLD_H3_HISTORICAL_FUTURES_ARCHIVE_RECOVERY_AUDIT_2026-10-05.md"

TOKENS=["GC=F","SI=F","NQ=F","ZN=F","CL=F"]
ALT_TOKENS=["GC","SI","NQ","ZN","CL"]
PATH_RX=re.compile(r"(hour|1h|futures|llrs|ifbc|panel|cache|backfill|intraday|gc|si|nq|zn|cl)",re.I)
TEXT_EXT={".py",".md",".txt",".csv",".json",".yml",".yaml",".tsv",".log"}
MAX_BLOB=12_000_000
MAX_ARTIFACT_BYTES=120_000_000

def sh(*args,timeout=180):
    p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,timeout=timeout)
    return p.returncode,p.stdout,p.stderr

def scan_git_history():
    rc,out,err=sh("git","fetch","origin","+refs/heads/*:refs/remotes/origin/*","--prune",timeout=180)
    fetch_ok=(rc==0)
    rc,objects,err2=sh("git","rev-list","--all","--objects",timeout=180)
    if rc!=0:
        raise RuntimeError("rev-list failed: "+err2[-1000:])
    by_blob={}
    for line in objects.splitlines():
        parts=line.split(" ",1)
        sha=parts[0]; path=parts[1] if len(parts)>1 else ""
        if not path: continue
        ext=Path(path).suffix.lower()
        if ext not in TEXT_EXT or not PATH_RX.search(path): continue
        by_blob.setdefault(sha,set()).add(path)

    candidates=[]; exact_data_candidates=[]
    for sha,paths in by_blob.items():
        rc,size_s,_=sh("git","cat-file","-s",sha,timeout=20)
        if rc!=0: continue
        try:size=int(size_s.strip())
        except:continue
        if size>MAX_BLOB: continue
        rc,content,_=sh("git","cat-file","-p",sha,timeout=60)
        if rc!=0: continue
        token_hits=[t for t in TOKENS if t in content]
        has_2023="2023-" in content; has_2024="2024-" in content
        first=content[:5000]
        alt_hits=[t for t in ALT_TOKENS if re.search(rf"(^|[,;_\s]){re.escape(t)}([,;_\s]|$)",first)]
        if len(token_hits)>=2 or (len(alt_hits)>=4 and (has_2023 or has_2024)):
            rec={"blob":sha,"size":size,"paths":sorted(paths)[:20],"token_hits":token_hits,
                 "alt_header_hits":alt_hits,"has_2023_text":has_2023,"has_2024_text":has_2024,
                 "head":content[:1200]}
            candidates.append(rec)
            if ((len(token_hits)>=4) or (len(alt_hits)>=5)) and (has_2023 or has_2024):
                exact_data_candidates.append(rec)

    path_hits=[]
    for line in objects.splitlines():
        parts=line.split(" ",1)
        if len(parts)<2: continue
        path=parts[1]
        if re.search(r"(LLRS|IFBC|FUTURES|HOURLY.*PANEL|PANEL.*HOURLY|GC.*SI|SI.*GC)",path,re.I):
            path_hits.append(path)
    return {"fetch_all_branches_ok":fetch_ok,"unique_text_blobs_scanned":len(by_blob),
            "strong_content_candidates":candidates[:300],
            "exact_old_five_channel_data_candidates":exact_data_candidates[:100],
            "strong_path_hits":sorted(set(path_hits))[:1000]}

def gh_headers():
    tok=os.environ.get("GITHUB_TOKEN","").strip()
    if not tok: raise RuntimeError("GITHUB_TOKEN missing")
    return {"Authorization":f"Bearer {tok}","Accept":"application/vnd.github+json",
            "X-GitHub-Api-Version":"2022-11-28","User-Agent":"gold-h3-archive-audit/1.0"}

def list_artifacts():
    repo=os.environ.get("GITHUB_REPOSITORY","ataullahturgut/sim3-automation")
    h=gh_headers(); allarts=[]
    for page in range(1,21):
        r=requests.get(f"https://api.github.com/repos/{repo}/actions/artifacts",
                       headers=h,params={"per_page":100,"page":page},timeout=45)
        if r.status_code!=200:
            return {"http":r.status_code,"error":r.text[:500],"artifacts":[]}
        j=r.json(); batch=j.get("artifacts") or []; allarts.extend(batch)
        if len(batch)<100: break
    return {"http":200,"total":len(allarts),"artifacts":allarts}

def inspect_zip_bytes(raw:bytes):
    z=zipfile.ZipFile(io.BytesIO(raw)); members=z.namelist()
    matching=[]; strong=[]
    for name in members:
        if not PATH_RX.search(name): continue
        info=z.getinfo(name); matching.append({"name":name,"size":info.file_size})
        if info.file_size>MAX_BLOB or Path(name).suffix.lower() not in TEXT_EXT: continue
        try: txt=z.read(name).decode("utf-8","ignore")
        except Exception: continue
        token_hits=[t for t in TOKENS if t in txt]
        first=txt[:5000]
        alt_hits=[t for t in ALT_TOKENS if re.search(rf"(^|[,;_\s]){re.escape(t)}([,;_\s]|$)",first)]
        has23="2023-" in txt; has24="2024-" in txt
        if len(token_hits)>=2 or (len(alt_hits)>=4 and (has23 or has24)):
            strong.append({"name":name,"size":info.file_size,"token_hits":token_hits,
                           "alt_header_hits":alt_hits,"has_2023_text":has23,
                           "has_2024_text":has24,"head":txt[:1200]})
    return {"members_n":len(members),"matching_members":matching[:500],"strong_members":strong[:100]}

def scan_artifacts():
    listing=list_artifacts(); arts=listing.get("artifacts",[])
    meta=[]; inspected=[]
    name_rx=re.compile(r"(gold|h3|hour|llrs|ifbc|futures|backfill|source|short|intraday)",re.I)
    h=gh_headers()
    relevant=[a for a in arts if name_rx.search(str(a.get("name","")))]
    for a in relevant:
        rec={"id":a.get("id"),"name":a.get("name"),"size_in_bytes":a.get("size_in_bytes"),
             "expired":a.get("expired"),"created_at":a.get("created_at"),
             "updated_at":a.get("updated_at"),"workflow_run":a.get("workflow_run")}
        meta.append(rec)
    # Prioritize artifacts whose names themselves suggest hourly/futures state.
    downloadable=[a for a in relevant if not a.get("expired") and int(a.get("size_in_bytes") or 0)<=MAX_ARTIFACT_BYTES]
    downloadable.sort(key=lambda a:(0 if re.search(r"(hour|llrs|ifbc|futures|backfill)",str(a.get("name","")),re.I) else 1,
                                    str(a.get("created_at",""))))
    for a in downloadable[:120]:
        rec={"id":a.get("id"),"name":a.get("name"),"size_in_bytes":a.get("size_in_bytes"),
             "expired":a.get("expired"),"created_at":a.get("created_at"),
             "updated_at":a.get("updated_at"),"workflow_run":a.get("workflow_run")}
        try:
            rr=requests.get(a.get("archive_download_url"),headers=h,timeout=90)
            if rr.status_code!=200:
                inspected.append({**rec,"download_http":rr.status_code}); continue
            inspected.append({**rec,"download_http":200,**inspect_zip_bytes(rr.content)})
        except Exception as e:
            inspected.append({**rec,"download_error":repr(e)})
    return {"list_http":listing.get("http"),"repo_artifact_total":listing.get("total",len(arts)),
            "relevant_artifact_metadata":meta[:1000],"nonexpired_relevant_inspected":inspected}

def main():
    git=scan_git_history(); art=scan_artifacts()
    artifact_strong=[]
    for a in art.get("nonexpired_relevant_inspected",[]):
        for m in a.get("strong_members",[]):
            artifact_strong.append({"artifact_id":a.get("id"),"artifact_name":a.get("name"),**m})
    exact_art=[x for x in artifact_strong if
               (len(x.get("token_hits",[]))>=4 or len(x.get("alt_header_hits",[]))>=5)
               and (x.get("has_2023_text") or x.get("has_2024_text"))]
    result={"schema":"GOLD_H3_HISTORICAL_FUTURES_ARCHIVE_RECOVERY_AUDIT_V1","date":"2026-10-05",
            "git_history":git,"actions_artifacts":art,"artifact_strong_candidates":artifact_strong,
            "artifact_exact_old_five_channel_candidates":exact_art}
    exact_git=git.get("exact_old_five_channel_data_candidates",[])
    result["exact_old_five_channel_candidate_found"]=bool(exact_git or exact_art)
    result["conclusion"]=("OLD_FIVE_CHANNEL_CANDIDATE_FOUND_REQUIRES_VALIDATION"
                          if result["exact_old_five_channel_candidate_found"]
                          else "NO_2023_2024_FIVE_CHANNEL_RAW_PANEL_FOUND_IN_GIT_OR_RETAINED_RELEVANT_ARTIFACTS")
    OUTJ.write_text(json.dumps(result,indent=2,default=str)+"\n",encoding="utf-8")
    lines=["# GOLD H3 — Historical Futures Archive Recovery Audit","",
           f"**Conclusion:** **{result['conclusion']}**","",
           "## Repository-wide Git history",
           f"- all branches fetch: **{git['fetch_all_branches_ok']}**",
           f"- unique candidate text blobs scanned: **{git['unique_text_blobs_scanned']}**",
           f"- strong content candidates: **{len(git['strong_content_candidates'])}**",
           f"- exact old five-channel candidates: **{len(git['exact_old_five_channel_data_candidates'])}**","",
           "## Git exact candidates"]
    if exact_git:
        for x in exact_git:
            lines.append(f"- paths={x['paths']} tokens={x['token_hits']} 2023={x['has_2023_text']} 2024={x['has_2024_text']} size={x['size']}")
    else:
        lines.append("- None found.")
    lines += ["","## Git paths with strong historical-hourly naming"]
    for p in git.get("strong_path_hits",[])[:120]: lines.append("- "+p)
    lines += ["","## GitHub Actions artifacts",
              f"- repository artifacts enumerated: **{art.get('repo_artifact_total',0)}**",
              f"- relevant artifact metadata rows: **{len(art.get('relevant_artifact_metadata',[]))}**",
              f"- non-expired relevant artifacts inspected: **{len(art.get('nonexpired_relevant_inspected',[]))}**",
              f"- strong archive members: **{len(artifact_strong)}**",
              f"- exact old five-channel archive candidates: **{len(exact_art)}**",""]
    if exact_art:
        for x in exact_art[:50]:
            lines.append(f"- artifact {x['artifact_id']} {x['artifact_name']} -> {x['name']} tokens={x.get('token_hits')} 2023={x.get('has_2023_text')} 2024={x.get('has_2024_text')}")
    else:
        lines.append("- No retained relevant artifact contained a 2023/2024 five-channel raw panel signature.")
    lines += ["","## Governance note",
              "Archive recovery only. No proxy substitution and no frozen DPTC/LLRS/IFBC model change."]
    OUTM.write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(OUTM.read_text())

if __name__=="__main__":
    main()
