# coding=utf-8
import enum
from datetime import datetime, timezone
from functools import partial
from uuid import uuid4

from sqlalchemy import (
    ARRAY,
    Column,
    DateTime,
    Enum,
    Integer,
    String,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import relationship

from drealcorsereports.models.meta import Base

SCHEMA = "reports"


class ReportModel(Base):
    __tablename__ = "report_model"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False, unique=True)
    layer_id = Column(String, nullable=False)
    created_by = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=partial(datetime.now, timezone.utc),
        nullable=False,
    )
    updated_by = Column(String, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=partial(datetime.now, timezone.utc),
        nullable=False,
    )
    custom_fields = relationship(
        "ReportModelCustomField",
        order_by="ReportModelCustomField.index",
        collection_class=ordering_list("index"),
    )


class FieldTypeEnum(enum.Enum):
    string = 1
    boolean = 2
    number = 3
    date = 4
    file = 6


class ReportModelCustomField(Base):
    __tablename__ = "report_model_custom_field"
    __table_args__ = (
        UniqueConstraint("report_model_id", "index", name="report_model_index_uc"),
        UniqueConstraint("report_model_id", "name", name="report_model_name_uc"),
        {"schema": SCHEMA},
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    report_model_id = Column(UUID(as_uuid=True), ForeignKey(ReportModel.id))
    index = Column(Integer)
    name = Column(String, nullable=False)
    type = Column(Enum(FieldTypeEnum), nullable=False)
    enum = Column(ARRAY(String))


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
    created_by = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=partial(datetime.now, timezone.utc),
        nullable=False,
    )
    # Since user comes from HTTP header (handled by georchestra security-proxy)
    # we don't have any User class in this app.
    updated_by = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
