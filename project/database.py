from __future__ import annotations
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import(
    DeclarativeBase,
    Mapped,
    mapped_column,
)
from datetime import datetime
from pathlib import Path
import os

# sqlite db_url for basic local developement
db_path = Path(__file__).parent / "db_data/tasks.db"
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite+aiosqlite:///{db_path.absolute()}")
engine = create_engine(DATABASE_URL, echo=False)
new_session = sessionmaker(engine, expire_on_commit=False, autoflush=False)


class Model(DeclarativeBase):
    pass

class DeviceMeasurement(Model):
    __tablename__ = 'device_measurements'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    device_id: Mapped[int] = mapped_column(index=True, nullable=False)
    x: Mapped[float]
    y: Mapped[float]
    z: Mapped[float]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, index=True)

    def __repr__(self) -> str:
        return (f"DeviceMeasurement(id={self.id}, device_id={self.device_id}, "
                f"x={self.x}, y={self.y}, z={self.z})")

def create_tables():
    Model.metadata.create_all(bind=engine)