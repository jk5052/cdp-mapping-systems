import os
import re
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


class GooglePlacesClient:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_PLACES_KEY")
        self.base_url = "https://maps.googleapis.com/maps/api"

        if not self.api_key:
            st.error("Google Places API key not found in .env file")

    def nearby_search(self, lat, lng, radius=1000, place_type=None, keyword=None):
        """Google Places Nearby Search"""

        url = f"{self.base_url}/place/nearbysearch/json"

        params = {"location": f"{lat},{lng}", "radius": radius, "key": self.api_key}

        if place_type:
            params["type"] = place_type
        if keyword:
            params["keyword"] = keyword

        try:
            response = requests.get(url, params=params)
            data = response.json()

            if data["status"] == "OK":
                return data.get("results", [])
            else:
                st.warning(f"Google Places API: {data['status']}")
                return []

        except Exception as e:
            st.error(f"Google Places API 호출 실패: {e}")
            return []

    def get_place_details(self, place_id):
        """장소 상세 정보"""

        url = f"{self.base_url}/place/details/json"

        params = {
            "place_id": place_id,
            "fields": "name,rating,formatted_address,types,geometry,photos,reviews",
            "key": self.api_key,
        }

        try:
            response = requests.get(url, params=params)
            data = response.json()

            if data["status"] == "OK":
                return data.get("result", {})
            else:
                return None

        except Exception as e:
            st.warning(f"장소 상세정보 실패: {e}")
            return None

    def analyze_place_personality(self, place_data):
        """장소의 주관적 특성 분석 - 리뷰 기반"""

        reviews = place_data.get("reviews", [])
        if not reviews:
            return {}, {}

        review_text = " ".join([review.get("text", "") for review in reviews]).lower()

        # 감성 키워드 사전 - 더 구체적이고 감성적으로
        personality_keywords = {
            "creative": [
                "artistic",
                "creative",
                "inspiring",
                "aesthetic",
                "unique",
                "bohemian",
                "gallery",
                "design",
                "art",
                "music",
                "vintage",
                "hipster",
                "indie",
                "instagram",
                "photogenic",
                "beautiful",
                "stylish",
                "trendy",
                "cool",
                "atmosphere",
                "vibe",
                "character",
                "charm",
            ],
            "healing": [
                "peaceful",
                "calm",
                "quiet",
                "relaxing",
                "zen",
                "tranquil",
                "serene",
                "meditation",
                "nature",
                "garden",
                "cozy",
                "comfortable",
                "warm",
                "escape",
                "refuge",
                "sanctuary",
                "mindful",
                "therapeutic",
                "soothing",
                "stress relief",
                "recharge",
            ],
            "social": [
                "lively",
                "social",
                "community",
                "friendly",
                "bustling",
                "vibrant",
                "meeting place",
                "gathering",
                "conversation",
                "networking",
                "date",
                "group",
                "friends",
                "people watching",
                "atmosphere",
                "energy",
                "welcoming",
                "inclusive",
            ],
            "energetic": [
                "energetic",
                "dynamic",
                "active",
                "exciting",
                "adventure",
                "fun",
                "workout",
                "fitness",
                "sports",
                "adrenaline",
                "motivating",
                "upbeat",
                "lively",
                "stimulating",
                "invigorating",
                "powerful",
                "boost",
                "pump up",
            ],
        }

        personality_profile = {}
        evidence = {}

        for mood, keywords in personality_keywords.items():
            score = 0
            found_evidence = []

            for keyword in keywords:
                # 키워드 주변 문맥 찾기
                pattern = f".{{0,40}}{re.escape(keyword)}.{{0,40}}"
                matches = re.findall(pattern, review_text, re.IGNORECASE)

                score += len(matches)

                if matches:
                    # 가장 좋은 문맥 선택 (길이가 적당한 것)
                    best_matches = sorted(matches, key=len, reverse=True)[:2]
                    found_evidence.extend([match.strip() for match in best_matches])

            # 점수 정규화 (10점 만점)
            personality_profile[mood] = min(10, score * 1.5)
            evidence[mood] = found_evidence[:3]  # 최대 3개 증거

        return personality_profile, evidence

    def nearby_search_with_personality(
        self, lat, lng, radius=1000, place_type=None, keyword=None
    ):
        """개성 분석이 포함된 장소 검색"""
        places = self.nearby_search(lat, lng, radius, place_type, keyword)

        enhanced_places = []
        for place in places:
            # 상세 정보 가져오기 (리뷰 포함)
            details = self.get_place_details(place.get("place_id"))

            if details:
                personality, evidence = self.analyze_place_personality(details)
                place.update(
                    {
                        "personality_scores": personality,
                        "personality_evidence": evidence,
                        "why_creative": evidence.get("creative", []),
                        "why_healing": evidence.get("healing", []),
                        "why_social": evidence.get("social", []),
                        "why_energetic": evidence.get("energetic", []),
                        "detailed_info": details,
                    }
                )

            enhanced_places.append(place)

        return enhanced_places


# 전역 인스턴스
google_places_client = GooglePlacesClient()
