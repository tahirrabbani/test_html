import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import pytest
from server.agent import rules
from server.database import SessionLocal, engine, Base
from server import models
from datetime import datetime, timedelta

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    site = models.Site(name='S', country='IE', lat=0, lon=0)
    db.add(site); db.flush()
    ch = models.Charger(site_id=site.id, model='A', ocpp_version='1.6J', power_kw=22, connectors='CCS', install_date=datetime.utcnow(), firmware_version='1.0', is_latest_firmware=False)
    db.add(ch); db.flush()
    now = datetime.utcnow()
    inc = models.Incident(site_id=site.id, charger_id=ch.id, created_ts=now-timedelta(hours=1), category='Site Offline', severity='P1', status='open')
    db.add(inc)
    db.commit()
    yield db
    db.close()


def test_rules_detect(db):
    acts = rules.rule_site_offline(db)
    assert acts
    acts2 = rules.rule_firmware_lag(db)
    assert acts2
