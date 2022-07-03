from django.forms import ModelForm

from auto_plate.models import FileForRecognition


class FileForm(ModelForm):
    class Meta:
        model = FileForRecognition
        fields = ['file']
