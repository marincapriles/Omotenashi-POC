# 📱 Authentication API Contract

## Phone Verification System for Omotenashi Concierge

### 🎯 **Purpose**
Secure guest authentication using phone number verification via SMS (Twilio integration) to ensure guest identity and prevent unauthorized access to concierge services.

---

## 🔌 **API Endpoints**

### **1. Request Phone Verification**

**Endpoint**: `POST /auth/request-verification`

**Purpose**: Initiate SMS verification for guest phone number

**Request Body**:
```json
{
  "phone_number": "+14155550123",
  "language": "en"  // Optional: for SMS language preference
}
```

**Response** (Success - 200):
```json
{
  "success": true,
  "verification_id": "ver_abc123def456",
  "message": "Verification code sent to +14155550123",
  "expires_in_seconds": 300,
  "can_resend_after_seconds": 60
}
```

**Response** (Error - 400):
```json
{
  "success": false,
  "error_code": "INVALID_PHONE_NUMBER",
  "message": "Phone number format is invalid",
  "details": "Phone number must include country code"
}
```

**Response** (Rate Limited - 429):
```json
{
  "success": false,
  "error_code": "RATE_LIMITED",
  "message": "Too many verification requests",
  "retry_after_seconds": 300
}
```

---

### **2. Verify Phone Code**

**Endpoint**: `POST /auth/verify-code`

**Purpose**: Validate SMS verification code and create authenticated session

**Request Body**:
```json
{
  "verification_id": "ver_abc123def456",
  "code": "123456",
  "phone_number": "+14155550123"
}
```

**Response** (Success - 200):
```json
{
  "success": true,
  "access_token": "jwt_token_here",
  "token_type": "Bearer",
  "expires_in_seconds": 86400,
  "guest": {
    "guest_id": "g1",
    "name": "Carlos Marin",
    "phone_number": "+14155550123",
    "preferred_language": "English",
    "vip_status": true
  },
  "current_booking": {
    "booking_id": "b1",
    "property_id": "villa_azul",
    "property_name": "Villa Azul",
    "check_in_date": "2025-06-10T15:00:00Z",
    "check_out_date": "2025-06-17T11:00:00Z",
    "room_type": "Deluxe Suite"
  }
}
```

**Response** (Invalid Code - 400):
```json
{
  "success": false,
  "error_code": "INVALID_CODE",
  "message": "Verification code is incorrect",
  "attempts_remaining": 2
}
```

**Response** (Expired - 400):
```json
{
  "success": false,
  "error_code": "CODE_EXPIRED",
  "message": "Verification code has expired",
  "can_request_new": true
}
```

---

### **3. Refresh Access Token**

**Endpoint**: `POST /auth/refresh-token`

**Purpose**: Refresh expired access token for continued session

**Request Headers**:
```
Authorization: Bearer {access_token}
```

**Request Body**:
```json
{
  "phone_number": "+14155550123"
}
```

**Response** (Success - 200):
```json
{
  "success": true,
  "access_token": "new_jwt_token_here",
  "token_type": "Bearer",
  "expires_in_seconds": 86400
}
```

---

### **4. Logout/End Session**

**Endpoint**: `POST /auth/logout`

**Purpose**: Invalidate current session and access token

**Request Headers**:
```
Authorization: Bearer {access_token}
```

**Response** (Success - 200):
```json
{
  "success": true,
  "message": "Session ended successfully"
}
```

---

## 🔒 **Security Specifications**

### **JWT Token Structure**
```json
{
  "sub": "g1",                    // Guest ID
  "phone": "+14155550123",        // Phone number
  "iat": 1640995200,             // Issued at
  "exp": 1641081600,             // Expires at
  "property_id": "villa_azul",    // Current property context
  "vip": true,                   // VIP status for authorization
  "role": "guest"                // Role-based access
}
```

### **Rate Limiting Rules**
- **SMS Requests**: 5 per phone number per hour
- **Verification Attempts**: 3 per verification_id
- **API Calls**: 100 per authenticated session per hour

### **Phone Number Validation**
- Must include country code (E.164 format)
- Supported countries: US (+1), Canada (+1), Mexico (+52)
- Blocked: VoIP numbers, temporary numbers

### **SMS Security**
- Codes: 6-digit numeric, cryptographically random
- Expiry: 5 minutes
- Single use only
- Rate limited per phone number

---

## 🛡️ **Middleware Integration**

### **Authentication Middleware**

**Purpose**: Protect concierge endpoints with token validation

**Usage**:
```python
@app.middleware("http")
async def authenticate_request(request: Request, call_next):
    # Skip auth for public endpoints
    if request.url.path in ["/", "/auth/request-verification", "/auth/verify-code"]:
        return await call_next(request)
    
    # Extract and validate JWT token
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={"error": "Missing or invalid authorization header"}
        )
    
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        request.state.guest_id = payload["sub"]
        request.state.phone_number = payload["phone"]
        request.state.vip_status = payload["vip"]
        request.state.property_id = payload["property_id"]
    except jwt.ExpiredSignatureError:
        return JSONResponse(
            status_code=401,
            content={"error": "Token has expired"}
        )
    except jwt.InvalidTokenError:
        return JSONResponse(
            status_code=401,
            content={"error": "Invalid token"}
        )
    
    return await call_next(request)
```

---

## 🔧 **Frontend Integration**

### **Authentication Flow for Ryokan-chan**

**1. Phone Number Entry**:
```javascript
// Guest enters phone number
const requestVerification = async (phoneNumber) => {
  const response = await fetch('/auth/request-verification', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone_number: phoneNumber })
  });
  
  const data = await response.json();
  if (data.success) {
    // Show code entry form
    showCodeEntryForm(data.verification_id);
  } else {
    // Show error message
    showError(data.message);
  }
};
```

**2. Code Verification**:
```javascript
// Guest enters SMS code
const verifyCode = async (verificationId, code, phoneNumber) => {
  const response = await fetch('/auth/verify-code', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      verification_id: verificationId,
      code: code,
      phone_number: phoneNumber
    })
  });
  
  const data = await response.json();
  if (data.success) {
    // Store token and guest info
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('guest_info', JSON.stringify(data.guest));
    
    // Initialize chat interface with guest context
    initializeChatInterface(data.guest, data.current_booking);
  } else {
    showError(data.message);
  }
};
```

**3. Authenticated API Calls**:
```javascript
// All subsequent API calls include authentication
const sendMessage = async (message) => {
  const token = localStorage.getItem('access_token');
  const response = await fetch('/message', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      message: message,
      // phone_number no longer needed - extracted from token
    })
  });
  
  if (response.status === 401) {
    // Token expired - redirect to login
    redirectToLogin();
    return;
  }
  
  return response.json();
};
```

---

## 📊 **Error Handling**

### **Standard Error Codes**
| Code | HTTP Status | Description | Action |
|------|-------------|-------------|---------|
| `INVALID_PHONE_NUMBER` | 400 | Phone format invalid | Show format example |
| `PHONE_NOT_FOUND` | 404 | No guest record | Offer registration |
| `RATE_LIMITED` | 429 | Too many requests | Show retry timer |
| `INVALID_CODE` | 400 | Wrong verification code | Allow retry |
| `CODE_EXPIRED` | 400 | Code expired | Offer new code |
| `TOKEN_EXPIRED` | 401 | JWT token expired | Refresh or re-login |
| `TOKEN_INVALID` | 401 | JWT token invalid | Force re-login |
| `SMS_FAILED` | 500 | SMS delivery failed | Retry mechanism |

### **Graceful Degradation**
- If SMS service fails: Offer alternative contact method
- If database unavailable: Cache authentication temporarily
- If rate limits hit: Queue verification requests

---

## 🔄 **Migration Strategy**

### **Phase 1: Backward Compatibility**
- Keep existing phone_number parameter in `/message` endpoint
- Add optional Authorization header support
- Log both authentication methods for analytics

### **Phase 2: Token-Only**
- Remove phone_number parameter requirement
- Extract guest context from JWT token
- Redirect unauthenticated requests to login

### **Database Changes Required**:
```sql
-- Add authentication tracking
ALTER TABLE conversation_sessions 
ADD COLUMN auth_method ENUM('phone_param', 'jwt_token') DEFAULT 'phone_param';

-- Add session tokens
ALTER TABLE conversation_sessions 
ADD COLUMN access_token_hash VARCHAR(255);
```

---

## 🎋 **Coordination with Ryokan-chan**

### **Frontend Implementation Tasks**:
1. **Phone entry form** with international formatting
2. **SMS code entry** with resend functionality  
3. **Token storage** and automatic refresh
4. **Error handling** for all auth scenarios
5. **Guest info display** from authenticated context

### **API Integration Points**:
- Replace phone_number parameter with token authentication
- Update guest context retrieval from token payload
- Handle authentication errors gracefully in chat interface

### **Testing Requirements**:
- Test with all supported phone number formats
- Verify SMS delivery across carriers
- Test token expiry and refresh flows
- Validate rate limiting behavior

---

**🤝 Ready for Ryokan-chan Integration**: This contract provides complete authentication foundation for secure guest verification while maintaining existing functionality during migration.