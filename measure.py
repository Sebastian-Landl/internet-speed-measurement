import argparse
import csv
import datetime
import logging
import os
import time

import speedtest

# Setup basic logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def run_speedtest():
    # We create a new Speedtest object each time to avoid cached states
    st = speedtest.Speedtest(secure=True)
    st.get_best_server()
    
    download_bps = st.download()
    upload_bps = st.upload()
    ping_ms = st.results.ping
    
    # Convert bits per second to megabits per second
    download_mbps = download_bps / 1_000_000
    upload_mbps = upload_bps / 1_000_000
    
    return download_mbps, upload_mbps, ping_ms

def main():
    parser = argparse.ArgumentParser(description="Measure internet speed periodically.")
    parser.add_argument("-i", "--interval", type=float, default=10.0,
                        help="Interval between measurements in minutes (default: 10)")
    parser.add_argument("-o", "--output", type=str, default=None,
                        help="Output CSV file path (default: internet_speed_<timestamp>.csv)")
    
    args = parser.parse_args()
    
    if args.output is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = f"internet_speed_{timestamp}.csv"
    else:
        csv_file = args.output
        
    interval_seconds = args.interval * 60
    
    logging.info(f"Starting internet speed measurement every {args.interval} minutes.")
    logging.info(f"Logging results to: {csv_file}")
    
    # Initialize CSV file with headers if it doesn't exist
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "download_mbps", "upload_mbps", "ping_ms"])
            
    while True:
        start_time = time.time()
        try:
            logging.info("Running speedtest...")
            dl, ul, ping = run_speedtest()
            
            timestamp_str = datetime.datetime.now().isoformat()
            
            logging.info(f"Result: Download: {dl:.2f} Mbps | Upload: {ul:.2f} Mbps | Ping: {ping:.2f} ms")
            
            with open(csv_file, mode='a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([timestamp_str, f"{dl:.4f}", f"{ul:.4f}", f"{ping:.4f}"])
                
        except Exception as e:
            logging.error(f"Error during speedtest: {e}")
            
        # Wait for the next interval
        elapsed = time.time() - start_time
        sleep_time = interval_seconds - elapsed
        if sleep_time > 0:
            logging.info(f"Waiting for {sleep_time:.1f} seconds until next measurement.")
            try:
                time.sleep(sleep_time)
            except KeyboardInterrupt:
                logging.info("Measurement stopped by user.")
                break
        else:
            logging.warning("Measurement took longer than the interval!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
