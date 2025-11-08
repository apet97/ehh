
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from typing import Dict, Any
from .integrations.base import get_integration

scheduler: AsyncIOScheduler | None = None

async def _job(integration: str, operation: str, params: Dict[str, Any]):
    integ = get_integration(integration)
    await integ.execute(operation, params)

def start_scheduler() -> AsyncIOScheduler:
    global scheduler
    if scheduler is None:
        scheduler = AsyncIOScheduler()
        scheduler.start()
    return scheduler

def schedule_action(integration: str, operation: str, params: Dict[str, Any], cron: Dict[str, str]):
    s = start_scheduler()
    trigger = CronTrigger(**{k: v for k, v in cron.items() if v is not None})
    s.add_job(_job, trigger, kwargs=dict(integration=integration, operation=operation, params=params))
