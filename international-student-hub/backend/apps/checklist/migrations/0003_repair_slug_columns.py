from django.db import migrations


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("checklist", "0002_checklistitem_slug_detail_description"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            ALTER TABLE checklist_checklistitem
                ADD COLUMN IF NOT EXISTS slug varchar(220);
            ALTER TABLE checklist_checklistitem
                ADD COLUMN IF NOT EXISTS detail_description text;

            UPDATE checklist_checklistitem
            SET slug = concat(
                trim(both '-' from lower(regexp_replace(coalesce(title, 'checklist-item'), '[^a-zA-Z0-9]+', '-', 'g'))),
                '-',
                id
            )
            WHERE slug IS NULL OR slug = '';

            UPDATE checklist_checklistitem
            SET detail_description = ''
            WHERE detail_description IS NULL;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
