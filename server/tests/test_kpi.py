import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import pytest
from server import models, kpi
from server.database import SessionLocal, engine, Base
from datetime import datetime, timedelta

@pytest.fixture(scope='module')
def db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    site = models.Site(name='Test', country='IE', lat=0, lon=0)
    db.add(site); db.flush()
    ch = models.Charger(site_id=site.id, model='A', ocpp_version='1.6J', power_kw=50, connectors='CCS', install_date=datetime.utcnow(), firmware_version='1.0', is_latest_firmware=True)
    db.add(ch); db.flush()
    now = datetime.utcnow()
    sess = models.Session(site_id=site.id, charger_id=ch.id, start_ts=now-timedelta(hours=1), end_ts=now, kwh=10, energy_price_per_kwh=0.4, total_cost=4, payment_type='App', driver_segment='Public', refund_applied=False, vat_rate=0.23)
    db.add(sess)
    inc = models.Incident(site_id=site.id, charger_id=ch.id, created_ts=now-timedelta(hours=2), closed_ts=now-timedelta(hours=1), category='Connector Fault', severity='P1', status='closed', first_contact_resolved=True)
    db.add(inc)
    db.commit()
    yield db
    db.close()


def test_summary_with_mode(db):
    pre = kpi.compute_summary(db, 'pre')
    post = kpi.compute_summary(db, 'with')
    assert post['uptime_pct'] > pre['uptime_pct']
    assert post['mttr_hours'] < pre['mttr_hours']
