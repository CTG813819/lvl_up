const { OpenAI } = require('openai');
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

async function suggestImprovement(code) {
  const response = await openai.chat.completions.create({
    model: 'gpt-4', // or 'gpt-3.5-turbo'
    messages: [
      { role: 'system', content: 'You are an expert code reviewer.' },
      { role: 'user', content: `Suggest improvements for this code:\n${code}` }
    ]
  });
  return response.choices[0].message.content;
}

module.exports = { suggestImprovement }; 