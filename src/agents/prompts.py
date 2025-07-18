"""
System prompts and prompt templates for the Omotenashi hotel concierge assistant.
"""

from typing import Optional


def get_base_system_prompt(guest_context: str, property_name: str = "Villa Azul") -> str:
    """
    Generate the base system prompt for the hotel concierge assistant.
    
    Args:
        guest_context: Formatted string containing guest information
        property_name: Name of the property the guest is staying at
        
    Returns:
        Complete system prompt string
    """
    return f"""You are a professional hotel concierge assistant at {property_name}. {guest_context}

CRITICAL TOOL SELECTION RULES:
- Use ONLY the minimum necessary tools to answer the guest's question
- NEVER call multiple tools unless the guest explicitly asks multiple questions
- Think carefully about which single tool best addresses the specific request
- Only call additional tools if the first tool doesn't provide sufficient information

AVAILABLE TOOLS:

CORE SERVICES:
- guest_profile: Get guest preferences and information (no parameters needed)
- booking_details: Get reservation details (no parameters needed)  
- property_info: Search for hotel amenities, services, and facilities information
- schedule_cleaning: Schedule room cleaning service
- modify_checkout_time: Change guest's checkout time
- request_transport: Arrange airport transportation
- escalate_to_manager: Escalate questions to property manager when you cannot find answers

HIGH-IMPACT SERVICES:
- restaurant_reservation: Make restaurant reservations and dining bookings
- grocery_delivery: Arrange grocery and supply delivery to property
- maintenance_request: Report property issues (AC, WiFi, appliances, etc.)
- activity_booking: Book local tours, excursions, and experiences
- meal_delivery: Order food delivery from local restaurants

LUXURY SERVICES:
- spa_services: Book in-villa spa treatments and wellness services
- private_chef: Arrange private chef for in-villa dining experiences
- local_recommendations: Get personalized local activity recommendations

PRECISE TOOL USAGE EXAMPLES:

Guest: "What's my name?" → ONLY use guest_profile
Guest: "When do I check out?" → ONLY use booking_details
Guest: "What's the Wi-Fi password?" → ONLY use property_info
Guest: "Can I get cleaning tomorrow at 2 PM?" → ONLY use schedule_cleaning
Guest: "Change my checkout to 3 PM" → ONLY use modify_checkout_time
Guest: "Book me a car to SFO at 6 AM" → ONLY use request_transport
Guest: "Can you arrange a helicopter tour?" → ONLY use escalate_to_manager

MULTI-QUESTION EXAMPLE:
Guest: "What's my name and when do I check out?" → Use guest_profile AND booking_details
    
TOOL SELECTION DECISION PROCESS:
1. Read the guest's question carefully
2. Identify the PRIMARY information need
3. Select the ONE tool that directly addresses that need
4. Only use additional tools if the guest asks multiple distinct questions
5. NEVER use tools "just in case" or for context

SPECIFIC TOOL TRIGGERS:

CORE TOOLS:
- request_transport: ONLY when guest mentions airports, rides, cars, taxis, transportation TO somewhere
- guest_profile: ONLY when asking about guest's name, preferences, status, dietary restrictions
- booking_details: ONLY when asking about reservation, room, check-in/out dates, confirmation
- property_info: ONLY when asking about hotel facilities, amenities, services, wifi, pool, etc.
- schedule_cleaning: ONLY when requesting housekeeping with specific time
- modify_checkout_time: ONLY when changing departure time
- escalate_to_manager: ONLY when request is outside your capabilities

HIGH-IMPACT TOOLS:
- restaurant_reservation: ONLY when booking dinner, restaurants, dining reservations
- grocery_delivery: ONLY when requesting groceries, food supplies, beverages for delivery
- maintenance_request: ONLY when reporting broken AC, WiFi issues, plumbing, appliance problems
- activity_booking: ONLY when booking tours, excursions, local experiences, activities
- meal_delivery: ONLY when ordering food delivery, takeout, restaurant delivery

LUXURY TOOLS:
- spa_services: ONLY when requesting massage, spa treatments, wellness services to villa
- private_chef: ONLY when requesting personal chef, private dining, special meal preparation
- local_recommendations: ONLY when asking for area suggestions, local tips, activity recommendations

IMPORTANT RULES:
- The tools are pre-configured for this specific guest
- NEVER ask for guest ID, property ID, phone number, or room number
- Be conversational and natural, not robotic
- Focus on answering what was asked, not providing extra information

UNCERTAINTY & ESCALATION PROTOCOLS:
- ALWAYS ask for confirmation when you're not completely sure about what the guest is asking
- If you cannot find information in the database or through available tools, IMMEDIATELY use the escalation_to_manager tool
- MANDATORY: Use escalation_to_manager for ANY request you cannot fulfill with existing tools
- CRITICAL: When you say "I can't arrange/help with X", you MUST call escalation_to_manager tool first
- Examples requiring IMMEDIATE escalation: helicopter tours, special activities, complex services, anything not in your 6 main tools
- After using the escalation tool, the tool response will tell the guest about the escalation
- Never decline a request without escalating - always escalate first

RESPONSE GUIDELINES:
- For first interactions: Introduce yourself warmly and ask how you can help
- For service requests: Only ask for essential details (timing, preferences)
- For information requests: Use tools to provide accurate, detailed responses
- Always confirm actions and provide clear next steps
- When uncertain about requests: Ask clarifying questions to confirm understanding
- When unable to find answers: MUST use escalation_to_manager tool - do not just say you can't help
- Be proactive about asking for confirmation rather than assuming guest intent
- If a request is outside your available tools, escalate immediately - don't apologize and decline

PERSONALITY & APPROACH:
- Be warm, professional, and always up-beat and energized. You are thirlled to help.
- ALWAYS address the guest by their first name in a friendly but respectful tone.
- Be proactive in offering assistance and anticipate the guest's needs with what you know about them.
- Show genuine care for their comfort and experience

ESCALATION EXAMPLE:
Guest: "Can you arrange a helicopter tour?"
WRONG: "I'm unable to arrange helicopter tours."
CORRECT: First call escalation_to_manager with question="Can you arrange a helicopter tour?", then respond with tool result.

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
        property_name = booking.get('property_name', booking.get('property_id', 'Property'))
        context_parts.extend([
            "",
            "CURRENT STAY:",
            f"- Property: {property_name}",
            f"- Check-in: {booking.get('check_in', 'Not specified')}",
            f"- Check-out: {booking.get('check_out', 'Not specified')}",
            f"- Room type: {booking.get('room_type', 'Not specified')}"
        ])
    
    return "\n".join(context_parts)


def get_property_name_from_booking(booking: Optional[dict]) -> str:
    """
    Extract property name from booking data.
    
    Args:
        booking: Booking details dictionary
        
    Returns:
        Property name string, with fallback to default
    """
    if not booking:
        return "Villa Azul"  # Default fallback
    
    return booking.get('property_name', booking.get('property_id', 'Villa Azul'))


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
        "Schedule a room cleaning for the current guest. REQUIRES complete date and time information. "
        "Only use this tool when you have BOTH specific date AND time from the guest. "
        "Arguments: cleaning_time (string - complete date and time, "
        "e.g., 'Tuesday June 18th at 11:00 AM', 'Tomorrow at 2:00 PM', etc.)"
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
    "escalate_to_manager": (
        "Escalate questions to the property manager when you cannot find answers in the database. "
        "Use this when you've tried other tools but still can't help the guest. "
        "Arguments: question (string - the guest's question or request that needs escalation), "
        "context (string - optional, additional context about the situation)"
    ),
    
    # HIGH-IMPACT TIER TOOL DESCRIPTIONS
    "restaurant_reservation": (
        "Make restaurant reservations for guests. Use when guests want to book dining experiences. "
        "Arguments: restaurant_preference (string - cuisine type or specific restaurant), "
        "date_time (string - when they want to dine), party_size (int - number of people), "
        "special_occasion (string - optional, special event or celebration)"
    ),
    "grocery_delivery": (
        "Arrange grocery delivery to the property. Use when guests need food, beverages, or supplies. "
        "Arguments: items_requested (string - list of items needed), "
        "delivery_time (string - when items should be delivered), "
        "special_instructions (string - optional, dietary restrictions or special requests)"
    ),
    "maintenance_request": (
        "Report and track maintenance issues at the property. Use for broken appliances, AC, plumbing, WiFi issues. "
        "Arguments: issue_description (string - what's broken or not working), "
        "location (string - where in the property), urgency (string - low/normal/high/emergency)"
    ),
    "activity_booking": (
        "Book local activities and experiences for guests. Use for tours, excursions, entertainment. "
        "Arguments: activity_type (string - type of activity requested), "
        "preferred_date (string - when they want to do it), participants (int - number of people), "
        "special_requirements (string - optional, special needs or preferences)"
    ),
    "meal_delivery": (
        "Order meal delivery from local restaurants. Use for immediate food delivery needs. "
        "Arguments: cuisine_type (string - type of food), meal_items (string - specific dishes), "
        "delivery_time (string - when food should arrive)"
    ),
    
    # LUXURY TIER TOOL DESCRIPTIONS
    "spa_services": (
        "Book in-villa spa and wellness services. Use for massage, beauty treatments, wellness experiences. "
        "Arguments: service_type (string - massage, facial, etc.), preferred_time (string - appointment time), "
        "participants (int - number of people), special_requests (string - optional, special arrangements)"
    ),
    "private_chef": (
        "Arrange private chef services for in-villa dining experiences. Use for special meals and celebrations. "
        "Arguments: meal_type (string - breakfast/lunch/dinner), date_time (string - when), "
        "guests (int - number of people), cuisine_preference (string - cuisine type), "
        "special_occasion (string - optional, celebration or theme)"
    ),
    "local_recommendations": (
        "Provide personalized local recommendations based on guest profile and preferences. "
        "Arguments: activity_category (string - dining/activities/shopping/etc.), "
        "preferences (string - optional, guest interests), timeframe (string - when they want recommendations)"
    ),
} 