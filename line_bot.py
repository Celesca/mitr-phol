from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
from dotenv import load_dotenv
import threading
from Multi_agent import crew_infer

# Load environment variables
load_dotenv()

app = Flask(__name__)

# LINE Bot configuration
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.environ.get('LINE_SECRET_CHANNEL')

if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_CHANNEL_SECRET:
    raise ValueError("LINE_ACCESS_TOKEN and LINE_SECRET_CHANNEL must be set in .env file")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Store active conversations to prevent multiple simultaneous requests
active_conversations = set()

def process_message(user_id, user_message):
    """Process user message and return response"""
    try:
        # Call the crew inference function
        response = crew_infer(user_message)
        # Ensure response is a string
        if not isinstance(response, str):
            response = str(response)
        return response
    except Exception as e:
        error_msg = f"ขออภัยค่ะ เกิดข้อผิดพลาดในการประมวลผล: {str(e)}"
        print(f"Error processing message: {e}")
        return error_msg
    finally:
        # Remove from active conversations
        active_conversations.discard(user_id)

@app.route("/callback", methods=['POST'])
def callback():
    """LINE Webhook callback"""
    # Get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # Get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # Handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """Handle incoming text messages"""
    user_id = event.source.user_id
    user_message = event.message.text.strip()

    # Check if user already has an active conversation
    if user_id in active_conversations:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="กำลังประมวลผลคำถามก่อนหน้านี้อยู่ค่ะ กรุณารอสักครู่...")
        )
        return

    # Add to active conversations
    active_conversations.add(user_id)

    # Send initial waiting message
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="รอสักครู่ค่ะ กำลังเตรียมคำตอบ...")
    )

    # Process message in background thread
    def background_process():
        response = process_message(user_id, user_message)
        print(f"Final response type: {type(response)}")
        print(f"Final response (first 200 chars): {str(response)[:200]}")

        # Send the final response
        try:
            line_bot_api.push_message(
                user_id,
                TextSendMessage(text=str(response))
            )
            print("Message sent successfully")
        except Exception as e:
            print(f"Error sending message: {e}")
            # Try to send error message
            try:
                line_bot_api.push_message(
                    user_id,
                    TextSendMessage(text="ขออภัยค่ะ เกิดข้อผิดพลาดในการส่งข้อความ")
                )
            except:
                pass

    # Start background thread
    thread = threading.Thread(target=background_process)
    thread.daemon = True
    thread.start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)