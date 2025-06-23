#!/usr/bin/env python3
"""
Comprehensive Guest Journey & Multi-Language Evaluation
Tests complete guest experiences with realistic personas and language variety
"""

import json
import requests
import time
from typing import List, Dict, Tuple

class GuestPersona:
    """Represents a guest with specific characteristics and journey"""
    
    def __init__(self, name: str, phone: str, language: str, vip: bool, journey: List[Tuple[str, str, str]]):
        self.name = name
        self.phone = phone  
        self.language = language
        self.vip = vip
        self.journey = journey  # List of (message, expected_tool, description)
        self.conversation_history = []
        self.tools_used_total = []

def clear_session(phone_number: str):
    """Clear a session to start fresh"""
    try:
        requests.delete(f"http://localhost:8000/session/{phone_number}", timeout=5)
    except:
        pass

def send_message(phone: str, message: str) -> Dict:
    """Send message and return response with tool detection"""
    try:
        payload = {"message": message, "phone_number": phone}
        response = requests.post("http://localhost:8000/message", json=payload, timeout=45)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "response": data.get("response", ""),
                "tools_used": data.get("tools_used", []),
                "debug_info": data.get("debug_info", {})
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}",
                "response": "",
                "tools_used": []
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "response": "",
            "tools_used": []
        }

def test_guest_journey(guest: GuestPersona) -> Dict:
    """Test complete guest journey with conversation continuity"""
    print(f"\n🏨 Testing Guest Journey: {guest.name}")
    print(f"📞 Phone: {guest.phone} | 🌍 Language: {guest.language} | ⭐ VIP: {guest.vip}")
    print("=" * 80)
    
    # Clear any existing session
    clear_session(guest.phone)
    
    journey_results = []
    tools_found = set()
    conversation_quality = []
    
    for step, (message, expected_tool, description) in enumerate(guest.journey, 1):
        print(f"\nStep {step}: {description}")
        print(f"Message: {message}")
        print(f"Expected Tool: {expected_tool}")
        
        result = send_message(guest.phone, message)
        
        # Analyze result
        tool_success = expected_tool in result.get("tools_used", [])
        tools_found.update(result.get("tools_used", []))
        
        # Store conversation history
        guest.conversation_history.append({
            "step": step,
            "message": message,
            "response": result.get("response", ""),
            "tools_used": result.get("tools_used", []),
            "expected_tool": expected_tool,
            "success": tool_success
        })
        
        # Evaluate response quality
        response_text = result.get("response", "").lower()
        quality_indicators = {
            "personalized": guest.name.lower() in response_text,
            "helpful": any(word in response_text for word in ["arranged", "booked", "scheduled", "confirmed", "help"]),
            "professional": any(word in response_text for word in ["please", "certainly", "happy to", "of course"]),
            "contextual": len(result.get("tools_used", [])) > 0
        }
        
        conversation_quality.append(quality_indicators)
        
        if tool_success:
            print(f"✅ SUCCESS - Tool {expected_tool} found in: {result.get('tools_used', [])}")
        else:
            print(f"❌ FAILED - Expected {expected_tool}, got: {result.get('tools_used', [])}")
        
        # Show response preview
        response_preview = result.get("response", "")[:150] + "..." if len(result.get("response", "")) > 150 else result.get("response", "")
        print(f"Response: {response_preview}")
        
        journey_results.append({
            "step": step,
            "description": description,
            "message": message,
            "expected_tool": expected_tool,
            "tools_used": result.get("tools_used", []),
            "tool_success": tool_success,
            "response_length": len(result.get("response", "")),
            "quality": quality_indicators
        })
        
        time.sleep(2)  # Small delay between requests
    
    # Calculate journey metrics
    successful_steps = sum(1 for r in journey_results if r["tool_success"])
    total_steps = len(journey_results)
    success_rate = successful_steps / total_steps * 100 if total_steps > 0 else 0
    
    # Conversation quality metrics
    avg_personalization = sum(q["personalized"] for q in conversation_quality) / len(conversation_quality) * 100
    avg_helpfulness = sum(q["helpful"] for q in conversation_quality) / len(conversation_quality) * 100
    avg_professionalism = sum(q["professional"] for q in conversation_quality) / len(conversation_quality) * 100
    avg_contextual = sum(q["contextual"] for q in conversation_quality) / len(conversation_quality) * 100
    
    return {
        "guest": guest,
        "journey_results": journey_results,
        "metrics": {
            "success_rate": success_rate,
            "successful_steps": successful_steps,
            "total_steps": total_steps,
            "unique_tools_used": len(tools_found),
            "conversation_quality": {
                "personalization": avg_personalization,
                "helpfulness": avg_helpfulness,
                "professionalism": avg_professionalism,
                "contextual": avg_contextual
            }
        }
    }

def main():
    """Run comprehensive guest journey evaluation"""
    print("🌟 COMPREHENSIVE GUEST JOURNEY & MULTI-LANGUAGE EVALUATION")
    print("=" * 90)
    
    # Define realistic guest personas with complete journeys
    guest_personas = [
        # VIP English Guest - Complete luxury experience
        GuestPersona(
            name="Carlos Marin",
            phone="+14155550001", 
            language="English",
            vip=True,
            journey=[
                ("Hi, what's my name? I just arrived at the villa.", "guest_profile", "Arrival greeting & identity confirmation"),
                ("When do I check out? Also, what room am I in?", "booking_details", "Reservation details check"),
                ("What's the WiFi password? Do you have a gym?", "property_info", "Property amenities inquiry"),
                ("Can you stock some wine and cheese before tonight?", "grocery_delivery", "Pre-arrival grocery request"),
                ("Book me dinner at a nice Italian restaurant for 2 people tonight at 8 PM", "restaurant_reservation", "Fine dining reservation"),
                ("The air conditioning isn't working properly in the master bedroom", "maintenance_request", "Service issue reporting"),
                ("Can you arrange a couples massage for tomorrow afternoon?", "spa_services", "Luxury wellness booking"),
                ("I need transportation to SFO tomorrow at 6 AM", "request_transport", "Departure transportation")
            ]
        ),
        
        # Standard Spanish Guest - Family vacation
        GuestPersona(
            name="Maria Rodriguez", 
            phone="+14155550002",
            language="Spanish",
            vip=False,
            journey=[
                ("Hola, ¿cuál es mi nombre? Soy nueva aquí.", "guest_profile", "Spanish greeting & identity"),
                ("¿Cuándo es mi check-out? ¿Qué habitación tengo?", "booking_details", "Spanish reservation inquiry"),
                ("¿Cuál es la contraseña del WiFi?", "property_info", "Spanish WiFi request"),
                ("¿Pueden entregar comida china esta noche?", "meal_delivery", "Spanish food delivery"),
                ("Necesito servicio de limpieza mañana a las 2 PM", "schedule_cleaning", "Spanish housekeeping"),
                ("¿Pueden recomendar actividades para niños?", "local_recommendations", "Spanish family activities")
            ]
        ),
        
        # VIP French Guest - Business traveler
        GuestPersona(
            name="Jean Baptiste",
            phone="+14155550003",
            language="French", 
            vip=True,
            journey=[
                ("Bonjour, quel est mon nom? Je viens d'arriver.", "guest_profile", "French greeting & identity"),
                ("Quand est mon départ? J'ai une réunion importante.", "booking_details", "French checkout inquiry"),
                ("Pouvez-vous réserver un chef privé pour ce soir?", "private_chef", "French private chef request"),
                ("Je peux changer mon checkout à 3 PM?", "modify_checkout_time", "French checkout modification"),
                ("Quels sont les meilleurs restaurants de la région?", "local_recommendations", "French restaurant recommendations")
            ]
        ),
        
        # Standard English Guest - Simple requests
        GuestPersona(
            name="John Smith",
            phone="+14155550004",
            language="English",
            vip=False,
            journey=[
                ("What's my name?", "guest_profile", "Basic identity check"),
                ("When do I check out?", "booking_details", "Simple checkout inquiry"),
                ("Can you clean my room tomorrow at 11 AM?", "schedule_cleaning", "Basic housekeeping"),
                ("I'm hungry - can you order pizza delivery?", "meal_delivery", "Quick food delivery"),
                ("Can you book a wine tour for tomorrow?", "activity_booking", "Activity booking")
            ]
        ),
        
        # Mixed Language Guest - Code switching
        GuestPersona(
            name="Sofia Chen",
            phone="+14155550005", 
            language="Mixed",
            vip=True,
            journey=[
                ("Hi, what's my name? Soy Sofia.", "guest_profile", "Mixed English-Spanish greeting"),
                ("When do I check out? ¿Cuándo es mi salida?", "booking_details", "Bilingual checkout question"),
                ("Can you book me a massage? Un masaje, por favor.", "spa_services", "Mixed language spa request"),
                ("¿Pueden entregar groceries? I need milk and bread.", "grocery_delivery", "Mixed grocery request")
            ]
        )
    ]
    
    # Run evaluation for each guest
    all_results = []
    
    for guest in guest_personas:
        result = test_guest_journey(guest)
        all_results.append(result)
        time.sleep(3)  # Pause between guests
    
    # Generate comprehensive report
    print("\n" + "=" * 90)
    print("📊 COMPREHENSIVE EVALUATION RESULTS")
    print("=" * 90)
    
    # Overall metrics
    total_steps = sum(r["metrics"]["total_steps"] for r in all_results)
    total_successful = sum(r["metrics"]["successful_steps"] for r in all_results)
    overall_success_rate = total_successful / total_steps * 100 if total_steps > 0 else 0
    
    print(f"\n🎯 OVERALL PERFORMANCE:")
    print(f"   Total Steps Tested: {total_steps}")
    print(f"   Successful Steps: {total_successful}")
    print(f"   Overall Success Rate: {overall_success_rate:.1f}%")
    
    # Language breakdown
    print(f"\n🌍 LANGUAGE PERFORMANCE:")
    for result in all_results:
        guest = result["guest"]
        metrics = result["metrics"]
        print(f"   {guest.language:8} ({guest.name:15}): {metrics['successful_steps']}/{metrics['total_steps']} ({metrics['success_rate']:.1f}%)")
    
    # VIP vs Standard breakdown
    vip_results = [r for r in all_results if r["guest"].vip]
    standard_results = [r for r in all_results if not r["guest"].vip]
    
    if vip_results:
        vip_success = sum(r["metrics"]["successful_steps"] for r in vip_results)
        vip_total = sum(r["metrics"]["total_steps"] for r in vip_results)
        vip_rate = vip_success / vip_total * 100 if vip_total > 0 else 0
        print(f"\n⭐ VIP GUEST PERFORMANCE: {vip_success}/{vip_total} ({vip_rate:.1f}%)")
    
    if standard_results:
        standard_success = sum(r["metrics"]["successful_steps"] for r in standard_results)
        standard_total = sum(r["metrics"]["total_steps"] for r in standard_results)
        standard_rate = standard_success / standard_total * 100 if standard_total > 0 else 0
        print(f"👤 STANDARD GUEST PERFORMANCE: {standard_success}/{standard_total} ({standard_rate:.1f}%)")
    
    # Conversation quality analysis
    print(f"\n💬 CONVERSATION QUALITY METRICS:")
    all_quality = []
    for result in all_results:
        quality = result["metrics"]["conversation_quality"]
        all_quality.append(quality)
        guest = result["guest"]
        print(f"   {guest.name:15} - Personalization: {quality['personalization']:.1f}%, Helpfulness: {quality['helpfulness']:.1f}%")
    
    # Tool usage analysis
    print(f"\n🔧 TOOL USAGE ANALYSIS:")
    all_tools_used = set()
    for result in all_results:
        for step in result["journey_results"]:
            all_tools_used.update(step["tools_used"])
    
    print(f"   Unique Tools Activated: {len(all_tools_used)}")
    print(f"   Tools Used: {sorted(list(all_tools_used))}")
    
    return all_results

if __name__ == "__main__":
    results = main()