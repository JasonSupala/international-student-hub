from django.db import migrations, models
from django.utils.text import slugify


def populate_slugs(apps, schema_editor):
    ServiceEntry = apps.get_model("directory", "ServiceEntry")
    used = set()

    for entry in ServiceEntry.objects.order_by("id"):
        base_slug = slugify(entry.slug or entry.name) or "service-entry"
        slug = base_slug
        suffix = 2
        while slug in used or ServiceEntry.objects.filter(slug=slug).exclude(pk=entry.pk).exists():
            slug = f"{base_slug}-{suffix}"
            suffix += 1
        entry.slug = slug
        entry.save(update_fields=["slug"])
        used.add(slug)


class Migration(migrations.Migration):

    dependencies = [
        ("directory", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="serviceentry",
            name="slug",
            field=models.CharField(blank=True, max_length=220, null=True),
        ),
        migrations.AddField(
            model_name="serviceentry",
            name="detail_description",
            field=models.TextField(blank=True, default="", help_text="Long Markdown description shown on the detail page"),
        ),
        migrations.AlterField(
            model_name="serviceentry",
            name="description",
            field=models.TextField(help_text="Short summary shown on directory lists"),
        ),
        migrations.RunPython(populate_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="serviceentry",
            name="detail_description",
            field=models.TextField(blank=True, help_text="Long Markdown description shown on the detail page"),
        ),
        migrations.AlterField(
            model_name="serviceentry",
            name="slug",
            field=models.SlugField(blank=True, max_length=220, unique=True),
        ),
    ]
