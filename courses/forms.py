from django import forms
from django.forms.models import inlineformset_factory

from .models import Course, Module

# набор форм ModuleFormSet
# формируем его с помощью фабричной функции Django inlineformset_factory()
# Получаем набор форм, когда объекты одного типа, модули, будут связаны с
# объектом другого типа, курсами
ModuleFormSet = inlineformset_factory(Course,
                                      Module,
                                      fields=['title', 'description'],
                                      extra=2,
                                      can_delete=True)
