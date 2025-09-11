from sqlalchemy import func
from sqlalchemy.orm import Session
from .. import models
from datetime import datetime, timedelta
import uuid

# Each rule returns list of Action instances not yet persisted

def rule_site_offline(db: Session):
    actions = []
    incidents = db.query(models.Incident).filter(models.Incident.category=='Site Offline', models.Incident.status=='open').all()
    for inc in incidents:
        action = models.Action(
            id=str(uuid.uuid4()),
            rules_fired='site_offline_p1',
            proposed_action=f'Remote reset chargers at site {inc.site_id}',
            related_entities=str({'site_id': inc.site_id})
        )
        actions.append(action)
    return actions

def rule_firmware_lag(db: Session):
    actions = []
    chargers = db.query(models.Charger).filter(models.Charger.is_latest_firmware==False).all()
    for ch in chargers:
        action = models.Action(
            id=str(uuid.uuid4()),
            rules_fired='firmware_lagging',
            proposed_action=f'Schedule firmware update for charger {ch.id}',
            related_entities=str({'charger_id': ch.id})
        )
        actions.append(action)
    return actions

def rule_excess_refunds(db: Session):
    actions = []
    seven_days_ago = datetime.utcnow()-timedelta(days=7)
    q = db.query(models.Session.charger_id, func.count(models.Session.id).label('cnt'))\
        .filter(models.Session.refund_applied==True, models.Session.start_ts>seven_days_ago)\
        .group_by(models.Session.charger_id)
    for row in q:
        if row.cnt > 5:
            action = models.Action(
                id=str(uuid.uuid4()),
                rules_fired='excess_refunds',
                proposed_action=f'Inspect charger {row.charger_id} for refund spike',
                related_entities=str({'charger_id': row.charger_id})
            )
            actions.append(action)
    return actions

# Add stubs for remaining rules

def rule_underutilized_site(db: Session):
    actions=[]
    thirty_days_ago = datetime.utcnow()-timedelta(days=30)
    sites = db.query(models.Site).all()
    for site in sites:
        sessions = db.query(models.Session).filter(models.Session.site_id==site.id, models.Session.start_ts>thirty_days_ago).all()
        energy = sum(s.kwh for s in sessions)
        power = sum(c.power_kw for c in site.chargers) or 1
        utilization = (energy/(power*24*30))*100
        if utilization < 5:
            action=models.Action(
                id=str(uuid.uuid4()),
                rules_fired='underperforming_site',
                proposed_action=f'Promote tariffs at site {site.id}',
                related_entities=str({'site_id': site.id})
            )
            actions.append(action)
    return actions

# Placeholder rules to reach ten

def rule_payment_failure(db: Session):
    actions=[]
    fails=db.query(models.Incident).filter(models.Incident.category=='Payment failure', models.Incident.created_ts>datetime.utcnow()-timedelta(hours=1)).count()
    if fails>3:
        actions.append(models.Action(id=str(uuid.uuid4()), rules_fired='payment_gateway_intermit', proposed_action='Enable grace sessions', related_entities='{}'))
    return actions

def rule_roaming_fail(db: Session):
    actions=[]
    fails=db.query(models.Incident).filter(models.Incident.category=='Roaming Auth Error', models.Incident.created_ts>datetime.utcnow()-timedelta(hours=1)).count()
    total=db.query(models.Incident).filter(models.Incident.created_ts>datetime.utcnow()-timedelta(hours=1)).count()
    if total and fails/total>0.1:
        actions.append(models.Action(id=str(uuid.uuid4()), rules_fired='roaming_auth_fail', proposed_action='Whitelist tokens for roaming partner', related_entities='{}'))
    return actions

def rule_high_occupancy(db: Session):
    actions=[]
    last_7=datetime.utcnow()-timedelta(days=7)
    sites=db.query(models.Site).all()
    for site in sites:
        sessions=db.query(models.Session).filter(models.Session.site_id==site.id, models.Session.start_ts>last_7).count()
        if sessions>200:
            actions.append(models.Action(id=str(uuid.uuid4()), rules_fired='high_occupancy', proposed_action=f'Evaluate capacity at site {site.id}', related_entities=str({'site_id':site.id})))
    return actions

def rule_energy_cost_spike(db: Session):
    cfg=db.query(models.Config).filter(models.Config.key=='energy_cost_spike').first()
    if cfg and cfg.value=='1':
        return [models.Action(id=str(uuid.uuid4()), rules_fired='energy_cost_spike', proposed_action='Adjust tariff floors', related_entities='{}')]
    return []

def rule_sla_breach(db: Session):
    actions=[]
    now=datetime.utcnow()
    incs=db.query(models.Incident).filter(models.Incident.status=='open').all()
    for inc in incs:
        deadline=inc.created_ts+timedelta(minutes=inc.sla_minutes)
        if deadline-now < timedelta(minutes=30):
            actions.append(models.Action(id=str(uuid.uuid4()), rules_fired='sla_breach_risk', proposed_action=f'Escalate incident {inc.id}', related_entities=str({'incident_id':inc.id})))
    return actions

RULES=[
    rule_site_offline,
    rule_firmware_lag,
    rule_excess_refunds,
    rule_underutilized_site,
    rule_payment_failure,
    rule_roaming_fail,
    rule_high_occupancy,
    rule_energy_cost_spike,
    rule_sla_breach,
]
