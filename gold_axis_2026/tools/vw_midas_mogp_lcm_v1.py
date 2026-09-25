from __future__ import annotations

import json, math, os, random
from pathlib import Path

import numpy as np
import torch
import gpytorch

import vw_midas_msvr_successor_v1 as base

DEV_START, DEV_END = "2022-04", "2024-12"
TRANSPORT_START, TRANSPORT_END = "2025-01", "2025-12"
STRESS_START, STRESS_END = "2026-01", "2026-07"
NUM_TASKS = 4

torch.set_default_dtype(torch.float64)

class ExactLCMGP(gpytorch.models.ExactGP):
    def __init__(self, train_x, train_y, likelihood, rank=1, q=1, kernel="RBF"):
        super().__init__(train_x, train_y, likelihood)
        self.mean_module = gpytorch.means.MultitaskMean(
            gpytorch.means.ConstantMean(), num_tasks=NUM_TASKS
        )
        d = train_x.shape[-1]
        bases = []
        for i in range(q):
            if kernel == "RBF":
                k = gpytorch.kernels.ScaleKernel(gpytorch.kernels.RBFKernel(ard_num_dims=d))
            elif kernel == "MATERN":
                k = gpytorch.kernels.ScaleKernel(gpytorch.kernels.MaternKernel(nu=1.5, ard_num_dims=d))
            elif kernel == "RBF_MATERN":
                k = (gpytorch.kernels.ScaleKernel(gpytorch.kernels.RBFKernel(ard_num_dims=d))
                     if i % 2 == 0 else
                     gpytorch.kernels.ScaleKernel(gpytorch.kernels.MaternKernel(nu=1.5, ard_num_dims=d)))
            else:
                raise ValueError(kernel)
            bases.append(k)
        self.covar_module = gpytorch.kernels.LCMKernel(
            bases, num_tasks=NUM_TASKS, rank=rank
        )

    def forward(self, x):
        return gpytorch.distributions.MultitaskMultivariateNormal(
            self.mean_module(x), self.covar_module(x)
        )

def arrays(samples, target):
    keys = sorted(k for k in samples if k < target)
    if len(keys) < 24:
        raise RuntimeError(f"TRAINING_ROWS_TOO_FEW {target} n={len(keys)}")
    X = np.stack([samples[k][0] for k in keys])
    Y = np.stack([samples[k][1] for k in keys])
    tx = samples[target][0][None, :]
    xm, xs, ym, ys = X.mean(0), X.std(0), Y.mean(0), Y.std(0)
    xs = np.where(xs < 1e-9, 1.0, xs)
    ys = np.where(ys < 1e-9, 1.0, ys)
    return keys, (X-xm)/xs, (Y-ym)/ys, (tx-xm)/xs, ym, ys

def fit_predict(samples, target, spec):
    rank, q, kernel, steps, lr = spec
    keys, X, Y, tx, ym, ys = arrays(samples, target)
    seed = 7301 + sum(ord(c) for c in target) + 100*rank + 10*q
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    train_x = torch.tensor(X)
    train_y = torch.tensor(Y)
    test_x = torch.tensor(tx)
    likelihood = gpytorch.likelihoods.MultitaskGaussianLikelihood(
        num_tasks=NUM_TASKS, rank=0
    )
    model = ExactLCMGP(train_x, train_y, likelihood, rank=rank, q=q, kernel=kernel)
    model.train(); likelihood.train()
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    mll = gpytorch.mlls.ExactMarginalLogLikelihood(likelihood, model)
    best_loss = float("inf")
    best_state = None
    stale = 0
    for _ in range(steps):
        opt.zero_grad()
        out = model(train_x)
        loss = -mll(out, train_y)
        if not torch.isfinite(loss):
            raise RuntimeError(f"NONFINITE_LOSS {target} {spec}")
        loss.backward()
        opt.step()
        lv = float(loss.detach())
        if lv < best_loss - 1e-6:
            best_loss = lv
            best_state = {k: v.detach().clone() for k,v in model.state_dict().items()}
            stale = 0
        else:
            stale += 1
        if stale >= 25:
            break
    if best_state is not None:
        model.load_state_dict(best_state)
    model.eval(); likelihood.eval()
    with torch.no_grad(), gpytorch.settings.fast_pred_var():
        predz = likelihood(model(test_x)).mean.detach().cpu().numpy()[0]
    pred = predz * ys + ym
    return pred, len(keys), best_loss

def row(bundle, target, pred, train_rows, spec, loss):
    p = base.month_shift(target,-1)
    return {
        "target":target, "origin":p, "spec":list(spec), "train_rows":train_rows,
        "train_mll_loss":float(loss),
        "pred_log_return_gold":float(pred[0]),
        "forecast":float(bundle.core_gold[p]*math.exp(float(pred[0]))),
        "actual":float(bundle.core_gold[target]),
        "rw":float(bundle.core_gold[p])
    }

def eval_spec(bundle, cache, spec, start, end):
    rows=[]
    errs=[]
    for t in base.month_range(start,end):
        pred,n,loss = fit_predict(cache[t], t, spec)
        r=row(bundle,t,pred,n,spec,loss); rows.append(r)
        p=base.month_shift(t,-1)
        actual_ret=math.log(bundle.monthly_metal["Gold"][t]/bundle.monthly_metal["Gold"][p])
        errs.append(abs(float(pred[0])-actual_ret))
    return float(np.mean(errs)), rows

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    b=base.load_data(dsn)
    cache={t:base.all_samples_at_origin(b,t,governed=True)
           for t in base.month_range(DEV_START,STRESS_END)}
    # Small, preregistered structural grid. 2025/2026 never used for selection.
    specs=[
        (1,1,"RBF",120,0.05),
        (2,1,"RBF",120,0.05),
        (1,2,"RBF_MATERN",120,0.05),
        (2,2,"RBF_MATERN",120,0.05),
    ]
    candidates=[]
    for s in specs:
        obj,rows=eval_spec(b,cache,s,DEV_START,DEV_END)
        candidates.append({"spec":s,"dev_logret_mae":obj,"dev_metrics":base.metrics(rows)})
    candidates.sort(key=lambda z:(z["dev_logret_mae"],z["spec"]))
    best=tuple(candidates[0]["spec"])
    _,dev_rows=eval_spec(b,cache,best,DEV_START,DEV_END)
    _,tr_rows=eval_spec(b,cache,best,TRANSPORT_START,TRANSPORT_END)
    _,st_rows=eval_spec(b,cache,best,STRESS_START,STRESS_END)
    result={
        "model_id":"VW_MIDAS_MOGP_LCM_V1",
        "scope":"RESEARCH_ONLY_HEAD_SWAP",
        "authority":{
            "base_feature_contract":"UNCHANGED_VW_MIDAS_8_FEATURE",
            "database_access":"READ_ONLY",
            "selection_period":f"{DEV_START}..{DEV_END}",
            "2025_role":"LOCKED_TRANSPORT_NOT_SELECTION",
            "2026_role":"RETROSPECTIVE_STRESS_NOT_SELECTION",
        },
        "source_checks":b.source_checks,
        "candidate_selection":candidates,
        "selected_spec":best,
        "dev": {"metrics":base.metrics(dev_rows),"yearly":base.yearly(dev_rows),"rows":dev_rows},
        "transport_2025":{"metrics":base.metrics(tr_rows),"rows":tr_rows},
        "stress_2026":{"metrics":base.metrics(st_rows),"rows":st_rows},
    }
    Path("vw_midas_mogp_lcm_v1_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "selected_spec":best,
        "dev":result["dev"]["metrics"],
        "transport_2025":result["transport_2025"]["metrics"],
        "stress_2026":result["stress_2026"]["metrics"],
    },sort_keys=True))

if __name__=="__main__":
    main()
