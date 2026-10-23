"""Inspect *original downloaded* official GPR legacy XLS and World Bank XLSX.

Describes sheet, columns and sample month rows without inferring a series
from a misleading heading. Never modifies a source workbook or Neon.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
import pandas as pd

def probe_xls(path):
    file=pd.ExcelFile(path,engine="xlrd")
    out=[]
    for sheet in file.sheet_names:
        df=pd.read_excel(file,sheet_name=sheet,header=None,nrows=14)
        filled=[]
        for i in range(min(len(df),14)):
            cells=[{"col":int(j),"text":str(v)[:110]} for j,v in enumerate(df.iloc[i].tolist()) if not pd.isna(v)]
            if cells:filled.append({"excel_row":i+1,"first_cells":cells[:24]})
        out.append({"sheet":sheet,"columns":len(df.columns),"rows_first14":filled[:8]})
    return {"file":Path(path).name,"sheet_count":len(out),"sheets":out}

def probe_wb(path):
    file=pd.ExcelFile(path,engine="openpyxl")
    out=[]
    for sheet in file.sheet_names:
        df=pd.read_excel(file,sheet_name=sheet,header=None,nrows=18)
        filled=[]
        for i in range(min(len(df),18)):
            cells=[{"col":int(j),"text":str(v)[:110]} for j,v in enumerate(df.iloc[i].tolist()) if not pd.isna(v)]
            if cells:filled.append({"excel_row":i+1,"first_cells":cells[:24]})
        out.append({"sheet":sheet,"columns":len(df.columns),"rows_first18":filled[:12]})
    return {"file":Path(path).name,"sheet_count":len(out),"sheets":out}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--gpr-sep",required=True)
    p.add_argument("--gpr-oct",required=True)
    p.add_argument("--wb",required=True)
    p.add_argument("--report",required=True)
    a=p.parse_args()
    out={"gpr_september":probe_xls(a.gpr_sep),
         "gpr_october":probe_xls(a.gpr_oct),
         "world_bank":probe_wb(a.wb)}
    Path(a.report).write_text(json.dumps(out,indent=2,default=str)+chr(10))
    print("OFFICIAL_WORKBOOK_STRUCTURE_INSPECTION=PASS")
    print(json.dumps(out,default=str))
if __name__=="__main__":main()
