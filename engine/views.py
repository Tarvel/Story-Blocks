"""
engine/views.py

Views for the StoryBoard platform:
- Creator Dashboard
- Story Canvas (node layout editor)
- HTMX endpoints for Node/Choice CRUD
- Node Editor slide-out panel
- AI Co-Pilot endpoints
- Player/Playtest engine
- User Registration
"""

import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.views.decorators.http import require_POST, require_http_methods

from .models import Story, Node, Choice, GameState
from .forms import StoryForm, NodeForm, ChoiceForm


# ─────────────────────────────────────────────
# Registration
# ─────────────────────────────────────────────

def register_view(request):
    """Handle new user registration."""
    if request.user.is_authenticated:
        return redirect('engine:dashboard')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('engine:dashboard')
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})
from .services import generate_story_enhancement


# ─────────────────────────────────────────────
# Phase 2: Dashboard & Canvas Views
# ─────────────────────────────────────────────

@login_required
def dashboard(request):
    """Creator Dashboard — lists all of the user's stories."""
    stories = Story.objects.filter(author=request.user).select_related('author').prefetch_related('nodes')
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
@require_POST
def story_delete(request, story_id):
    """Delete a story and all its nodes/choices."""
    story = get_object_or_404(Story, pk=story_id, author=request.user)
    story.delete()
    return redirect('engine:dashboard')

@login_required
@require_POST
def story_settings(request, story_id):
    """Update story metadata (title, description, publish, password) from canvas."""
    story = get_object_or_404(Story, pk=story_id, author=request.user)

    story.title = request.POST.get('title', story.title).strip() or story.title
    story.description = request.POST.get('description', story.description)
    story.is_published = request.POST.get('is_published') == 'on'
    # Handle access_password — empty string means remove password
    pw = request.POST.get('access_password', '').strip()
    story.access_password = pw if pw else None
    story.save()

    return JsonResponse({
        'status': 'ok',
        'title': story.title,
        'is_published': story.is_published,
    })

@login_required
def story_canvas(request, story_id):
    """
    Story Canvas — the visual node editor.
    Loads all nodes as JSON for the JS canvas renderer.
    """
    story = get_object_or_404(
        Story.objects.select_related('author').prefetch_related('nodes'),
        pk=story_id, author=request.user
    )
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
        'is_correct_path': choice.is_correct_path,
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
    import json
    response = HttpResponse('')
    response['HX-Trigger'] = json.dumps({'nodeDeleted': node_id})
    return response


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
            'is_correct_path': choice.is_correct_path,
        })

    return JsonResponse({'errors': form.errors}, status=400)


@login_required
def choice_delete(request, choice_id):
    """Delete a choice/edge."""
    choice = get_object_or_404(
        Choice, pk=choice_id, source_node__story__author=request.user
    )
    choice.delete()
    response = HttpResponse('')
    response['HX-Trigger'] = json.dumps({'edgeDeleted': choice_id})
    return response


# ─────────────────────────────────────────────
# Phase 4: AI Co-Pilot Endpoints
# ─────────────────────────────────────────────

def _gather_ai_context(request):
    """
    Helper: gather the passage text + optional story context.
    If node_id is provided, we also send the story title and
    content of connected (parent) nodes for richer AI context.
    """
    text = request.POST.get('text', '')
    node_id = request.POST.get('node_id', '')
    context_parts = []

    if node_id:
        try:
            node = Node.objects.select_related('story').get(pk=int(node_id))
            context_parts.append(f"Story: \"{node.story.title}\"")
            if node.story.description:
                context_parts.append(f"Story Description: {node.story.description}")
            context_parts.append(f"Current Node: \"{node.title}\"")

            # Gather content from parent/sibling nodes for narrative flow
            incoming = node.incoming_choices.select_related('source_node').all()[:3]
            for choice in incoming:
                src = choice.source_node
                if src.content:
                    context_parts.append(
                        f"Previous passage (\"{src.title}\"): {src.content[:300]}"
                    )
        except (Node.DoesNotExist, ValueError):
            pass

    if context_parts:
        context_header = "=== STORY CONTEXT ===\n" + "\n".join(context_parts) + "\n\n=== CURRENT PASSAGE ===\n"
        return context_header + text, text
    return text, text


@login_required
@require_POST
def ai_enhance(request):
    """AI endpoint: enhance the tone/description of a passage."""
    text = request.POST.get('text', '')
    if not text.strip():
        return HttpResponse('<p class="text-error font-metadata">No text provided.</p>')

    full_prompt, _ = _gather_ai_context(request)
    result = generate_story_enhancement(full_prompt, 'enhance')
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

    full_prompt, _ = _gather_ai_context(request)
    result = generate_story_enhancement(full_prompt, 'choices')
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

    full_prompt, _ = _gather_ai_context(request)
    result = generate_story_enhancement(full_prompt, 'expand')
    return render(request, 'engine/partials/ai_result.html', {
        'result': result,
    })


# ─────────────────────────────────────────────
# Phase 5: Player Engine
# ─────────────────────────────────────────────

def play_story(request, slug):
    """
    Player view — loads a published story starting from its start node.
    Uses slug for shareable URLs with password gate for private stories.
    """
    story = get_object_or_404(Story, slug=slug)

    # ── Password Gate ──
    if story.access_password:
        session_key = f'unlocked_{story.story_uuid}'
        if not request.session.get(session_key):
            if request.method == 'POST':
                submitted_password = request.POST.get('password', '')
                if submitted_password == story.access_password:
                    request.session[session_key] = True
                    return redirect('engine:play_story', slug=story.slug)
                else:
                    return render(request, 'engine/password_gate.html', {
                        'story': story,
                        'error': True,
                    })
            # GET request — show password gate
            return render(request, 'engine/password_gate.html', {
                'story': story,
            })

    # ── Normal Play Flow ──
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

    play_url = reverse('engine:play_story', kwargs={
        'slug': story.slug,
    })
    return redirect(f'{play_url}?node_id={target_node.pk}')


@require_POST
def riddle_check(request, node_id):
    """
    Validate a player's answer on a riddle node.
    Case-insensitive match against Node.correct_answer.
    Routes to correct-path or wrong-path edges based on is_correct_path.
    """
    node = get_object_or_404(Node, pk=node_id, node_type='riddle')
    player_answer = request.POST.get('answer', '').strip()
    story = node.story
    is_correct = player_answer.lower() == node.correct_answer.lower()

    # Find the appropriate outgoing edge
    if is_correct:
        branch = node.outgoing_choices.filter(is_correct_path=True).first()
    else:
        branch = node.outgoing_choices.filter(is_correct_path=False).first()

    # Fallback: if no riddle-specific edges, use first outgoing on correct
    if not branch and is_correct:
        branch = node.outgoing_choices.first()

    if branch:
        target_node = branch.target_node
        choices = target_node.get_outgoing_choices()

        # Update game state
        if request.user.is_authenticated:
            GameState.objects.filter(
                user=request.user, story=story
            ).update(current_node=target_node)

        if request.headers.get('HX-Request'):
            response = render(request, 'engine/partials/play_content.html', {
                'story': story,
                'node': target_node,
                'choices': choices,
            })
            response['HX-Retarget'] = '#reading-container'
            return response
        play_url = reverse('engine:play_story', kwargs={
            'slug': story.slug,
        })
        return redirect(f'{play_url}?node_id={target_node.pk}')
    else:
        # No matching branch edge configured — show inline feedback and disable form
        if is_correct:
            msg = '✓ Correct! But the path fades into nothingness (no connected node).'
            color = 'text-emerald-500'
        else:
            msg = 'Incorrect. The path is sealed.'
            color = 'text-red-500'

        play_url = reverse('engine:play_story', kwargs={'slug': story.slug})

        # Return the feedback message AND an OOB swap to replace the form
        html = f'''
        <p class="font-serif italic text-xl {color} mt-4">{msg}</p>

        <div id="riddle-form" hx-swap-oob="true" class="flex flex-col items-center gap-6 w-full">
            <input type="text" value="{player_answer}" disabled
                   class="w-full bg-transparent border-b-2 border-surface text-center text-2xl text-muted p-3 font-serif tracking-widest cursor-not-allowed opacity-50" />
            <div class="mt-8 flex justify-center w-full">
                <a href="{play_url}"
                   class="font-sans text-[10px] tracking-[0.3em] uppercase text-muted px-8 py-4 border border-surface hover:border-muted hover:bg-surface/30 transition-all rounded-sm no-underline flex items-center gap-3">
                    <span class="material-symbols-outlined text-lg">restart_alt</span>
                    Restart Story
                </a>
            </div>
        </div>
        '''
        return HttpResponse(html)


# ─────────────────────────────────────────────
# Phase 6: Community & Templates
# ─────────────────────────────────────────────

@login_required
def community_templates_view(request):
    """View public templates and stories from the community."""
    # Fetch published stories (could exclude current user if desired)
    stories = Story.objects.filter(is_published=True).select_related('author').prefetch_related('nodes')
    return render(request, 'engine/community.html', {
        'stories': stories,
    })
