# models.py
from sqlalchemy import Column, Integer, String, Float, BigInteger, DateTime, JSON, UniqueConstraint, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class District(Base):
    __tablename__ = 'districts'
    id = Column(Integer, primary_key=True)
    state = Column(String(100), nullable=False)
    district_code = Column(String(64), nullable=False, unique=True)
    district_name = Column(String(200), nullable=False)
    centroid_lat = Column(Float)
    centroid_lon = Column(Float)

class MonthlyMetric(Base):
    __tablename__ = 'monthly_metrics'
    id = Column(Integer, primary_key=True)
    district_id = Column(Integer, ForeignKey('districts.id', ondelete='CASCADE'), nullable=False)
    district = relationship('District', backref='metrics')
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    person_days = Column(BigInteger, default=0)
    households = Column(BigInteger, default=0)
    avg_wage = Column(Float, default=0.0)
    beneficiaries = Column(BigInteger, default=0)
    other_json = Column(JSON)
    source_updated_at = Column(DateTime)
    fetched_at = Column(DateTime, server_default=func.now())
    __table_args__ = (UniqueConstraint('district_id', 'year', 'month', name='uix_district_month'),)
