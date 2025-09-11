from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models
from datetime import datetime, timedelta

IMPROVEMENTS = {
    'mttr_reduction': 0.55,
    'uptime_pp': 1.8,
    'fcr_pp': 20.0,
    'refund_rel': 0.30,
    'revenue_pct': 0.07,
    'roaming_pp': 5.0,
    'firmware_pp': 35.0,
}

def compute_summary(db: Session, mode: str = 'pre'):
    total_sessions = db.query(models.Session).count()
    refunded_sessions = db.query(models.Session).filter(models.Session.refund_applied==True).count()
    refund_rate = (refunded_sessions / total_sessions)*100 if total_sessions else 0

    total_cost = db.query(func.sum(models.Session.total_cost/(1+models.Session.vat_rate))).scalar() or 0

    incidents = db.query(models.Incident).filter(models.Incident.severity.in_(['P1','P2']), models.Incident.closed_ts!=None).all()
    if incidents:
        mttr = sum((i.closed_ts - i.created_ts).total_seconds() for i in incidents)/len(incidents)/3600
    else:
        mttr = 0

    total_minutes = 180*24*60*db.query(models.Charger).count()
    downtime = 0
    down_incidents = db.query(models.Incident).filter(models.Incident.category.in_(['Site Offline','Connector Fault','Site Offline P1']))
    for inc in down_incidents:
        end = inc.closed_ts or datetime.utcnow()
        downtime += (end - inc.created_ts).total_seconds()/60
    uptime = 100.0*(1 - downtime/total_minutes) if total_minutes else 100

    energy = db.query(func.sum(models.Session.kwh)).scalar() or 0
    total_power = db.query(func.sum(models.Charger.power_kw)).scalar() or 1
    utilization = (energy/(total_power*180*24))*100

    fcr_total = db.query(models.Incident).filter(models.Incident.first_contact_resolved!=None).count()
    fcr_true = db.query(models.Incident).filter(models.Incident.first_contact_resolved==True).count()
    fcr = (fcr_true/fcr_total)*100 if fcr_total else 0

    if mode=='with':
        mttr *= (1-IMPROVEMENTS['mttr_reduction'])
        uptime += IMPROVEMENTS['uptime_pp']
        fcr += IMPROVEMENTS['fcr_pp']
        refund_rate *= (1-IMPROVEMENTS['refund_rel'])
        total_cost *= (1+IMPROVEMENTS['revenue_pct'])

    return {
        'uptime_pct': uptime,
        'utilization_pct': utilization,
        'mttr_hours': mttr,
        'fcr_pct': fcr,
        'refund_rate_pct': refund_rate,
        'revenue_eur': total_cost,
    }


def site_kpis(db: Session, site: models.Site):
    sessions = db.query(models.Session).filter(models.Session.site_id==site.id)
    energy = sum(s.kwh for s in sessions)
    power = sum(c.power_kw for c in site.chargers) or 1
    utilization = (energy/(power*180*24))*100
    incidents = [i for i in site.incidents if i.closed_ts]
    if incidents:
        mttr = sum((i.closed_ts - i.created_ts).total_seconds() for i in incidents)/len(incidents)/3600
    else:
        mttr = 0
    fcr_total = len([i for i in site.incidents if i.first_contact_resolved is not None])
    fcr = len([i for i in site.incidents if i.first_contact_resolved])/fcr_total*100 if fcr_total else 0
    refunds = db.query(models.Session).filter(models.Session.site_id==site.id, models.Session.refund_applied==True).count()
    total_sessions = db.query(models.Session).filter(models.Session.site_id==site.id).count()
    refund_rate = (refunds/total_sessions)*100 if total_sessions else 0
    revenue = sum(s.total_cost/(1+s.vat_rate) for s in sessions)
    downtime = 0
    for inc in site.incidents:
        if inc.category in ['Site Offline','Connector Fault']:
            end = inc.closed_ts or datetime.utcnow()
            downtime += (end - inc.created_ts).total_seconds()/60
    total_minutes = 180*24*60*len(site.chargers)
    uptime = 100*(1 - downtime/total_minutes) if total_minutes else 100
    return {
        'uptime_pct': uptime,
        'utilization_pct': utilization,
        'mttr_hours': mttr,
        'fcr_pct': fcr,
        'revenue_month': revenue,
        'refund_rate_pct': refund_rate
    }
