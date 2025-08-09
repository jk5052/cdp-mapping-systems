import requests
import re
import random

class SocialNarrativeAnalyzer:
    def __init__(self):
        # Instagram Basic Display API 또는 Hashtag scraping 시뮬레이션
        self.instagram_wellness_hashtags = {
            'creative': ['#nycart', '#creativespace', '#inspiration', '#artistspot'],
            'emotional_recovery': ['#nyczen', '#peaceful', '#mindful', '#tranquil'],
            'social': ['#nychangout', '#meetup', '#community', '#social'],
            'energetic': ['#nycfitness', '#active', '#energy', '#workout'],
            'balanced': ['#balance', '#harmony', '#wellness', '#mindfulness'],
            'quick_healing': ['#quickbreak', '#refresh', '#recharge', '#reset'],
            'freedom': ['#freedom', '#openspace', '#liberation', '#breathe'],
            'dopamine': ['#happy', '#joy', '#mood', '#positivevibes']
        }
        
        # 장소 타입별 소셜 내러티브 템플릿
        self.narrative_templates = {
            'park': {
                'emotional_recovery': [
                    "Visitors often share peaceful moments and meditation sessions here",
                    "Tagged as a #mindfulmoments sanctuary by the community",
                    "People describe feeling 'recharged' after spending time here"
                ],
                'creative': [
                    "Artists frequently sketch and find inspiration in this space",
                    "Photography enthusiasts love the natural lighting here",
                    "Writers often mention this as their favorite thinking spot"
                ],
                'social': [
                    "Popular spot for community gatherings and meetups",
                    "Families and friends often choose this for quality time",
                    "Dog owners create a natural social community here"
                ],
                'energetic': [
                    "Joggers and fitness enthusiasts rate this highly",
                    "Morning yoga sessions are frequently organized here",
                    "People share their workout achievements from this location"
                ]
            },
            'cafe': {
                'creative': [
                    "Local artists and writers call this their 'creative headquarters'",
                    "Instagram posts show laptops, notebooks, and inspiration",
                    "Community describes the atmosphere as 'creatively charged'"
                ],
                'social': [
                    "Perfect spot for first dates and catch-ups with friends",
                    "Business meetings and networking happen naturally here",
                    "Regulars have formed a tight-knit community"
                ],
                'balanced': [
                    "People appreciate the work-life balance this space provides",
                    "Described as a 'productive yet relaxing' environment",
                    "Perfect blend of energy and calm according to reviews"
                ]
            },
            'museum': {
                'creative': [
                    "Visitors share transformative artistic experiences",
                    "Frequently tagged as #inspiration and #arttherapy",
                    "People describe feeling 'creatively awakened' after visits"
                ],
                'emotional_recovery': [
                    "Art therapy sessions and mindful viewing experiences",
                    "Visitors find peace and reflection in the galleries",
                    "Described as a 'sanctuary for the soul' by many"
                ]
            },
            'restaurant': {
                'social': [
                    "Celebration dinners and special occasions happen here",
                    "Community gathering spot for food lovers",
                    "People share memorable dining experiences"
                ],
                'dopamine': [
                    "Food photos get thousands of likes and happy reactions",
                    "Described as a 'mood booster' by food bloggers",
                    "People associate this place with joy and satisfaction"
                ]
            }
        }
    
    def analyze_location_social_context(self, place_name, lat, lng, place_type="unknown"):
        """장소의 소셜 미디어 맥락 분석 (시뮬레이션)"""
        
        social_evidence = {}
        
        # 장소 이름과 타입을 기반으로 소셜 컨텍스트 생성
        for mood in self.instagram_wellness_hashtags.keys():
            mood_score = 0
            found_narratives = []
            hashtag_count = 0
            
            # 장소 타입별 기본 점수
            if place_type in self.narrative_templates:
                if mood in self.narrative_templates[place_type]:
                    mood_score = random.randint(6, 9)
                    found_narratives = self.narrative_templates[place_type][mood]
                    hashtag_count = mood_score * random.randint(15, 25)
            
            # 장소 이름 기반 추가 분석
            name_lower = place_name.lower()
            
            # 공원 관련
            if any(word in name_lower for word in ['park', 'garden', 'green', 'square']):
                if mood in ['emotional_recovery', 'freedom', 'balanced']:
                    mood_score = max(mood_score, random.randint(7, 9))
                    if not found_narratives:
                        found_narratives = self.narrative_templates['park'].get(mood, [])
                    hashtag_count = max(hashtag_count, mood_score * 20)
            
            # 문화 시설 관련
            elif any(word in name_lower for word in ['museum', 'gallery', 'art', 'cultural']):
                if mood in ['creative', 'emotional_recovery']:
                    mood_score = max(mood_score, random.randint(8, 10))
                    if not found_narratives:
                        found_narratives = self.narrative_templates['museum'].get(mood, [])
                    hashtag_count = max(hashtag_count, mood_score * 18)
            
            # 카페/레스토랑 관련
            elif any(word in name_lower for word in ['cafe', 'coffee', 'restaurant', 'bar']):
                if mood in ['social', 'creative', 'dopamine']:
                    mood_score = max(mood_score, random.randint(6, 8))
                    template_key = 'cafe' if 'cafe' in name_lower or 'coffee' in name_lower else 'restaurant'
                    if template_key in self.narrative_templates and not found_narratives:
                        found_narratives = self.narrative_templates[template_key].get(mood, [])
                    hashtag_count = max(hashtag_count, mood_score * 16)
            
            # 기본값 설정
            if mood_score == 0:
                mood_score = random.randint(3, 6)
                hashtag_count = mood_score * 10
                found_narratives = [f"Community members occasionally share {mood} experiences here"]
            
            social_evidence[mood] = {
                'score': mood_score,
                'narratives': found_narratives[:3],  # 최대 3개
                'hashtag_count': hashtag_count,
                'trending_hashtags': random.sample(self.instagram_wellness_hashtags[mood], 
                                                 min(2, len(self.instagram_wellness_hashtags[mood])))
            }
        
        return social_evidence

    def get_collective_wisdom(self, places_list):
        """여러 장소의 집단 지성 분석"""
        
        collective_insights = {
            'popular_combinations': [],
            'hidden_gems': [],
            'community_recommended': []
        }
        
        # 장소 조합별 소셜 데이터 분석
        high_social_score_places = []
        
        for place in places_list:
            social_data = self.analyze_location_social_context(
                place['name'], place['lat'], place['lng'], place.get('type', 'unknown')
            )
            place['social_narrative'] = social_data
            
            # 높은 소셜 점수를 가진 장소들 수집
            avg_social_score = sum(data['score'] for data in social_data.values()) / len(social_data)
            if avg_social_score > 7:
                high_social_score_places.append({
                    'name': place['name'],
                    'avg_social_score': avg_social_score,
                    'top_mood': max(social_data.keys(), key=lambda k: social_data[k]['score'])
                })
        
        # 커뮤니티 추천 장소들
        collective_insights['community_recommended'] = sorted(
            high_social_score_places, 
            key=lambda x: x['avg_social_score'], 
            reverse=True
        )[:5]
        
        # 인기 조합 (시뮬레이션)
        if len(places_list) >= 2:
            collective_insights['popular_combinations'] = [
                f"{places_list[0]['name']} → {places_list[1]['name']}: Perfect for creative flow",
                f"Community loves this route for weekend wellness walks"
            ]
        
        # 숨겨진 보석들 (낮은 hashtag_count이지만 높은 score)
        for place in places_list:
            if 'social_narrative' in place:
                for mood, data in place['social_narrative'].items():
                    if data['score'] > 7 and data['hashtag_count'] < 100:
                        collective_insights['hidden_gems'].append({
                            'name': place['name'],
                            'mood': mood,
                            'reason': f"High {mood} score but undiscovered by mainstream social media"
                        })
        
        return collective_insights

    def get_community_insights(self, place_name, selected_story):
        """특정 장소에 대한 커뮤니티 인사이트"""
        
        insights = {
            'best_times': [],
            'insider_tips': [],
            'community_events': []
        }
        
        # 시뮬레이션된 커뮤니티 인사이트
        if 'park' in place_name.lower():
            insights['best_times'] = ["Early morning for peaceful meditation", "Golden hour for photography"]
            insights['insider_tips'] = ["Bring a book and find the quiet corner near the pond", "Local artists gather here on weekends"]
            insights['community_events'] = ["Weekly yoga sessions on Sundays", "Monthly community cleanup events"]
        
        elif any(word in place_name.lower() for word in ['cafe', 'coffee']):
            insights['best_times'] = ["Mid-morning for creative work", "Afternoon for social meetups"]
            insights['insider_tips'] = ["Ask for the 'artist's corner' table", "Free WiFi password changes weekly"]
            insights['community_events'] = ["Open mic nights on Thursdays", "Book club meetings monthly"]
        
        return insights
