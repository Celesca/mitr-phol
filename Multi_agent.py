from crewai import LLM, Agent, Task, Crew
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from rag_tool import RAGSearchTool

default_region = "us-east-1"
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION = default_region

# Use the bedrock_client created in the previous cell
llm = LLM(model="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
          aws_access_key_id=AWS_ACCESS_KEY,
          aws_secret_access_key=AWS_SECRET_KEY,
          aws_region_name=default_region
        )

rag_tool = RAGSearchTool()

# -----------------------------
# Agents (Thai roles/goals)
# -----------------------------
classifier = Agent(
    llm=llm,
    role="Domain Classifier",
    goal="Classify farmer questions into one or more sugarcane categories",
    backstory="You are an expert who understands the categorization of sugarcane cultivation knowledge",
    tools=[],
    verbose=True
)

retriever = Agent(
    llm=llm,
    role="Data Retriever",
    goal="Search for relevant text from the knowledge base using RAG tool",
    backstory="You have a search tool that combines dense retrieval, BM25, and re-ranking",
    tools=[rag_tool],
    verbose=True
)

advisor = Agent(
    llm=llm,
    role="Sugarcane Farmer Advisor",
    goal="Provide friendly, easy-to-understand advice for farmers",
    backstory="I am a kind advisor who loves helping farmers with easy-to-understand words, no special symbols",
    tools=[],
    verbose=True
)

# -----------------------------
# Orchestration function
# -----------------------------
def crew_infer(question_text: str) -> str:
    """
    Run the full CrewAI orchestration:
    1. Classify the query into categories (Agent 1).
    2. Retrieve relevant passages from ALL categories (Agent 2).
    3. Summarize into advice (Agent 3).
    Returns the final answer in Thai.
    """

    # Task 1: Explicit classification prompt
    classify_prompt = f"""
    Please classify the farmer's question into one or more of the following sugarcane categories.
    Return only the category names (you can return more than one category separated by commas).

    Categories:
    1. Care and maintenance (growth period)
    2. Soil preparation and sugarcane varieties
    3. Harvesting and post-harvest management
    4. Marketing and general information
    5. Diseases and pests

    Question: "{question_text}"
    """

    task1 = Task(
        description=classify_prompt,
        expected_output="One or more category names from the list above",
        agent=classifier
    )

    # Task 2: Retrieval with multi-label support
    task2 = Task(
        description=f"""
        Use the RAG tool to search for relevant text related to the question '{question_text}'
        Filter by the categories obtained from Task 1 (if there are multiple categories, search from all categories and combine the results)
        """,
        expected_output="Up to 5 relevant passages per category with metadata",
        agent=retriever
    )

    # Task 3: Summarization
    task3 = Task(
        description=f"""
        Summarize the retrieved information into easy-to-understand and practical advice for farmers
        Based on the question '{question_text}'
        
        Provide the answer as plain text, no special symbols, no headers, no bold text
        """,
        expected_output="Short description with practical steps (in Thai) as plain text without symbols",
        agent=advisor
    )

    crew = Crew(
        agents=[classifier, retriever, advisor],
        tasks=[task1, task2, task3],
        verbose=True,
        planning=False
    )

    result = crew.kickoff()
    # Extract the actual text result from CrewOutput

    # Handle different CrewAI result formats
    if hasattr(result, 'final_output'):
        return str(result.final_output)
    elif hasattr(result, 'output'):
        return str(result.output)
    elif hasattr(result, 'raw'):
        return str(result.raw)
    elif isinstance(result, (list, tuple)) and len(result) > 0:
        # If it's a list of task results, get the last one (final answer)
        final_result = result[-1]
        if hasattr(final_result, 'output'):
            return str(final_result.output)
        elif hasattr(final_result, 'raw'):
            return str(final_result.raw)
        else:
            return str(final_result)
    else:
        return str(result)

# Remove the test code - this will be called from line_bot.py
# query = "พันธุ์อ้อยที่ทนโรคใบด่าง"
# answer = crew_infer(query)
# print(answer)