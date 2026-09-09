import argparse
import os
import sys

import pandas as pd


def merge_csv_files(
    input_files: list[str], output_file: str, drop_duplicates: bool = False
) -> None:
    dfs = []

    for file_path in input_files:
        if not os.path.isfile(file_path):
            print(f"Error: File '{file_path}' does not exist.", file=sys.stderr)
            sys.exit(1)

        try:
            df = pd.read_csv(file_path, dtype=str)
        except pd.errors.EmptyDataError:
            print(f"Warning: File '{file_path}' is empty. Skipping.")
            continue
        except Exception as e:
            print(f"Error reading '{file_path}': {e}", file=sys.stderr)
            sys.exit(1)

        if "timestamp" not in df.columns:
            print(
                f"Error: 'timestamp' column not found in '{file_path}'.",
                file=sys.stderr,
            )
            sys.exit(1)

        dfs.append(df)

    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    if not dfs:
        print("Warning: No data found in any of the input files.")
        default_headers = ["timestamp", "download_mbps", "upload_mbps", "ping_ms"]
        empty_df = pd.DataFrame(columns=default_headers)
        empty_df.to_csv(output_file, index=False)
        print(f"Wrote empty CSV with headers to '{output_file}'.")
        return

    merged_df = pd.concat(dfs, ignore_index=True)

    if drop_duplicates:
        merged_df = merged_df.drop_duplicates()

    # Sort ascending by timestamp (converting to datetime temporarily to ensure robust chronological order)
    parsed_timestamps = pd.to_datetime(merged_df["timestamp"], errors="coerce")
    merged_df = merged_df.assign(_sort_ts=parsed_timestamps)
    merged_df = merged_df.sort_values(by="_sort_ts", ascending=True).drop(
        columns=["_sort_ts"]
    )
    merged_df.reset_index(drop=True, inplace=True)

    merged_df.to_csv(output_file, index=False)
    print(
        f"Successfully merged {len(merged_df)} rows from {len(input_files)} file(s) into '{output_file}'."
    )


def main():
    parser = argparse.ArgumentParser(
        description="Merge multiple internet speed measurement CSV files, sorted ascending by timestamp."
    )
    parser.add_argument(
        "-i",
        "--input",
        nargs="+",
        action="extend",
        required=True,
        metavar="FILE",
        help="One or more input CSV files to merge.",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        metavar="FILE",
        help="Path to the output CSV file.",
    )
    parser.add_argument(
        "--drop-duplicates",
        action="store_true",
        help="Drop duplicate rows after merging.",
    )

    args = parser.parse_args()
    merge_csv_files(args.input, args.output, drop_duplicates=args.drop_duplicates)


if __name__ == "__main__":
    main()
