import requests
import json
import os
import zstandard as zstd
import brotli
import time  # Add this for timing operations

# Set global timeout for all requests
REQUEST_TIMEOUT = 15  # seconds

def get_spotify_track_metadata(track_url):
    """
    Fetches metadata for a Spotify track using the spotydown.com API
    
    Args:
        track_url (str): The Spotify track URL
        
    Returns:
        dict: Track metadata or None if request fails
    """
    start_time = time.time()  # Track start time
    request_url = "https://spotydown.com/api/get-metadata"

    headers = {
        "Host": "spotydown.com",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/json",
        "Origin": "https://spotydown.com",
        "Referer": "https://spotydown.com/",
        "User-Agent": "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36 Edg/136.0.0.0"
    }

    # Clean the URL by removing any query parameters
    if "?" in track_url:
        track_url = track_url.split("?")[0]
    
    request_payload = {"url": track_url}
    
    try:
        print(f"Fetching track metadata...")
        response = requests.post(
            request_url, 
            headers=headers, 
            json=request_payload,
            timeout=REQUEST_TIMEOUT  # Add timeout
        )
        
        # Try multiple approaches to decode the response
        data = None
        
        # First try: Let requests handle it automatically
        try:
            data = response.json()
        except json.JSONDecodeError:
            # Second try: If content-encoding is brotli, try manual decompression
            if 'content-encoding' in response.headers and 'br' in response.headers['content-encoding'].lower():
                try:
                    decompressed_data = brotli.decompress(response.content)
                    data = json.loads(decompressed_data)
                except Exception:
                    # Third try: Try to use requests built-in content decoding
                    try:
                        data = json.loads(response.text)
                    except json.JSONDecodeError:
                        # Fourth try: Try a different approach with raw content
                        try:
                            raw_text = response.content.decode('utf-8', errors='ignore')
                            data = json.loads(raw_text)
                        except Exception:
                            return None
        
        if data is None:
            return None
            
        if "apiResponse" in data and "data" in data["apiResponse"] and len(data["apiResponse"]["data"]) > 0:
            elapsed_time = time.time() - start_time
            print(f"Metadata fetched in {elapsed_time:.2f} seconds")
            return data["apiResponse"]["data"][0]
        else:
            print(f"Error: Unexpected response format")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None

def save_track_info(track_data, output_dir="downloads"):
    """
    Saves track information to a text file
    
    Args:
        track_data (dict): Track metadata
        output_dir (str): Directory to save the file
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create a filename based on track name and artist
    filename = f"{track_data['name']} - {track_data['artist']}.txt"
    filepath = os.path.join(output_dir, filename)
    
    # Write track information to file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"Track Name: {track_data['name']}\n")
        f.write(f"Artist: {track_data['artist']}\n")
        f.write(f"Album: {track_data['album_name']}\n")
        f.write(f"Album Artist: {track_data['album_artist']}\n")
        f.write(f"Cover URL: {track_data['cover_url']}\n")
        f.write(f"Spotify URL: {track_data['url']}\n")
    
    print(f"Track information saved to {filepath}")
    return filepath

def download_track(track_url):
    """
    Downloads the track using spotydown.com API
    
    Args:
        track_url (str): The Spotify track URL
        
    Returns:
        str: Download URL or None if request fails
    """
    start_time = time.time()  # Track start time
    request_url = "https://spotydown.com/api/download-track"

    headers = {
        "Host": "spotydown.com",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/json",
        "Origin": "https://spotydown.com",
        "Referer": "https://spotydown.com/",
        "User-Agent": "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36 Edg/136.0.0.0"
    }

    request_payload = {"url": track_url}
    
    try:
        print("Getting download link...")
        response = requests.post(
            request_url, 
            headers=headers, 
            json=request_payload,
            timeout=REQUEST_TIMEOUT  # Add timeout
        )
        response.raise_for_status()
        
        # Try multiple approaches to decode the response
        data = None
        
        # First try: Let requests handle it automatically
        try:
            data = response.json()
        except json.JSONDecodeError:
            # Second try: If content-encoding is brotli, try manual decompression
            if 'content-encoding' in response.headers and 'br' in response.headers['content-encoding'].lower():
                try:
                    decompressed_data = brotli.decompress(response.content)
                    data = json.loads(decompressed_data)
                except Exception:
                    # Third try: Try to use requests built-in content decoding
                    try:
                        data = json.loads(response.text)
                    except json.JSONDecodeError:
                        # Fourth try: Try a different approach with raw content
                        try:
                            raw_text = response.content.decode('utf-8', errors='ignore')
                            data = json.loads(raw_text)
                        except Exception:
                            return None
        
        if data is None:
            return None
        
        if "file_url" in data:
            elapsed_time = time.time() - start_time
            print(f"Download link obtained in {elapsed_time:.2f} seconds")
            return data["file_url"]
        else:
            print("Error: No download URL in response")
            return None
            
    except Exception as e:
        print(f"Error getting download link: {str(e)}")
        return None

# Add this at the top of the file if not already present
import time

# Set global timeout for all requests if not already defined
REQUEST_TIMEOUT = 30  # seconds

def download_file(url, filename, output_dir="downloads"):
    """
    Downloads a file from the given URL
    
    Args:
        url (str): The download URL
        filename (str): The filename to save as
        output_dir (str): Directory to save the file
    """
    start_time = time.time()  # Track start time
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    filepath = os.path.join(output_dir, f"{filename}.mp3")
    
    try:
        print(f"Downloading track to {filepath}...")
        
        # Use a session for better performance
        session = requests.Session()
        
        # First make a HEAD request to get file size
        head_response = session.head(url, timeout=REQUEST_TIMEOUT)
        file_size = int(head_response.headers.get('content-length', 0))
        print(f"Expected file size: {file_size/1024/1024:.2f} MB")
        
        # Download with progress tracking
        response = session.get(url, stream=True, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        downloaded_size = 0
        chunk_size = 1024 * 1024  # 1MB chunks for faster download
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    percent = (downloaded_size / file_size) * 100 if file_size > 0 else 0
                    print(f"Downloaded: {downloaded_size/1024/1024:.2f} MB ({percent:.1f}%)", end='\r')
        
        # Verify file size
        actual_size = os.path.getsize(filepath)
        if file_size > 0 and actual_size < file_size * 0.95:  # Allow 5% difference
            print(f"\nWarning: Downloaded file ({actual_size/1024/1024:.2f} MB) is smaller than expected ({file_size/1024/1024:.2f} MB)")
        
        elapsed_time = time.time() - start_time
        print(f"\nDownload completed in {elapsed_time:.2f} seconds: {filepath}")
        return filepath
    except Exception as e:
        print(f"Error downloading file: {str(e)}")
        return None

def download_track_direct(track_url, output_dir="downloads"):
    """
    One-step function to download a track directly
    
    Args:
        track_url (str): The Spotify track URL
        output_dir (str): Directory to save the file
        
    Returns:
        str: Path to downloaded file or None if failed
    """
    print(f"Processing Spotify track: {track_url}")
    
    # Get track metadata
    track_data = get_spotify_track_metadata(track_url)
    if not track_data:
        print("Failed to get track metadata")
        return None
    
    # Get download URL
    download_url = download_track(track_url)
    if not download_url:
        print("Failed to get download URL")
        return None
    
    # Create a clean filename
    filename = f"{track_data['name']} - {track_data['artist']}"
    # Remove characters that are invalid in filenames
    filename = "".join(c for c in filename if c not in r'<>:"/\|?*')
    
    # Download the file
    return download_file(download_url, filename, output_dir)

def main():
    print("Spotify Track Information and Download Link")
    print("------------------------------------------")
    
    track_url = input("Enter Spotify track URL: ")
    
    # Use the direct download function for faster processing
    filepath = download_track_direct(track_url)
    
    if filepath:
        print(f"Track successfully downloaded to: {filepath}")
    else:
        print("Failed to download track.")

if __name__ == "__main__":
    main()





