from typing import Dict, Any
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")


def enrich_place_info(place: Dict[str, Any]) -> Dict[str, Any]:
    """
    Google Places API를 사용해서 장소 정보를 풍부하게 만듭니다.
    """
    try:
        # 장소 검색
        search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            "query": f"{place['name']} near {place['lat']},{place['lng']}",
            "key": GOOGLE_API_KEY,
        }

        search_result = requests.get(search_url, params=params).json()

        if search_result.get("results"):
            place_id = search_result["results"][0]["place_id"]

            # 상세 정보 가져오기
            details_url = "https://maps.googleapis.com/maps/api/place/details/json"
            params = {
                "place_id": place_id,
                "fields": "name,rating,formatted_address,opening_hours,photos,reviews",
                "key": GOOGLE_API_KEY,
            }

            details = requests.get(details_url, params=params).json()
            place_details = details.get("result", {})

            # 정보 추가
            place.update(
                {
                    "rating": place_details.get("rating", 0),
                    "address": place_details.get("formatted_address", ""),
                    "opening_hours": place_details.get("opening_hours", {}).get(
                        "weekday_text", []
                    ),
                    "reviews": [
                        {
                            "text": review["text"],
                            "rating": review["rating"],
                            "time": datetime.fromtimestamp(review["time"]).strftime(
                                "%Y-%m-%d"
                            ),
                        }
                        for review in place_details.get("reviews", [])[
                            :3
                        ]  # 최근 리뷰 3개
                    ],
                }
            )

            # 이미지 URL 생성 (첫 번째 사진만)
            if place_details.get("photos"):
                photo_reference = place_details["photos"][0]["photo_reference"]
                place["photo_url"] = (
                    f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={GOOGLE_API_KEY}"
                )

    except Exception as e:
        print(f"Error enriching place info for {place['name']}: {str(e)}")

    return place


def get_place_highlights(place: Dict[str, Any]) -> Dict[str, Any]:
    """
    장소별 특별한 점이나 추천 포인트를 생성합니다.
    """
    highlights = {
        "parks": [
            "🌳 자연친화적인 환경",
            "🧘 명상하기 좋은 조용한 공간",
            "🏃‍♂️ 산책로",
            "🌸 계절별 풍경",
        ],
        "cultural": [
            "🎨 예술적 영감",
            "📚 독서하기 좋은 공간",
            "☕ 카페 공간",
            "🎭 문화 체험",
        ],
        "buildings": [
            "🏛️ 역사적 건축물",
            "🌆 도시 전망",
            "🍷 분위기 있는 공간",
            "📸 포토스팟",
        ],
    }

    place_type = place.get("type", "other")
    type_highlights = highlights.get(place_type, ["✨ 특별한 공간"])

    # 점수에 따라 하이라이트 선택
    score = place.get("score", 0)
    num_highlights = min(3, max(1, int(score / 3)))

    return {
        "highlights": type_highlights[:num_highlights],
        "mood_tag": get_mood_tag(score),
    }


def get_mood_tag(score: float) -> str:
    """
    점수에 따른 분위기 태그를 반환합니다.
    """
    if score >= 9:
        return "🌟 최고의 힐링 스팟"
    elif score >= 8:
        return "✨ 추천 명소"
    elif score >= 7:
        return "💫 좋은 장소"
    else:
        return "👍 괜찮은 곳"
