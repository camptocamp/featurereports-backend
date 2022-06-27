"""Remove layername in feature_id in existing TJS views

Revision ID: 4fb63ccdaa02
Revises: 77e41b5459e2
Create Date: 2022-06-27 07:39:49.496091

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4fb63ccdaa02"
down_revision = "77e41b5459e2"
branch_labels = None
depends_on = None

schema_name = "reports"
table_name = "report"


def upgrade():
    conn = op.get_bind()

    models = conn.execute(sa.text("SELECT id, name FROM reports.report_model;"))
    for (model_id, model_name) in models.fetchall():
        view_name = f"{schema_name}.v_tjs_view_{model_name}"
        # print(f"{model_name} => {view_name}")
        feature_id_pattern = r".*\.(.*)"

        columns = conn.execute(
            sa.text(
                f"""
SELECT name
FROM reports.report_model_custom_field
WHERE report_model_id = '{model_id}'
ORDER BY index;
                """
            )
        )

        view_columns = ",\n".join(
            [
                f"        custom_field_values->>'{column_name}' as {column_name}"
                for (column_name,) in columns.fetchall()
            ]
        )

        conn.execute(
            sa.text(
                f"""
DROP VIEW IF EXISTS {view_name};
CREATE VIEW {view_name} AS
    SELECT
        substring(feature_id from '{feature_id_pattern}') AS feature_id,
{view_columns}
    FROM {schema_name}.{table_name};
                """
            )
        )


def downgrade():
    pass
