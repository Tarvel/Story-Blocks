"""
engine/models.py

Core data models for the StoryBoard interactive storytelling platform.
"""

from django.db import models
from django.conf import settings
from django.urls import reverse


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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name_plural = 'stories'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('engine:story_canvas', kwargs={'story_id': self.pk})

    def get_start_node(self):
        """Return the designated start node for this story."""
        return self.nodes.filter(node_type='start').first()


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
