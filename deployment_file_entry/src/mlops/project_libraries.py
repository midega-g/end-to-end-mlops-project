import os
import pickle
import argparse
from datetime import datetime

import numpy as np
import mlflow
import pandas as pd
import uvicorn
import matplotlib.pyplot as plt
from fastapi import FastAPI
from sklearn.svm import SVC
from sklearn.impute import SimpleImputer
# from prefect import task, flow, get_run_logger
# from hyperopt import STATUS_OK, Trials, fmin, hp, tpe
# from hyperopt.pyll import scope
from sklearn.compose import ColumnTransformer
# fmt: off
from sklearn.metrics import (
    f1_score,
    recall_score,
    roc_auc_score,
    accuracy_score,
    precision_score
)
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
# fmt: on
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import PowerTransformer
from sklearn.feature_extraction import DictVectorizer

# from xgboost import XGBClassifier

# fmt: off
__all__ = [
    'argparse', 'os', 'mlflow', 'pickle', 'np', 'pd', 'plt', 'datetime', 'Pipeline', 
    'make_pipeline','SimpleImputer', 'ColumnTransformer', 'PowerTransformer', 'DictVectorizer',
    'GradientBoostingClassifier', 'RandomForestClassifier', 'SVC', 
    'LogisticRegression', 'f1_score','recall_score', 'roc_auc_score', 'accuracy_score', 
    'precision_score', 'FastAPI', 'uvicorn'
]
# fmt: on
