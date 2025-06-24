#!/usr/bin/env python3
"""
🏨 Omotenashi Data Migration Strategy
Migrates JSON data to PostgreSQL database for production deployment
"""

import json
import asyncio
import asyncpg
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OmotenashiDataMigration:
    """Handles migration from JSON files to PostgreSQL database"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool = None
    
    async def connect(self):
        """Establish database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=1,
                max_size=5,
                command_timeout=60
            )
            logger.info("✅ Database connection pool established")
        except Exception as e:
            logger.error(f"❌ Failed to connect to database: {e}")
            raise
    
    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("🔌 Database connection pool closed")
    
    async def load_json_data(self) -> tuple[List[Dict], List[Dict]]:
        """Load existing JSON data files"""
        try:
            # Load guests
            with open('guests.json', 'r', encoding='utf-8') as f:
                guests = json.load(f)
            logger.info(f"📄 Loaded {len(guests)} guests from JSON")
            
            # Load bookings
            with open('bookings.json', 'r', encoding='utf-8') as f:
                bookings = json.load(f)
            logger.info(f"📄 Loaded {len(bookings)} bookings from JSON")
            
            return guests, bookings
            
        except FileNotFoundError as e:
            logger.error(f"❌ JSON file not found: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON format: {e}")
            raise
    
    async def check_database_schema(self):
        """Verify database schema exists"""
        async with self.pool.acquire() as conn:
            try:
                # Check if main tables exist
                tables = await conn.fetch("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name IN ('properties', 'guests', 'bookings')
                """)
                
                table_names = [row['table_name'] for row in tables]
                
                if len(table_names) < 3:
                    missing = set(['properties', 'guests', 'bookings']) - set(table_names)
                    logger.error(f"❌ Missing database tables: {missing}")
                    logger.info("💡 Run database_schema.sql first to create tables")
                    raise Exception(f"Database schema incomplete. Missing tables: {missing}")
                
                logger.info("✅ Database schema validated")
                
            except Exception as e:
                logger.error(f"❌ Schema validation failed: {e}")
                raise
    
    async def migrate_properties(self):
        """Insert default property (Villa Azul)"""
        async with self.pool.acquire() as conn:
            try:
                # Check if property already exists
                existing = await conn.fetchval(
                    "SELECT property_id FROM properties WHERE property_id = 'villa_azul'"
                )
                
                if existing:
                    logger.info("🏨 Property 'villa_azul' already exists, skipping")
                    return
                
                # Insert Villa Azul property
                await conn.execute("""
                    INSERT INTO properties (
                        property_id, property_name, property_type, location, 
                        amenities, max_guests
                    ) VALUES (
                        $1, $2, $3, $4, $5, $6
                    )
                """, 
                'villa_azul', 
                'Villa Azul', 
                'luxury_villa', 
                'Costa Rica, Manuel Antonio',
                json.dumps({
                    "pool": True, "spa": True, "gym": True, "wifi": True, 
                    "kitchen": True, "concierge": True, "ocean_view": True
                }),
                8
                )
                
                logger.info("🏨 ✅ Property 'Villa Azul' migrated successfully")
                
            except Exception as e:
                logger.error(f"❌ Property migration failed: {e}")
                raise
    
    async def migrate_guests(self, guests: List[Dict]):
        """Migrate guest data to database"""
        async with self.pool.acquire() as conn:
            try:
                # Clear existing guests if any
                await conn.execute("DELETE FROM guests")
                logger.info("🧹 Cleared existing guest data")
                
                # Prepare batch insert
                guest_records = []
                for guest in guests:
                    guest_records.append((
                        guest['guest_id'],
                        guest['name'],
                        guest['phone_number'],
                        guest.get('email'),  # May not exist in JSON
                        guest['preferred_language'],
                        guest['vip_status'],
                        guest.get('dietary_restrictions'),  # May not exist
                        guest.get('accessibility_needs'),   # May not exist
                        None,  # emergency_contact (JSON)
                        None,  # guest_preferences (JSON)
                        datetime.now(timezone.utc),
                        datetime.now(timezone.utc)
                    ))
                
                # Batch insert guests
                await conn.executemany("""
                    INSERT INTO guests (
                        guest_id, name, phone_number, email, preferred_language,
                        vip_status, dietary_restrictions, accessibility_needs,
                        emergency_contact, guest_preferences, created_at, updated_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                """, guest_records)
                
                logger.info(f"👥 ✅ Migrated {len(guests)} guests successfully")
                
            except Exception as e:
                logger.error(f"❌ Guest migration failed: {e}")
                raise
    
    async def migrate_bookings(self, bookings: List[Dict]):
        """Migrate booking data to database"""
        async with self.pool.acquire() as conn:
            try:
                # Clear existing bookings if any
                await conn.execute("DELETE FROM bookings")
                logger.info("🧹 Cleared existing booking data")
                
                # Prepare batch insert
                booking_records = []
                for i, booking in enumerate(bookings):
                    # Generate booking ID if not present
                    booking_id = booking.get('booking_id', f"b{i+1}")
                    
                    # Parse dates
                    check_in = datetime.fromisoformat(booking['check_in'].replace('Z', '+00:00'))
                    check_out = datetime.fromisoformat(booking['check_out'].replace('Z', '+00:00'))
                    
                    booking_records.append((
                        booking_id,
                        booking['guest_id'],
                        booking.get('property_id', 'villa_azul'),  # Default to villa_azul
                        check_in,
                        check_out,
                        booking.get('number_of_guests', 1),
                        booking.get('room_type', 'Standard'),
                        'confirmed',  # Default status
                        booking.get('total_amount'),
                        'USD',
                        booking.get('special_requests', ''),
                        'direct',  # Default source
                        datetime.now(timezone.utc),
                        datetime.now(timezone.utc)
                    ))
                
                # Batch insert bookings
                await conn.executemany("""
                    INSERT INTO bookings (
                        booking_id, guest_id, property_id, check_in_date, check_out_date,
                        number_of_guests, room_type, booking_status, total_amount,
                        currency, special_requests, booking_source, created_at, updated_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                """, booking_records)
                
                logger.info(f"📅 ✅ Migrated {len(bookings)} bookings successfully")
                
            except Exception as e:
                logger.error(f"❌ Booking migration failed: {e}")
                raise
    
    async def expand_booking_data(self):
        """Create additional realistic bookings for pilot testing"""
        async with self.pool.acquire() as conn:
            try:
                # Generate 25 additional bookings with realistic data
                additional_bookings = []
                
                # Get all guest IDs for random assignment
                guest_ids = await conn.fetch("SELECT guest_id FROM guests WHERE guest_id != 'g1' AND guest_id != 'g2'")
                guest_id_list = [row['guest_id'] for row in guest_ids]
                
                # Create bookings for next 6 months
                import random
                from datetime import timedelta
                
                start_date = datetime(2025, 7, 1, 15, 0, 0, tzinfo=timezone.utc)
                
                for i in range(25):
                    # Random guest
                    guest_id = random.choice(guest_id_list)
                    
                    # Random check-in date (next 6 months)
                    days_from_start = random.randint(0, 180)
                    check_in = start_date + timedelta(days=days_from_start)
                    
                    # Random stay length (2-14 days)
                    stay_days = random.randint(2, 14)
                    check_out = check_in + timedelta(days=stay_days, hours=-4)  # 11:00 checkout
                    
                    # Random guest count and room type
                    num_guests = random.randint(1, 6)
                    room_types = ['Standard', 'Deluxe', 'Premium Suite', 'Villa Suite', 'Ocean View']
                    room_type = random.choice(room_types)
                    
                    # Random pricing based on room type and guest count
                    base_prices = {'Standard': 200, 'Deluxe': 300, 'Premium Suite': 450, 'Villa Suite': 600, 'Ocean View': 400}
                    total_amount = base_prices[room_type] * stay_days * (1 + num_guests * 0.1)
                    
                    # Random special requests
                    special_requests_options = [
                        '', 'Late checkout requested', 'Early check-in needed', 
                        'Vegetarian meals preferred', 'Spa services interest',
                        'Airport transport needed', 'Restaurant recommendations wanted',
                        'Celebration occasion - anniversary', 'Family with young children',
                        'Business traveler - quiet room preferred'
                    ]
                    special_requests = random.choice(special_requests_options)
                    
                    additional_bookings.append((
                        f"b{i+3}",  # Start from b3 since b1, b2 exist
                        guest_id,
                        'villa_azul',
                        check_in,
                        check_out,
                        num_guests,
                        room_type,
                        'confirmed',
                        round(total_amount, 2),
                        'USD',
                        special_requests,
                        random.choice(['direct', 'airbnb', 'vrbo', 'booking.com']),
                        datetime.now(timezone.utc),
                        datetime.now(timezone.utc)
                    ))
                
                # Insert additional bookings
                await conn.executemany("""
                    INSERT INTO bookings (
                        booking_id, guest_id, property_id, check_in_date, check_out_date,
                        number_of_guests, room_type, booking_status, total_amount,
                        currency, special_requests, booking_source, created_at, updated_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                """, additional_bookings)
                
                logger.info(f"📈 ✅ Generated {len(additional_bookings)} additional pilot bookings")
                
            except Exception as e:
                logger.error(f"❌ Booking expansion failed: {e}")
                raise
    
    async def validate_migration(self):
        """Validate migrated data integrity"""
        async with self.pool.acquire() as conn:
            try:
                # Count records
                guest_count = await conn.fetchval("SELECT COUNT(*) FROM guests")
                booking_count = await conn.fetchval("SELECT COUNT(*) FROM bookings")
                property_count = await conn.fetchval("SELECT COUNT(*) FROM properties")
                
                logger.info(f"📊 Migration Summary:")
                logger.info(f"   Properties: {property_count}")
                logger.info(f"   Guests: {guest_count}")
                logger.info(f"   Bookings: {booking_count}")
                
                # Validate relationships
                orphaned_bookings = await conn.fetchval("""
                    SELECT COUNT(*) FROM bookings b 
                    WHERE NOT EXISTS (SELECT 1 FROM guests g WHERE g.guest_id = b.guest_id)
                """)
                
                if orphaned_bookings > 0:
                    logger.warning(f"⚠️  Found {orphaned_bookings} bookings with invalid guest references")
                else:
                    logger.info("✅ All booking-guest relationships valid")
                
                # Check for upcoming bookings
                upcoming_bookings = await conn.fetchval("""
                    SELECT COUNT(*) FROM bookings 
                    WHERE check_in_date > NOW() AND booking_status = 'confirmed'
                """)
                
                logger.info(f"📅 Upcoming bookings: {upcoming_bookings}")
                
                # Language distribution
                language_stats = await conn.fetch("""
                    SELECT preferred_language, COUNT(*) as count 
                    FROM guests 
                    GROUP BY preferred_language 
                    ORDER BY count DESC
                """)
                
                logger.info("🌍 Guest language distribution:")
                for row in language_stats[:5]:  # Top 5 languages
                    logger.info(f"   {row['preferred_language']}: {row['count']}")
                
                logger.info("✅ Migration validation completed")
                
            except Exception as e:
                logger.error(f"❌ Migration validation failed: {e}")
                raise
    
    async def create_sample_sessions(self):
        """Create sample conversation sessions for testing"""
        async with self.pool.acquire() as conn:
            try:
                # Create a few sample sessions
                sample_sessions = [
                    ('carlos_session_1', 'g1', 'villa_azul', 'active', 5),
                    ('maria_session_1', 'g2', 'villa_azul', 'ended', 8),
                ]
                
                for session_id, guest_id, property_id, status, msg_count in sample_sessions:
                    await conn.execute("""
                        INSERT INTO conversation_sessions 
                        (session_id, guest_id, property_id, session_status, total_messages)
                        VALUES ($1, $2, $3, $4, $5)
                        ON CONFLICT (session_id) DO NOTHING
                    """, session_id, guest_id, property_id, status, msg_count)
                
                logger.info("💬 ✅ Sample conversation sessions created")
                
            except Exception as e:
                logger.error(f"❌ Sample session creation failed: {e}")
                raise

async def main():
    """Main migration function"""
    # Database connection from environment or default
    database_url = os.getenv('DATABASE_URL', 
                            'postgresql://omotenashi:concierge_secret@localhost:5432/omotenashi_db')
    
    migration = OmotenashiDataMigration(database_url)
    
    try:
        logger.info("🚀 Starting Omotenashi data migration...")
        
        # Connect to database
        await migration.connect()
        
        # Validate schema
        await migration.check_database_schema()
        
        # Load JSON data
        guests, bookings = await migration.load_json_data()
        
        # Migrate data
        await migration.migrate_properties()
        await migration.migrate_guests(guests)
        await migration.migrate_bookings(bookings)
        
        # Expand data for pilot
        await migration.expand_booking_data()
        
        # Create sample sessions
        await migration.create_sample_sessions()
        
        # Validate migration
        await migration.validate_migration()
        
        logger.info("🎉 Migration completed successfully!")
        logger.info("💡 Next steps:")
        logger.info("   1. Update main.py to use database instead of JSON")
        logger.info("   2. Test authentication flow with new data")
        logger.info("   3. Validate all 15 tools work with database")
        
    except Exception as e:
        logger.error(f"💥 Migration failed: {e}")
        return 1
    finally:
        await migration.close()
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())