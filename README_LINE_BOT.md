# Sugarcane Farmer Assistant LINE Bot

A LINE chatbot that provides sugarcane farming advice using AI multi-agent system with multimodal image analysis.

## Features

- **Text-based Q&A**: Answer sugarcane farming questions using RAG and multi-agent AI
- **Image Disease Classification**: Upload sugarcane images to identify diseases using Claude Sonnet 4 vision
- **Thai Language Support**: Provides advice in Thai for farmers
- **Structured Responses**: Answers formatted with numbered points for clarity
- **Async Processing**: Handles multiple conversations simultaneously

## How to Use

### Text Questions
Simply send any sugarcane farming question in Thai or English:
- "พันธุ์อ้อยที่ทนโรคใบด่าง"
- "วิธีการปลูกอ้อยที่ดีที่สุด"
- "โรคที่พบบ่อยในอ้อย"

### Image Classification
1. **Send an image** of sugarcane showing symptoms
2. **Bot responds**: "ได้รับรูปภาพแล้วค่ะ! กรุณาบอกรายละเอียดเพิ่มเติม เช่น อาการที่เห็น หรือคำถามเกี่ยวกับรูปภาพนี้"
3. **Send text description** like "ใบเหลือง" or "มีจุดด่างๆ"
4. **Bot analyzes** and provides disease classification with treatment recommendations

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

## Supported Diseases

The bot can identify common sugarcane diseases including:
- Pokkah Boeng (Pokkah disease)
- Leaf scald
- Red rot
- Wilt disease
- Rust disease
- Smut disease
- Mosaic virus
- Leaf blight
- Eyespot disease
- Downy mildew

## Environment Variables

- `LINE_ACCESS_TOKEN`: Your LINE Channel Access Token
- `LINE_SECRET_CHANNEL`: Your LINE Channel Secret
- `AWS_ACCESS_KEY_ID`: AWS access key for Bedrock
- `AWS_SECRET_ACCESS_KEY`: AWS secret key for Bedrock

## Architecture

### Multi-Agent System
- **Classifier Agent**: Categorizes questions into sugarcane topics
- **Retriever Agent**: Searches knowledge base using RAG
- **Advisor Agent**: Provides structured advice in Thai
- **Image Analyzer Agent**: Analyzes visual symptoms in sugarcane images
- **Disease Classifier Agent**: Identifies specific diseases and provides treatment

### Image Processing Flow
1. User uploads image → Stored temporarily
2. User provides description → Image + text sent to Claude Sonnet 4
3. Multi-agent analysis → Disease identification and recommendations
4. Structured response → Sent back to user

## Troubleshooting

- Make sure all environment variables are set in `.env` file
- Verify LINE channel is properly configured
- Check webhook URL is accessible from LINE servers
- Ensure all dependencies are installed
- For image processing, ensure images are clear and well-lit