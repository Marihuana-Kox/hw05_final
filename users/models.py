from django.db import models
from django.forms import ModelForm


# создадим модель, в которой будем хранить данные формы
class Book(models.Model):
    name = models.CharField(max_length=100)
    isbn = models.CharField(max_length=100)


class BookForm(ModelForm):
    class Meta:
        # эта форма будет хранить данные в модели Book
        model = Book
        # на странице формы будут отображаться поля 'name' и 'isbn'
        fields = ['name', 'isbn']
