import axios from 'axios';
import { TMDB_API_KEY } from './config.js';

const BASE_URL = 'https://api.themoviedb.org/3';

async function testTMDB() {
    try {
        const response = await axios.get(`${BASE_URL}/movie/popular?api_key=${TMDB_API_KEY}`);
        console.log('TMDB 연결 성공!');
        console.log('첫 번째 영화:', response.data.results[0].title);
    } catch (error) {
        console.error('오류:', error.message);
    }
}

testTMDB();