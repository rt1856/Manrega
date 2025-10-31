# fetcher.py
import os
import requests
from datetime import datetime
from utils import SessionLocal, engine
from models import Base, District, MonthlyMetric
from sqlalchemy.exc import IntegrityError

# create tables if not exists
Base.metadata.create_all(bind=engine)

API_KEY = os.getenv('DATA_GOV_API_KEY')
RESOURCE_ID = os.getenv('DATA_GOV_RESOURCE_ID')  # set if you want to use real data.gov resource

def seed_demo():
    session = SessionLocal()
    # check existing
    if session.query(District).count() > 0:
        print("Districts already present; skipping seed.")
        session.close()
        return

    # Insert three sample districts
    d1 = District(state='Gujarat', district_code='GD-GNR', district_name='Gandhinagar', centroid_lat=23.2156, centroid_lon=72.6369)
    d2 = District(state='Gujarat', district_code='GD-SRT', district_name='Surat', centroid_lat=21.1702, centroid_lon=72.8311)
    d3 = District(state='Gujarat', district_code='GD-PBR', district_name='Porbandar', centroid_lat=21.6417, centroid_lon=69.6042)
    session.add_all([d1,d2,d3])
    session.commit()

    # Add monthly metrics (demo)
    def add_metric(district_id, y, m, pdays, hh, wage, ben):
        mm = MonthlyMetric(
            district_id=district_id, year=y, month=m,
            person_days=pdays, households=hh, avg_wage=wage, beneficiaries=ben,
            source_updated_at=datetime.utcnow()
        )
        try:
            session.add(mm)
            session.commit()
        except IntegrityError:
            session.rollback()

    add_metric(d1.id, 2025, 9, 2510000, 58000, 235.0, 125480)
    add_metric(d2.id, 2025, 9, 2480000, 62000, 240.0, 142000)
    add_metric(d3.id, 2025, 9, 920000, 23000, 210.0, 45000)
    print("Seed done")
    session.close()

def fetch_from_datagov():
    """
    Template to fetch real data from data.gov.in. You must:
    - set RESOURCE_ID to the resource id for the MGNREGA dataset,
    - map fields of 'records' to the MonthlyMetric columns.
    This function demonstrates pattern and backoff.
    """
    if not API_KEY or not RESOURCE_ID:
        print("DATA_GOV_API_KEY or RESOURCE_ID missing in env; skipping real fetch.")
        return

    url = f"https://api.data.gov.in/backend/datagov/resource-download?resource_id={RESOURCE_ID}"
    # Note: actual endpoint and params may vary. Check data.gov.in docs for exact endpoint.
    params = {'api-key': API_KEY}
    try:
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        # parse and insert into DB similarly to seed_demo
        # Implementation depends on the response JSON or CSV returned by the resource.
    except Exception as e:
        print("Error fetching from data.gov:", e)

if __name__ == '__main__':
    seed_demo()
    # fetch_from_datagov()  # optional: enable once RESOURCE_ID and API_KEY are set
