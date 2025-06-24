"""
Tool Selection Evaluation for Omotenashi Hotel Concierge
Evaluates precision and recall of tool selection by the AI agent.

EXTENDING FOR NEW TOOLS:
========================

When adding a new tool to the system, follow these steps to update the evaluation:

1. ADD TOOL PATTERNS:
   - Update the `tool_patterns` dictionary in the ToolEvaluator class
   - Add key-value pair: "new_tool_name": ["pattern1", "pattern2", ...]
   - Patterns should be keywords/phrases that appear in responses when the tool is used

2. ADD TEST CASES:
   - Add test cases to the TEST_CASES list
   - Include both positive cases (should trigger the tool) and negative cases
   - Recommended: 10-15 test cases per tool for comprehensive coverage
   - Use format: {"id": X, "prompt": "...", "expected_tools": ["tool_name"], "category": "tool_category"}

3. CATEGORY NAMING:
   - Use consistent category names for grouping related tests
   - Examples: "new_tool", "new_tool_edge_cases", "new_tool_multi"

4. EXAMPLE - Adding a "book_restaurant" tool:

   # In tool_patterns:
   "book_restaurant": [
       "restaurant booked", "reservation confirmed", "table reserved",
       "dining reservation", "restaurant booking"
   ]

   # In TEST_CASES:
   {"id": 101, "prompt": "Can you book me a table at the hotel restaurant?", 
    "expected_tools": ["book_restaurant"], "category": "restaurant"},
   {"id": 102, "prompt": "I need a dinner reservation for 8 PM", 
    "expected_tools": ["book_restaurant"], "category": "restaurant"},

5. VALIDATION:
   - Run the evaluation after adding new tools
   - Check that detection patterns work correctly
   - Adjust patterns if false positives/negatives occur

The evaluation automatically handles new tools without code changes to the metrics calculation.
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

# Expanded test cases with 100 examples covering all tools and edge cases
TEST_CASES = [
    # GUEST PROFILE TOOL (15 cases)
    {"id": 1, "prompt": "Hi, what's my name?", "expected_tools": ["guest_profile"], "category": "guest_info"},
    {"id": 2, "prompt": "Can you tell me about my preferences?", "expected_tools": ["guest_profile"], "category": "guest_info"},
    {"id": 3, "prompt": "Am I a VIP guest?", "expected_tools": ["guest_profile"], "category": "guest_info"},
    {"id": 4, "prompt": "What language do I prefer?", "expected_tools": ["guest_profile"], "category": "guest_info"},
    {"id": 5, "prompt": "Hello, I'm new here. Can you help me?", "expected_tools": ["guest_profile"], "category": "guest_info"},
    {"id": 6, "prompt": "What are my dietary restrictions?", "expected_tools": ["guest_profile"], "category": "guest_info"},
    {"id": 7, "prompt": "Do you have my contact information?", "expected_tools": ["guest_profile"], "category": "guest_info"},
    {"id": 8, "prompt": "Can you show me my profile?", "expected_tools": ["guest_profile"], "category": "guest_info"},
    {"id": 9, "prompt": "What's my guest ID?", "expected_tools": ["guest_profile"], "category": "guest_info"},
    {"id": 10, "prompt": "Tell me about myself", "expected_tools": ["guest_profile"], "category": "guest_info"},
    {"id": 11, "prompt": "What do you know about me?", "expected_tools": ["guest_profile"], "category": "guest_info"},
    {"id": 12, "prompt": "Am I registered as a guest here?", "expected_tools": ["guest_profile"], "category": "guest_info"},
    {"id": 13, "prompt": "What's my preferred room temperature?", "expected_tools": ["guest_profile"], "category": "guest_info"},
    {"id": 14, "prompt": "Do I have any special requests on file?", "expected_tools": ["guest_profile"], "category": "guest_info"},
    {"id": 15, "prompt": "What's my guest status?", "expected_tools": ["guest_profile"], "category": "guest_info"},
    
    # BOOKING DETAILS TOOL (15 cases)
    {"id": 16, "prompt": "When do I check out?", "expected_tools": ["booking_details"], "category": "booking_info"},
    {"id": 17, "prompt": "What room am I staying in?", "expected_tools": ["booking_details"], "category": "booking_info"},
    {"id": 18, "prompt": "Can you show me my reservation details?", "expected_tools": ["booking_details"], "category": "booking_info"},
    {"id": 19, "prompt": "When is my check-in date?", "expected_tools": ["booking_details"], "category": "booking_info"},
    {"id": 20, "prompt": "What type of room did I book?", "expected_tools": ["booking_details"], "category": "booking_info"},
    {"id": 21, "prompt": "How many nights am I staying?", "expected_tools": ["booking_details"], "category": "booking_info"},
    {"id": 22, "prompt": "What's my confirmation number?", "expected_tools": ["booking_details"], "category": "booking_info"},
    {"id": 23, "prompt": "Show me my booking information", "expected_tools": ["booking_details"], "category": "booking_info"},
    {"id": 24, "prompt": "What's included in my reservation?", "expected_tools": ["booking_details"], "category": "booking_info"},
    {"id": 25, "prompt": "When did I make this reservation?", "expected_tools": ["booking_details"], "category": "booking_info"},
    {"id": 26, "prompt": "What's my room number?", "expected_tools": ["booking_details"], "category": "booking_info"},
    {"id": 27, "prompt": "How much did I pay for this room?", "expected_tools": ["booking_details"], "category": "booking_info"},
    {"id": 28, "prompt": "What's my arrival time?", "expected_tools": ["booking_details"], "category": "booking_info"},
    {"id": 29, "prompt": "What's my departure date?", "expected_tools": ["booking_details"], "category": "booking_info"},
    {"id": 30, "prompt": "Can you pull up my reservation?", "expected_tools": ["booking_details"], "category": "booking_info"},
    
    # PROPERTY INFO TOOL (15 cases)
    {"id": 31, "prompt": "What's the WiFi password?", "expected_tools": ["property_info"], "category": "property_info"},
    {"id": 32, "prompt": "What time does the pool open?", "expected_tools": ["property_info"], "category": "property_info"},
    {"id": 33, "prompt": "Do you have a gym?", "expected_tools": ["property_info"], "category": "property_info"},
    {"id": 34, "prompt": "What restaurants are nearby?", "expected_tools": ["property_info"], "category": "property_info"},
    {"id": 35, "prompt": "Tell me about the hotel amenities", "expected_tools": ["property_info"], "category": "property_info"},
    {"id": 36, "prompt": "What services do you offer?", "expected_tools": ["property_info"], "category": "property_info"},
    {"id": 37, "prompt": "Where is the spa located?", "expected_tools": ["property_info"], "category": "property_info"},
    {"id": 38, "prompt": "Can you tell me about the hotel facilities?", "expected_tools": ["property_info"], "category": "property_info"},
    {"id": 39, "prompt": "What's the breakfast schedule?", "expected_tools": ["property_info"], "category": "property_info"},
    {"id": 40, "prompt": "Do you have room service?", "expected_tools": ["property_info"], "category": "property_info"},
    {"id": 41, "prompt": "Where's the business center?", "expected_tools": ["property_info"], "category": "property_info"},
    {"id": 42, "prompt": "What are your pool hours?", "expected_tools": ["property_info"], "category": "property_info"},
    {"id": 43, "prompt": "Do you have a concierge desk?", "expected_tools": ["property_info"], "category": "property_info"},
    {"id": 44, "prompt": "What's the parking situation?", "expected_tools": ["property_info"], "category": "property_info"},
    {"id": 45, "prompt": "Tell me about your fitness center", "expected_tools": ["property_info"], "category": "property_info"},
    
    # SCHEDULE CLEANING TOOL (15 cases)
    {"id": 46, "prompt": "Can you clean my room tomorrow at 2 PM?", "expected_tools": ["schedule_cleaning"], "category": "cleaning"},
    {"id": 47, "prompt": "I need housekeeping service on Friday at 11:00 AM", "expected_tools": ["schedule_cleaning"], "category": "cleaning"},
    {"id": 48, "prompt": "Please schedule room cleaning for today at 3:30 PM", "expected_tools": ["schedule_cleaning"], "category": "cleaning"},
    {"id": 49, "prompt": "Can you arrange cleaning service for Monday morning at 10 AM?", "expected_tools": ["schedule_cleaning"], "category": "cleaning"},
    {"id": 50, "prompt": "I'd like room service cleaning tomorrow at 1:00 PM", "expected_tools": ["schedule_cleaning"], "category": "cleaning"},
    {"id": 51, "prompt": "Schedule housekeeping for Wednesday at 9:30 AM", "expected_tools": ["schedule_cleaning"], "category": "cleaning"},
    {"id": 52, "prompt": "Can you clean my room on Thursday at 4:00 PM?", "expected_tools": ["schedule_cleaning"], "category": "cleaning"},
    {"id": 53, "prompt": "I need cleaning service tomorrow at 12:30 PM", "expected_tools": ["schedule_cleaning"], "category": "cleaning"},
    {"id": 54, "prompt": "Please arrange housekeeping for Sunday at 10:15 AM", "expected_tools": ["schedule_cleaning"], "category": "cleaning"},
    {"id": 55, "prompt": "Book room cleaning for next Tuesday at 2:45 PM", "expected_tools": ["schedule_cleaning"], "category": "cleaning"},
    {"id": 56, "prompt": "Can you get someone to clean my room this afternoon?", "expected_tools": [], "category": "cleaning_vague"},
    {"id": 57, "prompt": "I need cleaning tomorrow morning", "expected_tools": [], "category": "cleaning_vague"},
    {"id": 58, "prompt": "Schedule housekeeping for later today", "expected_tools": [], "category": "cleaning_vague"},
    {"id": 59, "prompt": "Can you clean my room sometime tomorrow?", "expected_tools": [], "category": "cleaning_vague"},
    {"id": 60, "prompt": "I need housekeeping in the evening", "expected_tools": [], "category": "cleaning_vague"},
    
    # MODIFY CHECKOUT TOOL (10 cases)
    {"id": 61, "prompt": "Can I change my checkout to 3 PM?", "expected_tools": ["modify_checkout_time"], "category": "checkout"},
    {"id": 62, "prompt": "I need to extend my checkout until 2:00 PM", "expected_tools": ["modify_checkout_time"], "category": "checkout"},
    {"id": 63, "prompt": "Can you give me a late checkout at 1 PM?", "expected_tools": ["modify_checkout_time"], "category": "checkout"},
    {"id": 64, "prompt": "I want to check out at noon instead of 11 AM", "expected_tools": ["modify_checkout_time"], "category": "checkout"},
    {"id": 65, "prompt": "Please change my departure time to 4:00 PM", "expected_tools": ["modify_checkout_time"], "category": "checkout"},
    {"id": 66, "prompt": "Can I get a late checkout until 5 PM?", "expected_tools": ["modify_checkout_time"], "category": "checkout"},
    {"id": 67, "prompt": "I need to modify my checkout time to 1:30 PM", "expected_tools": ["modify_checkout_time"], "category": "checkout"},
    {"id": 68, "prompt": "Can you extend my stay until 6 PM checkout?", "expected_tools": ["modify_checkout_time"], "category": "checkout"},
    {"id": 69, "prompt": "Change my checkout from 11 AM to 2 PM please", "expected_tools": ["modify_checkout_time"], "category": "checkout"},
    {"id": 70, "prompt": "I want to leave later, can you change my checkout?", "expected_tools": ["modify_checkout_time"], "category": "checkout"},
    
    # TRANSPORT REQUEST TOOL (10 cases)
    {"id": 71, "prompt": "Can you get me a ride to SFO airport at 6 AM?", "expected_tools": ["request_transport"], "category": "transport"},
    {"id": 72, "prompt": "I need transportation to LAX tomorrow at 3:30 PM", "expected_tools": ["request_transport"], "category": "transport"},
    {"id": 73, "prompt": "Please arrange a car to the airport at 8:00 AM", "expected_tools": ["request_transport"], "category": "transport"},
    {"id": 74, "prompt": "Can you book airport transport for 5:45 AM to JFK?", "expected_tools": ["request_transport"], "category": "transport"},
    {"id": 75, "prompt": "I need a taxi to Oakland airport at 7 PM", "expected_tools": ["request_transport"], "category": "transport"},
    {"id": 76, "prompt": "Book me a car to SFO at 9:30 AM tomorrow", "expected_tools": ["request_transport"], "category": "transport"},
    {"id": 77, "prompt": "Can you arrange airport pickup at 4:15 PM to LAX?", "expected_tools": ["request_transport"], "category": "transport"},
    {"id": 78, "prompt": "I need transport to the airport at 6:45 AM", "expected_tools": ["request_transport"], "category": "transport"},
    {"id": 79, "prompt": "Please get me a ride to JFK at 2:30 PM", "expected_tools": ["request_transport"], "category": "transport"},
    {"id": 80, "prompt": "Can you call a taxi for airport transfer at 5 AM?", "expected_tools": ["request_transport"], "category": "transport"},
    
    # ESCALATION TOOL (10 cases)
    {"id": 81, "prompt": "Can you book me a helicopter tour?", "expected_tools": ["escalate_to_manager"], "category": "escalation"},
    {"id": 82, "prompt": "I want to rent a yacht for tomorrow", "expected_tools": ["escalate_to_manager"], "category": "escalation"},
    {"id": 83, "prompt": "Can you arrange a private chef for dinner?", "expected_tools": ["escalate_to_manager"], "category": "escalation"},
    {"id": 84, "prompt": "I need a massage therapist to come to my room", "expected_tools": ["escalate_to_manager"], "category": "escalation"},
    {"id": 85, "prompt": "Can you organize a wine tasting experience?", "expected_tools": ["escalate_to_manager"], "category": "escalation"},
    {"id": 86, "prompt": "I want to book a limousine for a city tour", "expected_tools": ["escalate_to_manager"], "category": "escalation"},
    {"id": 87, "prompt": "Can you arrange a private jet charter?", "expected_tools": ["escalate_to_manager"], "category": "escalation"},
    {"id": 88, "prompt": "I need a personal shopping assistant", "expected_tools": ["escalate_to_manager"], "category": "escalation"},
    {"id": 89, "prompt": "Can you book tickets to a Broadway show?", "expected_tools": ["escalate_to_manager"], "category": "escalation"},
    {"id": 90, "prompt": "I want to arrange a private dining experience", "expected_tools": ["escalate_to_manager"], "category": "escalation"},
    
    # MULTI-TOOL SCENARIOS (5 cases)
    {"id": 91, "prompt": "What time do I check out and can you get me transport to SFO at 2 PM?", "expected_tools": ["booking_details", "request_transport"], "category": "multi_tool"},
    {"id": 92, "prompt": "Can you tell me my room details and schedule cleaning for tomorrow at 11 AM?", "expected_tools": ["booking_details", "schedule_cleaning"], "category": "multi_tool"},
    {"id": 93, "prompt": "What's my name and when is my checkout time?", "expected_tools": ["guest_profile", "booking_details"], "category": "multi_tool"},
    {"id": 94, "prompt": "Show me my booking details and what are the hotel amenities?", "expected_tools": ["booking_details", "property_info"], "category": "multi_tool"},
    {"id": 95, "prompt": "I need to change checkout to 3 PM and book transport to LAX at 4 PM", "expected_tools": ["modify_checkout_time", "request_transport"], "category": "multi_tool"},
    
    # NO TOOL SCENARIOS (5 cases)
    {"id": 96, "prompt": "Thank you for your help!", "expected_tools": [], "category": "no_tool"},
    {"id": 97, "prompt": "How are you doing today?", "expected_tools": [], "category": "no_tool"},
    {"id": 98, "prompt": "That sounds great, thanks!", "expected_tools": [], "category": "no_tool"},
    {"id": 99, "prompt": "Good morning!", "expected_tools": [], "category": "no_tool"},
    {"id": 100, "prompt": "Have a nice day!", "expected_tools": [], "category": "no_tool"}
]

class ToolEvaluator:
    """Evaluates tool selection performance of the AI concierge agent."""
    
    def __init__(self, api_base_url: str = "http://localhost:8000", test_phone: str = "+14155550123"):
        self.api_base_url = api_base_url
        self.test_phone = test_phone
        self.results = []
        
        # Tool detection patterns - easily extensible for new tools
        self.tool_patterns = {
            "guest_profile": [
                "your name is", "you are", "your preferences", "vip status", 
                "guest id", "dietary restrictions", "contact information",
                "profile", "guest status", "special requests", "preferred"
            ],
            "booking_details": [
                "check out", "check-out", "reservation", "booking", "room type",
                "confirmation", "nights", "room number", "arrival", "departure"
            ],
            "schedule_cleaning": [
                "cleaning scheduled", "housekeeping", "cleaning team", 
                "room cleaning", "cleaning service", "housekeeping service"
            ],
            "modify_checkout_time": [
                "checkout time", "checkout updated", "departure time",
                "late checkout", "extend", "checkout changed", "modified"
            ],
            "request_transport": [
                "transport requested", "airport transport", "pickup",
                "taxi", "car", "ride", "transportation arranged"
            ],
            "property_info": [
                "wifi", "pool", "gym", "amenities", "facilities", "restaurant",
                "spa", "business center", "parking", "fitness", "breakfast",
                "room service", "concierge", "services"
            ],
            "escalate_to_manager": [
                "escalated", "property manager", "get back to you",
                "escalation", "manager", "forwarded"
            ]
        }
    
    def extract_tools_from_response(self, response_text: str) -> List[str]:
        """Extract tool names from agent response using improved pattern matching."""
        tools_called = []
        response_lower = response_text.lower()
        
        for tool_name, patterns in self.tool_patterns.items():
            if any(pattern in response_lower for pattern in patterns):
                tools_called.append(tool_name)
        
        return list(set(tools_called))  # Remove duplicates
    
    def send_message(self, message: str) -> Tuple[str, bool]:
        """Send a message to the API and get response."""
        try:
            payload = {"message": message, "phone_number": self.test_phone}
            response = requests.post(f"{self.api_base_url}/message", json=payload, timeout=30)
            
            if response.status_code == 200:
                return response.json()["response"], True
            else:
                logger.error(f"API error {response.status_code}: {response.text}")
                return f"API Error: {response.status_code}", False
                
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return f"Request failed: {e}", False
    
    def clear_session(self):
        """Clear the conversation session."""
        try:
            requests.delete(f"{self.api_base_url}/session/{self.test_phone}")
        except:
            pass  # Ignore errors
    
    def evaluate_test_case(self, test_case: Dict) -> Dict:
        """Evaluate a single test case."""
        logger.info(f"Testing case {test_case['id']}: {test_case['prompt']}")
        
        response, success = self.send_message(test_case["prompt"])
        actual_tools = self.extract_tools_from_response(response) if success else []
        
        result = {
            "test_id": test_case["id"],
            "prompt": test_case["prompt"],
            "expected_tools": test_case["expected_tools"],
            "actual_tools": actual_tools,
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
    
    def run_evaluation(self) -> Dict:
        """Run the complete evaluation."""
        logger.info(f"Starting evaluation with {len(TEST_CASES)} test cases")
        
        # Clear session to start fresh
        self.clear_session()
        
        # Run each test case
        for i, test_case in enumerate(TEST_CASES):
            result = self.evaluate_test_case(test_case)
            self.results.append(result)
            
            # Small delay to avoid overwhelming the API
            time.sleep(0.3)  # Reduced delay for 100 tests
            
            # Progress update
            if (i + 1) % 20 == 0:
                logger.info(f"Completed {i + 1}/{len(TEST_CASES)} test cases")
        
        # Calculate metrics
        metrics = self.calculate_metrics()
        
        # Save results
        self.save_results(metrics)
        
        return metrics
    
    def save_results(self, metrics: Dict):
        """Save detailed results to files."""
        today = datetime.now().strftime("%Y-%m-%d")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed JSON results
        with open(f"evaluation_results_{timestamp}.json", "w") as f:
            json.dump({
                "metrics": metrics,
                "detailed_results": self.results,
                "test_cases": TEST_CASES
            }, f, indent=2)
        
        # Save formatted TXT results
        txt_filename = f"tool_evaluation_results_{today}.txt"
        with open(txt_filename, "w") as f:
            f.write("=" * 80 + "\n")
            f.write("OMOTENASHI CONCIERGE TOOL SELECTION EVALUATION REPORT\n")
            f.write(f"Date: {today}\n")
            f.write(f"Test Cases: {len(TEST_CASES)}\n")
            f.write("=" * 80 + "\n\n")
            
            # Overall performance
            overall = metrics["overall"]
            f.write("OVERALL PERFORMANCE:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Precision: {overall['precision']:.3f} ({overall['total_tp']}/{overall['total_tp'] + overall['total_fp']})\n")
            f.write(f"Recall:    {overall['recall']:.3f} ({overall['total_tp']}/{overall['total_tp'] + overall['total_fn']})\n")
            f.write(f"F1 Score:  {overall['f1']:.3f}\n")
            f.write(f"Tests:     {overall['total_tests']}\n\n")
            
            # Per-tool performance
            f.write("PER-TOOL PERFORMANCE:\n")
            f.write("-" * 40 + "\n")
            f.write(f"{'Tool':<25} {'Precision':<10} {'Recall':<10} {'F1':<10} {'TP':<5} {'FP':<5} {'FN':<5}\n")
            f.write("-" * 80 + "\n")
            for tool, metrics_data in metrics["per_tool"].items():
                f.write(f"{tool:<25} {metrics_data['precision']:<10.3f} {metrics_data['recall']:<10.3f} "
                       f"{metrics_data['f1']:<10.3f} {metrics_data['tp']:<5} {metrics_data['fp']:<5} {metrics_data['fn']:<5}\n")
            
            # Per-category performance
            f.write("\nPER-CATEGORY PERFORMANCE:\n")
            f.write("-" * 40 + "\n")
            f.write(f"{'Category':<20} {'Precision':<10} {'Recall':<10} {'F1':<10} {'Tests':<6}\n")
            f.write("-" * 70 + "\n")
            for category, metrics_data in metrics["per_category"].items():
                f.write(f"{category:<20} {metrics_data['precision']:<10.3f} {metrics_data['recall']:<10.3f} "
                       f"{metrics_data['f1']:<10.3f} {metrics_data['test_count']:<6}\n")
            
            # Detailed test results
            f.write("\nDETAILED TEST RESULTS:\n")
            f.write("-" * 40 + "\n")
            for result in self.results:
                if result["success"]:
                    expected_str = ", ".join(result["expected_tools"]) if result["expected_tools"] else "None"
                    actual_str = ", ".join(result["actual_tools"]) if result["actual_tools"] else "None"
                    match = "✓" if set(result["expected_tools"]) == set(result["actual_tools"]) else "✗"
                    f.write(f"Test {result['test_id']:3d} {match} | Expected: {expected_str:<30} | Actual: {actual_str:<30} | {result['category']}\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 80 + "\n")
        
        logger.info(f"Results saved to {txt_filename} and evaluation_results_{timestamp}.json")

def main():
    """Run the tool evaluation."""
    evaluator = ToolEvaluator()
    
    try:
        # Test API connection
        response = requests.get("http://localhost:8000/debug/status", timeout=5)
        if response.status_code != 200:
            print("❌ API not accessible. Please ensure the server is running on http://localhost:8000")
            return
        
        print("🚀 Starting Tool Selection Evaluation")
        print(f"📋 Running {len(TEST_CASES)} test cases")
        print("=" * 60)
        
        metrics = evaluator.run_evaluation()
        
        # Print results
        print("\n" + "=" * 60)
        print("📊 EVALUATION RESULTS")
        print("=" * 60)
        
        overall = metrics["overall"]
        print(f"\n🎯 OVERALL PERFORMANCE:")
        print(f"   Precision: {overall['precision']:.3f} ({overall['total_tp']}/{overall['total_tp'] + overall['total_fp']})")
        print(f"   Recall:    {overall['recall']:.3f} ({overall['total_tp']}/{overall['total_tp'] + overall['total_fn']})")
        print(f"   F1 Score:  {overall['f1']:.3f}")
        print(f"   Tests:     {overall['total_tests']}")
        
        print(f"\n🔧 PER-TOOL PERFORMANCE:")
        for tool, metrics_data in metrics["per_tool"].items():
            print(f"   {tool:20} | P: {metrics_data['precision']:.3f} | R: {metrics_data['recall']:.3f} | F1: {metrics_data['f1']:.3f}")
        
        print(f"\n📂 PER-CATEGORY PERFORMANCE:")
        for category, metrics_data in metrics["per_category"].items():
            print(f"   {category:20} | P: {metrics_data['precision']:.3f} | R: {metrics_data['recall']:.3f} | F1: {metrics_data['f1']:.3f} | Tests: {metrics_data['test_count']}")
        
        print("\n✅ Evaluation completed successfully!")
        today = datetime.now().strftime("%Y-%m-%d")
        print(f"📄 Results saved to tool_evaluation_results_{today}.txt")
        
    except requests.RequestException:
        print("❌ Could not connect to API. Please ensure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        logger.error(f"Evaluation failed: {e}", exc_info=True)

if __name__ == "__main__":
    main() 