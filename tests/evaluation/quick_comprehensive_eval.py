#!/usr/bin/env python3
"""
Quick Comprehensive Tool Selection Evaluation (30 cases across all 15 tools)
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

# QUICK TEST CASES (30 cases - 2 per tool)
QUICK_TEST_CASES = [
    # CORE TOOLS (14 cases - 2 per tool)
    {"id": 1, "prompt": "Hi, what's my name?", "expected_tools": ["guest_profile"], "category": "guest_info"},
    {"id": 2, "prompt": "Am I a VIP guest?", "expected_tools": ["guest_profile"], "category": "guest_info"},
    
    {"id": 3, "prompt": "When do I check out?", "expected_tools": ["booking_details"], "category": "booking_info"},
    {"id": 4, "prompt": "What room am I staying in?", "expected_tools": ["booking_details"], "category": "booking_info"},
    
    {"id": 5, "prompt": "What's the WiFi password?", "expected_tools": ["property_info"], "category": "property_info"},
    {"id": 6, "prompt": "Do you have a gym?", "expected_tools": ["property_info"], "category": "property_info"},
    
    {"id": 7, "prompt": "Can you clean my room tomorrow at 2 PM?", "expected_tools": ["schedule_cleaning"], "category": "cleaning"},
    {"id": 8, "prompt": "I need housekeeping service on Friday at 11:00 AM", "expected_tools": ["schedule_cleaning"], "category": "cleaning"},
    
    {"id": 9, "prompt": "Can I change my checkout to 3 PM?", "expected_tools": ["modify_checkout_time"], "category": "checkout"},
    {"id": 10, "prompt": "I need to extend my checkout until 2:00 PM", "expected_tools": ["modify_checkout_time"], "category": "checkout"},
    
    {"id": 11, "prompt": "Can you get me a ride to SFO airport at 6 AM?", "expected_tools": ["request_transport"], "category": "transport"},
    {"id": 12, "prompt": "I need transportation to LAX tomorrow at 3:30 PM", "expected_tools": ["request_transport"], "category": "transport"},
    
    {"id": 13, "prompt": "Can you book me a helicopter tour?", "expected_tools": ["escalate_to_manager"], "category": "escalation"},
    {"id": 14, "prompt": "I want to rent a yacht for tomorrow", "expected_tools": ["escalate_to_manager"], "category": "escalation"},
    
    # HIGH-IMPACT TOOLS (10 cases - 2 per tool)
    {"id": 15, "prompt": "Can you book me dinner at a nice Italian restaurant tonight?", "expected_tools": ["restaurant_reservation"], "category": "dining"},
    {"id": 16, "prompt": "I need a table for 4 at a good seafood place tomorrow at 7 PM", "expected_tools": ["restaurant_reservation"], "category": "dining"},
    
    {"id": 17, "prompt": "Can you stock some wine and snacks before I arrive?", "expected_tools": ["grocery_delivery"], "category": "groceries"},
    {"id": 18, "prompt": "I need groceries delivered - milk, bread, and fruit", "expected_tools": ["grocery_delivery"], "category": "groceries"},
    
    {"id": 19, "prompt": "The air conditioning isn't working in the master bedroom", "expected_tools": ["maintenance_request"], "category": "maintenance"},
    {"id": 20, "prompt": "The WiFi is really slow throughout the house", "expected_tools": ["maintenance_request"], "category": "maintenance"},
    
    {"id": 21, "prompt": "Can you book us a wine tour for tomorrow?", "expected_tools": ["activity_booking"], "category": "activities"},
    {"id": 22, "prompt": "I want to book a sunset boat cruise for 4 people", "expected_tools": ["activity_booking"], "category": "activities"},
    
    {"id": 23, "prompt": "Can you order Chinese food for delivery tonight?", "expected_tools": ["meal_delivery"], "category": "food_delivery"},
    {"id": 24, "prompt": "I'm hungry now - can you get pizza delivered?", "expected_tools": ["meal_delivery"], "category": "food_delivery"},
    
    # LUXURY TOOLS (6 cases - 2 per tool)
    {"id": 25, "prompt": "Can you book a massage therapist to come to the villa?", "expected_tools": ["spa_services"], "category": "wellness"},
    {"id": 26, "prompt": "I need a couples massage for this afternoon", "expected_tools": ["spa_services"], "category": "wellness"},
    
    {"id": 27, "prompt": "Can you arrange a private chef for dinner tonight?", "expected_tools": ["private_chef"], "category": "private_dining"},
    {"id": 28, "prompt": "I want a chef to cook breakfast for 6 people tomorrow", "expected_tools": ["private_chef"], "category": "private_dining"},
    
    {"id": 29, "prompt": "What are the best restaurants in the area?", "expected_tools": ["local_recommendations"], "category": "recommendations"},
    {"id": 30, "prompt": "Can you recommend fun activities for kids?", "expected_tools": ["local_recommendations"], "category": "recommendations"},
]

class QuickComprehensiveEvaluator:
    """Quick evaluator for all 15 tools."""
    
    def __init__(self, api_base_url: str = "http://localhost:8000", test_phone: str = "+14155550123"):
        self.api_base_url = api_base_url
        self.test_phone = test_phone
        self.results = []
        
        # Tool detection patterns
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
        
        return list(set(tools_called))
    
    def send_message(self, message: str) -> Tuple[str, bool, List[str]]:
        """Send a message to the API and get response with tool information."""
        try:
            payload = {"message": message, "phone_number": self.test_phone}
            response = requests.post(f"{self.api_base_url}/message", json=payload, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                return data["response"], True, data.get("tools_used", [])
            else:
                logger.error(f"API error {response.status_code}: {response.text}")
                return f"API Error: {response.status_code}", False, []
                
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return f"Request failed: {e}", False, []
    
    def evaluate_test_case(self, test_case: Dict) -> Dict:
        """Evaluate a single test case."""
        logger.info(f"Testing case {test_case['id']}: {test_case['prompt']}")
        
        response, success, api_tools = self.send_message(test_case["prompt"])
        pattern_tools = self.extract_tools_from_response(response) if success else []
        actual_tools = list(set(api_tools + pattern_tools))
        
        result = {
            "test_id": test_case["id"],
            "prompt": test_case["prompt"],
            "expected_tools": test_case["expected_tools"],
            "actual_tools": actual_tools,
            "api_tools": api_tools,
            "pattern_tools": pattern_tools,
            "response": response[:100] + "..." if len(response) > 100 else response,
            "success": success,
            "category": test_case["category"]
        }
        
        # Calculate match status
        expected_set = set(test_case["expected_tools"])
        actual_set = set(actual_tools)
        
        precision_ok = len(actual_set - expected_set) == 0  # No extra tools
        recall_ok = len(expected_set - actual_set) == 0     # Found all expected
        perfect_match = precision_ok and recall_ok
        
        result.update({
            "precision_ok": precision_ok,
            "recall_ok": recall_ok,
            "perfect_match": perfect_match
        })
        
        status = "✅" if perfect_match else "❌"
        logger.info(f"  {status} Expected: {test_case['expected_tools']} | Got: {actual_tools}")
        
        return result
    
    def calculate_summary_metrics(self) -> Dict:
        """Calculate summary metrics."""
        successful_tests = [r for r in self.results if r["success"]]
        
        if not successful_tests:
            return {"error": "No successful tests"}
        
        total_tests = len(successful_tests)
        perfect_matches = sum(1 for r in successful_tests if r["perfect_match"])
        precision_success = sum(1 for r in successful_tests if r["precision_ok"])
        recall_success = sum(1 for r in successful_tests if r["recall_ok"])
        
        # Per-tool analysis
        tool_results = {}
        all_tools = set()
        for result in successful_tests:
            all_tools.update(result["expected_tools"])
            all_tools.update(result["actual_tools"])
        
        for tool in all_tools:
            tool_tests = [r for r in successful_tests if tool in r["expected_tools"]]
            if tool_tests:
                perfect = sum(1 for r in tool_tests if r["perfect_match"])
                tool_results[tool] = {
                    "tests": len(tool_tests),
                    "perfect": perfect,
                    "success_rate": perfect / len(tool_tests) if tool_tests else 0
                }
        
        return {
            "overall": {
                "total_tests": total_tests,
                "perfect_matches": perfect_matches,
                "precision_success": precision_success,
                "recall_success": recall_success,
                "perfect_rate": perfect_matches / total_tests,
                "precision_rate": precision_success / total_tests,
                "recall_rate": recall_success / total_tests
            },
            "per_tool": tool_results
        }
    
    def run_evaluation(self) -> Dict:
        """Run the quick evaluation."""
        logger.info(f"Starting quick comprehensive evaluation with {len(QUICK_TEST_CASES)} test cases")
        
        # Run each test case
        for i, test_case in enumerate(QUICK_TEST_CASES):
            result = self.evaluate_test_case(test_case)
            self.results.append(result)
            time.sleep(0.5)  # Small delay
            
            if (i + 1) % 10 == 0:
                logger.info(f"Completed {i + 1}/{len(QUICK_TEST_CASES)} test cases")
        
        return self.calculate_summary_metrics()

def main():
    """Run the quick comprehensive evaluation."""
    evaluator = QuickComprehensiveEvaluator()
    
    try:
        # Test connection
        response = requests.get("http://localhost:8000/debug/status", timeout=5)
        if response.status_code != 200:
            print("❌ API not accessible. Please ensure the server is running")
            return
            
        print("🚀 Quick Comprehensive Tool Evaluation (All 15 Tools)")
        print(f"📋 Testing {len(QUICK_TEST_CASES)} cases (2 per tool)")
        print("=" * 70)
        
        metrics = evaluator.run_evaluation()
        
        if "error" in metrics:
            print(f"❌ {metrics['error']}")
            return
        
        # Print results
        print("\n" + "=" * 70)
        print("📊 QUICK COMPREHENSIVE RESULTS")
        print("=" * 70)
        
        overall = metrics["overall"]
        print(f"\n🎯 OVERALL PERFORMANCE:")
        print(f"   Perfect Matches: {overall['perfect_matches']}/{overall['total_tests']} ({overall['perfect_rate']:.1%})")
        print(f"   Precision Rate:  {overall['precision_success']}/{overall['total_tests']} ({overall['precision_rate']:.1%})")
        print(f"   Recall Rate:     {overall['recall_success']}/{overall['total_tests']} ({overall['recall_rate']:.1%})")
        
        print(f"\n🔧 TOOL PERFORMANCE BREAKDOWN:")
        print(f"{'Tool':<25} {'Tests':<6} {'Perfect':<8} {'Rate':<8}")
        print("-" * 50)
        
        # Group by tool tier
        core_tools = ["guest_profile", "booking_details", "property_info", "schedule_cleaning", "modify_checkout_time", "request_transport", "escalate_to_manager"]
        high_impact_tools = ["restaurant_reservation", "grocery_delivery", "maintenance_request", "activity_booking", "meal_delivery"]
        luxury_tools = ["spa_services", "private_chef", "local_recommendations"]
        
        for tier_name, tool_list in [("CORE", core_tools), ("HIGH-IMPACT", high_impact_tools), ("LUXURY", luxury_tools)]:
            print(f"\n{tier_name} TOOLS:")
            tier_perfect = 0
            tier_total = 0
            
            for tool in tool_list:
                if tool in metrics["per_tool"]:
                    data = metrics["per_tool"][tool]
                    print(f"  {tool:<23} {data['tests']:<6} {data['perfect']:<8} {data['success_rate']:.1%}")
                    tier_perfect += data['perfect']
                    tier_total += data['tests']
            
            if tier_total > 0:
                print(f"  {tier_name} TIER AVERAGE: {tier_perfect}/{tier_total} ({tier_perfect/tier_total:.1%})")
        
        # Show failures for improvement
        failures = [r for r in evaluator.results if r["success"] and not r["perfect_match"]]
        if failures:
            print(f"\n⚠️  IMPROVEMENT OPPORTUNITIES ({len(failures)} cases):")
            for failure in failures[:5]:  # Show top 5
                print(f"   Test {failure['test_id']}: Expected {failure['expected_tools']} → Got {failure['actual_tools']}")
        
        print(f"\n✅ Quick evaluation completed!")
        
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")

if __name__ == "__main__":
    main()