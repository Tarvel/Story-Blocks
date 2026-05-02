"""
engine/views.py

Views for the StoryBoard platform:
- Creator Dashboard
- Story Canvas (node layout editor)
- HTMX endpoints for Node/Choice CRUD
- Node Editor slide-out panel
- AI Co-Pilot endpoints
- Player/Playtest engine
"""

import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods

from .models import Story, Node, Choice, GameState
from .forms import StoryForm, NodeForm, ChoiceForm
from .services import generate_story_enhancement


# ─────────────────────────────────────────────
# Phase 2: Dashboard & Canvas Views
# ─────────────────────────────────────────────

@login_required
def dashboard(request):
    """Creator Dashboard — lists all of the user's stories."""
    stories = Story.objects.filter(author=request.user)
    return render(request, 'engine/dashboard.html', {
        'stories': stories,
    })


@login_required
def story_create(request):
    """Create a new story and redirect to its canvas."""
    if request.method == 'POST':
        form = StoryForm(request.POST)
        if form.is_valid():
            story = form.save(commit=False)
            story.author = request.user
            story.save()
            # Auto-create a start node
            Node.objects.create(
                story=story,
                title='Start',
                content='The story begins here...',
                node_type='start',
                x=200,
                y=200,
            )
            return redirect('engine:story_canvas', story_id=story.pk)
    else:
        form = StoryForm()
    return render(request, 'engine/story_create.html', {'form': form})


@login_required
def story_canvas(request, story_id):
    """
    Story Canvas — the visual node editor.
    Loads all nodes as JSON for the JS canvas renderer.
    """
    story = get_object_or_404(Story, pk=story_id, author=request.user)
    nodes = story.nodes.all()
    choices = Choice.objects.filter(source_node__story=story).select_related(
        'source_node', 'target_node'
    )

    # Serialize nodes for the JS canvas
    nodes_json = json.dumps([{
        'id': node.pk,
        'title': node.title,
        'content': node.content[:80] + ('...' if len(node.content) > 80 else ''),
        'node_type': node.node_type,
        'x': node.x,
        'y': node.y,
    } for node in nodes])

    # Serialize choices/edges for SVG lines
    edges_json = json.dumps([{
        'id': choice.pk,
        'source_id': choice.source_node_id,
        'target_id': choice.target_node_id,
        'text': choice.choice_text,
    } for choice in choices])

    choice_form = ChoiceForm(story=story)

    return render(request, 'engine/canvas.html', {
        'story': story,
        'nodes': nodes,
        'nodes_json': nodes_json,
        'edges_json': edges_json,
        'choice_form': choice_form,
    })


# ─────────────────────────────────────────────
# HTMX Endpoints: Node CRUD
# ─────────────────────────────────────────────

@login_required
@require_POST
def node_create(request, story_id):
    """Create a new node on the canvas. Returns HTML partial."""
    story = get_object_or_404(Story, pk=story_id, author=request.user)

    node = Node.objects.create(
        story=story,
        title=request.POST.get('title', 'New Node'),
        content='',
        node_type=request.POST.get('node_type', 'passage'),
        x=float(request.POST.get('x', 300)),
        y=float(request.POST.get('y', 300)),
    )

    return render(request, 'engine/partials/canvas_node.html', {
        'node': node,
        'story': story,
    })


@login_required
@require_http_methods(["POST", "PATCH"])
def node_update(request, node_id):
    """
    Update a node's content or coordinates.
    Handles both HTMX form posts and JSON coordinate updates from drag-and-drop.
    """
    node = get_object_or_404(Node, pk=node_id, story__author=request.user)

    # JSON request (drag-and-drop coordinate update)
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            if 'x' in data:
                node.x = float(data['x'])
            if 'y' in data:
                node.y = float(data['y'])
            node.save(update_fields=['x', 'y'])
            return JsonResponse({'status': 'ok', 'x': node.x, 'y': node.y})
        except (json.JSONDecodeError, ValueError) as e:
            return JsonResponse({'error': str(e)}, status=400)

    # Form post (content update from node editor)
    form = NodeForm(request.POST, instance=node)
    if form.is_valid():
        form.save()
        # Return JSON so the canvas JS can sync its in-memory data
        return JsonResponse({
            'status': 'ok',
            'id': node.pk,
            'title': node.title,
            'content': node.content[:80],
            'node_type': node.node_type,
        })

    return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)


@login_required
def node_delete(request, node_id):
    """Delete a node from the canvas."""
    node = get_object_or_404(Node, pk=node_id, story__author=request.user)
    node.delete()
    return HttpResponse('')


# ─────────────────────────────────────────────
# HTMX Endpoint: Node Editor Slide-out
# ─────────────────────────────────────────────

@login_required
def node_detail(request, node_id):
    """
    Returns the Node Editor slide-out panel partial.
    Called via hx-get when clicking a node on the canvas.
    """
    node = get_object_or_404(Node, pk=node_id, story__author=request.user)
    form = NodeForm(instance=node)
    choices = node.outgoing_choices.select_related('target_node')

    return render(request, 'engine/partials/node_editor.html', {
        'node': node,
        'form': form,
        'choices': choices,
        'story': node.story,
    })


# ─────────────────────────────────────────────
# HTMX Endpoints: Choice CRUD
# ─────────────────────────────────────────────

@login_required
@require_POST
def choice_create(request, story_id):
    """Create a new Choice (edge) between two nodes."""
    story = get_object_or_404(Story, pk=story_id, author=request.user)
    form = ChoiceForm(request.POST, story=story)

    if form.is_valid():
        choice = form.save()
        # Return updated edge data as JSON for the canvas JS to draw
        return JsonResponse({
            'status': 'ok',
            'id': choice.pk,
            'source_id': choice.source_node_id,
            'target_id': choice.target_node_id,
            'text': choice.choice_text,
        })

    return JsonResponse({'errors': form.errors}, status=400)


@login_required
def choice_delete(request, choice_id):
    """Delete a choice/edge."""
    choice = get_object_or_404(
        Choice, pk=choice_id, source_node__story__author=request.user
    )
    choice.delete()
    return HttpResponse('')


# ─────────────────────────────────────────────
# Phase 4: AI Co-Pilot Endpoints
# ─────────────────────────────────────────────

@login_required
@require_POST
def ai_enhance(request):
    """AI endpoint: enhance the tone/description of a passage."""
    text = request.POST.get('text', '')
    if not text.strip():
        return HttpResponse('<p class="text-error font-metadata">No text provided.</p>')

    result = generate_story_enhancement(text, 'enhance')
    return render(request, 'engine/partials/ai_result.html', {
        'result': result,
        'action': 'enhance',
    })


@login_required
@require_POST
def ai_choices(request):
    """AI endpoint: suggest 3 player choices based on a passage."""
    text = request.POST.get('text', '')
    if not text.strip():
        return HttpResponse('<p class="text-error font-metadata">No text provided.</p>')

    result = generate_story_enhancement(text, 'choices')
    return render(request, 'engine/partials/ai_result.html', {
        'result': result,
        'action': 'choices',
    })


@login_required
@require_POST
def ai_expand(request):
    """AI endpoint: expand a passage with an additional paragraph."""
    text = request.POST.get('text', '')
    if not text.strip():
        return HttpResponse('<p class="text-error font-metadata">No text provided.</p>')

    result = generate_story_enhancement(text, 'expand')
    return render(request, 'engine/partials/ai_result.html', {
        'result': result,
        'action': 'expand',
    })


# ─────────────────────────────────────────────
# Phase 5: Player Engine
# ─────────────────────────────────────────────

def play_story(request, story_id):
    """
    Player view — loads a published story starting from its start node.
    Handles both initial page load and HTMX node transitions.
    """
    story = get_object_or_404(Story, pk=story_id)

    # Get or determine the current node
    node_id = request.GET.get('node_id')
    if node_id:
        node = get_object_or_404(Node, pk=node_id, story=story)
    else:
        node = story.get_start_node()
        if not node:
            return render(request, 'engine/play_error.html', {
                'story': story,
                'error': 'This story has no start node.',
            })

    choices = node.get_outgoing_choices()

    # Track game state if user is authenticated
    if request.user.is_authenticated:
        game_state, _ = GameState.objects.get_or_create(
            user=request.user,
            story=story,
            defaults={'current_node': node},
        )
        game_state.current_node = node
        game_state.save(update_fields=['current_node', 'updated_at'])

    # HTMX request — return just the reading partial
    if request.headers.get('HX-Request'):
        return render(request, 'engine/partials/play_content.html', {
            'story': story,
            'node': node,
            'choices': choices,
        })

    # Full page load
    return render(request, 'engine/play.html', {
        'story': story,
        'node': node,
        'choices': choices,
    })


def make_choice(request, choice_id):
    """
    Handle a player making a choice — redirect/swap to the target node.
    """
    choice = get_object_or_404(
        Choice, pk=choice_id
    )
    target_node = choice.target_node
    story = target_node.story
    choices = target_node.get_outgoing_choices()

    # Update game state
    if request.user.is_authenticated:
        GameState.objects.filter(
            user=request.user, story=story
        ).update(current_node=target_node)

    # HTMX request — return the reading partial
    if request.headers.get('HX-Request'):
        return render(request, 'engine/partials/play_content.html', {
            'story': story,
            'node': target_node,
            'choices': choices,
        })

    return redirect(f'/play/{story.pk}/?node_id={target_node.pk}')
