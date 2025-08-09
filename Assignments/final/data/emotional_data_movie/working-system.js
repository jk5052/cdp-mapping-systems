import axios from 'axios';
import OpenAI from 'openai';
import fs from 'fs';
import { TMDB_API_KEY, OPENAI_API_KEY } from './config.js';

const BASE_URL = 'https://api.themoviedb.org/3';
const openai = new OpenAI({ apiKey: OPENAI_API_KEY });

// 풀 스케일 설정
const countries = ['US', 'KR', 'JP', 'IN', 'CN', 'FR', 'DE', 'UK', 'IT', 'ES', 'BR', 'MX', 'RU', 'EG', 'NG', 'ZA', 'AU', 'CA', 'SE', 'NO'];
const years = Array.from({length: 35}, (_, i) => 1990 + i);
const moviesPerYear = 3;

let processedMovies = [];

// 핵심 감정 질감 (30개)
function getCoreEmotionTextures() {
    return {
        // 존재감/무게 (8개)
        heaviness: 0.5, lightness: 0.5, density: 0.5, emptiness: 0.5,
        solidity: 0.5, fragility: 0.5, weight: 0.5, buoyancy: 0.5,
        
        // 온도/촉감 (8개)
        warmth: 0.5, coldness: 0.5, burning: 0.5, freezing: 0.5,
        tenderness: 0.5, harshness: 0.5, smoothness: 0.5, roughness: 0.5,
        
        // 움직임/리듬 (8개)
        flowing: 0.5, stagnation: 0.5, pulsing: 0.5, stillness: 0.5,
        acceleration: 0.5, deceleration: 0.5, rhythm: 0.5, chaos: 0.5,
        
        // 빛/어둠/투명도 (6개)
        luminosity: 0.5, darkness: 0.5, transparency: 0.5, 
        opacity: 0.5, clarity: 0.5, murkiness: 0.5
    };
}

// 영화 기본 정보 + 상세 정보 가져오기
async function getTopMoviesByCountryYear(country, year, retries = 3) {
    for (let attempt = 1; attempt <= retries; attempt++) {
        try {
            const response = await axios.get(`${BASE_URL}/discover/movie`, {
                params: {
                    api_key: TMDB_API_KEY,
                    primary_release_year: year,
                    region: country,
                    sort_by: 'popularity.desc',
                    page: 1,
                    'vote_count.gte': 10
                },
                timeout: 10000
            });
            
            return response.data.results.slice(0, moviesPerYear);
            
        } catch (error) {
            console.error(`영화 수집 오류 (${country} ${year}) - 시도 ${attempt}/${retries}:`, error.message);
            
            if (attempt < retries) {
                console.log(`⏳ ${attempt * 5}초 후 재시도...`);
                await sleep(attempt * 5000);
            }
        }
    }
    
    console.log(`❌ ${country} ${year} 최종 실패 - 건너뛰기`);
    return [];
}

async function getMovieDetails(movieId) {
    try {
        const [movieResponse, creditsResponse, reviewsResponse] = await Promise.all([
            axios.get(`${BASE_URL}/movie/${movieId}`, { params: { api_key: TMDB_API_KEY } }),
            axios.get(`${BASE_URL}/movie/${movieId}/credits`, { params: { api_key: TMDB_API_KEY } }),
            axios.get(`${BASE_URL}/movie/${movieId}/reviews`, { params: { api_key: TMDB_API_KEY } })
        ]);
        
        const movie = movieResponse.data;
        const director = creditsResponse.data.crew.find(person => person.job === 'Director');
        const reviews = reviewsResponse.data.results.slice(0, 3);
        
        return {
            title: movie.title,
            overview: movie.overview || 'No overview available',
            genres: movie.genres.map(g => g.name),
            director: director ? director.name : 'Unknown',
            reviews: reviews.map(r => r.content),
            tagline: movie.tagline || '',
            runtime: movie.runtime || 0
        };
    } catch (error) {
        console.error(`영화 상세정보 오류 (ID: ${movieId}):`, error.message);
        return null;
    }
}

// Layer 1: 영화의 핵심 메시지 추출 및 감정 질감 분석
async function analyzeMovieMessage(movieDetails) {
    try {
        console.log(`🎭 Layer 1: "${movieDetails.title}" 핵심 메시지 분석 중...`);
        
        const response = await openai.chat.completions.create({
            model: "gpt-4o-mini", // 더 안정적인 모델 사용
            messages: [{
                role: "system",
                content: `You are an expert film analyst. Analyze the core message and emotional texture of films.
                
CRITICAL: Return ONLY valid JSON. No explanations, no markdown, no extra text.`
            }, {
                role: "user",
                content: `Film: "${movieDetails.title}"
Director: ${movieDetails.director}
Plot: ${movieDetails.overview}
Genres: ${movieDetails.genres.join(', ')}
Tagline: ${movieDetails.tagline}

Analyze the film's CORE MESSAGE and the emotional textures it creates:

1. What is the film's central theme/message about human condition?
2. What emotional qualities does this message evoke?

Return this exact JSON format with values 0.0-1.0:
{
  "core_message": "brief description",
  "heaviness": 0.5,
  "lightness": 0.5,
  "density": 0.5,
  "emptiness": 0.5,
  "warmth": 0.5,
  "coldness": 0.5,
  "tenderness": 0.5,
  "harshness": 0.5,
  "flowing": 0.5,
  "stagnation": 0.5,
  "luminosity": 0.5,
  "darkness": 0.5,
  "transparency": 0.5,
  "opacity": 0.5,
  "rhythm": 0.5,
  "chaos": 0.5
}`
            }],
            max_tokens: 400,
            temperature: 0.3
        });
        
        const content = response.choices[0].message.content.trim();
        console.log('🔍 Layer 1 응답 길이:', content.length);
        
        // JSON 추출 및 파싱
        const jsonMatch = content.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
            try {
                const parsed = JSON.parse(jsonMatch[0]);
                const coreMessage = parsed.core_message || 'Unknown';
                console.log(`✅ Layer 1 완료 - 핵심 메시지: "${coreMessage}"`);
                
                // core_message 제거하고 질감 데이터만 추출
                delete parsed.core_message;
                
                // 나머지 질감들은 기본값으로 채우기
                const fullTextures = getCoreEmotionTextures();
                Object.assign(fullTextures, parsed);
                
                return { textures: fullTextures, message: coreMessage };
            } catch (e) {
                console.log('❌ JSON 파싱 실패:', e.message);
            }
        }
        
        console.log('⚠️ 기본값 사용');
        return { textures: getCoreEmotionTextures(), message: 'Analysis failed' };
        
    } catch (error) {
        console.error('Layer 1 분석 오류:', error.message);
        return { textures: getCoreEmotionTextures(), message: 'Error' };
    }
}

// Layer 2: 관객 리뷰에서 실제 감정 반응 분석
async function analyzeAudienceResponse(reviews, coreMessage) {
    if (!reviews || reviews.length === 0) {
        console.log('⚠️ Layer 2: 리뷰 없음, 기본값 사용');
        return getCoreEmotionTextures();
    }
    
    try {
        console.log(`🎭 Layer 2: 관객 감정 반응 분석 중...`);
        const reviewTexts = reviews.join(' ').substring(0, 800); // 길이 제한
        
        const response = await openai.chat.completions.create({
            model: "gpt-4o-mini",
            messages: [{
                role: "system",
                content: "Analyze audience emotional responses. Return ONLY valid JSON."
            }, {
                role: "user",
                content: `Film's core message: "${coreMessage}"
Audience reviews: "${reviewTexts}"

How did audiences ACTUALLY FEEL? What emotional textures emerge from their responses?

Return ONLY this JSON with values 0.0-1.0:
{
  "heaviness": 0.5,
  "lightness": 0.5,
  "warmth": 0.5,
  "coldness": 0.5,
  "flowing": 0.5,
  "stagnation": 0.5,
  "luminosity": 0.5,
  "darkness": 0.5,
  "tenderness": 0.5,
  "harshness": 0.5
}`
            }],
            max_tokens: 200,
            temperature: 0.3
        });
        
        const content = response.choices[0].message.content.trim();
        const jsonMatch = content.match(/\{[\s\S]*\}/);
        
        if (jsonMatch) {
            try {
                const parsed = JSON.parse(jsonMatch[0]);
                const fullTextures = getCoreEmotionTextures();
                Object.assign(fullTextures, parsed);
                console.log(`✅ Layer 2 완료 - 관객 반응 분석`);
                return fullTextures;
            } catch (e) {
                console.log('❌ Layer 2 JSON 파싱 실패');
            }
        }
        
        return getCoreEmotionTextures();
        
    } catch (error) {
        console.error('Layer 2 분석 오류:', error.message);
        return getCoreEmotionTextures();
    }
}

// Layer 3: 문화적/시대적 맥락에서의 감정적 의미
async function analyzeCulturalEmotionalContext(movieDetails, country, year, coreMessage) {
    try {
        console.log(`🎭 Layer 3: 문화적 감정 맥락 분석 중...`);
        
        const response = await openai.chat.completions.create({
            model: "gpt-4o-mini",
            messages: [{
                role: "system", 
                content: "Analyze cultural-emotional context of films. Return ONLY valid JSON."
            }, {
                role: "user",
                content: `Film: "${movieDetails.title}" (${country}, ${year})
Core message: "${coreMessage}"
Historical context: What was happening in ${country} around ${year}?

What emotional textures does this message carry in THIS specific cultural/historical moment?

Return ONLY this JSON with values 0.0-1.0:
{
  "heaviness": 0.5,
  "density": 0.5,
  "warmth": 0.5,
  "coldness": 0.5,
  "flowing": 0.5,
  "luminosity": 0.5,
  "darkness": 0.5,
  "transparency": 0.5
}`
            }],
            max_tokens: 200,
            temperature: 0.3
        });
        
        const content = response.choices[0].message.content.trim();
        const jsonMatch = content.match(/\{[\s\S]*\}/);
        
        if (jsonMatch) {
            try {
                const parsed = JSON.parse(jsonMatch[0]);
                const fullTextures = getCoreEmotionTextures();
                Object.assign(fullTextures, parsed);
                console.log(`✅ Layer 3 완료 - 문화적 맥락 분석`);
                return fullTextures;
            } catch (e) {
                console.log('❌ Layer 3 JSON 파싱 실패');
            }
        }
        
        return getCoreEmotionTextures();
        
    } catch (error) {
        console.error('Layer 3 분석 오류:', error.message);
        return getCoreEmotionTextures();
    }
}

// 단일 영화 완전 처리 (메시지 중심 3 Layers)
async function processMovie(movie, country, year) {
    console.log(`\n🎬 처리 중: ${movie.title} (${country} ${year})`);
    
    try {
        // 영화 상세 정보 수집
        const movieDetails = await getMovieDetails(movie.id);
        if (!movieDetails) {
            console.log(`❌ "${movie.title}" 상세정보 수집 실패`);
            return null;
        }
        
        // Layer 1: 핵심 메시지 + 감정 질감 분석
        const layer1Result = await analyzeMovieMessage(movieDetails);
        await sleep(2000); // API rate limit 방지
        
        // Layer 2: 관객 반응 분석 (핵심 메시지 전달)
        const layer2 = await analyzeAudienceResponse(movieDetails.reviews, layer1Result.message);
        await sleep(2000);
        
        // Layer 3: 문화적 맥락 분석 (핵심 메시지 전달) 
        const layer3 = await analyzeCulturalEmotionalContext(movieDetails, country, year, layer1Result.message);
        await sleep(2000);
        
        const result = {
            basic_info: {
                id: movie.id,
                title: movie.title,
                country: country,
                year: year,
                director: movieDetails.director,
                genres: movieDetails.genres,
                vote_average: movie.vote_average,
                core_message: layer1Result.message // 핵심 메시지 저장
            },
            emotion_layers: {
                layer1_message_based: layer1Result.textures,
                layer2_audience_response: layer2,
                layer3_cultural_context: layer3
            },
            processed_at: new Date().toISOString()
        };
        
        return result;
        
    } catch (error) {
        console.error(`영화 처리 오류 (${movie.title}):`, error.message);
        return null;
    }
}

// 메인 처리 함수
async function processAllMovies() {
    console.log(`🚀 메시지 기반 감정 분석 시작: ${countries.length}개국 × ${years.length}년 × ${moviesPerYear}개 = 총 ${countries.length * years.length * moviesPerYear}개 영화`);
    
    let totalProcessed = 0;
    const totalTarget = countries.length * years.length * moviesPerYear;
    
    for (const country of countries) {
        console.log(`\n🌍 === ${country} 처리 시작 ===`);
        
        for (const year of years) {
            try {
                console.log(`📅 ${country} ${year} 처리 중...`);
                const movies = await getTopMoviesByCountryYear(country, year);
                
                for (const movie of movies) {
                    const processedMovie = await processMovie(movie, country, year);
                    
                    if (processedMovie) {
                        processedMovies.push(processedMovie);
                        totalProcessed++;
                        
                        console.log(`✅ 완료 (${totalProcessed}/${totalTarget}): ${movie.title}`);
                        console.log(`💭 핵심 메시지: "${processedMovie.basic_info.core_message}"`);
                        
                        // 10개마다 중간 저장
                        if (totalProcessed % 10 === 0) {
                            saveResults();
                        }
                    }
                    
                    // API rate limit 방지 (영화 하나당 15초 대기)
                    await sleep(15000);
                }
                
            } catch (error) {
                console.error(`${country} ${year} 처리 중 오류:`, error.message);
                continue;
            }
        }
        
        console.log(`🎉 ${country} 완료! 지금까지 ${totalProcessed}개 처리됨`);
    }
    
    // 최종 저장
    saveResults();
    console.log(`\n🎉 전체 처리 완료! 총 ${totalProcessed}개 영화의 메시지 기반 감정 데이터 생성`);
}

// 유틸리티 함수들
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function saveResults() {
    const filename = `message_based_emotion_data_${new Date().toISOString().slice(0, 10)}.json`;
    fs.writeFileSync(filename, JSON.stringify(processedMovies, null, 2));
    console.log(`💾 진행상황 저장됨: ${filename} (${processedMovies.length}개 영화)`);
}

// 실행
console.log('🎬 메시지 기반 영화 감정 분석 시스템 시작!');
console.log('📝 핵심: 영화의 메시지가 만들어내는 감정적 질감을 분석합니다');
console.log('⚠️  예상 시간: 4-5시간 (더 정교한 분석으로 인해)');

// 중단 시 데이터 저장
process.on('SIGINT', () => {
    console.log('\n중단 요청됨. 현재까지의 데이터를 저장합니다...');
    saveResults();
    process.exit(0);
});

// 메인 실행
processAllMovies().catch(error => {
    console.error('시스템 오류:', error);
    saveResults();
});