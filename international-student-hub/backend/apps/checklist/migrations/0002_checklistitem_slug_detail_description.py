from django.db import migrations, models
from django.utils.text import slugify


def populate_slugs(apps, schema_editor):
    ChecklistItem = apps.get_model("checklist", "ChecklistItem")
    used = set()

    for item in ChecklistItem.objects.order_by("id"):
        base_slug = slugify(item.slug or item.title) or "checklist-item"
        slug = base_slug
        suffix = 2
        while slug in used or ChecklistItem.objects.filter(slug=slug).exclude(pk=item.pk).exists():
            slug = f"{base_slug}-{suffix}"
            suffix += 1
        item.slug = slug
        item.save(update_fields=["slug"])
        used.add(slug)


class Migration(migrations.Migration):

    dependencies = [
        ("checklist", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="checklistitem",
            name="slug",
            field=models.CharField(blank=True, max_length=220, null=True),
        ),
        migrations.AddField(
            model_name="checklistitem",
            name="detail_description",
            field=models.TextField(blank=True, default="", help_text="Long Markdown instructions shown on the detail page"),
        ),
        migrations.AlterField(
            model_name="checklistitem",
            name="description",
            field=models.TextField(help_text="Short summary shown on checklist lists"),
        ),
        migrations.RunPython(populate_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="checklistitem",
            name="detail_description",
            field=models.TextField(blank=True, help_text="Long Markdown instructions shown on the detail page"),
        ),
        migrations.AlterField(
            model_name="checklistitem",
            name="slug",
            field=models.SlugField(blank=True, max_length=220, unique=True),
        ),
    ]
