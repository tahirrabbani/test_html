from .. import models
from sqlalchemy.orm import Session
from . import rules


def suggest_actions(db: Session):
    all_actions=[]
    for rule in rules.RULES:
        all_actions.extend(rule(db))
    for action in all_actions:
        db.add(action)
    db.commit()
    return all_actions


def execute_action(db: Session, action_id: str):
    action=db.query(models.Action).get(action_id)
    if action:
        action.status='Executed'
        db.commit()
    return action
