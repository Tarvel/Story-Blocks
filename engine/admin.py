"""
engine/admin.py

Admin configuration for managing Stories, Nodes, Choices, and GameStates.
"""

from django.contrib import admin
from .models import Story, Node, Choice, GameState


class NodeInline(admin.TabularInline):
    """Inline editor for Nodes within a Story."""
    model = Node
    extra = 1
    fields = ('title', 'node_type', 'x', 'y')
    show_change_link = True


class ChoiceInline(admin.TabularInline):
    """Inline editor for Choices (outgoing edges) within a Node."""
    model = Choice
    fk_name = 'source_node'
    extra = 1
    fields = ('choice_text', 'target_node')


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_published', 'updated_at', 'node_count')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'description', 'author__username')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [NodeInline]

    def node_count(self, obj):
        return obj.nodes.count()
    node_count.short_description = '# Nodes'


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ('title', 'story', 'node_type', 'x', 'y', 'choice_count')
    list_filter = ('node_type', 'story')
    search_fields = ('title', 'content')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ChoiceInline]

    def choice_count(self, obj):
        return obj.outgoing_choices.count()
    choice_count.short_description = '# Choices'


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'source_node', 'target_node', 'created_at')
    list_filter = ('source_node__story',)
    search_fields = ('choice_text',)


@admin.register(GameState)
class GameStateAdmin(admin.ModelAdmin):
    list_display = ('user', 'story', 'current_node', 'updated_at')
    list_filter = ('story',)
    search_fields = ('user__username', 'story__title')
    readonly_fields = ('started_at', 'updated_at')
