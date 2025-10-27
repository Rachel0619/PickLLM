import os
import sys
from pathlib import Path
import requests
import csv
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple
import pandas as pd

root_dir = Path(os.getcwd()).parent
sys.path.append(str(root_dir/"src"))

from match_openrouter import fetch_openrouter_models

def add_display_name(df: pd.DataFrame) -> pd.DataFrame:
    df['displayed_name'] = df.apply(lambda row: row['model'] if pd.isna(row['openrouter_id']) else row['openrouter_id'], axis=1)
    return df

def add_pricing(df: pd.DataFrame) -> pd.DataFrame:
    df_inter = add_display_name(df)
    df_pricing = df_inter.copy()
    df_pricing['pricing_source'] = df_pricing.apply(lambda row: "openrouter" if row['license'] == 'Proprietary' else "free", axis=1)

    openrouter_models = fetch_openrouter_models()
    openrouter_models_df = pd.json_normalize(openrouter_models)
    openrouter_models_df = openrouter_models_df[['id', 'description', 'pricing.prompt', 'pricing.completion', 'pricing.image']]

    result_df = df_pricing.merge(openrouter_models_df, left_on='openrouter_id', right_on='id', how='left')
    return result_df

def sum_pricing(df: pd.DataFrame) -> pd.DataFrame:
    df_result = df.copy()
    df_result['pricing'] = df_result['pricing.prompt'] + df_result['pricing.completion'] + df_result['pricing.image']
    return df_result

# if __name__ == "__main__":
#     df_webdev = pd.read_csv("../data/lmarena_webdev_with_pricing_or.csv")
#     df = sum_pricing(df_webdev)
#     df.to_csv("../data/lmarena_webdev_with_pricing.csv", index=False)
#     print("Sum price completed")