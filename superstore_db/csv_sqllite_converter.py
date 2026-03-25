"""Convert a CSV file into a SQLite database table.

Usage examples:
	python csv_sqllite_converter.py
	python csv_sqllite_converter.py --csv "superstore.csv" --db "superstore.db" --table superstore
	python csv_sqllite_converter.py --if-exists append
"""

from __future__ import annotations

import argparse
import importlib
import re
import sqlite3
from pathlib import Path
from typing import Sequence


def sanitize_identifier(value: str, fallback: str = "column") -> str:
	"""Convert arbitrary text into a safe SQLite identifier."""
	cleaned = re.sub(r"\W+", "_", value.strip().lower()).strip("_")
	if not cleaned:
		cleaned = fallback
	if cleaned[0].isdigit():
		cleaned = f"_{cleaned}"
	return cleaned


def build_unique_column_names(headers: Sequence[str]) -> tuple[list[str], dict[str, str]]:
	"""Return unique sanitized column names and a mapping from original -> sanitized."""
	used: set[str] = set()
	sanitized_headers: list[str] = []
	mapping: dict[str, str] = {}

	for index, original in enumerate(headers, start=1):
		base = sanitize_identifier(original, fallback=f"column_{index}")
		candidate = base
		suffix = 2
		while candidate in used:
			candidate = f"{base}_{suffix}"
			suffix += 1

		used.add(candidate)
		sanitized_headers.append(candidate)
		mapping[original] = candidate

	return sanitized_headers, mapping


def table_exists(connection: sqlite3.Connection, table_name: str) -> bool:
	cursor = connection.execute(
		"SELECT 1 FROM sqlite_master WHERE type='table' AND name = ? LIMIT 1",
		(table_name,),
	)
	return cursor.fetchone() is not None


def convert_csv_to_sqlite(
	csv_path: Path,
	db_path: Path,
	table_name: str,
	if_exists: str = "replace",
	encoding: str = "utf-8-sig",
	delimiter: str = ",",
	chunk_size: int = 1000,
) -> int:
	"""Load CSV rows into a SQLite table and return inserted row count."""
	try:
		pd = importlib.import_module("pandas")
	except ModuleNotFoundError as exc:
		raise ModuleNotFoundError(
			"pandas is required for this script. Install it with: pip install pandas"
		) from exc

	if not csv_path.exists():
		raise FileNotFoundError(f"CSV file not found: {csv_path}")

	db_path.parent.mkdir(parents=True, exist_ok=True)
	table_name = sanitize_identifier(table_name, fallback="imported_data")

	encoding_candidates: list[str] = []
	for candidate in [encoding, "utf-8-sig", "utf-8", "cp1252", "latin1"]:
		if candidate and candidate not in encoding_candidates:
			encoding_candidates.append(candidate)

	data_frame = None
	last_decode_error: UnicodeDecodeError | None = None

	for candidate_encoding in encoding_candidates:
		try:
			data_frame = pd.read_csv(
				csv_path,
				encoding=candidate_encoding,
				sep=delimiter,
				dtype=str,
			)
			break
		except UnicodeDecodeError as exc:
			last_decode_error = exc
			continue
		except pd.errors.EmptyDataError as exc:
			raise ValueError("CSV file is empty or has no header row.") from exc

	if data_frame is None:
		candidates = ", ".join(encoding_candidates)
		raise ValueError(
			f"Could not decode CSV using encodings: {candidates}. "
			f"Try passing --encoding explicitly. Last error: {last_decode_error}"
		) from last_decode_error

	if data_frame.columns.empty:
		raise ValueError("CSV file has no header row.")

	column_names, _ = build_unique_column_names([str(column) for column in data_frame.columns])
	data_frame.columns = column_names

	to_sql_mode = "append"
	if if_exists == "replace":
		to_sql_mode = "replace"
	elif if_exists == "fail":
		to_sql_mode = "fail"

	with sqlite3.connect(db_path) as connection:
		data_frame.to_sql(
			table_name,
			connection,
			if_exists=to_sql_mode,
			index=False,
			chunksize=chunk_size,
			method="multi",
		)

	return int(len(data_frame.index))


def build_parser() -> argparse.ArgumentParser:
	script_dir = Path(__file__).resolve().parent

	parser = argparse.ArgumentParser(description="Convert a CSV file to a SQLite database.")
	parser.add_argument(
		"--csv",
		type=Path,
		default=script_dir / "Sample - Superstore.csv",
		help="Path to input CSV file (default: Sample - Superstore.csv in this folder).",
	)
	parser.add_argument(
		"--db",
		type=Path,
		default=script_dir / "superstore.db",
		help="Path to output SQLite database (default: superstore.db in this folder).",
	)
	parser.add_argument(
		"--table",
		type=str,
		default="superstore",
		help="Destination table name (default: superstore).",
	)
	parser.add_argument(
		"--if-exists",
		choices=["replace", "append", "fail"],
		default="replace",
		help="What to do if table exists: replace (default), append, or fail.",
	)
	parser.add_argument(
		"--encoding",
		type=str,
		default="utf-8-sig",
		help="CSV file encoding (default: utf-8-sig).",
	)
	parser.add_argument(
		"--delimiter",
		type=str,
		default=",",
		help="CSV delimiter (default: ',').",
	)
	parser.add_argument(
		"--chunk-size",
		type=int,
		default=1000,
		help="Rows per batch insert (default: 1000).",
	)

	return parser


def main() -> None:
	args = build_parser().parse_args()

	rows = convert_csv_to_sqlite(
		csv_path=args.csv,
		db_path=args.db,
		table_name=args.table,
		if_exists=args.if_exists,
		encoding=args.encoding,
		delimiter=args.delimiter,
		chunk_size=args.chunk_size,
	)

	print(f"Inserted {rows} rows into table '{sanitize_identifier(args.table)}'.")
	print(f"SQLite database created at: {args.db.resolve()}")


if __name__ == "__main__":
	main()
