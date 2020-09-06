from rest_framework.permissions import BasePermission


class IsEnrolled(BasePermission):
    """
    Ограничение доступа к содержимому курсов
    для студентов не записанных на него

    проверяем, является ли текущий пользователь слушателем курса,
    через атри- бут students объекта модели Course

    Класс IsEnrolled является наследником BasePermission и переопределяет
    метод has_object_permission().

    methods:
    has_permission() – выполняет проверку доступа на уровне обработчика;
    has_object_permission() – проверяет доступ к объекту.

    """

    def has_object_permissions(self, request, view, obj):
        return obj.students.filter(id=request.user.id).exists()
