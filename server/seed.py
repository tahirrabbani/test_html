from .database import Base, engine, SessionLocal
from . import models
from faker import Faker
import random
from datetime import datetime, timedelta
import argparse

RANDOM_SEED = 424242
faker = Faker()
random.seed(RANDOM_SEED)
Faker.seed(RANDOM_SEED)

SITE_DATA = [
    ('Viztronics Dublin Central','IE',53.3498,-6.2603),
    ('Viztronics Cork','IE',51.8985,-8.4756),
    ('Viztronics Galway','IE',53.2707,-9.0568),
    ('Viztronics Belfast','UK',54.5973,-5.9301),
    ('Viztronics London','UK',51.5074,-0.1278),
    ('Viztronics Manchester','UK',53.4808,-2.2426),
    ('Viztronics Birmingham','UK',52.4862,-1.8904),
    ('Viztronics Glasgow','UK',55.8642,-4.2518),
    ('Viztronics Bristol','UK',51.4545,-2.5879),
    ('Viztronics Leeds','UK',53.8008,-1.5491),
]

CHARGER_MODELS=['Alpitronic Hyper 150','ABB Terra 54','Tritium RT50','Wallbox Copper']
OCPP=['1.6J','2.0.1']
CONNECTORS=['Type2','CCS','CHAdeMO']


def seed(reset=False):
    if reset:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db=SessionLocal()
    if db.query(models.Site).first():
        db.close()
        return

    sites=[]
    for idx, (name,country,lat,lon) in enumerate(SITE_DATA):
        site=models.Site(name=name,country=country,address=faker.address(),lat=lat,lon=lon,site_type=random.choice(['Public','Depot','Workplace']),owner_type=random.choice(['Owned','3rd-party']),sla_tier=random.choice(['Gold','Silver','Bronze']),grid_kw=random.choice([100,200,400]))
        db.add(site)
        db.flush()
        sites.append(site)
        for _ in range(2 if idx%2==0 else 3):
            ch=models.Charger(site_id=site.id,model=random.choice(CHARGER_MODELS),ocpp_version=random.choice(OCPP),power_kw=random.choice([22,50,150]),connectors=','.join(random.sample(CONNECTORS,1)),install_date=datetime.utcnow()-timedelta(days=random.randint(200,400)),firmware_version=random.choice(['1.0','1.1','1.2']),is_latest_firmware=random.random()<0.6)
            db.add(ch)
    db.commit()

    chargers=db.query(models.Charger).all()
    # Sessions
    for _ in range(3000):
        ch=random.choice(chargers)
        duration=random.gauss(34,12)
        duration=max(10,min(duration,120))
        start=datetime.utcnow()-timedelta(days=random.randint(0,179),minutes=random.randint(0,1439))
        end=start+timedelta(minutes=duration)
        kwh=ch.power_kw*duration/60*0.9
        price=0.4 if ch.site.country=='IE' else 0.45
        cost=kwh*price
        session=models.Session(site_id=ch.site_id,charger_id=ch.id,start_ts=start,end_ts=end,kwh=kwh,energy_price_per_kwh=price,total_cost=cost,payment_type=random.choice(['App','RFID','Roaming','Fleet']),driver_segment=random.choice(['Public','Fleet','Roaming']),refund_applied=random.random()<0.03,vat_rate=0.23 if ch.site.country=='IE' else 0.20)
        db.add(session)
    db.commit()

    # Incidents
    for _ in range(200):
        site=random.choice(sites)
        charger=random.choice(site.chargers)
        created=datetime.utcnow()-timedelta(days=random.randint(0,179),hours=random.randint(0,23))
        dur=timedelta(hours=random.randint(1,8))
        closed=created+dur
        inc=models.Incident(site_id=site.id,charger_id=charger.id,created_ts=created,closed_ts=closed,category=random.choice(['Payment failure','Stuck in Finishing','Connector Fault','Site Offline','Roaming Auth Error','Firmware Needed']),severity=random.choice(['P1','P2','P3']),status='closed',sla_minutes=random.choice([120,240,480]),first_contact_resolved=random.random()<0.7)
        db.add(inc)
    db.commit()

    db.close()

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--reset',action='store_true')
    args=parser.parse_args()
    seed(reset=args.reset)
