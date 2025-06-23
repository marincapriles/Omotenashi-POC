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

# HIGH-IMPACT TIER INPUT SCHEMAS
class RestaurantReservationInput(BaseModel):
    restaurant_preference: str = Field(description="Type of cuisine or specific restaurant request")
    date_time: str = Field(description="Date and time for reservation")
    party_size: int = Field(description="Number of people")
    special_occasion: str = Field(default="", description="Special occasion or requirements")

class GroceryDeliveryInput(BaseModel):
    items_requested: str = Field(description="List of grocery items, beverages, or food preferences")
    delivery_time: str = Field(description="When items should be delivered")
    special_instructions: str = Field(default="", description="Dietary restrictions or special requests")

class MaintenanceRequestInput(BaseModel):
    issue_description: str = Field(description="Description of the maintenance issue")
    location: str = Field(description="Where in the property the issue is located")
    urgency: str = Field(default="normal", description="Urgency level: low, normal, high, emergency")

class ActivityBookingInput(BaseModel):
    activity_type: str = Field(description="Type of activity or experience requested")
    preferred_date: str = Field(description="Preferred date for the activity")
    participants: int = Field(description="Number of participants")
    special_requirements: str = Field(default="", description="Special requirements or preferences")

class MealDeliveryInput(BaseModel):
    cuisine_type: str = Field(description="Type of cuisine or specific restaurant")
    meal_items: str = Field(description="Specific dishes or meal preferences")
    delivery_time: str = Field(description="When the meal should be delivered")

# LUXURY TIER INPUT SCHEMAS  
class SpaServicesInput(BaseModel):
    service_type: str = Field(description="Type of spa service (massage, facial, etc.)")
    preferred_time: str = Field(description="Preferred appointment time")
    participants: int = Field(description="Number of people requiring service")
    special_requests: str = Field(default="", description="Special requests or preferences")

class PrivateChefInput(BaseModel):
    meal_type: str = Field(description="Breakfast, lunch, dinner, or special event")
    date_time: str = Field(description="Date and time for the meal")
    guests: int = Field(description="Number of guests")
    cuisine_preference: str = Field(description="Cuisine type or dietary preferences")
    special_occasion: str = Field(default="", description="Special occasion or theme")

class LocalRecommendationsInput(BaseModel):
    activity_category: str = Field(description="Type of recommendation: dining, activities, shopping, etc.")
    preferences: str = Field(default="", description="Guest preferences or interests")
    timeframe: str = Field(default="today", description="When they want to do this activity")

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
    
    # HIGH-IMPACT TIER TOOLS
    def restaurant_reservation(restaurant_preference: str, date_time: str, party_size: int, special_occasion: str = "") -> str:
        """Make restaurant reservations for guests."""
        guest = guest_service.get_guest(phone_number)
        if not guest:
            return "Guest not found."
        
        booking = guest_service.get_booking(guest["guest_id"])
        location = booking.get('property_name', 'your area') if booking else 'your area'
        
        occasion_text = f" for {special_occasion}" if special_occasion else ""
        dietary_info = ""
        if 'dietary_restrictions' in guest and guest['dietary_restrictions']:
            dietary_info = f" Please note dietary restrictions: {guest['dietary_restrictions']}."
        
        return (f"Perfect! I've secured a reservation for {party_size} people at a wonderful {restaurant_preference} restaurant "
                f"in {location} on {date_time}{occasion_text}. The restaurant has been notified of your VIP status and "
                f"will ensure an exceptional dining experience.{dietary_info} "
                f"You'll receive confirmation details shortly with the restaurant's address and any special instructions.")

    def grocery_delivery(items_requested: str, delivery_time: str, special_instructions: str = "") -> str:
        """Arrange grocery delivery to the property."""
        guest = guest_service.get_guest(phone_number)
        if not guest:
            return "Guest not found."
            
        booking = guest_service.get_booking(guest["guest_id"])
        property_name = booking.get('property_name', 'your property') if booking else 'your property'
        
        instruction_text = f" Special instructions: {special_instructions}." if special_instructions else ""
        
        return (f"Excellent, {guest['name']}! I've arranged grocery delivery to {property_name} "
                f"for {delivery_time}. Your order includes: {items_requested}.{instruction_text} "
                f"Our trusted local grocery partner will deliver fresh, high-quality items directly to your villa. "
                f"The groceries will be properly stored and organized for your arrival. "
                f"You'll receive a detailed receipt and confirmation when the delivery is complete.")

    def maintenance_request(issue_description: str, location: str, urgency: str = "normal") -> str:
        """Report and track maintenance issues at the property."""
        guest = guest_service.get_guest(phone_number)
        if not guest:
            return "Guest not found."
            
        booking = guest_service.get_booking(guest["guest_id"])
        property_name = booking.get('property_name', 'the property') if booking else 'the property'
        
        urgency_responses = {
            "emergency": "immediately. Our emergency response team has been notified and will arrive within 30 minutes",
            "high": "as a priority. Our maintenance team will address this within 2 hours", 
            "normal": "promptly. Our maintenance team will resolve this within 4-6 hours",
            "low": "and scheduled appropriately. This will be addressed within 24 hours"
        }
        
        response_text = urgency_responses.get(urgency, urgency_responses["normal"])
        
        # Log maintenance request details
        maintenance_details = {
            "timestamp": "2025-01-01T12:00:00Z",
            "guest_name": guest.get('name', 'Unknown Guest'),
            "guest_phone": phone_number,
            "property": property_name,
            "issue": issue_description,
            "location": location,
            "urgency": urgency,
            "status": "reported"
        }
        logger.info(f"MAINTENANCE REQUEST: {maintenance_details}")
        
        return (f"I've reported the {issue_description} in {location} at {property_name} {response_text}. "
                f"You'll receive updates on the repair progress, and our team will ensure minimal disruption to your stay. "
                f"If this is preventing you from enjoying any amenities, please let me know so I can arrange alternatives.")

    def activity_booking(activity_type: str, preferred_date: str, participants: int, special_requirements: str = "") -> str:
        """Book local activities and experiences for guests."""
        guest = guest_service.get_guest(phone_number)
        if not guest:
            return "Guest not found."
            
        booking = guest_service.get_booking(guest["guest_id"])
        location = booking.get('property_name', 'your area') if booking else 'your area'
        
        requirements_text = f" Special arrangements: {special_requirements}." if special_requirements else ""
        vip_text = " As our VIP guest, you'll receive premium treatment and priority access." if guest.get('vip_status') else ""
        
        return (f"Wonderful! I've arranged {activity_type} for {participants} people on {preferred_date} in {location}. "
                f"This curated experience has been selected specifically for our discerning guests and includes all necessary "
                f"arrangements and transportation.{requirements_text}{vip_text} "
                f"You'll receive detailed itinerary information including pickup times, what to bring, and contact details "
                f"for your experience coordinator.")

    def meal_delivery(cuisine_type: str, meal_items: str, delivery_time: str) -> str:
        """Order meal delivery from local restaurants."""
        guest = guest_service.get_guest(phone_number)
        if not guest:
            return "Guest not found."
            
        booking = guest_service.get_booking(guest["guest_id"])
        property_name = booking.get('property_name', 'your villa') if booking else 'your villa'
        
        dietary_info = ""
        if 'dietary_restrictions' in guest and guest['dietary_restrictions']:
            dietary_info = f" I've communicated your dietary restrictions ({guest['dietary_restrictions']}) to ensure everything meets your needs."
        
        return (f"Perfect, {guest['name']}! I've ordered {meal_items} from our preferred {cuisine_type} restaurant "
                f"for delivery to {property_name} at {delivery_time}. The restaurant is known for fresh, high-quality ingredients "
                f"and exceptional presentation.{dietary_info} "
                f"Your meal will arrive beautifully packaged with serving suggestions and will be delivered directly to your door. "
                f"Enjoy your delicious meal!")

    # LUXURY TIER TOOLS
    def spa_services(service_type: str, preferred_time: str, participants: int, special_requests: str = "") -> str:
        """Book in-villa spa and wellness services."""
        guest = guest_service.get_guest(phone_number)
        if not guest:
            return "Guest not found."
            
        booking = guest_service.get_booking(guest["guest_id"])
        property_name = booking.get('property_name', 'your villa') if booking else 'your villa'
        
        requests_text = f" Special arrangements: {special_requests}." if special_requests else ""
        
        return (f"Exceptional choice, {guest['name']}! I've arranged {service_type} for {participants} people "
                f"at {property_name} on {preferred_time}. Our certified wellness professionals will bring everything needed "
                f"for a luxurious spa experience in the comfort of your private space.{requests_text} "
                f"This includes premium organic products, relaxing music, and all necessary equipment. "
                f"Prepare for ultimate relaxation and rejuvenation in your own personal spa sanctuary.")

    def private_chef(meal_type: str, date_time: str, guests: int, cuisine_preference: str, special_occasion: str = "") -> str:
        """Arrange private chef services for in-villa dining."""
        guest = guest_service.get_guest(phone_number)
        if not guest:
            return "Guest not found."
            
        booking = guest_service.get_booking(guest["guest_id"])
        property_name = booking.get('property_name', 'your villa') if booking else 'your villa'
        
        occasion_text = f" celebrating {special_occasion}" if special_occasion else ""
        dietary_info = ""
        if 'dietary_restrictions' in guest and guest['dietary_restrictions']:
            dietary_info = f" The chef will accommodate your dietary preferences: {guest['dietary_restrictions']}."
        
        return (f"Magnificent, {guest['name']}! I've arranged a private chef to prepare {meal_type} "
                f"for {guests} guests at {property_name} on {date_time}{occasion_text}. "
                f"Your chef specializes in {cuisine_preference} cuisine and will create an unforgettable dining experience "
                f"using the finest local ingredients.{dietary_info} "
                f"The service includes menu planning, shopping, cooking, elegant presentation, and cleanup. "
                f"This will be a truly memorable culinary journey in the comfort of your private villa.")

    def local_recommendations(activity_category: str, preferences: str = "", timeframe: str = "today") -> str:
        """Provide personalized local recommendations based on guest profile."""
        guest = guest_service.get_guest(phone_number)
        if not guest:
            return "Guest not found."
            
        booking = guest_service.get_booking(guest["guest_id"])
        location = booking.get('property_name', 'your area') if booking else 'your area'
        
        preferences_text = f" matching your interests in {preferences}" if preferences else ""
        vip_text = " As our VIP guest, I've included exclusive options and insider recommendations." if guest.get('vip_status') else ""
        
        return (f"I'd be delighted to recommend the best {activity_category} options in {location} for {timeframe}{preferences_text}! "
                f"Based on your profile and current local conditions, I've curated a selection of exceptional experiences "
                f"that align perfectly with your style and the unique character of this destination.{vip_text} "
                f"These recommendations include insider tips, optimal timing, and booking assistance. "
                f"Would you like me to arrange reservations or provide additional details about any of these options?")
    
    # Return the structured tools
    return [
        # ORIGINAL CORE TOOLS
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
        
        # HIGH-IMPACT TIER TOOLS
        StructuredTool.from_function(
            func=restaurant_reservation,
            args_schema=RestaurantReservationInput,
            name="restaurant_reservation",
            description=TOOL_DESCRIPTIONS["restaurant_reservation"]
        ),
        StructuredTool.from_function(
            func=grocery_delivery,
            args_schema=GroceryDeliveryInput,
            name="grocery_delivery",
            description=TOOL_DESCRIPTIONS["grocery_delivery"]
        ),
        StructuredTool.from_function(
            func=maintenance_request,
            args_schema=MaintenanceRequestInput,
            name="maintenance_request",
            description=TOOL_DESCRIPTIONS["maintenance_request"]
        ),
        StructuredTool.from_function(
            func=activity_booking,
            args_schema=ActivityBookingInput,
            name="activity_booking",
            description=TOOL_DESCRIPTIONS["activity_booking"]
        ),
        StructuredTool.from_function(
            func=meal_delivery,
            args_schema=MealDeliveryInput,
            name="meal_delivery",
            description=TOOL_DESCRIPTIONS["meal_delivery"]
        ),
        
        # LUXURY TIER TOOLS
        StructuredTool.from_function(
            func=spa_services,
            args_schema=SpaServicesInput,
            name="spa_services",
            description=TOOL_DESCRIPTIONS["spa_services"]
        ),
        StructuredTool.from_function(
            func=private_chef,
            args_schema=PrivateChefInput,
            name="private_chef",
            description=TOOL_DESCRIPTIONS["private_chef"]
        ),
        StructuredTool.from_function(
            func=local_recommendations,
            args_schema=LocalRecommendationsInput,
            name="local_recommendations",
            description=TOOL_DESCRIPTIONS["local_recommendations"]
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