"""create initial booking schema"""
from alembic import op
import sqlalchemy as sa
revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("parents", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(120), nullable=False), sa.Column("email", sa.String(320), nullable=False, unique=True))
    op.create_table("students", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("parent_id", sa.Integer(), sa.ForeignKey("parents.id"), nullable=False), sa.Column("name", sa.String(120), nullable=False))
    op.create_table("trial_classes", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("title", sa.String(160), nullable=False), sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False), sa.Column("capacity", sa.Integer(), nullable=False, server_default="4"), sa.CheckConstraint("capacity > 0", name="ck_trial_classes_capacity_positive"))
    op.create_table("bookings", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("student_id", sa.Integer(), sa.ForeignKey("students.id"), nullable=False), sa.Column("trial_class_id", sa.Integer(), sa.ForeignKey("trial_classes.id"), nullable=False), sa.Column("status", sa.String(32), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("uq_confirmed_student_trial_class", "bookings", ["student_id", "trial_class_id"], unique=True, postgresql_where=sa.text("status = 'confirmed'"))
    op.create_table("payment_attempts", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("booking_id", sa.Integer(), sa.ForeignKey("bookings.id"), nullable=False), sa.Column("status", sa.String(16), nullable=False), sa.Column("provider_reference", sa.String(255)), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))

def downgrade():
    op.drop_table("payment_attempts")
    op.drop_index("uq_confirmed_student_trial_class", table_name="bookings")
    op.drop_table("bookings")
    op.drop_table("trial_classes")
    op.drop_table("students")
    op.drop_table("parents")
