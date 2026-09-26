"""Synthetic interface contract; never used as forecast performance evidence."""
import numpy as np
import gpr_experiment_v1 as e

def run():
 rng=np.random.default_rng(8);X=rng.normal(size=(35,8));Y=rng.normal(size=(35,4))
 for method in sum(e.r.BATCHES,[]):
  obj=e.Objective();mod,fn=e.adapter(method,obj)
  t,s=fn(X[:27],Y[:27],977,1,center=e.gp.PRIOR.copy(),Xv=X[27:],Yv=Y[27:],refit=False)
  assert len(t)==22 and np.isfinite(s),method
 print('PASS all32 GP adapters')
 import gpr_stage3a_v1 as a
 for method in a.METHODS:
  obj=e.Objective();mod,fn=a.optimizer(method,obj)
  t,s=fn(X[:27],Y[:27],977,1,center=e.gp.PRIOR.copy(),Xv=X[27:],Yv=Y[27:],refit=False)
  assert len(t)==22 and np.isfinite(s),method
 print('PASS all6 mandatory GP refinement interfaces')
 import gpr_stage3b_v1 as b
 for method in ['MPA_SCA','MPA_GA','MPA_CPA']:
  obj=e.Objective();mod,fn=b.adapter(method,obj)
  t,s=fn(X[:27],Y[:27],977,1,center=e.gp.PRIOR.copy(),Xv=X[27:],Yv=Y[27:],refit=False)
  assert len(t)==22 and np.isfinite(s),method
 print('PASS conditional GP hybrid interfaces; no production opening implied')
if __name__=='__main__':run()
