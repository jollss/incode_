from app.tasks import celery
from app import create_app
from app.tasks.celery_utils import init_celery
app = create_app()
init_celery(celery, app)