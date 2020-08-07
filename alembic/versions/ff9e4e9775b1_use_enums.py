"""use enums

Revision ID: ff9e4e9775b1
Revises: d5722b05d753
Create Date: 2020-08-06 18:38:52.835127

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "ff9e4e9775b1"
down_revision = "d5722b05d753"
branch_labels = None
depends_on = None


def upgrade():
    # moderations
    op.execute("UPDATE moderations SET type='BAN' WHERE moderations.type = 'baneado'")
    op.execute(
        "UPDATE moderations SET type='WARN' WHERE moderations.type = 'advertido'"
    )
    op.execute(
        "UPDATE moderations SET type='KICK' WHERE moderations.type = 'expulsado'"
    )
    op.execute(
        "UPDATE moderations SET type='MUTE' WHERE moderations.type = 'silenciado'"
    )

    e1 = sa.Enum("BAN", "WARN", "KICK", "MUTE", name="moderationtype")
    e1.create(op.get_bind())

    op.execute(
        "ALTER TABLE moderations ALTER COLUMN type TYPE moderationtype USING type::moderationtype"
    )

    # settings
    op.execute("UPDATE settings SET name='DEBUG' WHERE settings.name = 'debug'")
    op.execute("UPDATE settings SET name='PREFIX' WHERE settings.name = 'prefix'")
    op.execute(
        "UPDATE settings SET name='RULES_CHANNEL' WHERE settings.name = 'rules_channel'"
    )
    op.execute(
        "UPDATE settings SET name='MODERATION_CHANNEL' WHERE settings.name = 'moderation_logs_channel'"
    )

    e2 = sa.Enum(
        "DEBUG",
        "PREFIX",
        "RULES_CHANNEL",
        "MODERATION_CHANNEL",
        "MIN_MOD_ROLE",
        "MUTED_ROLE",
        "WARNING_ROLE",
        name="guildsetting",
    )
    e2.create(op.get_bind())

    op.execute(
        "ALTER TABLE settings ALTER COLUMN name TYPE guildsetting USING name::guildsetting"
    )


def downgrade():
    # moderations
    op.execute("UPDATE moderations SET type='baneado' WHERE moderations.type = 'BAN'")
    op.execute(
        "UPDATE moderations SET type='advertido' WHERE moderations.type = 'WARN'"
    )
    op.execute(
        "UPDATE moderations SET type='expulsado' WHERE moderations.type = 'KICK'"
    )
    op.execute(
        "UPDATE moderations SET type='silenciado' WHERE moderations.type = 'MUTE'"
    )

    op.execute("ALTER TABLE moderations ALTER COLUMN type TYPE varchar")

    # settings
    op.execute("UPDATE settings SET name='debug' WHERE settings.name = 'DEBUG'")
    op.execute("UPDATE settings SET name='prefix' WHERE settings.name = 'PREFIX'")
    op.execute(
        "UPDATE settings SET name='rules_channel' WHERE settings.name = 'RULES_CHANNEL'"
    )
    op.execute(
        "UPDATE settings SET name='moderation_logs_channel' WHERE settings.name = 'MODERATION_LOGS'"
    )

    op.execute("ALTER TABLE settings ALTER COLUMN name TYPE varchar(50)")
