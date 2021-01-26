"""First revision

Revision ID: 066134a29f29
Revises: 
Create Date: 2021-01-26 12:19:54.933864

"""
from alembic import op
import sqlalchemy as sa
import geoalchemy2
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '066134a29f29'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('report_model',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('layer_id', sa.String(), nullable=False),
    sa.Column('custom_field_schema', postgresql.JSON(astext_type=sa.Text()), nullable=False),
    sa.Column('created_by', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_by', sa.String(), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_report_model')),
    sa.UniqueConstraint('name', name=op.f('uq_report_model_name')),
    schema='reports'
    )
    op.create_table('report',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('feature_id', sa.String(), nullable=False),
    sa.Column('report_model_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('custome_field_values', postgresql.JSON(astext_type=sa.Text()), nullable=False),
    sa.Column('created_by', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_by', sa.String(), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['report_model_id'], ['reports.report_model.id'], name=op.f('fk_report_report_model_id_report_model')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_report')),
    schema='reports'
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('report', schema='reports')
    op.drop_table('report_model', schema='reports')
    # ### end Alembic commands ###