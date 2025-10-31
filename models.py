import sqlite3
import math
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path='database/mgnrega.db'):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Districts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS districts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                district_code TEXT UNIQUE NOT NULL,
                district_name TEXT NOT NULL,
                district_name_hindi TEXT,
                district_name_gujarati TEXT,
                state_code TEXT DEFAULT 'GJ',
                state_name TEXT DEFAULT 'Gujarat',
                state_name_hindi TEXT DEFAULT 'गुजरात',
                state_name_gujarati TEXT DEFAULT 'ગુજરાત',
                latitude REAL,
                longitude REAL,
                population INTEGER,
                total_households INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Performance data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                district_code TEXT NOT NULL,
                year INTEGER,
                month INTEGER,
                households_provided_employment INTEGER DEFAULT 0,
                persons_worked INTEGER DEFAULT 0,
                total_person_days INTEGER DEFAULT 0,
                sc_person_days INTEGER DEFAULT 0,
                st_person_days INTEGER DEFAULT 0,
                women_person_days INTEGER DEFAULT 0,
                total_expenditure REAL DEFAULT 0,
                works_taken_up INTEGER DEFAULT 0,
                works_completed INTEGER DEFAULT 0,
                avg_days_per_household REAL DEFAULT 0,
                data_source TEXT DEFAULT 'mock',
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(district_code, year, month)
            )
        ''')
        
        conn.commit()
        conn.close()
        self.load_initial_data()
    
    def load_initial_data(self):
        """Load Gujarat districts data with all three languages"""
        gujarat_districts = [
            # Format: code, name, hindi_name, gujarati_name, lat, lon, population, households
            ("GJ01", "Ahmedabad", "अहमदाबाद", "અમદાવાદ", 23.0225, 72.5714, 7410000, 1200000),
            ("GJ02", "Amreli", "अमरेली", "અમરેલી", 21.6000, 71.2000, 1514000, 240000),
            ("GJ03", "Anand", "आनंद", "આણંદ", 22.5600, 72.9500, 2090000, 330000),
            ("GJ04", "Aravalli", "अरवल्ली", "અરવલ્લી", 23.5000, 73.0000, 1052000, 170000),
            ("GJ05", "Banaskantha", "बनासकांठा", "બનાસકાંઠા", 24.2500, 72.5000, 3120000, 500000),
            ("GJ06", "Bharuch", "भरूच", "ભરૂચ", 21.7000, 72.9667, 1550000, 250000),
            ("GJ07", "Bhavnagar", "भावनगर", "ભાવનગર", 21.7667, 72.1500, 2880000, 460000),
            ("GJ08", "Botad", "बोटाद", "બોટાદ", 22.1700, 71.6700, 656000, 105000),
            ("GJ09", "Chhota Udaipur", "छोटा उदयपुर", "છોટા ઉદેપુર", 22.3200, 74.0000, 1072000, 170000),
            ("GJ10", "Dahod", "दाहोद", "દાહોદ", 22.8300, 74.2600, 2127000, 340000),
            ("GJ11", "Dang", "डांग", "ડાંગ", 20.7500, 73.7500, 228000, 36000),
            ("GJ12", "Devbhoomi Dwarka", "देवभूमि द्वारका", "દેવભૂમિ દ્વારકા", 22.2400, 69.6500, 752000, 120000),
            ("GJ13", "Gandhinagar", "गांधीनगर", "ગાંધીનગર", 23.2200, 72.6500, 1387000, 220000),
            ("GJ14", "Gir Somnath", "गिर सोमनाथ", "ગીર સોમનાથ", 20.9100, 70.3700, 1217000, 195000),
            ("GJ15", "Jamnagar", "जामनगर", "જામનગર", 22.4700, 70.0700, 2160000, 345000),
            ("GJ16", "Junagadh", "जूनागढ़", "જૂનાગઢ", 21.5200, 70.4700, 2743000, 440000),
            ("GJ17", "Kheda", "खेड़ा", "ખેડા", 22.7500, 72.6833, 2299000, 370000),
            ("GJ18", "Kutch", "कच्छ", "કચ્છ", 23.7000, 70.9000, 2090000, 335000),
            ("GJ19", "Mahisagar", "महिसागर", "મહીસાગર", 23.1000, 73.3500, 994000, 160000),
            ("GJ20", "Mehsana", "मेहसाणा", "મહેસાણા", 23.6000, 72.4000, 2027000, 325000),
            ("GJ21", "Morbi", "मोरबी", "મોરબી", 22.8200, 70.8400, 961000, 155000),
            ("GJ22", "Narmada", "नर्मदा", "નર્મદા", 21.8700, 73.5000, 590000, 95000),
            ("GJ23", "Navsari", "नवसारी", "નવસારી", 20.9500, 72.9300, 1331000, 210000),
            ("GJ24", "Panchmahal", "पंचमहल", "પંચમહાલ", 22.7500, 73.6000, 2391000, 380000),
            ("GJ25", "Patan", "पाटन", "પાટણ", 23.8500, 72.1300, 1343000, 215000),
            ("GJ26", "Porbandar", "पोरबंदर", "પોરબંદર", 21.6400, 69.6000, 586000, 95000),
            ("GJ27", "Rajkot", "राजकोट", "રાજકોટ", 22.3000, 70.7833, 3805000, 610000),
            ("GJ28", "Sabarkantha", "साबरकांठा", "સાબરકાંઠા", 23.5000, 73.0000, 2428000, 390000),
            ("GJ29", "Surat", "सूरत", "સુરત", 21.1700, 72.8300, 6081000, 970000),
            ("GJ30", "Surendranagar", "सुरेंद्रनगर", "સુરેન્દ્રનગર", 22.7200, 71.6500, 1756000, 280000),
            ("GJ31", "Tapi", "तापी", "તાપી", 21.1200, 73.4000, 807000, 130000),
            ("GJ32", "Vadodara", "वडोदरा", "વડોદરા", 22.3000, 73.2000, 4165000, 665000),
            ("GJ33", "Valsad", "वलसाड", "વલસાડ", 20.3800, 72.9000, 1705000, 270000)
        ]
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        for district in gujarat_districts:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO districts 
                    (district_code, district_name, district_name_hindi, district_name_gujarati, 
                     latitude, longitude, population, total_households)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', district)
            except Exception as e:
                logger.warning(f"Could not insert district {district[0]}: {str(e)}")
        
        conn.commit()
        conn.close()
    
    def get_all_districts(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT district_code, district_name, district_name_hindi, district_name_gujarati 
            FROM districts ORDER BY district_name
        ''')
        districts = cursor.fetchall()
        conn.close()
        return districts
    
    def get_district_info(self, district_code):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT district_code, district_name, district_name_hindi, district_name_gujarati,
                   state_name, state_name_hindi, state_name_gujarati,
                   population, total_households, latitude, longitude
            FROM districts WHERE district_code = ?
        ''', (district_code,))
        district = cursor.fetchone()
        conn.close()
        return district
    
    def get_district_name(self, district_code):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT district_name FROM districts WHERE district_code = ?', (district_code,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else "Unknown District"
    
    def get_performance_data(self, district_code, year, month):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM performance_data 
            WHERE district_code = ? AND year = ? AND month = ?
        ''', (district_code, year, month))
        
        columns = [desc[0] for desc in cursor.description]
        row = cursor.fetchone()
        conn.close()
        
        if row:
            data = dict(zip(columns, row))
            return {"records": [data]}
        return None
    
    def save_performance_data(self, data):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO performance_data 
            (district_code, year, month, households_provided_employment, persons_worked,
             total_person_days, sc_person_days, st_person_days, women_person_days,
             total_expenditure, works_taken_up, works_completed, avg_days_per_household, data_source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('district_code'),
            data.get('year'),
            data.get('month'),
            data.get('households_provided_employment', 0),
            data.get('persons_worked', 0),
            data.get('total_person_days', 0),
            data.get('sc_person_days', 0),
            data.get('st_person_days', 0),
            data.get('women_person_days', 0),
            data.get('total_expenditure', 0),
            data.get('works_taken_up', 0),
            data.get('works_completed', 0),
            data.get('avg_days_per_household', 0),
            data.get('data_source', 'mock')
        ))
        
        conn.commit()
        conn.close()
    
    def find_nearest_district(self, lat, lon):
        """Find nearest district based on coordinates"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT district_code, district_name, district_name_hindi, district_name_gujarati, latitude, longitude FROM districts')
        districts = cursor.fetchall()
        conn.close()
        
        if not districts:
            return None
        
        nearest = None
        min_distance = float('inf')
        
        for district in districts:
            dist_lat, dist_lon = district[4], district[5]
            if dist_lat and dist_lon:
                distance = math.sqrt((lat - dist_lat)**2 + (lon - dist_lon)**2)
                if distance < min_distance:
                    min_distance = distance
                    nearest = district
        
        return nearest
    
    def get_comparison_data(self, district_code, compare_with='state', year=None, month=None):
        """Get comparison data for a district, year, and month"""
        if year is None:
            year = datetime.now().year
        if month is None:
            month = datetime.now().month
        district_data = self.get_performance_data(district_code, year, month)

        if not district_data or not district_data['records']:
            return None

        base_data = district_data['records'][0]

        # TODO: Replace with real state average calculation from DB if available
        comparison = {
            'district': base_data,
            'state_avg': {
                'households_provided_employment': int(base_data.get('households_provided_employment', 0) * 0.85),
                'persons_worked': int(base_data.get('persons_worked', 0) * 0.88),
                'total_person_days': int(base_data.get('total_person_days', 0) * 0.90),
                'women_participation_rate': 45.2,  # percentage
                'works_completion_rate': 72.1,     # percentage
                'expenditure_per_person': 520      # rupees per person
            },
            'district_rank': 15,
            'total_districts': 33
        }

        return comparison