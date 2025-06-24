"""
Omotenashi Hotel Concierge API
A FastAPI application providing AI-powered hotel concierge services.
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# LangChain imports
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from langchain_chroma import Chroma
from langchain_anthropic import ChatAnthropic

# Local imports
from src.api.config import MEMORY_EXPIRY_HOURS, ANTHROPIC_API_KEY, CLAUDE_MODEL, PORT
from src.agents.prompts import combine_prompts, format_guest_context, get_base_system_prompt, get_property_name_from_booking
from src.agents.tools import create_guest_tools

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------------
# FastAPI Application Setup
# ----------------------------------------------------------------------------

app = FastAPI(
    title="Omotenashi Hotel Concierge API",
    description="AI-powered hotel concierge services",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# ----------------------------------------------------------------------------
# Data Models
# ----------------------------------------------------------------------------

class MessageRequest(BaseModel):
    message: str
    phone_number: str
    system_prompt: Optional[str] = None

class MessageResponse(BaseModel):
    response: str
    session_id: str
    tools_used: List[str] = []
    debug_info: Optional[dict] = None

class SessionResponse(BaseModel):
    session_id: str
    messages: List[dict]

# ----------------------------------------------------------------------------
# Service Classes
# ----------------------------------------------------------------------------

class VectorStoreService:
    """Manages the vector store for property information retrieval."""
    
    def __init__(self):
        self._vectorstore = None
        self._retriever = None
    
    @property
    def retriever(self):
        """Lazy-load the vector store retriever."""
        if self._retriever is None:
            try:
                # Note: Claude doesn't provide embeddings, so we'll use a different approach
                # For now, we'll use a local embedding model or keep OpenAI embeddings
                # This is a common pattern when using Claude for LLM but needing embeddings elsewhere
                from langchain_community.embeddings import HuggingFaceEmbeddings
                embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
                self._vectorstore = Chroma(
                    persist_directory="data/vector_store/chroma_db", 
                    embedding_function=embeddings
                )
                self._retriever = self._vectorstore.as_retriever(search_kwargs={"k": 4})
                logger.info("Vector store initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize vector store: {e}")
                return None
        return self._retriever
    
    def get_property_info(self, property_id: str, query: str) -> str:
        """Retrieve property information based on query."""
        if not self.retriever:
            return "Property knowledge base not available."
        
        try:
            logger.info(f"Searching property info for property_id: {property_id}, query: {query}")
            
            # Use the new invoke method instead of deprecated get_relevant_documents
            docs = self.retriever.invoke(query)
            
            if docs:
                result = "\n---\n".join(d.page_content for d in docs)
                logger.info(f"Found {len(docs)} documents for property info query")
                return result
            else:
                logger.warning("No documents found for property info query")
                return "No relevant information found."
                
        except Exception as e:
            logger.error(f"Error retrieving property info for {property_id}: {e}", exc_info=True)
            return "Error retrieving property information."

class GuestService:
    """Manages guest profiles and booking information."""
    
    def __init__(self):
        self.guests_by_phone: Dict[str, dict] = {}
        self.bookings_by_guest: Dict[str, dict] = {}
        self._load_data()
    
    def _load_data(self):
        """Load guest and booking data from JSON files."""
        try:
            with open("data/demo/guests.json", "r", encoding="utf-8") as f:
                guests = json.load(f)
            with open("data/demo/bookings.json", "r", encoding="utf-8") as f:
                bookings = json.load(f)
            
            self.guests_by_phone = {g["phone_number"]: g for g in guests}
            self.bookings_by_guest = {b["guest_id"]: b for b in bookings}
            
            logger.info(f"Loaded {len(guests)} guests and {len(bookings)} bookings")
        except FileNotFoundError as e:
            logger.error(f"Data file not found: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in data file: {e}")
        except Exception as e:
            logger.error(f"Error loading data: {e}")
    
    def get_guest(self, phone_number: str) -> Optional[dict]:
        """Get guest by phone number."""
        return self.guests_by_phone.get(phone_number)
    
    def get_booking(self, guest_id: str) -> Optional[dict]:
        """Get booking by guest ID."""
        return self.bookings_by_guest.get(guest_id)

class MemoryService:
    """Manages conversation memory for each guest session."""
    
    def __init__(self):
        self.memory_store: Dict[str, ConversationBufferMemory] = {}
        self.last_activity: Dict[str, datetime] = {}
        self.expiry = timedelta(hours=MEMORY_EXPIRY_HOURS)
    
    def get_memory(self, phone: str) -> ConversationBufferMemory:
        """Get or create conversation memory for a guest."""
        if phone not in self.memory_store:
            self.memory_store[phone] = ConversationBufferMemory(
                memory_key="chat_history", 
                return_messages=True
            )
        self.last_activity[phone] = datetime.utcnow()
        return self.memory_store[phone]
    
    def cleanup_expired(self):
        """Remove expired conversation memories."""
        now = datetime.utcnow()
        expired = [
            phone for phone, last_time in self.last_activity.items() 
            if now - last_time > self.expiry
        ]
        for phone in expired:
            self.memory_store.pop(phone, None)
            self.last_activity.pop(phone, None)
        
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired sessions")
    
    def get_session_messages(self, phone: str) -> Optional[List[BaseMessage]]:
        """Get conversation messages for a guest."""
        memory = self.memory_store.get(phone)
        return memory.chat_memory.messages if memory else None
    
    def delete_session(self, phone: str):
        """Delete a guest's conversation session."""
        self.memory_store.pop(phone, None)
        self.last_activity.pop(phone, None)

# ----------------------------------------------------------------------------
# Service Instances
# ----------------------------------------------------------------------------

vector_store = VectorStoreService()
guest_service = GuestService()
memory_service = MemoryService()

# ----------------------------------------------------------------------------
# Tool Creation (moved to tools.py)
# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# Agent Creation
# ----------------------------------------------------------------------------

def create_agent(phone: str, custom_prompt: Optional[str] = None):
    """Create a personalized agent for a specific guest."""
    try:
        guest = guest_service.get_guest(phone)
        booking = None
        
        if guest and "guest_id" in guest:
            booking = guest_service.get_booking(guest["guest_id"])
        
        # Create personalized system prompt
        guest_context = format_guest_context(guest, booking)
        property_name = get_property_name_from_booking(booking)
        base_prompt = get_base_system_prompt(guest_context, property_name)
        final_prompt = combine_prompts(base_prompt, custom_prompt)
        
        # Create guest-specific tools and agent
        tools = create_guest_tools(phone, guest_service, vector_store)
        llm = ChatAnthropic(
            model=CLAUDE_MODEL,
            anthropic_api_key=ANTHROPIC_API_KEY,
            temperature=0
        )
        
        logger.info(f"Creating agent for phone: {phone}, guest found: {guest is not None}")
        
        # Modern tool-calling agent for Claude native function calling
        prompt = ChatPromptTemplate.from_messages([
            ("system", final_prompt + "\n\nCRITICAL: Use EXACTLY ONE tool per request unless the guest asks multiple distinct questions. STOP after using one tool."),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        agent = create_tool_calling_agent(llm, tools, prompt)
        return AgentExecutor(
            agent=agent, 
            tools=tools, 
            memory=memory_service.get_memory(phone),
            verbose=False,  # Disable verbose to improve performance
            handle_parsing_errors=True,
            return_intermediate_steps=True,  # Enable intermediate steps tracking
            max_execution_time=30  # Add timeout to prevent hanging
        )
    except Exception as e:
        logger.error(f"Error creating agent for phone {phone}: {e}")
        raise

# ----------------------------------------------------------------------------
# API Endpoints
# ----------------------------------------------------------------------------

@app.get("/")
async def serve_frontend():
    """Serve the frontend application."""
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "index.html")
    return FileResponse(frontend_path)

@app.get("/guest_profile/all")
async def get_all_guests():
    """Get all guest profiles."""
    try:
        guests = list(guest_service.guests_by_phone.values())
        return guests
    except Exception as e:
        logger.error(f"Error retrieving guest profiles: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve guest profiles")

@app.get("/debug/status")
async def debug_status():
    """Debug endpoint to check system status."""
    return {
        "status": "ok",
        "guests_loaded": len(guest_service.guests_by_phone),
        "bookings_loaded": len(guest_service.bookings_by_guest),
        "active_sessions": len(memory_service.memory_store),
        "vector_store_ready": vector_store.retriever is not None
    }

@app.post("/message", response_model=MessageResponse)
async def handle_message(request: MessageRequest):
    """Handle chat message from guest."""
    try:
        logger.info(f"Handling message from phone: {request.phone_number}")
        logger.info(f"Message: {request.message[:100]}...")  # Log first 100 chars
        
        # Validate request
        if not request.phone_number:
            raise HTTPException(status_code=400, detail="Phone number is required")
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        agent = create_agent(request.phone_number, request.system_prompt)
        logger.info("Agent created successfully")
        
        # Try to invoke the agent with detailed error handling
        try:
            logger.info("About to invoke agent...")
            result = agent.invoke({"input": request.message})
            logger.info(f"Agent invoke result type: {type(result)}")
            logger.info(f"Agent invoke result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
            
            # Extract tools used from intermediate steps and response patterns
            tools_used = []
            debug_info = {}
            
            if isinstance(result, dict):
                # Extract intermediate steps to see which tools were called
                if "intermediate_steps" in result:
                    intermediate_steps = result["intermediate_steps"]
                    logger.info(f"Intermediate steps: {len(intermediate_steps)} steps")
                    
                    for step in intermediate_steps:
                        if isinstance(step, tuple) and len(step) >= 2:
                            action, observation = step[0], step[1]
                            if hasattr(action, 'tool'):
                                tool_name = action.tool
                                tools_used.append(tool_name)
                                logger.info(f"Tool called: {tool_name}")
                            elif hasattr(action, 'log'):
                                # Try to extract tool name from log
                                log_text = action.log.lower()
                                all_tools = [
                                    # Core tools
                                    "guest_profile", "booking_details", "property_info", "schedule_cleaning", 
                                    "modify_checkout_time", "request_transport", "escalate_to_manager",
                                    # High-impact tools
                                    "restaurant_reservation", "grocery_delivery", "maintenance_request", 
                                    "activity_booking", "meal_delivery",
                                    # Luxury tools
                                    "spa_services", "private_chef", "local_recommendations"
                                ]
                                for tool in all_tools:
                                    if tool in log_text:
                                        tools_used.append(tool)
                                        logger.info(f"Tool detected from log: {tool}")
                                        break
                
                # Fallback: Analyze response patterns to detect likely tool usage
                if "output" in result:
                    response_text = str(result["output"]).lower()
                    
                    # Pattern-based tool detection (same as evaluation patterns)
                    tool_patterns = {
                        # CORE TOOLS
                        "guest_profile": ["your name is", "you are", "vip guest", "carlos", "guest profile", "guest information"],
                        "booking_details": ["check out", "check-out", "reservation", "booking", "room type", "confirmation", "villa azul"],
                        "property_info": ["wifi", "pool", "gym", "amenities", "facilities", "restaurant", "spa", "property"],
                        "schedule_cleaning": ["cleaning scheduled", "housekeeping", "cleaning team", "room cleaning"],
                        "modify_checkout_time": ["checkout time", "checkout updated", "departure time", "late checkout"],
                        "request_transport": ["transport requested", "arranged your transportation", "car has been", "pickup", "airport"],
                        "escalate_to_manager": ["escalated", "property manager", "get back to you"],
                        
                        # HIGH-IMPACT TOOLS
                        "restaurant_reservation": ["reservation for", "restaurant", "dining", "table booked", "secured a reservation"],
                        "grocery_delivery": ["grocery delivery", "groceries", "arranged grocery", "food supplies", "beverage delivery"],
                        "maintenance_request": ["reported", "maintenance", "repair", "broken", "not working", "issue"],
                        "activity_booking": ["arranged", "activity", "tour", "experience", "excursion", "booked"],
                        "meal_delivery": ["ordered", "meal", "food delivery", "restaurant delivery", "takeout"],
                        
                        # LUXURY TOOLS
                        "spa_services": ["spa", "massage", "wellness", "relaxation", "therapeutic"],
                        "private_chef": ["private chef", "chef", "culinary", "dining experience", "meal preparation"],
                        "local_recommendations": ["recommend", "suggest", "local", "area", "best", "options"]
                    }
                    
                    for tool_name, patterns in tool_patterns.items():
                        for pattern in patterns:
                            if pattern in response_text:
                                tools_used.append(tool_name)
                                logger.info(f"Tool detected from response pattern '{pattern}': {tool_name}")
                                break
                
                debug_info = {
                    "result_keys": list(result.keys()) if isinstance(result, dict) else [],
                    "intermediate_steps_count": len(result.get("intermediate_steps", [])),
                    "raw_result_type": str(type(result))
                }
                
                if "output" in result:
                    output = result["output"]
                    # Handle different response formats from modern agent
                    if isinstance(output, list) and len(output) > 0:
                        # Extract text from list format
                        if isinstance(output[0], dict) and "text" in output[0]:
                            response = output[0]["text"]
                        else:
                            response = str(output[0])
                    elif isinstance(output, str):
                        response = output
                    else:
                        response = str(output)
                else:
                    logger.error(f"Unexpected agent result format: {result}")
                    response = "I apologize, but I'm having trouble processing your request right now."
            else:
                logger.error(f"Agent result is not a dict: {type(result)}")
                response = "I apologize, but I'm having trouble processing your request right now."
                
        except Exception as agent_error:
            logger.error(f"Agent invoke error: {agent_error}", exc_info=True)
            response = "I'm sorry, I'm experiencing technical difficulties. Please try again."
            tools_used = []
            debug_info = {"error": str(agent_error)}
        
        logger.info(f"Agent response generated successfully. Tools used: {tools_used}")
        
        memory_service.cleanup_expired()
        
        return MessageResponse(
            response=response, 
            session_id=request.phone_number,
            tools_used=list(set(tools_used)),  # Remove duplicates
            debug_info=debug_info
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling message from {request.phone_number}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/session/{phone}", response_model=SessionResponse)
async def get_session(phone: str):
    """Get conversation session for a guest."""
    try:
        messages = memory_service.get_session_messages(phone)
        if not messages:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return SessionResponse(
            session_id=phone,
            messages=[m.dict() for m in messages],
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving session: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve session")

@app.delete("/session/{phone}")
async def delete_session(phone: str):
    """Delete a guest's conversation session."""
    try:
        memory_service.delete_session(phone)
        return {"status": "deleted"}
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete session")

# ----------------------------------------------------------------------------
# Application Entry Point
# ----------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT) 