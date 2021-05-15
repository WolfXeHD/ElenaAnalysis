#-*- coding:utf-8 -*-
from datetime import datetime, timedelta
import pkg_resources
import pandas as pd

pd.options.mode.chained_assignment = None

excretions = pkg_resources.resource_filename('ElenaAnalysis',
                                             'data/excretions.csv')

pee_file = pkg_resources.resource_filename('ElenaAnalysis',
                                           'data/pee_modified.pkl')
poo_file = pkg_resources.resource_filename('ElenaAnalysis',
                                           'data/poo_modified.pkl')

df = pd.read_csv(excretions)
df.columns = [col.replace(" ", "") for col in df.columns]
df_pee = df[df["Type"] == "Pee"]

