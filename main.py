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
from langchain.agents import AgentType, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage, SystemMessage
from langchain.tools import Tool, StructuredTool
from pydantic import BaseModel, Field
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Local imports
from config import MEMORY_EXPIRY_HOURS, OPENAI_API_KEY, OPENAI_MODEL, PORT
from prompts import TOOL_DESCRIPTIONS, combine_prompts, format_guest_context, get_base_system_prompt

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
static_dir = os.path.join(os.path.dirname(__file__), "static")
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
                embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
                self._vectorstore = Chroma(
                    persist_directory="chroma_db", 
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
            with open("guests.json", "r", encoding="utf-8") as f:
                guests = json.load(f)
            with open("bookings.json", "r", encoding="utf-8") as f:
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
# Tool Creation
# ----------------------------------------------------------------------------

def create_guest_tools(phone_number: str) -> List[Tool]:
    """Create tools pre-configured for a specific guest."""
    
    def schedule_cleaning(cleaning_time: str) -> str:
        """Schedule room cleaning."""
        guest = guest_service.get_guest(phone_number)
        if not guest:
            return "Guest not found."
        
        booking = guest_service.get_booking(guest["guest_id"])
        if not booking:
            return "Booking not found."
        
        return (f"Cleaning scheduled for room {booking['property_id']} "
                f"at {cleaning_time} for {guest['name']} (ID: {guest['guest_id']}).")
    
    def modify_checkout_time(new_checkout_time: str) -> str:
        """Modify guest's checkout time."""
        guest = guest_service.get_guest(phone_number)
        if not guest:
            return "Guest not found."
        
        return (f"Checkout time for {guest['name']} (ID: {guest['guest_id']}) "
                f"updated to {new_checkout_time}.")
    
    def request_transport(pickup_time: str, airport_code: str) -> str:
        """Request airport transport."""
        guest = guest_service.get_guest(phone_number)
        if not guest:
            return "Guest not found."
        
        return (f"Transport requested for {guest['name']} (ID: {guest['guest_id']}) "
                f"to {airport_code} at {pickup_time}.")
    
    def get_guest_profile() -> str:
        """Get guest profile information."""
        guest = guest_service.get_guest(phone_number)
        return json.dumps(guest, indent=2) if guest else "Guest not found."
    
    def get_booking_details() -> str:
        """Get guest booking details."""
        guest = guest_service.get_guest(phone_number)
        if not guest:
            return "Guest not found."
        
        booking = guest_service.get_booking(guest["guest_id"])
        return json.dumps(booking, indent=2) if booking else "Booking not found."
    
    def get_property_info(query: str = "general information") -> str:
        """Get property information."""
        try:
            guest = guest_service.get_guest(phone_number)
            if not guest:
                return "Guest not found."
            
            booking = guest_service.get_booking(guest["guest_id"])
            if not booking:
                return "Booking not found."
            
            logger.info(f"Getting property info for guest {guest.get('name', 'Unknown')} - property: {booking.get('property_id', 'Unknown')}")
            return vector_store.get_property_info(booking["property_id"], query)
        except Exception as e:
            logger.error(f"Error in get_property_info tool: {e}", exc_info=True)
            return "Sorry, I'm having trouble accessing property information right now."
    
    # Input schemas for structured tools
    class CleaningInput(BaseModel):
        cleaning_time: str = Field(description="When to schedule the cleaning")
    
    class CheckoutInput(BaseModel):
        new_checkout_time: str = Field(description="New checkout time")
    
    class TransportInput(BaseModel):
        pickup_time: str = Field(description="Pickup time")
        airport_code: str = Field(description="Airport code")
    
    class PropertyInfoInput(BaseModel):
        query: str = Field(default="general information", description="What to search for")
    
    return [
        StructuredTool.from_function(
            func=schedule_cleaning,
            args_schema=CleaningInput,
            name="schedule_cleaning",
            description=TOOL_DESCRIPTIONS["schedule_cleaning"]
        ),
        StructuredTool.from_function(
            func=modify_checkout_time,
            args_schema=CheckoutInput,
            name="modify_checkout_time",
            description=TOOL_DESCRIPTIONS["modify_checkout_time"]
        ),
        StructuredTool.from_function(
            func=request_transport,
            args_schema=TransportInput,
            name="request_transport",
            description=TOOL_DESCRIPTIONS["request_transport"]
        ),
        StructuredTool.from_function(
            func=get_guest_profile,
            name="guest_profile",
            description=TOOL_DESCRIPTIONS["guest_profile"]
        ),
        StructuredTool.from_function(
            func=get_booking_details,
            name="booking_details",
            description=TOOL_DESCRIPTIONS["booking_details"]
        ),
        StructuredTool.from_function(
            func=get_property_info,
            args_schema=PropertyInfoInput,
            name="property_info",
            description=TOOL_DESCRIPTIONS["property_info"]
        ),
    ]

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
        base_prompt = get_base_system_prompt(guest_context)
        final_prompt = combine_prompts(base_prompt, custom_prompt)
        
        # Create guest-specific tools and agent
        tools = create_guest_tools(phone)
        llm = ChatOpenAI(model_name=OPENAI_MODEL, temperature=0, openai_api_key=OPENAI_API_KEY)
        
        logger.info(f"Creating agent for phone: {phone}, guest found: {guest is not None}")
        
        return initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.OPENAI_FUNCTIONS,
            memory=memory_service.get_memory(phone),
            system_message=SystemMessage(content=final_prompt),
            verbose=False,
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
    return FileResponse(os.path.join(static_dir, "index.html"))

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
            
            if isinstance(result, dict) and "output" in result:
                response = result["output"]
            else:
                logger.error(f"Unexpected agent result format: {result}")
                response = "I apologize, but I'm having trouble processing your request right now."
                
        except Exception as agent_error:
            logger.error(f"Agent invoke error: {agent_error}", exc_info=True)
            response = "I'm sorry, I'm experiencing technical difficulties. Please try again."
        
        logger.info("Agent response generated successfully")
        
        memory_service.cleanup_expired()
        
        return MessageResponse(response=response, session_id=request.phone_number)
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