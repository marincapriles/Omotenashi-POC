"""
Agent Tools for Omotenashi Hotel Concierge
Contains all tool definitions for the AI concierge agent.
"""

import json
import logging
from typing import List
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from prompts import TOOL_DESCRIPTIONS

# Configure logging
logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------------
# Tool Input Schemas
# ----------------------------------------------------------------------------

class CleaningInput(BaseModel):
    cleaning_time: str = Field(description="Complete date and time for cleaning (e.g., 'Tuesday June 18th at 11:00 AM', 'Tomorrow at 2:00 PM')")

class CheckoutInput(BaseModel):
    new_checkout_time: str = Field(description="New checkout time")

class TransportInput(BaseModel):
    pickup_time: str = Field(description="Pickup time")
    airport_code: str = Field(description="Airport code")

class PropertyInfoInput(BaseModel):
    query: str = Field(default="general information", description="What to search for")

class EscalationInput(BaseModel):
    question: str = Field(description="The guest's question or request that needs escalation")
    context: str = Field(default="", description="Additional context about the situation")

# ----------------------------------------------------------------------------
# Tool Functions
# ----------------------------------------------------------------------------

def create_guest_tools(phone_number: str, guest_service, vector_store) -> List[StructuredTool]:
    """Create tools pre-configured for a specific guest."""
    
    def schedule_cleaning(cleaning_time: str) -> str:
        """Schedule room cleaning with complete date and time information."""
        guest = guest_service.get_guest(phone_number)
        if not guest:
            return "Guest not found."
        
        booking = guest_service.get_booking(guest["guest_id"])
        if not booking:
            return "Booking not found."
        
        # Validate that the time is specific enough
        cleaning_time_lower = cleaning_time.lower()
        vague_terms = ['morning', 'afternoon', 'evening', 'later', 'early', 'late', 'night']
        
        for vague_term in vague_terms:
            if vague_term in cleaning_time_lower and ':' not in cleaning_time_lower:
                return (f"I need a more specific time than '{cleaning_time}'. "
                        f"What exact time would work for you? We typically clean between "
                        f"10:00 AM and 2:00 PM. For example, would 11:00 AM or 1:00 PM work?")
        
        property_name = booking.get('property_name', booking.get('property_id', 'your room'))
        
        return (f"Perfect! I've scheduled room cleaning for {guest['name']} "
                f"at {property_name} on {cleaning_time}. "
                f"Our housekeeping team will arrive at the scheduled time. "
                f"Please ensure the room is accessible. Is there anything specific "
                f"you'd like our cleaning team to focus on?")
    
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
    
    def escalate_to_manager(question: str, context: str = "") -> str:
        """Escalate questions to property manager when unable to find answers."""
        guest = guest_service.get_guest(phone_number)
        if not guest:
            return "Unable to escalate - guest information not found."
        
        booking = guest_service.get_booking(guest["guest_id"])
        property_name = booking.get('property_name', 'Unknown Property') if booking else 'Unknown Property'
        
        # Log the escalation (in a real implementation, this would send notifications)
        escalation_details = {
            "timestamp": "2025-01-01T12:00:00Z",  # In real implementation, use actual timestamp
            "guest_name": guest.get('name', 'Unknown Guest'),
            "guest_phone": phone_number,
            "property": property_name,
            "question": question,
            "context": context,
            "status": "escalated"
        }
        
        logger.info(f"ESCALATION: {escalation_details}")
        
        # Stub implementation - in reality, this would:
        # - Send notification to property manager
        # - Create a ticket in management system
        # - Send email/SMS to admin
        # - Log in database
        
        return (f"I've escalated your question to the property manager at {property_name}. "
                f"They will get back to you shortly regarding: '{question}'. "
                f"Thank you for your patience!")
    
    # Return the structured tools
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
        StructuredTool.from_function(
            func=escalate_to_manager,
            args_schema=EscalationInput,
            name="escalate_to_manager",
            description=TOOL_DESCRIPTIONS["escalate_to_manager"]
        ),
    ]

# ----------------------------------------------------------------------------
# Tool Management Functions
# ----------------------------------------------------------------------------

def add_custom_tool(tools_list: List[StructuredTool], tool_func, tool_name: str, 
                   tool_description: str, args_schema=None) -> List[StructuredTool]:
    """
    Helper function to add custom tools to the existing tools list.
    
    Args:
        tools_list: Existing list of tools
        tool_func: Function to be wrapped as a tool
        tool_name: Name of the tool
        tool_description: Description of what the tool does
        args_schema: Optional Pydantic schema for structured inputs
    
    Returns:
        Updated tools list with the new tool added
    """
    if args_schema:
        new_tool = StructuredTool.from_function(
            func=tool_func,
            args_schema=args_schema,
            name=tool_name,
            description=tool_description
        )
    else:
        new_tool = StructuredTool.from_function(
            func=tool_func,
            name=tool_name,
            description=tool_description
        )
    
    tools_list.append(new_tool)
    return tools_list

def get_tool_info() -> dict:
    """
    Get information about all available tools.
    
    Returns:
        Dictionary with tool names and descriptions
    """
    return {
        "available_tools": {
            "schedule_cleaning": "Schedule room cleaning service",
            "modify_checkout_time": "Modify guest checkout time",
            "request_transport": "Request airport transport service",
            "guest_profile": "Get guest profile information",
            "booking_details": "Get guest booking details",
            "property_info": "Get property and amenities information",
            "escalate_to_manager": "Escalate questions to property manager"
        },
        "tool_descriptions": TOOL_DESCRIPTIONS
    } 