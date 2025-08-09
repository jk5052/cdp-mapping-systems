import json
from jinja2 import Template
import os


def generate_art_map(start_location, end_location, waypoints, story_info):
    """
    아트맵 HTML 생성
    """
    # HTML 템플릿 로드
    template_path = os.path.join(os.path.dirname(__file__), "../art_map_template.html")
    with open(template_path, "r", encoding="utf-8") as f:
        template_content = f.read()

    # 웨이포인트 데이터 가공
    formatted_waypoints = []
    for i, wp in enumerate(waypoints):
        formatted_waypoints.append(
            {
                "name": wp["name"],
                "type": wp["type"].title(),
                "score": wp["score"],
                "description": get_place_description(wp),
                "position": calculate_position(i, len(waypoints)),
            }
        )

    # 템플릿 데이터 준비
    template_data = {
        "start_name": start_location["name"],
        "end_name": end_location["name"],
        "waypoints": formatted_waypoints,
        "story": story_info,
    }

    # 템플릿 렌더링
    template = Template(template_content)
    return template.render(**template_data)


def get_place_description(waypoint):
    """
    장소별 특별한 설명 생성
    """
    type_descriptions = {
        "parks": [
            "A tranquil oasis perfect for meditation and nature connection.",
            "Beautiful green space with scenic walking paths and peaceful corners.",
            "Historic park offering a respite from urban energy.",
        ],
        "cultural": [
            "Inspiring cultural venue that nurtures creativity and reflection.",
            "Artistic space where imagination meets tranquility.",
            "Cultural landmark with a unique atmospheric charm.",
        ],
        "buildings": [
            "Architectural gem with unique character and peaceful spots.",
            "Historic building with a story in every corner.",
            "Urban sanctuary with distinctive architectural elements.",
        ],
    }

    descriptions = type_descriptions.get(
        waypoint["type"],
        [
            "A special place in the urban landscape.",
            "Unique spot with its own character and charm.",
            "Distinctive location worth exploring.",
        ],
    )

    return descriptions[hash(waypoint["name"]) % len(descriptions)]


def calculate_position(index, total):
    """
    웨이포인트의 시각적 위치 계산
    """
    base_left = 15 + (70 * (index + 1) / (total + 1))
    base_top = 40 + (10 * ((-1) ** index))

    return {"left": f"{base_left}%", "top": f"{base_top}%"}
