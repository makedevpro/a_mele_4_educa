from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, FormView

from .forms import CourseEnrollForm


class StudentRegistrationView(CreateView):
    template_name = 'students/student/registration.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('students:student_course_list')

    def form_valid(self, form):
        """
        form_valid() обработчика будет выполняться при успешной валида-
        ции формы. Он должен возвращать объект HTTP-ответа. Мы переопределили
        его в нашем обработчике, чтобы после регистрации автоматически авторизо-
        вать пользователя на сайте.
        """
        result = super(StudentRegistrationView, self).form_valid(form)
        cd = form.cleaned_data
        user = authenticate(username=cd['username'],
                            password=cd['password1'])
        login(self.request, user)
        return result


class StudentEnrollCourseView(LoginRequiredMixin, FormView):
    """ Зачисление студанта на курс """
    course = None
    form_class = CourseEnrollForm

    def form_valid(self, form):
        # значение поля course из HiddenInput формы CourseEnrollForm
        self.course = form.cleaned_data['course']
        # создание связи между студентом и курсом
        self.course.students.add(self.request.user)
        return super(StudentEnrollCourseView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('students:student_course_detail',
                            args=[self.course.id])
