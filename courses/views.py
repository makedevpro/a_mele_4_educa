from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin, \
    PermissionRequiredMixin
from django.forms.models import modelform_factory
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
# TemplateResponseMixin – примесь, которая добавит формирование HTML- шаблона
# и вернет его в качестве ответа на запрос. добавляет в дочерние классы метод
# render_to_response(), который сформирует результирую- щую страницу
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .forms import ModuleFormSet
from .models import Course, Module, Content


class OwnerMixin(object):

    def get_queryset(self):
        qs = super(OwnerMixin, self).get_queryset()
        # Получаем только объекты, владельцем которых является
        # текущий пользователь
        return qs.filter(owner=self.request.user)


class OwnerEditMixin(object):
    def form_valid(self, form):
        # автоматически заполняем поле owner сохраняемого объекта
        form.instance.owner = self.request.user
        return super(OwnerEditMixin, self).form_valid(form)


class OwnerCourseMixin(LoginRequiredMixin, OwnerMixin):
    model = Course


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    fields = ['subject', 'title', 'slug', 'overview']
    success_url = reverse_lazy('courses:manage_course_list')
    template_name = 'courses/manage/course/form.html'


class ManageCourseListView(OwnerCourseMixin, ListView):
    """ Список курсов, созданных пользователем """
    template_name = 'courses/manage/course/list.html'


class CourseCreateView(PermissionRequiredMixin,
                       OwnerCourseEditMixin,
                       CreateView):
    """ Используем модельную форму для создания нового курса """
    permission_required = 'courses.add_course'


class CourseUpdateView(PermissionRequiredMixin,
                       OwnerCourseEditMixin,
                       UpdateView):
    """ Редактирование курса владельцем """
    permission_required = 'courses.change_course'


class CourseDeleteView(PermissionRequiredMixin,
                       OwnerCourseMixin,
                       DeleteView):
    """ Удаление курса владельцем """
    template_name = 'courses/manage/course/delete.html'
    success_url = reverse_lazy('courses:manage_course_list')
    permission_required = 'courses.delete_course'


class CourseModuleUpdateView(TemplateResponseMixin, View):
    """
    Обрабатывает действия, связанные с набором форм по сохранению,
    редактированию и удалению модулей для конкретного курса
    """
    template_name = 'courses/manage/module/formset.html'
    course = None

    # Формируем набор форм
    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.course, data=data)

    # метод, определенный в базовом классе View. Он принимает
    # объект запроса и его параметры и пытается вызвать метод,
    # который соответствует HTTP-методу запроса
    def dispatch(self, request, pk):
        self.course = get_object_or_404(Course,
                                        pk=pk,
                                        owner=request.user)
        return super(CourseModuleUpdateView, self).dispatch(request, pk)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({'course': self.course,
                                        'formset': formset})

    def post(self, request, *args, **kwargs):
        # Создаем набор форм ModuleFormSet по отправленным данным
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('courses:manage_course_list')
        return self.render_to_response({'course': self.course,
                                        'formset': formset})


class ContentCreatedUpdateView(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    template_name = 'courses/manage/content/form.html'

    # возвращает класс модели по переданному имени
    # обращаемся к модулю apps Django, чтобы получить класс модели
    def get_model(self, model_name):
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label='courses',
                                  model_name=model_name)
        return None

    # создает форму в зависимости от типа содержимого
    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, exclude=['owner',
                                                 'order',
                                                 'created',
                                                 'updated'])
        return Form(*args, **kwargs)

    # получает приведенные ниже данные из запроса и создает соответствующие
    # объекты модуля, модели содержимого:
    # - module_id–идентификатормодуля,ккоторомупривязаносодержимое;
    # - model_name – имя модели содержимого;
    # - id – идентификатор изменяемого объекта.
    def dispatch(self, request, module_id, model_name, id=None):
        self.module = get_object_or_404(Module,
                                        id=module_id,
                                        course__owner=request.user)
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model,
                                         id=id,
                                         owner=request.user)
        return super(ContentCreatedUpdateView, self).dispatch(request,
                                                              module_id,
                                                              model_name,
                                                              id)

    def get(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form, 'object': object})

    def post(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model,
                             instance=self.obj,
                             data=request.POST,
                             files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                # Создаем новый объект.
                Content.objects.create(module=self.module, item=obj)
            return redirect('courses:module_content_list', self.module.id)
        return self.render_to_response({'form': form, 'object': self.obj})


class ContentDeleteView(View):

    def post(self, request, id):
        content = get_object_or_404(Content,
                                    id=id,
                                    module__course__owner=request.user)
        module = content.module
        content.item.delete()
        content.delete()
        return redirect('courses:module_content_list', module.id)
