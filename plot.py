import argparse
import colorsys
import os

import matplotlib.colors as mcolors
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd


def main():
    parser = argparse.ArgumentParser(description="Plot internet speed from CSV data.")
    parser.add_argument(
        "csv_file",
        type=str,
        nargs="?",
        default=None,
        help="Path to the input CSV file (optional if -i/--input is provided).",
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        default=None,
        help="Path to the input CSV file.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Output PNG file path (default: same name as CSV with .png extension)",
    )
    parser.add_argument(
        "-d",
        "--expected-download",
        type=float,
        nargs="+",
        default=None,
        help="Expected download speed in Mbps (1 value, or 3 values for MIN AVG MAX) to draw reference line(s).",
    )
    parser.add_argument(
        "-u",
        "--expected-upload",
        type=float,
        nargs="+",
        default=None,
        help="Expected upload speed in Mbps (1 value, or 3 values for MIN AVG MAX) to draw reference line(s).",
    )
    parser.add_argument(
        "-p",
        "--expected-ping",
        type=float,
        nargs="+",
        default=None,
        help="Expected ping in ms (1 value, or 3 values for MIN AVG MAX) to draw reference line(s).",
    )

    args = parser.parse_args()

    for flag_name, val in [
        ("--expected-download / -d", args.expected_download),
        ("--expected-upload / -u", args.expected_upload),
        ("--expected-ping / -p", args.expected_ping),
    ]:
        if val is not None and len(val) not in (1, 3):
            parser.error(
                f"{flag_name} expects either 1 value or 3 values (MIN AVG MAX), but got {len(val)}."
            )

    csv_file = args.input or args.csv_file
    if not csv_file:
        parser.error("the following arguments are required: -i/--input or csv_file")

    if not os.path.isfile(csv_file):
        print(f"Error: File {csv_file} does not exist.")
        return

    if args.output is None:
        base, _ = os.path.splitext(csv_file)
        out_file = f"{base}.png"
    else:
        out_file = args.output

    print(f"Reading data from {csv_file}...")
    df = pd.read_csv(csv_file)

    # Parse timestamps
    if "timestamp" not in df.columns:
        print("Error: 'timestamp' column not found in CSV.")
        return

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Check if necessary columns exist
    required_columns = ["download_mbps", "upload_mbps", "ping_ms"]
    for col in required_columns:
        if col not in df.columns:
            print(f"Error: '{col}' column not found in CSV.")
            return

    def get_shades(color):
        r, g, b = mcolors.to_rgb(color)
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        # Min: lighter shade, Avg: base color, Max: darker shade
        r_min, g_min, b_min = colorsys.hls_to_rgb(
            h, min(0.85, l + (1.0 - l) * 0.5), max(0.2, s * 0.8)
        )
        r_max, g_max, b_max = colorsys.hls_to_rgb(h, max(0.15, l * 0.6), s)
        return (
            mcolors.to_hex((r_min, g_min, b_min)),
            color,
            mcolors.to_hex((r_max, g_max, b_max)),
        )

    def add_expected_lines(ax, values, label_prefix, unit, color):
        if values is not None:
            if len(values) == 1:
                ax.axhline(
                    y=values[0],
                    color=color,
                    linestyle=":",
                    linewidth=2,
                    label=f"Expected {label_prefix} ({values[0]} {unit})",
                )
            elif len(values) == 3:
                shades = get_shades(color)
                ax.axhline(
                    y=values[0],
                    color=shades[0],
                    linestyle=":",
                    linewidth=2,
                    label=f"Expected {label_prefix} Min ({values[0]} {unit})",
                )
                ax.axhline(
                    y=values[1],
                    color=shades[1],
                    linestyle=":",
                    linewidth=2,
                    label=f"Expected {label_prefix} Avg ({values[1]} {unit})",
                )
                ax.axhline(
                    y=values[2],
                    color=shades[2],
                    linestyle=":",
                    linewidth=2,
                    label=f"Expected {label_prefix} Max ({values[2]} {unit})",
                )

    print("Generating plots...")

    # Create a figure with 2 subplots (vertically stacked)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

    # Subplot 1: Download and Upload speed
    ax1.plot(
        df["timestamp"],
        df["download_mbps"],
        label="Download (Mbps)",
        color="#1f77b4",
        marker="o",
        markersize=4,
        linestyle="-",
        linewidth=1.5,
    )
    ax1.plot(
        df["timestamp"],
        df["upload_mbps"],
        label="Upload (Mbps)",
        color="#ff7f0e",
        marker="o",
        markersize=4,
        linestyle="-",
        linewidth=1.5,
    )

    add_expected_lines(ax1, args.expected_download, "Download", "Mbps", "#1f77b4")
    add_expected_lines(ax1, args.expected_upload, "Upload", "Mbps", "#ff7f0e")

    ax1.set_ylabel("Speed (Mbps)", fontsize=12)
    ax1.set_title("Internet Download and Upload Speeds Over Time", fontsize=14)
    ax1.legend(loc="upper left", bbox_to_anchor=(1.01, 1))
    ax1.grid(True, linestyle="--", alpha=0.7)

    # Subplot 2: Ping
    ax2.plot(
        df["timestamp"],
        df["ping_ms"],
        label="Ping (ms)",
        color="#2ca02c",
        marker="s",
        markersize=4,
        linestyle="-",
        linewidth=1.5,
    )

    add_expected_lines(ax2, args.expected_ping, "Ping", "ms", "#2ca02c")

    ax2.set_ylabel("Ping (ms)", fontsize=12)
    ax2.set_xlabel("Time", fontsize=12)
    ax2.set_title("Internet Ping Over Time", fontsize=14)
    ax2.legend(loc="upper left", bbox_to_anchor=(1.01, 1))
    ax2.grid(True, linestyle="--", alpha=0.7)

    # Formatting X-axis dates
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
    plt.xticks(rotation=45)

    # Adjust layout
    plt.tight_layout()

    print(f"Saving plot to {out_file} (High Resolution 300 DPI)...")
    plt.savefig(out_file, dpi=300, bbox_inches="tight")
    plt.close()

    print("Done!")


if __name__ == "__main__":
    main()
