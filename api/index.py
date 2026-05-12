from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import traceback

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({
        "status": "✅ API Working",
        "message": "Universal Video Downloader (YouTube, TikTok, Instagram, Facebook)"
    })

@app.route('/download', methods=['POST'])
def download():
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({"success": False, "error": "URL is required"}), 400

        url = data['url'].strip()

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'extract_flat': False,
            'nocheckcertificate': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
            },
            'format': 'best[height<=720]/bestvideo[height<=720]+bestaudio/best',
            'merge_output_format': 'mp4',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            download_url = info.get('url') or (info.get('formats')[-1].get('url') if info.get('formats') else None)
            platform = info.get('extractor_key') or info.get('ie_key') or 'Unknown'

            return jsonify({
                "success": True,
                "title": info.get('title'),
                "thumbnail": info.get('thumbnail'),
                "download_url": download_url,
                "platform": platform,
                "duration": info.get('duration'),
                "original_url": url
            })

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)