"""Helper to download Kaggle datasets into the project's data/ folder.

Usage:
    python scripts/download_kaggle.py owner/dataset-name

This script uses the KaggleApi from the kaggle package. Make sure you have
placed your `kaggle.json` in `%USERPROFILE%/.kaggle/kaggle.json` and that
it is not committed to the repo (it's added to .gitignore).
"""
from pathlib import Path
import sys


def download_dataset(owner_dataset: str, dest: str = "data", unzip: bool = True) -> None:
    # Ensure the kaggle.json token exists
    kaggle_token = Path.home() / ".kaggle" / "kaggle.json"
    if not kaggle_token.exists():
        print(f"Kaggle API token not found at: {kaggle_token}")
        print("Create one at https://www.kaggle.com/ -> Account -> Create API Token and place it at the path above.")
        raise FileNotFoundError(kaggle_token)

    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
    except Exception as exc:
        print("kaggle package is not installed. Run: python -m pip install kaggle")
        raise

    api = KaggleApi()
    api.authenticate()

    dest_path = Path(dest)
    dest_path.mkdir(parents=True, exist_ok=True)

    print(f"Downloading {owner_dataset} to {dest_path} (unzip={unzip})...")
    api.dataset_download_files(owner_dataset, path=str(dest_path), unzip=unzip)
    print("Done.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/download_kaggle.py <owner/dataset>")
        sys.exit(1)

    dataset = sys.argv[1]
    download_dataset(dataset)
