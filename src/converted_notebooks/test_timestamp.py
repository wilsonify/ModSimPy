# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.4.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

import pandas as pd

timestamp = pd.Timestamp(1412526600000000000)
series = pd.Series([], dtype=object)
series['timestamp'] = timestamp
type(series.timestamp)

series = pd.Series([], dtype=object)
series['anything'] = 300.0
series['timestamp'] = timestamp
type(series.timestamp)

series.dtype

pd.show_versions()


