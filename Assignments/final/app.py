import streamlit as st
import folium
from streamlit_folium import st_folium
from src.data_loader import load_geojson_data
from config.story_config import STORY_OPTIONS
from src.google_places_client import google_places_client
from src.social_narrative import SocialNarrativeAnalyzer
from src.art_map_generator import generate_art_map
from geopy.distance import geodesic
import os
import uuid

st.set_page_config(
    page_title="NYC Wellness Route Navigator",
    page_icon="🗽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Modern CSS Styling
st.markdown(
    """
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Main container */
    .main > div {
        padding-top: 2rem;
    }

    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }

    /* Section headers */
    .section-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #2c3e50;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #ecf0f1;
    }

    /* Clean cards */
    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }

    /* Route info styling */
    .route-info {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #2c3e50;
        margin: 1rem 0;
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    /* Modern Radio Button Grid */
    .wellness-options {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }

    .wellness-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border: 2px solid #dee2e6;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        position: relative;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    .wellness-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        border-color: #2c3e50;
    }

    .wellness-card.selected {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        color: white;
        border-color: #2c3e50;
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(44,62,80,0.3);
    }

    .wellness-emoji {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        display: block;
    }

    .wellness-title {
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }

    .wellness-desc {
        font-size: 0.9rem;
        opacity: 0.8;
        line-height: 1.4;
    }

    /* Style radio buttons */
    .stRadio > div {
        flex-direction: row;
        flex-wrap: wrap;
        gap: 0.5rem;
        justify-content: center;
    }

    .stRadio > div > label {
        background: white;
        border: 2px solid #e9ecef;
        border-radius: 25px;
        padding: 0.5rem 1rem;
        margin: 0.25rem;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 0.9rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    .stRadio > div > label:hover {
        border-color: #2c3e50;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    .stRadio > div > label[data-checked="true"] {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        color: white;
        border-color: #2c3e50;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(44,62,80,0.2);
    }



    /* Selectbox styling */
    .stSelectbox > div > div {
        border-radius: 8px;
        border: 1px solid #e9ecef;
    }

    /* Metric cards */
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }

    /* Clean spacing */
    .element-container {
        margin-bottom: 1rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Clean Header
st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.markdown("# NYC Wellness Route Navigator")
st.markdown("AI-powered wellness routes using real NYC geospatial data")
st.markdown("</div>", unsafe_allow_html=True)

# 세션 상태 초기화
if "generate_route" not in st.session_state:
    st.session_state.generate_route = False
if "start_loc" not in st.session_state:
    st.session_state.start_loc = [40.8075, -73.9626]
if "end_loc" not in st.session_state:
    st.session_state.end_loc = [40.7829, -73.9654]
if "force_show_route" not in st.session_state:
    st.session_state.force_show_route = False
if "selected_route_idx" not in st.session_state:
    st.session_state.selected_route_idx = 0


# 데이터 로드
@st.cache_data
def load_all_data():
    return load_geojson_data()


# 소셜 내러티브 분석기 초기화
@st.cache_resource
def get_social_analyzer():
    return SocialNarrativeAnalyzer()


# 웰니스 점수 계산 함수 (소셜 내러티브 포함)
def calculate_wellness_score(place_data, story_key, api_data=None, social_data=None):
    """GeoJSON + API + 소셜 내러티브 데이터 기반 웰니스 점수 계산"""

    base_score = 5.0
    place_type = place_data.get("type", "unknown")

    # 장소 타입별 스토리 점수 매핑
    type_scores = {
        "parks": {
            "emotional_recovery": 9,
            "freedom": 9,
            "energetic": 8,
            "quick_healing": 8,
            "balanced": 7,
            "creative": 6,
            "social": 7,
            "dopamine": 7,
        },
        "cultural": {
            "creative": 10,
            "social": 8,
            "balanced": 8,
            "dopamine": 7,
            "emotional_recovery": 6,
            "freedom": 6,
            "energetic": 5,
            "quick_healing": 6,
        },
        "streets": {
            "energetic": 7,
            "social": 6,
            "balanced": 6,
            "freedom": 8,
            "creative": 5,
            "emotional_recovery": 4,
            "quick_healing": 5,
            "dopamine": 6,
        },
        "buildings": {
            "social": 7,
            "creative": 6,
            "balanced": 7,
            "dopamine": 6,
            "energetic": 5,
            "emotional_recovery": 4,
            "quick_healing": 5,
            "freedom": 5,
        },
    }

    base_score = type_scores.get(place_type, {}).get(story_key, 5)

    # Google Places API 데이터로 보정
    if api_data:
        rating = api_data.get("rating", 3.5)
        rating_bonus = (rating - 3.5) * 0.5
        base_score += rating_bonus

        user_ratings_total = api_data.get("user_ratings_total", 0)
        if user_ratings_total > 500:
            base_score += 0.5
        elif user_ratings_total > 100:
            base_score += 0.3

        # 주관적 특성 점수 반영
        personality_scores = api_data.get("personality_scores", {})
        if personality_scores:
            # 스토리에 맞는 주관적 점수 가중치 적용
            story_personality_map = {
                "creative": "creative",
                "emotional_recovery": "healing",
                "social": "social",
                "energetic": "energetic",
                "freedom": "energetic",
                "balanced": "healing",
                "quick_healing": "healing",
                "dopamine": "social",
            }

            relevant_personality = story_personality_map.get(story_key, "creative")
            personality_score = personality_scores.get(relevant_personality, 0)

            # 주관적 점수를 웰니스 점수에 반영 (최대 2점 보너스)
            personality_bonus = (personality_score / 10) * 2
            base_score += personality_bonus

    # 🔥 새로운 기능: 소셜 내러티브 데이터로 점수 보정
    if social_data and story_key in social_data:
        social_score = social_data[story_key]["score"]
        hashtag_popularity = social_data[story_key]["hashtag_count"]

        # 소셜 점수를 웰니스 점수에 반영 (최대 1.5점 보너스)
        social_boost = (social_score / 10) * 1.5

        # 해시태그 인기도로 추가 보정 (최대 0.5점)
        popularity_boost = min(0.5, hashtag_popularity / 500)

        base_score = (
            (base_score * 0.7) + (social_boost * 0.25) + (popularity_boost * 0.05)
        )

    return min(10.0, max(1.0, base_score))


# 메인 레이아웃
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown(
        '<div class="section-header">Choose Your Wellness Story</div>',
        unsafe_allow_html=True,
    )

    # Wellness story selection with styled radio buttons
    selected_story = st.radio(
        "Select your wellness focus:",
        options=list(STORY_OPTIONS.keys()),
        format_func=lambda x: f"{STORY_OPTIONS[x]['emoji']} {STORY_OPTIONS[x]['text']}",
        horizontal=True,
    )

    story_info = STORY_OPTIONS[selected_story]

    st.markdown(
        f"""
    <div class="info-card">
    <h4>{story_info['text']}</h4>
    <p style="color: #6c757d; margin-bottom: 0;">{story_info['description']}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Route Planning Section
    st.markdown(
        '<div class="section-header">Route Planning</div>', unsafe_allow_html=True
    )

    # Starting Point Setup
    st.markdown("**Starting Point**")
    start_input_type = st.radio(
        "Starting point input method:",
        ["Preset locations", "Enter address"],
        horizontal=True,
    )

    if start_input_type == "Preset locations":
        start_options = {
            "🏫 Columbia University": [40.8075, -73.9626],
            "🌟 Times Square": [40.7580, -73.9855],
            "🌳 Central Park": [40.7829, -73.9654],
            "🚂 Grand Central": [40.7527, -73.9772],
            "🌉 Brooklyn Bridge": [40.7061, -73.9969],
            "🏢 Empire State Building": [40.7484, -73.9857],
        }

        selected_start = st.selectbox(
            "Select starting location:",
            list(start_options.keys()),
            label_visibility="collapsed",
        )
        start_location = start_options[selected_start]
        start_name = selected_start.split(" ", 1)[1]  # Remove emoji for internal use
    else:
        # Address input field
        address = st.text_input("Enter address (e.g., 235 W 23rd St, New York, NY):")
        if address:
            try:
                # Convert address to latitude/longitude
                from geopy.geocoders import Nominatim

                geolocator = Nominatim(user_agent="wellness_route_app")
                location = geolocator.geocode(f"{address}, New York, NY")

                if location:
                    start_lat = location.latitude
                    start_lng = location.longitude
                    start_location = [start_lat, start_lng]
                    start_name = address
                    st.success(f"✅ Address found: {location.address}")
                else:
                    st.error("❌ Address not found. Please try again.")
                    start_location = [40.8075, -73.9626]  # Default value
                    start_name = "Location search failed"
            except Exception:
                st.error("Error occurred during address search. Please try again.")
                start_location = [40.8075, -73.9626]  # Default value
                start_name = "Location search failed"
        else:
            start_location = [40.8075, -73.9626]  # Default value
            start_name = "Please enter an address"

    # Destination Setup
    st.markdown("**Destination**")
    end_input_type = st.radio(
        "Destination input method:",
        ["Preset locations", "Enter address"],
        horizontal=True,
        key="end_input_type",
    )

    if end_input_type == "Preset locations":
        end_options = {
            "🌳 Central Park": [40.7829, -73.9654],
            "🌟 Times Square": [40.7580, -73.9855],
            "🌉 Brooklyn Bridge": [40.7061, -73.9969],
            "🏢 Empire State Building": [40.7484, -73.9857],
            "🚶 High Line": [40.7480, -74.0048],
            "🏫 Columbia University": [40.8075, -73.9626],
        }

        selected_end = st.selectbox(
            "Select destination:",
            list(end_options.keys()),
            label_visibility="collapsed",
        )
        end_location = end_options[selected_end]
        end_name = selected_end.split(" ", 1)[1]  # Remove emoji for internal use
    else:
        # Address input field
        end_address = st.text_input(
            "Enter address (e.g., 235 W 23rd St, New York, NY):", key="end_address"
        )
        if end_address:
            try:
                # Convert address to latitude/longitude
                from geopy.geocoders import Nominatim

                geolocator = Nominatim(user_agent="wellness_route_app")
                location = geolocator.geocode(f"{end_address}, New York, NY")

                if location:
                    end_lat = location.latitude
                    end_lng = location.longitude
                    end_location = [end_lat, end_lng]
                    end_name = end_address
                    st.success(f"✅ Address found: {location.address}")
                else:
                    st.error("❌ Address not found. Please try again.")
                    end_location = [40.7829, -73.9654]  # Default value
                    end_name = "Location search failed"
            except Exception:
                st.error("❌ Error occurred during address search. Please try again.")
                end_location = [40.7829, -73.9654]  # Default value
                end_name = "Location search failed"
        else:
            end_location = [40.7829, -73.9654]  # Default value
            end_name = "Please enter an address"

    # Route Settings
    st.markdown("**Route Settings**")
    max_waypoints = st.slider("Number of waypoints", 2, 6, 4)
    search_radius = 4.0  # Fixed wide search radius

    # Route Generation Buttons
    st.markdown("<br>", unsafe_allow_html=True)

    # Create button columns
    btn_col1, btn_col2 = st.columns(2)

    with btn_col1:

        if st.button(
            "Generate Wellness Route", type="primary", key="generate_route_btn"
        ):
            st.session_state.generate_route = True
            st.session_state.start_loc = start_location
            st.session_state.end_loc = end_location
            st.session_state.start_name = start_name
            st.session_state.end_name = end_name
            st.session_state.force_show_route = True
            st.session_state.selected_route_idx = 0  # 새 루트 생성 시 첫 번째 옵션 선택
            st.success(f"🎯 Generating route: {start_name} → {end_name}")
            st.rerun()

    with btn_col2:

        if st.button("Reset Route", key="reset_route_btn"):
            st.session_state.generate_route = False
            st.session_state.force_show_route = False
            st.session_state.selected_route_idx = 0  # 루트 선택도 초기화
            st.info("🔄 Route has been reset")
            st.rerun()

    # Debug Information (collapsed by default)
    with st.expander("Debug Information"):
        st.write(f"**Starting Point:** {start_name}")
        st.write(f"**Destination:** {end_name}")
        st.write(f"**Search Radius:** {search_radius}km")
        st.write(f"**Waypoints:** {max_waypoints}")

with col2:
    st.markdown(
        '<div class="section-header">Interactive Wellness Map</div>',
        unsafe_allow_html=True,
    )

    # Data Loading
    with st.spinner("Loading NYC geospatial data..."):
        geojson_data = load_all_data()

    # Map Center Setting
    if st.session_state.generate_route or st.session_state.force_show_route:
        map_center = st.session_state.start_loc
        start_name_display = st.session_state.get("start_name", start_name)
        end_name_display = st.session_state.get("end_name", end_name)
        st.info(f"Route Mode: {start_name_display} → {end_name_display}")
    else:
        map_center = start_location

    # Map Creation
    m = folium.Map(location=map_center, zoom_start=13, tiles="OpenStreetMap")

    # Wellness Places Collection
    wellness_places = []
    colors = ["green", "blue", "purple", "orange"]

    # Route Generation Mode (including forced display)
    if st.session_state.generate_route or st.session_state.force_show_route:

        # Always display start and end markers
        folium.Marker(
            st.session_state.start_loc,
            popup=f"Starting Point: {start_name_display}",
            icon=folium.Icon(color="red", icon="play"),
        ).add_to(m)

        folium.Marker(
            st.session_state.end_loc,
            popup=f"Destination: {end_name_display}",
            icon=folium.Icon(color="darkred", icon="stop"),
        ).add_to(m)

        # Always display basic straight route
        basic_route = [st.session_state.start_loc, st.session_state.end_loc]

        folium.PolyLine(
            basic_route,
            weight=4,
            color="#2c3e50",
            opacity=0.6,
            popup=f"Direct Route: {start_name_display} → {end_name_display}",
            dash_array="10,5",
        ).add_to(m)

        # Route display success message
        st.success(f"Basic route displayed: {start_name_display} → {end_name_display}")

        # Finding wellness waypoints
        waypoint_candidates = []

        # 🔥 소셜 내러티브 분석기 초기화
        social_analyzer = get_social_analyzer()
        st.write("🌟 Social narrative analysis enabled!")

        # 테스트: 소셜 분석기 작동 확인
        test_social = social_analyzer.analyze_location_social_context(
            "Central Park", 40.7829, -73.9654, "park"
        )
        st.write(
            f"🧪 Test social analysis: {test_social[selected_story]['score']}/10 for {selected_story}"
        )

        # Debug: Check data loading status
        st.write(f"🔍 Loaded data types: {list(geojson_data.keys())}")
        total_features_checked = 0

        # Calculate midpoint between start and end points and route line
        mid_lat = (st.session_state.start_loc[0] + st.session_state.end_loc[0]) / 2
        mid_lng = (st.session_state.start_loc[1] + st.session_state.end_loc[1]) / 2
        route_center = [mid_lat, mid_lng]

        # Search for wellness places in all data types (greatly expanded)
        for i, (data_type, data) in enumerate(geojson_data.items()):
            if data_type == "cultural":
                continue  # CSV data processed separately

            if isinstance(data, dict) and "features" in data:
                # Process many more features
                max_features = 500 if data_type == "buildings" else 200
                features = data["features"][:max_features]

                # Debug information
                st.write(f"📍 {data_type}: Processing {len(features)} features...")
                features_in_radius = 0

                for j, feature in enumerate(features):
                    try:
                        coords = feature["geometry"]["coordinates"]
                        total_features_checked += 1

                        if len(coords) >= 2:
                            # 좌표 처리 - Polygon인 경우 첫 번째 좌표 사용
                            if isinstance(coords[0], list):
                                if isinstance(coords[0][0], list):
                                    # MultiPolygon 또는 Polygon
                                    lat, lng = coords[0][0][1], coords[0][0][0]
                                else:
                                    # LineString
                                    lat, lng = coords[0][1], coords[0][0]
                            else:
                                # Point
                                lat, lng = coords[1], coords[0]

                            # 경로 근처 장소 검색 (조건 대폭 완화)
                            dist_to_start = geodesic(
                                (lat, lng), st.session_state.start_loc
                            ).km
                            dist_to_end = geodesic(
                                (lat, lng), st.session_state.end_loc
                            ).km
                            dist_to_center = geodesic((lat, lng), route_center).km

                            # 최소 거리 계산
                            min_dist = min(dist_to_start, dist_to_end, dist_to_center)

                            # 검색 반경 내에 있는 장소들 (4km로 확대)
                            if min_dist <= search_radius:
                                features_in_radius += 1
                                name = feature.get("properties", {}).get(
                                    "name", f"{data_type}_{j}"
                                )
                                if not name or name == "None":
                                    name = f"{data_type.title()} #{j}"

                                # 🔥 소셜 내러티브 분석 추가
                                social_context = (
                                    social_analyzer.analyze_location_social_context(
                                        name, lat, lng, data_type
                                    )
                                )

                                # 디버깅: 소셜 데이터 확인
                                if j < 3:  # 처음 3개만 디버깅
                                    st.write(
                                        f"🔍 Social analysis for {name}: {social_context[selected_story]['score']}/10"
                                    )

                                # Calculate wellness score with social data
                                place_data = {"type": data_type}
                                wellness_score = calculate_wellness_score(
                                    place_data,
                                    selected_story,
                                    social_data=social_context,
                                )

                                # Greatly relaxed score criteria (3 points or higher)
                                if wellness_score >= 3.0:
                                    waypoint_candidates.append(
                                        {
                                            "name": name,
                                            "lat": lat,
                                            "lng": lng,
                                            "score": wellness_score,
                                            "type": data_type,
                                            "distance_from_start": dist_to_start,
                                            "distance_from_route": min_dist,
                                            "social_narrative": social_context,
                                            "why_community_loves": social_context[
                                                selected_story
                                            ]["narratives"],
                                        }
                                    )

                    except Exception:
                        continue

                # Display results by data type
                st.write(f"✅ {data_type}: {features_in_radius} places within radius")

        # Final debug information
        st.write(
            f"🎯 Total {total_features_checked} features checked, {len(waypoint_candidates)} wellness candidates found"
        )

        # Google Places API로 실제 장소들 추가 검색 (선택적)
        google_places = []

        # Google Places API 키가 있는 경우에만 시도
        if google_places_client.api_key:
            st.write("🔍 Searching for cafes, restaurants, and interesting places...")

            # 경로 중간 지점들에서 Google Places 검색
            search_points = [
                st.session_state.start_loc,
                route_center,
                st.session_state.end_loc,
            ]

            for point in search_points:
                # 카페, 레스토랑, 관광지 등 검색
                place_types = [
                    "cafe",
                    "restaurant",
                    "tourist_attraction",
                    "art_gallery",
                    "museum",
                ]

                for place_type in place_types:
                    try:
                        places = google_places_client.nearby_search_with_personality(
                            point[0], point[1], radius=1500, place_type=place_type
                        )

                        if not places:
                            continue  # 조용히 넘어가기

                        for place in places[:3]:  # 각 타입당 최대 3개
                            if place.get("rating", 0) >= 3.5:  # 평점 3.5 이상으로 완화
                                # 거리 계산
                                place_location = place["geometry"]["location"]
                                place_lat = place_location["lat"]
                                place_lng = place_location["lng"]

                                dist_to_start = geodesic(
                                    (place_lat, place_lng), st.session_state.start_loc
                                ).km
                                dist_to_end = geodesic(
                                    (place_lat, place_lng), st.session_state.end_loc
                                ).km
                                min_dist = min(dist_to_start, dist_to_end)

                                if min_dist <= search_radius:
                                    # 🔥 Google Places에도 소셜 내러티브 분석 추가
                                    place_name = place.get("name", "Unknown Place")
                                    social_context = (
                                        social_analyzer.analyze_location_social_context(
                                            place_name, place_lat, place_lng, place_type
                                        )
                                    )

                                    # API + 소셜 데이터로 웰니스 점수 계산
                                    place_data = {"type": "google_places"}
                                    wellness_score = calculate_wellness_score(
                                        place_data,
                                        selected_story,
                                        place,
                                        social_context,
                                    )

                                    google_places.append(
                                        {
                                            "name": place_name,
                                            "lat": place_lat,
                                            "lng": place_lng,
                                            "score": wellness_score,
                                            "type": "google_places",
                                            "distance_from_start": dist_to_start,
                                            "distance_from_route": min_dist,
                                            "rating": place.get("rating", 0),
                                            "place_type": place_type,
                                            "why_creative": place.get(
                                                "why_creative", []
                                            ),
                                            "why_healing": place.get("why_healing", []),
                                            "why_social": place.get("why_social", []),
                                            "why_energetic": place.get(
                                                "why_energetic", []
                                            ),
                                            "personality_scores": place.get(
                                                "personality_scores", {}
                                            ),
                                            "social_narrative": social_context,
                                            "why_community_loves": social_context[
                                                selected_story
                                            ]["narratives"],
                                            "trending_hashtags": social_context[
                                                selected_story
                                            ]["trending_hashtags"],
                                            "google_place": True,
                                        }
                                    )

                    except Exception as e:
                        continue  # 조용히 넘어가기

        else:
            st.info(
                "💡 Google Places API not configured. Using NYC geospatial data only."
            )

        # Google Places 결과를 기존 후보에 추가
        waypoint_candidates.extend(google_places)
        if google_places:
            st.write(f"🎉 Added {len(google_places)} Google Places to candidates!")
        else:
            st.write("📍 Using NYC geospatial data for route generation.")

        # 만약 후보가 없다면 기본 장소들을 추가
        if not waypoint_candidates:
            st.warning(
                "No candidates found from data. Adding default NYC wellness spots..."
            )
            default_places = [
                {
                    "name": "Central Park Reservoir",
                    "lat": 40.7851,
                    "lng": -73.9558,
                    "score": 8.5,
                    "type": "park",
                },
                {
                    "name": "Bryant Park",
                    "lat": 40.7536,
                    "lng": -73.9832,
                    "score": 8.0,
                    "type": "park",
                },
                {
                    "name": "High Line Park",
                    "lat": 40.7480,
                    "lng": -74.0048,
                    "score": 9.0,
                    "type": "park",
                },
                {
                    "name": "Washington Square Park",
                    "lat": 40.7308,
                    "lng": -73.9973,
                    "score": 7.5,
                    "type": "park",
                },
            ]

            # 시작점과 끝점 사이의 거리 계산하여 적절한 장소만 선택
            for place in default_places:
                dist_to_start = geodesic(
                    (place["lat"], place["lng"]), st.session_state.start_loc
                ).km
                dist_to_end = geodesic(
                    (place["lat"], place["lng"]), st.session_state.end_loc
                ).km
                place["distance_from_start"] = dist_to_start
                place["distance_from_route"] = min(dist_to_start, dist_to_end)

                if place["distance_from_route"] <= search_radius:
                    # 기본 장소들에도 소셜 내러티브 추가
                    social_context = social_analyzer.analyze_location_social_context(
                        place["name"], place["lat"], place["lng"], place["type"]
                    )
                    place["social_narrative"] = social_context
                    place["why_community_loves"] = social_context[selected_story][
                        "narratives"
                    ]
                    place["trending_hashtags"] = social_context[selected_story][
                        "trending_hashtags"
                    ]

                    waypoint_candidates.append(place)

        # Wellness waypoint selection and display
        if waypoint_candidates:
            st.success(f"🎯 Found {len(waypoint_candidates)} wellness candidates!")

            # Generate 3 different style routes
            route_options = []

            # 1. Wellness Optimized Route (score priority)
            wellness_route = sorted(
                waypoint_candidates, key=lambda x: x["score"], reverse=True
            )[:max_waypoints]
            route_options.append(
                {
                    "name": "Wellness Optimized",
                    "description": "Places with highest wellness scores",
                    "waypoints": wellness_route,
                    "color": "#27ae60",
                }
            )

            # 2. Balanced Route (score + distance)
            for wp in waypoint_candidates:
                wp["balanced_score"] = wp["score"] - (wp["distance_from_route"] * 1.2)
            balanced_route = sorted(
                waypoint_candidates, key=lambda x: x["balanced_score"], reverse=True
            )[:max_waypoints]
            route_options.append(
                {
                    "name": "Balanced",
                    "description": "Balance of wellness score and distance",
                    "waypoints": balanced_route,
                    "color": "#3498db",
                }
            )

            # 3. Quick Route (distance priority)
            quick_route = sorted(
                waypoint_candidates, key=lambda x: x["distance_from_route"]
            )[:max_waypoints]
            route_options.append(
                {
                    "name": "Quick Route",
                    "description": "Shortest distance route",
                    "waypoints": quick_route,
                    "color": "#e74c3c",
                }
            )

            # 🎨 Interactive Route Selection with Art Map Generation
            st.markdown("**🎨 Choose Your Wellness Journey**")
            st.markdown(
                "*Click on a route to generate your personalized subjective art map*"
            )

            # Create route selection buttons
            route_cols = st.columns(len(route_options))

            # 세션 상태에서 선택된 루트 인덱스 가져오기 (기본값: 0)
            if st.session_state.selected_route_idx >= len(route_options):
                st.session_state.selected_route_idx = 0

            for idx, route_option in enumerate(route_options):
                with route_cols[idx]:
                    # Create styled button for each route
                    button_html = f"""
                    <div style="
                        background: linear-gradient(135deg, {route_option['color']}22 0%, {route_option['color']}44 100%);
                        border: 2px solid {route_option['color']};
                        border-radius: 12px;
                        padding: 1rem;
                        text-align: center;
                        margin-bottom: 1rem;
                        cursor: pointer;
                        transition: all 0.3s ease;
                    ">
                        <h4 style="color: {route_option['color']}; margin: 0 0 0.5rem 0;">{route_option['name']}</h4>
                        <p style="margin: 0; font-size: 0.9rem; color: #666;">{route_option['description']}</p>
                        <p style="margin: 0.5rem 0 0 0; font-size: 0.8rem; color: {route_option['color']};">
                            {len(route_option['waypoints'])} stops
                        </p>
                    </div>
                    """
                    st.markdown(button_html, unsafe_allow_html=True)

                    # Generate Art Map button
                    if st.button("🎨 Generate Art Map", key=f"artmap_{idx}"):
                        # Set this as selected route
                        st.session_state.selected_route_idx = idx
                        # Generate art map HTML
                        start_location = {
                            "name": st.session_state.get("start_name", "Start Point"),
                            "lat": st.session_state.start_loc[0],
                            "lng": st.session_state.start_loc[1],
                        }
                        end_location = {
                            "name": st.session_state.get("end_name", "End Point"),
                            "lat": st.session_state.end_loc[0],
                            "lng": st.session_state.end_loc[1],
                        }

                        # Generate unique filename
                        import uuid

                        map_id = str(uuid.uuid4())[:8]
                        filename = f"artmap_{route_option['name'].lower().replace(' ', '_')}_{map_id}.html"

                        # Generate art map
                        art_map_html = generate_art_map(
                            start_location,
                            end_location,
                            route_option["waypoints"],
                            STORY_OPTIONS[selected_story],
                        )

                        # Save to file
                        os.makedirs("generated_maps", exist_ok=True)
                        filepath = os.path.join("generated_maps", filename)
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(art_map_html)

                        # Show success message with link
                        st.success("🎨 Art map generated successfully!")
                        st.markdown(
                            f"""
                        **Your subjective art map is ready!**

                        📁 **File location:** `{filepath}`

                        🌐 **To view:** Open the file in your browser or click the link below:
                        """
                        )

                        # Create download link
                        with open(filepath, "r", encoding="utf-8") as f:
                            art_map_content = f.read()

                        st.download_button(
                            label="📥 Download Art Map HTML",
                            data=art_map_content,
                            file_name=filename,
                            mime="text/html",
                            key=f"download_{idx}",
                        )

            # Use traditional radio as backup/alternative selection
            st.markdown("---")
            st.markdown("**Alternative Selection:**")
            new_selected_route_idx = st.radio(
                "Choose route for map display:",
                range(len(route_options)),
                format_func=lambda x: f"{route_options[x]['name']} - {route_options[x]['description']}",
                index=st.session_state.selected_route_idx,
                label_visibility="collapsed",
            )

            # 라디오 버튼에서 선택이 바뀌면 세션 상태 업데이트
            if new_selected_route_idx != st.session_state.selected_route_idx:
                st.session_state.selected_route_idx = new_selected_route_idx
                st.rerun()

            selected_route_option = route_options[st.session_state.selected_route_idx]
            selected_waypoints = selected_route_option["waypoints"]

            # Display selected waypoints on map
            for i, wp in enumerate(selected_waypoints):
                # 주관적 정보 생성
                why_sections = []

                if wp.get("google_place", False):
                    # Google Places 데이터가 있는 경우
                    story_map = {
                        "creative": "why_creative",
                        "emotional_recovery": "why_healing",
                        "social": "why_social",
                        "energetic": "why_energetic",
                        "freedom": "why_energetic",
                        "balanced": "why_healing",
                        "quick_healing": "why_healing",
                        "dopamine": "why_social",
                    }

                    relevant_why = story_map.get(selected_story, "why_creative")
                    why_evidence = wp.get(relevant_why, [])

                    if why_evidence:
                        why_sections.append(
                            f"<b>Why {STORY_OPTIONS[selected_story]['text']}:</b><br>"
                        )
                        for evidence in why_evidence[:2]:
                            why_sections.append(f"• {evidence}<br>")

                    # 평점 정보
                    rating_info = f"<b>Rating:</b> {wp.get('rating', 'N/A')}/5<br>"
                    place_type_info = (
                        f"<b>Place Type:</b> {wp.get('place_type', 'Unknown')}<br>"
                    )
                else:
                    # 기존 GeoJSON 데이터
                    rating_info = ""
                    place_type_info = ""

                # 🔥 소셜 내러티브 정보 추가
                social_info = ""

                # 디버깅: 소셜 데이터 존재 확인
                st.write(f"🔍 Debug - wp keys: {list(wp.keys())}")

                if (
                    "social_narrative" in wp
                    and selected_story in wp["social_narrative"]
                ):
                    social_data = wp["social_narrative"][selected_story]
                    social_score = social_data["score"]
                    hashtag_count = social_data["hashtag_count"]
                    trending_tags = wp.get("trending_hashtags", [])

                    social_info = f"""
                    <hr>
                    <b>🌟 Community Insights:</b><br>
                    <b>Social Score:</b> {social_score}/10<br>
                    <b>Hashtag Mentions:</b> {hashtag_count:,}<br>
                    """

                    if trending_tags:
                        social_info += (
                            f"<b>Trending:</b> {', '.join(trending_tags)}<br>"
                        )

                    # 커뮤니티가 사랑하는 이유
                    community_reasons = wp.get("why_community_loves", [])
                    if community_reasons:
                        social_info += "<b>Why Community Loves It:</b><br>"
                        for reason in community_reasons[:2]:
                            social_info += f"• {reason}<br>"
                else:
                    # 소셜 데이터가 없는 경우 디버깅 정보
                    social_info = f"""
                    <hr>
                    <b>🔍 Debug Info:</b><br>
                    Social narrative in wp: {'social_narrative' in wp}<br>
                    Selected story: {selected_story}<br>
                    Available keys: {list(wp.get('social_narrative', {}).keys()) if 'social_narrative' in wp else 'No social_narrative'}<br>
                    """

                popup_content = f"""
                <div style="width:350px">
                <h4>Waypoint {i+1}: {wp['name']}</h4>
                <b>Wellness Score:</b> {wp['score']:.1f}/10<br>
                <b>Type:</b> {wp['type']}<br>
                {place_type_info}
                {rating_info}
                <b>Distance:</b> {wp['distance_from_start']:.1f}km<br>
                <hr>
                {''.join(why_sections) if why_sections else '<i>Analyzing place personality...</i>'}
                {social_info}
                </div>
                """

                # 마커 색상을 타입에 따라 다르게
                marker_color = "darkgreen" if wp.get("google_place", False) else "green"
                marker_icon = "star" if wp.get("google_place", False) else "leaf"

                folium.Marker(
                    [wp["lat"], wp["lng"]],
                    popup=popup_content,
                    icon=folium.Icon(color=marker_color, icon=marker_icon),
                ).add_to(m)

            # Generate wellness route (sorted by distance)
            if selected_waypoints:
                sorted_waypoints = sorted(
                    selected_waypoints, key=lambda x: x["distance_from_start"]
                )

                wellness_route = [st.session_state.start_loc]
                for wp in sorted_waypoints:
                    wellness_route.append([wp["lat"], wp["lng"]])
                wellness_route.append(st.session_state.end_loc)

                # Selected route line
                folium.PolyLine(
                    wellness_route,
                    weight=6,
                    color=selected_route_option["color"],
                    opacity=0.9,
                    popup=f"{selected_route_option['name']} ({len(selected_waypoints)} waypoints)",
                ).add_to(m)

                # 전역 wellness_places 변수에 할당
                wellness_places.extend(selected_waypoints)
                st.success(
                    f"✅ Wellness route completed! Includes {len(selected_waypoints)} waypoints"
                )

        else:
            st.warning("⚠️ No wellness places found on current route.")
            st.info("💡 Try selecting different start/end points or try again later.")

            # Display only basic straight route
            st.success("📍 Basic straight route displayed.")

            # 기본 장소라도 추가해서 빈 결과를 방지
            wellness_places = [
                {
                    "name": "Start Point",
                    "lat": st.session_state.start_loc[0],
                    "lng": st.session_state.start_loc[1],
                    "score": 5.0,
                    "type": "start",
                },
                {
                    "name": "End Point",
                    "lat": st.session_state.end_loc[0],
                    "lng": st.session_state.end_loc[1],
                    "score": 5.0,
                    "type": "end",
                },
            ]

    else:
        # General exploration mode
        folium.Marker(
            map_center,
            popup=f"Current Location: {start_name}",
            icon=folium.Icon(color="red", icon="home"),
        ).add_to(m)

        # Display nearby wellness places (greatly expanded)
        for i, (data_type, data) in enumerate(geojson_data.items()):
            if data_type == "cultural":
                continue

            if isinstance(data, dict) and "features" in data:
                features = data["features"][:100]  # Display many more features

                for j, feature in enumerate(features):
                    try:
                        coords = feature["geometry"]["coordinates"]
                        if len(coords) >= 2:
                            lat, lng = coords[1], coords[0]

                            if (
                                geodesic(map_center, (lat, lng)).km <= 4.0
                            ):  # Greatly expanded radius
                                name = feature.get("properties", {}).get(
                                    "name", f"{data_type}_{j}"
                                )
                                if not name or name == "None":
                                    name = f"{data_type.title()} #{j}"

                                place_data = {"type": data_type}
                                wellness_score = calculate_wellness_score(
                                    place_data, selected_story
                                )

                                if wellness_score >= 3.0:  # Greatly relaxed criteria
                                    color = colors[i % len(colors)]

                                    folium.Marker(
                                        [lat, lng],
                                        popup=f"""
                                        <b>{name}</b><br>
                                        Wellness Score: {wellness_score:.1f}/10<br>
                                        Type: {data_type}
                                        """,
                                        icon=folium.Icon(color=color, icon="leaf"),
                                    ).add_to(m)

                                    wellness_places.append(
                                        {
                                            "name": name,
                                            "score": wellness_score,
                                            "type": data_type,
                                            "distance": geodesic(
                                                map_center, (lat, lng)
                                            ).km,
                                        }
                                    )

                    except Exception:
                        continue

    # Display Map
    map_data = st_folium(m, width=800, height=600)

# Route Information Display
if (
    st.session_state.generate_route or st.session_state.force_show_route
) and wellness_places:
    st.markdown('<div class="route-info">', unsafe_allow_html=True)
    st.subheader("🗺️ Generated Wellness Route")

    # Distance calculation
    total_distance = geodesic(st.session_state.start_loc, st.session_state.end_loc).km

    # Add distances between waypoints
    if len(wellness_places) > 1:
        prev_point = st.session_state.start_loc
        for wp in sorted(wellness_places, key=lambda x: x["distance_from_start"]):
            total_distance += geodesic(prev_point, (wp["lat"], wp["lng"])).km
            prev_point = [wp["lat"], wp["lng"]]
        total_distance += geodesic(prev_point, st.session_state.end_loc).km

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Total Distance", f"{total_distance:.1f}km")
    with col_b:
        estimated_time = total_distance * 12  # Based on 5km/h walking speed
        st.metric("Estimated Time", f"{estimated_time:.0f} min")
    with col_c:
        avg_wellness = sum([p["score"] for p in wellness_places]) / len(wellness_places)
        st.metric("Average Wellness Score", f"{avg_wellness:.1f}/10")

    st.write("**Waypoint Order:**")
    sorted_places = sorted(
        wellness_places, key=lambda x: x.get("distance_from_start", 0)
    )
    for i, place in enumerate(sorted_places):
        st.write(
            f"{i+1}. **{place['name']}** - {place['score']:.1f}/10 points ({place['type']})"
        )

    # 🔥 집단 지성 분석 추가
    if wellness_places and len(wellness_places) > 1:
        social_analyzer = get_social_analyzer()
        collective_insights = social_analyzer.get_collective_wisdom(wellness_places)

        st.markdown("### 🌟 Community Insights")

        # 커뮤니티 추천 장소들
        if collective_insights["community_recommended"]:
            st.markdown("**🏆 Community Favorites:**")
            for place in collective_insights["community_recommended"][:3]:
                st.write(
                    f"• **{place['name']}** - Social Score: {place['avg_social_score']:.1f}/10 (Best for: {place['top_mood']})"
                )

        # 인기 조합
        if collective_insights["popular_combinations"]:
            st.markdown("**🔗 Popular Route Combinations:**")
            for combo in collective_insights["popular_combinations"]:
                st.write(f"• {combo}")

        # 숨겨진 보석들
        if collective_insights["hidden_gems"]:
            st.markdown(
                "**💎 Hidden Gems (Low social media presence but high quality):**"
            )
            for gem in collective_insights["hidden_gems"][:2]:
                st.write(f"• **{gem['name']}** - {gem['reason']}")

    st.markdown("</div>", unsafe_allow_html=True)

# Bottom - Recommended Places List
if wellness_places:
    st.markdown(
        '<div class="section-header">Wellness Recommendations</div>',
        unsafe_allow_html=True,
    )

    sorted_places = sorted(wellness_places, key=lambda x: x["score"], reverse=True)

    cols = st.columns(3)
    for i, place in enumerate(sorted_places[:9]):
        with cols[i % 3]:
            distance = place.get("distance", place.get("distance_from_start", 0))

            # 주관적 정보 표시
            if place.get("google_place", False):
                # Google Places 데이터가 있는 경우
                story_map = {
                    "creative": "why_creative",
                    "emotional_recovery": "why_healing",
                    "social": "why_social",
                    "energetic": "why_energetic",
                    "freedom": "why_energetic",
                    "balanced": "why_healing",
                    "quick_healing": "why_healing",
                    "dopamine": "why_social",
                }

                relevant_why = story_map.get(selected_story, "why_creative")
                why_evidence = place.get(relevant_why, [])

                # 메트릭 표시
                st.metric(
                    label=f"{place['name'][:20]}...",
                    value=f"{place['score']:.1f}/10",
                    delta=f"{distance:.1f}km",
                )

                # 타입과 평점
                place_type = place.get("place_type", place["type"]).title()
                rating = place.get("rating", "N/A")
                st.caption(f"{place_type} • {rating}/5")

                # 주관적 이유 (첫 번째만)
                if why_evidence:
                    st.caption(f"💭 {why_evidence[0][:50]}...")
                else:
                    st.caption("💭 Analyzing personality...")
            else:
                # 기존 GeoJSON 데이터
                st.metric(
                    label=f"{place['name'][:20]}...",
                    value=f"{place['score']:.1f}/10",
                    delta=f"{distance:.1f}km",
                )
                st.caption(f"{place['type'].title()}")

    # Statistics
    st.markdown('<div class="section-header">Statistics</div>', unsafe_allow_html=True)
    avg_score = sum([p["score"] for p in wellness_places]) / len(wellness_places)

    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        st.metric("Places Found", len(wellness_places))
    with col_b:
        st.metric("Average Score", f"{avg_score:.1f}/10")
    with col_c:
        if st.session_state.generate_route or st.session_state.force_show_route:
            st.metric("Route Mode", "Active")
        else:
            st.metric("Exploration Mode", "Basic")
    with col_d:
        best_score = max([p["score"] for p in wellness_places])
        st.metric("Best Score", f"{best_score:.1f}/10")

else:
    if st.session_state.generate_route or st.session_state.force_show_route:
        st.info("Try selecting different start/end points.")
    else:
        st.info("Choose a story and generate a route!")

# Footer Information
st.markdown("---")
st.markdown(
    f"""
<div class="info-card">

### About Your Wellness Journey
**Current Story:** {story_info['text']}
**Description:** {story_info['description']}

### How It Works
1. **Choose Your Story** - Select from 8 emotional states
2. **Plan Your Route** - Set starting point and destination
3. **AI Optimization** - Generate optimal routes based on wellness scores
4. **Real-time Data** - Utilize official NYC data

### Data Sources
- **NYC Open Data**: Parks, buildings, roads, cultural facilities (70,000+ features)
- **Wellness Algorithm**: Emotional state-based scoring calculation
- **Route Optimization**: Route generation considering distance and wellness scores

**Total Data**: 90,000+ NYC locations analyzed for wellness potential

**Built with:** Python, Streamlit, Folium, NYC GeoJSON Data

</div>
""",
    unsafe_allow_html=True,
)
