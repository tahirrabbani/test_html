from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class SiteKPI(BaseModel):
    uptime_pct: float
    utilization_pct: float
    mttr_hours: float
    fcr_pct: float
    revenue_month: float
    refund_rate_pct: float

class SiteOut(BaseModel):
    id: int
    name: str
    country: str
    lat: float
    lon: float
    site_type: Optional[str]
    owner_type: Optional[str]
    sla_tier: Optional[str]
    grid_kw: Optional[float]
    kpis: SiteKPI

class SummaryOut(BaseModel):
    uptime_pct: float
    utilization_pct: float
    mttr_hours: float
    fcr_pct: float
    refund_rate_pct: float
    revenue_eur: float

class IncidentOut(BaseModel):
    id: int
    site_id: int
    category: str
    severity: str
    status: str
    created_ts: datetime
    closed_ts: Optional[datetime]

class ActionOut(BaseModel):
    id: str
    proposed_action: str
    status: str
    rules_fired: str
