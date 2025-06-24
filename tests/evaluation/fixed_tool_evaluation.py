#!/usr/bin/env python3
"""
Fixed Tool Evaluation - Clears sessions between tests
"""

import json
import requests
import time

def clear_session(phone_number):
    """Clear a session to avoid memory issues"""
    try:
        requests.delete(f"http://localhost:8000/session/{phone_number}", timeout=5)
    except:
        pass

def test_tool(message, expected_tool, phone_number="+14155550123"):
    """Test a single tool with fresh session"""
    clear_session(phone_number)
    
    try:
        payload = {"message": message, "phone_number": phone_number}
        response = requests.post("http://localhost:8000/message", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            tools_used = data.get("tools_used", [])
            
            # Check for exact match and partial match
            exact_match = expected_tool in tools_used
            partial_match = any(expected_tool in tool for tool in tools_used)
            
            return {
                "success": exact_match,
                "partial": partial_match,
                "tools_used": tools_used,
                "response": data.get("response", "")[:100] + "..." if len(data.get("response", "")) > 100 else data.get("response", "")
            }
        else:
            return {"success": False, "error": f"HTTP {response.status_code}", "tools_used": []}
            
    except Exception as e:
        return {"success": False, "error": str(e), "tools_used": []}

def main():
    """Run comprehensive tool evaluation with session clearing"""
    print("🔧 Fixed Comprehensive Tool Evaluation")
    print("=" * 60)
    
    # Comprehensive test cases (2 per tool for 15 tools = 30 tests)
    test_cases = [
        # CORE TOOLS
        ("Hi, what's my name?", "guest_profile"),
        ("Am I a VIP guest?", "guest_profile"),
        ("When do I check out?", "booking_details"), 
        ("What room am I staying in?", "booking_details"),
        ("What's the WiFi password?", "property_info"),
        ("Do you have a gym?", "property_info"),
        ("Can you clean my room tomorrow at 2 PM?", "schedule_cleaning"),
        ("I need housekeeping service on Friday at 11:00 AM", "schedule_cleaning"),
        ("Can I change my checkout to 3 PM?", "modify_checkout_time"),
        ("I need to extend my checkout until 2:00 PM", "modify_checkout_time"),
        ("Can you get me a ride to SFO airport at 6 AM?", "request_transport"),
        ("I need transportation to LAX tomorrow at 3:30 PM", "request_transport"),
        ("Can you book me a helicopter tour?", "escalate_to_manager"),
        ("I want to rent a yacht for tomorrow", "escalate_to_manager"),
        
        # HIGH-IMPACT TOOLS
        ("Can you book me dinner at a nice Italian restaurant tonight?", "restaurant_reservation"),
        ("I need a table for 4 at a good seafood place tomorrow at 7 PM", "restaurant_reservation"),
        ("Can you stock some wine and snacks before I arrive?", "grocery_delivery"),
        ("I need groceries delivered - milk, bread, and fruit", "grocery_delivery"),
        ("The air conditioning isn't working in the master bedroom", "maintenance_request"),
        ("The WiFi is really slow throughout the house", "maintenance_request"),
        ("Can you book us a wine tour for tomorrow?", "activity_booking"),
        ("I want to book a sunset boat cruise for 4 people", "activity_booking"),
        ("Can you order Chinese food for delivery tonight?", "meal_delivery"),
        ("I'm hungry now - can you get pizza delivered?", "meal_delivery"),
        
        # LUXURY TOOLS
        ("Can you book a massage therapist to come to the villa?", "spa_services"),
        ("I need a couples massage for this afternoon", "spa_services"),
        ("Can you arrange a private chef for dinner tonight?", "private_chef"),
        ("I want a chef to cook breakfast for 6 people tomorrow", "private_chef"),
        ("What are the best restaurants in the area?", "local_recommendations"),
        ("Can you recommend fun activities for kids?", "local_recommendations"),
    ]
    
    results = []
    successful_tests = 0
    partial_successes = 0
    
    for i, (message, expected) in enumerate(test_cases, 1):
        print(f"\nTest {i:2d}: {message}")
        print(f"Expected: {expected}")
        
        # Use different phone numbers to ensure fresh sessions
        phone = f"+1415555{i:04d}"
        result = test_tool(message, expected, phone)
        results.append(result)
        
        if result["success"]:
            print(f"✅ SUCCESS - Got: {result['tools_used']}")
            successful_tests += 1
        elif result.get("partial"):
            print(f"🟡 PARTIAL - Got: {result['tools_used']}")
            partial_successes += 1
        else:
            print(f"❌ FAILED - Got: {result['tools_used']} | Error: {result.get('error', 'N/A')}")
        
        time.sleep(1)  # Small delay between tests
        
        if i % 10 == 0:
            print(f"\n--- Progress: {i}/{len(test_cases)} tests completed ---")
    
    # Calculate metrics
    total_tests = len(test_cases)
    success_rate = successful_tests / total_tests * 100
    partial_rate = partial_successes / total_tests * 100
    combined_rate = (successful_tests + partial_successes) / total_tests * 100
    
    print(f"\n🎯 FINAL RESULTS:")
    print(f"=" * 60)
    print(f"Perfect Matches: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
    print(f"Partial Matches: {partial_successes}/{total_tests} ({partial_rate:.1f}%)")
    print(f"Combined Success: {successful_tests + partial_successes}/{total_tests} ({combined_rate:.1f}%)")
    
    # Tool-specific breakdown
    tool_categories = {
        "CORE": ["guest_profile", "booking_details", "property_info", "schedule_cleaning", "modify_checkout_time", "request_transport", "escalate_to_manager"],
        "HIGH-IMPACT": ["restaurant_reservation", "grocery_delivery", "maintenance_request", "activity_booking", "meal_delivery"],
        "LUXURY": ["spa_services", "private_chef", "local_recommendations"]
    }
    
    print(f"\n📊 TOOL CATEGORY BREAKDOWN:")
    for category, tools in tool_categories.items():
        category_results = [r for i, r in enumerate(results) if test_cases[i][1] in tools]
        category_successes = sum(1 for r in category_results if r["success"])
        category_rate = category_successes / len(category_results) * 100 if category_results else 0
        print(f"{category:<12}: {category_successes}/{len(category_results)} ({category_rate:.1f}%)")

if __name__ == "__main__":
    main()