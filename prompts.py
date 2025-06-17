"""
System prompts and prompt templates for the Omotenashi hotel concierge assistant.
"""

from typing import Optional


def get_base_system_prompt(guest_context: str) -> str:
    """
    Generate the base system prompt for the hotel concierge assistant.
    
    Args:
        guest_context: Formatted string containing guest information
        
    Returns:
        Complete system prompt string
    """
    return f"""You are a helpful hotel concierge assistant. {guest_context}

You are currently helping this specific guest. The tools are already configured for this guest 
and automatically know their guest ID, property ID, and other details.

IMPORTANT: Do NOT ask the guest for information you can get from tools:
- Do NOT ask for guest ID, property ID, or phone number
- Do NOT ask for room number or booking details
- Use the tools to get information you need

Available tools:
- guest_profile: Get this guest's preferences and information (no arguments needed)
- booking_details: Get this guest's reservation details (no arguments needed)  
- property_info: Get information about hotel amenities, services, and facilities 
  (provide a query about what you want to know)
- schedule_cleaning: Schedule room cleaning (only needs cleaning_time - when they want it cleaned)
- modify_checkout_time: Change checkout time (only needs new_checkout_time - the new time they want)
- request_transport: Arrange airport transportation (needs pickup_time and airport_code)

Be helpful, professional, and personalized. Use the guest's name when appropriate. 
When they request services, just ask for the essential details like timing or preferences, 
not their personal information."""


def format_guest_context(guest: Optional[dict], booking: Optional[dict] = None) -> str:
    """
    Format guest information into a context string for the system prompt.
    
    Args:
        guest: Guest profile dictionary
        booking: Optional booking details dictionary
        
    Returns:
        Formatted guest context string
    """
    if not guest:
        return ""
    
    context_parts = [
        f"You are helping guest: {guest['name']} (Phone: {guest.get('phone_number', 'N/A')})",
        f"Guest ID: {guest['guest_id']}",
        f"Preferred Language: {guest['preferred_language']}",
        f"VIP Status: {'Yes' if guest['vip_status'] else 'No'}"
    ]
    
    if booking:
        booking_info = [
            "Booking Details:",
            f"- Property ID: {booking['property_id']}",
            f"- Check-in: {booking.get('check_in_date', 'Not specified')}",
            f"- Check-out: {booking.get('check_out_date', 'Not specified')}",
            f"- Room Type: {booking.get('room_type', 'Not specified')}"
        ]
        context_parts.extend(booking_info)
    
    return "\n".join(context_parts)


def combine_prompts(base_prompt: str, custom_prompt: Optional[str] = None) -> str:
    """
    Combine base system prompt with optional custom instructions.
    
    Args:
        base_prompt: The base system prompt
        custom_prompt: Optional additional instructions
        
    Returns:
        Combined prompt string
    """
    if custom_prompt:
        return f"{base_prompt}\n\nAdditional instructions: {custom_prompt}"
    return base_prompt


# Tool descriptions for better organization
TOOL_DESCRIPTIONS = {
    "schedule_cleaning": (
        "Schedule a room cleaning for the current guest. Only requires the cleaning time. "
        "Arguments: cleaning_time (string - when the guest wants the cleaning, "
        "e.g., '2:00 PM today', 'tomorrow morning', etc.)"
    ),
    "modify_checkout_time": (
        "Modify the current guest's checkout time. Only requires the new checkout time. "
        "Arguments: new_checkout_time (string - the new checkout time, "
        "e.g., '12:00 PM', 'late checkout 3:00 PM', etc.)"
    ),
    "request_transport": (
        "Request transport to the airport for the current guest. "
        "Arguments: pickup_time (string - when to pick up the guest), "
        "airport_code (string - destination airport code like 'SFO', 'LAX', etc.)"
    ),
    "guest_profile": (
        "Get the profile and preferences of the current guest. "
        "Use this to get guest information. No arguments needed."
    ),
    "booking_details": (
        "Get the booking details for the current guest. "
        "Use this to get reservation information. No arguments needed."
    ),
    "property_info": (
        "Retrieve information about the current guest's property. "
        "Use this to answer questions about the hotel/property. "
        "Arguments: query (string - optional, what information you want to know about the property)"
    ),
} 