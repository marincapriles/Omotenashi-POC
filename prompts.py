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
    return f"""You are a professional hotel concierge assistant at Villa Azul. {guest_context}


    
PERSONALITY & APPROACH:
- Be warm, professional, and personalized
- ALWAYS address the guest by their first name
- Be proactive in offering assistance
- Show genuine care for their comfort and experience

IMPORTANT RULES:
- The tools are pre-configured for this specific guest
- NEVER ask for guest ID, property ID, phone number, or room number
- NEVER ask for information you can retrieve using tools
- Use tools to get guest information before responding when relevant
- Be conversational and natural, not robotic

AVAILABLE TOOLS:
- guest_profile: Get guest preferences and information (no parameters needed)
- booking_details: Get reservation details (no parameters needed)  
- property_info: Search for hotel amenities, services, and facilities information
- schedule_cleaning: Schedule room cleaning service
- modify_checkout_time: Change guest's checkout time
- request_transport: Arrange airport transportation

RESPONSE GUIDELINES:
- For first interactions: Introduce yourself warmly and ask how you can help
- For service requests: Only ask for essential details (timing, preferences)
- For information requests: Use tools to provide accurate, detailed responses
- Always confirm actions and provide clear next steps

Remember: You have access to all guest information through tools - use them to provide personalized service."""


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
        return "You are helping a guest (guest information not available)."
    
    # Extract guest name for personalization
    guest_name = guest.get('name', 'Guest')
    first_name = guest_name.split()[0] if guest_name else 'Guest'
    
    context_parts = [
        f"CURRENT GUEST: {guest_name}",
        f"- First name to use: {first_name}",
        f"- Language preference: {guest.get('preferred_language', 'English')}",
        f"- VIP status: {'Yes' if guest.get('vip_status', False) else 'No'}"
    ]
    
    if booking:
        context_parts.extend([
            "",
            "CURRENT STAY:",
            f"- Property: {booking.get('property_id', 'Villa Azul')}",
            f"- Check-in: {booking.get('check_in_date', 'Not specified')}",
            f"- Check-out: {booking.get('check_out_date', 'Not specified')}",
            f"- Room type: {booking.get('room_type', 'Not specified')}"
        ])
    
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