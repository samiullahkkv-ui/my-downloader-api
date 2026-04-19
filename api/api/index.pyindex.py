from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import yt_dlp
import requests

app = Flask(__name__)
CORS(app) # Is se aapki API har jagah chal sakegi

# TikTok Bypass Logic
def get_tiktok_api(url):
    try:
        r = requests.get("https://www.tikwm.com/api/", params={'url': url}).json()
        if r.get('code') == 0:
            d = r['data']
            return {
                "status": "success",
                "title": d.get('title'),
                "thumbnail": d.get('cover'),
                "video": d.get('play'),
                "audio": d.get('music'),
                "likes": d.get('digg_count'),
                "views": d.get('play_count')
            }
    except:
        return None

@app.route('/api/extract', methods=['POST'])
def extract():
    data = request.json
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({"status": "error", "message": "Link lazmi hai!"}), 400

    # First check TikTok
    if 'tiktok.com' in url:
        res = get_tiktok_api(url)
        if res: return jsonify(res)

    # General extraction for Instagram, FB, etc.
    try:
        ydl_opts = {'quiet': True, 'nocheckcertificate': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "status": "success",
                "title": info.get('title'),
                "thumbnail": info.get('thumbnail'),
                "video": info.get('url'),
                "audio": info.get('url'),
                "likes": info.get('like_count', 'N/A'),
                "views": info.get('view_count', 'N/A')
            })
    except Exception as e:
        return jsonify({"status": "error", "message": "Link support nahi ho raha."}), 500

# Force Download Route (Browser Fix)
@app.route('/api/download')
def download_proxy():
    file_url = request.args.get('url')
    name = request.args.get('name', 'video.mp4')
    
    if not file_url:
        return "URL Missing", 400
        
    req = requests.get(file_url, stream=True)
    return Response(req.iter_content(chunk_size=1024*8), headers={
        "Content-Disposition": f"attachment; filename={name}",
        "Content-Type": "application/octet-stream"
    })

# --- VERCEL SPECIFIC CONFIG ---
app = app # Ye line Vercel ko app object pehchanne mein madad karti hai

if __name__ == '__main__':
    app.run()
