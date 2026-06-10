import requests
import re

INPUT_M3U = "all_channels.m3u" 
OUTPUT_M3U = "active_channels.m3u"

def check_link(url):
    try:
        # প্রথমে HEAD রিকোয়েস্ট দিয়ে চেক করবে দ্রুত হওয়ার জন্য
        response = requests.head(url, timeout=4, allow_redirects=True)
        if response.status_code == 200:
            return True
        # কিছু ওটিটি সার্ভার HEAD ব্লক করলে GET দিয়ে শেষ চেষ্টা করবে
        response = requests.get(url, timeout=4, stream=True)
        return response.status_code == 200
    except:
        return False

def parse_and_filter_m3u():
    try:
        with open(INPUT_M3U, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print("Error: all_channels.m3u file not found!")
        return

    pattern = re.compile(r'(#EXTINF:.*?\n)(http[s]?://[^\s]+)')
    matches = pattern.findall(content)
    
    with open(OUTPUT_M3U, "w", encoding="utf-8") as out_f:
        out_f.write("#EXTM3U\n\n")
        
        for extinf, url in matches:
            if check_link(url.strip()):
                out_f.write(extinf)
                out_f.write(url + "\n\n")

if __name__ == "__main__":
    parse_and_filter_m3u()
