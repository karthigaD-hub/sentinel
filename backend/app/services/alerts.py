from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Alert
from app.repositories.alerts import AlertRepository

class AlertService:
    @staticmethod
    async def update_status(session: AsyncSession, alert_id: UUID, status: str) -> Alert:
        alert = await AlertRepository(session).get(alert_id)
        if not alert:
            raise LookupError("Alert not found")
        alert.status = status
        if status == "resolved":
            alert.resolved_at = datetime.now(timezone.utc)
        await session.commit()
        await session.refresh(alert)
        return alert
