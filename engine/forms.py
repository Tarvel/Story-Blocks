"""
engine/forms.py

Forms for Story, Node, and Choice CRUD operations.
"""

from django import forms
from .models import Story, Node, Choice


class StoryForm(forms.ModelForm):
    """Form for creating and editing stories."""
    class Meta:
        model = Story
        fields = ['title', 'description', 'is_published', 'is_template', 'access_password']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full bg-white border-4 border-black p-4 font-metadata uppercase focus:outline-none focus:bg-primary-container transition-colors shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]',
                'placeholder': 'STORY TITLE...',
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full bg-white border-4 border-black p-4 font-body-md focus:outline-none focus:bg-primary-container transition-colors shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]',
                'placeholder': 'Describe your story...',
                'rows': 4,
            }),
            'access_password': forms.TextInput(attrs={
                'class': 'w-full bg-white border-4 border-black p-4 font-metadata focus:outline-none focus:bg-primary-container transition-colors shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]',
                'placeholder': 'Leave blank for public access',
            }),
        }


class NodeForm(forms.ModelForm):
    """Form for creating and editing nodes."""
    class Meta:
        model = Node
        fields = ['title', 'content', 'node_type', 'correct_answer']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full bg-white border-4 border-black p-3 font-metadata uppercase focus:outline-none focus:bg-primary-container transition-colors',
                'placeholder': 'NODE TITLE...',
            }),
            'content': forms.Textarea(attrs={
                'id': 'node-content-editor',
                'class': 'w-full bg-transparent border-none focus:ring-0 p-0 resize-none leading-relaxed font-body-lg text-black placeholder:opacity-30',
                'placeholder': 'Write your passage here...',
                'rows': 12,
            }),
            'node_type': forms.Select(attrs={
                'class': 'w-full bg-white border-4 border-black p-3 font-metadata uppercase focus:outline-none focus:bg-primary-container transition-colors',
            }),
            'correct_answer': forms.TextInput(attrs={
                'class': 'w-full bg-white border-4 border-black p-3 font-metadata focus:outline-none focus:bg-primary-container transition-colors',
                'placeholder': 'e.g. Tai (case-insensitive)',
            }),
        }


class ChoiceForm(forms.ModelForm):
    """Form for creating connections (edges) between nodes."""

    RIDDLE_PATH_CHOICES = [
        ('', '— Not a riddle edge —'),
        ('true', '✓ Correct Answer Path'),
        ('false', '✗ Wrong Answer Path'),
    ]

    riddle_path = forms.ChoiceField(
        choices=RIDDLE_PATH_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full bg-white border-4 border-black p-3 font-metadata uppercase focus:outline-none',
            'id': 'id_riddle_path',
        }),
    )

    class Meta:
        model = Choice
        fields = ['source_node', 'target_node', 'choice_text']
        widgets = {
            'choice_text': forms.TextInput(attrs={
                'class': 'w-full bg-white border-4 border-black p-3 font-metadata uppercase focus:outline-none focus:bg-primary-container transition-colors',
                'placeholder': 'WHAT DOES THE PLAYER SEE?',
            }),
            'source_node': forms.Select(attrs={
                'class': 'w-full bg-white border-4 border-black p-3 font-metadata uppercase focus:outline-none',
            }),
            'target_node': forms.Select(attrs={
                'class': 'w-full bg-white border-4 border-black p-3 font-metadata uppercase focus:outline-none',
            }),
        }

    def __init__(self, *args, story=None, **kwargs):
        super().__init__(*args, **kwargs)
        if story:
            self.fields['source_node'].queryset = Node.objects.filter(story=story)
            self.fields['target_node'].queryset = Node.objects.filter(story=story)

    def save(self, commit=True):
        choice = super().save(commit=False)
        # Map the riddle_path dropdown to the model field
        rp = self.cleaned_data.get('riddle_path', '')
        if rp == 'true':
            choice.is_correct_path = True
        elif rp == 'false':
            choice.is_correct_path = False
        else:
            choice.is_correct_path = None
        if commit:
            choice.save()
        return choice
