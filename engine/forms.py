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
        fields = ['title', 'description', 'is_published']
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
        }


class NodeForm(forms.ModelForm):
    """Form for creating and editing nodes."""
    class Meta:
        model = Node
        fields = ['title', 'content', 'node_type']
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
        }


class ChoiceForm(forms.ModelForm):
    """Form for creating connections (edges) between nodes."""
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
