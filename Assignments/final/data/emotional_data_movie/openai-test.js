import OpenAI from 'openai';
import { OPENAI_API_KEY } from './config.js';

const openai = new OpenAI({
    apiKey: OPENAI_API_KEY
});

async function testOpenAI() {
    try {
        const response = await openai.chat.completions.create({
            model: "gpt-3.5-turbo",
            messages: [
                { role: "user", content: "영화 '타이타닉'의 감정을 sadness, romance, drama 0-1 점수로 분석해줘" }
            ],
            max_tokens: 150
        });
        
        console.log('OpenAI 연결 성공!');
        console.log('응답:', response.choices[0].message.content);
    } catch (error) {
        console.error('오류:', error.message);
    }
}

testOpenAI();