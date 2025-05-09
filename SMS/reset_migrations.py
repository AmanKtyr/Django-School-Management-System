import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "school_app.settings")
django.setup()

from django.db import connection

# SQL to reset Django migrations
reset_migrations_sql = """
DELETE FROM django_migrations;
"""

# Execute the SQL
with connection.cursor() as cursor:
    cursor.execute(reset_migrations_sql)
    print("Migration history has been reset")
