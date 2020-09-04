from django.urls import reverse_lazy
from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .models import Course


class OwnerMixin(object):
    def get_queryset(self):
        qs = super(OwnerMixin, self).get_queryset()
        # Получаем только объекты, владельцем которых является
        # текущий пользователь
        return qs.filter(owner=self.request.user)


class OwnerEditMixin(object):
    def form_valid(self, form):
        # автоматически заполняем поле owner сохраняемого объекта
        form.instanse.owner = self.request.user
        return super(OwnerEditMixin, self).form_valid(form)


class OwnerCourseMixin(OwnerMixin):
    model = Course


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    fields = ['subject', 'title', 'slug', 'overview']
    success_url = reverse_lazy('manage_course_list')
    template_name = 'courses/manage/course/form.html'


class ManageCourseListView(OwnerCourseMixin, ListView):
    """ Список курсов, созданных пользователем """
    template_name = 'courses/manage/course/list.html'


class CourseCreateView(OwnerCourseEditMixin, CreateView):
    """ Используем модельную форму для создания нового курса """
    pass


class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    """ Редактирование курса владельцем """
    pass


class CourseDeleteView(OwnerCourseMixin, DeleteView):
    """ Удаление курса владельцем """
    template_name = 'course/manage/course/delete.html'
    success_url = reverse_lazy('manage_course_list')

