import pandas as pd
import json
import os


def load_config(path='config.json'): # read config file
    with open(path, 'r') as f:
        return json.load(f)


def check_config(cfg):
    # basic config check
    needed = ['region','year','operation','output']
    for key in needed:
        if key not in cfg:
            raise ValueError(f"missing config value {key}")

    if cfg['operation'] not in ['average','sum']:
        raise ValueError("operation must be average or sum")


def load_data(path='data/gdp_data.csv'):
    # load csv data
    if not os.path.exists(path):
        raise FileNotFoundError("gdp data in csv not found")

    df = pd.read_csv(path)

    cols = ['Country Name','Region','Year','Value']
    for c in cols:
        if c not in df.columns:
            raise ValueError("missing column " + c)

    return df


def data_info(df): # basic dataset info
    return {
        'total': len(df),
        'year_range': (int(df['Year'].min()), int(df['Year'].max()))
    }
