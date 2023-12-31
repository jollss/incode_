"""empty message

Revision ID: 1073f8b7d6dd
Revises: 9d71a180a2e9
Create Date: 2022-05-12 17:54:17.954042

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '1073f8b7d6dd'
down_revision = '9d71a180a2e9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('checks',
    sa.Column('id', sa.String(length=255), nullable=False),
    sa.Column('cic', sa.String(length=255), nullable=True),
    sa.Column('citizen_id', sa.String(length=255), nullable=True),
    sa.Column('company_summary', sqlalchemy_utils.types.json.JSONType(), nullable=True),
    sa.Column('country', sa.String(length=255), nullable=True),
    sa.Column('creation_date', sa.DateTime(), nullable=True),
    sa.Column('date_of_birth', sa.Date(), nullable=True),
    sa.Column('document_recognition_id', sa.String(length=255), nullable=True),
    sa.Column('elector_key', sa.String(length=255), nullable=True),
    sa.Column('expedition_date', sa.DateTime(), nullable=True),
    sa.Column('issue_date', sa.DateTime(), nullable=True),
    sa.Column('first_name', sa.String(length=255), nullable=True),
    sa.Column('name_score', sa.Integer(), nullable=True),
    sa.Column('id_score', sa.Integer(), nullable=True),
    sa.Column('last_name', sa.String(length=255), nullable=True),
    sa.Column('ocr', sa.String(length=255), nullable=True),
    sa.Column('score', sa.Integer(), nullable=True),
    sa.Column('scores', sqlalchemy_utils.types.json.JSONType(), nullable=True),
    sa.Column('status', sa.String(length=255), nullable=True),
    sa.Column('statuses', sqlalchemy_utils.types.json.JSONType(), nullable=True),
    sa.Column('summary', sqlalchemy_utils.types.json.JSONType(), nullable=True),
    sa.Column('update_date', sa.DateTime(), nullable=True),
    sa.Column('vehicle_summary', sqlalchemy_utils.types.json.JSONType(), nullable=True),
    sa.Column('national_id', sa.String(length=255), nullable=True),
    sa.Column('owner_document_type', sa.String(length=255), nullable=True),
    sa.Column('type', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('digital_ids',
    sa.Column('id', sa.String(length=255), nullable=False),
    sa.Column('status', sa.String(length=255), nullable=True),
    sa.Column('creation_date', sa.DateTime(), nullable=True),
    sa.Column('update_date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('hook_logs',
    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False),
    sa.Column('event_type', sa.String(length=255), nullable=True),
    sa.Column('event_action', sa.String(length=255), nullable=True),
    sa.Column('object', sqlalchemy_utils.types.json.JSONType(), nullable=True),
    sa.Column('version', sa.Float(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('process_ids',
    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False),
    sa.Column('proccess_id', sa.String(length=255), nullable=True),
    sa.Column('account_id', sa.String(length=255), nullable=True),
    sa.Column('first_check_id', sa.String(length=255), nullable=True),
    sa.Column('last_check_id', sa.String(length=255), nullable=True),
    sa.Column('validation_id', sa.String(length=255), nullable=True),
    sa.Column('user_id', sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_process_ids_account_id'), 'process_ids', ['account_id'], unique=False)
    op.create_index(op.f('ix_process_ids_first_check_id'), 'process_ids', ['first_check_id'], unique=False)
    op.create_index(op.f('ix_process_ids_last_check_id'), 'process_ids', ['last_check_id'], unique=False)
    op.create_index(op.f('ix_process_ids_proccess_id'), 'process_ids', ['proccess_id'], unique=False)
    op.create_index(op.f('ix_process_ids_validation_id'), 'process_ids', ['validation_id'], unique=False)
    op.create_table('validations',
    sa.Column('id', sa.String(length=255), nullable=False),
    sa.Column('ip_address', sqlalchemy_utils.types.ip_address.IPAddressType(length=50), nullable=True),
    sa.Column('type', sa.String(length=255), nullable=True),
    sa.Column('validation_status', sa.String(length=255), nullable=True),
    sa.Column('creation_date', sa.DateTime(), nullable=True),
    sa.Column('declined_reason', sa.String(length=255), nullable=True),
    sa.Column('failure_reason', sa.String(length=255), nullable=True),
    sa.Column('attachment_status', sa.String(length=255), nullable=True),
    sa.Column('retry_of_id', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('validation_details',
    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False),
    sa.Column('validation_id', sa.String(length=255), nullable=True),
    sa.Column('country', sa.String(length=255), nullable=True),
    sa.Column('creation_date', sa.DateTime(), nullable=True),
    sa.Column('date_of_birth', sa.Date(), nullable=True),
    sa.Column('document_number', sa.String(length=255), nullable=True),
    sa.Column('document_type', sa.String(length=255), nullable=True),
    sa.Column('expiration_date', sa.DateTime(), nullable=True),
    sa.Column('gender', sa.String(length=255), nullable=True),
    sa.Column('issue_date', sa.DateTime(), nullable=True),
    sa.Column('last_name', sa.String(length=255), nullable=True),
    sa.Column('machine_readable', sa.String(length=255), nullable=True),
    sa.Column('municipality', sa.Integer(), nullable=True),
    sa.Column('municipality_name', sa.String(length=255), nullable=True),
    sa.Column('state', sa.Integer(), nullable=True),
    sa.Column('state_name', sa.String(length=255), nullable=True),
    sa.Column('locality', sa.Integer(), nullable=True),
    sa.Column('section', sa.Integer(), nullable=True),
    sa.Column('elector_key', sa.String(length=255), nullable=True),
    sa.Column('ocr', sa.String(length=255), nullable=True),
    sa.Column('cic', sa.String(length=255), nullable=True),
    sa.Column('citizen_id', sa.String(length=255), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('registration_date', sa.DateTime(), nullable=True),
    sa.Column('residence_address', sa.String(length=255), nullable=True),
    sa.Column('update_date', sa.DateTime(), nullable=True),
    sa.Column('front_url', sa.Text(), nullable=True),
    sa.Column('back_url', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['validation_id'], ['validations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('validation_documents',
    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False),
    sa.Column('validation_id', sa.String(length=255), nullable=True),
    sa.Column('validation_name', sa.String(length=255), nullable=True),
    sa.Column('result', sa.String(length=255), nullable=True),
    sa.Column('validation_type', sa.String(length=255), nullable=True),
    sa.Column('message', sa.String(length=255), nullable=True),
    sa.Column('manually_reviewed', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['validation_id'], ['validations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('results_ine', sa.Column('updated_at', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('results_ine', 'updated_at')
    op.drop_table('validation_documents')
    op.drop_table('validation_details')
    op.drop_table('validations')
    op.drop_index(op.f('ix_process_ids_validation_id'), table_name='process_ids')
    op.drop_index(op.f('ix_process_ids_proccess_id'), table_name='process_ids')
    op.drop_index(op.f('ix_process_ids_last_check_id'), table_name='process_ids')
    op.drop_index(op.f('ix_process_ids_first_check_id'), table_name='process_ids')
    op.drop_index(op.f('ix_process_ids_account_id'), table_name='process_ids')
    op.drop_table('process_ids')
    op.drop_table('hook_logs')
    op.drop_table('digital_ids')
    op.drop_table('checks')
    # ### end Alembic commands ###
