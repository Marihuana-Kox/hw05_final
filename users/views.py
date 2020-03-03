# позволяет узнать ссылку на URL по его имени, параметр name функции path
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm
from django.core import mail
from django.http import request


class SignUp(CreateView):
    form_class = CreationForm
    success_url = "/auth/login/"
    template_name = "signup.html"

    def form_valid(self, form):
        email = form.cleaned_data['email']
        mail.send_mail(
            'Тема письма', 'Текст письма.',
            'from@rocknrolla.net', [email],
            fail_silently=False,
        )
        return super().form_valid(form)
