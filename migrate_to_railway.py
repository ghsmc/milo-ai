#!/usr/bin/env python3
"""
Railway Database Migration Script
This script migrates your local SQLite Yale database to Railway's PostgreSQL database.
"""

import sqlite3
import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any
import time

def get_railway_db_url():
    """Get Railway PostgreSQL URL from environment"""
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL environment variable not found")
        print("💡 Get this from your Railway project dashboard:")
        print("   1. Go to your Railway project")
        print("   2. Add a PostgreSQL database service")
        print("   3. Copy the DATABASE_URL from the database service")
        print("   4. Set it as an environment variable")
        return None
    return db_url

def create_postgres_tables(conn):
    """Create the necessary tables in PostgreSQL"""
    cursor = conn.cursor()
    
    # Create profiles table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS yale_profiles (
            person_id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255),
            position TEXT,
            company VARCHAR(255),
            location VARCHAR(255),
            city VARCHAR(255),
            country_code VARCHAR(10),
            about TEXT,
            connections INTEGER,
            followers INTEGER,
            recommendations_count INTEGER,
            educations_details TEXT,
            current_company_name VARCHAR(255),
            current_title VARCHAR(255),
            experience_history JSONB,
            education_details JSONB,
            company_industry VARCHAR(255),
            company_size VARCHAR(100),
            employee_count INTEGER,
            yale_alumni_count INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes for better performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_company ON yale_profiles(company)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_current_company ON yale_profiles(current_company_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_connections ON yale_profiles(connections)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_position ON yale_profiles(position)")
    
    conn.commit()
    print("✅ PostgreSQL tables created successfully")

def migrate_data():
    """Migrate data from SQLite to PostgreSQL"""
    
    # Check if local database exists
    if not os.path.exists('yale.db'):
        print("❌ yale.db not found in current directory")
        return False
    
    # Get Railway database URL
    db_url = get_railway_db_url()
    if not db_url:
        return False
    
    print("🔄 Starting migration from SQLite to Railway PostgreSQL...")
    
    # Connect to SQLite
    sqlite_conn = sqlite3.connect('yale.db')
    sqlite_cursor = sqlite_conn.cursor()
    
    # Connect to PostgreSQL
    try:
        pg_conn = psycopg2.connect(db_url)
        print("✅ Connected to Railway PostgreSQL database")
    except Exception as e:
        print(f"❌ Failed to connect to PostgreSQL: {e}")
        return False
    
    # Create tables
    create_postgres_tables(pg_conn)
    
    # Get data from SQLite
    query = """
    SELECT 
        p.person_id,
        p.name,
        p.position,
        p.company,
        p.location,
        p.city,
        p.country_code,
        p.about,
        p.connections,
        p.followers,
        p.recommendations_count,
        p.educations_details,
        cc.name as current_company_name,
        cc.title as current_title,
        GROUP_CONCAT(e.company || '|' || e.title || '|' || e.start_date || '|' || e.end_date || '|' || COALESCE(e.description, ''), '||') as experience_history,
        GROUP_CONCAT(ed.title || '|' || ed.degree || '|' || ed.field || '|' || ed.start_year || '|' || ed.end_year, '||') as education_details,
        ec.industry as company_industry,
        ec.size as company_size,
        ec.employee_count,
        ec.yale_alumni_count
    FROM clean_yale_profiles p
    LEFT JOIN current_companies cc ON p.person_id = cc.person_id
    LEFT JOIN clean_experiences e ON p.person_id = e.person_id
    LEFT JOIN clean_educations ed ON p.person_id = ed.person_id
    LEFT JOIN enhanced_companies ec ON (cc.name = ec.name OR p.company = ec.name)
    WHERE p.name IS NOT NULL 
    AND p.position IS NOT NULL
    AND p.company IS NOT NULL
    AND p.company != ''
    GROUP BY p.person_id
    ORDER BY p.connections DESC
    """
    
    print("📊 Fetching data from SQLite...")
    sqlite_cursor.execute(query)
    profiles = sqlite_cursor.fetchall()
    
    print(f"📈 Found {len(profiles)} profiles to migrate")
    
    # Insert data into PostgreSQL
    pg_cursor = pg_conn.cursor()
    
    batch_size = 100
    total_inserted = 0
    
    for i in range(0, len(profiles), batch_size):
        batch = profiles[i:i + batch_size]
        
        for profile in batch:
            # Parse experience history
            experience_history = []
            if profile[14]:  # experience_history
                for exp in profile[14].split('||'):
                    if exp and '|' in exp:
                        parts = exp.split('|')
                        if len(parts) >= 4:
                            experience_history.append({
                                'company': parts[0],
                                'title': parts[1],
                                'start_date': parts[2],
                                'end_date': parts[3],
                                'description': parts[4] if len(parts) > 4 else ''
                            })
            
            # Parse education details
            education_details = []
            if profile[15]:  # education_details
                for edu in profile[15].split('||'):
                    if edu and '|' in edu:
                        parts = edu.split('|')
                        if len(parts) >= 5:
                            education_details.append({
                                'institution': parts[0],
                                'degree': parts[1],
                                'field': parts[2],
                                'start_year': parts[3],
                                'end_year': parts[4]
                            })
            
            # Insert into PostgreSQL
            try:
                pg_cursor.execute("""
                    INSERT INTO yale_profiles (
                        person_id, name, position, company, location, city, country_code,
                        about, connections, followers, recommendations_count, educations_details,
                        current_company_name, current_title, experience_history, education_details,
                        company_industry, company_size, employee_count, yale_alumni_count
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    ) ON CONFLICT (person_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        position = EXCLUDED.position,
                        company = EXCLUDED.company,
                        location = EXCLUDED.location,
                        city = EXCLUDED.city,
                        country_code = EXCLUDED.country_code,
                        about = EXCLUDED.about,
                        connections = EXCLUDED.connections,
                        followers = EXCLUDED.followers,
                        recommendations_count = EXCLUDED.recommendations_count,
                        educations_details = EXCLUDED.educations_details,
                        current_company_name = EXCLUDED.current_company_name,
                        current_title = EXCLUDED.current_title,
                        experience_history = EXCLUDED.experience_history,
                        education_details = EXCLUDED.education_details,
                        company_industry = EXCLUDED.company_industry,
                        company_size = EXCLUDED.company_size,
                        employee_count = EXCLUDED.employee_count,
                        yale_alumni_count = EXCLUDED.yale_alumni_count
                """, (
                    profile[0], profile[1], profile[2], profile[3], profile[4], profile[5], profile[6],
                    profile[7], profile[8], profile[9], profile[10], profile[11], profile[12], profile[13],
                    json.dumps(experience_history), json.dumps(education_details),
                    profile[16], profile[17], profile[18], profile[19]
                ))
                total_inserted += 1
            except Exception as e:
                print(f"⚠️  Error inserting profile {profile[0]}: {e}")
                continue
        
        # Commit batch
        pg_conn.commit()
        
        # Progress update
        progress = (i + len(batch)) / len(profiles) * 100
        print(f"📊 Progress: {progress:.1f}% ({total_inserted} profiles migrated)")
        
        # Small delay to avoid overwhelming the database
        time.sleep(0.1)
    
    # Close connections
    sqlite_conn.close()
    pg_conn.close()
    
    print(f"✅ Migration completed! {total_inserted} profiles migrated to Railway PostgreSQL")
    return True

def test_connection():
    """Test the PostgreSQL connection"""
    db_url = get_railway_db_url()
    if not db_url:
        return False
    
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM yale_profiles")
        count = cursor.fetchone()[0]
        print(f"✅ Connection successful! Found {count} profiles in database")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Railway Yale Database Migration")
    print("=" * 40)
    
    # Check if we have the required dependencies
    try:
        import psycopg2
    except ImportError:
        print("❌ psycopg2 not installed")
        print("💡 Install it with: pip install psycopg2-binary")
        return
    
    # Test connection first
    if not test_connection():
        print("\n🔧 Setup Instructions:")
        print("1. Go to your Railway project dashboard")
        print("2. Add a PostgreSQL database service")
        print("3. Copy the DATABASE_URL from the database service")
        print("4. Set it as an environment variable:")
        print("   export DATABASE_URL='your_postgresql_url_here'")
        print("5. Run this script again")
        return
    
    # Ask for confirmation
    print(f"\n⚠️  This will migrate your local yale.db to Railway PostgreSQL")
    print("This may take several minutes due to the large dataset.")
    response = input("Continue? (y/N): ")
    
    if response.lower() != 'y':
        print("Migration cancelled.")
        return
    
    # Run migration
    if migrate_data():
        print("\n🎉 Migration completed successfully!")
        print("Your Yale database is now available on Railway PostgreSQL")
        print("Update your backend to use the DATABASE_URL environment variable")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
