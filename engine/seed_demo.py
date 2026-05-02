"""
Seed script: Creates a demo story with interconnected nodes and choices.
Run with: python manage.py shell < engine/seed_demo.py
"""

from django.contrib.auth.models import User
from engine.models import Story, Node, Choice

user = User.objects.get(username='admin')

# Create the demo story
story, created = Story.objects.get_or_create(
    title='The Obsidian Spire',
    author=user,
    defaults={
        'description': 'A high-stakes sci-fi mystery set in a dying orbital station. Every choice reshapes your fate.',
        'is_published': True,
    }
)

if created:
    # Start Node
    start = Node.objects.create(
        story=story, title='The Threshold', node_type='start',
        x=100, y=200,
        content=(
            "The air here tastes of ozone and forgotten machinery. You stand at the threshold of "
            "the Great Divide, where the floor of the station gives way to a sprawling abyss of "
            "liquid data. Below, currents of static-white code pulse like the heartbeat of a dying god.\n\n"
            "To your left, a terminal flickers with a persistent, rhythmic amber glow. It is the only "
            "light in this section of the Spire, casting your shadow long and distorted against the "
            "brutalist concrete pillars."
        ),
    )

    # Passage Nodes
    dark_room = Node.objects.create(
        story=story, title='The Dark Room', node_type='passage',
        x=500, y=100,
        content=(
            "You enter the chamber. The hum of the life support systems is the only sound. "
            "Shadows stretch like fingers across the panels. A control terminal sits dormant "
            "in the center, its screen cracked but still functional.\n\n"
            "The air is thinner here. Your suit's oxygen readout drops by 3%."
        ),
    )

    control = Node.objects.create(
        story=story, title='Control Panel', node_type='passage',
        x=900, y=50,
        content=(
            'The terminal flickers to life. "Oxygen levels at 12%," it warns in a cold, '
            "synthetic voice. You scan the interface — there's an override sequence available, "
            "but it requires a Section Key you may or may not have.\n\n"
            '"Warning: unauthorized access will trigger station lockdown."'
        ),
    )

    airlock = Node.objects.create(
        story=story, title='The Airlock', node_type='death',
        x=900, y=350,
        content=(
            "The door is jammed. Rust from the internal seals has fused the mechanism. "
            "You pull with everything you have, but the handle snaps clean off.\n\n"
            "Behind you, you hear the grinding of gears. The station is sealing this "
            "section. You are trapped. The oxygen counter ticks down to zero."
        ),
    )

    escape = Node.objects.create(
        story=story, title='Emergency Pod', node_type='ending',
        x=1300, y=50,
        content=(
            "The override works. Emergency lights flood the corridor in pulsing red. "
            "An escape pod bay opens — Pod 7 is still operational.\n\n"
            "You strap in. The launch sequence initiates. Through the viewport, you "
            "watch the Obsidian Spire shrink into the void, a monolith swallowed by "
            "the infinite dark.\n\nYou survived. But at what cost?"
        ),
    )

    # Create Choices (Edges)
    Choice.objects.create(
        source_node=start, target_node=dark_room,
        choice_text='Enter the Dark Room'
    )
    Choice.objects.create(
        source_node=dark_room, target_node=control,
        choice_text='Access the Control Panel'
    )
    Choice.objects.create(
        source_node=dark_room, target_node=airlock,
        choice_text='Retreat to the Airlock'
    )
    Choice.objects.create(
        source_node=control, target_node=escape,
        choice_text='Execute the Override Sequence'
    )
    Choice.objects.create(
        source_node=control, target_node=airlock,
        choice_text='Abandon the Terminal and Run'
    )

    print(f"✓ Demo story '{story.title}' created with {story.nodes.count()} nodes and {Choice.objects.filter(source_node__story=story).count()} edges.")
else:
    print(f"Demo story '{story.title}' already exists. Skipping.")
