#!/usr/bin/env python3
"""
Comprehensive Tool Selection Evaluation for Expanded Omotenashi System
Evaluates precision and recall of all 15 tools (7 original + 8 new).
"""

import json
import logging
import requests
import time
from typing import Dict, List, Tuple
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# COMPREHENSIVE TEST CASES (150+ tests covering all 15 tools)
TEST_CASES = [
    # CORE TOOLS (Original 7 tools) - 70 cases
    
    # GUEST PROFILE TOOL (10 cases)
    {"id": 1, "prompt": "Hi, what's my name?", "expected_tools": ["guest_profile"], "category": "guest_info"},
    {"id": 2, "prompt": "Can you tell me about my preferences?", "expected_tools": ["guest_profile"], "category": "guest_info"},
    {"id": 3, "prompt": "Am I a VIP guest?", "expected_tools": ["guest_profile"], "category": "guest_info"},
    {"id": 4, "prompt": "What language do I prefer?", "expected_tools": ["guest_profile"], "category": "guest_info"},
    {"id": 5, "prompt": "What are my dietary restrictions?", "expected_tools": ["guest_profile"], "category": "guest_info"},
    {"id": 6, "prompt": "Do you have my contact information?", "expected_tools": ["guest_profile"], "category": "guest_info"},
    {"id": 7, "prompt": "Can you show me my profile?", "expected_tools": ["guest_profile"], "category": "guest_info"},
    {"id": 8, "prompt": "What's my guest ID?", "expected_tools": ["guest_profile"], "category": "guest_info"},
    {"id": 9, "prompt": "Tell me about myself", "expected_tools": ["guest_profile"], "category": "guest_info"},
    {"id": 10, "prompt": "What's my guest status?", "expected_tools": ["guest_profile"], "category": "guest_info"},
    
    # BOOKING DETAILS TOOL (10 cases)
    {"id": 11, "prompt": "When do I check out?", "expected_tools": ["booking_details"], "category": "booking_info"},
    {"id": 12, "prompt": "What room am I staying in?", "expected_tools": ["booking_details"], "category": "booking_info"},
    {"id": 13, "prompt": "Can you show me my reservation details?", "expected_tools": ["booking_details"], "category": "booking_info"},
    {"id": 14, "prompt": "When is my check-in date?", "expected_tools": ["booking_details"], "category": "booking_info"},
    {"id": 15, "prompt": "What type of room did I book?", "expected_tools": ["booking_details"], "category": "booking_info"},
    {"id": 16, "prompt": "How many nights am I staying?", "expected_tools": ["booking_details"], "category": "booking_info"},
    {"id": 17, "prompt": "What's my confirmation number?", "expected_tools": ["booking_details"], "category": "booking_info"},
    {"id": 18, "prompt": "Show me my booking information", "expected_tools": ["booking_details"], "category": "booking_info"},
    {"id": 19, "prompt": "What's my arrival time?", "expected_tools": ["booking_details"], "category": "booking_info"},
    {"id": 20, "prompt": "What's my departure date?", "expected_tools": ["booking_details"], "category": "booking_info"},
    
    # PROPERTY INFO TOOL (10 cases)
    {"id": 21, "prompt": "What's the WiFi password?", "expected_tools": ["property_info"], "category": "property_info"},
    {"id": 22, "prompt": "What time does the pool open?", "expected_tools": ["property_info"], "category": "property_info"},
    {"id": 23, "prompt": "Do you have a gym?", "expected_tools": ["property_info"], "category": "property_info"},
    {"id": 24, "prompt": "Tell me about the hotel amenities", "expected_tools": ["property_info"], "category": "property_info"},
    {"id": 25, "prompt": "What services do you offer?", "expected_tools": ["property_info"], "category": "property_info"},
    {"id": 26, "prompt": "Where is the spa located?", "expected_tools": ["property_info"], "category": "property_info"},
    {"id": 27, "prompt": "Can you tell me about the hotel facilities?", "expected_tools": ["property_info"], "category": "property_info"},
    {"id": 28, "prompt": "What's the breakfast schedule?", "expected_tools": ["property_info"], "category": "property_info"},
    {"id": 29, "prompt": "Do you have room service?", "expected_tools": ["property_info"], "category": "property_info"},
    {"id": 30, "prompt": "Where's the business center?", "expected_tools": ["property_info"], "category": "property_info"},
    
    # SCHEDULE CLEANING TOOL (10 cases)
    {"id": 31, "prompt": "Can you clean my room tomorrow at 2 PM?", "expected_tools": ["schedule_cleaning"], "category": "cleaning"},
    {"id": 32, "prompt": "I need housekeeping service on Friday at 11:00 AM", "expected_tools": ["schedule_cleaning"], "category": "cleaning"},
    {"id": 33, "prompt": "Please schedule room cleaning for today at 3:30 PM", "expected_tools": ["schedule_cleaning"], "category": "cleaning"},
    {"id": 34, "prompt": "Can you arrange cleaning service for Monday morning at 10 AM?", "expected_tools": ["schedule_cleaning"], "category": "cleaning"},
    {"id": 35, "prompt": "I'd like room service cleaning tomorrow at 1:00 PM", "expected_tools": ["schedule_cleaning"], "category": "cleaning"},
    {"id": 36, "prompt": "Schedule housekeeping for Wednesday at 9:30 AM", "expected_tools": ["schedule_cleaning"], "category": "cleaning"},
    {"id": 37, "prompt": "Can you clean my room on Thursday at 4:00 PM?", "expected_tools": ["schedule_cleaning"], "category": "cleaning"},
    {"id": 38, "prompt": "I need cleaning service tomorrow at 12:30 PM", "expected_tools": ["schedule_cleaning"], "category": "cleaning"},
    {"id": 39, "prompt": "Please arrange housekeeping for Sunday at 10:15 AM", "expected_tools": ["schedule_cleaning"], "category": "cleaning"},
    {"id": 40, "prompt": "Book room cleaning for next Tuesday at 2:45 PM", "expected_tools": ["schedule_cleaning"], "category": "cleaning"},
    
    # MODIFY CHECKOUT TOOL (10 cases)
    {"id": 41, "prompt": "Can I change my checkout to 3 PM?", "expected_tools": ["modify_checkout_time"], "category": "checkout"},
    {"id": 42, "prompt": "I need to extend my checkout until 2:00 PM", "expected_tools": ["modify_checkout_time"], "category": "checkout"},
    {"id": 43, "prompt": "Can you give me a late checkout at 1 PM?", "expected_tools": ["modify_checkout_time"], "category": "checkout"},
    {"id": 44, "prompt": "I want to check out at noon instead of 11 AM", "expected_tools": ["modify_checkout_time"], "category": "checkout"},
    {"id": 45, "prompt": "Please change my departure time to 4:00 PM", "expected_tools": ["modify_checkout_time"], "category": "checkout"},
    {"id": 46, "prompt": "Can I get a late checkout until 5 PM?", "expected_tools": ["modify_checkout_time"], "category": "checkout"},
    {"id": 47, "prompt": "I need to modify my checkout time to 1:30 PM", "expected_tools": ["modify_checkout_time"], "category": "checkout"},
    {"id": 48, "prompt": "Can you extend my stay until 6 PM checkout?", "expected_tools": ["modify_checkout_time"], "category": "checkout"},
    {"id": 49, "prompt": "Change my checkout from 11 AM to 2 PM please", "expected_tools": ["modify_checkout_time"], "category": "checkout"},
    {"id": 50, "prompt": "I want to leave later, can you change my checkout?", "expected_tools": ["modify_checkout_time"], "category": "checkout"},
    
    # REQUEST TRANSPORT TOOL (10 cases)
    {"id": 51, "prompt": "Can you get me a ride to SFO airport at 6 AM?", "expected_tools": ["request_transport"], "category": "transport"},
    {"id": 52, "prompt": "I need transportation to LAX tomorrow at 3:30 PM", "expected_tools": ["request_transport"], "category": "transport"},
    {"id": 53, "prompt": "Please arrange a car to the airport at 8:00 AM", "expected_tools": ["request_transport"], "category": "transport"},
    {"id": 54, "prompt": "Can you book airport transport for 5:45 AM to JFK?", "expected_tools": ["request_transport"], "category": "transport"},
    {"id": 55, "prompt": "I need a taxi to Oakland airport at 7 PM", "expected_tools": ["request_transport"], "category": "transport"},
    {"id": 56, "prompt": "Book me a car to SFO at 9:30 AM tomorrow", "expected_tools": ["request_transport"], "category": "transport"},
    {"id": 57, "prompt": "Can you arrange airport pickup at 4:15 PM to LAX?", "expected_tools": ["request_transport"], "category": "transport"},
    {"id": 58, "prompt": "I need transport to the airport at 6:45 AM", "expected_tools": ["request_transport"], "category": "transport"},
    {"id": 59, "prompt": "Please get me a ride to JFK at 2:30 PM", "expected_tools": ["request_transport"], "category": "transport"},
    {"id": 60, "prompt": "Can you call a taxi for airport transfer at 5 AM?", "expected_tools": ["request_transport"], "category": "transport"},
    
    # ESCALATION TOOL (10 cases)
    {"id": 61, "prompt": "Can you book me a helicopter tour?", "expected_tools": ["escalate_to_manager"], "category": "escalation"},
    {"id": 62, "prompt": "I want to rent a yacht for tomorrow", "expected_tools": ["escalate_to_manager"], "category": "escalation"},
    {"id": 63, "prompt": "Can you arrange a private jet charter?", "expected_tools": ["escalate_to_manager"], "category": "escalation"},
    {"id": 64, "prompt": "I need a personal shopping assistant", "expected_tools": ["escalate_to_manager"], "category": "escalation"},
    {"id": 65, "prompt": "Can you book tickets to a Broadway show?", "expected_tools": ["escalate_to_manager"], "category": "escalation"},
    {"id": 66, "prompt": "I want to arrange a private dining experience", "expected_tools": ["escalate_to_manager"], "category": "escalation"},
    {"id": 67, "prompt": "Can you help me buy a luxury watch?", "expected_tools": ["escalate_to_manager"], "category": "escalation"},
    {"id": 68, "prompt": "I need to charter a private plane", "expected_tools": ["escalate_to_manager"], "category": "escalation"},
    {"id": 69, "prompt": "Can you arrange for a limousine city tour?", "expected_tools": ["escalate_to_manager"], "category": "escalation"},
    {"id": 70, "prompt": "I want to book a penthouse suite upgrade", "expected_tools": ["escalate_to_manager"], "category": "escalation"},

    # HIGH-IMPACT TIER TOOLS (50 cases)
    
    # RESTAURANT RESERVATION TOOL (10 cases)
    {"id": 71, "prompt": "Can you book me dinner at a nice Italian restaurant tonight?", "expected_tools": ["restaurant_reservation"], "category": "dining"},
    {"id": 72, "prompt": "I need a table for 4 at a good seafood place tomorrow at 7 PM", "expected_tools": ["restaurant_reservation"], "category": "dining"},
    {"id": 73, "prompt": "Please make a reservation for 2 people at a romantic restaurant", "expected_tools": ["restaurant_reservation"], "category": "dining"},
    {"id": 74, "prompt": "Can you book us a table for our anniversary dinner?", "expected_tools": ["restaurant_reservation"], "category": "dining"},
    {"id": 75, "prompt": "I want to make a dinner reservation for 6 people at 8 PM", "expected_tools": ["restaurant_reservation"], "category": "dining"},
    {"id": 76, "prompt": "Book me a table at the best French restaurant in town", "expected_tools": ["restaurant_reservation"], "category": "dining"},
    {"id": 77, "prompt": "Can you get us a reservation at a steakhouse for tonight?", "expected_tools": ["restaurant_reservation"], "category": "dining"},
    {"id": 78, "prompt": "I need a table for lunch tomorrow at a nice Mediterranean place", "expected_tools": ["restaurant_reservation"], "category": "dining"},
    {"id": 79, "prompt": "Please book a birthday dinner for 8 people", "expected_tools": ["restaurant_reservation"], "category": "dining"},
    {"id": 80, "prompt": "Can you make a reservation at a sushi restaurant for 2?", "expected_tools": ["restaurant_reservation"], "category": "dining"},
    
    # GROCERY DELIVERY TOOL (10 cases)
    {"id": 81, "prompt": "Can you stock some wine and snacks before I arrive?", "expected_tools": ["grocery_delivery"], "category": "groceries"},
    {"id": 82, "prompt": "I need groceries delivered - milk, bread, and fruit", "expected_tools": ["grocery_delivery"], "category": "groceries"},
    {"id": 83, "prompt": "Please arrange for breakfast items to be delivered tomorrow", "expected_tools": ["grocery_delivery"], "category": "groceries"},
    {"id": 84, "prompt": "Can you get some beverages and cheese delivered today?", "expected_tools": ["grocery_delivery"], "category": "groceries"},
    {"id": 85, "prompt": "I need organic vegetables and pasta delivered this evening", "expected_tools": ["grocery_delivery"], "category": "groceries"},
    {"id": 86, "prompt": "Can you stock the fridge with healthy options before my arrival?", "expected_tools": ["grocery_delivery"], "category": "groceries"},
    {"id": 87, "prompt": "Please arrange grocery delivery with baby food and diapers", "expected_tools": ["grocery_delivery"], "category": "groceries"},
    {"id": 88, "prompt": "I need gluten-free items delivered to the villa", "expected_tools": ["grocery_delivery"], "category": "groceries"},
    {"id": 89, "prompt": "Can you get champagne and appetizers delivered for tonight?", "expected_tools": ["grocery_delivery"], "category": "groceries"},
    {"id": 90, "prompt": "Please stock basic cooking ingredients in the kitchen", "expected_tools": ["grocery_delivery"], "category": "groceries"},
    
    # MAINTENANCE REQUEST TOOL (10 cases)
    {"id": 91, "prompt": "The air conditioning isn't working in the master bedroom", "expected_tools": ["maintenance_request"], "category": "maintenance"},
    {"id": 92, "prompt": "The WiFi is really slow throughout the house", "expected_tools": ["maintenance_request"], "category": "maintenance"},
    {"id": 93, "prompt": "There's no hot water in the main bathroom", "expected_tools": ["maintenance_request"], "category": "maintenance"},
    {"id": 94, "prompt": "The dishwasher seems to be broken", "expected_tools": ["maintenance_request"], "category": "maintenance"},
    {"id": 95, "prompt": "The pool heater isn't working properly", "expected_tools": ["maintenance_request"], "category": "maintenance"},
    {"id": 96, "prompt": "One of the bedroom lights is flickering constantly", "expected_tools": ["maintenance_request"], "category": "maintenance"},
    {"id": 97, "prompt": "The garbage disposal is making strange noises", "expected_tools": ["maintenance_request"], "category": "maintenance"},
    {"id": 98, "prompt": "The TV in the living room won't turn on", "expected_tools": ["maintenance_request"], "category": "maintenance"},
    {"id": 99, "prompt": "There's a leak under the kitchen sink", "expected_tools": ["maintenance_request"], "category": "maintenance"},
    {"id": 100, "prompt": "The hot tub jets aren't working", "expected_tools": ["maintenance_request"], "category": "maintenance"},
    
    # ACTIVITY BOOKING TOOL (10 cases)
    {"id": 101, "prompt": "Can you book us a wine tour for tomorrow?", "expected_tools": ["activity_booking"], "category": "activities"},
    {"id": 102, "prompt": "I want to book a sunset boat cruise for 4 people", "expected_tools": ["activity_booking"], "category": "activities"},
    {"id": 103, "prompt": "Please arrange a hiking tour for this weekend", "expected_tools": ["activity_booking"], "category": "activities"},
    {"id": 104, "prompt": "Can you book tickets for a cooking class?", "expected_tools": ["activity_booking"], "category": "activities"},
    {"id": 105, "prompt": "I need to book a fishing charter for 6 people", "expected_tools": ["activity_booking"], "category": "activities"},
    {"id": 106, "prompt": "Please arrange a city tour for my family", "expected_tools": ["activity_booking"], "category": "activities"},
    {"id": 107, "prompt": "Can you book a golf tee time for 2 people tomorrow?", "expected_tools": ["activity_booking"], "category": "activities"},
    {"id": 108, "prompt": "I want to book a zip-lining adventure for Friday", "expected_tools": ["activity_booking"], "category": "activities"},
    {"id": 109, "prompt": "Please arrange a museum tour with a private guide", "expected_tools": ["activity_booking"], "category": "activities"},
    {"id": 110, "prompt": "Can you book us a snorkeling excursion?", "expected_tools": ["activity_booking"], "category": "activities"},
    
    # MEAL DELIVERY TOOL (10 cases)
    {"id": 111, "prompt": "Can you order Chinese food for delivery tonight?", "expected_tools": ["meal_delivery"], "category": "food_delivery"},
    {"id": 112, "prompt": "I'm hungry now - can you get pizza delivered?", "expected_tools": ["meal_delivery"], "category": "food_delivery"},
    {"id": 113, "prompt": "Please order sushi for 4 people for lunch", "expected_tools": ["meal_delivery"], "category": "food_delivery"},
    {"id": 114, "prompt": "Can you get Thai food delivered in 30 minutes?", "expected_tools": ["meal_delivery"], "category": "food_delivery"},
    {"id": 115, "prompt": "I need healthy salads delivered for the family", "expected_tools": ["meal_delivery"], "category": "food_delivery"},
    {"id": 116, "prompt": "Please order Indian food for dinner delivery", "expected_tools": ["meal_delivery"], "category": "food_delivery"},
    {"id": 117, "prompt": "Can you get burgers and fries delivered for the kids?", "expected_tools": ["meal_delivery"], "category": "food_delivery"},
    {"id": 118, "prompt": "I want Mexican food delivered at 7 PM", "expected_tools": ["meal_delivery"], "category": "food_delivery"},
    {"id": 119, "prompt": "Please order breakfast delivery for tomorrow morning", "expected_tools": ["meal_delivery"], "category": "food_delivery"},
    {"id": 120, "prompt": "Can you get sandwiches delivered for lunch?", "expected_tools": ["meal_delivery"], "category": "food_delivery"},

    # LUXURY TIER TOOLS (30 cases)
    
    # SPA SERVICES TOOL (10 cases)
    {"id": 121, "prompt": "Can you book a massage therapist to come to the villa?", "expected_tools": ["spa_services"], "category": "wellness"},
    {"id": 122, "prompt": "I need a couples massage for this afternoon", "expected_tools": ["spa_services"], "category": "wellness"},
    {"id": 123, "prompt": "Please arrange a facial treatment at the house", "expected_tools": ["spa_services"], "category": "wellness"},
    {"id": 124, "prompt": "Can you book a spa day for 4 ladies?", "expected_tools": ["spa_services"], "category": "wellness"},
    {"id": 125, "prompt": "I want a deep tissue massage tomorrow at 2 PM", "expected_tools": ["spa_services"], "category": "wellness"},
    {"id": 126, "prompt": "Please arrange manicure and pedicure services", "expected_tools": ["spa_services"], "category": "wellness"},
    {"id": 127, "prompt": "Can you book a prenatal massage for my wife?", "expected_tools": ["spa_services"], "category": "wellness"},
    {"id": 128, "prompt": "I need aromatherapy treatment in the villa", "expected_tools": ["spa_services"], "category": "wellness"},
    {"id": 129, "prompt": "Please book a hot stone massage for tonight", "expected_tools": ["spa_services"], "category": "wellness"},
    {"id": 130, "prompt": "Can you arrange yoga instructor to come here?", "expected_tools": ["spa_services"], "category": "wellness"},
    
    # PRIVATE CHEF TOOL (10 cases)
    {"id": 131, "prompt": "Can you arrange a private chef for dinner tonight?", "expected_tools": ["private_chef"], "category": "private_dining"},
    {"id": 132, "prompt": "I want a chef to cook breakfast for 6 people tomorrow", "expected_tools": ["private_chef"], "category": "private_dining"},
    {"id": 133, "prompt": "Please book a private chef for our anniversary dinner", "expected_tools": ["private_chef"], "category": "private_dining"},
    {"id": 134, "prompt": "Can you get a chef to prepare a 7-course meal?", "expected_tools": ["private_chef"], "category": "private_dining"},
    {"id": 135, "prompt": "I need a personal chef for the entire weekend", "expected_tools": ["private_chef"], "category": "private_dining"},
    {"id": 136, "prompt": "Please arrange a chef for a birthday party dinner", "expected_tools": ["private_chef"], "category": "private_dining"},
    {"id": 137, "prompt": "Can you book a chef specializing in French cuisine?", "expected_tools": ["private_chef"], "category": "private_dining"},
    {"id": 138, "prompt": "I want a chef to cook a romantic dinner for 2", "expected_tools": ["private_chef"], "category": "private_dining"},
    {"id": 139, "prompt": "Please get a chef for a family reunion meal", "expected_tools": ["private_chef"], "category": "private_dining"},
    {"id": 140, "prompt": "Can you arrange a sushi chef for tonight?", "expected_tools": ["private_chef"], "category": "private_dining"},
    
    # LOCAL RECOMMENDATIONS TOOL (10 cases)
    {"id": 141, "prompt": "What are the best restaurants in the area?", "expected_tools": ["local_recommendations"], "category": "recommendations"},
    {"id": 142, "prompt": "Can you recommend fun activities for kids?", "expected_tools": ["local_recommendations"], "category": "recommendations"},
    {"id": 143, "prompt": "What's the best beach to visit today?", "expected_tools": ["local_recommendations"], "category": "recommendations"},
    {"id": 144, "prompt": "Please suggest romantic spots for couples", "expected_tools": ["local_recommendations"], "category": "recommendations"},
    {"id": 145, "prompt": "What are good shopping areas nearby?", "expected_tools": ["local_recommendations"], "category": "recommendations"},
    {"id": 146, "prompt": "Can you recommend nightlife options?", "expected_tools": ["local_recommendations"], "category": "recommendations"},
    {"id": 147, "prompt": "What are the must-see attractions here?", "expected_tools": ["local_recommendations"], "category": "recommendations"},
    {"id": 148, "prompt": "Please suggest outdoor activities for tomorrow", "expected_tools": ["local_recommendations"], "category": "recommendations"},
    {"id": 149, "prompt": "What are good breakfast spots in town?", "expected_tools": ["local_recommendations"], "category": "recommendations"},
    {"id": 150, "prompt": "Can you recommend local art galleries?", "expected_tools": ["local_recommendations"], "category": "recommendations"},
]

class ComprehensiveToolEvaluator:
    """Evaluates tool selection performance of the expanded Omotenashi system."""
    
    def __init__(self, api_base_url: str = "http://localhost:8000", test_phone: str = "+14155550123"):
        self.api_base_url = api_base_url
        self.test_phone = test_phone
        self.results = []
        
        # Comprehensive tool detection patterns for all 15 tools
        self.tool_patterns = {
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
    
    def extract_tools_from_response(self, response_text: str) -> List[str]:
        """Extract tool names from agent response using pattern matching."""
        tools_called = []
        response_lower = response_text.lower()
        
        for tool_name, patterns in self.tool_patterns.items():
            if any(pattern in response_lower for pattern in patterns):
                tools_called.append(tool_name)
        
        return list(set(tools_called))  # Remove duplicates
    
    def send_message(self, message: str) -> Tuple[str, bool, List[str]]:
        """Send a message to the API and get response with tool information."""
        try:
            payload = {"message": message, "phone_number": self.test_phone}
            response = requests.post(f"{self.api_base_url}/message", json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data["response"], True, data.get("tools_used", [])
            else:
                logger.error(f"API error {response.status_code}: {response.text}")
                return f"API Error: {response.status_code}", False, []
                
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return f"Request failed: {e}", False, []
    
    def clear_session(self):
        """Clear the conversation session."""
        try:
            requests.delete(f"{self.api_base_url}/session/{self.test_phone}")
        except:
            pass  # Ignore errors
    
    def evaluate_test_case(self, test_case: Dict) -> Dict:
        """Evaluate a single test case."""
        logger.info(f"Testing case {test_case['id']}: {test_case['prompt']}")
        
        response, success, api_tools = self.send_message(test_case["prompt"])
        
        # Use both API-reported tools and pattern detection
        pattern_tools = self.extract_tools_from_response(response) if success else []
        actual_tools = list(set(api_tools + pattern_tools))  # Combine and deduplicate
        
        result = {
            "test_id": test_case["id"],
            "prompt": test_case["prompt"],
            "expected_tools": test_case["expected_tools"],
            "actual_tools": actual_tools,
            "api_tools": api_tools,
            "pattern_tools": pattern_tools,
            "response": response[:200] + "..." if len(response) > 200 else response,
            "success": success,
            "category": test_case["category"]
        }
        
        logger.info(f"Expected: {test_case['expected_tools']}, Got: {actual_tools}")
        return result
    
    def calculate_metrics(self) -> Dict:
        """Calculate precision, recall, and F1 scores."""
        successful_tests = [r for r in self.results if r["success"]]
        
        if not successful_tests:
            return {"error": "No successful tests to evaluate"}
        
        # Overall metrics
        total_tp = total_fp = total_fn = 0
        tool_metrics = {}
        
        for result in successful_tests:
            expected = set(result["expected_tools"])
            actual = set(result["actual_tools"])
            
            tp = len(expected & actual)
            fp = len(actual - expected)
            fn = len(expected - actual)
            
            total_tp += tp
            total_fp += fp
            total_fn += fn
            
            # Track per-tool performance
            for tool in expected:
                if tool not in tool_metrics:
                    tool_metrics[tool] = {"tp": 0, "fp": 0, "fn": 0}
                if tool in actual:
                    tool_metrics[tool]["tp"] += 1
                else:
                    tool_metrics[tool]["fn"] += 1
            
            for tool in actual:
                if tool not in tool_metrics:
                    tool_metrics[tool] = {"tp": 0, "fp": 0, "fn": 0}
                if tool not in expected:
                    tool_metrics[tool]["fp"] += 1
        
        # Calculate overall metrics
        precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
        recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        # Calculate per-tool metrics
        tool_results = {}
        for tool, counts in tool_metrics.items():
            tp, fp, fn = counts["tp"], counts["fp"], counts["fn"]
            tool_precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            tool_recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            tool_f1 = 2 * (tool_precision * tool_recall) / (tool_precision + tool_recall) if (tool_precision + tool_recall) > 0 else 0
            
            tool_results[tool] = {
                "precision": round(tool_precision, 3),
                "recall": round(tool_recall, 3),
                "f1": round(tool_f1, 3),
                "tp": tp, "fp": fp, "fn": fn
            }
        
        # Category analysis
        category_metrics = {}
        for category in set(r["category"] for r in successful_tests):
            category_tests = [r for r in successful_tests if r["category"] == category]
            cat_tp = cat_fp = cat_fn = 0
            
            for result in category_tests:
                expected = set(result["expected_tools"])
                actual = set(result["actual_tools"])
                
                cat_tp += len(expected & actual)
                cat_fp += len(actual - expected)
                cat_fn += len(expected - actual)
            
            cat_precision = cat_tp / (cat_tp + cat_fp) if (cat_tp + cat_fp) > 0 else 0
            cat_recall = cat_tp / (cat_tp + cat_fn) if (cat_tp + cat_fn) > 0 else 0
            cat_f1 = 2 * (cat_precision * cat_recall) / (cat_precision + cat_recall) if (cat_precision + cat_recall) > 0 else 0
            
            category_metrics[category] = {
                "precision": round(cat_precision, 3),
                "recall": round(cat_recall, 3),
                "f1": round(cat_f1, 3),
                "test_count": len(category_tests)
            }
        
        return {
            "overall": {
                "precision": round(precision, 3),
                "recall": round(recall, 3),
                "f1": round(f1, 3),
                "total_tests": len(successful_tests),
                "total_tp": total_tp,
                "total_fp": total_fp,
                "total_fn": total_fn
            },
            "per_tool": tool_results,
            "per_category": category_metrics
        }
    
    def run_evaluation(self, limit: int = None) -> Dict:
        """Run the complete evaluation."""
        test_cases = TEST_CASES[:limit] if limit else TEST_CASES
        logger.info(f"Starting comprehensive evaluation with {len(test_cases)} test cases")
        
        # Clear session to start fresh
        self.clear_session()
        
        # Run each test case
        for i, test_case in enumerate(test_cases):
            result = self.evaluate_test_case(test_case)
            self.results.append(result)
            
            # Small delay to avoid overwhelming the API
            time.sleep(0.5)
            
            # Progress update
            if (i + 1) % 25 == 0:
                logger.info(f"Completed {i + 1}/{len(test_cases)} test cases")
        
        # Calculate metrics
        metrics = self.calculate_metrics()
        
        # Save results
        self.save_results(metrics)
        
        return metrics
    
    def save_results(self, metrics: Dict):
        """Save detailed results to files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed JSON results
        with open(f"comprehensive_evaluation_results_{timestamp}.json", "w") as f:
            json.dump({
                "metrics": metrics,
                "detailed_results": self.results,
                "test_cases_count": len(TEST_CASES),
                "tools_evaluated": 15
            }, f, indent=2)
        
        # Save formatted TXT results
        txt_filename = f"comprehensive_tool_evaluation_{timestamp}.txt"
        with open(txt_filename, "w") as f:
            f.write("=" * 100 + "\n")
            f.write("COMPREHENSIVE OMOTENASHI TOOL SELECTION EVALUATION REPORT\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Test Cases: {len(TEST_CASES)}\n")
            f.write(f"Tools Evaluated: 15 (7 Core + 5 High-Impact + 3 Luxury)\n")
            f.write("=" * 100 + "\n\n")
            
            # Overall performance
            overall = metrics["overall"]
            f.write("OVERALL SYSTEM PERFORMANCE:\n")
            f.write("-" * 50 + "\n")
            f.write(f"Precision: {overall['precision']:.3f} ({overall['total_tp']}/{overall['total_tp'] + overall['total_fp']})\n")
            f.write(f"Recall:    {overall['recall']:.3f} ({overall['total_tp']}/{overall['total_tp'] + overall['total_fn']})\n")
            f.write(f"F1 Score:  {overall['f1']:.3f}\n")
            f.write(f"Tests:     {overall['total_tests']}\n\n")
            
            # Per-tool performance
            f.write("PER-TOOL PERFORMANCE:\n")
            f.write("-" * 50 + "\n")
            f.write(f"{'Tool':<25} {'Precision':<10} {'Recall':<10} {'F1':<10} {'TP':<5} {'FP':<5} {'FN':<5}\n")
            f.write("-" * 80 + "\n")
            for tool, metrics_data in metrics["per_tool"].items():
                f.write(f"{tool:<25} {metrics_data['precision']:<10.3f} {metrics_data['recall']:<10.3f} "
                       f"{metrics_data['f1']:<10.3f} {metrics_data['tp']:<5} {metrics_data['fp']:<5} {metrics_data['fn']:<5}\n")
            
            # Tool tier analysis
            f.write("\nTOOL TIER ANALYSIS:\n")
            f.write("-" * 50 + "\n")
            
            core_tools = ["guest_profile", "booking_details", "property_info", "schedule_cleaning", "modify_checkout_time", "request_transport", "escalate_to_manager"]
            high_impact_tools = ["restaurant_reservation", "grocery_delivery", "maintenance_request", "activity_booking", "meal_delivery"]
            luxury_tools = ["spa_services", "private_chef", "local_recommendations"]
            
            for tier_name, tool_list in [("CORE TOOLS", core_tools), ("HIGH-IMPACT TOOLS", high_impact_tools), ("LUXURY TOOLS", luxury_tools)]:
                tier_metrics = [metrics["per_tool"][tool] for tool in tool_list if tool in metrics["per_tool"]]
                if tier_metrics:
                    avg_f1 = sum(t["f1"] for t in tier_metrics) / len(tier_metrics)
                    f.write(f"{tier_name}: Average F1 = {avg_f1:.3f} ({len(tier_metrics)} tools)\n")
            
            f.write("\n" + "=" * 100 + "\n")
            f.write("END OF COMPREHENSIVE EVALUATION REPORT\n")
            f.write("=" * 100 + "\n")
        
        logger.info(f"Comprehensive results saved to {txt_filename}")

def main():
    """Run the comprehensive tool evaluation."""
    evaluator = ComprehensiveToolEvaluator()
    
    try:
        # Test API connection
        response = requests.get("http://localhost:8000/debug/status", timeout=5)
        if response.status_code != 200:
            print("❌ API not accessible. Please ensure the server is running on http://localhost:8000")
            return
        
        print("🚀 Starting Comprehensive Tool Selection Evaluation")
        print(f"📋 Running {len(TEST_CASES)} test cases across 15 tools")
        print("=" * 80)
        
        # Run evaluation
        metrics = evaluator.run_evaluation()
        
        # Print results
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE EVALUATION RESULTS")
        print("=" * 80)
        
        overall = metrics["overall"]
        print(f"\n🎯 OVERALL PERFORMANCE:")
        print(f"   Precision: {overall['precision']:.3f} ({overall['total_tp']}/{overall['total_tp'] + overall['total_fp']})")
        print(f"   Recall:    {overall['recall']:.3f} ({overall['total_tp']}/{overall['total_tp'] + overall['total_fn']})")
        print(f"   F1 Score:  {overall['f1']:.3f}")
        print(f"   Tests:     {overall['total_tests']}")
        
        print(f"\n🔧 TOP PERFORMING TOOLS:")
        top_tools = sorted(metrics["per_tool"].items(), key=lambda x: x[1]["f1"], reverse=True)[:5]
        for tool, data in top_tools:
            print(f"   {tool:25} | F1: {data['f1']:.3f}")
        
        print(f"\n⚠️  TOOLS NEEDING IMPROVEMENT:")
        bottom_tools = sorted(metrics["per_tool"].items(), key=lambda x: x[1]["f1"])[:5]
        for tool, data in bottom_tools:
            print(f"   {tool:25} | F1: {data['f1']:.3f}")
        
        print("\n✅ Comprehensive evaluation completed!")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        print(f"📄 Results saved to comprehensive_tool_evaluation_{timestamp}.txt")
        
    except requests.RequestException:
        print("❌ Could not connect to API. Please ensure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        logger.error(f"Evaluation failed: {e}", exc_info=True)

if __name__ == "__main__":
    main()