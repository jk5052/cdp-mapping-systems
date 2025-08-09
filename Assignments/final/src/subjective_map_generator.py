import folium
import os
from datetime import datetime
import json

class SubjectiveMapGenerator:
    def __init__(self):
        self.output_dir = "generated_maps"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def generate_subjective_art_map(self, route_data, story_key, route_name):
        """주관적 아트 맵 HTML 생성"""
        
        # 맵 중심점 계산
        all_lats = [route_data['start_loc'][0], route_data['end_loc'][0]]
        all_lngs = [route_data['start_loc'][1], route_data['end_loc'][1]]
        
        for waypoint in route_data['waypoints']:
            all_lats.append(waypoint['lat'])
            all_lngs.append(waypoint['lng'])
        
        center_lat = sum(all_lats) / len(all_lats)
        center_lng = sum(all_lngs) / len(all_lngs)
        
        # 주관적 스타일의 맵 생성
        m = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=13,
            tiles=None
        )
        
        # 아트스타일 타일 추가
        folium.TileLayer(
            tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            attr='OpenStreetMap',
            name='Base Map',
            overlay=False,
            control=True,
            opacity=0.7
        ).add_to(m)
        
        # 스토리별 색상 테마
        story_colors = {
            'creative': '#9C27B0',
            'emotional_recovery': '#4CAF50', 
            'social': '#FF9800',
            'energetic': '#F44336',
            'balanced': '#2196F3',
            'freedom': '#00BCD4',
            'quick_healing': '#FF5722',
            'dopamine': '#E91E63'
        }
        
        route_color = story_colors.get(story_key, '#2c3e50')
        
        # 시작점 마커 (특별한 스타일)
        folium.Marker(
            route_data['start_loc'],
            popup=f"""
            <div style="width:300px; text-align:center;">
                <h3>🚀 Journey Begins</h3>
                <p><strong>{route_data['start_name']}</strong></p>
                <p style="font-style:italic;">Your wellness adventure starts here...</p>
            </div>
            """,
            icon=folium.Icon(color='green', icon='play', prefix='fa')
        ).add_to(m)
        
        # 웨이포인트들 - 주관적 스토리텔링
        for i, waypoint in enumerate(route_data['waypoints']):
            # 소셜 내러티브 정보 가져오기
            social_narrative = waypoint.get('social_narrative', {})
            community_loves = waypoint.get('why_community_loves', [])
            trending_hashtags = waypoint.get('trending_hashtags', [])
            
            # 주관적 설명 생성
            subjective_description = self.generate_subjective_description(
                waypoint, story_key, i+1
            )
            
            popup_content = f"""
            <div style="width:350px; font-family: 'Georgia', serif;">
                <h3 style="color: {route_color};">✨ Stop {i+1}: {waypoint['name']}</h3>
                
                <div style="background: #f8f9fa; padding: 10px; border-radius: 8px; margin: 10px 0;">
                    <h4 style="color: #2c3e50;">🎨 Subjective Experience</h4>
                    <p style="font-style: italic; line-height: 1.6;">{subjective_description}</p>
                </div>
                
                <div style="background: #e8f5e8; padding: 10px; border-radius: 8px; margin: 10px 0;">
                    <h4 style="color: #27ae60;">📊 Wellness Metrics</h4>
                    <p><strong>Wellness Score:</strong> {waypoint['score']:.1f}/10</p>
                    <p><strong>Distance from start:</strong> {waypoint.get('distance_from_start', 0):.1f}km</p>
                </div>
                
                <div style="background: #fff3cd; padding: 10px; border-radius: 8px; margin: 10px 0;">
                    <h4 style="color: #856404;">🌟 Community Voice</h4>
                    {self.format_community_insights(community_loves, trending_hashtags)}
                </div>
            </div>
            """
            
            # 웨이포인트별 다른 아이콘
            icons = ['star', 'heart', 'leaf', 'camera', 'music', 'palette']
            icon_name = icons[i % len(icons)]
            
            folium.Marker(
                [waypoint['lat'], waypoint['lng']],
                popup=popup_content,
                icon=folium.Icon(color='purple', icon=icon_name, prefix='fa')
            ).add_to(m)
        
        # 목적지 마커
        folium.Marker(
            route_data['end_loc'],
            popup=f"""
            <div style="width:300px; text-align:center;">
                <h3>🏁 Journey's End</h3>
                <p><strong>{route_data['end_name']}</strong></p>
                <p style="font-style:italic;">You've completed your wellness journey!</p>
            </div>
            """,
            icon=folium.Icon(color='red', icon='stop', prefix='fa')
        ).add_to(m)
        
        # 아트스틱한 경로 라인
        route_coordinates = [route_data['start_loc']]
        for waypoint in route_data['waypoints']:
            route_coordinates.append([waypoint['lat'], waypoint['lng']])
        route_coordinates.append(route_data['end_loc'])
        
        # 메인 경로
        folium.PolyLine(
            route_coordinates,
            weight=6,
            color=route_color,
            opacity=0.8,
            popup=f"🎨 {route_name} - Subjective Wellness Journey"
        ).add_to(m)
        
        # 그림자 효과
        folium.PolyLine(
            route_coordinates,
            weight=8,
            color='black',
            opacity=0.3,
            offset=-2
        ).add_to(m)
        
        # HTML 파일 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"subjective_map_{story_key}_{timestamp}.html"
        filepath = os.path.join(self.output_dir, filename)
        
        # 커스텀 CSS와 JavaScript 추가
        custom_html = self.add_custom_styling(m, route_name, story_key, route_data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(custom_html)
        
        return filepath, filename
    
    def generate_subjective_description(self, waypoint, story_key, stop_number):
        """주관적 경험 설명 생성"""
        
        descriptions = {
            'creative': [
                f"This {stop_number}{'st' if stop_number == 1 else 'nd' if stop_number == 2 else 'rd' if stop_number == 3 else 'th'} stop pulses with creative energy. The very air seems to whisper artistic possibilities.",
                "Here, inspiration flows like an invisible river, carrying dreams and visions to those who pause to listen.",
                "This space has witnessed countless moments of creative breakthrough, where ordinary thoughts transform into extraordinary art."
            ],
            'emotional_recovery': [
                "A sanctuary where wounded souls find solace. The gentle embrace of this place heals what words cannot touch.",
                "Time moves differently here - slower, kinder, allowing the heart to mend at its own pace.",
                "This haven offers the rare gift of true peace, where emotional storms quiet into gentle whispers."
            ],
            'social': [
                "Conversations bloom here like flowers in spring. Strangers become friends, and friends become family.",
                "The social fabric of the city weaves itself most beautifully in this vibrant gathering place.",
                "Human connections spark and flourish here, creating a tapestry of shared experiences and laughter."
            ],
            'energetic': [
                "Electric vitality courses through this space like lightning through storm clouds. Energy is both given and received.",
                "This dynamic hub charges the spirit and invigorates the soul with its infectious enthusiasm.",
                "Here, lethargy dissolves and vigor awakens, as if the very ground pulses with life force."
            ]
        }
        
        story_descriptions = descriptions.get(story_key, descriptions['creative'])
        return story_descriptions[stop_number % len(story_descriptions)]
    
    def format_community_insights(self, community_loves, trending_hashtags):
        """커뮤니티 인사이트 포맷팅"""
        html = ""
        
        if community_loves:
            html += "<p><strong>What the community says:</strong></p><ul>"
            for reason in community_loves[:2]:
                html += f"<li style='margin: 5px 0;'>{reason}</li>"
            html += "</ul>"
        
        if trending_hashtags:
            html += f"<p><strong>Trending:</strong> {', '.join(trending_hashtags)}</p>"
        
        if not html:
            html = "<p><em>Discovering community insights...</em></p>"
        
        return html
    
    def add_custom_styling(self, folium_map, route_name, story_key, route_data):
        """커스텀 스타일링 추가"""
        
        # 기본 HTML 생성
        map_html = folium_map._repr_html_()
        
        # 커스텀 CSS와 JavaScript 추가
        custom_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>🎨 {route_name} - Subjective Wellness Map</title>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: 'Georgia', serif;
                    margin: 0;
                    padding: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }}
                .header {{
                    background: rgba(255,255,255,0.95);
                    padding: 20px;
                    text-align: center;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .map-container {{
                    height: calc(100vh - 120px);
                    position: relative;
                }}
                .story-info {{
                    position: absolute;
                    top: 10px;
                    right: 10px;
                    background: rgba(255,255,255,0.9);
                    padding: 15px;
                    border-radius: 10px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                    z-index: 1000;
                    max-width: 300px;
                }}
                .leaflet-container {{
                    border-radius: 10px;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎨 {route_name}</h1>
                <p>A subjective wellness journey through NYC</p>
                <p><em>Story: {story_key.replace('_', ' ').title()}</em></p>
            </div>
            
            <div class="map-container">
                <div class="story-info">
                    <h3>📍 Route Summary</h3>
                    <p><strong>Start:</strong> {route_data['start_name']}</p>
                    <p><strong>End:</strong> {route_data['end_name']}</p>
                    <p><strong>Stops:</strong> {len(route_data['waypoints'])}</p>
                    <p><strong>Theme:</strong> {story_key.replace('_', ' ').title()}</p>
                </div>
                {map_html}
            </div>
            
            <script>
                // 맵 로드 후 애니메이션 효과
                window.addEventListener('load', function() {{
                    document.querySelector('.map-container').style.opacity = '0';
                    document.querySelector('.map-container').style.transition = 'opacity 1s ease-in-out';
                    setTimeout(function() {{
                        document.querySelector('.map-container').style.opacity = '1';
                    }}, 500);
                }});
            </script>
        </body>
        </html>
        """
        
        return custom_html
