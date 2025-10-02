from crewai import LLM, Agent, Task, Crew
import os
from dotenv import load_dotenv
import base64
import requests
from typing import Optional, Dict, Any

# Load environment variables
load_dotenv()

class ImageProcessor:
    """Helper class to process images for Claude vision"""

    @staticmethod
    def encode_image_from_url(image_url: str) -> str:
        """Download image from URL and encode as base64"""
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            image_data = response.content
            return base64.b64encode(image_data).decode('utf-8')
        except Exception as e:
            raise Exception(f"Failed to download image: {str(e)}")

    @staticmethod
    def encode_image_from_path(image_path: str) -> str:
        """Encode local image file as base64"""
        try:
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
                return base64.b64encode(image_data).decode('utf-8')
        except Exception as e:
            raise Exception(f"Failed to read image file: {str(e)}")

class SugarcaneDiseaseClassifier:
    """Multi-agent system for sugarcane disease classification using images"""

    def __init__(self):
        # Initialize Claude Sonnet 4 with vision capabilities
        self.llm = LLM(
            model="us.anthropic.claude-sonnet-4-20250514-v1:0",
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            aws_region_name="us-east-1"
        )

        # Create specialized agents
        self.image_analyzer = Agent(
            llm=self.llm,
            role="Sugarcane Disease Image Analyzer",
            goal="Analyze sugarcane images to identify visual symptoms of diseases",
            backstory="I am an expert in visual analysis of sugarcane plants, specializing in identifying disease symptoms from photographs. I can detect discoloration, lesions, wilting, and other visual indicators of sugarcane diseases.",
            verbose=True
        )

        self.disease_classifier = Agent(
            llm=self.llm,
            role="Disease Classification Specialist",
            goal="Classify sugarcane diseases based on symptoms and provide treatment recommendations",
            backstory="I am a sugarcane pathology expert who can accurately diagnose diseases based on symptoms and provide evidence-based treatment recommendations. I understand the common diseases affecting sugarcane in Thailand and their management strategies.",
            verbose=True
        )

        self.advisor_agent = Agent(
            llm=self.llm,
            role="Treatment Advisor",
            goal="Provide practical treatment recommendations and prevention strategies",
            backstory="I am a helpful agricultural advisor who provides clear, actionable recommendations for managing sugarcane diseases. I focus on integrated pest management and sustainable farming practices.",
            verbose=True
        )

    def classify_disease_from_image(self, image_path: str, user_description: str = "") -> str:
        """
        Classify sugarcane disease from image file path and user description

        Args:
            image_path: Path to the image file
            user_description: Optional text description from user

        Returns:
            Classification result with treatment recommendations
        """

        # Convert image to base64 for Claude vision API
        try:
            image_base64 = ImageProcessor.encode_image_from_path(image_path)
        except Exception as e:
            return f"Error processing image: {str(e)}"

        # For now, use direct LLM call for image analysis since CrewAI context might not work properly with vision
        try:
            # Create the message with image for Claude vision
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"""Analyze this sugarcane image for disease symptoms. Look for:
- Leaf discoloration (yellowing, browning, reddening)
- Lesions, spots, or streaks on leaves
- Wilting or drooping
- Root rot or stem damage
- Fungal growth or mold
- Insect damage signs
- Nutrient deficiency symptoms

User description: {user_description}

Provide a detailed description of what you see in the image."""
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_base64
                            }
                        }
                    ]
                }
            ]

            # Call Claude directly for image analysis
            response = self.llm.invoke(messages)
            image_analysis = str(response)

            # Now use CrewAI for the remaining tasks with the analysis result
            return self._process_with_crew(image_analysis, user_description)

        except Exception as e:
            print(f"Error in direct LLM call: {e}")
            # Fallback to CrewAI approach
            return self._process_with_crew_fallback(image_base64, user_description)

    def _process_with_crew(self, image_analysis: str, user_description: str) -> str:
        """Process with CrewAI using the image analysis result"""

        # Task 2: Classify the disease based on symptoms
        task2 = Task(
            description=f"""
            Based on this visual analysis of the sugarcane image: '{image_analysis}'

            Classify the sugarcane disease.

            Common sugarcane diseases in Thailand:
            1. Pokkah Boeng (Pokkah disease) - White stripe on leaves
            2. Leaf scald - Water-soaked lesions
            3. Red rot - Red discoloration in stalks
            4. Wilt disease - Sudden wilting
            5. Rust disease - Orange pustules on leaves
            6. Smut disease - Black whip-like structures
            7. Mosaic virus - Yellow/green mottling
            8. Leaf blight - Brown lesions
            9. Eyespot disease - Small circular spots
            10. Downy mildew - White fungal growth

            User description: {user_description}

            Provide:
            - Disease name
            - Confidence level
            - Key symptoms that match
            - Differential diagnosis (why not other diseases)
            """,
            expected_output="Disease classification with confidence level and reasoning",
            agent=self.disease_classifier
        )

        # Task 3: Provide treatment recommendations
        task3 = Task(
            description="""Based on the disease classification, provide comprehensive treatment recommendations.

Include:
1. Immediate actions to contain the disease
2. Chemical treatments (if appropriate)
3. Cultural practices to prevent spread
4. Prevention strategies for the future
5. Monitoring recommendations

Structure the response with numbered points for clarity.
Use Thai language for the final recommendations.""",
            expected_output="Structured treatment recommendations in Thai with numbered points",
            agent=self.advisor_agent
        )

        # Create and run the crew
        crew = Crew(
            agents=[self.disease_classifier, self.advisor_agent],
            tasks=[task2, task3],
            verbose=True,
            planning=False
        )

        result = crew.kickoff()

        # Extract the final result
        if hasattr(result, 'final_output'):
            return str(result.final_output)
        elif hasattr(result, 'output'):
            return str(result.output)
        elif hasattr(result, 'raw'):
            return str(result.raw)
        else:
            return str(result)

    def _process_with_crew_fallback(self, image_base64: str, user_description: str) -> str:
        """Fallback method using CrewAI context approach"""

        # Task 1: Analyze the image for disease symptoms
        image_analysis_prompt = f"""
        Analyze this sugarcane image for disease symptoms. Look for:
        - Leaf discoloration (yellowing, browning, reddening)
        - Lesions, spots, or streaks on leaves
        - Wilting or drooping
        - Root rot or stem damage
        - Fungal growth or mold
        - Insect damage signs
        - Nutrient deficiency symptoms

        User description: {user_description}

        Provide a detailed description of what you see in the image.
        """

        task1 = Task(
            description=image_analysis_prompt,
            expected_output="Detailed visual analysis of disease symptoms observed in the sugarcane image",
            agent=self.image_analyzer,
            context=[{
                "description": "Sugarcane plant image for disease analysis",
                "expected_output": "Visual analysis of plant symptoms",
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": image_base64
                }
            }]
        )

        # Task 2: Classify the disease based on symptoms
        task2 = Task(
            description="""Based on the visual analysis from Task 1, classify the sugarcane disease.

Common sugarcane diseases in Thailand:
1. Pokkah Boeng (Pokkah disease) - White stripe on leaves
2. Leaf scald - Water-soaked lesions
3. Red rot - Red discoloration in stalks
4. Wilt disease - Sudden wilting
5. Rust disease - Orange pustules on leaves
6. Smut disease - Black whip-like structures
7. Mosaic virus - Yellow/green mottling
8. Leaf blight - Brown lesions
9. Eyespot disease - Small circular spots
10. Downy mildew - White fungal growth

Provide:
- Disease name
- Confidence level
- Key symptoms that match
- Differential diagnosis (why not other diseases)""",
            expected_output="Disease classification with confidence level and reasoning",
            agent=self.disease_classifier
        )

        # Task 3: Provide treatment recommendations
        task3 = Task(
            description="""Based on the disease classification, provide comprehensive treatment recommendations.

Include:
1. Immediate actions to contain the disease
2. Chemical treatments (if appropriate)
3. Cultural practices to prevent spread
4. Prevention strategies for the future
5. Monitoring recommendations

Structure the response with numbered points for clarity.
Use Thai language for the final recommendations.""",
            expected_output="Structured treatment recommendations in Thai with numbered points",
            agent=self.advisor_agent
        )

        # Create and run the crew
        crew = Crew(
            agents=[self.image_analyzer, self.disease_classifier, self.advisor_agent],
            tasks=[task1, task2, task3],
            verbose=True,
            planning=False
        )

        result = crew.kickoff()

        # Extract the final result
        if hasattr(result, 'final_output'):
            return str(result.final_output)
        elif hasattr(result, 'output'):
            return str(result.output)
        elif hasattr(result, 'raw'):
            return str(result.raw)
        else:
            return str(result)

        # Task 2: Classify the disease based on symptoms
        task2 = Task(
            description="""
            Based on the visual analysis from Task 1, classify the sugarcane disease.

            Common sugarcane diseases in Thailand:
            1. Pokkah Boeng (Pokkah disease) - White stripe on leaves
            2. Leaf scald - Water-soaked lesions
            3. Red rot - Red discoloration in stalks
            4. Wilt disease - Sudden wilting
            5. Rust disease - Orange pustules on leaves
            6. Smut disease - Black whip-like structures
            7. Mosaic virus - Yellow/green mottling
            8. Leaf blight - Brown lesions
            9. Eyespot disease - Small circular spots
            10. Downy mildew - White fungal growth

            Provide:
            - Disease name
            - Confidence level
            - Key symptoms that match
            - Differential diagnosis (why not other diseases)
            """,
            expected_output="Disease classification with confidence level and reasoning",
            agent=self.disease_classifier
        )

        # Task 3: Provide treatment recommendations
        task3 = Task(
            description="""
            Based on the disease classification, provide comprehensive treatment recommendations.

            Include:
            1. Immediate actions to contain the disease
            2. Chemical treatments (if appropriate)
            3. Cultural practices to prevent spread
            4. Prevention strategies for the future
            5. Monitoring recommendations

            Structure the response with numbered points for clarity.
            Use Thai language for the final recommendations.
            """,
            expected_output="Structured treatment recommendations in Thai with numbered points",
            agent=self.advisor_agent
        )

        # Create and run the crew
        crew = Crew(
            agents=[self.image_analyzer, self.disease_classifier, self.advisor_agent],
            tasks=[task1, task2, task3],
            verbose=True,
            planning=False
        )

        result = crew.kickoff()

        # Extract the final result
        if hasattr(result, 'final_output'):
            return str(result.final_output)
        elif hasattr(result, 'output'):
            return str(result.output)
        elif hasattr(result, 'raw'):
            return str(result.raw)
        else:
            return str(result)

def process_sugarcane_image(image_path: str, user_description: str = "") -> str:
    """
    Main function to process sugarcane disease classification

    Args:
        image_path: Path to the image file
        user_description: User's text description

    Returns:
        Classification result and recommendations
    """
    classifier = SugarcaneDiseaseClassifier()
    return classifier.classify_disease_from_image(image_path, user_description)

# Example usage
if __name__ == "__main__":
    # Test with a sample image (you would replace this with actual image data)
    # image_path = "path/to/sugarcane_image.jpg"
    # image_base64 = ImageProcessor.encode_image_from_path(image_path)
    # result = process_sugarcane_image(image_base64, "The leaves are turning yellow")
    # print(result)
    print("Sugarcane Disease Classifier initialized. Use process_sugarcane_image() function.")