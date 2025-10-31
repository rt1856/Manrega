#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database_manager import DatabaseManager

def test_database():
    print("Testing Database Manager...")
    
    # Initialize database
    db = DatabaseManager()
    
    # Test getting all districts
    districts = db.get_all_districts()
    print(f"Found {len(districts)} districts")
    
    # Test getting district info
    if districts:
        district_code = districts[0][0]
        info = db.get_district_info(district_code)
        print(f"District info for {district_code}: {info}")
        
        # Test performance data
        performance = db.get_performance_data(district_code)
        print(f"Performance data: {performance}")
        
        # Test comparison data
        comparison = db.get_comparison_data(district_code)
        print(f"Comparison data keys: {comparison.keys()}")
        print(f"District rank: {comparison.get('district_rank')}/{comparison.get('total_districts')}")
        
        # Test database stats
        stats = db.get_database_stats()
        print(f"Database stats: {stats}")
    else:
        print("No districts found!")

if __name__ == '__main__':
    test_database()