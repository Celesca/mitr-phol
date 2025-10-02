from crewai import LLM, Agent, Task, Crew
import os
from dotenv import load_dotenv
from functools import lru_cache
import time

# Load environment variables from .env file
load_dotenv()

from rag_tool import RAGSearchTool

# Simple in-memory cache for recent queries (max 100 entries)
query_cache = {}
CACHE_MAX_SIZE = 100
CACHE_TTL = 3600  # 1 hour TTL

default_region = "us-east-1"
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION = default_region

# Use the bedrock_client created in the previous cell
llm = LLM(model="us.anthropic.claude-3-5-haiku-20241022-v1:0",
          aws_access_key_id=AWS_ACCESS_KEY,
          aws_secret_access_key=AWS_SECRET_KEY,
          aws_region_name=default_region
        )

rag_tool = RAGSearchTool()

# -----------------------------
# Agents (Thai roles/goals) - Optimized for speed
# -----------------------------
classifier = Agent(
    llm=llm,
    role="Domain Classifier",
    goal="Classify farmer questions into one or more sugarcane categories",
    backstory="You are an expert who understands the categorization of sugarcane cultivation knowledge",
    tools=[],
    verbose=False,  # Reduced verbosity for speed
    max_iter=3,     # Limit iterations
    allow_delegation=False  # Direct execution
)

retriever = Agent(
    llm=llm,
    role="Data Retriever",
    goal="Search for relevant text from the knowledge base using RAG tool",
    backstory="You have a search tool that combines dense retrieval, BM25, and re-ranking",
    tools=[rag_tool],
    verbose=True,  # Reduced verbosity for speed
    allow_delegation=False  # Direct execution
)

advisor = Agent(
    llm=llm,
    role="Sugarcane Farmer Advisor",
    goal="Provide friendly, easy-to-understand advice for farmers",
    backstory="I am a kind advisor who loves helping farmers with easy-to-understand words, no special symbols",
    tools=[],
    verbose=False,  # Reduced verbosity for speed
    max_iter=3,     # Limit iterations
    allow_delegation=False  # Direct execution
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
    
    Includes caching for performance optimization.
    """
    
    # Check cache first
    cache_key = question_text.strip().lower()
    current_time = time.time()
    
    if cache_key in query_cache:
        cached_result, timestamp = query_cache[cache_key]
        if current_time - timestamp < CACHE_TTL:
            print(f"Cache hit for: {question_text[:50]}...")
            return cached_result
    
    # Clean up old cache entries if cache is too large
    if len(query_cache) >= CACHE_MAX_SIZE:
        # Remove oldest entries
        sorted_cache = sorted(query_cache.items(), key=lambda x: x[1][1])
        # Keep only the most recent 50 entries
        query_cache.clear()
        for key, value in sorted_cache[-50:]:
            query_cache[key] = value

    # Task 1: Explicit classification prompt - Simplified
    classify_prompt = f"""
    Classify this sugarcane farming question into 1-2 categories from:
    1. Care and maintenance (growth period)
    2. Soil preparation and sugarcane varieties  
    3. Harvesting and post-harvest management
    4. Marketing and general information
    5. Diseases and pests

    Question: {question_text}
    Return only category names separated by commas.
    """

    task1 = Task(
        description=classify_prompt,
        expected_output="Category names only, comma-separated",
        agent=classifier
    )

    # Task 2: Retrieval with multi-label support - Optimized
    task2 = Task(
        description=f"""
        Search for relevant sugarcane farming information about: {question_text}
        
        Use the RAG tool to find specific information that directly answers this question.
        If no relevant information exists, return exactly: "NO_RELEVANT_INFO_FOUND"
        """,
        expected_output="Relevant passages or 'NO_RELEVANT_INFO_FOUND'",
        agent=retriever
    )

    # Task 3: Summarization - Optimized
    task3 = Task(
        description=f"""
        Provide practical sugarcane farming advice for: {question_text}
        
        If information shows "NO_RELEVANT_INFO_FOUND", return exactly: "EXPERT_CONSULTATION_REQUIRED"
        
        Otherwise, give clear, practical advice in Thai. Keep it concise and actionable.
        """,
        expected_output="Thai advice or 'EXPERT_CONSULTATION_REQUIRED'",
        agent=advisor
    )

    crew = Crew(
        agents=[classifier, retriever, advisor],
        tasks=[task1, task2, task3],
        verbose=False,  # Reduced verbosity for production speed
        planning=False,
        memory=False,   # Disable memory for faster execution
        cache=False     # Disable caching to avoid overhead
    )

    result = crew.kickoff()

    # Check if RAG search found no relevant documents
    # Extract the retriever result from task2
    if hasattr(result, 'tasks_output') and len(result.tasks_output) >= 2:
        retriever_output = str(result.tasks_output[1].raw)
        if ("No relevant documents found" in retriever_output or 
            retriever_output.strip() == "" or 
            "NO_RELEVANT_INFO_FOUND" in retriever_output):
            return "โปรดถามเจ้าหน้าที่ที่ชำนาญ\n/ปรึกษาผู้เชี่ยวชาญ"

    # Extract the actual text result from CrewOutput

    # Handle different CrewAI result formats
    final_output = ""
    if hasattr(result, 'final_output'):
        final_output = str(result.final_output)
    elif hasattr(result, 'output'):
        final_output = str(result.output)
    elif hasattr(result, 'raw'):
        final_output = str(result.raw)
    elif isinstance(result, (list, tuple)) and len(result) > 0:
        # If it's a list of task results, get the last one (final answer)
        final_result = result[-1]
        if hasattr(final_result, 'output'):
            final_output = str(final_result.output)
        elif hasattr(final_result, 'raw'):
            final_output = str(final_result.raw)
        else:
            final_output = str(final_result)
    else:
        final_output = str(result)

    # Check if advisor determined expert consultation is required
    if "EXPERT_CONSULTATION_REQUIRED" in final_output:
        result = "โปรดถามเจ้าหน้าที่ที่ชำนาญ\n/ปรึกษาผู้เชี่ยวชาญ"
    else:
        result = final_output
    
    # Cache the result
    query_cache[cache_key] = (result, current_time)
    
    return result

def crew_infer_with_timing(question_text: str) -> tuple[str, float]:
    """
    Run crew_infer with timing for performance monitoring.
    Returns (response, processing_time_seconds)
    """
    start_time = time.time()
    response = crew_infer(question_text)
    end_time = time.time()
    processing_time = end_time - start_time
    return response, processing_time