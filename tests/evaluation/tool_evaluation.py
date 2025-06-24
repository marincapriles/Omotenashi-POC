"""
Tool Selection Evaluation for Omotenashi Hotel Concierge
Evaluates precision and recall of tool selection by the AI agent.
"""

import json
import logging
import os
import requests
import time
from typing import Dict, List, Set, Tuple
from datetime import datetime
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test cases with ground truth tool selections
TEST_CASES = [
    # GUEST PROFILE TOOL (5 cases)
    {
        "id": 1,
        "prompt": "Hi, what's my name?",
        "expected_tools": ["guest_profile"],
        "category": "guest_info"
    },
    {
        "id": 2,
        "prompt": "Can you tell me about my preferences?",
        "expected_tools": ["guest_profile"],
        "category": "guest_info"
    },
    {
        "id": 3,
        "prompt": "Am I a VIP guest?",
        "expected_tools": ["guest_profile"],
        "category": "guest_info"
    },
    {
        "id": 4,
        "prompt": "What language do I prefer?",
        "expected_tools": ["guest_profile"],
        "category": "guest_info"
    },
    {
        "id": 5,
        "prompt": "Hello, I'm new here. Can you help me?",
        "expected_tools": ["guest_profile"],
        "category": "guest_info"
    },
    
    # BOOKING DETAILS TOOL (5 cases)
    {
        "id": 6,
        "prompt": "When do I check out?",
        "expected_tools": ["booking_details"],
        "category": "booking_info"
    },
    {
        "id": 7,
        "prompt": "What room am I staying in?",
        "expected_tools": ["booking_details"],
        "category": "booking_info"
    },
    {
        "id": 8,
        "prompt": "Can you show me my reservation details?",
        "expected_tools": ["booking_details"],
        "category": "booking_info"
    },
    {
        "id": 9,
        "prompt": "When is my check-in date?",
        "expected_tools": ["booking_details"],
        "category": "booking_info"
    },
    {
        "id": 10,
        "prompt": "What type of room did I book?",
        "expected_tools": ["booking_details"],
        "category": "booking_info"
    },
    
    # PROPERTY INFO TOOL (8 cases)
    {
        "id": 11,
        "prompt": "What's the WiFi password?",
        "expected_tools": ["property_info"],
        "category": "property_info"
    },
    {
        "id": 12,
        "prompt": "What time does the pool open?",
        "expected_tools": ["property_info"],
        "category": "property_info"
    },
    {
        "id": 13,
        "prompt": "Do you have a gym?",
        "expected_tools": ["property_info"],
        "category": "property_info"
    },
    {
        "id": 14,
        "prompt": "What restaurants are nearby?",
        "expected_tools": ["property_info"],
        "category": "property_info"
    },
    {
        "id": 15,
        "prompt": "Tell me about the hotel amenities",
        "expected_tools": ["property_info"],
        "category": "property_info"
    },
    {
        "id": 16,
        "prompt": "What services do you offer?",
        "expected_tools": ["property_info"],
        "category": "property_info"
    },
    {
        "id": 17,
        "prompt": "Where is the spa located?",
        "expected_tools": ["property_info"],
        "category": "property_info"
    },
    {
        "id": 18,
        "prompt": "Can you tell me about the hotel facilities?",
        "expected_tools": ["property_info"],
        "category": "property_info"
    },
    
    # SCHEDULE CLEANING TOOL (8 cases)
    {
        "id": 19,
        "prompt": "Can you clean my room tomorrow at 2 PM?",
        "expected_tools": ["schedule_cleaning"],
        "category": "cleaning"
    },
    {
        "id": 20,
        "prompt": "I need housekeeping service on Friday at 11:00 AM",
        "expected_tools": ["schedule_cleaning"],
        "category": "cleaning"
    },
    {
        "id": 21,
        "prompt": "Please schedule room cleaning for today at 3:30 PM",
        "expected_tools": ["schedule_cleaning"],
        "category": "cleaning"
    },
    {
        "id": 22,
        "prompt": "Can you arrange cleaning service for Monday morning at 10 AM?",
        "expected_tools": ["schedule_cleaning"],
        "category": "cleaning"
    },
    {
        "id": 23,
        "prompt": "I'd like room service cleaning tomorrow at 1:00 PM",
        "expected_tools": ["schedule_cleaning"],
        "category": "cleaning"
    },
    {
        "id": 24,
        "prompt": "Can you get someone to clean my room this afternoon?",
        "expected_tools": [],  # Should ask for specific time
        "category": "cleaning_vague"
    },
    {
        "id": 25,
        "prompt": "I need cleaning tomorrow morning",
        "expected_tools": [],  # Should ask for specific time
        "category": "cleaning_vague"
    },
    {
        "id": 26,
        "prompt": "Schedule housekeeping for later today",
        "expected_tools": [],  # Should ask for specific time
        "category": "cleaning_vague"
    },
    
    # MODIFY CHECKOUT TOOL (5 cases)
    {
        "id": 27,
        "prompt": "Can I change my checkout to 3 PM?",
        "expected_tools": ["modify_checkout_time"],
        "category": "checkout"
    },
    {
        "id": 28,
        "prompt": "I need to extend my checkout until 2:00 PM",
        "expected_tools": ["modify_checkout_time"],
        "category": "checkout"
    },
    {
        "id": 29,
        "prompt": "Can you give me a late checkout at 1 PM?",
        "expected_tools": ["modify_checkout_time"],
        "category": "checkout"
    },
    {
        "id": 30,
        "prompt": "I want to check out at noon instead of 11 AM",
        "expected_tools": ["modify_checkout_time"],
        "category": "checkout"
    },
    {
        "id": 31,
        "prompt": "Please change my departure time to 4:00 PM",
        "expected_tools": ["modify_checkout_time"],
        "category": "checkout"
    },
    
    # TRANSPORT REQUEST TOOL (5 cases)
    {
        "id": 32,
        "prompt": "Can you get me a ride to SFO airport at 6 AM?",
        "expected_tools": ["request_transport"],
        "category": "transport"
    },
    {
        "id": 33,
        "prompt": "I need transportation to LAX tomorrow at 3:30 PM",
        "expected_tools": ["request_transport"],
        "category": "transport"
    },
    {
        "id": 34,
        "prompt": "Please arrange a car to the airport at 8:00 AM",
        "expected_tools": ["request_transport"],
        "category": "transport"
    },
    {
        "id": 35,
        "prompt": "Can you book airport transport for 5:45 AM to JFK?",
        "expected_tools": ["request_transport"],
        "category": "transport"
    },
    {
        "id": 36,
        "prompt": "I need a taxi to Oakland airport at 7 PM",
        "expected_tools": ["request_transport"],
        "category": "transport"
    },
    
    # ESCALATION TOOL (6 cases)
    {
        "id": 37,
        "prompt": "Can you book me a helicopter tour?",
        "expected_tools": ["escalate_to_manager"],
        "category": "escalation"
    },
    {
        "id": 38,
        "prompt": "I want to rent a yacht for tomorrow",
        "expected_tools": ["escalate_to_manager"],
        "category": "escalation"
    },
    {
        "id": 39,
        "prompt": "Can you arrange a private chef for dinner?",
        "expected_tools": ["escalate_to_manager"],
        "category": "escalation"
    },
    {
        "id": 40,
        "prompt": "I need a massage therapist to come to my room",
        "expected_tools": ["escalate_to_manager"],
        "category": "escalation"
    },
    {
        "id": 41,
        "prompt": "Can you organize a wine tasting experience?",
        "expected_tools": ["escalate_to_manager"],
        "category": "escalation"
    },
    {
        "id": 42,
        "prompt": "I want to book a limousine for a city tour",
        "expected_tools": ["escalate_to_manager"],
        "category": "escalation"
    },
    
    # MULTI-TOOL SCENARIOS (5 cases)
    {
        "id": 43,
        "prompt": "What time do I check out and can you get me transport to SFO at 2 PM?",
        "expected_tools": ["booking_details", "request_transport"],
        "category": "multi_tool"
    },
    {
        "id": 44,
        "prompt": "Can you tell me my room details and schedule cleaning for tomorrow at 11 AM?",
        "expected_tools": ["booking_details", "schedule_cleaning"],
        "category": "multi_tool"
    },
    {
        "id": 45,
        "prompt": "What's my name and when is my checkout time?",
        "expected_tools": ["guest_profile", "booking_details"],
        "category": "multi_tool"
    },
    {
        "id": 46,
        "prompt": "Show me my booking details and what are the hotel amenities?",
        "expected_tools": ["booking_details", "property_info"],
        "category": "multi_tool"
    },
    {
        "id": 47,
        "prompt": "I need to change checkout to 3 PM and book transport to LAX at 4 PM",
        "expected_tools": ["modify_checkout_time", "request_transport"],
        "category": "multi_tool"
    },
    
    # NO TOOL SCENARIOS (3 cases)
    {
        "id": 48,
        "prompt": "Thank you for your help!",
        "expected_tools": [],
        "category": "no_tool"
    },
    {
        "id": 49,
        "prompt": "How are you doing today?",
        "expected_tools": [],
        "category": "no_tool"
    },
    {
        "id": 50,
        "prompt": "That sounds great, thanks!",
        "expected_tools": [],
        "category": "no_tool"
    }
]

class ToolEvaluator:
    """Evaluates tool selection performance of the AI concierge agent."""
    
    def __init__(self, api_base_url: str = "http://localhost:8000", test_phone: str = "+1234567890"):
        self.api_base_url = api_base_url
        self.test_phone = test_phone
        self.results = []
        
    def extract_tools_from_response(self, response_text: str) -> List[str]:
        """
        Extract tool names from agent response by looking for tool usage patterns.
        This is a simplified approach - in production you'd want to capture actual tool calls.
        """
        tools_called = []
        
        # Look for patterns that indicate tool usage
        response_lower = response_text.lower()
        
        # Pattern matching for tool usage indicators
        if any(keyword in response_lower for keyword in ["your name is", "you are", "your preferences", "vip status"]):
            tools_called.append("guest_profile")
            
        if any(keyword in response_lower for keyword in ["check out", "check-out", "reservation", "booking", "room type"]):
            tools_called.append("booking_details")
            
        if any(keyword in response_lower for keyword in ["cleaning scheduled", "housekeeping", "cleaning team"]):
            tools_called.append("schedule_cleaning")
            
        if any(keyword in response_lower for keyword in ["checkout time", "checkout updated", "departure time"]):
            tools_called.append("modify_checkout_time")
            
        if any(keyword in response_lower for keyword in ["transport requested", "airport transport", "pickup"]):
            tools_called.append("request_transport")
            
        if any(keyword in response_lower for keyword in ["wifi", "pool", "gym", "amenities", "facilities", "restaurant"]):
            tools_called.append("property_info")
            
        if any(keyword in response_lower for keyword in ["escalated", "property manager", "get back to you"]):
            tools_called.append("escalate_to_manager")
            
        return list(set(tools_called))  # Remove duplicates
    
    def send_message(self, message: str) -> Tuple[str, bool]:
        """Send a message to the API and get response."""
        try:
            payload = {
                "message": message,
                "phone_number": self.test_phone
            }
            
            response = requests.post(
                f"{self.api_base_url}/message",
                json=payload,
                timeout=30
            )
            
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
        
        if not success:
            return {
                "test_id": test_case["id"],
                "prompt": test_case["prompt"],
                "expected_tools": test_case["expected_tools"],
                "actual_tools": [],
                "response": response,
                "success": False,
                "category": test_case["category"]
            }
        
        actual_tools = self.extract_tools_from_response(response)
        
        result = {
            "test_id": test_case["id"],
            "prompt": test_case["prompt"],
            "expected_tools": test_case["expected_tools"],
            "actual_tools": actual_tools,
            "response": response[:200] + "..." if len(response) > 200 else response,
            "success": True,
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
        total_tp = 0  # True Positives
        total_fp = 0  # False Positives
        total_fn = 0  # False Negatives
        
        # Per-tool metrics
        tool_metrics = {}
        all_tools = set()
        
        for result in successful_tests:
            expected = set(result["expected_tools"])
            actual = set(result["actual_tools"])
            
            all_tools.update(expected)
            all_tools.update(actual)
            
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
                "tp": tp,
                "fp": fp,
                "fn": fn
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
            time.sleep(0.5)
            
            # Progress update
            if (i + 1) % 10 == 0:
                logger.info(f"Completed {i + 1}/{len(TEST_CASES)} test cases")
        
        # Calculate metrics
        metrics = self.calculate_metrics()
        
        # Save results
        self.save_results(metrics)
        
        return metrics
    
    def save_results(self, metrics: Dict):
        """Save detailed results to files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed results
        with open(f"evaluation_results_{timestamp}.json", "w") as f:
            json.dump({
                "metrics": metrics,
                "detailed_results": self.results,
                "test_cases": TEST_CASES
            }, f, indent=2)
        
        # Save CSV for easy analysis
        df_results = pd.DataFrame(self.results)
        df_results.to_csv(f"evaluation_results_{timestamp}.csv", index=False)
        
        logger.info(f"Results saved to evaluation_results_{timestamp}.json and .csv")

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
        print("📄 Detailed results saved to evaluation_results_*.json and *.csv")
        
    except requests.RequestException:
        print("❌ Could not connect to API. Please ensure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        logger.error(f"Evaluation failed: {e}", exc_info=True)

if __name__ == "__main__":
    main() 