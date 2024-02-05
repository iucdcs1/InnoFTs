from apscheduler.schedulers.asyncio import AsyncIOScheduler


async def setup_scheduler():
    scheduler = AsyncIOScheduler()

    return scheduler
