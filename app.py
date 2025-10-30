# app.py
import os
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from utlis import SessionLocal
from models import District, MonthlyMetric
from sqlalchemy import desc, func
# serve static files from project root (index.html and styles.css are at repo root)
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Serve frontend
@app.route('/')
def index():
    # index.html lives at the project root in this repo, serve it directly
    return app.send_static_file('index.html')

# 1) list districts (state filter optional)
@app.route('/api/districts')
def list_districts():
    state = request.args.get('state', 'Gujarat')
    try:
        session = SessionLocal()
    except Exception as e:
        return jsonify({'error': 'database connection failed', 'details': str(e)}), 503
    try:
        q = session.query(District).filter(District.state == state).order_by(District.district_name).all()
        items = [{'id': d.id, 'code': d.district_code, 'name': d.district_name, 'lat': d.centroid_lat, 'lon': d.centroid_lon} for d in q]
        return jsonify(items)
    except Exception as e:
        return jsonify({'error': 'query failed', 'details': str(e)}), 500
    finally:
        session.close()

# 2) nearest district by coords (simple Euclidean nearest on centroid)
@app.route('/api/nearest-district')
def nearest_district():
    try:
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))
    except Exception:
        return jsonify({'error':'lat/lon required'}), 400
    try:
        session = SessionLocal()
    except Exception as e:
        return jsonify({'error': 'database connection failed', 'details': str(e)}), 503
    try:
        rows = session.query(District).all()
    except Exception as e:
        return jsonify({'error': 'query failed', 'details': str(e)}), 500
    finally:
        session.close()
    if not rows:
        return jsonify({'error': 'no districts in DB'}), 404
    # find nearest by centroid (simple)
    def dist_sq(d):
        if d.centroid_lat is None or d.centroid_lon is None:
            return float('inf')
        return (d.centroid_lat - lat)**2 + (d.centroid_lon - lon)**2
    nearest = min(rows, key=dist_sq)
    return jsonify({'id': nearest.id, 'code': nearest.district_code, 'name': nearest.district_name})

# 3) latest metrics for district
@app.route('/api/district/<int:district_id>/latest')
def district_latest(district_id):
    try:
        session = SessionLocal()
    except Exception as e:
        return jsonify({'error': 'database connection failed', 'details': str(e)}), 503
    try:
        row = session.query(MonthlyMetric).filter(MonthlyMetric.district_id==district_id).order_by(desc(MonthlyMetric.year), desc(MonthlyMetric.month)).first()
    except Exception as e:
        return jsonify({'error':'query failed','details':str(e)}), 500
    finally:
        session.close()
    if not row:
        return jsonify({'error':'no data'}), 404
    return jsonify({
        'year': row.year, 'month': row.month,
        'person_days': int(row.person_days or 0),
        'beneficiaries': int(row.beneficiaries or 0),
        'avg_wage': float(row.avg_wage or 0),
        'source_updated_at': row.source_updated_at.isoformat() if row.source_updated_at else None
    })

# 4) 12-month trend
@app.route('/api/district/<int:district_id>/trend')
def district_trend(district_id):
    try:
        session = SessionLocal()
    except Exception as e:
        return jsonify({'error': 'database connection failed', 'details': str(e)}), 503
    try:
        rows = session.query(MonthlyMetric).filter(MonthlyMetric.district_id==district_id).order_by(MonthlyMetric.year, MonthlyMetric.month).all()
    except Exception as e:
        return jsonify({'error':'query failed','details':str(e)}), 500
    finally:
        session.close()
    data = [{'year': r.year, 'month': r.month, 'person_days': int(r.person_days or 0), 'avg_wage': float(r.avg_wage or 0)} for r in rows]
    return jsonify(data)

# 5) compare vs state average for latest month
@app.route('/api/district/<int:district_id>/compare')
def district_compare(district_id):
    try:
        session = SessionLocal()
    except Exception as e:
        return jsonify({'error': 'database connection failed', 'details': str(e)}), 503
    try:
        last = session.query(MonthlyMetric).filter(MonthlyMetric.district_id==district_id).order_by(desc(MonthlyMetric.year), desc(MonthlyMetric.month)).first()
        if not last:
            return jsonify({'error':'no data'}), 404
        # find state
        district = session.query(District).get(district_id)
        state = district.state
        # compute state average person_days for same month
        agg = session.query(func.avg(MonthlyMetric.person_days)).join(District, District.id == MonthlyMetric.district_id).filter(District.state==state, MonthlyMetric.year==last.year, MonthlyMetric.month==last.month).scalar()
        return jsonify({
            'district': {'person_days': int(last.person_days or 0), 'avg_wage': float(last.avg_wage or 0)},
            'state_avg_person_days': int(agg or 0)
        })
    except Exception as e:
        return jsonify({'error':'query failed','details':str(e)}), 500
    finally:
        session.close()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
