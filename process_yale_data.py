#!/usr/bin/env python3
"""
Yale Data Processing Pipeline
Filters and cleans the raw Yale dataset for optimal career guidance
"""

import json
import re
from typing import Dict, List, Any
import pandas as pd

class YaleDataProcessor:
    def __init__(self, input_file: str = "yale.json"):
        self.input_file = input_file
        self.processed_data = []
        
    def load_data(self) -> List[Dict]:
        """Load the raw Yale JSON data"""
        print(f"📁 Loading data from {self.input_file}...")
        with open(self.input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Loaded {len(data)} profiles")
        return data
    
    def is_yale_university_alumni(self, profile: Dict) -> bool:
        """Filter for actual Yale University alumni"""
        education = profile.get('education', [])
        
        # Look for Yale University in education
        for edu in education:
            if isinstance(edu, dict):
                institution = edu.get('institution', '').lower()
                if 'yale university' in institution or 'yale' in institution:
                    # Additional filters to ensure it's Yale University, New Haven
                    if any(keyword in institution for keyword in ['new haven', 'connecticut', 'ct']):
                        return True
                    # If just "yale" but no conflicting info, likely Yale University
                    if 'yale' in institution and not any(conflict in institution for conflict in ['india', 'delhi', 'mumbai']):
                        return True
        
        return False
    
    def is_high_quality_profile(self, profile: Dict) -> bool:
        """Filter for high-quality, relevant profiles"""
        # Must have basic info
        if not profile.get('name') or not profile.get('location'):
            return False
            
        # Must have some professional experience
        experience = profile.get('experience', [])
        if not experience or len(experience) == 0:
            return False
            
        # Must have education info
        education = profile.get('education', [])
        if not education or len(education) == 0:
            return False
            
        # Filter out profiles with very little information
        if len(str(profile).lower()) < 200:  # Very minimal profile
            return False
            
        return True
    
    def is_relevant_for_undergrads(self, profile: Dict) -> bool:
        """Filter for profiles relevant to current Yale undergrads"""
        # Look for recent graduates or current professionals
        experience = profile.get('experience', [])
        
        # Must have some professional experience (not just student)
        has_professional_exp = False
        for exp in experience:
            if isinstance(exp, dict):
                title = exp.get('title', '').lower()
                if any(keyword in title for keyword in ['intern', 'analyst', 'associate', 'engineer', 'consultant', 'manager', 'director', 'founder', 'ceo']):
                    has_professional_exp = True
                    break
        
        return has_professional_exp
    
    def clean_profile(self, profile: Dict) -> Dict:
        """Clean and standardize profile data"""
        cleaned = {}
        
        # Basic info
        cleaned['name'] = profile.get('name', '').strip()
        cleaned['location'] = profile.get('location', '').strip()
        cleaned['about'] = profile.get('about', '').strip()
        
        # Education - focus on Yale
        yale_education = []
        for edu in profile.get('education', []):
            if isinstance(edu, dict):
                institution = edu.get('institution', '').lower()
                if 'yale' in institution:
                    yale_education.append({
                        'institution': edu.get('institution', ''),
                        'degree': edu.get('degree', ''),
                        'field': edu.get('field', ''),
                        'start_date': edu.get('start_date', ''),
                        'end_date': edu.get('end_date', '')
                    })
        
        cleaned['yale_education'] = yale_education
        
        # Experience - clean and structure
        cleaned_experience = []
        for exp in profile.get('experience', []):
            if isinstance(exp, dict):
                cleaned_experience.append({
                    'title': exp.get('title', ''),
                    'company': exp.get('company', ''),
                    'location': exp.get('location', ''),
                    'start_date': exp.get('start_date', ''),
                    'end_date': exp.get('end_date', ''),
                    'description': exp.get('description', '')
                })
        
        cleaned['experience'] = cleaned_experience
        
        # Skills
        cleaned['skills'] = profile.get('skills', [])
        
        # Additional metadata
        cleaned['profile_url'] = profile.get('profile_url', '')
        cleaned['connections'] = profile.get('connections', 0)
        
        return cleaned
    
    def process_data(self) -> List[Dict]:
        """Main processing pipeline"""
        print("🚀 Starting Yale data processing...")
        
        # Load raw data
        raw_data = self.load_data()
        
        # Apply filters
        print("🔍 Filtering for Yale University alumni...")
        yale_alumni = [p for p in raw_data if self.is_yale_university_alumni(p)]
        print(f"✅ Found {len(yale_alumni)} Yale University alumni")
        
        print("🔍 Filtering for high-quality profiles...")
        quality_profiles = [p for p in yale_alumni if self.is_high_quality_profile(p)]
        print(f"✅ Found {len(quality_profiles)} high-quality profiles")
        
        print("🔍 Filtering for undergrad-relevant profiles...")
        relevant_profiles = [p for p in quality_profiles if self.is_relevant_for_undergrads(p)]
        print(f"✅ Found {len(relevant_profiles)} relevant profiles for undergrads")
        
        # Clean profiles
        print("🧹 Cleaning and standardizing profiles...")
        self.processed_data = [self.clean_profile(p) for p in relevant_profiles]
        
        print(f"🎯 Final dataset: {len(self.processed_data)} high-quality Yale alumni profiles")
        return self.processed_data
    
    def save_processed_data(self, output_file: str = "yale_processed.json"):
        """Save processed data"""
        print(f"💾 Saving processed data to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.processed_data, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved {len(self.processed_data)} profiles to {output_file}")
    
    def generate_summary(self):
        """Generate summary statistics"""
        if not self.processed_data:
            print("❌ No processed data available")
            return
            
        print("\n📊 YALE DATASET SUMMARY")
        print("=" * 50)
        print(f"Total Profiles: {len(self.processed_data)}")
        
        # Industry breakdown
        industries = {}
        for profile in self.processed_data:
            for exp in profile.get('experience', []):
                company = exp.get('company', '').lower()
                if company:
                    # Simple industry detection
                    if any(keyword in company for keyword in ['tech', 'software', 'google', 'microsoft', 'apple', 'amazon']):
                        industries['Technology'] = industries.get('Technology', 0) + 1
                    elif any(keyword in company for keyword in ['bank', 'finance', 'investment', 'goldman', 'morgan']):
                        industries['Finance'] = industries.get('Finance', 0) + 1
                    elif any(keyword in company for keyword in ['consulting', 'mckinsey', 'bain', 'bcg']):
                        industries['Consulting'] = industries.get('Consulting', 0) + 1
                    elif any(keyword in company for keyword in ['law', 'legal', 'attorney']):
                        industries['Law'] = industries.get('Law', 0) + 1
                    else:
                        industries['Other'] = industries.get('Other', 0) + 1
        
        print("\n🏢 Top Industries:")
        for industry, count in sorted(industries.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {industry}: {count}")
        
        # Location breakdown
        locations = {}
        for profile in self.processed_data:
            location = profile.get('location', '').lower()
            if location:
                if 'new york' in location or 'nyc' in location:
                    locations['New York'] = locations.get('New York', 0) + 1
                elif 'san francisco' in location or 'sf' in location:
                    locations['San Francisco'] = locations.get('San Francisco', 0) + 1
                elif 'boston' in location:
                    locations['Boston'] = locations.get('Boston', 0) + 1
                elif 'washington' in location or 'dc' in location:
                    locations['Washington DC'] = locations.get('Washington DC', 0) + 1
                else:
                    locations['Other'] = locations.get('Other', 0) + 1
        
        print("\n📍 Top Locations:")
        for location, count in sorted(locations.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {location}: {count}")

def main():
    """Main execution"""
    processor = YaleDataProcessor("yale.json")
    
    # Process the data
    processed_data = processor.process_data()
    
    # Save processed data
    processor.save_processed_data("yale_processed.json")
    
    # Generate summary
    processor.generate_summary()
    
    print("\n🎉 Yale data processing complete!")
    print("Ready to build the ultimate career guidance engine for Yale students!")

if __name__ == "__main__":
    main()
