
# csv_loader.py
from pathlib import Path
import os
import pandas as pd
from typing import List, Tuple

CANDIDATE_FILENAMES = ["movies.csv", "영화DB(임시).csv"]

def _repo_root_candidates() -> List[Path]:
    here = Path(__file__).resolve()
    cands = [here.parent] + list(here.parents) + [Path.cwd()]
    # de-duplicate while preserving order
    seen = set()
    uniq = []
    for p in cands:
        if p not in seen:
            uniq.append(p)
            seen.add(p)
    return uniq

def candidate_paths() -> List[Path]:
    paths = []
    for root in _repo_root_candidates():
        for name in CANDIDATE_FILENAMES:
            paths.append(root / "data" / name)
    env = os.getenv("DATA_CSV_PATH")
    if env:
        paths.append(Path(env))
    return paths

def resolve_csv_path() -> Path | None:
    for p in candidate_paths():
        if p.exists():
            return p
    return None

def load_csv(encoding_candidates=("utf-8-sig", "cp949", "utf-8")) -> pd.DataFrame | None:
    p = resolve_csv_path()
    if not p:
        return None
    last_err = None
    for enc in encoding_candidates:
        try:
            return pd.read_csv(p, encoding=enc)
        except UnicodeDecodeError as e:
            last_err = e
            continue
    try:
        return pd.read_csv(p)
    except Exception:
        if last_err:
            raise last_err
        raise

def debug_info() -> Tuple[list, list]:
    """Return (candidate_paths_as_str, data_dir_listing) for debugging in Streamlit."""
    cps = [str(p) for p in candidate_paths()]
    # Try to list the most likely data dir
    likely = Path.cwd() / "data"
    listing = []
    if likely.exists():
        listing = [x.name for x in likely.glob("*")]
    return cps, listing
