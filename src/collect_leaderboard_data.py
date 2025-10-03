import glob
import os
import pandas as pd
import pickle
import subprocess
import sys
from datetime import datetime

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(FILE_DIR, os.pardir))
CSV_DIR = os.path.join(ROOT_DIR, "data")
LMARENA_DIR = os.path.join(ROOT_DIR, "lmarena")

def clone_lmarena_repo():
    """Clone the LMArena repository if it doesn't exist."""
    url = "https://huggingface.co/spaces/lmarena-ai/lmarena-leaderboard"
    repo = LMARENA_DIR
    if not os.path.exists(repo):
        try:
            print("Installing git-lfs...")
            subprocess.run(["git", "lfs", "install", "--skip-repo"])
            print(f"Cloning repository from {url}...")
            subprocess.run(["git", "clone", "--depth", "1", url, repo], check=True)
            print("Repository cloned successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Error cloning repository: {e}")
            return None
    else:
        print(f"Repository '{repo}' already exists.")
    return repo

def get_date_from_filename(filename):
    return filename.split('_')[-1].split('.')[0]

def get_pkl_by_date(repo):
    files = glob.glob(f"{repo}/*.pkl")
    if not files:
        raise FileNotFoundError("No .pkl files found in the lmarena directory.")

    # Always use today's date
    today = datetime.now().strftime("%Y%m%d")

    # Check if today's exact file exists
    today_file = f"{repo}/elo_results_{today}.pkl"
    if os.path.exists(today_file):
        print(f"Found exact file for {today}: {today_file}", file=sys.stderr)
        return today_file

    # If not found, get the newest available file
    files.sort(key=get_date_from_filename, reverse=True)
    latest_file = files[0]
    latest_date = get_date_from_filename(latest_file)
    print(f"File for {today} not found. Using latest available file: {latest_file} (date: {latest_date})", file=sys.stderr)
    return latest_file

def get_date_version(repo):
    # Get the latest available data (today's or newest)
    filename = get_pkl_by_date(repo)
    date = get_date_from_filename(filename)
    return date, filename

def load_lmarena_data(filename, subset):
    with open(filename, 'rb') as f:
        data = pickle.load(f)

    if isinstance(data, dict):
        if subset in data:
            subset_data = data[subset]
            if isinstance(subset_data, dict) and 'full' in subset_data:
                return subset_data['full']['leaderboard_table_df']
            elif isinstance(subset_data, pd.DataFrame):
                return subset_data

        # If no match found, print available keys for debugging
        print(f"Available keys in data: {list(data.keys())}", file=sys.stderr)
        return None
    else:
        return None

def load_lmarena_metadata(repo):
    # Find all metadata files and get the most recent one
    metadata_files = glob.glob(f"{repo}/leaderboard_table_*.csv")
    if metadata_files:
        # Sort by date in filename to get the most recent
        metadata_files.sort(key=lambda x: get_date_from_filename(x), reverse=True)
        latest_file = metadata_files[0]
        latest_date = get_date_from_filename(latest_file)
        print(f"Using latest metadata file: {latest_file} (date: {latest_date})", file=sys.stderr)
        df = pd.read_csv(latest_file)
    else:
        print(f"No metadata files found in {repo}", file=sys.stderr)
        return None

    # Save a copy to project-root data/metadata_<date>.csv
    out_dir = build_directory(CSV_DIR)
    out_path = os.path.join(out_dir, f"metadata_{latest_date}.csv")
    try:
        df.to_csv(out_path, index=False)
        print(f"Saved metadata to {out_path}")
    except Exception as e:
        print(f"Failed to save metadata to {out_path}: {e}", file=sys.stderr)
    return df

def build_full_leaderboard(leaderboard, metadata):
    lm = leaderboard.merge(metadata, left_index=True, right_on='key')
    df = pd.DataFrame({
        'rank': range(1, len(lm) + 1),
        'rank_stylectrl': lm['final_ranking'].values.astype(int),
        'model': lm['Model'].values,
        'arena_score': lm['rating'].values.astype(int),
        '95_pct_ci': [
            f"+{int(upper - rating)}/-{int(rating - lower)}" 
            for rating, upper, lower in zip(
                lm['rating'].values,
                lm['rating_upper'].values,
                lm['rating_lower'].values
            )
        ],
        'votes': lm['num_battles'].values.astype(int),
        'organization': lm['Organization'].values,
        'license': lm['License'].values,
        'knowledge_cutoff': lm['Knowledge cutoff date'].astype(str).str.replace('-', 'not specified', regex=False).values,
        'url': lm['Link'].values,
    })
    return df

def build_directory(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)
    return dir

def build_lmarena_leaderboards(metadata, filename):
    dir = build_directory(CSV_DIR)
    subsets = ['text', 'vision', 'image', 'image-edit', 'webdev']
    for subset in subsets:
        print(f"Building {subset} Leaderboard")
        leaderboard = load_lmarena_data(filename, subset)
        df = build_full_leaderboard(leaderboard, metadata)
        path = os.path.join(dir, f"lmarena_{subset}.csv")
        df.to_csv(path, index=False)

if __name__ == "__main__":
    repo = clone_lmarena_repo()
    date, filename = get_date_version(repo)
    metadata = load_lmarena_metadata(repo)
    build_lmarena_leaderboards(metadata, filename)
