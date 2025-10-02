from crewai import LLM, Agent, Task, Crew
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class IntentClassifier:
    """Classify user messages into different intent categories for LINE bot"""

    def __init__(self):
        # Initialize Claude for intent classification
        self.llm = LLM(
            model="us.qwen.qwen3-32b-v1:0",
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            aws_region_name="us-east-1"
        )

        # Create intent classification agent
        self.classifier_agent = Agent(
            llm=self.llm,
            role="Intent Classifier",
            goal="Classify user messages into appropriate intent categories for sugarcane farming assistant",
            backstory="You are an expert at understanding user intentions in agricultural conversations, especially for sugarcane farming in Thailand.",
            verbose=False  # Keep quiet for faster responses
        )

    def classify_intent(self, message: str) -> str:
        """
        Classify the intent of a user message

        Args:
            message: The user's message text

        Returns:
            Intent category: "NATURAL", "NORMALRAG", or "LOCALIZE"
        """

        # Quick checks for obvious cases first
        message_lower = message.lower().strip()

        # Check for natural conversation starters
        natural_keywords = [
            'สวัสดี', 'hello', 'hi', 'หวัดดี', 'ดี', 'สบายดี',
            'ช่วยเหลือ', 'ช่วยอะไร', 'ทำอะไรได้บ้าง', 'ทำอะไรให้'
        ]

        if any(keyword in message_lower for keyword in natural_keywords) or len(message.strip()) < 5:
            return "NATURAL"

        # Use AI classification for more complex cases
        task = Task(
            description=f"""
            Classify this user message into one of three intent categories:

            Message: "{message}"

            Categories:
            1. NATURAL - Casual conversation, greetings, or general questions that don't require specific sugarcane knowledge. Examples: "สวัสดี", "มีไรให้ช่วย", "ทำอะไรได้บ้าง"

            2. NORMALRAG - Questions about general sugarcane farming knowledge that can be answered using the knowledge base. Examples: "อ้อยโตยังไง", "โรคอะไรที่พบบ่อย", "พันธุ์อ้อยที่ดี"

            3. LOCALIZE - Questions that require specific farmer data, location-based information, or personalized recommendations. Examples: "ที่นี่อ้อยเป็นยังไง", "อ้อยของฉัน", "ที่บ้านฉัน", "แปลงของฉัน"

            Return ONLY the intent category name (NATURAL, NORMALRAG, or LOCALIZE) without any explanation.
            """,
            expected_output="One of: NATURAL, NORMALRAG, LOCALIZE",
            agent=self.classifier_agent
        )

        crew = Crew(
            agents=[self.classifier_agent],
            tasks=[task],
            verbose=False,
            planning=False
        )

        result = crew.kickoff()

        # Extract the result
        if hasattr(result, 'final_output'):
            intent = str(result.final_output).strip()
        elif hasattr(result, 'output'):
            intent = str(result.output).strip()
        elif hasattr(result, 'raw'):
            intent = str(result.raw).strip()
        else:
            intent = str(result).strip()

        # Clean up the intent (remove any extra text)
        intent = intent.upper().replace("INTENT:", "").replace("CATEGORY:", "").strip()

        # Validate and default to NORMALRAG if unclear
        if intent not in ["NATURAL", "NORMALRAG", "LOCALIZE"]:
            # Additional fallback logic
            if any(word in message_lower for word in ['ฉัน', 'บ้าน', 'ที่นี่', 'แปลง', 'ฟาร์ม', 'ไร่']):
                return "LOCALIZE"
            else:
                return "NORMALRAG"

        return intent

def classify_message_intent(message: str) -> str:
    """
    Convenience function to classify message intent

    Args:
        message: User message text

    Returns:
        Intent category
    """
    classifier = IntentClassifier()
    return classifier.classify_intent(message)