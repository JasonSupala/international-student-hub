from django.db import migrations


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("directory", "0002_serviceentry_slug_detail_description"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            ALTER TABLE directory_serviceentry
                ADD COLUMN IF NOT EXISTS slug varchar(220);
            ALTER TABLE directory_serviceentry
                ADD COLUMN IF NOT EXISTS detail_description text;

            UPDATE directory_serviceentry
            SET slug = concat(
                trim(both '-' from lower(regexp_replace(coalesce(name, 'service-entry'), '[^a-zA-Z0-9]+', '-', 'g'))),
                '-',
                id
            )
            WHERE slug IS NULL OR slug = '';

            UPDATE directory_serviceentry
            SET detail_description = ''
            WHERE detail_description IS NULL;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
