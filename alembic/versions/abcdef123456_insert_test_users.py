"""Insert two test users into the users table

Revision ID: abcdef123456
Revises: <previous_revision>  # Replace with the previous revision ID
Create Date: 2025-03-05 12:05:00
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = 'abcdef123456'
down_revision = '5008a63749f3'
branch_labels = None
depends_on = None

def upgrade():
    op.execute(
        """
        INSERT INTO users (username, email, password, first_name, last_name, is_active, created_at, updated_at)
        VALUES
        ('John', 'john@example.com', '$2b$12$E9t0KN8EcqN4AdES9wQn5uP3s3EvfwivTc92bj94QSHqrSfqSE25G', 'John', 'Doe', 1, NOW(), NOW()),
        ('Jane', 'jane@example.com', '$2b$12$E9t0KN8EcqN4AdES9wQn5uP3s3EvfwivTc92bj94QSHqrSfqSE25G', 'Jane', 'Doe', 1, NOW(), NOW());
        """
    )


def downgrade():
    op.execute(
        """
        DELETE FROM users
        WHERE email IN ('john@example.com', 'jane@example.com');
        """
    )
