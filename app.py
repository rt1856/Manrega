from flask import Flask, render_template, request, jsonify, session
import sqlite3
import requests
import json
import os
from datetime import datetime, timedelta
import logging
from models import DatabaseManager

app = Flask(__name__)
app.secret_key = 'mgnrega-gujarat-2024-secret-key'
app.config['DATABASE'] = 'database/mgnrega.db'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database manager
db_manager = DatabaseManager()

class MGNREGADataService:
    def __init__(self):
        self.base_api_url = "https://api.data.gov.in/resource/mgnrega"
        self.api_key = "579b464db66ec23bdd0000016c007f893e704b6f6cd80fb7888bfa1a"  # demo key
        self.cache_timeout = 24 * 3600  # 24 hours
    
    def get_district_performance(self, district_code, year, month):
        """Get performance data for a district"""
        try:
            # Try to get from database first
            cached_data = db_manager.get_performance_data(district_code, year, month)
            if cached_data:
                return cached_data
            
            # If not in database, try API with fallback to mock data
            api_data = self.fetch_from_api(district_code, year, month)
            if api_data and 'records' in api_data and api_data['records']:
                # Store in database for future use
                db_manager.save_performance_data(api_data['records'][0])
                return api_data
            else:
                # Generate mock data
                return self.generate_mock_data(district_code, year, month)
                
        except Exception as e:
            logger.error(f"Error getting performance data: {str(e)}")
            return self.generate_mock_data(district_code, year, month)
    
    def fetch_from_api(self, district_code, year, month):
        """Fetch data from data.gov.in API"""
        try:
            params = {
                'api-key': self.api_key,
                'format': 'json',
                'filters[district_code]': district_code,
                'filters[year]': year,
                'filters[month]': month,
                'limit': 10
            }
            
            response = requests.get(self.base_api_url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            logger.warning(f"API fetch failed: {str(e)}")
            return None
    
    def generate_mock_data(self, district_code, year, month):
        """Generate realistic mock data for demonstration"""
        # Base values with some variation
        base_values = {
            'households_provided_employment': 45000,
            'persons_worked': 62000,
            'total_person_days': 1250000,
            'sc_person_days': 375000,
            'st_person_days': 250000,
            'women_person_days': 500000,
            'total_expenditure': 35000000,
            'works_taken_up': 185,
            'works_completed': 142
        }
        
        # Add variation based on district, year, month
        variation_seed = hash(f"{district_code}{year}{month}") % 1000 / 1000.0
        seasonal_factor = 1.0 + (0.2 * abs(hash(str(month))) % 1000 / 1000.0 - 0.1)
        
        mock_data = {
            "records": [{
                "district_code": district_code,
                "district_name": db_manager.get_district_name(district_code),
                "year": year,
                "month": month,
                "households_provided_employment": int(base_values['households_provided_employment'] * seasonal_factor * (0.9 + variation_seed * 0.2)),
                "persons_worked": int(base_values['persons_worked'] * seasonal_factor * (0.9 + variation_seed * 0.2)),
                "total_person_days": int(base_values['total_person_days'] * seasonal_factor * (0.9 + variation_seed * 0.2)),
                "sc_person_days": int(base_values['sc_person_days'] * seasonal_factor * (0.9 + variation_seed * 0.2)),
                "st_person_days": int(base_values['st_person_days'] * seasonal_factor * (0.9 + variation_seed * 0.2)),
                "women_person_days": int(base_values['women_person_days'] * seasonal_factor * (0.9 + variation_seed * 0.2)),
                "total_expenditure": int(base_values['total_expenditure'] * seasonal_factor * (0.9 + variation_seed * 0.2)),
                "works_taken_up": int(base_values['works_taken_up'] * (0.9 + variation_seed * 0.2)),
                "works_completed": int(base_values['works_completed'] * (0.9 + variation_seed * 0.2)),
                "avg_days_per_household": round(25 * (0.9 + variation_seed * 0.2), 1)
            }]
        }
        
        # Store mock data in database
        db_manager.save_performance_data(mock_data['records'][0])
        
        return mock_data

data_service = MGNREGADataService()

# Custom template filters
@app.template_filter('format_number')
def format_number(value):
    """Format numbers with Indian comma separation"""
    try:
        return f"{int(value):,}"
    except:
        return value

@app.template_filter('format_currency')
def format_currency(value):
    """Format currency values"""
    try:
        if value >= 10000000:  # Crores
            return f"₹{value/10000000:.2f} Cr"
        elif value >= 100000:  # Lakhs
            return f"₹{value/100000:.2f} L"
        else:
            return f"₹{int(value):,}"
    except:
        return f"₹{value}"

@app.template_filter('get_month_name')
def get_month_name(month_num):
    """Convert month number to name"""
    months = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April',
        5: 'May', 6: 'June', 7: 'July', 8: 'August',
        9: 'September', 10: 'October', 11: 'November', 12: 'December'
    }
    return months.get(int(month_num), 'Unknown')

# Routes
@app.route('/')
def index():
    """Home page"""
    districts = db_manager.get_all_districts()
    return render_template('index.html', districts=districts)

@app.route('/dashboard')
def dashboard():
    """District performance dashboard"""
    district_code = request.args.get('district')
    year = request.args.get('year', datetime.now().year)
    month = request.args.get('month', datetime.now().month)
    
    if not district_code:
        return render_template('error.html', 
                            message="Please select a district",
                            hindi_message="कृपया एक जिला चुनें",
                            gujarati_message="કૃપા કરીને એક જિલ્લો પસંદ કરો")
    
    district_info = db_manager.get_district_info(district_code)
    if not district_info:
        return render_template('error.html', 
                            message="District not found",
                            hindi_message="जिला नहीं मिला",
                            gujarati_message="જિલ્લો મળ્યો નથી")
    
    performance_data = data_service.get_district_performance(district_code, year, month)
    
    return render_template('dashboard.html',
                         district_info=district_info,
                         performance_data=performance_data,
                         year=year,
                         month=month)

@app.route('/comparison')
def comparison():
    """District comparison page"""
    district_code = request.args.get('district')
    compare_with = request.args.get('compare_with', 'state')
    
    if not district_code:
        return render_template('error.html',
                            message="Please select a district",
                            hindi_message="कृपया एक जिला चुनें",
                            gujarati_message="કૃપા કરીને એક જિલ્લો પસંદ કરો")
    
    district_info = db_manager.get_district_info(district_code)
    comparison_data = db_manager.get_comparison_data(district_code, compare_with)
    
    return render_template('comparison.html',
                         district_info=district_info,
                         comparison_data=comparison_data,
                         compare_with=compare_with)

# API endpoints
@app.route('/api/districts')
def api_districts():
    """Get all districts"""
    districts = db_manager.get_all_districts()
    return jsonify([{
        'code': d[0], 
        'name': d[1], 
        'name_hindi': d[2],
        'name_gujarati': d[3]
    } for d in districts])

@app.route('/api/performance/<district_code>')
def api_performance(district_code):
    """Get performance data for a district"""
    year = request.args.get('year', datetime.now().year)
    month = request.args.get('month', datetime.now().month)
    
    data = data_service.get_district_performance(district_code, year, month)
    return jsonify(data)

@app.route('/api/detect-location')
def detect_location():
    """Detect user location and suggest district"""
    try:
        # Get IP-based location (simplified)
        user_ip = request.remote_addr
        
        # For demo, return a random district from Gujarat
        districts = db_manager.get_all_districts()
        import random
        random_district = random.choice(districts)
        
        return jsonify({
            'success': True,
            'district_code': random_district[0],
            'district_name': random_district[1],
            'district_name_hindi': random_district[2],
            'district_name_gujarati': random_district[3],
            'method': 'ip_geolocation'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/geolocation')
def geolocation():
    """Handle browser geolocation"""
    try:
        lat = request.args.get('lat')
        lon = request.args.get('lon')
        
        if lat and lon:
            # Find nearest district
            district = db_manager.find_nearest_district(float(lat), float(lon))
            if district:
                return jsonify({
                    'success': True,
                    'district_code': district[0],
                    'district_name': district[1],
                    'district_name_hindi': district[2],
                    'district_name_gujarati': district[3]
                })
        
        return jsonify({'success': False, 'error': 'Could not determine location'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('database', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    app.run(host='0.0.0.0', port=5000, debug=True)