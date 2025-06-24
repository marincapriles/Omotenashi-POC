-- 🏨 Omotenashi Hotel Concierge Database Schema
-- Designed for customer pilot deployment
-- Compatible with PostgreSQL/MySQL production systems

-- =============================================================================
-- CORE TABLES
-- =============================================================================

-- Properties/Vacation Rentals
CREATE TABLE properties (
    property_id VARCHAR(50) PRIMARY KEY,
    property_name VARCHAR(255) NOT NULL,
    property_type VARCHAR(100) DEFAULT 'vacation_rental', -- villa, apartment, house, etc.
    location VARCHAR(255),
    address TEXT,
    amenities JSON, -- Flexible storage for property features
    check_in_time TIME DEFAULT '15:00:00',
    check_out_time TIME DEFAULT '11:00:00',
    max_guests INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Guest Profiles  
CREATE TABLE guests (
    guest_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20) NOT NULL UNIQUE, -- Primary identifier for sessions
    email VARCHAR(255),
    preferred_language VARCHAR(10) NOT NULL DEFAULT 'English',
    vip_status BOOLEAN DEFAULT FALSE,
    dietary_restrictions TEXT, -- JSON or TEXT for special requirements
    accessibility_needs TEXT,
    emergency_contact JSON, -- {name, phone, relationship}
    guest_preferences JSON, -- Flexible storage for preferences
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_phone_number (phone_number),
    INDEX idx_vip_status (vip_status),
    INDEX idx_preferred_language (preferred_language)
);

-- Bookings/Reservations
CREATE TABLE bookings (
    booking_id VARCHAR(50) PRIMARY KEY,
    guest_id VARCHAR(50) NOT NULL,
    property_id VARCHAR(50) NOT NULL,
    check_in_date DATETIME NOT NULL,
    check_out_date DATETIME NOT NULL,
    number_of_guests INTEGER DEFAULT 1,
    room_type VARCHAR(100),
    booking_status ENUM('confirmed', 'checked_in', 'checked_out', 'cancelled') DEFAULT 'confirmed',
    total_amount DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'USD',
    special_requests TEXT,
    booking_source VARCHAR(100), -- airbnb, direct, vrbo, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (guest_id) REFERENCES guests(guest_id) ON DELETE CASCADE,
    FOREIGN KEY (property_id) REFERENCES properties(property_id) ON DELETE CASCADE,
    INDEX idx_guest_id (guest_id),
    INDEX idx_property_id (property_id),
    INDEX idx_check_in_date (check_in_date),
    INDEX idx_check_out_date (check_out_date),
    INDEX idx_booking_status (booking_status)
);

-- =============================================================================
-- CONVERSATION & SESSION MANAGEMENT
-- =============================================================================

-- Conversation Sessions
CREATE TABLE conversation_sessions (
    session_id VARCHAR(100) PRIMARY KEY, -- phone_number for now
    guest_id VARCHAR(50),
    property_id VARCHAR(50),
    session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_end TIMESTAMP NULL,
    session_status ENUM('active', 'ended', 'expired') DEFAULT 'active',
    total_messages INTEGER DEFAULT 0,
    tools_used JSON, -- Array of tools used in session
    guest_satisfaction INTEGER, -- 1-5 rating if provided
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (guest_id) REFERENCES guests(guest_id) ON DELETE SET NULL,
    FOREIGN KEY (property_id) REFERENCES properties(property_id) ON DELETE SET NULL,
    INDEX idx_guest_id (guest_id),
    INDEX idx_session_status (session_status),
    INDEX idx_session_start (session_start)
);

-- Individual Messages
CREATE TABLE conversation_messages (
    message_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    message_type ENUM('user', 'assistant', 'system') NOT NULL,
    message_content TEXT NOT NULL,
    tools_used JSON, -- Array of tools used for this specific message
    response_time_ms INTEGER, -- Response time for assistant messages
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (session_id) REFERENCES conversation_sessions(session_id) ON DELETE CASCADE,
    INDEX idx_session_id (session_id),
    INDEX idx_message_type (message_type),
    INDEX idx_timestamp (timestamp)
);

-- =============================================================================
-- TOOL USAGE & ANALYTICS
-- =============================================================================

-- Tool Usage Tracking
CREATE TABLE tool_usage_logs (
    log_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    guest_id VARCHAR(50),
    tool_name VARCHAR(100) NOT NULL,
    tool_category ENUM('core', 'high_impact', 'luxury') NOT NULL,
    success BOOLEAN NOT NULL,
    execution_time_ms INTEGER,
    error_message TEXT,
    tool_parameters JSON, -- Parameters passed to tool
    tool_response JSON, -- Tool response data
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (session_id) REFERENCES conversation_sessions(session_id) ON DELETE CASCADE,
    FOREIGN KEY (guest_id) REFERENCES guests(guest_id) ON DELETE SET NULL,
    INDEX idx_session_id (session_id),
    INDEX idx_guest_id (guest_id),
    INDEX idx_tool_name (tool_name),
    INDEX idx_tool_category (tool_category),
    INDEX idx_success (success),
    INDEX idx_timestamp (timestamp)
);

-- Service Requests (generated by tools)
CREATE TABLE service_requests (
    request_id VARCHAR(100) PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    guest_id VARCHAR(50) NOT NULL,
    property_id VARCHAR(50) NOT NULL,
    service_type VARCHAR(100) NOT NULL, -- cleaning, transport, restaurant, spa, etc.
    service_category ENUM('core', 'high_impact', 'luxury') NOT NULL,
    request_details JSON NOT NULL, -- Service-specific parameters
    request_status ENUM('pending', 'confirmed', 'in_progress', 'completed', 'cancelled') DEFAULT 'pending',
    scheduled_datetime DATETIME,
    completion_datetime DATETIME,
    provider_name VARCHAR(255), -- Restaurant, spa, transport company, etc.
    cost DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'USD',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (session_id) REFERENCES conversation_sessions(session_id) ON DELETE CASCADE,
    FOREIGN KEY (guest_id) REFERENCES guests(guest_id) ON DELETE CASCADE,
    FOREIGN KEY (property_id) REFERENCES properties(property_id) ON DELETE CASCADE,
    INDEX idx_guest_id (guest_id),
    INDEX idx_property_id (property_id),
    INDEX idx_service_type (service_type),
    INDEX idx_service_category (service_category),
    INDEX idx_request_status (request_status),
    INDEX idx_scheduled_datetime (scheduled_datetime)
);

-- =============================================================================
-- AUTHENTICATION & SECURITY
-- =============================================================================

-- Phone Verification for Guest Authentication
CREATE TABLE phone_verifications (
    verification_id VARCHAR(100) PRIMARY KEY,
    phone_number VARCHAR(20) NOT NULL,
    verification_code VARCHAR(10) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    verified BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMP NULL,
    attempts INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_phone_number (phone_number),
    INDEX idx_verification_code (verification_code),
    INDEX idx_expires_at (expires_at)
);

-- API Keys and Access Control (for future multi-property support)
CREATE TABLE api_access (
    access_id VARCHAR(100) PRIMARY KEY,
    property_id VARCHAR(50) NOT NULL,
    api_key_hash VARCHAR(255) NOT NULL,
    access_level ENUM('read_only', 'full_access', 'admin') DEFAULT 'full_access',
    rate_limit_per_hour INTEGER DEFAULT 1000,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP NULL,
    
    FOREIGN KEY (property_id) REFERENCES properties(property_id) ON DELETE CASCADE,
    INDEX idx_property_id (property_id),
    INDEX idx_api_key_hash (api_key_hash),
    INDEX idx_is_active (is_active)
);

-- =============================================================================
-- BUSINESS ANALYTICS & REPORTING
-- =============================================================================

-- Daily/Weekly Performance Metrics
CREATE TABLE performance_metrics (
    metric_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    property_id VARCHAR(50),
    metric_date DATE NOT NULL,
    total_sessions INTEGER DEFAULT 0,
    total_messages INTEGER DEFAULT 0,
    unique_guests INTEGER DEFAULT 0,
    average_session_length_minutes DECIMAL(5,2),
    total_tools_used INTEGER DEFAULT 0,
    success_rate_percentage DECIMAL(5,2),
    guest_satisfaction_average DECIMAL(3,2),
    top_tools_used JSON, -- Array of {tool_name, usage_count}
    revenue_generated DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'USD',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (property_id) REFERENCES properties(property_id) ON DELETE CASCADE,
    UNIQUE KEY unique_property_date (property_id, metric_date),
    INDEX idx_property_id (property_id),
    INDEX idx_metric_date (metric_date)
);

-- =============================================================================
-- INITIAL DATA FOR PILOT
-- =============================================================================

-- Insert sample property (Villa Azul)
INSERT INTO properties (property_id, property_name, property_type, location, amenities, max_guests) VALUES
('villa_azul', 'Villa Azul', 'luxury_villa', 'Costa Rica, Manuel Antonio', 
 '{"pool": true, "spa": true, "gym": true, "wifi": true, "kitchen": true, "concierge": true, "ocean_view": true}', 
 8);

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

-- Composite indexes for common queries
CREATE INDEX idx_active_sessions ON conversation_sessions(session_status, session_start);
CREATE INDEX idx_guest_bookings ON bookings(guest_id, check_in_date, check_out_date);
CREATE INDEX idx_recent_messages ON conversation_messages(session_id, timestamp);
CREATE INDEX idx_tool_analytics ON tool_usage_logs(tool_name, timestamp, success);
CREATE INDEX idx_service_tracking ON service_requests(guest_id, service_type, request_status);

-- =============================================================================
-- VIEWS FOR COMMON QUERIES
-- =============================================================================

-- Active Guest Sessions with Guest Info
CREATE VIEW active_guest_sessions AS
SELECT 
    cs.session_id,
    cs.guest_id,
    g.name as guest_name,
    g.phone_number,
    g.preferred_language,
    g.vip_status,
    cs.property_id,
    p.property_name,
    cs.session_start,
    cs.total_messages,
    cs.tools_used
FROM conversation_sessions cs
JOIN guests g ON cs.guest_id = g.guest_id
JOIN properties p ON cs.property_id = p.property_id
WHERE cs.session_status = 'active';

-- Tool Performance Summary
CREATE VIEW tool_performance_summary AS
SELECT 
    tool_name,
    tool_category,
    COUNT(*) as total_uses,
    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_uses,
    (SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as success_rate,
    AVG(execution_time_ms) as avg_execution_time_ms
FROM tool_usage_logs
GROUP BY tool_name, tool_category;

-- Guest Journey Analytics
CREATE VIEW guest_journey_analytics AS
SELECT 
    g.guest_id,
    g.name,
    g.vip_status,
    g.preferred_language,
    COUNT(DISTINCT cs.session_id) as total_sessions,
    SUM(cs.total_messages) as total_messages,
    COUNT(DISTINCT sr.request_id) as total_service_requests,
    AVG(cs.guest_satisfaction) as avg_satisfaction
FROM guests g
LEFT JOIN conversation_sessions cs ON g.guest_id = cs.guest_id
LEFT JOIN service_requests sr ON g.guest_id = sr.guest_id
GROUP BY g.guest_id, g.name, g.vip_status, g.preferred_language;