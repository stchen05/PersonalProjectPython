"""Small helper to load the sample data and print the first rows.

This module is intentionally dependency-light: it will use pandas if
available, otherwise fall back to the standard-library csv reader.

It also locates the CSV relative to the project root (assumes this file
is at src/personal_project/...). That makes running the script from the
project root work reliably.
"""

from pathlib import Path
import csv
from typing import List, Dict


def find_sample_csv() -> Path:
	"""Return a Path to the sample CSV file.

	Search order:
	1. <project_root>/data/sample_data.csv
	2. <cwd>/sample_data.csv
	Raises FileNotFoundError if not found.
	"""
	# project root is two parents up from this file: src/personal_project/<this_file>
	project_root = Path(__file__).resolve().parents[2]
	candidate = project_root / "data" / "sample_data.csv"
	if candidate.exists():
		return candidate

	# fallback: look in current working directory
	candidate = Path.cwd() / "sample_data.csv"
	if candidate.exists():
		return candidate

	raise FileNotFoundError(
		"sample_data.csv not found. Expected at 'data/sample_data.csv' under the project root or in CWD."
	)


def read_head(path: Path, n: int = 7) -> List[Dict[str, str]]:
	"""Read the first n rows from CSV and return a list of dicts.

	If pandas is available it will be used for nicer output; otherwise csv.DictReader is used.
	"""
	try:
		import pandas as pd  # type: ignore

		df = pd.read_csv(path)
		# convert first n rows to list of dicts for consistent printing
		return df.head(n).to_dict(orient="records")
	except Exception:
		# fallback to stdlib csv
		rows = []
		with path.open(newline="", encoding="utf-8") as fh:
			reader = csv.DictReader(fh)
			for i, row in enumerate(reader):
				if i >= n:
					break
				rows.append(row)
		return rows


def main() -> None:
    # Load and display sample data
    path = find_sample_csv()
    data = read_head(path, n=10)  # get up to 10 rows for sorting
    print(f"Using: {path}\n")

    # Sort data by score (highest to lowest)
    sorted_data = sorted(data, key=lambda x: int(x['score']), reverse=True)
    
    # Print sorted leaderboard
    print("🏆 Leaderboard (by score):")
    print("-" * 40)
    print(f"{'Rank':<6}{'Name':<12}{'Score':<8}{'Level':<6}")
    print("-" * 40)
    
    for i, player in enumerate(sorted_data, 1):
        print(f"{i:<6}{player['name']:<12}{player['score']:<8}{player['level']:<6}")
    
    # Print some basic stats
    try:
        total_score = sum(int(r['score']) for r in sorted_data)
        avg_score = total_score / len(sorted_data)
        print("\n📊 Statistics:")
        print(f"Total players: {len(sorted_data)}")
        print(f"Average score: {avg_score:.1f}")
        print(f"Top score: {sorted_data[0]['score']} (by {sorted_data[0]['name']})")
        print(f"Lowest score: {sorted_data[-1]['score']} (by {sorted_data[-1]['name']})")
    except (ValueError, KeyError) as e:
        print(f"Could not calculate stats: {e}")


if __name__ == "__main__":
    main()