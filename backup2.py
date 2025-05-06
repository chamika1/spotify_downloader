import requests
import json
import os
import zstandard as zstd
import brotli  # Add this import

def get_spotify_track_metadata(track_url):
    """
    Fetches metadata for a Spotify track using the spotydown.com API
    
    Args:
        track_url (str): The Spotify track URL
        
    Returns:
        dict: Track metadata or None if request fails
    """
    request_url = "https://spotydown.com/api/get-metadata"

    headers = {
        "Host": "spotydown.com",
        "Accept": "*/*",
        # Modify to explicitly exclude brotli if it's causing issues
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/json",
        "Origin": "https://spotydown.com",
        "Priority": "u=1, i",
        "Referer": "https://spotydown.com/",
        "Sec-CH-UA": '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
        "Sec-CH-UA-Mobile": "?1",
        "Sec-CH-UA-Platform": '"Android"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36 Edg/136.0.0.0"
    }

    # Clean the URL by removing any query parameters
    if "?" in track_url:
        track_url = track_url.split("?")[0]
    
    request_payload = {"url": track_url}
    
    try:
        print(f"Sending request to {request_url} with payload: {request_payload}")
        response = requests.post(request_url, headers=headers, json=request_payload)
        
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        # Try multiple approaches to decode the response
        data = None
        
        # First try: Let requests handle it automatically
        try:
            data = response.json()
            print("Successfully decoded JSON directly from response")
        except json.JSONDecodeError:
            print("Failed to decode JSON directly, trying alternative methods...")
            
            # Second try: If content-encoding is brotli, try manual decompression
            if 'content-encoding' in response.headers and 'br' in response.headers['content-encoding'].lower():
                try:
                    print("Attempting Brotli decompression...")
                    # Print first few bytes to debug
                    print(f"Content first 20 bytes: {response.content[:20]}")
                    decompressed_data = brotli.decompress(response.content)
                    data = json.loads(decompressed_data)
                    print("Successfully decompressed Brotli content")
                except Exception as e:
                    print(f"Error decompressing Brotli content: {str(e)}")
                    
                    # Third try: Try to use requests built-in content decoding
                    try:
                        print("Trying to access raw decoded content...")
                        # Sometimes requests might have already decoded it
                        data = json.loads(response.text)
                        print("Successfully decoded from response.text")
                    except json.JSONDecodeError:
                        print("Failed to decode from response.text")
                        
                        # Fourth try: Try a different approach with raw content
                        try:
                            # Try to manually strip any potential BOM or other markers
                            raw_text = response.content.decode('utf-8', errors='ignore')
                            data = json.loads(raw_text)
                            print("Successfully decoded after manual UTF-8 decoding")
                        except Exception as e:
                            print(f"All decoding attempts failed: {str(e)}")
                            return None
        
        if data is None:
            print("Failed to decode response content")
            return None
            
        # Debug the data structure
        print(f"Response data keys: {data.keys() if isinstance(data, dict) else 'Not a dictionary'}")
        
        if "apiResponse" in data and "data" in data["apiResponse"] and len(data["apiResponse"]["data"]) > 0:
            return data["apiResponse"]["data"][0]
        else:
            print(f"Error: Unexpected response format: {data}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        print(f"Response content type: {type(response.content)}")
        print(f"Content preview: {response.content[:100]}")
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
    request_url = "https://spotydown.com/api/download-track"

    headers = {
        "Host": "spotydown.com",
        "Accept": "*/*",
        # Modify to explicitly exclude brotli if it's causing issues
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/json",
        "Origin": "https://spotydown.com",
        "Priority": "u=1, i",
        "Referer": "https://spotydown.com/",
        "Sec-CH-UA": '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
        "Sec-CH-UA-Mobile": "?1",
        "Sec-CH-UA-Platform": '"Android"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36 Edg/136.0.0.0"
    }

    request_payload = {"url": track_url}
    
    try:
        print("Getting download link...")
        response = requests.post(request_url, headers=headers, json=request_payload)
        response.raise_for_status()
        
        # Try multiple approaches to decode the response
        data = None
        
        # First try: Let requests handle it automatically
        try:
            data = response.json()
            print("Successfully decoded JSON directly from response")
        except json.JSONDecodeError:
            print("Failed to decode JSON directly, trying alternative methods...")
            
            # Second try: If content-encoding is brotli, try manual decompression
            if 'content-encoding' in response.headers and 'br' in response.headers['content-encoding'].lower():
                try:
                    print("Attempting Brotli decompression...")
                    decompressed_data = brotli.decompress(response.content)
                    data = json.loads(decompressed_data)
                    print("Successfully decompressed Brotli content")
                except Exception as e:
                    print(f"Error decompressing Brotli content: {str(e)}")
                    
                    # Third try: Try to use requests built-in content decoding
                    try:
                        print("Trying to access raw decoded content...")
                        data = json.loads(response.text)
                        print("Successfully decoded from response.text")
                    except json.JSONDecodeError:
                        print("Failed to decode from response.text")
                        
                        # Fourth try: Try a different approach with raw content
                        try:
                            raw_text = response.content.decode('utf-8', errors='ignore')
                            data = json.loads(raw_text)
                            print("Successfully decoded after manual UTF-8 decoding")
                        except Exception as e:
                            print(f"All decoding attempts failed: {str(e)}")
                            return None
        
        if data is None:
            print("Failed to decode response content")
            return None
        
        if "file_url" in data:
            return data["file_url"]
        else:
            print("Error: No download URL in response")
            return None
            
    except Exception as e:
        print(f"Error getting download link: {str(e)}")
        return None

def download_file(url, filename, output_dir="downloads"):
    """
    Downloads a file from the given URL
    
    Args:
        url (str): The download URL
        filename (str): The filename to save as
        output_dir (str): Directory to save the file
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    filepath = os.path.join(output_dir, f"{filename}.mp3")
    
    try:
        print(f"Downloading track to {filepath}...")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        print(f"Download completed: {filepath}")
        return filepath
    except Exception as e:
        print(f"Error downloading file: {str(e)}")
        return None

def main():
    print("Spotify Track Information and Download Link")
    print("------------------------------------------")
    
    track_url = input("Enter Spotify track URL: ")
    
    print("Fetching track metadata...")
    track_data = get_spotify_track_metadata(track_url)
    
    if track_data:
        print("\nTrack Information:")
        print(f"Name: {track_data['name']}")
        print(f"Artist: {track_data['artist']}")
        print(f"Album: {track_data['album_name']}")
        print(f"Album Artist: {track_data['album_artist']}")
        print(f"Cover URL: {track_data['cover_url']}")
        print(f"Spotify URL: {track_data['url']}")
        
        # Get download link
        print("\nGetting download link...")
        download_url = download_track(track_url)
        if download_url:
            print(f"\nDownload Link: {download_url}")
        else:
            print("Failed to get download URL.")
    else:
        print("Failed to get track metadata.")

if __name__ == "__main__":
    main()





