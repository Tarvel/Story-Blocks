"""
engine/models.py

Core data models for the StoryBoard interactive storytelling platform.
"""

import uuid
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify


class Story(models.Model):
    """
    Represents a complete interactive story/narrative project.
    Each story contains multiple Nodes connected by Choices.
    """
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='stories',
    )
    is_published = models.BooleanField(default=False)
    is_template = models.BooleanField(
        default=False,
        help_text='If True, other users can clone this story into their own projects.',
    )

    # Unique identifiers for shareable URLs
    story_uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text='Unique identifier for shareable play URLs.',
    )
    slug = models.SlugField(
        max_length=280,
        blank=True,
        help_text='URL-friendly version of the title (auto-generated).',
    )

    # Private game access
    access_password = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        help_text='If set, players must enter this password before playing.',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name_plural = 'stories'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Auto-populate slug from title on save."""
        if not self.slug or self._title_changed():
            base_slug = slugify(self.title) or 'untitled'
            slug = base_slug
            counter = 1
            # Handle slug collisions
            while Story.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def _title_changed(self):
        """Check if title changed since last save."""
        if not self.pk:
            return True
        try:
            old = Story.objects.get(pk=self.pk)
            return old.title != self.title
        except Story.DoesNotExist:
            return True

    def get_absolute_url(self):
        return reverse('engine:story_canvas', kwargs={'story_id': self.pk})

    def get_play_url(self):
        """Return the shareable play URL using the slug."""
        return reverse('engine:play_story', kwargs={
            'slug': self.slug,
        })

    def get_start_node(self):
        """Return the designated start node, or fallback to the first node."""
        start = self.nodes.filter(node_type='start').first()
        if start:
            return start
        # Fallback: use the first node created (e.g. for stories without
        # an explicit start node set)
        return self.nodes.order_by('created_at').first()


class Node(models.Model):
    """
    Represents a single passage/event/scene in a story.
    Positioned on a visual canvas using x/y coordinates.
    """
    NODE_TYPES = [
        ('start', 'Start'),
        ('passage', 'Passage'),
        ('riddle', 'Riddle'),
        ('death', 'Death'),
        ('ending', 'Ending'),
        ('checkpoint', 'Checkpoint'),
    ]

    story = models.ForeignKey(
        Story,
        on_delete=models.CASCADE,
        related_name='nodes',
    )
    title = models.CharField(max_length=255, default='Untitled Node')
    content = models.TextField(blank=True, default='')
    node_type = models.CharField(
        max_length=20,
        choices=NODE_TYPES,
        default='passage',
    )
    # Canvas coordinates for the visual editor
    x = models.FloatField(default=100.0)
    y = models.FloatField(default=100.0)
    # Riddle answer (only used when node_type='riddle')
    correct_answer = models.CharField(
        max_length=500,
        blank=True,
        default='',
        help_text='The answer the player must type (case-insensitive). Only used for riddle nodes.',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"[{self.get_node_type_display()}] {self.title}"

    def get_outgoing_choices(self):
        """Return all choices leading away from this node."""
        return self.outgoing_choices.select_related('target_node')


class Choice(models.Model):
    """
    Represents an edge/connection between two Nodes.
    This is what the player clicks to navigate the story.
    For riddle nodes, is_correct_path determines branching on answer validation.
    """
    source_node = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name='outgoing_choices',
    )
    target_node = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name='incoming_choices',
    )
    choice_text = models.CharField(max_length=500, default='Continue...')

    # Riddle branching: True = correct answer path, False = wrong answer path, None = normal choice
    is_correct_path = models.BooleanField(
        null=True,
        blank=True,
        default=None,
        help_text='For riddle nodes only: True = correct answer, False = wrong answer, None = normal choice.',
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.source_node.title} → {self.target_node.title}: {self.choice_text}"


class GameState(models.Model):
    """
    Tracks a player's progress through a story.
    Stores current position and custom variables (health, inventory, etc).
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='game_states',
    )
    story = models.ForeignKey(
        Story,
        on_delete=models.CASCADE,
        related_name='game_states',
    )
    current_node = models.ForeignKey(
        Node,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='active_players',
    )
    variables = models.JSONField(
        default=dict,
        blank=True,
        help_text='Custom game variables (health, inventory, flags, etc.)',
    )
    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        # One active game state per user per story
        unique_together = ['user', 'story']

    def __str__(self):
        node_title = self.current_node.title if self.current_node else 'N/A'
        return f"{self.user.username} playing '{self.story.title}' at '{node_title}'"
