function panel(d) {
 const rows=load("market").filter(x=>x.d.slice(0,10)<=d);
 const out={};for(const k of [...new Set(rows.map(x=>x.s))]){
 const a=rows.filter(x=>x.s===k);const z=a.at(-1);const p=a.at(-2);out[k]={d:z.d.slice(0,10),v:z.v,change:p?Math.round((z.v/p.v-1)*10000)/100:null};
 }store("panel_"+d,out);return out;
}

async function daysearch(d) {
 const dt=new Date(d+"T12:00:00Z");const label=dt.toLocaleDateString("en-US",{month:"short",day:"numeric",year:"numeric",timeZone:"UTC"});
 const r=await tools.mcp__codex_apps__search_service_web_run({system1_search_query:[{q:'gold Reuters "'+label.split(',')[0]+'" "2026" -sports',domains:['reuters.com']}],response_length:"long"});
 const raw=r.content.filter(x=>x.type==="text").map(x=>x.text).join("\n");
 const blocks=raw.split(/\n[-]{10,}\n/).filter(x=>x.split("\n")[0].includes(d)&&x.split("\n")[0].includes("reuters.com/")&&!x.split("\n")[0].includes("/sports/"));
 store("news_"+d,blocks);const score=x=>{const h=x.split("\n")[0];return /Trading Day:/.test(h)?6:/Gold /.test(h)?5:/global-markets-wrap/.test(h)?4:/global-markets/.test(h)?3:0;};
 text({date:d,panel:Object.fromEntries(Object.entries(eval("("+load("panelfn")+")")(d)).filter(([k,v])=>v.d===d).map(([k,v])=>[k,[v.v,v.change]])),sources:[...blocks].sort((a,b)=>score(b)-score(a)).slice(0,3).map(x=>x.slice(0,650)),excluded:raw.split(/\n[-]{10,}\n/).length-blocks.length});
}

async function record(action,reason,invalidation,coverage="daily_news_and_reconstructed_market") {
 const s=load("replay");const news=load("news_"+s.date)||[];
 if(action==="AL")s.pos=1;if(action==="SAT")s.pos=0;
 if((action==="TUT"&&s.pos!==1)||(action==="BEKLE"&&s.pos!==0))throw Error("position mismatch");
 const row={date:s.date,action,position_after:s.pos,reason,invalidation,coverage,sources:news.map(x=>x.split("\n")[0]),panel:load("panel_"+s.date)||null};
 s.ledger.push(row);
 await tools.apply_patch("*** Begin Patch\n*** Add File: "+s.base+"/days/"+s.date+".json\n+"+JSON.stringify(row,null,2).split("\n").join("\n+")+"\n*** End Patch");
 let next=new Date(s.date+"T12:00:00Z");next.setUTCDate(next.getUTCDate()+1);s.date=next.toISOString().slice(0,10);store("replay",s);
 text({saved:row.date,action,next:s.date,days:s.ledger.length});
}
