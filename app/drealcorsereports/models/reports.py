# coding=utf-8
import enum
from datetime import datetime, timezone
from functools import partial
from uuid import uuid4

import zope
from sqlalchemy import (
    ARRAY,
    Boolean,
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
from sqlalchemy.sql.expression import text

from drealcorsereports.models.meta import Base

SCHEMA = "reports"


class ReportModel(Base):
    __tablename__ = "report_model"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False, unique=True)
    title = Column(String, nullable=False)
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

    def tjs_view_name(self):
        schema_name = ReportModel.__table_args__["schema"]
        return f"{schema_name}.v_tjs_view_{self.name}"

    def create_tjs_view(self, dbsession):
        schema_name = Report.__table_args__["schema"]
        table_name = Report.__tablename__
        view_columns = ",\n".join(
            [
                f"        custom_field_values->>'{f.name}' as {f.name}"
                for f in self.custom_fields
            ]
        )
        dbsession.execute(
            text(
                f"""CREATE OR REPLACE VIEW {self.tjs_view_name()} AS
    SELECT
        feature_id,
{view_columns}
    FROM {schema_name}.{table_name};
"""
            )
        )
        # mark the session as dirty, if not transaction manager will rollback the transaction.
        # ¯\_(ツ)_/¯
        zope.sqlalchemy.mark_changed(dbsession)


class FieldTypeEnum(enum.Enum):
    boolean = "boolean"
    date = "date"
    enum = "enum"
    file = "file"
    number = "number"
    string = "string"


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
    title = Column(String, nullable=False)
    type = Column(Enum(FieldTypeEnum), nullable=False)
    enum = Column(ARRAY(String))
    required = Column(Boolean, default=False, nullable=False)


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
    custom_field_values = Column(JSON, nullable=False)
    created_by = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=partial(datetime.now, timezone.utc),
        nullable=False,
    )
    # Since user comes from HTTP header (handled by georchestra security-proxy)
    # we don't have any User class in this app.
    updated_by = Column(String, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=partial(datetime.now, timezone.utc),
        nullable=False,
    )
