from flask import Flask, render_template, request, redirect, url_for, send_file
import youtube_dl
from googleapiclient.discovery import build
import os

app = Flask(__name__)

# Set up YouTube Data API
YOUTUBE_API_KEY = 'AIzaSyBcwqm5-PyBmc5OtLkgzKIAac0w1AFrqSM'
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    search_response = youtube.search().list(
        q=query,
        part='id,snippet',
        maxResults=10
    ).execute()

    videos = []
    for item in search_response['items']:
        if item['id']['kind'] == 'youtube#video':
            videos.append({
                'title': item['snippet']['title'],
                'videoId': item['id']['videoId'],
                'thumbnail': item['snippet']['thumbnails']['default']['url']
            })

    return render_template('index.html', videos=videos)

@app.route('/download/<video_id>/<resolution>')
def download(video_id, resolution):
    # Define options for youtube_dl
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'verbose': True  # Add verbose flag
    }

    # Initialize youtube_dl
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(f'https://www.youtube.com/watch?v={video_id}', download=True)

        if resolution == 'mp3_320':
            # Convert to 320 kbps MP3
            audio_file = ydl.prepare_filename(info_dict)
            os.system(f'ffmpeg -i "{audio_file}" -b:a 320k "{audio_file[:-4]}_320.mp3"')
            return send_file(f'{audio_file[:-4]}_320.mp3', as_attachment=True)

        elif resolution == 'mp3_128':
            # Convert to 128 kbps MP3
            audio_file = ydl.prepare_filename(info_dict)
            os.system(f'ffmpeg -i "{audio_file}" -b:a 128k "{audio_file[:-4]}_128.mp3"')
            return send_file(f'{audio_file[:-4]}_128.mp3', as_attachment=True)

        # Download video with specified resolution
        for format in info_dict['formats']:
            if format['format_id'] == resolution:
                video_file = ydl.prepare_filename(info_dict)
                os.rename(video_file, f'{video_file[:-4]}.{format["ext"]}')
                return send_file(f'{video_file[:-4]}.{format["ext"]}', as_attachment=True)

    return f"No stream available for resolution {resolution}"

if __name__ == '__main__':
    app.run(debug=True)
