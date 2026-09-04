from flask import jsonify, request
import requests


def _valid_coordinate(value, minimum, maximum):
    try:
        value = float(value)
        return minimum <= value <= maximum
    except (TypeError, ValueError):
        return False


def routes_location(app):
    @app.route('/api/geocode/reverse', methods=['GET'])
    def reverse_geocode():
        lat = request.args.get('lat')
        lon = request.args.get('lon')
        if not _valid_coordinate(lat, -90, 90) or not _valid_coordinate(lon, -180, 180):
            return jsonify({'error': 'Valid latitude and longitude are required', 'status': 'fail'}), 400
        try:
            response = requests.get(
                'https://nominatim.openstreetmap.org/reverse',
                params={'lat': lat, 'lon': lon, 'format': 'jsonv2', 'zoom': 18},
                headers={'User-Agent': 'Shravan/2.0 (health-app)'},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            return jsonify({'address': data.get('display_name'), 'status': 'success'}), 200
        except requests.RequestException:
            return jsonify({'error': 'Geocoding service is temporarily unavailable', 'status': 'fail'}), 502

    @app.route('/api/geocode/search', methods=['GET'])
    def search_location():
        query = request.args.get('q', '').strip()
        if not query or len(query) > 200:
            return jsonify({'error': 'A location query is required', 'status': 'fail'}), 400
        try:
            response = requests.get(
                'https://nominatim.openstreetmap.org/search',
                params={'q': query, 'format': 'jsonv2', 'limit': 1},
                headers={'User-Agent': 'Shravan/2.0 (health-app)'},
                timeout=10,
            )
            response.raise_for_status()
            results = response.json()
            if not results:
                return jsonify({'location': None, 'status': 'success'}), 200
            result = results[0]
            return jsonify({'location': {
                'lat': float(result['lat']),
                'lng': float(result['lon']),
                'formatted_address': result.get('display_name'),
            }, 'status': 'success'}), 200
        except (requests.RequestException, ValueError, KeyError):
            return jsonify({'error': 'Geocoding service is temporarily unavailable', 'status': 'fail'}), 502
