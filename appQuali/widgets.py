from django.forms import FileInput
from django import forms


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True
