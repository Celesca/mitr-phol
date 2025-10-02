from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, ImageMessage, TextSendMessage
import os
from dotenv import load_dotenv
import threading
import requests
import uuid
from datetime import datetime, timedelta
from Multi_agent import crew_infer
from Image_agent import process_sugarcane_image, ImageProcessor
from intent_classifier import classify_message_intent

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

# Store active conversations and pending image classifications
active_conversations = set()
pending_images = {}  # user_id -> {'image_base64': str, 'timestamp': datetime}

def download_image(message_id: str) -> str:
    """Download image from LINE and save to local file, return file path"""
    try:
        # Create images directory if it doesn't exist
        import os
        images_dir = "images"
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)

        # Generate unique filename
        import uuid
        filename = f"{uuid.uuid4()}.jpg"
        filepath = os.path.join(images_dir, filename)

        # Get image content
        message_content = line_bot_api.get_message_content(message_id)

        # Save image data to file
        with open(filepath, 'wb') as f:
            for chunk in message_content.iter_content():
                f.write(chunk)

        print(f"Image saved to: {filepath}")
        return filepath
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None

def cleanup_old_pending_images():
    """Remove pending images older than 10 minutes and their files"""
    current_time = datetime.now()
    expired_users = []
    
    for user_id, data in pending_images.items():
        if current_time - data['timestamp'] > timedelta(minutes=10):
            expired_users.append(user_id)
            # Delete the image file
            try:
                if os.path.exists(data['image_path']):
                    os.remove(data['image_path'])
                    print(f"Deleted old image file: {data['image_path']}")
            except Exception as e:
                print(f"Error deleting image file {data['image_path']}: {e}")
    
    # Remove expired entries
    for user_id in expired_users:
        del pending_images[user_id]

def process_message(user_id, user_message):
    """Process user message and return response"""
    try:
        # First, classify the intent of the message
        intent = classify_message_intent(user_message)
        print(f"Message intent: {intent}")

        if intent == "NATURAL":
            # Natural conversation - instant response
            response = "สวัสดีค่ะ มีไรให้มิตรจังผู้ช่วยชาวไร่อ้อยช่วยคะ?"
            return f"{response}\n\n📚 แหล่งข้อมูล: มิตรผล ผู้ช่วยชาวไร่อ้อย"

        elif intent == "NORMALRAG":
            # Normal sugarcane knowledge - use RAG system
            response = crew_infer(user_message)
            # Ensure response is a string
            if not isinstance(response, str):
                response = str(response)
            return f"{response}\n\n📚 แหล่งข้อมูล: มิตรผล ผู้ช่วยชาวไร่อ้อย"

        elif intent == "LOCALIZE":
            # Localized/farmer-specific data - mock response for now
            response = "ขออภัยค่ะ ขณะนี้ระบบยังไม่รองรับการวิเคราะห์ข้อมูลเฉพาะบุคคลหรือพื้นที่ กรุณาถามคำถามทั่วไปเกี่ยวกับอ้อย หรือติดต่อเจ้าหน้าที่ที่ชำนาญโดยตรง /ปรึกษาผู้เชี่ยวชาญ"
            return f"{response}\n\n📚 แหล่งข้อมูล: มิตรผล ผู้ช่วยชาวไร่อ้อย"

        else:
            # Fallback to normal RAG if classification fails
            response = crew_infer(user_message)
            if not isinstance(response, str):
                response = str(response)
            return f"{response}\n\n📚 แหล่งข้อมูล: มิตรผล ผู้ช่วยชาวไร่อ้อย"

    except Exception as e:
        error_msg = f"ขออภัยค่ะ เกิดข้อผิดพลาดในการประมวลผล: {str(e)}"
        print(f"Error processing message: {e}")
        return f"{error_msg}\n\n📚 แหล่งข้อมูล: มิตรผล ผู้ช่วยชาวไร่อ้อย"
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
def handle_text_message(event):
    """Handle incoming text messages"""
    user_id = event.source.user_id
    user_message = event.message.text.strip()

    # Clean up old pending images
    cleanup_old_pending_images()

    # Check if user has a pending image for classification
    if user_id in pending_images:
        # This is a description for an image classification
        image_path = pending_images[user_id]['image_path']

        # Remove from pending images
        del pending_images[user_id]

        # Clean up the image file after processing
        try:
            if os.path.exists(image_path):
                os.remove(image_path)
                print(f"Cleaned up processed image file: {image_path}")
        except Exception as e:
            print(f"Error cleaning up image file {image_path}: {e}")

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
            TextSendMessage(text="รอสักครู่ค่ะ กำลังวิเคราะห์รูปภาพและจำแนกโรค...")
        )

        # Process image classification in background thread
        def background_process():
            try:
                response = process_sugarcane_image(image_path, user_message)
                print(f"Image classification response: {str(response)[:200]}")

                # Add reference to the response
                final_response = f"{str(response)}\n\n📚 แหล่งข้อมูล: มิตรผล ผู้ช่วยชาวไร่อ้อย"

                # Send the final response
                line_bot_api.push_message(
                    user_id,
                    TextSendMessage(text=final_response)
                )
                print("Image classification result sent successfully")
            except Exception as e:
                print(f"Error in image classification: {e}")
                try:
                    error_response = "ขออภัยค่ะ เกิดข้อผิดพลาดในการวิเคราะห์รูปภาพ"
                    final_error_response = f"{error_response}\n\n📚 แหล่งข้อมูล: มิตรผล ผู้ช่วยชาวไร่อ้อย"
                    line_bot_api.push_message(
                        user_id,
                        TextSendMessage(text=final_error_response)
                    )
                except:
                    pass
            finally:
                active_conversations.discard(user_id)

        # Start background thread
        thread = threading.Thread(target=background_process)
        thread.daemon = True
        thread.start()

    else:
        # This is a regular text question
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
            finally:
                active_conversations.discard(user_id)

        # Start background thread
        thread = threading.Thread(target=background_process)
        thread.daemon = True
        thread.start()

@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    """Handle incoming image messages"""
    user_id = event.source.user_id
    message_id = event.message.id

    # Download and save the image
    image_path = download_image(message_id)

    if image_path:
        # Store the image path for later classification
        pending_images[user_id] = {
            'image_path': image_path,
            'timestamp': datetime.now()
        }

        # Ask for description
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="ได้รับรูปภาพแล้วค่ะ! กรุณาบอกรายละเอียดเพิ่มเติม เช่น อาการที่เห็น หรือคำถามเกี่ยวกับรูปภาพนี้")
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="ขออภัยค่ะ ไม่สามารถดาวน์โหลดรูปภาพได้ กรุณาลองส่งรูปภาพใหม่อีกครั้ง")
        )

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)