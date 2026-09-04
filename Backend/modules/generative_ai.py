import base64

import requests
from flask import jsonify


class GenerativeAI:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

    def generate_content(self, contents):
        if not self.api_key:
            return {"error": "AI service is not configured"}, 503
        try:
            response = requests.post(
                self.endpoint,
                params={"key": self.api_key},
                json={"contents": contents},
                timeout=30,
            )
            try:
                body = response.json()
            except ValueError:
                body = {"error": "Invalid response from AI provider"}
            return body, response.status_code
        except requests.RequestException:
            return {"error": "AI provider is temporarily unavailable"}, 502

    def generate_asana_images(self, asana_name, limit):
        return jsonify({
            "error": "Image generation is not enabled. Use the seeded asana image catalogue instead.",
            "status": "fail",
        }), 503
