"""
Custom migration to add uuid, slug, and access_password to Story.
Uses a 3-step approach for the UUID field to handle existing rows:
1. Add the field as nullable (no unique constraint)
2. Populate each row with a unique uuid4 value
3. Make the field non-nullable + unique
"""

import uuid
from django.db import migrations, models
from django.utils.text import slugify


def populate_uuid_and_slug(apps, schema_editor):
    """Generate unique UUIDs and slugs for all existing Story rows."""
    Story = apps.get_model('engine', 'Story')
    for story in Story.objects.all():
        story.story_uuid = uuid.uuid4()
        base_slug = slugify(story.title) or 'untitled'
        slug = base_slug
        counter = 1
        while Story.objects.filter(slug=slug).exclude(pk=story.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        story.slug = slug
        story.save(update_fields=['story_uuid', 'slug'])


class Migration(migrations.Migration):

    dependencies = [
        ('engine', '0002_node_correct_answer_alter_node_node_type'),
    ]

    operations = [
        # Step 1: Add fields as nullable / non-unique
        migrations.AddField(
            model_name='story',
            name='story_uuid',
            field=models.UUIDField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='story',
            name='slug',
            field=models.SlugField(max_length=280, blank=True, default=''),
        ),
        migrations.AddField(
            model_name='story',
            name='access_password',
            field=models.CharField(
                max_length=128, blank=True, null=True,
                help_text='If set, players must enter this password before playing.',
            ),
        ),

        # Step 2: Populate existing rows with unique values
        migrations.RunPython(populate_uuid_and_slug, migrations.RunPython.noop),

        # Step 3: Alter to final schema (non-nullable, unique, with default)
        migrations.AlterField(
            model_name='story',
            name='story_uuid',
            field=models.UUIDField(
                default=uuid.uuid4,
                editable=False,
                unique=True,
                help_text='Unique identifier for shareable play URLs.',
            ),
        ),
    ]
