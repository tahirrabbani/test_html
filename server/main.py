from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import get_db, engine
from . import models, schemas, kpi
from .agent import engine as agent_engine
from sqlalchemy.orm import Session
import os

app = FastAPI(title='Viztronics Chargepoint Copilot (Demo)')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

models.Base.metadata.create_all(bind=engine)

if os.path.isdir('client/dist'):
    app.mount('/', StaticFiles(directory='client/dist', html=True), name='static')

@app.get('/api/summary', response_model=schemas.SummaryOut)
async def summary(mode: str='pre', db: Session = Depends(get_db)):
    data = kpi.compute_summary(db, mode)
    return schemas.SummaryOut(**data)

@app.get('/api/sites', response_model=list[schemas.SiteOut])
async def list_sites(db: Session = Depends(get_db)):
    sites = db.query(models.Site).all()
    results=[]
    for s in sites:
        kpis = kpi.site_kpis(db, s)
        results.append(schemas.SiteOut(id=s.id,name=s.name,country=s.country,lat=s.lat,lon=s.lon,site_type=s.site_type,owner_type=s.owner_type,sla_tier=s.sla_tier,grid_kw=s.grid_kw,kpis=schemas.SiteKPI(**kpis)))
    return results

@app.get('/api/incidents', response_model=list[schemas.IncidentOut])
async def list_incidents(db: Session = Depends(get_db)):
    incs = db.query(models.Incident).all()
    return [schemas.IncidentOut(id=i.id,site_id=i.site_id,category=i.category,severity=i.severity,status=i.status,created_ts=i.created_ts,closed_ts=i.closed_ts) for i in incs]

@app.post('/api/agent/suggest', response_model=list[schemas.ActionOut])
async def suggest(db: Session = Depends(get_db)):
    actions = agent_engine.suggest_actions(db)
    return [schemas.ActionOut(id=a.id,proposed_action=a.proposed_action,status=a.status,rules_fired=a.rules_fired) for a in actions]

@app.post('/api/agent/execute', response_model=schemas.ActionOut)
async def execute(action_id: str, db: Session = Depends(get_db)):
    action=agent_engine.execute_action(db, action_id)
    if not action:
        raise HTTPException(404, 'action not found')
    return schemas.ActionOut(id=action.id,proposed_action=action.proposed_action,status=action.status,rules_fired=action.rules_fired)

@app.get('/api/agent/audit', response_model=list[schemas.ActionOut])
async def audit(db: Session = Depends(get_db)):
    acts=db.query(models.Action).all()
    return [schemas.ActionOut(id=a.id,proposed_action=a.proposed_action,status=a.status,rules_fired=a.rules_fired) for a in acts]
