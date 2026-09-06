import argparse
import os

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def main():
    parser = argparse.ArgumentParser(description="Plot internet speed from CSV data.")
    parser.add_argument("csv_file", type=str, help="Path to the input CSV file.")
    parser.add_argument("-o", "--output", type=str, default=None,
                        help="Output PNG file path (default: same name as CSV with .png extension)")
    parser.add_argument("-d", "--expected-download", type=float, default=None,
                        help="Expected download speed in Mbps to draw a reference line.")
    parser.add_argument("-u", "--expected-upload", type=float, default=None,
                        help="Expected upload speed in Mbps to draw a reference line.")
    parser.add_argument("-p", "--expected-ping", type=float, default=None,
                        help="Expected ping in ms to draw a reference line.")
    
    args = parser.parse_args()
    
    if not os.path.isfile(args.csv_file):
        print(f"Error: File {args.csv_file} does not exist.")
        return
        
    if args.output is None:
        base, _ = os.path.splitext(args.csv_file)
        out_file = f"{base}.png"
    else:
        out_file = args.output
        
    print(f"Reading data from {args.csv_file}...")
    df = pd.read_csv(args.csv_file)
    
    # Parse timestamps
    if "timestamp" not in df.columns:
        print("Error: 'timestamp' column not found in CSV.")
        return
        
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Check if necessary columns exist
    required_columns = ["download_mbps", "upload_mbps", "ping_ms"]
    for col in required_columns:
        if col not in df.columns:
            print(f"Error: '{col}' column not found in CSV.")
            return

    print("Generating plots...")
    
    # Create a figure with 2 subplots (vertically stacked)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
    
    # Subplot 1: Download and Upload speed
    ax1.plot(df['timestamp'], df['download_mbps'], label='Download (Mbps)', color='#1f77b4', marker='o', markersize=4, linestyle='-', linewidth=1.5)
    ax1.plot(df['timestamp'], df['upload_mbps'], label='Upload (Mbps)', color='#ff7f0e', marker='o', markersize=4, linestyle='-', linewidth=1.5)
    
    if args.expected_download is not None:
        ax1.axhline(y=args.expected_download, color='#1f77b4', linestyle=':', linewidth=2, label=f'Expected Download ({args.expected_download} Mbps)')
    if args.expected_upload is not None:
        ax1.axhline(y=args.expected_upload, color='#ff7f0e', linestyle=':', linewidth=2, label=f'Expected Upload ({args.expected_upload} Mbps)')
        
    ax1.set_ylabel('Speed (Mbps)', fontsize=12)
    ax1.set_title('Internet Download and Upload Speeds Over Time', fontsize=14)
    ax1.legend(loc='best')
    ax1.grid(True, linestyle='--', alpha=0.7)
    
    # Subplot 2: Ping
    ax2.plot(df['timestamp'], df['ping_ms'], label='Ping (ms)', color='#2ca02c', marker='s', markersize=4, linestyle='-', linewidth=1.5)
    
    if args.expected_ping is not None:
        ax2.axhline(y=args.expected_ping, color='#2ca02c', linestyle=':', linewidth=2, label=f'Expected Ping ({args.expected_ping} ms)')
        
    ax2.set_ylabel('Ping (ms)', fontsize=12)
    ax2.set_xlabel('Time', fontsize=12)
    ax2.set_title('Internet Ping Over Time', fontsize=14)
    ax2.legend(loc='best')
    ax2.grid(True, linestyle='--', alpha=0.7)
    
    # Formatting X-axis dates
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.xticks(rotation=45)
    
    # Adjust layout
    plt.tight_layout()
    
    print(f"Saving plot to {out_file} (High Resolution 300 DPI)...")
    plt.savefig(out_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Done!")

if __name__ == "__main__":
    main()
