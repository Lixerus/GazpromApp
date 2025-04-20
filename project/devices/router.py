from fastapi import APIRouter, Depends, status, Response
from fastapi.responses import JSONResponse
from celery.result import AsyncResult
from datetime import datetime
from database import DeviceMeasurement, new_session
from tasks import calculate_stats_sql_grouped, calculate_stats_sql
from .schemas import MeasurementCreate
from sqlalchemy.orm import Session
from typing import Optional

router = APIRouter(
    prefix="/devices",
    tags=["devices"],
    responses={404: {"description": "Not found"}}
)

def get_db():
    db = new_session()
    try:
        yield db
    finally:
        db.close()

@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    summary="Создать новое измерение",
    response_description="Созданное измерение"
)
def create_measurement(
    measurement: MeasurementCreate,
    db: Session = Depends(get_db)
):
    db_measurement = DeviceMeasurement(**measurement.model_dump())
    db.add(db_measurement)
    db.commit()
    db.refresh(db_measurement)
    return Response(status_code=201)


@router.get(
    "/stats/all",
    status_code=status.HTTP_200_OK,
    summary="Получить статистику по всем устройствам за промежуток времени",
    response_description="Идентификатор асинхронной задачи"
        )
def get_device_stats(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
):
    task = calculate_stats_sql.delay(
        start_date=start_date,
        end_date=end_date
    )
    return {"task_id": task.id}

@router.get(
    "/stats/grouped",
    status_code=status.HTTP_200_OK,
    summary="Получить статистику по сгруппированным устройствам за промежуток времени",
    response_description="Идентификатор асинхронной задачи"
    )
def get_device_stats_grouped(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
):
    task = calculate_stats_sql_grouped.delay(
        start_date=start_date,
        end_date=end_date
    )
    return {"task_id": task.id}

@router.get(
    "/tasks/{task_id}",
    status_code=status.HTTP_200_OK,
    summary="Узнать статус и результат вызванной задачи",
    response_description="Статус и результат асинхронной задачи"
    )
def get_status(task_id):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return JSONResponse(result)