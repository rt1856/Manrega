"""
DatabaseManager utility module.
Only database-related classes and functions should be defined here.
Remove all Flask app routes and rendering logic.
"""

import sqlite3
import math
import random
from datetime import datetime
import logging
import os
from typing import List, Dict, Optional, Tuple, Any
import json

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = 'database/mgnrega.db'):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self) -> None:
        """Initialize database with required tables"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Enable foreign keys and WAL mode for better performance
            cursor.execute('PRAGMA foreign_keys = ON')
            cursor.execute('PRAGMA journal_mode = WAL')
            
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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Performance data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    district_code TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    month INTEGER NOT NULL,
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
                    FOREIGN KEY (district_code) REFERENCES districts (district_code),
                    UNIQUE(district_code, year, month)
                )
            ''')
            
            # Analytics cache table for faster comparisons
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analytics_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cache_key TEXT UNIQUE NOT NULL,
                    cache_data TEXT NOT NULL,
                    expires_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_district_code ON districts(district_code)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_performance_district ON performance_data(district_code)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_performance_year_month ON performance_data(year, month)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_performance_composite ON performance_data(district_code, year, month)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_cache_key ON analytics_cache(cache_key)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_expires ON analytics_cache(expires_at)')
            
            conn.commit()
            conn.close()
            
            # Load initial data
            self.load_initial_data()
            logger.info("Database initialized successfully!")
            
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def load_initial_data(self) -> None:
        """Load initial data with realistic sample data"""
        gujarat_districts = [
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
        
        # Check if data already exists to avoid duplicates
        cursor.execute('SELECT COUNT(*) FROM districts')
        existing_districts = cursor.fetchone()[0]
        
        if existing_districts > 0:
            logger.info(f"Database already contains {existing_districts} districts. Skipping initial data load.")
            conn.close()
            return
        
        # Insert districts
        inserted_count = 0
        for district in gujarat_districts:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO districts 
                    (district_code, district_name, district_name_hindi, district_name_gujarati, 
                     latitude, longitude, population, total_households)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', district)
                if cursor.rowcount > 0:
                    inserted_count += 1
            except Exception as e:
                logger.warning(f"Could not insert district {district[0]}: {str(e)}")
        
        # Generate sample performance data for current year and previous months
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        # Generate data for last 6 months
        for i in range(6):
            month = current_month - i
            year = current_year
            if month <= 0:
                month += 12
                year -= 1
            
            for district_code, _, _, _, _, _, population, households in gujarat_districts:
                # Generate realistic random data
                base_employment = random.randint(int(households * 0.08), int(households * 0.18))
                base_persons = random.randint(int(base_employment * 1.5), int(base_employment * 2.2))
                base_days = random.randint(base_persons * 40, base_persons * 60)
                
                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO performance_data 
                        (district_code, year, month, households_provided_employment, persons_worked,
                         total_person_days, sc_person_days, st_person_days, women_person_days,
                         total_expenditure, works_taken_up, works_completed, avg_days_per_household, data_source)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        district_code,
                        year,
                        month,
                        base_employment,
                        base_persons,
                        base_days,
                        int(base_days * random.uniform(0.3, 0.4)),  # SC
                        int(base_days * random.uniform(0.2, 0.3)),  # ST
                        int(base_days * random.uniform(0.4, 0.5)),  # Women
                        base_days * random.randint(200, 300),  # Expenditure
                        random.randint(int(base_employment * 0.7), int(base_employment * 0.9)),
                        random.randint(int(base_employment * 0.5), int(base_employment * 0.8)),
                        random.uniform(40, 60),
                        'sample'
                    ))
                except Exception as e:
                    logger.warning(f"Could not insert performance data for {district_code}: {str(e)}")
        
        # Clear old cache
        cursor.execute('DELETE FROM analytics_cache WHERE expires_at < datetime("now")')
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized with {inserted_count} districts and sample performance data!")
    
    def get_all_districts(self) -> List[Tuple]:
        """Get all districts with basic info"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT district_code, district_name, district_name_hindi, district_name_gujarati 
                FROM districts ORDER BY district_name
            ''')
            districts = cursor.fetchall()
            conn.close()
            return districts
        except Exception as e:
            logger.error(f"Error getting districts: {str(e)}")
            return []
    
    def get_district_info(self, district_code: str) -> Optional[Dict[str, Any]]:
        """Get detailed district information"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT district_code, district_name, district_name_hindi, district_name_gujarati,
                       state_name, state_name_hindi, state_name_gujarati,
                       population, total_households, latitude, longitude
                FROM districts WHERE district_code = ?
            ''', (district_code,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            return None
        except Exception as e:
            logger.error(f"Error getting district info for {district_code}: {str(e)}")
            return None
    
    def get_performance_data(self, district_code: str, year: Optional[int] = None, month: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Get performance data for dashboard"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if year and month:
                cursor.execute('''
                    SELECT * FROM performance_data 
                    WHERE district_code = ? AND year = ? AND month = ?
                ''', (district_code, year, month))
            else:
                # Get latest data for the district
                cursor.execute('''
                    SELECT * FROM performance_data 
                    WHERE district_code = ? 
                    ORDER BY year DESC, month DESC 
                    LIMIT 1
                ''', (district_code,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            
            # If no data found, return default data
            return self._get_default_performance_data(district_code)
            
        except Exception as e:
            logger.error(f"Error getting performance data for {district_code}: {str(e)}")
            return self._get_default_performance_data(district_code)
    
    def _get_default_performance_data(self, district_code: str) -> Dict[str, Any]:
        """Generate default performance data when no data exists"""
        district_info = self.get_district_info(district_code)
        households = district_info['total_households'] if district_info else 200000
        
        base_employment = int(households * 0.12)
        base_persons = int(base_employment * 1.8)
        base_days = base_persons * 48
        
        return {
            'district_code': district_code,
            'year': datetime.now().year,
            'month': datetime.now().month,
            'households_provided_employment': base_employment,
            'persons_worked': base_persons,
            'total_person_days': base_days,
            'sc_person_days': int(base_days * 0.35),
            'st_person_days': int(base_days * 0.25),
            'women_person_days': int(base_days * 0.45),
            'total_expenditure': base_days * 280,
            'works_taken_up': int(base_employment * 0.15),
            'works_completed': int(base_employment * 0.12),
            'avg_days_per_household': 48.0,
            'data_source': 'default'
        }
    
    def save_performance_data(self, data: Dict[str, Any]) -> bool:
        """Save performance data to database"""
        try:
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
            return True
            
        except Exception as e:
            logger.error(f"Error saving performance data: {str(e)}")
            return False
    
    def find_nearest_district(self, lat: float, lon: float) -> Optional[Tuple]:
        """Find nearest district based on coordinates"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT district_code, district_name, district_name_hindi, district_name_gujarati, latitude, longitude 
                FROM districts WHERE latitude IS NOT NULL AND longitude IS NOT NULL
            ''')
            districts = cursor.fetchall()
            conn.close()
            
            if not districts:
                return None
            
            nearest = None
            min_distance = float('inf')
            
            for district in districts:
                dist_lat, dist_lon = district[4], district[5]
                if dist_lat and dist_lon:
                    distance = self.calculate_distance(lat, lon, dist_lat, dist_lon)
                    if distance < min_distance:
                        min_distance = distance
                        nearest = district
            
            logger.info(f"Nearest district: {nearest[1]} with distance {min_distance:.2f} km")
            return nearest
        except Exception as e:
            logger.error(f"Error finding nearest district: {str(e)}")
            return None
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates using Haversine formula"""
        # Convert degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        radius = 6371  # Earth radius in kilometers
        return radius * c
    
    def get_comparison_data(self, district_code: str, compare_with: str = 'state') -> Dict[str, Any]:
        """Get comparison data for comparison page"""
        try:
            # Get district data
            district_data = self.get_performance_data(district_code)
            
            if not district_data:
                district_data = self._get_default_performance_data(district_code)
            
            # Calculate state averages
            state_avg = self.calculate_state_averages()
            
            # Calculate district rank
            district_rank, total_districts = self.calculate_district_rank(district_code)
            
            # Prepare comparison data
            comparison_data = {
                'district': district_data,
                'state_avg': state_avg,
                'district_rank': district_rank,
                'total_districts': total_districts,
                'comparison_type': compare_with
            }
            
            # Add percentage comparisons
            comparison_data['comparison_percentages'] = self._calculate_comparison_percentages(district_data, state_avg)
            
            return comparison_data
            
        except Exception as e:
            logger.error(f"Error getting comparison data for {district_code}: {str(e)}")
            return self.get_default_comparison_data(district_code)
    
    def _calculate_comparison_percentages(self, district_data: Dict[str, Any], state_avg: Dict[str, Any]) -> Dict[str, float]:
        """Calculate percentage differences between district and state average"""
        percentages = {}
        
        metrics = [
            'households_provided_employment',
            'persons_worked', 
            'total_person_days',
            'works_completed'
        ]
        
        for metric in metrics:
            district_val = district_data.get(metric, 0)
            state_val = state_avg.get(metric, 1)  # Avoid division by zero
            
            if state_val > 0:
                percentage = ((district_val - state_val) / state_val) * 100
                percentages[metric] = round(percentage, 1)
            else:
                percentages[metric] = 0.0
        
        return percentages
    
    def calculate_state_averages(self) -> Dict[str, Any]:
        """Calculate state averages from all districts"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            current_year = datetime.now().year
            current_month = datetime.now().month
            
            cursor.execute('''
                SELECT 
                    AVG(households_provided_employment) as avg_households,
                    AVG(persons_worked) as avg_persons,
                    AVG(total_person_days) as avg_days,
                    AVG(works_completed) as avg_works_completed,
                    AVG((women_person_days * 100.0 / NULLIF(total_person_days, 0))) as avg_women_rate,
                    AVG((works_completed * 100.0 / NULLIF(works_taken_up, 0))) as avg_completion_rate,
                    AVG(total_expenditure / NULLIF(persons_worked, 0)) as avg_exp_per_person
                FROM performance_data
                WHERE year = ? AND month = ?
            ''', (current_year, current_month))
            
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0] is not None:
                return {
                    'households_provided_employment': round(result[0] or 0),
                    'persons_worked': round(result[1] or 0),
                    'total_person_days': round(result[2] or 0),
                    'works_completed': round(result[3] or 0),
                    'women_participation_rate': round(result[4] or 0, 1),
                    'works_completion_rate': round(result[5] or 0, 1),
                    'expenditure_per_person': round(result[6] or 0)
                }
            
            return self.get_default_state_averages()
            
        except Exception as e:
            logger.error(f"Error calculating state averages: {str(e)}")
            return self.get_default_state_averages()
    
    def calculate_district_rank(self, district_code: str) -> Tuple[int, int]:
        """Calculate district rank based on performance"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM districts')
            total_districts = cursor.fetchone()[0]
            
            # Simple ranking based on households employed
            cursor.execute('''
                SELECT pd.district_code, pd.households_provided_employment
                FROM performance_data pd
                INNER JOIN (
                    SELECT district_code, MAX(year) as max_year, MAX(month) as max_month
                    FROM performance_data
                    GROUP BY district_code
                ) latest ON pd.district_code = latest.district_code 
                         AND pd.year = latest.max_year 
                         AND pd.month = latest.max_month
                ORDER BY pd.households_provided_employment DESC
            ''')
            
            ranked_districts = cursor.fetchall()
            conn.close()
            
            for rank, (code, _) in enumerate(ranked_districts, 1):
                if code == district_code:
                    return rank, total_districts
            
            return total_districts, total_districts
            
        except Exception as e:
            logger.error(f"Error calculating district rank: {str(e)}")
            return 1, 33
    
    def get_default_state_averages(self) -> Dict[str, Any]:
        """Return default state averages"""
        return {
            'households_provided_employment': 12500,
            'persons_worked': 22500,
            'total_person_days': 425000,
            'works_completed': 850,
            'women_participation_rate': 42.5,
            'works_completion_rate': 68.3,
            'expenditure_per_person': 275
        }
    
    def get_default_comparison_data(self, district_code: str) -> Dict[str, Any]:
        """Return default data when no real data is available"""
        district_data = self._get_default_performance_data(district_code)
        state_avg = self.get_default_state_averages()
        
        return {
            'district': district_data,
            'state_avg': state_avg,
            'district_rank': 8,
            'total_districts': 33,
            'comparison_type': 'state',
            'comparison_percentages': {
                'households_provided_employment': 20.0,
                'persons_worked': 24.4,
                'total_person_days': 22.4,
                'works_completed': 4.7
            }
        }
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            stats = {}
            
            # Count districts
            cursor.execute('SELECT COUNT(*) FROM districts')
            stats['total_districts'] = cursor.fetchone()[0]
            
            # Count performance records
            cursor.execute('SELECT COUNT(*) FROM performance_data')
            stats['total_performance_records'] = cursor.fetchone()[0]
            
            # Latest data date
            cursor.execute('SELECT MAX(year), MAX(month) FROM performance_data')
            latest = cursor.fetchone()
            stats['latest_data'] = f"{latest[1]}/{latest[0]}" if latest[0] else "No data"
            
            conn.close()
            return stats
        except Exception as e:
            logger.error(f"Error getting database stats: {str(e)}")
            return {'error': str(e)}