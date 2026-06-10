import requests
import re
import os
import urllib3

# এসএসএল (SSL) ওয়ার্নিং বন্ধ করার জন্য
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

INPUT_M3U = "all_channels.m3u" 
OUTPUT_M3U = "active_channels.m3u"

def check_link(url):
    # কিছু লিঙ্ক খালি থাকতে পারে বা ফরম্যাট ভুল হতে পারে, তাই শুরুতেই চেক
    if not url or not url.startswith("http"):
        return False
        
    # ব্রাউজারের মতো ইউজার এজেন্ট দেওয়া হলো যেন ওটিটি সার্ভার রিকোয়েস্ট ব্লক না করে
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        # প্রথমে HEAD দিয়ে টেস্ট করবে (SSL ভেরিফিকেশন স্কিপ করে দ্রুত করার জন্য verify=False)
        response = requests.head(url, headers=headers, timeout=5, allow_redirects=True, verify=False)
        if response.status_code in [200, 201, 301, 302]:
            return True
            
        # HEAD ফেল করলে GET দিয়ে শেষ চেষ্টা
        response = requests.get(url, headers=headers, timeout=5, stream=True, verify=False)
        if response.status_code in [200, 201]:
            return True
    except Exception as e:
        # কোনো লিঙ্কে এরর আসলে কোড ক্র্যাশ করবে না, শুধু লগ প্রিন্ট করবে
        print(f" (Error checking link: {str(e)}) ", end="")
        
    return False

def parse_and_filter_m3u():
    if not os.path.exists(INPUT_M3U):
        print(f"CRITICAL ERROR: '{INPUT_M3U}' file not found!")
        return

    print(f"Reading '{INPUT_M3U}'...")
    with open(INPUT_M3U, "r", encoding="utf-8") as f:
        content = f.read()

    # রেগুলার এক্সপ্রেশন উন্নত করা হয়েছে যেন কোনো ভাঙা ফরম্যাট আসলেও সমস্যা না হয়
    pattern = re.compile(r'(#EXTINF:[^\n]*\n)(http[s]?://[^\s]+)')
    matches = pattern.findall(content)
    
    print(f"Total channels found in database: {len(matches)}")
    
    active_count = 0
    with open(OUTPUT_M3U, "w", encoding="utf-8") as out_f:
        out_f.write("#EXTM3U\n\n")
        
        for idx, (extinf, url) in enumerate(matches, 1):
            clean_url = url.strip()
            print(f"[{idx}/{len(matches)}] Testing stream... ", end="")
            
            # পাইথন যেন কোনো এররের কারণে মাঝপথে বন্ধ না হয় তার জন্য সেফটি ট্রাই-ক্যাচ
            try:
                if check_link(clean_url):
                    print("🟢 ACTIVE")
                    out_f.write(extinf)
                    out_f.write(clean_url + "\n\n")
                    active_count += 1
                else:
                    print("🔴 DEAD")
            except Exception as loop_error:
                print(f"🔴 FAILED IN LOOP: {str(loop_error)}")

    print(f"Task finished! Total active channels written: {active_count}")

if __name__ == "__main__":
    parse_and_filter_m3u()
