from locust import HttpUser, task, between
from datetime import datetime, timedelta, timezone
import random

class ApiUser(HttpUser):
    wait_time = between(1, 3)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_ids = []
    
    @task(3)
    def post_measurement(self):
        data = {
            "device_id": random.randint(1, 100),
            "x": random.uniform(-100, 100),
            "y": random.uniform(-100, 100),
            "z": random.uniform(-100, 100),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        with self.client.post(
            "/devices/upload",
            json=data,
            catch_response=True
        ) as response:
            if response.status_code != 201:
                response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def get_stats_all(self):
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(hours=random.randint(1, 30))
        with self.client.get(
            "/devices/stats/all",
            params={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            catch_response=True
        ) as response:
            if response.status_code == 200:
                self.task_ids.append(response.json()["task_id"])
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def get_stats_grouped(self):
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=random.randint(1, 30))
        with self.client.get(
            "/devices/stats/grouped",
            params={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            catch_response=True
        ) as response:
            if response.status_code == 200:
                self.task_ids.append(response.json()["task_id"])
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(3)
    def check_task_status(self):
        if self.task_ids:
            task_id = random.choice(self.task_ids)
            with self.client.get(
                f"/devices/tasks/{task_id}",
                catch_response=True
            ) as response:
                if response.status_code != 200:
                    response.failure(f"Status code: {response.status_code}")
                elif response.json()["task_status"] != "PENDING":
                    self.task_ids.remove(task_id)