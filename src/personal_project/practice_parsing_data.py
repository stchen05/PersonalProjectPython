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
	path = find_sample_csv()
	head = read_head(path, n=7)
	print(f"Using: {path}")
	print("First rows:")
	for r in head:
		print(r)
		
	print("test github again")


if __name__ == "__main__":
	main()