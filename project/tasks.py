from celery import Celery
from sqlalchemy import func
from statistics import median
from database import new_session, DeviceMeasurement
from sqlalchemy.exc import DatabaseError
from datetime import datetime
import os

celery = Celery("tasks")
celery.conf.update(
    broker_url=os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0"),
    result_backend=os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/0"),
    worker_pool='gevent',
    worker_concurrency=6,
    imports=['tasks'] 
)
@celery.task(name='tasks.stats_sql', bind=True, max_retries=3, default_retry_delay=3)
def calculate_stats_sql(self, start_date: datetime | None = None, end_date: datetime | None = None):
    session = new_session()
    try:
        query = session.query(
            func.min(DeviceMeasurement.x).label('x_min'),
            func.max(DeviceMeasurement.x).label('x_max'),
            func.count(DeviceMeasurement.x).label('x_count'),
            func.sum(DeviceMeasurement.x).label('x_sum'),
            func.min(DeviceMeasurement.y).label('y_min'),
            func.max(DeviceMeasurement.y).label('y_max'),
            func.count(DeviceMeasurement.y).label('y_count'),
            func.sum(DeviceMeasurement.y).label('y_sum'),
            func.min(DeviceMeasurement.z).label('z_min'),
            func.max(DeviceMeasurement.z).label('z_max'),
            func.count(DeviceMeasurement.z).label('z_count'),
            func.sum(DeviceMeasurement.z).label('z_sum'),
        )
        if start_date and end_date:
            query = query.filter(DeviceMeasurement.created_at.between(start_date, end_date))
        elif start_date:
            query = query.filter(DeviceMeasurement.created_at >= start_date)
        elif end_date:
            query = query.filter(DeviceMeasurement.created_at <= end_date)
        stats = query.first()
        
        if not stats:
            return {}

        def get_median(column):
            median_query = session.query(column)
            if start_date and end_date:
                median_query = median_query.filter(DeviceMeasurement.created_at.between(start_date, end_date))
            elif start_date:
                median_query = median_query.filter(DeviceMeasurement.created_at >= start_date)
            elif end_date:
                median_query = median_query.filter(DeviceMeasurement.created_at <= end_date)
            values = median_query.order_by(column).all()
            values = [v[0] for v in values]
            return median(values) if values else 0

        return {
            "x": {
                "min": stats.x_min,
                "max": stats.x_max,
                "count": stats.x_count,
                "sum": stats.x_sum,
                "median": get_median(DeviceMeasurement.x),
            },
            "y": {
                "min": stats.y_min,
                "max": stats.y_max,
                "count": stats.y_count,
                "sum": stats.y_sum,
                "median": get_median(DeviceMeasurement.y),
            },
            "z": {
                "min": stats.z_min,
                "max": stats.z_max,
                "count": stats.z_count,
                "sum": stats.z_sum,
                "median": get_median(DeviceMeasurement.z),
            }
        }
    except DatabaseError as exc:
        self.retry(exc=exc)
    finally:
        session.close()

@celery.task(name='tasks.stats_sql_grouped', bind=True, max_retries=3, default_retry_delay=3)
def calculate_stats_sql_grouped(
    self,
    start_date: datetime | None = None,
    end_date: datetime | None = None
):
    session = new_session()
    try:
        query = session.query(
            DeviceMeasurement.device_id,
            func.min(DeviceMeasurement.x).label('x_min'),
            func.max(DeviceMeasurement.x).label('x_max'),
            func.count(DeviceMeasurement.x).label('x_count'),
            func.sum(DeviceMeasurement.x).label('x_sum'),
            func.min(DeviceMeasurement.y).label('y_min'),
            func.max(DeviceMeasurement.y).label('y_max'),
            func.count(DeviceMeasurement.y).label('y_count'),
            func.sum(DeviceMeasurement.y).label('y_sum'),
            func.min(DeviceMeasurement.z).label('z_min'),
            func.max(DeviceMeasurement.z).label('z_max'),
            func.count(DeviceMeasurement.z).label('z_count'),
            func.sum(DeviceMeasurement.z).label('z_sum'),
        ).group_by(DeviceMeasurement.device_id)

        if start_date and end_date:
            query = query.filter(DeviceMeasurement.created_at.between(start_date, end_date))
        elif start_date:
            query = query.filter(DeviceMeasurement.created_at >= start_date)
        elif end_date:
            query = query.filter(DeviceMeasurement.created_at <= end_date)
        grouped_stats = query.all()

        result = []
        for stat in grouped_stats:
            device_id = stat.device_id
            
            def get_median(axis):
                q = session.query(axis).filter(DeviceMeasurement.device_id == device_id)
                if start_date and end_date:
                    q = q.filter(DeviceMeasurement.created_at.between(start_date, end_date))
                elif start_date:
                    q = q.filter(DeviceMeasurement.created_at >= start_date)
                elif end_date:
                    q = q.filter(DeviceMeasurement.created_at <= end_date)
                values = [v[0] for v in q.order_by(axis).all()]
                return median(values) if values else 0
            
            result.append({
                'device_id': device_id,
                'x': {
                    'min': stat.x_min,
                    'max': stat.x_max,
                    'count': stat.x_count,
                    'sum': stat.x_sum,
                    'median': get_median(DeviceMeasurement.x),
                },
                'y': {
                    'min': stat.y_min,
                    'max': stat.y_max,
                    'count': stat.y_count,
                    'sum': stat.y_sum,
                    'median': get_median(DeviceMeasurement.y),
                },
                'z': {
                    'min': stat.z_min,
                    'max': stat.z_max,
                    'count': stat.z_count,
                    'sum': stat.z_sum,
                    'median': get_median(DeviceMeasurement.z),
                }
            })
        return result

    except DatabaseError as exc:
        self.retry(exc=exc)
    finally:
        session.close()