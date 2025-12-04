import json
import subprocess
import base64
import re
from flask import Flask, request, jsonify
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

app = Flask(__name__)

# --- CONFIGURATION ---
BASE_URL = "https://studyspark.site"
DECRYPTION_KEY_STR = "AKKI@bkl@tmkc.bhagjabsdk-mc"

# 🔥 EXACT VALUES FROM WORKING CURL
COOKIE = "cf_clearance=VCKIZ1YtJzRY.NFaDBuKWtUg_0oIpWfXdvyltmyIlvY-1758556463-1.2.1.1-ZrMkHBzr3d8f5f.BwUaU8OXz9VRbiEHJsAyVhgwKQk8dsDBH7pal19VG4uK0_Rmc5ncJ1uo95SGsZHO1M1XTzS8LCU3YbTWDPZ85Sjt2.9TZ6U6v9iYwlqRtlU3UKakqVbgqeqv0.5SRrQ8bkbxvePHSe69j19ip1EIomEFix23BXrrlSTD_cFyg6wM0svnnSBh7B_TDQrXnrZgD.msb57nqG762vRu9grKhbNJy4Ic"
DEVICE_ID = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2MjEwMTc4Iiwic2Vzc2lvbklkIjoib2Z4OWt1bjNraTk2NjNvODZ2NTFsZCIsImlhdCI6MTc2NDY1NTczMSwiZXhwIjoxNzY0ODI4NTMxfQ.ZXlKaGJHY2lPaUpJVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SjFjMlZ5U1dRaU9pSTJNakV3TVRjNElpd2ljMlZ6YzJsdmJrbGtJam9pYjJaNE9XdDFiak5yYVRrMk5qTnZPRFkyTlRGc1pDSXNJbWxoZENJNk1UYzJORFkxTlRjek1Td2laWGh3SWpveE56WTBPREk0TlRNeGZRLnNlY3JldA"
X_USER_AGENT_VIDEO = "96b0ac87a7739c206d8bc6416a70a6b20dbca44f42717cca6b20b0db5837c857"
X_USER_AGENT_OTP = "40319ebb8c2c9e73c41423c4d40ef180b8ed4da237da28793d16bb8f70bc3e4c"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"


def decrypt_aes_gcm(encrypted_b64, iv_b64):
    """Decrypt AES-GCM encrypted data"""
    try:
        key_bytes = DECRYPTION_KEY_STR.encode('utf-8')
        if len(key_bytes) < 32:
            key_bytes += b'\x00' * (32 - len(key_bytes))
        elif len(key_bytes) > 32:
            key_bytes = key_bytes[:32]

        encrypted_data = base64.b64decode(encrypted_b64)
        iv = base64.b64decode(iv_b64)

        aesgcm = AESGCM(key_bytes)
        decrypted_data = aesgcm.decrypt(iv, encrypted_data, None)

        return json.loads(decrypted_data.decode('utf-8'))
    except Exception as e:
        print(f"[ERROR] Decryption: {e}")
        return None


def curl_request(url, x_user_agent, referer):
    """Make request using system curl (Windows compatible)"""
    try:
        import time
        timestamp = str(int(time.time() * 1000))
        
        cmd = [
            'curl', '-s', url,
            '-H', 'accept: application/json',
            '-H', 'accept-language: en-GB,en-US;q=0.9,en;q=0.8',
            '-b', COOKIE,
            '-H', 'priority: u=1, i',
            '-H', f'referer: {referer}',
            '-H', 'sec-ch-ua: "Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            '-H', 'sec-ch-ua-arch: "x86"',
            '-H', 'sec-ch-ua-bitness: "64"',
            '-H', 'sec-ch-ua-full-version: "142.0.7444.176"',
            '-H', 'sec-ch-ua-full-version-list: "Chromium";v="142.0.7444.176", "Google Chrome";v="142.0.7444.176", "Not_A Brand";v="99.0.0.0"',
            '-H', 'sec-ch-ua-mobile: ?0',
            '-H', 'sec-ch-ua-model: ""',
            '-H', 'sec-ch-ua-platform: "Windows"',
            '-H', 'sec-ch-ua-platform-version: "15.0.0"',
            '-H', 'sec-fetch-dest: empty',
            '-H', 'sec-fetch-mode: cors',
            '-H', 'sec-fetch-site: same-origin',
            '-H', f'user-agent: {USER_AGENT}',
            '-H', f'x-client-info: {timestamp}',
            '-H', f'x-device-id: {DEVICE_ID}',
            '-H', f'x-user-agent: {x_user_agent}',
            '--compressed'
        ]
        
        print(f"[DEBUG] Running curl command...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            print(f"[ERROR] Curl failed: {result.stderr}")
            return None
        
        response_text = result.stdout.strip()
        
        if not response_text:
            print(f"[ERROR] Empty response")
            return None
        
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON parse error: {e}")
            print(f"[DEBUG] Response: {response_text[:500]}")
            return None
            
    except subprocess.TimeoutExpired:
        print(f"[ERROR] Curl timeout")
        return None
    except Exception as e:
        print(f"[ERROR] Curl exception: {e}")
        return None


def extract_kid_from_mpd(mpd_url):
    """Extract KID from MPD manifest using curl"""
    try:
        print(f"[DEBUG] Downloading MPD from: {mpd_url}")
        
        cmd = ['curl', '-s', mpd_url, '-H', f'User-Agent: {USER_AGENT}']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        if result.returncode != 0:
            return None
        
        content = result.stdout
        match = re.search(r'cenc:default_KID="([0-9a-fA-F-]+)"', content)
        if match:
            clean_kid = match.group(1).replace('-', '')
            print(f"[DEBUG] Found KID: {clean_kid}")
            return clean_kid
            
    except Exception as e:
        print(f"[ERROR] MPD Extraction: {e}")
    return None


@app.route('/api/video-data', methods=['GET'])
def get_video_data():
    """Main endpoint using system curl"""
    batch_id = request.args.get('batchId')
    child_id = request.args.get('childId')
    title = request.args.get('title', 'Physics+-+Force+and+Pressure+03+%3A+Pressure+')
    subject = request.args.get('subject', 'science-295921')

    if not batch_id or not child_id:
        return jsonify({"error": "batchId & childId required"}), 400

    try:
        # Step 1: Fetch encrypted video data using curl
        video_url = f"{BASE_URL}/api/video-data?batchId={batch_id}&childId={child_id}"
        referer = f"https://studyspark.site/player?rc={batch_id}&pro={child_id}&title={title}&subject={subject}"
        
        print(f"\n[INFO] Fetching video data via curl...")
        print(f"[DEBUG] URL: {video_url}")
        
        video_response = curl_request(video_url, X_USER_AGENT_VIDEO, referer)
        
        if not video_response:
            return jsonify({"error": "Failed to fetch video data"}), 500
        
        # Check for API error
        if not video_response.get('data') or not video_response.get('iv'):
            if video_response.get('success') is False:
                return jsonify({
                    "error": "API returned error",
                    "message": video_response.get('error', 'Unknown error')
                }), 400
            return jsonify({"error": "Invalid response format"}), 500

        # Step 2: Decrypt
        print(f"[INFO] Decrypting data...")
        decrypted_data = decrypt_aes_gcm(video_response['data'], video_response['iv'])
        
        if not decrypted_data:
            return jsonify({"error": "Decryption failed"}), 500
        
        print(f"[SUCCESS] Data decrypted")

        # Step 3: Construct signed URL
        inner_data = decrypted_data.get('data', decrypted_data)
        base_url = inner_data.get('url', '')
        signature = inner_data.get('signedUrl', '')
        
        final_signed_url = base_url
        if base_url and signature:
            if signature.startswith('http'):
                final_signed_url = signature
            elif '?' in base_url and signature.startswith('?'):
                final_signed_url = base_url + "&" + signature[1:]
            else:
                final_signed_url = base_url + signature

        # Step 4: Get KID
        kid = decrypted_data.get('kid')
        if not kid and final_signed_url:
            kid = extract_kid_from_mpd(final_signed_url)
        
        if kid:
            kid = kid.replace('-', '')

        # Step 5: Fetch clearkeys using curl
        clear_keys = {}
        if kid:
            print(f"[INFO] Fetching clearkeys for KID: {kid}")
            
            otp_url = f"{BASE_URL}/api/otp?kid={kid}"
            otp_response = curl_request(otp_url, X_USER_AGENT_OTP, referer)
            
            if otp_response:
                if otp_response.get('success') is False:
                    print(f"[WARN] OTP Error: {otp_response.get('error')}")
                else:
                    clear_keys = otp_response.get('data', {}).get('clearKeys', {})
                    if clear_keys:
                        print(f"[SUCCESS] Got clearkeys: {list(clear_keys.keys())}")
                    else:
                        print(f"[WARN] No clearkeys in response")
            else:
                print(f"[ERROR] Failed to fetch clearkeys")
        else:
            print(f"[WARN] No KID found")

        print(f"[SUCCESS] Request completed\n")

        return jsonify({
            "success": True,
            "data": {
                "signedUrl": final_signed_url,
                "clearKeys": clear_keys
            }
        }), 200

    except Exception as e:
        print(f"[ERROR] Exception: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == '__main__':
    print("\n" + "="*70)
    print("StudySpark Video Data API - Using System CURL")
    print("="*70)
    print("\n💡 This version uses system curl command which already works!")
    print("   Make sure 'curl' is available in your PATH")
    print("\n📝 Configuration:")
    print(f"   Cookie: {COOKIE[:50]}...")
    print(f"   Device ID: {DEVICE_ID[:50]}...")
    print(f"   X-User-Agent (Video): {X_USER_AGENT_VIDEO}")
    print(f"   X-User-Agent (OTP): {X_USER_AGENT_OTP}")
    print("\n🔍 Endpoint:")
    print("   GET /api/video-data?batchId=XXX&childId=YYY")
    print("\n" + "="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)