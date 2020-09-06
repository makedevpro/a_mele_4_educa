from rest_framework import generics, viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.shortcuts import get_object_or_404

from ..models import Subject, Course
from .serializers import SubjectSerializer, CourseSerializer


class SubjectListView(generics.ListAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class SubjectDetailView(generics.RetrieveAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


# class CourseEnrollView(APIView):
#     """ Запись студента на курс """
#     # добавляем классу атрибу аутентификации
#     authentication_classes = (BasicAuthentication,)
#     # добавляем атрибут разрешений
#     # IsAuthenticated - анонимам запрещен доступ к обработчику
#     permission_classes = (IsAuthenticated,)
#
#     def post(self, request, pk, format=None):
#         course = get_object_or_404(Course, pk=pk)
#         course.students.add(request.user)
#         return Response({'enrolled': True})


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """ Маршрутизатор с методами retrieve и list """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    # detail_route, чтобы указать, что метод работает с одним объектом,
    # а не списком
    @action(detail=True, methods=['post'],
            authentication_classes=[BasicAuthentication],
            permission_classes=[IsAuthenticated])
    def enroll(self, request, *args, **kwargs):
        """
        метод enroll(), который будет обрабатывать нестандартное
        действие – зачисление студентов на курсы
        """
        course = self.get_object()
        course.students.add(request.user)
        return Response({'enrolled': True})
