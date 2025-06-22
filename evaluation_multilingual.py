#!/usr/bin/env python3
"""
Multilingual Tool Selection Evaluation for Omotenashi Hotel Concierge
Evaluates precision and recall of tool selection by the AI agent using prompts 
in the guest's preferred language.
"""

import json
import logging
import requests
import time
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Multilingual test cases organized by language and category
MULTILINGUAL_TEST_CASES = {
    "English": {
        "guest_info": [
            {"prompt": "Hi, what's my name?", "expected_tools": ["guest_profile"]},
            {"prompt": "Can you tell me about my preferences?", "expected_tools": ["guest_profile"]},
            {"prompt": "Am I a VIP guest?", "expected_tools": ["guest_profile"]},
            {"prompt": "What language do I prefer?", "expected_tools": ["guest_profile"]},
            {"prompt": "Hello, I'm new here. Can you help me?", "expected_tools": ["guest_profile"]},
        ],
        "booking_info": [
            {"prompt": "When do I check out?", "expected_tools": ["booking_details"]},
            {"prompt": "What room am I staying in?", "expected_tools": ["booking_details"]},
            {"prompt": "Can you show me my reservation details?", "expected_tools": ["booking_details"]},
            {"prompt": "When is my check-in date?", "expected_tools": ["booking_details"]},
            {"prompt": "What type of room did I book?", "expected_tools": ["booking_details"]},
        ],
        "property_info": [
            {"prompt": "What's the WiFi password?", "expected_tools": ["property_info"]},
            {"prompt": "What time does the pool open?", "expected_tools": ["property_info"]},
            {"prompt": "Do you have a gym?", "expected_tools": ["property_info"]},
            {"prompt": "What restaurants are nearby?", "expected_tools": ["property_info"]},
            {"prompt": "Tell me about the hotel amenities", "expected_tools": ["property_info"]},
        ],
        "cleaning": [
            {"prompt": "Can you clean my room tomorrow at 2 PM?", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "I need housekeeping service on Friday at 11:00 AM", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "Please schedule room cleaning for today at 3:30 PM", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "Can you arrange cleaning service for Monday morning at 10 AM?", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "I'd like room service cleaning tomorrow at 1:00 PM", "expected_tools": ["schedule_cleaning"]},
        ],
        "checkout": [
            {"prompt": "Can I change my checkout to 3 PM?", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "I need to extend my checkout until 2:00 PM", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "Can you give me a late checkout at 1 PM?", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "I want to check out at noon instead of 11 AM", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "Please change my departure time to 4:00 PM", "expected_tools": ["modify_checkout_time"]},
        ],
        "transport": [
            {"prompt": "Can you get me a ride to SFO airport at 6 AM?", "expected_tools": ["request_transport"]},
            {"prompt": "I need transportation to LAX tomorrow at 3:30 PM", "expected_tools": ["request_transport"]},
            {"prompt": "Please arrange a car to the airport at 8:00 AM", "expected_tools": ["request_transport"]},
            {"prompt": "Can you book airport transport for 5:45 AM to JFK?", "expected_tools": ["request_transport"]},
            {"prompt": "I need a taxi to Oakland airport at 7 PM", "expected_tools": ["request_transport"]},
        ],
        "escalation": [
            {"prompt": "Can you book me a helicopter tour?", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "I want to rent a yacht for tomorrow", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "Can you arrange a private chef for dinner?", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "I need a massage therapist to come to my room", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "Can you organize a wine tasting experience?", "expected_tools": ["escalate_to_manager"]},
        ],
        "no_tool": [
            {"prompt": "Thank you for your help!", "expected_tools": []},
            {"prompt": "How are you doing today?", "expected_tools": []},
            {"prompt": "That sounds great, thanks!", "expected_tools": []},
            {"prompt": "Good morning!", "expected_tools": []},
            {"prompt": "Have a nice day!", "expected_tools": []},
        ]
    },
    
    "Spanish": {
        "guest_info": [
            {"prompt": "Hola, ¿cuál es mi nombre?", "expected_tools": ["guest_profile"]},
            {"prompt": "¿Puede decirme sobre mis preferencias?", "expected_tools": ["guest_profile"]},
            {"prompt": "¿Soy un huésped VIP?", "expected_tools": ["guest_profile"]},
            {"prompt": "¿Qué idioma prefiero?", "expected_tools": ["guest_profile"]},
            {"prompt": "Hola, soy nuevo aquí. ¿Puede ayudarme?", "expected_tools": ["guest_profile"]},
        ],
        "booking_info": [
            {"prompt": "¿Cuándo hago el check-out?", "expected_tools": ["booking_details"]},
            {"prompt": "¿En qué habitación me estoy quedando?", "expected_tools": ["booking_details"]},
            {"prompt": "¿Puede mostrarme los detalles de mi reserva?", "expected_tools": ["booking_details"]},
            {"prompt": "¿Cuándo es mi fecha de check-in?", "expected_tools": ["booking_details"]},
            {"prompt": "¿Qué tipo de habitación reservé?", "expected_tools": ["booking_details"]},
        ],
        "property_info": [
            {"prompt": "¿Cuál es la contraseña del WiFi?", "expected_tools": ["property_info"]},
            {"prompt": "¿A qué hora abre la piscina?", "expected_tools": ["property_info"]},
            {"prompt": "¿Tienen gimnasio?", "expected_tools": ["property_info"]},
            {"prompt": "¿Qué restaurantes hay cerca?", "expected_tools": ["property_info"]},
            {"prompt": "Hábleme sobre las comodidades del hotel", "expected_tools": ["property_info"]},
        ],
        "cleaning": [
            {"prompt": "¿Puede limpiar mi habitación mañana a las 2 PM?", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "Necesito servicio de limpieza el viernes a las 11:00 AM", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "Por favor programe la limpieza de la habitación para hoy a las 3:30 PM", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "¿Puede organizar el servicio de limpieza para el lunes por la mañana a las 10 AM?", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "Me gustaría limpieza de habitación mañana a la 1:00 PM", "expected_tools": ["schedule_cleaning"]},
        ],
        "checkout": [
            {"prompt": "¿Puedo cambiar mi check-out a las 3 PM?", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "Necesito extender mi check-out hasta las 2:00 PM", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "¿Puede darme un check-out tardío a la 1 PM?", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "Quiero hacer check-out al mediodía en lugar de las 11 AM", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "Por favor cambie mi hora de salida a las 4:00 PM", "expected_tools": ["modify_checkout_time"]},
        ],
        "transport": [
            {"prompt": "¿Puede conseguirme un viaje al aeropuerto SFO a las 6 AM?", "expected_tools": ["request_transport"]},
            {"prompt": "Necesito transporte a LAX mañana a las 3:30 PM", "expected_tools": ["request_transport"]},
            {"prompt": "Por favor organice un auto al aeropuerto a las 8:00 AM", "expected_tools": ["request_transport"]},
            {"prompt": "¿Puede reservar transporte al aeropuerto para las 5:45 AM a JFK?", "expected_tools": ["request_transport"]},
            {"prompt": "Necesito un taxi al aeropuerto de Oakland a las 7 PM", "expected_tools": ["request_transport"]},
        ],
        "escalation": [
            {"prompt": "¿Puede reservarme un tour en helicóptero?", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "Quiero alquilar un yate para mañana", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "¿Puede organizar un chef privado para la cena?", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "Necesito un masajista que venga a mi habitación", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "¿Puede organizar una experiencia de cata de vinos?", "expected_tools": ["escalate_to_manager"]},
        ],
        "no_tool": [
            {"prompt": "¡Gracias por su ayuda!", "expected_tools": []},
            {"prompt": "¿Cómo está usted hoy?", "expected_tools": []},
            {"prompt": "¡Eso suena genial, gracias!", "expected_tools": []},
            {"prompt": "¡Buenos días!", "expected_tools": []},
            {"prompt": "¡Que tenga un buen día!", "expected_tools": []},
        ]
    },
    
    "French": {
        "guest_info": [
            {"prompt": "Bonjour, quel est mon nom?", "expected_tools": ["guest_profile"]},
            {"prompt": "Pouvez-vous me parler de mes préférences?", "expected_tools": ["guest_profile"]},
            {"prompt": "Suis-je un client VIP?", "expected_tools": ["guest_profile"]},
            {"prompt": "Quelle langue est-ce que je préfère?", "expected_tools": ["guest_profile"]},
            {"prompt": "Bonjour, je suis nouveau ici. Pouvez-vous m'aider?", "expected_tools": ["guest_profile"]},
        ],
        "booking_info": [
            {"prompt": "Quand est-ce que je pars?", "expected_tools": ["booking_details"]},
            {"prompt": "Dans quelle chambre suis-je?", "expected_tools": ["booking_details"]},
            {"prompt": "Pouvez-vous me montrer les détails de ma réservation?", "expected_tools": ["booking_details"]},
            {"prompt": "Quand est ma date d'arrivée?", "expected_tools": ["booking_details"]},
            {"prompt": "Quel type de chambre ai-je réservé?", "expected_tools": ["booking_details"]},
        ],
        "property_info": [
            {"prompt": "Quel est le mot de passe WiFi?", "expected_tools": ["property_info"]},
            {"prompt": "À quelle heure ouvre la piscine?", "expected_tools": ["property_info"]},
            {"prompt": "Avez-vous une salle de sport?", "expected_tools": ["property_info"]},
            {"prompt": "Quels restaurants y a-t-il à proximité?", "expected_tools": ["property_info"]},
            {"prompt": "Parlez-moi des équipements de l'hôtel", "expected_tools": ["property_info"]},
        ],
        "cleaning": [
            {"prompt": "Pouvez-vous nettoyer ma chambre demain à 14h?", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "J'ai besoin du service de ménage vendredi à 11h00", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "Veuillez programmer le nettoyage de la chambre pour aujourd'hui à 15h30", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "Pouvez-vous organiser le service de nettoyage pour lundi matin à 10h?", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "J'aimerais un nettoyage de chambre demain à 13h00", "expected_tools": ["schedule_cleaning"]},
        ],
        "checkout": [
            {"prompt": "Puis-je changer mon départ à 15h?", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "Je dois prolonger mon départ jusqu'à 14h00", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "Pouvez-vous me donner un départ tardif à 13h?", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "Je veux partir à midi au lieu de 11h", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "Veuillez changer mon heure de départ à 16h00", "expected_tools": ["modify_checkout_time"]},
        ],
        "transport": [
            {"prompt": "Pouvez-vous me trouver un transport vers l'aéroport SFO à 6h?", "expected_tools": ["request_transport"]},
            {"prompt": "J'ai besoin de transport vers LAX demain à 15h30", "expected_tools": ["request_transport"]},
            {"prompt": "Veuillez organiser une voiture vers l'aéroport à 8h00", "expected_tools": ["request_transport"]},
            {"prompt": "Pouvez-vous réserver un transport aéroport pour 5h45 vers JFK?", "expected_tools": ["request_transport"]},
            {"prompt": "J'ai besoin d'un taxi vers l'aéroport d'Oakland à 19h", "expected_tools": ["request_transport"]},
        ],
        "escalation": [
            {"prompt": "Pouvez-vous me réserver un tour en hélicoptère?", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "Je veux louer un yacht pour demain", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "Pouvez-vous organiser un chef privé pour le dîner?", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "J'ai besoin d'un masseur qui vient dans ma chambre", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "Pouvez-vous organiser une expérience de dégustation de vins?", "expected_tools": ["escalate_to_manager"]},
        ],
        "no_tool": [
            {"prompt": "Merci pour votre aide!", "expected_tools": []},
            {"prompt": "Comment allez-vous aujourd'hui?", "expected_tools": []},
            {"prompt": "Cela sonne bien, merci!", "expected_tools": []},
            {"prompt": "Bonjour!", "expected_tools": []},
            {"prompt": "Passez une bonne journée!", "expected_tools": []},
        ]
    }
}

class MultilingualToolEvaluator:
    """Evaluates tool selection performance using guest's preferred language."""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.results = []
        self.guests = self._load_guests()
        
        # Multilingual tool detection patterns
        self.tool_patterns = {
            "guest_profile": [
                # English
                "your name is", "you are", "your preferences", "vip status", 
                "guest id", "dietary restrictions", "contact information",
                "profile", "guest status", "special requests", "preferred",
                # Spanish
                "tu nombre es", "eres", "tus preferencias", "estado vip",
                "id de huésped", "restricciones dietéticas", "información de contacto",
                "perfil", "estado de huésped", "solicitudes especiales", "preferido",
                # French
                "votre nom est", "vous êtes", "vos préférences", "statut vip",
                "id client", "restrictions alimentaires", "informations de contact",
                "profil", "statut client", "demandes spéciales", "préféré"
            ],
            "booking_details": [
                # English
                "check out", "check-out", "reservation", "booking", "room type",
                "confirmation", "nights", "room number", "arrival", "departure",
                # Spanish
                "salida", "reserva", "tipo de habitación", "confirmación",
                "noches", "número de habitación", "llegada", "partida",
                # French
                "départ", "réservation", "type de chambre", "confirmation",
                "nuits", "numéro de chambre", "arrivée", "départ"
            ],
            "schedule_cleaning": [
                # English
                "cleaning scheduled", "housekeeping", "cleaning team", 
                "room cleaning", "cleaning service", "housekeeping service",
                # Spanish
                "limpieza programada", "servicio de limpieza", "equipo de limpieza",
                "limpieza de habitación", "servicio de limpieza",
                # French
                "nettoyage programmé", "service de ménage", "équipe de nettoyage",
                "nettoyage de chambre", "service de nettoyage"
            ],
            "modify_checkout_time": [
                # English
                "checkout", "departure", "late checkout", "extend",
                "check-out time", "leaving time",
                # Spanish
                "salida", "partida", "salida tardía", "extender",
                "hora de salida", "hora de partida",
                # French
                "départ", "départ tardif", "prolonger",
                "heure de départ", "heure de sortie"
            ],
            "request_transport": [
                # English
                "transport", "taxi", "car", "airport", "ride",
                "pickup", "transfer", "transportation",
                # Spanish
                "transporte", "taxi", "auto", "aeropuerto", "viaje",
                "recogida", "traslado", "transporte",
                # French
                "transport", "taxi", "voiture", "aéroport", "voyage",
                "prise en charge", "transfert", "transport"
            ],
            "property_info": [
                # English
                "wifi", "pool", "gym", "spa", "restaurant", "amenities",
                "facilities", "services", "breakfast", "parking",
                # Spanish
                "wifi", "piscina", "gimnasio", "spa", "restaurante", "comodidades",
                "instalaciones", "servicios", "desayuno", "estacionamiento",
                # French
                "wifi", "piscine", "salle de sport", "spa", "restaurant", "équipements",
                "installations", "services", "petit-déjeuner", "parking"
            ],
            "escalate_to_manager": [
                # English
                "escalated", "manager", "property manager", "forwarded",
                "escalation", "manager will", "contact you",
                # Spanish
                "escalado", "gerente", "administrador", "reenviado",
                "escalación", "gerente se", "contactará",
                # French
                "escaladé", "gestionnaire", "directeur", "transféré",
                "escalade", "gestionnaire va", "vous contacter"
            ]
        }
    
    def _load_guests(self) -> List[Dict]:
        """Load guest information from guests.json"""
        try:
            with open("guests.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load guests: {e}")
            return []
    
    def _get_guest_by_phone(self, phone: str) -> Optional[Dict]:
        """Get guest information by phone number"""
        return next((g for g in self.guests if g["phone_number"] == phone), None)
    
    def _generate_test_cases_for_guest(self, guest: Dict) -> List[Dict]:
        """Generate test cases in the guest's preferred language"""
        language = guest.get("preferred_language", "English")
        
        # Fallback to English if language not supported
        if language not in MULTILINGUAL_TEST_CASES:
            logger.warning(f"Language '{language}' not supported, falling back to English for guest {guest['name']}")
            language = "English"
        
        test_cases = []
        test_id = 1
        
        # Generate test cases from each category
        for category, cases in MULTILINGUAL_TEST_CASES[language].items():
            for case in cases:
                test_case = {
                    "id": test_id,
                    "prompt": case["prompt"],
                    "expected_tools": case["expected_tools"],
                    "category": category,
                    "language": language,
                    "guest_phone": guest["phone_number"],
                    "guest_name": guest["name"]
                }
                test_cases.append(test_case)
                test_id += 1
        
        return test_cases
    
    def extract_tools_from_response(self, response_text: str) -> List[str]:
        """Extract tool names from agent response using multilingual pattern matching."""
        tools_called = []
        response_lower = response_text.lower()
        
        for tool_name, patterns in self.tool_patterns.items():
            if any(pattern in response_lower for pattern in patterns):
                tools_called.append(tool_name)
        
        return list(set(tools_called))  # Remove duplicates
    
    def send_message(self, message: str, phone: str) -> Tuple[str, bool]:
        """Send a message to the API and get response."""
        try:
            payload = {"message": message, "phone_number": phone}
            response = requests.post(f"{self.api_base_url}/message", json=payload, timeout=30)
            
            if response.status_code == 200:
                return response.json()["response"], True
            else:
                logger.error(f"API error {response.status_code}: {response.text}")
                return f"API Error: {response.status_code}", False
                
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return f"Request failed: {e}", False
    
    def clear_session(self, phone: str):
        """Clear the conversation session for a specific guest."""
        try:
            requests.delete(f"{self.api_base_url}/session/{phone}")
        except:
            pass  # Ignore errors
    
    def evaluate_test_case(self, test_case: Dict) -> Dict:
        """Evaluate a single test case."""
        logger.info(f"Testing case {test_case['id']} ({test_case['language']}): {test_case['prompt'][:50]}...")
        
        response, success = self.send_message(test_case["prompt"], test_case["guest_phone"])
        actual_tools = self.extract_tools_from_response(response) if success else []
        
        result = {
            "test_id": test_case["id"],
            "prompt": test_case["prompt"],
            "expected_tools": test_case["expected_tools"],
            "actual_tools": actual_tools,
            "response": response[:200] + "..." if len(response) > 200 else response,
            "success": success,
            "category": test_case["category"],
            "language": test_case["language"],
            "guest_phone": test_case["guest_phone"],
            "guest_name": test_case["guest_name"]
        }
        
        logger.info(f"Expected: {test_case['expected_tools']}, Got: {actual_tools}")
        return result
    
    def calculate_metrics(self) -> Dict:
        """Calculate precision, recall, and F1 scores with language breakdown."""
        successful_tests = [r for r in self.results if r["success"]]
        
        if not successful_tests:
            return {"error": "No successful tests to evaluate"}
        
        # Overall metrics
        total_tp = total_fp = total_fn = 0
        tool_metrics = {}
        language_metrics = {}
        
        for result in successful_tests:
            expected = set(result["expected_tools"])
            actual = set(result["actual_tools"])
            language = result["language"]
            
            tp = len(expected & actual)
            fp = len(actual - expected)
            fn = len(expected - actual)
            
            total_tp += tp
            total_fp += fp
            total_fn += fn
            
            # Track per-language performance
            if language not in language_metrics:
                language_metrics[language] = {"tp": 0, "fp": 0, "fn": 0, "tests": 0}
            language_metrics[language]["tp"] += tp
            language_metrics[language]["fp"] += fp
            language_metrics[language]["fn"] += fn
            language_metrics[language]["tests"] += 1
            
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
        
        # Calculate per-language metrics
        language_results = {}
        for language, counts in language_metrics.items():
            tp, fp, fn = counts["tp"], counts["fp"], counts["fn"]
            lang_precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            lang_recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            lang_f1 = 2 * (lang_precision * lang_recall) / (lang_precision + lang_recall) if (lang_precision + lang_recall) > 0 else 0
            
            language_results[language] = {
                "precision": round(lang_precision, 3),
                "recall": round(lang_recall, 3),
                "f1": round(lang_f1, 3),
                "test_count": counts["tests"]
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
            "per_language": language_results,
            "per_category": category_metrics
        }
    
    def run_evaluation_for_guest(self, guest_phone: str) -> Dict:
        """Run evaluation for a specific guest using their preferred language."""
        guest = self._get_guest_by_phone(guest_phone)
        if not guest:
            logger.error(f"Guest not found for phone: {guest_phone}")
            return {"error": f"Guest not found for phone: {guest_phone}"}
        
        logger.info(f"Running multilingual evaluation for guest: {guest['name']} (Language: {guest.get('preferred_language', 'English')})")
        
        # Generate test cases for this guest's language
        test_cases = self._generate_test_cases_for_guest(guest)
        
        logger.info(f"Generated {len(test_cases)} test cases in {guest.get('preferred_language', 'English')}")
        
        # Clear session to start fresh
        self.clear_session(guest_phone)
        
        # Run each test case
        for i, test_case in enumerate(test_cases):
            result = self.evaluate_test_case(test_case)
            self.results.append(result)
            
            # Small delay to avoid overwhelming the API
            time.sleep(0.3)
            
            # Progress update
            if (i + 1) % 10 == 0:
                logger.info(f"Completed {i + 1}/{len(test_cases)} test cases")
        
        # Calculate metrics
        metrics = self.calculate_metrics()
        
        # Save results
        self.save_results(metrics, guest)
        
        return metrics
    
    def save_results(self, metrics: Dict, guest: Dict):
        """Save detailed results to files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        language = guest.get("preferred_language", "English")
        guest_name = guest["name"].replace(" ", "_")
        
        # Save detailed JSON results
        filename_base = f"multilingual_evaluation_{guest_name}_{language}_{timestamp}"
        
        with open(f"{filename_base}.json", "w", encoding="utf-8") as f:
            json.dump({
                "guest_info": guest,
                "metrics": metrics,
                "detailed_results": self.results
            }, f, indent=2, ensure_ascii=False)
        
        # Save formatted TXT results
        with open(f"{filename_base}.txt", "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("OMOTENASHI MULTILINGUAL TOOL EVALUATION REPORT\n")
            f.write(f"Guest: {guest['name']}\n")
            f.write(f"Language: {language}\n")
            f.write(f"Phone: {guest['phone_number']}\n")
            f.write(f"VIP Status: {'Yes' if guest.get('vip_status', False) else 'No'}\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            # Overall performance
            overall = metrics["overall"]
            f.write("OVERALL PERFORMANCE:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Precision: {overall['precision']:.3f} ({overall['total_tp']}/{overall['total_tp'] + overall['total_fp']})\n")
            f.write(f"Recall:    {overall['recall']:.3f} ({overall['total_tp']}/{overall['total_tp'] + overall['total_fn']})\n")
            f.write(f"F1 Score:  {overall['f1']:.3f}\n")
            f.write(f"Tests:     {overall['total_tests']}\n\n")
            
            # Per-language performance
            if "per_language" in metrics:
                f.write("PER-LANGUAGE PERFORMANCE:\n")
                f.write("-" * 40 + "\n")
                for lang, lang_metrics in metrics["per_language"].items():
                    f.write(f"{lang:15} | P: {lang_metrics['precision']:.3f} | R: {lang_metrics['recall']:.3f} | F1: {lang_metrics['f1']:.3f} | Tests: {lang_metrics['test_count']}\n")
                f.write("\n")
            
            # Per-tool performance
            f.write("PER-TOOL PERFORMANCE:\n")
            f.write("-" * 40 + "\n")
            for tool, tool_metrics in metrics["per_tool"].items():
                f.write(f"{tool:25} | P: {tool_metrics['precision']:.3f} | R: {tool_metrics['recall']:.3f} | F1: {tool_metrics['f1']:.3f}\n")
            f.write("\n")
            
            # Per-category performance
            f.write("PER-CATEGORY PERFORMANCE:\n")
            f.write("-" * 40 + "\n")
            for category, cat_metrics in metrics["per_category"].items():
                f.write(f"{category:20} | P: {cat_metrics['precision']:.3f} | R: {cat_metrics['recall']:.3f} | F1: {cat_metrics['f1']:.3f} | Tests: {cat_metrics['test_count']}\n")
        
        logger.info(f"Results saved to {filename_base}.json and {filename_base}.txt")

def main():
    """Run the multilingual tool evaluation."""
    evaluator = MultilingualToolEvaluator()
    
    try:
        # Test API connection
        response = requests.get("http://localhost:8000/debug/status", timeout=5)
        if response.status_code != 200:
            print("❌ API not accessible. Please ensure the server is running on http://localhost:8000")
            return
        
        # Get available guests
        if not evaluator.guests:
            print("❌ No guests found in guests.json")
            return
        
        print("🌍 Multilingual Tool Selection Evaluation")
        print("=" * 60)
        
        # Show available guests
        print("Available guests:")
        for i, guest in enumerate(evaluator.guests, 1):
            print(f"  {i}. {guest['name']} ({guest.get('preferred_language', 'English')}) - {guest['phone_number']}")
        
        # Get user selection
        try:
            choice = input(f"\nSelect guest (1-{len(evaluator.guests)}) or press Enter for all: ").strip()
            
            if choice == "":
                # Run for all guests
                all_results = {}
                for guest in evaluator.guests:
                    print(f"\n🔄 Evaluating {guest['name']} ({guest.get('preferred_language', 'English')})...")
                    evaluator.results = []  # Reset results for each guest
                    metrics = evaluator.run_evaluation_for_guest(guest["phone_number"])
                    all_results[guest["name"]] = metrics
                
                # Print summary
                print("\n" + "=" * 60)
                print("📊 MULTILINGUAL EVALUATION SUMMARY")
                print("=" * 60)
                for guest_name, metrics in all_results.items():
                    if "error" not in metrics:
                        overall = metrics["overall"]
                        print(f"{guest_name:20} | F1: {overall['f1']:.3f} | Tests: {overall['total_tests']}")
            
            else:
                # Run for selected guest
                guest_idx = int(choice) - 1
                if 0 <= guest_idx < len(evaluator.guests):
                    selected_guest = evaluator.guests[guest_idx]
                    print(f"\n🔄 Evaluating {selected_guest['name']} ({selected_guest.get('preferred_language', 'English')})...")
                    
                    metrics = evaluator.run_evaluation_for_guest(selected_guest["phone_number"])
                    
                    if "error" not in metrics:
                        # Print results
                        print("\n" + "=" * 60)
                        print("📊 EVALUATION RESULTS")
                        print("=" * 60)
                        
                        overall = metrics["overall"]
                        print(f"\n🎯 OVERALL PERFORMANCE:")
                        print(f"   Precision: {overall['precision']:.3f}")
                        print(f"   Recall:    {overall['recall']:.3f}")
                        print(f"   F1 Score:  {overall['f1']:.3f}")
                        print(f"   Tests:     {overall['total_tests']}")
                        
                        if "per_language" in metrics:
                            print(f"\n🌍 LANGUAGE PERFORMANCE:")
                            for lang, lang_metrics in metrics["per_language"].items():
                                print(f"   {lang:15} | F1: {lang_metrics['f1']:.3f} | Tests: {lang_metrics['test_count']}")
                        
                        print(f"\n🔧 PER-TOOL PERFORMANCE:")
                        for tool, tool_metrics in metrics["per_tool"].items():
                            print(f"   {tool:20} | F1: {tool_metrics['f1']:.3f}")
                        
                        print("\n✅ Evaluation completed successfully!")
                    else:
                        print(f"❌ {metrics['error']}")
                else:
                    print("❌ Invalid selection")
        
        except ValueError:
            print("❌ Invalid input")
        except KeyboardInterrupt:
            print("\n⏹️  Evaluation cancelled by user")
        
    except requests.RequestException:
        print("❌ Could not connect to API. Please ensure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        logger.error(f"Evaluation failed: {e}", exc_info=True)

if __name__ == "__main__":
    main()
