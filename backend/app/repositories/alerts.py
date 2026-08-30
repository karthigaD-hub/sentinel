from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Alert

class AlertRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, alert_id: UUID) -> Alert | None:
        return await self.session.scalar(select(Alert).where(Alert.id == alert_id))

    async def list(self, limit: int = 50, offset: int = 0) -> list[Alert]:
        return list((await self.session.execute(select(Alert).order_by(Alert.created_at.desc()).offset(offset).limit(limit))).scalars().all())
