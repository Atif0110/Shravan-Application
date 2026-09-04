from flask import Flask, request, jsonify
from models import db, YogaVideos
from flasgger.utils import swag_from
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def routes_content(app, db):
    @app.route('/api/youtube/search', methods=['GET'])
    def youtube_search():
        """
        Searches YouTube for yoga videos using the server-side YOUTUBE_API_KEY,
        so the key never has to be exposed to the browser. Caretakers/NGOs use
        this to find and pick a video instead of pasting a raw URL.
        Query params: q (search text, required), max_results (optional, default 8)
        """
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'error': 'q (search query) is required', 'status': 'fail'}), 400

        api_key = os.environ.get('YOUTUBE_API_KEY')
        if not api_key:
            return jsonify({
                'error': 'YOUTUBE_API_KEY is not configured on the server. '
                         'Add it to Backend/.env to enable YouTube search.',
                'status': 'fail'
            }), 503

        max_results = min(request.args.get('max_results', 8, type=int), 25)

        try:
            resp = requests.get(
                'https://www.googleapis.com/youtube/v3/search',
                params={
                    'part': 'snippet',
                    'q': f'{query} yoga',
                    'type': 'video',
                    'maxResults': max_results,
                    'safeSearch': 'strict',
                    'key': api_key,
                },
                timeout=10,
            )
            data = resp.json()

            if resp.status_code != 200:
                return jsonify({
                    'error': data.get('error', {}).get('message', 'YouTube API error'),
                    'status': 'fail'
                }), resp.status_code

            results = []
            for item in data.get('items', []):
                video_id = item.get('id', {}).get('videoId')
                snippet = item.get('snippet', {})
                if not video_id:
                    continue
                results.append({
                    'video_id': video_id,
                    'title': snippet.get('title'),
                    'description': snippet.get('description'),
                    'channel_title': snippet.get('channelTitle'),
                    'thumbnail_url': snippet.get('thumbnails', {}).get('medium', {}).get('url'),
                    'video_url': f'https://www.youtube.com/watch?v={video_id}',
                })

            return jsonify({'status': 'success', 'results': results}), 200

        except requests.exceptions.RequestException as e:
            return jsonify({'error': f'Failed to reach YouTube API: {str(e)}', 'status': 'fail'}), 502

    @app.route('/api/yoga-videos', methods=['GET'])
    @swag_from("docs/get_yoga_videos.yml")
    def get_yoga_videos():
        difficulty = request.args.get('difficulty')
        query = YogaVideos.query
        if difficulty:
            query = query.filter_by(difficulty=difficulty)

        videos = query.all()
        video_list = [{
            'id': v.video_id,
            'title': v.title,
            'description': v.description,
            'video_url': v.video_url,
            'difficulty': v.difficulty,
            'duration': v.duration_minutes
        } for v in videos]

        return jsonify({'videos': video_list}), 200

    @app.route('/api/yoga-videos', methods=['POST'])
    @swag_from("docs/post_yoga_video.yml")
    def create_yoga_video():
        data = request.get_json(silent=True) or {}
        title = str(data.get('title') or '').strip()
        video_url = str(data.get('video_url') or '').strip()
        if not title or not video_url or len(title) > 255:
            return jsonify({'error': 'title and video_url are required', 'status': 'fail'}), 400
        video = YogaVideos(
            title=title,
            description=str(data.get('description') or '').strip()[:5000] or None,
            video_url=video_url[:1000],
            difficulty=str(data.get('difficulty') or '').strip()[:50] or None,
            duration_minutes=data.get('duration')
        )
        db.session.add(video)
        db.session.commit()
        return jsonify({'message': 'Yoga video created', 'id': video.video_id}), 201

    @app.route('/api/yoga-videos/<int:video_id>', methods=['PUT'])
    @swag_from("docs/put_yoga_video.yml")
    def update_yoga_video(video_id):
        data = request.get_json()
        video = YogaVideos.query.get_or_404(video_id)
        video.title = data.get('title', video.title)
        video.description = data.get('description', video.description)
        video.video_url = data.get('video_url', video.video_url)
        video.difficulty = data.get('difficulty', video.difficulty)
        video.duration_minutes = data.get('duration', video.duration_minutes)
        db.session.commit()
        return jsonify({'message': 'Yoga video updated'}), 200

    @app.route('/api/yoga-videos/<int:video_id>', methods=['DELETE'])
    @swag_from("docs/delete_yoga_video.yml")
    def delete_yoga_video(video_id):
        video = YogaVideos.query.get_or_404(video_id)
        db.session.delete(video)
        db.session.commit()
        return jsonify({'message': 'Yoga video deleted'}), 200
