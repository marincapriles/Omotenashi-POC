from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from config import OPENAI_API_KEY
from typing import Dict, Optional
from datetime import datetime, timedelta
import json

# LangChain imports
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.schema import SystemMessage

import os

# ----------------------------------------------------------------------------
# FastAPI initialisation
# ----------------------------------------------------------------------------
app = FastAPI(title="Omotenashi API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific origins in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------------------------------
# Vector-store setup (hotel knowledge base)
# ----------------------------------------------------------------------------
try:
    _embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    vectorstore = Chroma(persist_directory="chroma_db", embedding_function=_embeddings)
    property_retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
except Exception:
    vectorstore = None
    property_retriever = None

# ----------------------------------------------------------------------------
# Memory + housekeeping per guest (phone number => memory)
# ----------------------------------------------------------------------------
memory_store: Dict[str, ConversationBufferMemory] = {}
last_activity: Dict[str, datetime] = {}

MEMORY_EXPIRY = timedelta(hours=1)


def get_memory(phone: str) -> ConversationBufferMemory:
    if phone not in memory_store:
        memory_store[phone] = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )
    last_activity[phone] = datetime.utcnow()
    return memory_store[phone]


def cleanup_expired_sessions():
    now = datetime.utcnow()
    expired = [p for p, t in last_activity.items() if now - t > MEMORY_EXPIRY]
    for p in expired:
        memory_store.pop(p, None)
        last_activity.pop(p, None)

# ----------------------------------------------------------------------------
# Data loading (sample guests & bookings)
# ----------------------------------------------------------------------------
with open("guests.json", "r", encoding="utf-8") as f:
    _guests = json.load(f)
with open("bookings.json", "r", encoding="utf-8") as f:
    _bookings = json.load(f)

guests_by_phone = {g["phone_number"]: g for g in _guests}
bookings_by_guest = {b["guest_id"]: b for b in _bookings}

# ----------------------------------------------------------------------------
# Tool implementations (extend existing stubs)
# ----------------------------------------------------------------------------

def schedule_cleaning(guest_id: str, property_id: str, cleaning_time: str) -> str:
    """Schedule a room cleaning (stub)."""
    return (
        f"Cleaning scheduled for room {property_id} at {cleaning_time} (guest {guest_id})."
    )


def modify_checkout_time(guest_id: str, new_checkout_time: str) -> str:
    """Modify checkout time (stub)."""
    return f"Checkout time for guest {guest_id} updated to {new_checkout_time}."


def request_transport(guest_id: str, pickup_time: str, airport_code: str) -> str:
    """Request transport to airport (stub)."""
    return (
        f"Transport requested for guest {guest_id} to {airport_code} at {pickup_time}."
    )


def guest_profile(phone_number: str) -> str:
    """Return guest profile information as JSON string."""
    guest = guests_by_phone.get(phone_number)
    return json.dumps(guest) if guest else "Guest not found."


def booking_details(phone_number: str) -> str:
    """Return booking details for the guest using their phone number."""
    guest = guests_by_phone.get(phone_number)
    if not guest:
        return "Guest not found."
    booking = bookings_by_guest.get(guest["guest_id"])
    return json.dumps(booking) if booking else "Booking not found."


def property_info(phone_number: str, query: str) -> str:
    """Retrieve property-specific info relevant to the guest's booking."""
    guest = guests_by_phone.get(phone_number)
    if not guest:
        return "Guest not found."
    booking = bookings_by_guest.get(guest["guest_id"])
    if not booking:
        return "Booking not found."
    prop_id = booking["property_id"]
    if not property_retriever:
        return "Property knowledge base not initialised yet."
    docs = property_retriever.get_relevant_documents(query, filter={"property_id": prop_id})
    return "\n---\n".join(d.page_content for d in docs) or "No relevant information found."

TOOLS = [
    Tool(
        name="schedule_cleaning",
        func=schedule_cleaning,
        description="Schedule a room cleaning. JSON: {guest_id, property_id, cleaning_time}",
    ),
    Tool(
        name="modify_checkout_time",
        func=modify_checkout_time,
        description="Modify a guest checkout time. JSON: {guest_id, new_checkout_time}",
    ),
    Tool(
        name="request_transport",
        func=request_transport,
        description="Request transport to the airport. JSON: {guest_id, pickup_time, airport_code}",
    ),
    Tool(
        name="guest_profile",
        func=guest_profile,
        description="Get the profile/preferences of a guest. JSON: {phone_number}",
    ),
    Tool(
        name="booking_details",
        func=booking_details,
        description="Get the booking details for a guest. JSON: {phone_number}",
    ),
    Tool(
        name="property_info",
        func=property_info,
        description="Retrieve information about the guest's property. JSON: {phone_number, query}",
    ),
]

# ----------------------------------------------------------------------------
# Agent helper
# ----------------------------------------------------------------------------

def get_agent(phone: str, system_prompt: Optional[str] = None):
    llm = ChatOpenAI(model_name="gpt-3.5-turbo-0613", temperature=0, openai_api_key=OPENAI_API_KEY)
    agent_kwargs = {"system_message": SystemMessage(content=system_prompt)} if system_prompt else {}
    return initialize_agent(
        TOOLS,
        llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        memory=get_memory(phone),
        verbose=False,
        **agent_kwargs,
    )

# ----------------------------------------------------------------------------
# API schema
# ----------------------------------------------------------------------------
class MessageRequest(BaseModel):
    message: str
    phone_number: str
    system_prompt: Optional[str] = None


class MessageResponse(BaseModel):
    response: str
    session_id: str  # Here we simply echo the phone number

# ----------------------------------------------------------------------------
# Endpoints
# ----------------------------------------------------------------------------
@app.post("/message", response_model=MessageResponse)
async def handle_message(req: MessageRequest):
    try:
        agent = get_agent(req.phone_number, req.system_prompt)
        reply = agent.run(req.message)
        cleanup_expired_sessions()
        return {"response": reply, "session_id": req.phone_number}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/session/{phone}")
async def get_session(phone: str):
    if phone not in memory_store:
        raise HTTPException(status_code=404, detail="Session not found")
    mem = memory_store[phone]
    return {
        "session_id": phone,
        "messages": [m.dict() for m in mem.chat_memory.messages],
    }


@app.delete("/session/{phone}")
async def delete_session(phone: str):
    memory_store.pop(phone, None)
    last_activity.pop(phone, None)
    return {"status": "deleted"}

# ----------------------------------------------------------------------------
# Dev entry-point
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 