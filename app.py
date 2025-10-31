from flask import Flask, render_template, request, jsonify, session
import sqlite3
import requests
import json
import os
from datetime import datetime, timedelta
import logging
from database.database_manager import DatabaseManager  # Updated import

app = Flask(__name__)
app.secret_key = 'mgnrega-gujarat-2024-secret-key'
app.config['DATABASE'] = 'database/mgnrega.db'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database manager
db_manager = DatabaseManager()

# Language support
SUPPORTED_LANGUAGES = ['en', 'hi', 'gu']
DEFAULT_LANGUAGE = 'gu'  # Gujarati as default

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
                return {"records": [cached_data]}
            
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
        # Get district info for realistic data generation
        district_info = db_manager.get_district_info(district_code)
        if district_info:
            population = district_info[7]  # population is at index 7
            households = district_info[8]  # total_households at index 8
        else:
            population = 2000000
            households = 400000
        
        # Base values scaled by district size
        employment_rate = 0.12  # 12% of households
        persons_per_household = 1.8
        days_per_person = 48
        
        base_employment = int(households * employment_rate)
        base_persons = int(base_employment * persons_per_household)
        base_days = base_persons * days_per_person
        
        mock_data = {
            "district_code": district_code,
            "year": year,
            "month": month,
            "households_provided_employment": base_employment,
            "persons_worked": base_persons,
            "total_person_days": base_days,
            "sc_person_days": int(base_days * 0.35),  # 35% SC
            "st_person_days": int(base_days * 0.25),  # 25% ST
            "women_person_days": int(base_days * 0.45),  # 45% Women
            "total_expenditure": base_days * 280,  # ₹280 per day
            "works_taken_up": int(base_employment * 0.15),
            "works_completed": int(base_employment * 0.12),
            "avg_days_per_household": days_per_person,
            "data_source": "mock"
        }
        
        # Store mock data in database
        db_manager.save_performance_data(mock_data)
        
        return {"records": [mock_data]}

data_service = MGNREGADataService()

# Custom template filters
@app.template_filter('format_number')
def format_number(value):
    """Format numbers with Indian comma separation"""
    try:
        if value is None:
            return "0"
        return f"{int(value):,}"
    except:
        return str(value)

@app.template_filter('abs')
def abs_filter(value):
    """Absolute value filter"""
    try:
        return abs(float(value))
    except:
        return value

@app.template_filter('format_currency')
def format_currency(value):
    """Format currency values"""
    try:
        if value is None:
            return "₹0"
        value = float(value)
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

@app.template_filter('get_month_name_hindi')
def get_month_name_hindi(month_num):
    """Convert month number to Hindi name"""
    months = {
        1: 'जनवरी', 2: 'फरवरी', 3: 'मार्च', 4: 'अप्रैल',
        5: 'मई', 6: 'जून', 7: 'जुलाई', 8: 'अगस्त',
        9: 'सितंबर', 10: 'अक्टूबर', 11: 'नवंबर', 12: 'दिसंबर'
    }
    return months.get(int(month_num), 'अज्ञात')

@app.template_filter('get_month_name_gujarati')
def get_month_name_gujarati(month_num):
    """Convert month number to Gujarati name"""
    months = {
        1: 'જાન્યુઆરી', 2: 'ફેબ્રુઆરી', 3: 'માર્ચ', 4: 'એપ્રિલ',
        5: 'મે', 6: 'જૂન', 7: 'જુલાઈ', 8: 'ઑગસ્ટ',
        9: 'સપ્ટેમ્બર', 10: 'ઑક્ટોબર', 11: 'નવેમ્બર', 12: 'ડિસેમ્બર'
    }
    return months.get(int(month_num), 'અજ્ઞાત')

# Language management
@app.context_processor
def inject_language():
    """Inject language into all templates"""
    return {
        'current_language': session.get('language', DEFAULT_LANGUAGE),
        'supported_languages': SUPPORTED_LANGUAGES
    }

@app.route('/set_language', methods=['POST'])
def set_language():
    """Set user's preferred language"""
    language = request.json.get('language', DEFAULT_LANGUAGE)
    if language in SUPPORTED_LANGUAGES:
        session['language'] = language
        session.permanent = True
        return jsonify({'success': True, 'language': language})
    return jsonify({'success': False, 'error': 'Unsupported language'})

# Routes
@app.route('/')
def index():
    """Home page with language support"""
    districts = db_manager.get_all_districts()
    current_language = session.get('language', DEFAULT_LANGUAGE)
    
    # Try to auto-detect location
    user_location = None
    try:
        # For demo, use Ahmedabad as default
        user_location = {
            'district_code': 'GJ01',
            'district_name': 'Ahmedabad',
            'district_name_hindi': 'अहमदाबाद',
            'district_name_gujarati': 'અમદાવાદ'
        }
    except Exception as e:
        logger.warning(f"Location detection failed: {str(e)}")
    
    return render_template('index.html', 
                         districts=districts,
                         user_location=user_location,
                         current_language=current_language)

@app.route('/dashboard')
def dashboard():
    """District performance dashboard"""
    district_code = request.args.get('district', 'GJ01')
    year = request.args.get('year', str(datetime.now().year))
    month = request.args.get('month', str(datetime.now().month))
    current_language = session.get('language', DEFAULT_LANGUAGE)
    
    district_info = db_manager.get_district_info(district_code)
    if not district_info:
        # Fallback to first district
        districts = db_manager.get_all_districts()
        if districts:
            district_code = districts[0][0]
            district_info = db_manager.get_district_info(district_code)
        else:
            return render_template('error.html', 
                                message="No districts available",
                                hindi_message="कोई जिला उपलब्ध नहीं है",
                                gujarati_message="કોઈ જિલ્લા ઉપલબ્ધ નથી")
    
    performance_data = data_service.get_district_performance(district_code, year, month)
    
    # Ensure performance_data has the expected structure
    if performance_data and 'records' in performance_data and performance_data['records']:
        performance_record = performance_data['records'][0]
    else:
        # Fallback to database data
        performance_record = db_manager.get_performance_data(district_code, year, month)
    
    return render_template('dashboard.html',
                         district_info=district_info,
                         performance_data=performance_record,
                         year=year,
                         month=month,
                         current_language=current_language)

@app.route('/comparison')
def comparison():
    """District comparison page"""
    district_code = request.args.get('district', 'GJ01')
    compare_with = request.args.get('compare_with', 'state')
    current_language = session.get('language', DEFAULT_LANGUAGE)
    
    district_info = db_manager.get_district_info(district_code)
    if not district_info:
        # Fallback to first district
        districts = db_manager.get_all_districts()
        if districts:
            district_code = districts[0][0]
            district_info = db_manager.get_district_info(district_code)
        else:
            return render_template('error.html', 
                                message="No districts available",
                                hindi_message="कोई जिला उपलब्ध नहीं है",
                                gujarati_message="કોઈ જિલ્લા ઉપલબ્ધ નથી")
    
    comparison_data = db_manager.get_comparison_data(district_code, compare_with)
    
    # Debug information
    logger.info(f"Comparison data for {district_code}: {comparison_data}")
    
    return render_template('comparison.html',
                         district_info=district_info,
                         comparison_data=comparison_data,
                         compare_with=compare_with,
                         current_language=current_language)
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
    year = request.args.get('year', str(datetime.now().year))
    month = request.args.get('month', str(datetime.now().month))
    
    data = data_service.get_district_performance(district_code, year, month)
    return jsonify(data)

@app.route('/api/detect-location')
def detect_location():
    """Detect user location and suggest district"""
    try:
        # For demo, return Ahmedabad
        district_info = db_manager.get_district_info('GJ01')
        if district_info:
            return jsonify({
                'success': True,
                'district_code': district_info[0],
                'district_name': district_info[1],
                'district_name_hindi': district_info[2],
                'district_name_gujarati': district_info[3],
                'method': 'default'
            })
        else:
            return jsonify({'success': False, 'error': 'No districts available'})
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/geolocation', methods=['POST'])
def geolocation():
    """Handle browser geolocation"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'})
        lat = data.get('latitude')
        lon = data.get('longitude')
        if lat and lon:
            nearest_district = db_manager.find_nearest_district(float(lat), float(lon))
            if nearest_district:
                return jsonify({
                    'success': True,
                    'district_code': nearest_district[0],
                    'district_name': nearest_district[1],
                    'district_name_hindi': nearest_district[2],
                    'district_name_gujarati': nearest_district[3]
                })
        return jsonify({'success': False, 'error': 'Could not determine location'})
    except Exception as e:
        logger.error(f"Geolocation error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'database': 'connected' if db_manager else 'disconnected',
        'timestamp': datetime.now().isoformat()
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    current_language = session.get('language', DEFAULT_LANGUAGE)
    return render_template('error.html',
                         message="Page not found",
                         hindi_message="पृष्ठ नहीं मिला",
                         gujarati_message="પૃષ્ઠ મળ્યું નથી",
                         current_language=current_language), 404

@app.errorhandler(500)
def internal_error(error):
    current_language = session.get('language', DEFAULT_LANGUAGE)
    return render_template('error.html',
                         message="Internal server error",
                         hindi_message="आंतरिक सर्वर त्रुटि",
                         gujarati_message="આંતરિક સર્વર ભૂલ",
                         current_language=current_language), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('database', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    print("MGNREGA Analytics Server Starting...")
    print("Available Districts:", len(db_manager.get_all_districts()))
    print("Default Language: Gujarati")
    print("Server running on http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)