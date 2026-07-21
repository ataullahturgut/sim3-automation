from __future__ import annotations
import argparse, ctypes, json, os, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent
STATE_PATH=ROOT/"state.json"
STEPS=["GPT görevi/cevabı bekleniyor","Görev yakalanıyor","Codex'e gönderiliyor","Codex çalışıyor","Rapor üretiliyor","Rapor GPT'ye yükleniyor"]

def load_state():
    try:
        value=json.loads(STATE_PATH.read_text(encoding="utf-8"))
        return value if isinstance(value,dict) else {}
    except Exception:return {}

def atomic_write(data):
    fd,temp=tempfile.mkstemp(prefix="state_",suffix=".json.tmp",dir=str(ROOT))
    try:
        with os.fdopen(fd,"w",encoding="utf-8",newline="\n") as h:
            json.dump(data,h,ensure_ascii=False,indent=2);h.flush();os.fsync(h.fileno())
        os.replace(temp,STATE_PATH)
    finally:
        try:
            if os.path.exists(temp):os.unlink(temp)
        except OSError:pass

def common(state,args):
    if getattr(args,"task_id",""):state["active_task_id"]=args.task_id
    if getattr(args,"task_title",""):state["active_task_title"]=args.task_title
    if getattr(args,"elapsed",""):state["elapsed_text"]=args.elapsed

def notify():
    if os.name=="nt":
        try:ctypes.windll.user32.MessageBeep(0x10)
        except Exception:pass

def stage(args):
    state=load_state();n=max(1,min(args.stage,6))
    state.update(overall_status="running",state_label="RUNNING",needs_attention=False,cycle_stage=n,cycle_stage_label=STEPS[n-1],stop_reason="",steps=STEPS)
    common(state,args);atomic_write(state)

def running(args):
    state=load_state();state.update(overall_status="running",state_label="RUNNING",needs_attention=False,stop_reason="",diagnostic_file="",report_path="",steps=STEPS)
    common(state,args);atomic_write(state)

def stopped(args):
    state=load_state();n=max(1,min(args.stage,6))
    state.update(overall_status="stopped",state_label="DURDU",needs_attention=True,cycle_stage=n,cycle_stage_label=STEPS[n-1],stop_reason=args.reason,diagnostic_file=args.diagnostic or "",report_path=args.report or "",steps=STEPS)
    common(state,args);atomic_write(state);notify()

def parser():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest="command",required=True)
    parent=argparse.ArgumentParser(add_help=False)
    parent.add_argument("--task-id",default="");parent.add_argument("--task-title",default="");parent.add_argument("--elapsed",default="")
    s=sub.add_parser("stage",parents=[parent]);s.add_argument("stage",type=int);s.set_defaults(func=stage)
    r=sub.add_parser("running",parents=[parent]);r.set_defaults(func=running)
    x=sub.add_parser("stopped",parents=[parent]);x.add_argument("stage",type=int);x.add_argument("--reason",required=True);x.add_argument("--diagnostic",default="");x.add_argument("--report",default="");x.set_defaults(func=stopped)
    return p
if __name__=="__main__":
    a=parser().parse_args();a.func(a)
