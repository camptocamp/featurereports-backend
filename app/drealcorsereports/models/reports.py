# coding=utf-8
from sqlalchemy import Column, DateTime, String, ForeignKey
from drealcorsereports.models.meta import Base
from sqlalchemy.dialects.postgresql import UUID, JSON
from uuid import uuid4
from sqlalchemy.orm import relationship
from datetime import datetime

SCHEMA = "reports"


class ReportModel(Base):
    __tablename__ = "report_model"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False, unique=True)
    # postgres offer JSON and JSONB. Binary is more powerful for querying but
    # since we always want all the JSON and not some part. JSON is more
    # convinent (and insert is faster).
    # Schema store the json schema that will be interpret by the frontend.
    custom_field_schema = Column(JSON, nullable=False)
    layer_id = Column(String, nullable=False)
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)
    updated_by = Column(String)
    updated_at = Column(DateTime(timezone=True))


class Report(Base):
    __tablename__ = "report"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    feature_id = Column(String, nullable=False)
    report_model_id = Column(
        UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.report_model.id"), nullable=False
    )
    report_model = relationship("ReportModel", backref="report")
    # response of the form. based on the template json schema
    custome_field_values = Column(JSON, nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    # Since user comes from HTTP header (handled by georchestra security-proxy)
    # we don't have any User class in this app.
    updated_by = Column(String, nullable=False)
