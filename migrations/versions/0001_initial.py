"""initial schema"""
from alembic import op
import sqlalchemy as sa
revision='0001_initial'; down_revision=None
def upgrade():
    op.create_table('devices',sa.Column('id',sa.Integer,primary_key=True),sa.Column('device_id',sa.String(80),unique=True),sa.Column('device_type',sa.String(30)),sa.Column('last_seen',sa.DateTime(timezone=True)),sa.Column('status',sa.String(20)),sa.Column('metadata_json',sa.JSON))
    op.create_table('detection_events',sa.Column('id',sa.Integer,primary_key=True),sa.Column('timestamp',sa.DateTime(timezone=True)),sa.Column('detected',sa.Boolean),sa.Column('detection_class',sa.String(80)),sa.Column('confidence',sa.Float),sa.Column('image_path',sa.String(300)),sa.Column('sensor_readings',sa.JSON),sa.Column('capture_status',sa.String(30)),sa.Column('device_id',sa.String(80),sa.ForeignKey('devices.device_id')))
    op.create_table('repellent_events',sa.Column('id',sa.Integer,primary_key=True),sa.Column('detection_id',sa.Integer,sa.ForeignKey('detection_events.id')),sa.Column('activation_time',sa.DateTime(timezone=True)),sa.Column('duration_s',sa.Integer),sa.Column('frequencies',sa.JSON),sa.Column('outcome',sa.String(40)),sa.Column('completed_at',sa.DateTime(timezone=True)),sa.Column('command_claimed_at',sa.DateTime(timezone=True)))
    op.create_table('system_configuration',sa.Column('id',sa.Integer,primary_key=True),sa.Column('key',sa.String(80),unique=True),sa.Column('value',sa.Text))
def downgrade():
    for t in ('system_configuration','repellent_events','detection_events','devices'): op.drop_table(t)
