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
    
    "Japanese": {
        "guest_info": [
            {"prompt": "こんにちは、私の名前は何ですか？", "expected_tools": ["guest_profile"]},
            {"prompt": "私の好みについて教えてください", "expected_tools": ["guest_profile"]},
            {"prompt": "私はVIPゲストですか？", "expected_tools": ["guest_profile"]},
            {"prompt": "私はどの言語を好みますか？", "expected_tools": ["guest_profile"]},
            {"prompt": "こんにちは、初めてです。手伝ってもらえますか？", "expected_tools": ["guest_profile"]},
        ],
        "booking_info": [
            {"prompt": "チェックアウトはいつですか？", "expected_tools": ["booking_details"]},
            {"prompt": "どの部屋に泊まっていますか？", "expected_tools": ["booking_details"]},
            {"prompt": "予約の詳細を見せてもらえますか？", "expected_tools": ["booking_details"]},
            {"prompt": "チェックイン日はいつですか？", "expected_tools": ["booking_details"]},
            {"prompt": "どんなタイプの部屋を予約しましたか？", "expected_tools": ["booking_details"]},
        ],
        "property_info": [
            {"prompt": "WiFiのパスワードは何ですか？", "expected_tools": ["property_info"]},
            {"prompt": "プールは何時に開きますか？", "expected_tools": ["property_info"]},
            {"prompt": "ジムはありますか？", "expected_tools": ["property_info"]},
            {"prompt": "近くにどんなレストランがありますか？", "expected_tools": ["property_info"]},
            {"prompt": "ホテルの設備について教えてください", "expected_tools": ["property_info"]},
        ],
        "cleaning": [
            {"prompt": "明日の午後2時に部屋を掃除してもらえますか？", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "金曜日の午前11時にハウスキーピングが必要です", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "今日の午後3時30分に部屋の掃除を予約してください", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "月曜日の朝10時に掃除サービスを手配してもらえますか？", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "明日の午後1時にルームクリーニングをお願いします", "expected_tools": ["schedule_cleaning"]},
        ],
        "checkout": [
            {"prompt": "チェックアウトを午後3時に変更できますか？", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "午後2時までチェックアウトを延長する必要があります", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "午後1時にレイトチェックアウトをお願いできますか？", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "午前11時ではなく正午にチェックアウトしたいです", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "出発時間を午後4時に変更してください", "expected_tools": ["modify_checkout_time"]},
        ],
        "transport": [
            {"prompt": "朝6時にSFO空港への送迎をお願いできますか？", "expected_tools": ["request_transport"]},
            {"prompt": "明日の午後3時30分にLAXへの交通手段が必要です", "expected_tools": ["request_transport"]},
            {"prompt": "朝8時に空港への車を手配してください", "expected_tools": ["request_transport"]},
            {"prompt": "朝5時45分にJFKへの空港送迎を予約できますか？", "expected_tools": ["request_transport"]},
            {"prompt": "午後7時にオークランド空港へのタクシーが必要です", "expected_tools": ["request_transport"]},
        ],
        "escalation": [
            {"prompt": "ヘリコプターツアーを予約してもらえますか？", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "明日ヨットをレンタルしたいです", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "夕食にプライベートシェフを手配してもらえますか？", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "部屋にマッサージセラピストを呼んでもらいたいです", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "ワインテイスティング体験を企画してもらえますか？", "expected_tools": ["escalate_to_manager"]},
        ],
        "no_tool": [
            {"prompt": "ご協力ありがとうございました！", "expected_tools": []},
            {"prompt": "今日の調子はいかがですか？", "expected_tools": []},
            {"prompt": "それは素晴らしいです、ありがとう！", "expected_tools": []},
            {"prompt": "おはようございます！", "expected_tools": []},
            {"prompt": "良い一日をお過ごしください！", "expected_tools": []},
        ]
    },
    
    "Arabic": {
        "guest_info": [
            {"prompt": "مرحباً، ما اسمي؟", "expected_tools": ["guest_profile"]},
            {"prompt": "هل يمكنك إخباري عن تفضيلاتي؟", "expected_tools": ["guest_profile"]},
            {"prompt": "هل أنا ضيف VIP؟", "expected_tools": ["guest_profile"]},
            {"prompt": "ما اللغة التي أفضلها؟", "expected_tools": ["guest_profile"]},
            {"prompt": "مرحباً، أنا جديد هنا. هل يمكنك مساعدتي؟", "expected_tools": ["guest_profile"]},
        ],
        "booking_info": [
            {"prompt": "متى أقوم بتسجيل المغادرة؟", "expected_tools": ["booking_details"]},
            {"prompt": "في أي غرفة أقيم؟", "expected_tools": ["booking_details"]},
            {"prompt": "هل يمكنك إظهار تفاصيل حجزي؟", "expected_tools": ["booking_details"]},
            {"prompt": "متى تاريخ تسجيل وصولي؟", "expected_tools": ["booking_details"]},
            {"prompt": "ما نوع الغرفة التي حجزتها؟", "expected_tools": ["booking_details"]},
        ],
        "property_info": [
            {"prompt": "ما كلمة مرور الواي فاي؟", "expected_tools": ["property_info"]},
            {"prompt": "في أي وقت يفتح المسبح؟", "expected_tools": ["property_info"]},
            {"prompt": "هل لديكم صالة رياضية؟", "expected_tools": ["property_info"]},
            {"prompt": "ما المطاعم القريبة؟", "expected_tools": ["property_info"]},
            {"prompt": "أخبرني عن مرافق الفندق", "expected_tools": ["property_info"]},
        ],
        "cleaning": [
            {"prompt": "هل يمكنك تنظيف غرفتي غداً في الساعة 2 مساءً؟", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "أحتاج خدمة التنظيف يوم الجمعة في الساعة 11:00 صباحاً", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "يرجى جدولة تنظيف الغرفة اليوم في الساعة 3:30 مساءً", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "هل يمكنك ترتيب خدمة التنظيف صباح الاثنين في الساعة 10؟", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "أريد تنظيف الغرفة غداً في الساعة 1:00 مساءً", "expected_tools": ["schedule_cleaning"]},
        ],
        "checkout": [
            {"prompt": "هل يمكنني تغيير مغادرتي إلى 3 مساءً؟", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "أحتاج تمديد مغادرتي حتى 2:00 مساءً", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "هل يمكنك إعطائي مغادرة متأخرة في 1 مساءً؟", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "أريد المغادرة في الظهر بدلاً من 11 صباحاً", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "يرجى تغيير وقت مغادرتي إلى 4:00 مساءً", "expected_tools": ["modify_checkout_time"]},
        ],
        "transport": [
            {"prompt": "هل يمكنك الحصول على وسيلة نقل إلى مطار SFO في 6 صباحاً؟", "expected_tools": ["request_transport"]},
            {"prompt": "أحتاج نقل إلى LAX غداً في 3:30 مساءً", "expected_tools": ["request_transport"]},
            {"prompt": "يرجى ترتيب سيارة إلى المطار في 8:00 صباحاً", "expected_tools": ["request_transport"]},
            {"prompt": "هل يمكنك حجز نقل للمطار في 5:45 صباحاً إلى JFK؟", "expected_tools": ["request_transport"]},
            {"prompt": "أحتاج تاكسي إلى مطار أوكلاند في 7 مساءً", "expected_tools": ["request_transport"]},
        ],
        "escalation": [
            {"prompt": "هل يمكنك حجز جولة بالهليكوبتر لي؟", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "أريد استئجار يخت لغد", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "هل يمكنك ترتيب طاهٍ خاص للعشاء؟", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "أحتاج معالج تدليك يأتي إلى غرفتي", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "هل يمكنك تنظيم تجربة تذوق النبيذ؟", "expected_tools": ["escalate_to_manager"]},
        ],
        "no_tool": [
            {"prompt": "شكراً لمساعدتك!", "expected_tools": []},
            {"prompt": "كيف حالك اليوم؟", "expected_tools": []},
            {"prompt": "يبدو ذلك رائعاً، شكراً!", "expected_tools": []},
            {"prompt": "صباح الخير!", "expected_tools": []},
            {"prompt": "أتمنى لك يوماً سعيداً!", "expected_tools": []},
        ]
    },
    
    "Hindi": {
        "guest_info": [
            {"prompt": "नमस्ते, मेरा नाम क्या है?", "expected_tools": ["guest_profile"]},
            {"prompt": "क्या आप मुझे मेरी प्राथमिकताओं के बारे में बता सकते हैं?", "expected_tools": ["guest_profile"]},
            {"prompt": "क्या मैं एक VIP अतिथि हूं?", "expected_tools": ["guest_profile"]},
            {"prompt": "मैं कौन सी भाषा पसंद करता हूं?", "expected_tools": ["guest_profile"]},
            {"prompt": "नमस्ते, मैं यहां नया हूं। क्या आप मेरी मदद कर सकते हैं?", "expected_tools": ["guest_profile"]},
        ],
        "booking_info": [
            {"prompt": "मैं कब चेक आउट करूंगा?", "expected_tools": ["booking_details"]},
            {"prompt": "मैं किस कमरे में रुक रहा हूं?", "expected_tools": ["booking_details"]},
            {"prompt": "क्या आप मुझे मेरी बुकिंग का विवरण दिखा सकते हैं?", "expected_tools": ["booking_details"]},
            {"prompt": "मेरी चेक-इन की तारीख कब है?", "expected_tools": ["booking_details"]},
            {"prompt": "मैंने किस प्रकार का कमरा बुक किया था?", "expected_tools": ["booking_details"]},
        ],
        "property_info": [
            {"prompt": "WiFi का पासवर्ड क्या है?", "expected_tools": ["property_info"]},
            {"prompt": "पूल कितने बजे खुलता है?", "expected_tools": ["property_info"]},
            {"prompt": "क्या आपके पास जिम है?", "expected_tools": ["property_info"]},
            {"prompt": "पास में कौन से रेस्तरां हैं?", "expected_tools": ["property_info"]},
            {"prompt": "होटल की सुविधाओं के बारे में बताइए", "expected_tools": ["property_info"]},
        ],
        "cleaning": [
            {"prompt": "क्या आप कल दोपहर 2 बजे मेरे कमरे की सफाई कर सकते हैं?", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "मुझे शुक्रवार सुबह 11:00 बजे हाउसकीपिंग सेवा चाहिए", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "कृपया आज दोपहर 3:30 बजे कमरे की सफाई का समय निर्धारित करें", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "क्या आप सोमवार सुबह 10 बजे सफाई सेवा की व्यवस्था कर सकते हैं?", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "मुझे कल दोपहर 1:00 बजे रूम सर्विस क्लीनिंग चाहिए", "expected_tools": ["schedule_cleaning"]},
        ],
        "checkout": [
            {"prompt": "क्या मैं अपना चेक आउट 3 बजे कर सकता हूं?", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "मुझे अपना चेक आउट दोपहर 2:00 बजे तक बढ़ाना है", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "क्या आप मुझे दोपहर 1 बजे लेट चेक आउट दे सकते हैं?", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "मैं सुबह 11 बजे के बजाय दोपहर में चेक आउट करना चाहता हूं", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "कृपया मेरा प्रस्थान समय शाम 4:00 बजे कर दें", "expected_tools": ["modify_checkout_time"]},
        ],
        "transport": [
            {"prompt": "क्या आप मुझे सुबह 6 बजे SFO हवाई अड्डे तक पहुंचा सकते हैं?", "expected_tools": ["request_transport"]},
            {"prompt": "मुझे कल दोपहर 3:30 बजे LAX के लिए परिवहन चाहिए", "expected_tools": ["request_transport"]},
            {"prompt": "कृपया सुबह 8:00 बजे हवाई अड्डे के लिए कार की व्यवस्था करें", "expected_tools": ["request_transport"]},
            {"prompt": "क्या आप सुबह 5:45 बजे JFK के लिए हवाई अड्डा परिवहन बुक कर सकते हैं?", "expected_tools": ["request_transport"]},
            {"prompt": "मुझे शाम 7 बजे ओकलैंड हवाई अड्डे के लिए टैक्सी चाहिए", "expected_tools": ["request_transport"]},
        ],
        "escalation": [
            {"prompt": "क्या आप मेरे लिए हेलीकॉप्टर टूर बुक कर सकते हैं?", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "मैं कल के लिए नौका किराए पर लेना चाहता हूं", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "क्या आप रात के खाने के लिए एक निजी रसोइए की व्यवस्था कर सकते हैं?", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "मुझे अपने कमरे में मालिश चिकित्सक की जरूरत है", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "क्या आप वाइन टेस्टिंग अनुभव का आयोजन कर सकते हैं?", "expected_tools": ["escalate_to_manager"]},
        ],
        "no_tool": [
            {"prompt": "आपकी मदद के लिए धन्यवाद!", "expected_tools": []},
            {"prompt": "आज आप कैसे हैं?", "expected_tools": []},
            {"prompt": "यह बहुत अच्छा लगता है, धन्यवाद!", "expected_tools": []},
            {"prompt": "सुप्रभात!", "expected_tools": []},
            {"prompt": "आपका दिन शुभ हो!", "expected_tools": []},
        ]
    },
    
    "Italian": {
        "guest_info": [
            {"prompt": "Ciao, qual è il mio nome?", "expected_tools": ["guest_profile"]},
            {"prompt": "Puoi dirmi le mie preferenze?", "expected_tools": ["guest_profile"]},
            {"prompt": "Sono un ospite VIP?", "expected_tools": ["guest_profile"]},
            {"prompt": "Che lingua preferisco?", "expected_tools": ["guest_profile"]},
            {"prompt": "Ciao, sono nuovo qui. Puoi aiutarmi?", "expected_tools": ["guest_profile"]},
        ],
        "booking_info": [
            {"prompt": "Quando faccio il check-out?", "expected_tools": ["booking_details"]},
            {"prompt": "In che camera sto soggiornando?", "expected_tools": ["booking_details"]},
            {"prompt": "Puoi mostrarmi i dettagli della mia prenotazione?", "expected_tools": ["booking_details"]},
            {"prompt": "Quando è la mia data di check-in?", "expected_tools": ["booking_details"]},
            {"prompt": "Che tipo di camera ho prenotato?", "expected_tools": ["booking_details"]},
        ],
        "property_info": [
            {"prompt": "Qual è la password del WiFi?", "expected_tools": ["property_info"]},
            {"prompt": "A che ora apre la piscina?", "expected_tools": ["property_info"]},
            {"prompt": "Avete una palestra?", "expected_tools": ["property_info"]},
            {"prompt": "Quali ristoranti ci sono nelle vicinanze?", "expected_tools": ["property_info"]},
            {"prompt": "Dimmi dei servizi dell'hotel", "expected_tools": ["property_info"]},
        ],
        "cleaning": [
            {"prompt": "Puoi pulire la mia camera domani alle 14?", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "Ho bisogno del servizio di pulizia venerdì alle 11:00", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "Per favore programma la pulizia della camera per oggi alle 15:30", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "Puoi organizzare il servizio di pulizia per lunedì mattina alle 10?", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "Vorrei la pulizia della camera domani alle 13:00", "expected_tools": ["schedule_cleaning"]},
        ],
        "checkout": [
            {"prompt": "Posso cambiare il mio check-out alle 15?", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "Devo estendere il mio check-out fino alle 14:00", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "Puoi darmi un check-out tardivo alle 13?", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "Voglio fare il check-out a mezzogiorno invece che alle 11", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "Per favore cambia il mio orario di partenza alle 16:00", "expected_tools": ["modify_checkout_time"]},
        ],
        "transport": [
            {"prompt": "Puoi procurarmi un passaggio per l'aeroporto SFO alle 6?", "expected_tools": ["request_transport"]},
            {"prompt": "Ho bisogno di trasporto per LAX domani alle 15:30", "expected_tools": ["request_transport"]},
            {"prompt": "Per favore organizza un'auto per l'aeroporto alle 8:00", "expected_tools": ["request_transport"]},
            {"prompt": "Puoi prenotare un trasporto aeroportuale per le 5:45 per JFK?", "expected_tools": ["request_transport"]},
            {"prompt": "Ho bisogno di un taxi per l'aeroporto di Oakland alle 19", "expected_tools": ["request_transport"]},
        ],
        "escalation": [
            {"prompt": "Puoi prenotarmi un tour in elicottero?", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "Voglio noleggiare uno yacht per domani", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "Puoi organizzare uno chef privato per cena?", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "Ho bisogno di un massaggiatore che venga in camera", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "Puoi organizzare un'esperienza di degustazione vini?", "expected_tools": ["escalate_to_manager"]},
        ],
        "no_tool": [
            {"prompt": "Grazie per il tuo aiuto!", "expected_tools": []},
            {"prompt": "Come stai oggi?", "expected_tools": []},
            {"prompt": "Sembra fantastico, grazie!", "expected_tools": []},
            {"prompt": "Buongiorno!", "expected_tools": []},
            {"prompt": "Buona giornata!", "expected_tools": []},
        ]
    },
    
    "German": {
        "guest_info": [
            {"prompt": "Hallo, wie ist mein Name?", "expected_tools": ["guest_profile"]},
            {"prompt": "Können Sie mir meine Präferenzen mitteilen?", "expected_tools": ["guest_profile"]},
            {"prompt": "Bin ich ein VIP-Gast?", "expected_tools": ["guest_profile"]},
            {"prompt": "Welche Sprache bevorzuge ich?", "expected_tools": ["guest_profile"]},
            {"prompt": "Hallo, ich bin neu hier. Können Sie mir helfen?", "expected_tools": ["guest_profile"]},
        ],
        "booking_info": [
            {"prompt": "Wann checke ich aus?", "expected_tools": ["booking_details"]},
            {"prompt": "In welchem Zimmer übernachte ich?", "expected_tools": ["booking_details"]},
            {"prompt": "Können Sie mir meine Reservierungsdetails zeigen?", "expected_tools": ["booking_details"]},
            {"prompt": "Wann ist mein Check-in-Datum?", "expected_tools": ["booking_details"]},
            {"prompt": "Welchen Zimmertyp habe ich gebucht?", "expected_tools": ["booking_details"]},
        ],
        "property_info": [
            {"prompt": "Wie lautet das WLAN-Passwort?", "expected_tools": ["property_info"]},
            {"prompt": "Um wie viel Uhr öffnet der Pool?", "expected_tools": ["property_info"]},
            {"prompt": "Haben Sie ein Fitnessstudio?", "expected_tools": ["property_info"]},
            {"prompt": "Welche Restaurants gibt es in der Nähe?", "expected_tools": ["property_info"]},
            {"prompt": "Erzählen Sie mir von den Hoteleinrichtungen", "expected_tools": ["property_info"]},
        ],
        "cleaning": [
            {"prompt": "Können Sie mein Zimmer morgen um 14 Uhr reinigen?", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "Ich brauche Reinigungsservice am Freitag um 11:00 Uhr", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "Bitte planen Sie die Zimmerreinigung für heute um 15:30 Uhr", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "Können Sie Reinigungsservice für Montagmorgen um 10 Uhr arrangieren?", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "Ich möchte Zimmerreinigung morgen um 13:00 Uhr", "expected_tools": ["schedule_cleaning"]},
        ],
        "checkout": [
            {"prompt": "Kann ich meinen Check-out auf 15 Uhr ändern?", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "Ich muss meinen Check-out bis 14:00 Uhr verlängern", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "Können Sie mir einen späten Check-out um 13 Uhr geben?", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "Ich möchte um 12 Uhr statt um 11 Uhr auschecken", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "Bitte ändern Sie meine Abreisezeit auf 16:00 Uhr", "expected_tools": ["modify_checkout_time"]},
        ],
        "transport": [
            {"prompt": "Können Sie mir eine Fahrt zum Flughafen SFO um 6 Uhr besorgen?", "expected_tools": ["request_transport"]},
            {"prompt": "Ich brauche Transport nach LAX morgen um 15:30 Uhr", "expected_tools": ["request_transport"]},
            {"prompt": "Bitte organisieren Sie ein Auto zum Flughafen um 8:00 Uhr", "expected_tools": ["request_transport"]},
            {"prompt": "Können Sie Flughafentransport für 5:45 Uhr nach JFK buchen?", "expected_tools": ["request_transport"]},
            {"prompt": "Ich brauche ein Taxi zum Oakland Flughafen um 19 Uhr", "expected_tools": ["request_transport"]},
        ],
        "escalation": [
            {"prompt": "Können Sie mir eine Hubschraubertour buchen?", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "Ich möchte eine Yacht für morgen mieten", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "Können Sie einen Privatkoch für das Abendessen arrangieren?", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "Ich brauche einen Massagetherapeuten in mein Zimmer", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "Können Sie eine Weinverkostung organisieren?", "expected_tools": ["escalate_to_manager"]},
        ],
        "no_tool": [
            {"prompt": "Danke für Ihre Hilfe!", "expected_tools": []},
            {"prompt": "Wie geht es Ihnen heute?", "expected_tools": []},
            {"prompt": "Das klingt großartig, danke!", "expected_tools": []},
            {"prompt": "Guten Morgen!", "expected_tools": []},
            {"prompt": "Haben Sie einen schönen Tag!", "expected_tools": []},
        ]
    },
    
    "Chinese": {
        "guest_info": [
            {"prompt": "你好，我的名字是什么？", "expected_tools": ["guest_profile"]},
            {"prompt": "能告诉我我的偏好吗？", "expected_tools": ["guest_profile"]},
            {"prompt": "我是VIP客人吗？", "expected_tools": ["guest_profile"]},
            {"prompt": "我喜欢哪种语言？", "expected_tools": ["guest_profile"]},
            {"prompt": "你好，我是新来的。你能帮助我吗？", "expected_tools": ["guest_profile"]},
        ],
        "booking_info": [
            {"prompt": "我什么时候退房？", "expected_tools": ["booking_details"]},
            {"prompt": "我住在哪个房间？", "expected_tools": ["booking_details"]},
            {"prompt": "能显示我的预订详情吗？", "expected_tools": ["booking_details"]},
            {"prompt": "我的入住日期是什么时候？", "expected_tools": ["booking_details"]},
            {"prompt": "我预订了什么类型的房间？", "expected_tools": ["booking_details"]},
        ],
        "property_info": [
            {"prompt": "WiFi密码是什么？", "expected_tools": ["property_info"]},
            {"prompt": "游泳池什么时候开放？", "expected_tools": ["property_info"]},
            {"prompt": "你们有健身房吗？", "expected_tools": ["property_info"]},
            {"prompt": "附近有什么餐厅？", "expected_tools": ["property_info"]},
            {"prompt": "告诉我酒店的设施", "expected_tools": ["property_info"]},
        ],
        "cleaning": [
            {"prompt": "明天下午2点能清洁我的房间吗？", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "我需要周五上午11:00的清洁服务", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "请安排今天下午3:30的房间清洁", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "能安排周一上午10点的清洁服务吗？", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "我想要明天下午1:00的房间清洁", "expected_tools": ["schedule_cleaning"]},
        ],
        "checkout": [
            {"prompt": "我能把退房时间改到下午3点吗？", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "我需要把退房时间延长到下午2:00", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "能给我下午1点的延迟退房吗？", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "我想中午退房而不是上午11点", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "请把我的离店时间改到下午4:00", "expected_tools": ["modify_checkout_time"]},
        ],
        "transport": [
            {"prompt": "能安排早上6点到SFO机场的交通吗？", "expected_tools": ["request_transport"]},
            {"prompt": "我需要明天下午3:30到LAX的交通", "expected_tools": ["request_transport"]},
            {"prompt": "请安排早上8:00到机场的车", "expected_tools": ["request_transport"]},
            {"prompt": "能预订早上5:45到JFK的机场交通吗？", "expected_tools": ["request_transport"]},
            {"prompt": "我需要晚上7点到奥克兰机场的出租车", "expected_tools": ["request_transport"]},
        ],
        "escalation": [
            {"prompt": "能为我预订直升机旅游吗？", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "我想明天租一艘游艇", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "能安排晚餐的私人厨师吗？", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "我需要按摩师到我房间", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "能组织品酒体验吗？", "expected_tools": ["escalate_to_manager"]},
        ],
        "no_tool": [
            {"prompt": "谢谢您的帮助！", "expected_tools": []},
            {"prompt": "您今天怎么样？", "expected_tools": []},
            {"prompt": "听起来很棒，谢谢！", "expected_tools": []},
            {"prompt": "早上好！", "expected_tools": []},
            {"prompt": "祝您有美好的一天！", "expected_tools": []},
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
    },
    
    "Portuguese": {
        "guest_info": [
            {"prompt": "Olá, qual é o meu nome?", "expected_tools": ["guest_profile"]},
            {"prompt": "Pode me falar sobre as minhas preferências?", "expected_tools": ["guest_profile"]},
            {"prompt": "Sou um hóspede VIP?", "expected_tools": ["guest_profile"]},
            {"prompt": "Que idioma prefiro?", "expected_tools": ["guest_profile"]},
            {"prompt": "Olá, sou novo aqui. Pode me ajudar?", "expected_tools": ["guest_profile"]},
        ],
        "booking_info": [
            {"prompt": "Quando faço o check-out?", "expected_tools": ["booking_details"]},
            {"prompt": "Em que quarto estou hospedado?", "expected_tools": ["booking_details"]},
            {"prompt": "Pode me mostrar os detalhes da minha reserva?", "expected_tools": ["booking_details"]},
            {"prompt": "Quando é a minha data de check-in?", "expected_tools": ["booking_details"]},
            {"prompt": "Que tipo de quarto reservei?", "expected_tools": ["booking_details"]},
        ],
        "property_info": [
            {"prompt": "Qual é a senha do WiFi?", "expected_tools": ["property_info"]},
            {"prompt": "A que horas abre a piscina?", "expected_tools": ["property_info"]},
            {"prompt": "Têm ginásio?", "expected_tools": ["property_info"]},
            {"prompt": "Que restaurantes há por perto?", "expected_tools": ["property_info"]},
            {"prompt": "Fale-me sobre as comodidades do hotel", "expected_tools": ["property_info"]},
        ],
        "cleaning": [
            {"prompt": "Pode limpar o meu quarto amanhã às 14h?", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "Preciso do serviço de limpeza na sexta-feira às 11:00", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "Por favor, agende a limpeza do quarto para hoje às 15:30", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "Pode organizar o serviço de limpeza para segunda-feira de manhã às 10h?", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "Gostaria de limpeza do quarto amanhã às 13:00", "expected_tools": ["schedule_cleaning"]},
        ],
        "checkout": [
            {"prompt": "Posso mudar o meu check-out para as 15h?", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "Preciso estender o meu check-out até às 14:00", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "Pode me dar um check-out tardio às 13h?", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "Quero fazer check-out ao meio-dia em vez das 11h", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "Por favor, mude o meu horário de partida para as 16:00", "expected_tools": ["modify_checkout_time"]},
        ],
        "transport": [
            {"prompt": "Pode conseguir-me transporte para o aeroporto SFO às 6h?", "expected_tools": ["request_transport"]},
            {"prompt": "Preciso de transporte para LAX amanhã às 15:30", "expected_tools": ["request_transport"]},
            {"prompt": "Por favor, organize um carro para o aeroporto às 8:00", "expected_tools": ["request_transport"]},
            {"prompt": "Pode reservar transporte para o aeroporto às 5:45 para JFK?", "expected_tools": ["request_transport"]},
            {"prompt": "Preciso de um táxi para o aeroporto de Oakland às 19h", "expected_tools": ["request_transport"]},
        ],
        "escalation": [
            {"prompt": "Pode reservar-me um passeio de helicóptero?", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "Quero alugar um iate para amanhã", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "Pode organizar um chef privado para o jantar?", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "Preciso de um massoterapeuta no meu quarto", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "Pode organizar uma experiência de degustação de vinhos?", "expected_tools": ["escalate_to_manager"]},
        ],
        "no_tool": [
            {"prompt": "Obrigado pela sua ajuda!", "expected_tools": []},
            {"prompt": "Como está hoje?", "expected_tools": []},
            {"prompt": "Isso parece ótimo, obrigado!", "expected_tools": []},
            {"prompt": "Bom dia!", "expected_tools": []},
            {"prompt": "Tenha um bom dia!", "expected_tools": []},
        ]
    },
    
    "Korean": {
        "guest_info": [
            {"prompt": "안녕하세요, 제 이름이 뭐예요?", "expected_tools": ["guest_profile"]},
            {"prompt": "제 선호도에 대해 말해주실 수 있나요?", "expected_tools": ["guest_profile"]},
            {"prompt": "저는 VIP 손님인가요?", "expected_tools": ["guest_profile"]},
            {"prompt": "어떤 언어를 선호하나요?", "expected_tools": ["guest_profile"]},
            {"prompt": "안녕하세요, 여기 처음 왔어요. 도와주실 수 있나요?", "expected_tools": ["guest_profile"]},
        ],
        "booking_info": [
            {"prompt": "체크아웃은 언제 하나요?", "expected_tools": ["booking_details"]},
            {"prompt": "어떤 방에 머물고 있나요?", "expected_tools": ["booking_details"]},
            {"prompt": "예약 세부사항을 보여주실 수 있나요?", "expected_tools": ["booking_details"]},
            {"prompt": "체크인 날짜가 언제인가요?", "expected_tools": ["booking_details"]},
            {"prompt": "어떤 타입의 방을 예약했나요?", "expected_tools": ["booking_details"]},
        ],
        "property_info": [
            {"prompt": "WiFi 비밀번호가 뭐예요?", "expected_tools": ["property_info"]},
            {"prompt": "수영장은 몇 시에 열나요?", "expected_tools": ["property_info"]},
            {"prompt": "헬스장이 있나요?", "expected_tools": ["property_info"]},
            {"prompt": "근처에 어떤 레스토랑이 있나요?", "expected_tools": ["property_info"]},
            {"prompt": "호텔 편의시설에 대해 말해주세요", "expected_tools": ["property_info"]},
        ],
        "cleaning": [
            {"prompt": "내일 오후 2시에 방 청소해 주실 수 있나요?", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "금요일 오전 11시에 하우스키핑 서비스가 필요해요", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "오늘 오후 3시 30분에 방 청소를 예약해 주세요", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "월요일 아침 10시에 청소 서비스를 준비해 주실 수 있나요?", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "내일 오후 1시에 룸 서비스 청소를 원해요", "expected_tools": ["schedule_cleaning"]},
        ],
        "checkout": [
            {"prompt": "체크아웃을 오후 3시로 변경할 수 있나요?", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "체크아웃을 오후 2시까지 연장해야 해요", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "오후 1시에 레이트 체크아웃을 해주실 수 있나요?", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "오전 11시 대신 정오에 체크아웃하고 싶어요", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "출발 시간을 오후 4시로 변경해 주세요", "expected_tools": ["modify_checkout_time"]},
        ],
        "transport": [
            {"prompt": "오전 6시에 SFO 공항까지 타서 주실 수 있나요?", "expected_tools": ["request_transport"]},
            {"prompt": "내일 오후 3시 30분에 LAX로 가는 교통편이 필요해요", "expected_tools": ["request_transport"]},
            {"prompt": "오전 8시에 공항까지 차를 준비해 주세요", "expected_tools": ["request_transport"]},
            {"prompt": "오전 5시 45분에 JFK로 가는 공항 교통편을 예약해 주실 수 있나요?", "expected_tools": ["request_transport"]},
            {"prompt": "오후 7시에 오클랜드 공항까지 택시가 필요해요", "expected_tools": ["request_transport"]},
        ],
        "escalation": [
            {"prompt": "헬리콥터 투어를 예약해 주실 수 있나요?", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "내일 요트를 대여하고 싶어요", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "저녁에 개인 셔프를 준비해 주실 수 있나요?", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "방으로 마사지 치료사가 와주었으면 해요", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "와인 시음 체험을 준비해 주실 수 있나요?", "expected_tools": ["escalate_to_manager"]},
        ],
        "no_tool": [
            {"prompt": "도와주셔서 감사합니다!", "expected_tools": []},
            {"prompt": "오늘 어떻게 지내세요?", "expected_tools": []},
            {"prompt": "좋게 들리네요, 감사합니다!", "expected_tools": []},
            {"prompt": "좋은 아침이에요!", "expected_tools": []},
            {"prompt": "좋은 하루 보내세요!", "expected_tools": []},
        ]
    },
    
    "Swedish": {
        "guest_info": [
            {"prompt": "Hej, vad heter jag?", "expected_tools": ["guest_profile"]},
            {"prompt": "Kan du berätta om mina preferenser?", "expected_tools": ["guest_profile"]},
            {"prompt": "Är jag en VIP-gäst?", "expected_tools": ["guest_profile"]},
            {"prompt": "Vilket språk föredrar jag?", "expected_tools": ["guest_profile"]},
            {"prompt": "Hej, jag är ny här. Kan du hjälpa mig?", "expected_tools": ["guest_profile"]},
        ],
        "booking_info": [
            {"prompt": "När checkar jag ut?", "expected_tools": ["booking_details"]},
            {"prompt": "Vilket rum bor jag i?", "expected_tools": ["booking_details"]},
            {"prompt": "Kan du visa mina bokningsdetaljer?", "expected_tools": ["booking_details"]},
            {"prompt": "När är mitt incheckningsdatum?", "expected_tools": ["booking_details"]},
            {"prompt": "Vilken typ av rum har jag bokat?", "expected_tools": ["booking_details"]},
        ],
        "property_info": [
            {"prompt": "Vad är WiFi-lösenordet?", "expected_tools": ["property_info"]},
            {"prompt": "Vilken tid öppnar poolen?", "expected_tools": ["property_info"]},
            {"prompt": "Har ni ett gym?", "expected_tools": ["property_info"]},
            {"prompt": "Vilka restauranger finns i närheten?", "expected_tools": ["property_info"]},
            {"prompt": "Berätta om hotellets bekvämligheter", "expected_tools": ["property_info"]},
        ],
        "cleaning": [
            {"prompt": "Kan du städa mitt rum imorgon klockan 14?", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "Jag behöver städservice på fredag klockan 11:00", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "Varför schemalagd rumstädning idag klockan 15:30", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "Kan du ordna städservice på måndagsmorgon klockan 10?", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "Jag skulle vilja ha rumstädning imorgon klockan 13:00", "expected_tools": ["schedule_cleaning"]},
        ],
        "checkout": [
            {"prompt": "Kan jag ändra min utcheckning till 15?", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "Jag behöver förlänga min utcheckning till 14:00", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "Kan du ge mig sen utcheckning klockan 13?", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "Jag vill checka ut vid lunchtid istället för 11", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "Varför ändra min avresetid till 16:00", "expected_tools": ["modify_checkout_time"]},
        ],
        "transport": [
            {"prompt": "Kan du fixa en resa till SFO flygplats klockan 6?", "expected_tools": ["request_transport"]},
            {"prompt": "Jag behöver transport till LAX imorgon klockan 15:30", "expected_tools": ["request_transport"]},
            {"prompt": "Vänligen ordna en bil till flygplatsen klockan 8:00", "expected_tools": ["request_transport"]},
            {"prompt": "Kan du boka flygplatstransport för 5:45 till JFK?", "expected_tools": ["request_transport"]},
            {"prompt": "Jag behöver en taxi till Oakland flygplats klockan 19", "expected_tools": ["request_transport"]},
        ],
        "escalation": [
            {"prompt": "Kan du boka en helikoptertur för mig?", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "Jag vill hyra en yacht imorgon", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "Kan du ordna en privat kock för middag?", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "Jag behöver en massageterapeut som kommer till mitt rum", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "Kan du organisera en vinprovningsupplevelse?", "expected_tools": ["escalate_to_manager"]},
        ],
        "no_tool": [
            {"prompt": "Tack för din hjälp!", "expected_tools": []},
            {"prompt": "Hur mår du idag?", "expected_tools": []},
            {"prompt": "Det låter bra, tack!", "expected_tools": []},
            {"prompt": "God morgon!", "expected_tools": []},
            {"prompt": "Ha en bra dag!", "expected_tools": []},
        ]
    },
    
    "Russian": {
        "guest_info": [
            {"prompt": "Привет, как меня зовут?", "expected_tools": ["guest_profile"]},
            {"prompt": "Можете рассказать о моих предпочтениях?", "expected_tools": ["guest_profile"]},
            {"prompt": "Я VIP-гость?", "expected_tools": ["guest_profile"]},
            {"prompt": "Какой язык я предпочитаю?", "expected_tools": ["guest_profile"]},
            {"prompt": "Привет, я здесь новичок. Можете помочь?", "expected_tools": ["guest_profile"]},
        ],
        "booking_info": [
            {"prompt": "Когда я выезжаю?", "expected_tools": ["booking_details"]},
            {"prompt": "В каком номере я остановился?", "expected_tools": ["booking_details"]},
            {"prompt": "Можете показать детали моего бронирования?", "expected_tools": ["booking_details"]},
            {"prompt": "Когда дата моего заезда?", "expected_tools": ["booking_details"]},
            {"prompt": "Какой тип номера я забронировал?", "expected_tools": ["booking_details"]},
        ],
        "property_info": [
            {"prompt": "Какой пароль от WiFi?", "expected_tools": ["property_info"]},
            {"prompt": "Во сколько открывается бассейн?", "expected_tools": ["property_info"]},
            {"prompt": "У вас есть спортзал?", "expected_tools": ["property_info"]},
            {"prompt": "Какие рестораны находятся поблизости?", "expected_tools": ["property_info"]},
            {"prompt": "Расскажите об удобствах отеля", "expected_tools": ["property_info"]},
        ],
        "cleaning": [
            {"prompt": "Можете убрать мою комнату завтра в 14:00?", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "Мне нужна уборка в пятницу в 11:00", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "Пожалуйста, запланируйте уборку номера на сегодня в 15:30", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "Можете организовать уборку на понедельник утром в 10:00?", "expected_tools": ["schedule_cleaning"]},
            {"prompt": "Я бы хотел уборку комнаты завтра в 13:00", "expected_tools": ["schedule_cleaning"]},
        ],
        "checkout": [
            {"prompt": "Могу ли я изменить выезд на 15:00?", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "Мне нужно продлить выезд до 14:00", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "Можете дать мне поздний выезд в 13:00?", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "Я хочу выехать в полдень вместо 11:00", "expected_tools": ["modify_checkout_time"]},
            {"prompt": "Пожалуйста, измените время моего отъезда на 16:00", "expected_tools": ["modify_checkout_time"]},
        ],
        "transport": [
            {"prompt": "Можете организовать поездку в аэропорт SFO в 6:00?", "expected_tools": ["request_transport"]},
            {"prompt": "Мне нужен транспорт в LAX завтра в 15:30", "expected_tools": ["request_transport"]},
            {"prompt": "Пожалуйста, организуйте машину в аэропорт в 8:00", "expected_tools": ["request_transport"]},
            {"prompt": "Можете забронировать транспорт в аэропорт на 5:45 в JFK?", "expected_tools": ["request_transport"]},
            {"prompt": "Мне нужно такси в аэропорт Окленд в 19:00", "expected_tools": ["request_transport"]},
        ],
        "escalation": [
            {"prompt": "Можете забронировать мне экскурсию на вертолёте?", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "Я хочу арендовать яхту на завтра", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "Можете организовать личного повара на ужин?", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "Мне нужен массажист, который придёт в мою комнату", "expected_tools": ["escalate_to_manager"]},
            {"prompt": "Можете организовать дегустацию вин?", "expected_tools": ["escalate_to_manager"]},
        ],
        "no_tool": [
            {"prompt": "Спасибо за помощь!", "expected_tools": []},
            {"prompt": "Как дела сегодня?", "expected_tools": []},
            {"prompt": "Звучит отлично, спасибо!", "expected_tools": []},
            {"prompt": "Доброе утро!", "expected_tools": []},
            {"prompt": "Хорошего дня!", "expected_tools": []},
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
                "profil", "statut client", "demandes spéciales", "préféré",
                # Japanese
                "名前", "好み", "VIP", "ゲスト", "プロファイル", "特別", "言語",
                # Arabic
                "اسم", "تفضيلات", "ضيف", "مميز", "ملف", "طلبات", "لغة",
                # Hindi
                "नाम", "प्राथमिकता", "अतिथि", "विशेष", "प्रोफाइल", "भाषा",
                # Italian
                "nome", "preferenze", "ospite", "vip", "profilo", "richieste", "lingua",
                # German
                "name", "präferenzen", "gast", "vip", "profil", "anfragen", "sprache",
                # Chinese
                "名字", "偏好", "客人", "贵宾", "个人资料", "语言",
                # Portuguese
                "nome", "preferências", "hóspede", "vip", "perfil", "solicitações", "idioma",
                # Korean
                "이름", "선호", "손님", "비아이피", "프로필", "요청", "언어",
                # Swedish
                "namn", "preferenser", "gäst", "vip", "profil", "begäranden", "språk",
                # Russian
                "имя", "предпочтения", "гость", "вип", "профиль", "запросы", "язык"
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
                "nuits", "numéro de chambre", "arrivée", "départ",
                # Japanese
                "チェックアウト", "予約", "部屋", "タイプ", "確認", "泊", "到着", "出発",
                # Arabic
                "تسجيل المغادرة", "حجز", "غرفة", "نوع", "تأكيد", "ليالي", "وصول", "مغادرة",
                # Hindi
                "चेक आउट", "बुकिंग", "कमरा", "प्रकार", "पुष्टि", "रात", "आगमन", "प्रस्थान",
                # Italian
                "check-out", "prenotazione", "camera", "tipo", "conferma", "notti", "arrivo", "partenza",
                # German
                "check-out", "reservierung", "zimmer", "typ", "bestätigung", "nächte", "ankunft", "abreise",
                # Chinese
                "退房", "预订", "房间", "类型", "确认", "晚上", "到达", "离开",
                # Portuguese
                "check-out", "reserva", "quarto", "tipo", "confirmação", "noites", "chegada", "partida",
                # Korean
                "체크아웃", "예약", "방", "타입", "확인", "밤", "도착", "출발",
                # Swedish
                "utcheckning", "bokning", "rum", "typ", "bekräftelse", "nätter", "ankomst", "avresa",
                # Russian
                "выезд", "бронирование", "номер", "тип", "подтверждение", "ночи", "прибытие", "отъезд"
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
                "nettoyage de chambre", "service de nettoyage",
                # Japanese
                "掃除", "ハウスキーピング", "清掃", "クリーニング", "部屋掃除",
                # Arabic
                "تنظيف", "خدمة التنظيف", "تنظيف الغرفة", "جدولة",
                # Hindi
                "सफाई", "हाउसकीपिंग", "मेघावन", "कमरा सफाई", "सेवा",
                # Italian
                "pulizia", "servizio pulizie", "pulizia camera", "programmata", "domestiche",
                # German
                "reinigung", "housekeeping", "zimmerreinigung", "reinigungsservice", "geplant",
                # Chinese
                "清洁", "客房服务", "房间清洁", "安排", "清洁服务",
                # Portuguese
                "limpeza", "housekeeping", "limpeza do quarto", "serviço de limpeza", "agendada",
                # Korean
                "청소", "하우스키핑", "방 청소", "청소 서비스", "예약",
                # Swedish
                "städning", "housekeeping", "rumstädning", "städservice", "schemalagd",
                # Russian
                "уборка", "сервис уборки", "уборка номера", "запланирована"
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
                "heure de départ", "heure de sortie",
                # Japanese
                "チェックアウト", "出発", "遅い", "延長", "時間",
                # Arabic
                "مغادرة", "تأخير", "تمديد", "وقت", "تغيير",
                # Hindi
                "चेक आउट", "प्रस्थान", "देर से", "बढ़ाना", "समय",
                # Italian
                "check-out", "partenza", "tardivo", "estendere", "orario",
                # German
                "check-out", "abreise", "später", "verlängern", "zeit",
                # Chinese
                "退房", "离开", "延迟", "延长", "时间",
                # Portuguese
                "check-out", "partida", "tardio", "estender", "horário",
                # Korean
                "체크아웃", "출발", "늘어나다", "연장", "시간",
                # Swedish
                "utcheckning", "avresa", "sen", "förlänga", "tid",
                # Russian
                "выезд", "отъезд", "поздний", "продлить", "время"
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
                "prise en charge", "transfert", "transport",
                # Japanese
                "交通", "タクシー", "車", "空港", "送迎", "移動",
                # Arabic
                "نقل", "تاكسي", "سيارة", "مطار", "رحلة", "ترتيب",
                # Hindi
                "परिवहन", "टैक्सी", "कार", "हवाई अड्डा", "यात्रा", "व्यवस्था",
                # Italian
                "trasporto", "taxi", "auto", "aeroporto", "viaggio", "trasferimento",
                # German
                "transport", "taxi", "auto", "flughafen", "fahrt", "übertragung",
                # Chinese
                "交通", "出租车", "汽车", "机场", "乘车", "接送",
                # Portuguese
                "transporte", "táxi", "carro", "aeroporto", "viagem", "transferência",
                # Korean
                "교통", "택시", "차", "공항", "여행", "이동",
                # Swedish
                "transport", "taxi", "bil", "flygplats", "resa", "överföring",
                # Russian
                "транспорт", "такси", "машина", "аэропорт", "поездка", "перевозка"
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
                "installations", "services", "petit-déjeuner", "parking",
                # Japanese
                "WiFi", "プール", "ジム", "スパ", "レストラン", "設備", "サービス",
                # Arabic
                "واي فاي", "مسبح", "صالة رياضية", "منتجع", "مطعم", "مرافق", "خدمات",
                # Hindi
                "WiFi", "पूल", "जिम", "स्पा", "रेस्तरां", "सुविधाएं", "सेवाएं",
                # Italian
                "wifi", "piscina", "palestra", "spa", "ristorante", "servizi", "strutture",
                # German
                "wlan", "pool", "fitnessstudio", "spa", "restaurant", "einrichtungen", "service",
                # Chinese
                "WiFi", "游泳池", "健身房", "水疗", "餐厅", "设施", "服务",
                # Portuguese
                "wifi", "piscina", "ginásio", "spa", "restaurante", "comodidades", "serviços",
                # Korean
                "WiFi", "수영장", "헬스장", "스파", "레스토랑", "편의시설", "서비스",
                # Swedish
                "wifi", "pool", "gym", "spa", "restaurang", "bekvämligheter", "service",
                # Russian
                "вайфай", "бассейн", "спортзал", "спа", "ресторан", "удобства", "сервис"
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
                "escalade", "gestionnaire va", "vous contacter",
                # Japanese
                "マネージャー", "管理者", "エスカレーション", "転送", "連絡",
                # Arabic
                "مدير", "إدارة", "تصعيد", "إحالة", "اتصال",
                # Hindi
                "मैनेजर", "प्रबंधक", "एस्कलेशन", "भेजा", "संपर्क",
                # Italian
                "manager", "direttore", "escalation", "inoltrato", "contattare",
                # German
                "manager", "direktor", "eskalation", "weitergeleitet", "kontaktieren",
                # Chinese
                "经理", "管理员", "上报", "转发", "联系",
                # Portuguese
                "gerente", "administrador", "escalation", "encaminhado", "contato",
                # Korean
                "매니저", "관리자", "에스케이레이션", "전달", "연락",
                # Swedish
                "manager", "chef", "eskalation", "vidarebefordrad", "kontakta",
                # Russian
                "менеджер", "управляющий", "эскалация", "передано", "связь"
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
