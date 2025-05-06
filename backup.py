import requests
import json
import os
import zstandard as zstd

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
        "Accept-Encoding": "gzip, deflate, br",  # Changed from zstd to standard encodings
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
        
        # Let requests handle the decompression automatically
        try:
            data = response.json()
            print(f"Response data preview: {str(data)[:200]}...")  # Debug print
        except json.JSONDecodeError:
            print("Failed to decode JSON, trying to decode raw content...")
            print(f"Raw content preview: {response.content[:100]}")
            return None
        
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
        "Accept-Encoding": "gzip, deflate, br",
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
        
        data = response.json()
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





