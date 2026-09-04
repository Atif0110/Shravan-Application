import math

import requests


class NearbyPlaces:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.timeout = 10

    def _google_nearby(self, lat, lon, place_type, radius):
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        response = requests.get(
            url,
            params={"location": f"{lat},{lon}", "radius": radius, "type": place_type, "key": self.api_key},
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json().get("results", [])

    def _google_details(self, place_id):
        url = "https://maps.googleapis.com/maps/api/place/details/json"
        response = requests.get(
            url,
            params={"placeid": place_id, "fields": "name,rating,user_ratings_total,formatted_phone_number,website,opening_hours,geometry,formatted_address,types", "key": self.api_key},
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json().get("result", {})

    def _osm_nearby(self, lat, lon, place_type, radius):
        tag = "amenity=hospital" if place_type in {"hospital", "clinic", "doctor"} else "amenity=pharmacy"
        query = f"[out:json][timeout:10];nwr[{tag}](around:{min(max(int(radius), 100), 5000)},{lat},{lon});out center tags;"
        response = requests.post(
            "https://overpass-api.de/api/interpreter",
            data=query,
            headers={"User-Agent": "Shravan/2.0 (health-app)"},
            timeout=15,
        )
        response.raise_for_status()
        results = []
        for item in response.json().get("elements", []):
            tags = item.get("tags", {})
            center = item.get("center", {})
            item_lat = item.get("lat", center.get("lat"))
            item_lon = item.get("lon", center.get("lon"))
            if item_lat is None or item_lon is None:
                continue
            distance = self._distance_m(lat, lon, item_lat, item_lon)
            results.append({
                "place_id": f"osm:{item.get('type')}:{item.get('id')}",
                "name": tags.get("name", "Unnamed place"),
                "vicinity": ", ".join(filter(None, [tags.get("addr:housenumber"), tags.get("addr:street"), tags.get("addr:city")])),
                "formatted_address": ", ".join(filter(None, [tags.get("addr:street"), tags.get("addr:city"), tags.get("addr:postcode")])),
                "geometry": {"location": {"lat": item_lat, "lng": item_lon}},
                "rating": None,
                "user_ratings_total": 0,
                "formatted_phone_number": tags.get("phone") or tags.get("contact:phone"),
                "website": tags.get("website") or tags.get("contact:website"),
                "business_status": "OPERATIONAL",
                "types": [place_type],
                "distance": distance,
            })
        return sorted(results, key=lambda x: x["distance"])

    @staticmethod
    def _distance_m(lat1, lon1, lat2, lon2):
        radius = 6371000
        p1, p2 = math.radians(lat1), math.radians(lat2)
        dp = math.radians(lat2 - lat1)
        dl = math.radians(lon2 - lon1)
        a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
        return 2 * radius * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def find_nearby_places(self, lat, lon, type="hospital", radius=5000):
        try:
            lat = float(lat)
            lon = float(lon)
            radius = min(max(int(radius), 100), 5000)
            if self.api_key:
                return self._google_nearby(lat, lon, type, radius)
            return self._osm_nearby(lat, lon, type, radius)
        except (TypeError, ValueError, requests.RequestException):
            return []

    def place_details(self, place_id):
        if place_id and str(place_id).startswith("osm:"):
            return {}
        if not self.api_key:
            return {}
        try:
            return self._google_details(place_id)
        except requests.RequestException:
            return {}
