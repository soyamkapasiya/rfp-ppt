from celery import Celery


def create_celery(redis_url: str) -> Celery:
    app = Celery("rfp_worker", broker=redis_url, backend=redis_url)
    app.conf.task_serializer = "json"
    app.conf.result_serializer = "json"
    app.conf.accept_content = ["json"]
    return app
