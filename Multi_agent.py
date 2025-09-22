"""
Mitr Phol Sugar ChatBot System - CrewAI Implementation
A sophisticated multi-agent system for Thai sugar industry customer service and knowledge management
"""

import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from pydantic import BaseModel, Field


# ==================== CUSTOM TOOLS ====================

class KnowledgeGraphTool(BaseTool):
    """Knowledge Graph retrieval tool for Mitr Phol domain knowledge"""
    
    name: str = "knowledge_graph_retrieval"
    description: str = "Retrieves structured knowledge from Mitr Phol's knowledge graph including sugar production, sustainability, supply chain, and customer service information"
    
    def __init__(self):
        super().__init__()
        # Initialize knowledge graph connections
        self.kg_entities = {
            "sugar_production": {
                "processes": ["milling", "refining", "packaging", "quality_control"],
                "products": ["raw_sugar", "refined_sugar", "molasses", "bagasse"],
                "facilities": ["factories", "warehouses", "distribution_centers"]
            },
            "sustainability": {
                "initiatives": ["renewable_energy", "water_conservation", "waste_reduction"],
                "certifications": ["bonsucro", "iso14001", "fair_trade"],
                "environmental_impact": ["carbon_footprint", "biodiversity", "soil_health"]
            },
            "customer_service": {
                "inquiries": ["product_info", "pricing", "delivery", "complaints"],
                "channels": ["phone", "email", "website", "mobile_app"],
                "resolution_process": ["ticket_creation", "assignment", "resolution", "follow_up"]
            }
        }
    
    def _run(self, query: str) -> str:
        """Retrieve knowledge graph information based on query"""
        query_lower = query.lower()
        relevant_info = []
        
        # Simple keyword matching for demo - in production, use proper graph queries
        for domain, entities in self.kg_entities.items():
            if any(keyword in query_lower for keyword in domain.split('_')):
                relevant_info.append(f"{domain.title()}: {json.dumps(entities, indent=2)}")
        
        if not relevant_info:
            return "No specific domain knowledge found. Available domains: sugar production, sustainability, customer service."
        
        return "\n\n".join(relevant_info)


class ThaiLocalizationTool(BaseTool):
    """Thai language localization and cultural context tool"""
    
    name: str = "thai_localization"
    description: str = "Provides Thai language support and cultural context for responses"
    
    def __init__(self):
        super().__init__()
        self.thai_translations = {
            "sugar": "น้ำตาล",
            "production": "การผลิต",
            "quality": "คุณภาพ",
            "customer_service": "บริการลูกค้า",
            "sustainability": "ความยั่งยืน",
            "delivery": "การจัดส่ง",
            "price": "ราคา",
            "complaint": "ข้อร้องเรียน"
        }
        
        self.cultural_context = {
            "business_hours": "เวลาทำการ: จันทร์-ศุกร์ 8:00-17:00 น.",
            "politeness": "ใช้คำสุภาพในการตอบ เช่น 'ครับ/ค่ะ'",
            "hierarchy": "แสดงความเคารพต่อลูกค้า",
            "communication_style": "อธิบายอย่างละเอียดและเป็นมิตร"
        }
    
    def _run(self, text: str, target_language: str = "thai") -> str:
        """Localize text for Thai context"""
        if target_language.lower() == "thai":
            # Simple translation mapping - in production, use proper translation service
            for eng, thai in self.thai_translations.items():
                text = text.replace(eng, f"{eng} ({thai})")
            
            # Add cultural context
            cultural_note = "การบริการแบบไทย: " + self.cultural_context["communication_style"]
            return f"{text}\n\n{cultural_note}"
        
        return text


class RAGRetrievalTool(BaseTool):
    """Advanced RAG tool with knowledge graph integration"""
    
    name: str = "rag_retrieval"
    description: str = "Retrieves relevant documents using RAG with knowledge graph enhancement"
    
    def __init__(self):
        super().__init__()
        # Initialize RAG components
        self.embeddings = OpenAIEmbeddings()  # Replace with actual embeddings
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        # Sample documents for Mitr Phol
        self.sample_docs = [
            Document(page_content="Mitr Phol is Thailand's largest sugar producer with over 40 years of experience in sustainable sugar production.", metadata={"type": "company_info"}),
            Document(page_content="Our sugar refining process ensures the highest quality products meeting international standards including Bonsucro certification.", metadata={"type": "production"}),
            Document(page_content="Customer service is available 24/7 through multiple channels including phone, email, and mobile application.", metadata={"type": "customer_service"}),
        ]
        
        # In production, initialize with actual vector store
        # self.vectorstore = Chroma.from_documents(documents, embeddings)
    
    def _run(self, query: str, top_k: int = 3) -> str:
        """Retrieve relevant documents using RAG"""
        # Simplified retrieval for demo
        relevant_docs = []
        query_lower = query.lower()
        
        for doc in self.sample_docs:
            if any(term in doc.page_content.lower() for term in query_lower.split()):
                relevant_docs.append(doc.page_content)
        
        if not relevant_docs:
            return "No relevant documents found in the knowledge base."
        
        return "\n\n".join(relevant_docs[:top_k])


class PolicyReasoningTool(BaseTool):
    """Policy-based reasoning tool for decision making"""
    
    name: str = "policy_reasoning"
    description: str = "Applies business policies and reasoning to provide appropriate responses and actions"
    
    def __init__(self):
        super().__init__()
        self.policies = {
            "customer_complaints": {
                "priority": "high",
                "escalation_time": "2 hours",
                "resolution_target": "24 hours",
                "compensation_guidelines": "case_by_case_basis"
            },
            "product_inquiries": {
                "response_time": "immediate",
                "information_level": "detailed",
                "follow_up_required": "yes"
            },
            "pricing_requests": {
                "authorization_level": "sales_team",
                "discount_limits": "manager_approval_required",
                "bulk_pricing": "special_rates_available"
            }
        }
    
    def _run(self, situation: str, query_type: str) -> str:
        """Apply policy reasoning to determine appropriate action"""
        query_type_lower = query_type.lower()
        
        for policy_name, policy_rules in self.policies.items():
            if any(keyword in query_type_lower for keyword in policy_name.split('_')):
                reasoning = f"Policy Applied: {policy_name.title()}\n"
                for rule, value in policy_rules.items():
                    reasoning += f"- {rule.replace('_', ' ').title()}: {value}\n"
                
                # Add specific recommendations
                if "complaint" in query_type_lower:
                    reasoning += "\nRecommended Actions:\n1. Acknowledge complaint immediately\n2. Escalate to supervisor if needed\n3. Follow up within 24 hours"
                elif "pricing" in query_type_lower:
                    reasoning += "\nRecommended Actions:\n1. Check current pricing tiers\n2. Verify customer eligibility\n3. Obtain necessary approvals"
                
                return reasoning
        
        return f"No specific policy found for: {query_type}. Applying general customer service guidelines."


# ==================== AGENTS DEFINITION ====================

def create_router_agent() -> Agent:
    """Router/Orchestrator Agent"""
    return Agent(
        role="Router and Orchestrator",
        goal="Intelligently route customer inquiries to appropriate specialized agents and orchestrate the overall conversation flow",
        backstory="""You are the central coordinator for Mitr Phol's customer service system. 
        With deep understanding of sugar industry operations and Thai business culture, you ensure 
        each customer interaction is handled by the most appropriate specialist while maintaining 
        consistent service quality and cultural sensitivity.""",
        verbose=True,
        allow_delegation=True,
        tools=[],
        max_iter=3
    )


def create_knowledge_agent() -> Agent:
    """Knowledge Agent with RAG capabilities"""
    return Agent(
        role="Knowledge Specialist",
        goal="Provide accurate, comprehensive, and culturally appropriate information about Mitr Phol's products, services, and operations",
        backstory="""You are Mitr Phol's knowledge expert with comprehensive understanding of 
        sugar production, sustainability practices, product specifications, and company policies. 
        You combine advanced RAG retrieval with knowledge graphs to provide precise, contextual 
        information while ensuring proper Thai localization and cultural sensitivity.""",
        verbose=True,
        tools=[
            KnowledgeGraphTool(),
            ThaiLocalizationTool(),
            RAGRetrievalTool()
        ],
        max_iter=5
    )


def create_planner_agent() -> Agent:
    """Planner Agent with reasoning capabilities"""
    return Agent(
        role="Strategic Planner and Decision Maker",
        goal="Analyze customer needs, apply business policies, and create optimal action plans for customer service resolutions",
        backstory="""You are Mitr Phol's strategic planning specialist who combines policy 
        knowledge, business reasoning, and customer psychology to create optimal solutions. 
        You excel at transforming information into actionable plans that satisfy both customer 
        needs and business objectives while respecting Thai cultural values.""",
        verbose=True,
        tools=[PolicyReasoningTool()],
        max_iter=4
    )


# ==================== TASKS DEFINITION ====================

def create_routing_task(customer_query: str) -> Task:
    """Create routing task"""
    return Task(
        description=f"""
        Analyze the following customer query and determine the optimal handling approach:
        
        Customer Query: "{customer_query}"
        
        Your responsibilities:
        1. Classify the query type (product inquiry, complaint, pricing, technical support, etc.)
        2. Identify the primary language and cultural context needed
        3. Determine urgency level and appropriate response timeline
        4. Route to appropriate specialist agents
        5. Set expectations for the customer interaction
        
        Consider Mitr Phol's context: sugar industry, Thai market, sustainability focus, premium quality positioning.
        """,
        agent=create_router_agent(),
        expected_output="Structured routing decision with query classification, urgency level, and specialist assignment"
    )


def create_knowledge_retrieval_task(customer_query: str, routing_info: str) -> Task:
    """Create knowledge retrieval task"""
    return Task(
        description=f"""
        Based on the routing decision, retrieve comprehensive information to address the customer query:
        
        Original Query: "{customer_query}"
        Routing Information: {routing_info}
        
        Your responsibilities:
        1. Use knowledge graph retrieval to find relevant domain information
        2. Apply RAG techniques to get specific documentation and policies
        3. Ensure Thai localization where appropriate
        4. Provide cultural context for Thai customers
        5. Compile comprehensive, accurate information
        
        Focus areas:
        - Product specifications and quality standards
        - Company policies and procedures  
        - Sustainability initiatives and certifications
        - Cultural and linguistic appropriateness
        """,
        agent=create_knowledge_agent(),
        expected_output="Comprehensive, localized information package addressing the customer query"
    )


def create_planning_task(customer_query: str, knowledge_info: str) -> Task:
    """Create strategic planning task"""
    return Task(
        description=f"""
        Create an optimal action plan based on the customer query and retrieved knowledge:
        
        Original Query: "{customer_query}"
        Knowledge Base Information: {knowledge_info}
        
        Your responsibilities:
        1. Apply policy reasoning to determine appropriate business response
        2. Create step-by-step action plan for customer service
        3. Consider escalation paths and approval requirements
        4. Ensure compliance with Thai business practices
        5. Optimize for customer satisfaction and business objectives
        
        Consider:
        - Business policies and approval workflows
        - Customer relationship management
        - Cultural sensitivity in Thai context
        - Long-term business implications
        - Quality assurance and follow-up requirements
        """,
        agent=create_planner_agent(),
        expected_output="Detailed action plan with specific steps, timelines, and success metrics"
    )


# ==================== MAIN CREW SYSTEM ====================

class MitrPholChatBot:
    """Main ChatBot System for Mitr Phol Sugar"""
    
    def __init__(self):
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        self.session_context = {}
        
    def process_customer_query(self, query: str, customer_context: Dict = None) -> Dict[str, Any]:
        """Process customer query through the multi-agent system"""
        
        # Update session context
        if customer_context:
            self.session_context.update(customer_context)
        
        # Create tasks
        routing_task = create_routing_task(query)
        
        # Initial routing crew
        routing_crew = Crew(
            agents=[create_router_agent()],
            tasks=[routing_task],
            verbose=True,
            process=Process.sequential
        )
        
        # Execute routing
        routing_result = routing_crew.kickoff()
        
        # Create knowledge retrieval task
        knowledge_task = create_knowledge_retrieval_task(query, str(routing_result))
        
        # Knowledge crew
        knowledge_crew = Crew(
            agents=[create_knowledge_agent()],
            tasks=[knowledge_task],
            verbose=True,
            process=Process.sequential
        )
        
        # Execute knowledge retrieval
        knowledge_result = knowledge_crew.kickoff()
        
        # Create planning task
        planning_task = create_planning_task(query, str(knowledge_result))
        
        # Planning crew
        planning_crew = Crew(
            agents=[create_planner_agent()],
            tasks=[planning_task],
            verbose=True,
            process=Process.sequential
        )
        
        # Execute planning
        planning_result = planning_crew.kickoff()
        
        # Compile final response
        response = {
            "timestamp": datetime.now().isoformat(),
            "customer_query": query,
            "routing_decision": str(routing_result),
            "knowledge_base": str(knowledge_result),
            "action_plan": str(planning_result),
            "session_id": self.session_context.get("session_id", "default"),
            "language": self.session_context.get("language", "thai-english"),
            "customer_type": self.session_context.get("customer_type", "general")
        }
        
        # Store in memory
        self.memory.save_context(
            {"input": query},
            {"output": str(planning_result)}
        )
        
        return response


# ==================== USAGE EXAMPLE ====================

def demo_mitr_phol_chatbot():
    """Demonstrate the Mitr Phol ChatBot system"""
    
    # Initialize chatbot
    chatbot = MitrPholChatBot()
    
    # Example customer queries
    test_queries = [
        "I want to know about your sugar quality certifications and sustainability practices",
        "มีน้ำตาลชนิดไหนบ้างสำหรับร้านขนมครับ", # "What types of sugar do you have for bakeries?"
        "I received damaged products in my last shipment and need immediate resolution",
        "Can you provide bulk pricing for 100 tons of refined sugar for industrial use?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*50}")
        print(f"DEMO QUERY {i}: {query}")
        print('='*50)
        
        # Customer context
        customer_context = {
            "session_id": f"demo_session_{i}",
            "customer_type": "business" if i > 2 else "general",
            "language": "thai" if "มี" in query else "english",
            "timestamp": datetime.now().isoformat()
        }
        
        # Process query
        try:
            result = chatbot.process_customer_query(query, customer_context)
            
            print("\n--- ROUTING DECISION ---")
            print(result["routing_decision"])
            
            print("\n--- KNOWLEDGE RETRIEVED ---")
            print(result["knowledge_base"])
            
            print("\n--- ACTION PLAN ---")
            print(result["action_plan"])
            
        except Exception as e:
            print(f"Error processing query: {e}")


if __name__ == "__main__":
    print("Mitr Phol Sugar ChatBot System - CrewAI Implementation")
    print("=" * 60)
    
    # Set up environment (in production, use proper API keys)
    os.environ.setdefault("OPENAI_API_KEY", "your-openai-api-key")
    
    # Run demo
    demo_mitr_phol_chatbot()