from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class Site(Base):
    __tablename__ = 'sites'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    country = Column(String, nullable=False)
    address = Column(String)
    lat = Column(Float)
    lon = Column(Float)
    site_type = Column(String)
    owner_type = Column(String)
    sla_tier = Column(String)
    grid_kw = Column(Float)

    chargers = relationship('Charger', back_populates='site')
    incidents = relationship('Incident', back_populates='site')

class Charger(Base):
    __tablename__ = 'chargers'
    id = Column(Integer, primary_key=True)
    site_id = Column(Integer, ForeignKey('sites.id'))
    model = Column(String)
    ocpp_version = Column(String)
    power_kw = Column(Float)
    connectors = Column(String)
    install_date = Column(DateTime)
    firmware_version = Column(String)
    is_latest_firmware = Column(Boolean, default=True)

    site = relationship('Site', back_populates='chargers')
    sessions = relationship('Session', back_populates='charger')

class Session(Base):
    __tablename__ = 'sessions'
    id = Column(Integer, primary_key=True)
    site_id = Column(Integer, ForeignKey('sites.id'))
    charger_id = Column(Integer, ForeignKey('chargers.id'))
    start_ts = Column(DateTime)
    end_ts = Column(DateTime)
    kwh = Column(Float)
    energy_price_per_kwh = Column(Float)
    total_cost = Column(Float)
    payment_type = Column(String)
    driver_segment = Column(String)
    refund_applied = Column(Boolean, default=False)
    vat_rate = Column(Float, default=0.2)

    charger = relationship('Charger', back_populates='sessions')

class Incident(Base):
    __tablename__ = 'incidents'
    id = Column(Integer, primary_key=True)
    site_id = Column(Integer, ForeignKey('sites.id'))
    charger_id = Column(Integer, ForeignKey('chargers.id'), nullable=True)
    created_ts = Column(DateTime, default=datetime.utcnow)
    closed_ts = Column(DateTime, nullable=True)
    category = Column(String)
    severity = Column(String)
    status = Column(String, default='open')
    sla_minutes = Column(Integer, default=240)
    first_contact_resolved = Column(Boolean, default=False)

    site = relationship('Site', back_populates='incidents')

class Action(Base):
    __tablename__ = 'actions'
    id = Column(String, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    rules_fired = Column(String)
    proposed_action = Column(String)
    status = Column(String, default='Proposed')
    related_entities = Column(String)  # JSON string
    expected_outcome = Column(String)
    measured_outcome = Column(String)

class Config(Base):
    __tablename__ = 'config'
    key = Column(String, primary_key=True)
    value = Column(String)
