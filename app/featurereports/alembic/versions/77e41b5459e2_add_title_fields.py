"""Add title fields

Revision ID: 77e41b5459e2
Revises: 066134a29f29
Create Date: 2021-05-09 07:36:46.529366

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "77e41b5459e2"
down_revision = "066134a29f29"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "report_model",
        sa.Column("title", sa.String(), nullable=False),
        schema="reports",
    )
    op.add_column(
        "report_model_custom_field",
        sa.Column("title", sa.String(), nullable=False),
        schema="reports",
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("report_model_custom_field", "title", schema="reports")
    op.drop_column("report_model", "title", schema="reports")
    # ### end Alembic commands ###