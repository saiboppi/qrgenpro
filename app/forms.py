from django import forms
from .models import Image

class LabelsForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['code']
