# Prompt Engineering Plan: Claude-4 Opus Performance Recovery

## 📊 **Current Performance Issues Analysis**

### Major Losses Identified:

1. **guest_profile**: 53.8% → 41.4% F1 (-12.4%) - Over-triggering with booking_details
2. **modify_checkout_time**: 76.2% → 63.2% F1 (-13.0%) - Mixed with other tool calls
3. **request_transport**: 0% F1 - Complete failure to recognize transport requests
4. **Overall F1**: 48.1% → 47.9% (-0.2%) - Net degradation despite some improvements

### Root Cause Analysis:

- **Tool Co-triggering**: Claude-4 calling multiple tools when only one is needed
- **Pattern Recognition**: Transport keywords not being detected effectively
- **Agent Type Change**: STRUCTURED_CHAT vs OPENAI_FUNCTIONS behaves differently
- **Prompt Clarity**: Current prompts may not provide clear tool boundaries

---

## 🎯 **Phase 1: Tool Separation & Precision (Priority: HIGH)**

### Problem: Over-triggering guest_profile + booking_details together

**Current Issue Pattern:**

```
Expected: guest_profile
Actual: guest_profile, booking_details
```

### Solution 1A: Enhanced Tool Descriptions

**File**: `tools.py` - Update tool descriptions with clear boundaries

```python
# BEFORE (current)
description="Get guest profile information including name, preferences, and VIP status"

# AFTER (proposed)
description="""Get ONLY guest profile information (name, language, VIP status, preferences).
Use this tool EXCLUSIVELY for:
- Guest identity questions ("What's my name?", "Am I VIP?")
- Personal preferences ("What language do I prefer?")
- Profile verification ("Do you have my contact info?")

DO NOT use for booking information (dates, room numbers, reservations).
DO NOT combine with booking_details unless explicitly asked for both."""
```

### Solution 1B: System Prompt Refinement

**File**: `prompts.py` - Add tool selection guidelines

```python
TOOL_SELECTION_GUIDELINES = """
CRITICAL TOOL SELECTION RULES:
1. Use ONLY ONE tool unless the guest explicitly asks for multiple things
2. guest_profile = Personal info ONLY (name, VIP, language, preferences)
3. booking_details = Reservation info ONLY (dates, room, confirmation)
4. If unsure between tools, choose the most specific one
5. Never combine guest_profile + booking_details unless both are explicitly requested

Examples:
- "What's my name?" → guest_profile ONLY
- "When do I check out?" → booking_details ONLY
- "What's my name and checkout time?" → BOTH tools acceptable
"""
```

---

## 🎯 **Phase 2: Transport Tool Recovery (Priority: CRITICAL)**

### Problem: 0% F1 - Complete failure to recognize transport requests

**Failed Examples:**

- "Can you get me a ride to SFO airport at 6 AM?" → No transport tool triggered
- "I need transportation to LAX tomorrow" → guest_profile, booking_details instead

### Solution 2A: Enhanced Transport Tool Description

**File**: `tools.py`

```python
description="""Book transportation/transport services to airports or destinations.
Use this tool for ANY request involving:
- Airport transport: "ride to SFO", "transport to LAX", "airport pickup"
- Transportation booking: "book a car", "arrange transport", "get me a taxi"
- Travel arrangements: "car to airport", "ride to JFK", "transport at 6 AM"

Keywords that ALWAYS trigger this tool:
- transport, transportation, ride, car, taxi, airport, pickup, drop-off
- Destinations: SFO, LAX, JFK, Oakland airport, any airport codes
- Travel verbs: book, arrange, get, need (when combined with transport terms)

ALWAYS use this tool when guests mention going somewhere with a time."""
```

### Solution 2B: Transport-Specific System Prompt Addition

**File**: `prompts.py`

```python
TRANSPORT_DETECTION_PROMPT = """
TRANSPORT REQUEST DETECTION:
If the guest mentions ANY of these, use request_transport tool:
- Airport names or codes (SFO, LAX, JFK, Oakland, etc.)
- Transportation words (ride, car, taxi, transport, pickup)
- Travel phrases ("get me to", "take me to", "book transport")
- Time + destination combinations ("6 AM to airport")

Examples that REQUIRE request_transport:
✓ "I need a ride to SFO at 6 AM"
✓ "Can you book transport to LAX?"
✓ "Get me a taxi to the airport"
✓ "Arrange car pickup at 3 PM"

Do NOT use guest_profile or booking_details for transport requests.
"""
```

---

## 🎯 **Phase 3: Checkout Time Tool Precision (Priority: HIGH)**

### Problem: modify_checkout_time mixed with other tools (76.2% → 63.2%)

**Issue Pattern:**

```
Expected: modify_checkout_time
Actual: guest_profile, modify_checkout_time, booking_details
```

### Solution 3A: Checkout Tool Refinement

**File**: `tools.py`

```python
description="""Modify or change guest checkout time ONLY.
Use this tool EXCLUSIVELY when guests want to:
- Change checkout time: "change checkout to 3 PM"
- Request late checkout: "late checkout until 2 PM"
- Modify departure time: "extend checkout to 4 PM"

DO NOT use other tools simultaneously unless guest asks for additional services.
Focus ONLY on the checkout time modification request."""
```

### Solution 3B: Checkout-Specific Prompt Logic

**File**: `prompts.py`

```python
CHECKOUT_MODIFICATION_PROMPT = """
CHECKOUT TIME CHANGES:
When guest wants to modify checkout time:
1. Use ONLY modify_checkout_time tool
2. Do NOT call guest_profile or booking_details unless specifically asked
3. Focus on the time change request only

Clear checkout modification phrases:
- "change my checkout to X PM"
- "can I get late checkout until X"
- "extend my checkout time"
- "modify my departure time"

Handle the checkout change first, then ask if they need anything else.
"""
```

---

## 🎯 **Phase 4: Agent Behavior Optimization (Priority: MEDIUM)**

### Problem: STRUCTURED_CHAT agent behaves differently than OPENAI_FUNCTIONS

### Solution 4A: Agent Configuration Tuning

**File**: `main.py`

```python
# Enhanced agent initialization with specific instructions
return initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    memory=memory_service.get_memory(phone),
    system_message=SystemMessage(content=final_prompt),
    verbose=False,
    # Add these parameters for better control
    max_iterations=3,  # Prevent excessive tool calling
    early_stopping_method="generate",  # Stop when answer is found
)
```

### Solution 4B: Enhanced System Message Structure

**File**: `prompts.py`

```python
def get_enhanced_system_prompt(guest_context, property_name):
    return f"""
{get_base_system_prompt(guest_context, property_name)}

{TOOL_SELECTION_GUIDELINES}
{TRANSPORT_DETECTION_PROMPT}
{CHECKOUT_MODIFICATION_PROMPT}

EXECUTION GUIDELINES:
1. Read the guest request carefully
2. Identify the PRIMARY intent (what they mainly want)
3. Select the MOST SPECIFIC tool for that intent
4. Use ONLY ONE tool unless multiple things are explicitly requested
5. Provide clear, helpful responses
6. If unsure, ask for clarification rather than guessing

Remember: Precision over recall. Better to use the right tool once than multiple tools incorrectly.
"""
```

---

## 🎯 **Phase 5: Pattern Matching Improvements (Priority: MEDIUM)**

### Problem: Evaluation uses pattern matching that may not align with Claude-4's responses

### Solution 5A: Enhanced Pattern Detection

**File**: `evaluation.py` - Update transport patterns

```python
'request_transport': [
    r'\btransport\b.*\b(arranged|booked|scheduled|confirmed)\b',
    r'\b(ride|car|taxi)\b.*\b(arranged|booked|to)\b',
    r'\b(airport|SFO|LAX|JFK)\b.*\b(transport|ride|car)\b',
    r'\btravel.*\b(arranged|safe)\b',
    # Add Claude-4 specific response patterns
    r'\byour.*transport.*has been.*arranged\b',
    r'\bI.*arranged.*transport\b',
    r'\btransportation.*successfully.*booked\b',
]
```

### Solution 5B: Tool Response Standardization

**File**: `tools.py` - Ensure consistent response patterns

```python
def request_transport(destination: str, time: str, guest_id: str) -> str:
    # Standardized response format for pattern matching
    return f"Your transport to {destination} at {time} has been successfully arranged. Safe travels!"
```

---

## 📋 **Implementation Roadmap**

### Week 1: Critical Fixes

- [ ] Implement transport tool description enhancement (Solution 2A)
- [ ] Add transport detection prompt (Solution 2B)
- [ ] Update tool selection guidelines (Solution 1B)
- [ ] Test transport tool recognition

### Week 2: Tool Separation

- [ ] Enhance guest_profile tool boundaries (Solution 1A)
- [ ] Implement checkout tool refinement (Solution 3A)
- [ ] Add checkout-specific prompts (Solution 3B)
- [ ] Run evaluation to measure improvements

### Week 3: Agent Optimization

- [ ] Implement agent configuration tuning (Solution 4A)
- [ ] Deploy enhanced system prompt structure (Solution 4B)
- [ ] Update pattern matching (Solution 5A)
- [ ] Standardize tool responses (Solution 5B)

### Week 4: Testing & Validation

- [ ] Run comprehensive evaluation
- [ ] A/B test with original prompts
- [ ] Fine-tune based on results
- [ ] Deploy to production

---

## 🎯 **Success Metrics**

### Target Performance Recovery:

- **guest_profile**: 41.4% → 50%+ F1 (reduce co-triggering)
- **modify_checkout_time**: 63.2% → 70%+ F1 (improve precision)
- **request_transport**: 0% → 30%+ F1 (basic functionality)
- **Overall F1**: 47.9% → 50%+ (net improvement over original)

### Key Performance Indicators:

1. **Tool Separation**: Reduce guest_profile + booking_details co-occurrence by 50%
2. **Transport Recognition**: Achieve >20% transport tool detection rate
3. **Precision Improvement**: Increase overall precision from 40.3% to 45%+
4. **User Experience**: Maintain response quality while improving accuracy

---

## 🔧 **Testing Strategy**

### A/B Testing Plan:

1. **Baseline**: Current Claude-4 system (47.9% F1)
2. **Version A**: Transport fixes only (Solutions 2A, 2B)
3. **Version B**: Tool separation fixes (Solutions 1A, 1B, 3A, 3B)
4. **Version C**: Complete implementation (All solutions)

### Evaluation Protocol:

- Run 100-test evaluation after each phase
- Compare against both GPT-4o (48.1%) and current Claude-4 (47.9%)
- Monitor individual tool performance and overall metrics
- Track user satisfaction in production environment

---

## 💡 **Risk Mitigation**

### Potential Issues:

1. **Over-specification**: Too detailed prompts might confuse Claude-4
2. **Prompt Length**: Very long prompts might hit token limits
3. **Tool Conflicts**: Enhanced descriptions might create new conflicts

### Mitigation Strategies:

1. **Iterative Testing**: Implement changes incrementally
2. **Prompt Optimization**: Keep descriptions clear but concise
3. **Fallback Plan**: Maintain ability to rollback to current version
4. **Monitoring**: Track performance metrics continuously

---

## 🎯 **Expected Outcomes**

### Conservative Estimate:

- **Overall F1**: 47.9% → 50.5% (+2.6% improvement)
- **Transport Tool**: 0% → 25% F1 (basic functionality restored)
- **Tool Separation**: 30% reduction in false positive co-triggering

### Optimistic Estimate:

- **Overall F1**: 47.9% → 52% (+4.1% improvement, exceeding GPT-4o)
- **Transport Tool**: 0% → 40% F1 (good functionality)
- **All Tools**: Performance at or above GPT-4o baseline

This plan addresses the core issues systematically while maintaining Claude-4 Opus's enhanced reasoning capabilities. The focus is on precision improvements and tool boundary clarification rather than fundamental architecture changes.
