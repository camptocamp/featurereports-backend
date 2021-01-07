# coding=utf-8
from sqlalchemy import Column, DateTime, String, ForeignKey
from drealcorsereports.models.meta import Base
from sqlalchemy.dialects.postgresql import UUID, JSON
from uuid import uuid4
from sqlalchemy.orm import relationship

SCHEMA = "reports"


class Template(Base):
    __tablename__ = "template"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    # postgres offer JSON and JSONB. Binary is more powerful for querying but
    # since we always want all the JSON and not some part. JSON is more
    # convinent (and insert is faster).
    # Schema store the json schema that will be interpret by the frontend.
    schema = Column(JSON, nullable=False)
    layer_id = Column(String, nullable=False)


class Report(Base):
    __tablename__ = "report"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    feature_id = Column(String, nullable=False)
    template_id = Column(
        UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.template.id"), nullable=False
    )
    template = relationship("Template", backref="report")
    # response of the form. based on the template json schema
    response = Column(JSON, nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    # Since user comes from HTTP header (handled by georchestra security-proxy)
    # we don't have any User class in this app.
    updated_by = Column(String, nullable=False)
