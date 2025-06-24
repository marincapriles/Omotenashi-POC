#!/usr/bin/env python3
"""
Simple tool evaluation to test basic functionality
"""

import json
import requests
import time

def test_single_tool(message, expected_tool):
    """Test a single message and return result"""
    try:
        payload = {"message": message, "phone_number": "+14155550123"}
        response = requests.post("http://localhost:8000/message", json=payload, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            tools_used = data.get("tools_used", [])
            response_text = data.get("response", "")
            
            # Check if expected tool was used
            success = expected_tool in tools_used
            return {
                "success": success,
                "tools_used": tools_used,
                "response": response_text[:100] + "..." if len(response_text) > 100 else response_text,
                "expected": expected_tool
            }
        else:
            return {"success": False, "error": f"HTTP {response.status_code}"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    """Run simple tool tests"""
    print("🔧 Simple Tool Functionality Test")
    print("=" * 50)
    
    # Test core tools with clear, simple queries
    test_cases = [
        ("What's my name?", "guest_profile"),
        ("When do I check out?", "booking_details"),  
        ("What's the WiFi password?", "property_info"),
        ("Can you book me a ride to SFO at 6 AM?", "request_transport"),
        ("Can you book dinner at an Italian restaurant tonight?", "restaurant_reservation"),
        ("The AC isn't working", "maintenance_request"),
    ]
    
    results = []
    for i, (message, expected) in enumerate(test_cases, 1):
        print(f"\nTest {i}: {message}")
        print(f"Expected: {expected}")
        
        result = test_single_tool(message, expected)
        results.append(result)
        
        if result["success"]:
            print(f"✅ SUCCESS - Got: {result['tools_used']}")
        else:
            print(f"❌ FAILED - Got: {result.get('tools_used', [])} | Error: {result.get('error', 'N/A')}")
        
        time.sleep(2)  # Small delay between tests
    
    # Summary
    successful = sum(1 for r in results if r["success"])
    print(f"\n🎯 SUMMARY: {successful}/{len(test_cases)} tests passed ({successful/len(test_cases)*100:.1f}%)")

if __name__ == "__main__":
    main()