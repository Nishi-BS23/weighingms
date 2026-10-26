"""Alembic environment: migrations run on the connection handed over by `db.migrate`."""

from alembic import context

connection = context.config.attributes["connection"]
context.configure(connection=connection, render_as_batch=True)

with context.begin_transaction():
    context.run_migrations()
