import requests
import time
import json
import re

def is_valid_url(url: str) -> bool:
    """Validate the URL format."""
    pattern = re.compile(r'^(http|https)://[^\s/$.?#].[^\s]*$', re.IGNORECASE)
    return re.match(pattern, url) is not None

def download_content(url: str, output_file: str, pause_event=None, log_function=None, progress_callback=None) -> bool:
    """Downloads content from a URL and saves it to a file with a progress bar, supporting pause/resume."""
    if not is_valid_url(url):
        raise ValueError("Invalid URL")
    
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, stream=True, timeout=10)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        if total_size == 0:
            log_function("Unable to determine the file size.")
            return False

        start_time = time.time()
        downloaded = 0

        with open(output_file, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if pause_event and not pause_event.is_set():  # Pause if the event is cleared
                    log_function("Download paused...")
                    pause_event.wait()  # Wait until the event is set to resume
                    log_function("Download resumed...")

                if chunk:
                    file.write(chunk)
                    downloaded += len(chunk)

                    elapsed_time = time.time() - start_time
                    download_speed = downloaded / elapsed_time if elapsed_time > 0 else 0
                    time_remaining = (total_size - downloaded) / download_speed if download_speed > 0 else float('inf')
                    progress = (downloaded / total_size) * 100

                    # Update progress and log
                    if callable(progress_callback):
                        progress_callback(progress, download_speed, time_remaining)
                    if callable(log_function):
                        log_function(f"Progress: {progress:.2f}% | Speed: {download_speed / 1024:.2f} KB/s | Time Remaining: {time_remaining:.2f}s")

        log_function(f"Download completed and saved to '{output_file}'.")
        return True
    except requests.exceptions.RequestException as e:
        log_function(f"Error: {e}")
        return False
