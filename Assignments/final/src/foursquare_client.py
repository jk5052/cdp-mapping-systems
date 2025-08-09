import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


class FoursquareClient:
    def __init__(self):
        self.api_key = os.getenv("FOURSQUARE_API_KEY")
        self.base_url = "https://api.foursquare.com/v3"

        if not self.api_key:
            st.error("Foursquare API key not found in .env file")

    def search_places(self, lat, lng, radius=1000, categories=None, limit=20):
        """Foursquare Places API로 장소 검색"""

        url = f"{self.base_url}/places/search"

        headers = {"Authorization": self.api_key, "Accept": "application/json"}

        params = {"ll": f"{lat},{lng}", "radius": radius, "limit": limit}

        if categories:
            params["categories"] = ",".join(categories)

        try:
            response = requests.get(url, headers=headers, params=params)

            if response.status_code == 200:
                data = response.json()
                return data.get("results", [])
            else:
                st.error(f"Foursquare API Error: {response.status_code}")
                return []

        except Exception as e:
            st.error(f"Foursquare API 호출 실패: {e}")
            return []

    def get_place_details(self, place_id):
        """특정 장소의 상세 정보 가져오기"""

        url = f"{self.base_url}/places/{place_id}"

        headers = {"Authorization": self.api_key, "Accept": "application/json"}

        try:
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                return response.json()
            else:
                return None

        except Exception as e:
            st.warning(f"장소 상세정보 가져오기 실패: {e}")
            return None


# 전역 인스턴스
foursquare_client = FoursquareClient()
