import json
import pandas as pd
import geopandas as gpd
import streamlit as st
from pathlib import Path


@st.cache_data
def load_geojson_data():
    """GeoJSON과 CSV 파일들을 로드"""
    data = {}
    data_dir = Path("data/nyc_qgis")

    # 실제 파일명들로 매핑
    file_mapping = {
        "buildings": {"file": "manhattan_buildings.geojson", "type": "geojson"},
        "parks": {"file": "manhattan_parks.geojson", "type": "geojson"},
        "streets": {"file": "manhattan_streets.geojson", "type": "geojson"},
        "cultural": {"file": "manhattan_cultural.csv", "type": "csv"},
    }

    for key, file_info in file_mapping.items():
        filepath = data_dir / file_info["file"]

        if filepath.exists():
            try:
                if file_info["type"] == "geojson":
                    with open(filepath, "r", encoding="utf-8") as f:
                        data[key] = json.load(f)

                elif file_info["type"] == "csv":
                    df = pd.read_csv(filepath)
                    data[key] = df

            except Exception:
                pass  # 조용히 실패 처리

    return data


def get_sample_places(data, place_type="parks", limit=10):
    """데이터에서 샘플 장소들 추출"""
    if place_type not in data:
        return []

    places = []

    if place_type == "cultural":
        # CSV 데이터 처리
        df = data[place_type]
        for _, row in df.head(limit).iterrows():
            places.append(
                {
                    "name": row.get("name", "Unknown"),
                    "type": place_type,
                    "properties": row.to_dict(),
                }
            )
    else:
        # GeoJSON 데이터 처리
        features = data[place_type].get("features", [])
        for feature in features[:limit]:
            coords = feature.get("geometry", {}).get("coordinates", [0, 0])
            places.append(
                {
                    "name": feature.get("properties", {}).get("name", "Unknown"),
                    "lat": coords[1] if len(coords) >= 2 else 0,
                    "lng": coords[0] if len(coords) >= 2 else 0,
                    "type": place_type,
                    "properties": feature.get("properties", {}),
                }
            )

    return places
