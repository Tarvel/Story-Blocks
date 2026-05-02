"""
engine/urls.py

URL routing for the StoryBoard engine.
"""

from django.urls import path
from . import views

app_name = 'engine'

urlpatterns = [
    # ── Dashboard ──
    path('', views.dashboard, name='dashboard'),
    path('story/create/', views.story_create, name='story_create'),

    # ── Story Canvas ──
    path('story/<int:story_id>/canvas/', views.story_canvas, name='story_canvas'),

    # ── Node CRUD (HTMX) ──
    path('story/<int:story_id>/node/create/', views.node_create, name='node_create'),
    path('node/<int:node_id>/update/', views.node_update, name='node_update'),
    path('node/<int:node_id>/delete/', views.node_delete, name='node_delete'),
    path('node/<int:node_id>/detail/', views.node_detail, name='node_detail'),

    # ── Choice CRUD ──
    path('story/<int:story_id>/choice/create/', views.choice_create, name='choice_create'),
    path('choice/<int:choice_id>/delete/', views.choice_delete, name='choice_delete'),

    # ── AI Co-Pilot ──
    path('ai/enhance/', views.ai_enhance, name='ai_enhance'),
    path('ai/choices/', views.ai_choices, name='ai_choices'),
    path('ai/expand/', views.ai_expand, name='ai_expand'),

    # ── Player Engine ──
    path('play/<int:story_id>/', views.play_story, name='play_story'),
    path('play/choice/<int:choice_id>/', views.make_choice, name='make_choice'),
]
