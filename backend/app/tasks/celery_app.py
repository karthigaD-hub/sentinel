from celery import Celery
from app.core.config import settings

celery_app = Celery("qsentinel", broker=settings.celery_broker_url, backend=settings.celery_result_backend)
celery_app.conf.update(task_serializer="json", result_serializer="json", accept_content=["json"], timezone="UTC", enable_utc=True)

@celery_app.task(name="dataset_preprocessing")
def dataset_preprocessing(path: str) -> dict[str, str]:
    raise RuntimeError(f"Dataset preprocessing requires a configured dataset: {path}")

@celery_app.task(name="model_training")
def model_training(dataset_id: str) -> dict[str, str]:
    raise RuntimeError(f"Model training requires a configured dataset: {dataset_id}")

@celery_app.task(name="rag_ingestion")
def rag_ingestion(source: str) -> dict[str, str]:
    raise RuntimeError(f"RAG ingestion requires a configured source: {source}")

@celery_app.task(name="report_generation")
def report_generation(report_id: str) -> dict[str, str]:
    raise RuntimeError(f"Report generation requires configured report data: {report_id}")
