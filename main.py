import csv
import requests
import os
import sys
import zipfile
import yaml
import concurrent.futures # Import the concurrent futures module
import math
import time

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

resolution = config['resolution']
file_type = config['file_type']
unzip = config['unzip']
unzipping_directory = config['unzip']['folder']
downloads_directory = config['downloads_folder']

if resolution not in ["1K", "2K", "4K", "8K"] or file_type not in ["PNG", "JPG"]:
    print("Invalid format or type. Valid formats: 1k, 2k, 4k, 8k. Valid types: png, jpg.")
    sys.exit(1)

os.makedirs(downloads_directory, exist_ok=True)
os.makedirs(unzipping_directory, exist_ok=True)

csv_url = "https://ambientCG.com/api/v2/downloads_csv"
response = requests.get(csv_url)
csv_file = "downloads.csv"

with open(csv_file, "wb") as file:
    file.write(response.content)

# Define the resolutions to exclude
negate_resolutions = ["12K", "16K"]

# --- New Function for Concurrent Downloads and Throughput monitoring ---
def download_file(download_url, file_name):
    """Handles the downloading of a single file and displays throughput."""
    if os.path.exists(file_name):
        print(f"[SKIPPING] {file_name} already exists.")
        return
    
    print(f"[STARTING] Downloading {file_name}...")
    start_time = time.time()
    downloaded_bytes = 0

    try:
        # Use stream=True to download content in chunks
        with requests.get(download_url, stream=True, timeout=30) as zip_response:
            zip_response.raise_for_status() # Raise an exception for bad status codes

            # Determine total file size for potential progress tracking
            total_size = int(zip_response.headers.get('content-length', 0))

            with open(file_name, "wb") as zip_file:
                # Iterate over chunks of data
                for chunk in zip_response.iter_content(chunk_size=8192):
                    if chunk: # Filter out keep-alive new chunks
                        zip_file.write(chunk)
                        downloaded_bytes += len(chunk)
                        
                        # Calculate elapsed time and throughput
                        elapsed_time = time.time() - start_time
                        if elapsed_time > 0:
                            # Throughput in KB/s
                            throughput = (downloaded_bytes / 1024) / elapsed_time 
                            # Use carriage return \r to update the current line in the console
                            print(f"\r[DOWNLOADING] {file_name} -> {downloaded_bytes / (1024 * 1024):.1f} MB / {total_size / (1024 * 1024):.1f} MB | Speed: {throughput:.2f} KB/s", end='')
        
        # Newline after download is complete
        print(f"\r[COMPLETE] {file_name} downloaded successfully. Total time: {time.time() - start_time:.2f}s")

    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR] Error downloading {file_name}: {e}")
# --- End of New Function ---

# --- Modify the Main Download Loop to use ThreadPoolExecutor ---
files_to_download = []
with open(csv_file, "r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        # Check if any of the negate_resolutions are present in the downloadAttribute string
        is_negated = any(neg_res in row["downloadAttribute"] for neg_res in negate_resolutions)

        # Added "not is_negated" condition to skip negated resolutions
        if not is_negated and resolution in row["downloadAttribute"] and file_type in row["downloadAttribute"]:
            download_url = row["downloadLink"]
            file_name = os.path.join(downloads_directory, download_url.split("file=")[1])
            files_to_download.append((download_url, file_name))

# Use ThreadPoolExecutor to download files concurrently
CPU_Threads = os.cpu_count() or 4  # Fallback to 4 if os.cpu_count() returns None
initConcurrentDL_Threads = max(2, math.floor(CPU_Threads * 1.25))  # Minor over commit threads by factor of 25%, but maintian minimum of 2
CalcDL_Threads = math.ceil(initConcurrentDL_Threads) # If fraction, round up to nearest integer
if CalcDL_Threads % 2 != 0:
    CalcDL_Threads += 1
MaxConcurrentDL_Threads = min(CalcDL_Threads, 8)  # Cap the maximum number of threads to 8
with concurrent.futures.ThreadPoolExecutor(max_workers=MaxConcurrentDL_Threads) as executor:
    # Submit all download tasks to the executor
    future_downloads = [executor.submit(download_file, url, name) for url, name in files_to_download]
    
    # Optional: Wait for all futures to complete and handle exceptions if necessary
    for future in concurrent.futures.as_completed(future_downloads):
        try:
            future.result() # This re-raises any exceptions caught during the download_file function execution
        except Exception as e:
            print(f"A download task failed: {e}")
            # Note: The download_file function already prints error messages
            pass

# --- Rest of the script remains unchanged ---
if unzip:
    for file in os.listdir(downloads_directory):
        with zipfile.ZipFile(f"{downloads_directory}/{file}", 'r') as zip_ref:
            if not os.path.exists(f"{unzipping_directory}/{file[:-4]}"):
                print(file + " extracted.")
                zip_ref.extractall(unzipping_directory + "/" + file[:-4])
            else:
                print(f"{file} already extracted. Skipping...")

def delete_files(file_type):
    for directory in os.listdir(unzipping_directory):
        for file in os.listdir(os.path.join(unzipping_directory, directory)):
            if file_type in file:
                print(f'Found {file_type} at {unzipping_directory}/{directory}. Deleting...')
                os.remove(os.path.join(unzipping_directory, directory, file))

for file_type in config['keep_files']:
    match file_type:
        case "color":
            if not config['keep_files']['color']:
                delete_files("Color")
        
        case "roughness":
            if not config['keep_files']['roughness']:
                delete_files("Roughness")

        case "normal_gl":
            if not config['keep_files']['normal_gl']:
                delete_files("NormalGL")
        
        case "normal_dx":
            if not config['keep_files']['normal_dx']:
                delete_files("NormalDX")

        case "metalness":
            if not config['keep_files']['metalness']:
                delete_files("Metalness")

        case "opacity":
            if not config['keep_files']['opacity']:
                delete_files("Opacity")

        case "ambient_occlusion":
            if not config['keep_files']['ambient_occlusion']:
                delete_files("AmbientOcclusion")
        
        case "displacement":
                    if not config['keep_files']['displacement']:
                        delete_files("Displacement")

        case "cover":
            if not config['keep_files']['ambient_occlusion']:
                for directory in os.listdir(unzipping_directory):
                    for file in os.listdir(os.path.join(unzipping_directory, directory)):
                        if not any(keyword in file for keyword in ["Color", "Roughness", "NormalGL", "NormalDX","Metalness", "AmbientOcclusion", "Opacity", "Displacement"]):
                            print(f'Found {file_type} at {unzipping_directory}/{directory}. Deleting...')
                            os.remove(os.path.join(unzipping_directory, directory, file))