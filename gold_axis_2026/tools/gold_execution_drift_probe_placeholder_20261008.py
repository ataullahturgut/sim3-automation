"""Causal 2026 XAU/USD research experiment."""
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

def weighted_logit(x,y,ages):
    weights=np.exp(-np.log(2)*ages/252)
    model=Pipeline([("scale",StandardScaler()),("reg",LogisticRegression(C=.3))])
    model.fit(x,y,reg__sample_weight=weights)
    return model
