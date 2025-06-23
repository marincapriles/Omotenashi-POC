#!/usr/bin/env python3
"""
Quick evaluation script to test transport tool performance after prompt tuning.
"""

import requests
import time

# Transport test cases
TRANSPORT_TESTS = [
    {"id": 71, "prompt": "Can you get me a ride to SFO airport at 6 AM?", "expected_tools": ["request_transport"]},
    {"id": 72, "prompt": "I need transportation to LAX tomorrow at 3:30 PM", "expected_tools": ["request_transport"]},
    {"id": 73, "prompt": "Please arrange a car to the airport at 8:00 AM", "expected_tools": ["request_transport"]},
    {"id": 74, "prompt": "Can you book airport transport for 5:45 AM to JFK?", "expected_tools": ["request_transport"]},
    {"id": 75, "prompt": "I need a taxi to Oakland airport at 7 PM", "expected_tools": ["request_transport"]},
]

# Single tool test cases  
SINGLE_TOOL_TESTS = [
    {"id": 1, "prompt": "Hi, what's my name?", "expected_tools": ["guest_profile"]},
    {"id": 16, "prompt": "When do I check out?", "expected_tools": ["booking_details"]},
    {"id": 31, "prompt": "What's the WiFi password?", "expected_tools": ["property_info"]},
]

def extract_tools_from_response(response_text):
    """Extract tool usage patterns from response."""
    response_lower = response_text.lower()
    tools_detected = []
    
    # Transport tool patterns
    transport_patterns = ["transport requested", "airport transport", "pickup", "taxi", "car", "ride", "transportation arranged"]
    if any(pattern in response_lower for pattern in transport_patterns):
        tools_detected.append("request_transport")
    
    # Guest profile patterns  
    guest_patterns = ["your name is", "you are", "your preferences", "vip status", "guest id", "profile"]
    if any(pattern in response_lower for pattern in guest_patterns):
        tools_detected.append("guest_profile")
        
    # Booking patterns
    booking_patterns = ["check out", "check-out", "reservation", "booking", "room type", "confirmation"]
    if any(pattern in response_lower for pattern in booking_patterns):
        tools_detected.append("booking_details")
        
    # Property patterns
    property_patterns = ["wifi", "pool", "gym", "amenities", "facilities", "restaurant", "spa"]
    if any(pattern in response_lower for pattern in property_patterns):
        tools_detected.append("property_info")
    
    return tools_detected

def test_cases(test_list, category_name):
    """Test a list of cases and return results."""
    print(f"\n=== {category_name} ===")
    results = []
    
    for test in test_list:
        print(f"Testing: {test['prompt']}")
        
        try:
            response = requests.post(
                "http://localhost:8000/message",
                json={"message": test["prompt"], "phone_number": "+14155550123"},
                timeout=20
            )
            
            if response.status_code == 200:
                response_text = response.json()["response"]
                detected_tools = extract_tools_from_response(response_text)
                expected_tools = test["expected_tools"]
                
                # Check precision (no extra tools)
                precision_ok = len(detected_tools) <= len(expected_tools)
                # Check recall (found expected tools)
                recall_ok = all(tool in detected_tools for tool in expected_tools)
                
                result = {
                    "test_id": test["id"],
                    "expected": expected_tools,
                    "detected": detected_tools,
                    "precision_ok": precision_ok,
                    "recall_ok": recall_ok,
                    "response": response_text[:100] + "..." if len(response_text) > 100 else response_text
                }
                
                status = "✅" if (precision_ok and recall_ok) else "❌"
                print(f"  {status} Expected: {expected_tools} | Detected: {detected_tools}")
                print(f"     Precision: {'✅' if precision_ok else '❌'} | Recall: {'✅' if recall_ok else '❌'}")
                
                results.append(result)
            else:
                print(f"  ❌ API Error: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            
        time.sleep(1)  # Small delay between requests
    
    return results

def main():
    print("🚀 Quick Evaluation: Transport Tool + Prompt Tuning")
    print("=" * 60)
    
    # Test transport tools
    transport_results = test_cases(TRANSPORT_TESTS, "TRANSPORT TOOL TESTS")
    
    # Test single tool selection
    single_results = test_cases(SINGLE_TOOL_TESTS, "SINGLE TOOL PRECISION TESTS")
    
    # Summary
    all_results = transport_results + single_results
    total_tests = len(all_results)
    precision_success = sum(1 for r in all_results if r["precision_ok"])
    recall_success = sum(1 for r in all_results if r["recall_ok"])
    perfect_matches = sum(1 for r in all_results if r["precision_ok"] and r["recall_ok"])
    
    print(f"\n" + "=" * 60)
    print(f"📊 QUICK EVALUATION RESULTS")
    print(f"=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"Precision (no over-calling): {precision_success}/{total_tests} ({precision_success/total_tests*100:.1f}%)")
    print(f"Recall (found expected): {recall_success}/{total_tests} ({recall_success/total_tests*100:.1f}%)")
    print(f"Perfect Matches: {perfect_matches}/{total_tests} ({perfect_matches/total_tests*100:.1f}%)")
    
    # Transport-specific analysis
    transport_perfect = sum(1 for r in transport_results if r["precision_ok"] and r["recall_ok"])
    print(f"\n🚗 Transport Tool Success: {transport_perfect}/{len(transport_results)} ({transport_perfect/len(transport_results)*100:.1f}%)")

if __name__ == "__main__":
    main()