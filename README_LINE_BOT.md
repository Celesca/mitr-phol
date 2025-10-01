# Sugarcane Farmer Assistant LINE Bot

A LINE chatbot that provides sugarcane farming advice using AI multi-agent system.

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure LINE Channel
1. Go to [LINE Developers Console](https://developers.line.biz/)
2. Create a new channel or use existing one
3. Get your Channel Access Token and Channel Secret
4. Update your `.env` file:
```
LINE_ACCESS_TOKEN=your_channel_access_token_here
LINE_SECRET_CHANNEL=your_channel_secret_here
```

### 3. Set Webhook URL
1. In LINE Developers Console, set the webhook URL to:
   `https://your-domain.com/callback`
2. For local testing, you can use ngrok:
   ```bash
   npm install -g ngrok
   ngrok http 5000
   ```
   Then use the ngrok URL as your webhook URL.

### 4. Run the Bot
```bash
python run_bot.py
```

## Features

- **Multi-Agent AI System**: Uses CrewAI with specialized agents for classification, retrieval, and advice generation
- **RAG Integration**: Retrieves relevant information from sugarcane knowledge base
- **Thai Language Support**: Provides advice in Thai for farmers
- **Structured Responses**: Answers formatted with numbered points for clarity
- **Async Processing**: Handles multiple conversations simultaneously

## How It Works

1. User sends a question via LINE
2. Bot immediately responds with "รอสักครู่ค่ะ กำลังเตรียมคำตอบ..." (Please wait, preparing answer...)
3. Question is processed by the multi-agent system:
   - **Classifier Agent**: Categorizes the question
   - **Retriever Agent**: Searches knowledge base using RAG
   - **Advisor Agent**: Provides structured advice in Thai
4. Final answer is sent back to the user

## Environment Variables

- `LINE_ACCESS_TOKEN`: Your LINE Channel Access Token
- `LINE_SECRET_CHANNEL`: Your LINE Channel Secret
- `AWS_ACCESS_KEY_ID`: AWS access key for Bedrock
- `AWS_SECRET_ACCESS_KEY`: AWS secret key for Bedrock

## Troubleshooting

- Make sure all environment variables are set in `.env` file
- Verify LINE channel is properly configured
- Check webhook URL is accessible from LINE servers
- Ensure all dependencies are installed