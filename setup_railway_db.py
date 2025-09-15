#!/usr/bin/env python3
"""
Railway Database Setup Script
This script helps you set up the Yale database on Railway's PostgreSQL service.
Run this locally to migrate your SQLite data to Railway's PostgreSQL.
"""

import sqlite3
import os
import json
from typing import List, Dict, Any

def get_railway_db_url():
    """Get Railway PostgreSQL URL from environment"""
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL environment variable not found")
        print("💡 Get this from your Railway project dashboard")
        return None
    return db_url

def create_sample_data():
    """Create a small sample dataset for testing (no personal data)"""
    sample_data = [
        {
            "person_id": "sample_1",
            "name": "Yale Alumnus A",
            "position": "Software Engineer",
            "company": "Google",
            "location": "San Francisco, CA",
            "about": "Yale Computer Science graduate working in technology",
            "connections": 500,
            "followers": 1000,
            "recommendations_count": 5,
            "educations_details": "Yale University - Computer Science",
            "current_company_name": "Google",
            "current_title": "Software Engineer",
            "experience_history": [
                {
                    "company": "Google",
                    "title": "Software Engineer",
                    "start_date": "2020",
                    "end_date": "Present",
                    "description": "Full-stack development"
                }
            ],
            "education_details": [
                {
                    "institution": "Yale University",
                    "degree": "Bachelor of Science",
                    "field": "Computer Science",
                    "start_year": "2016",
                    "end_year": "2020"
                }
            ],
            "company_industry": "Technology",
            "company_size": "10000+",
            "yale_alumni_count": 150
        },
        {
            "person_id": "sample_2", 
            "name": "Yale Alumnus B",
            "position": "Investment Banking Analyst",
            "company": "Goldman Sachs",
            "location": "New York, NY",
            "about": "Yale Economics graduate in finance",
            "connections": 300,
            "followers": 500,
            "recommendations_count": 3,
            "educations_details": "Yale University - Economics",
            "current_company_name": "Goldman Sachs",
            "current_title": "Investment Banking Analyst",
            "experience_history": [
                {
                    "company": "Goldman Sachs",
                    "title": "Investment Banking Analyst",
                    "start_date": "2021",
                    "end_date": "Present",
                    "description": "Financial analysis and modeling"
                }
            ],
            "education_details": [
                {
                    "institution": "Yale University",
                    "degree": "Bachelor of Arts",
                    "field": "Economics",
                    "start_year": "2017",
                    "end_year": "2021"
                }
            ],
            "company_industry": "Finance",
            "company_size": "5000+",
            "yale_alumni_count": 200
        }
    ]
    
    return sample_data

def main():
    """Main setup function"""
    print("🚀 Railway Database Setup for Milo AI")
    print("=" * 40)
    
    # Check if we have the full database locally
    if os.path.exists('yale.db'):
        print("✅ Found local yale.db")
        print("💡 For production, you'll need to:")
        print("   1. Set up Railway PostgreSQL database")
        print("   2. Run a migration script to transfer data")
        print("   3. Update DATABASE_URL in Railway environment")
        print("\n🔒 For now, using sample data for testing...")
        
        # Create sample data file
        sample_data = create_sample_data()
        with open('sample_data.json', 'w') as f:
            json.dump(sample_data, f, indent=2)
        
        print("✅ Created sample_data.json for testing")
        print("📊 Sample data includes 2 anonymized profiles")
        
    else:
        print("⚠️  No yale.db found locally")
        print("💡 Make sure your database file is in the project directory")
    
    print("\n🎯 Next Steps:")
    print("1. Deploy backend to Railway (without database files)")
    print("2. Set up Railway PostgreSQL database")
    print("3. Run migration script to populate production database")
    print("4. Test the connection")

if __name__ == "__main__":
    main()
