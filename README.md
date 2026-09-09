# Internet Speed Logger

A set of Python scripts to continuously monitor and log your internet speed over time, and generate high-resolution plots of the data. 

This project uses [`uv`](https://docs.astral.sh/uv/) for dependency management.

## Setup

Ensure you have `uv` installed. Then, simply run the scripts via `uv run` which will automatically handle the environment and dependencies.

## Usage

### Quick Start (Default Use Case)

A typical workflow involves continuously logging measurements every 10 minutes and then plotting the collected data with reference lines for expected network performance:

1. **Start measuring** (every 10 minutes, automatically saving to `internet_speed_<timestamp>.csv`):
   ```bash
   uv run measure.py --interval 10
   ```
   *(Press `Ctrl+C` when you want to finish or pause data collection. You can also run `uv run measure.py` without arguments as 10 minutes is the default interval.)*

2. **Plot the collected data** with expected reference lines (100 Mbps download, 50 Mbps upload, and 20 ms ping):
   ```bash
   uv run plot.py -d 70 90 100 -u 15 35 50 -p 20 35 50 -i internet_speed_<timestamp>.csv
   ```


---

### 1. Measuring Internet Speed (`measure.py`)

This script runs indefinitely, measuring your download speed, upload speed, and ping at a specified interval. It logs the progress to the terminal and appends the results to a CSV file.

```bash
uv run measure.py [OPTIONS]
```

**Options:**
- `-i`, `--interval <minutes>`: Interval between measurements in minutes (default: `10.0`)
- `-o`, `--output <file.csv>`: Output CSV file path (default: `internet_speed_YYYYMMDD_HHMMSS.csv`)

**Example:**
Run a test every 5 minutes and save it to `my_speed_data.csv`:
```bash
uv run measure.py --interval 5 --output my_speed_data.csv
```

To stop the measurement, press `Ctrl+C` in your terminal. The script is designed to run for weeks and will gracefully handle temporary network connection drops.

### 2. Plotting the Data (`plot.py`)

This script reads a generated CSV file and creates a high-resolution (300 DPI) PNG image with two stacked plots: 
1. Download & Upload speeds over time (in Mbps).
2. Ping over time (in ms).

```bash
uv run plot.py [csv_file] [OPTIONS]
```

**Positional Arguments:**
- `<csv_file>`: Path to the input CSV file (optional if `-i`/`--input` is provided).

**Options:**
- `-i`, `--input <file.csv>`: Path to the input CSV file
- `-o`, `--output <file.png>`: Output PNG file path (default: same name as the input CSV, but with a `.png` extension)
- `-d`, `--expected-download <mbps>`: Expected download speed in Mbps to draw a reference line
- `-u`, `--expected-upload <mbps>`: Expected upload speed in Mbps to draw a reference line
- `-p`, `--expected-ping <ms>`: Expected ping in ms to draw a reference line

**Examples:**

Generate a plot for `my_speed_data.csv`:
```bash
uv run plot.py my_speed_data.csv
```
This will automatically generate `my_speed_data.png` in the same directory.

Generate a plot with benchmark reference lines:
```bash
uv run plot.py my_speed_data.csv -d 100 -u 50 -p 20
```
This adds dotted reference lines for expected download (100 Mbps), expected upload (50 Mbps), and expected ping (20 ms).

### 3. Merging CSV Files (`merge.py`)

This script combines multiple measurement CSV files into a single file, sorting the rows chronologically ascending by timestamp.

```bash
uv run merge.py -i <csv_file_1> <csv_file_2> ... -o <output_csv_file>
```

**Options:**
- `-i`, `--input <file1.csv> [file2.csv ...]`: One or more input CSV files to merge.
- `-o`, `--output <file.csv>`: Output merged CSV file path.
- `--drop-duplicates`: (Optional) Drop duplicate rows after merging.

**Example:**
```bash
uv run merge.py -i internet_speed_part1.csv internet_speed_part2.csv -o combined_speed.csv
```
