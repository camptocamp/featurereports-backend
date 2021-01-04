# coding=utf-8
from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
)
from drealcorsereports.models.meta import Base

SCHEMA = "reports"


class Report(Base):
    __tablename__ = "report"
    __table_args__ = {"schema": SCHEMA}

    id = Column(Integer, primary_key=True)
    feature_id = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    updated_by = Column(String, nullable=False)
