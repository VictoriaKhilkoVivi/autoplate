from django.shortcuts import render
from django.views import View

from auto_plate.forms import FileForm
from auto_plate.models import FileForRecognition
from auto_plate.recognition import main_recognition, get_region
from auto_plate.work_with_database import find_by_plate_number


class CreateNewFileForRecognition(View):
    template_name = 'auto_plate/index.html'
    form_class = FileForm
    model = FileForRecognition

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        context = {}
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            form = form.save(commit=False)
            form.file = request.FILES['file']
            form.save()

            name = 'media/test/' + request.FILES['file'].name
            number = main_recognition(name)
            context['number'] = number

            data_about_driver = find_by_plate_number(number)
            context['driver'] = data_about_driver

            try:
                region = get_region(number)['data']
            except KeyError:
                context['region'] = None
            else:
                context['region'] = region

            return render(request, 'auto_plate/after_recognition.html', context)

        context = {'form': form}
        return render(request, self.template_name, context)
