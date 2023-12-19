from rest_framework import status, generics
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsCharityOwner, IsBenefactor
from charities.models import Task , Benefactor
from charities.serializers import (
    TaskSerializer, CharitySerializer, BenefactorSerializer
)



class BenefactorRegistration(APIView):
    def post(self,request):
        Benefactor_serializer=BenefactorSerializer(data=request.data)
        if Benefactor_serializer.is_valid():
            Benefactor_serializer.save(user=request.user)
            return Response({"massage":"successfully ...."})



class CharityRegistration(APIView):
    def post(self,request):
        Charity_serializer=CharitySerializer(data=request.data)
        if Charity_serializer.is_valid():
            Charity_serializer.save(user=request.user)
            return Response({"message":"successfuly ...."})


class Tasks(generics.ListCreateAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.all_related_tasks_to_user(self.request.user)

    def post(self, request, *args, **kwargs):
        data = {
            **request.data,
            "charity_id": request.user.charity.id
        }
        serializer = self.serializer_class(data = data)
        serializer.is_valid(raise_exception = True)
        serializer.save()
        return Response(serializer.data, status = status.HTTP_201_CREATED)

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            self.permission_classes = [IsAuthenticated, ]
        else:
            self.permission_classes = [IsCharityOwner, ]

        return [permission() for permission in self.permission_classes]

    def filter_queryset(self, queryset):
        filter_lookups = {}
        for name, value in Task.filtering_lookups:
            param = self.request.GET.get(value)
            if param:
                filter_lookups[name] = param
        exclude_lookups = {}
        for name, value in Task.excluding_lookups:
            param = self.request.GET.get(value)
            if param:
                exclude_lookups[name] = param

        return queryset.filter(**filter_lookups).exclude(**exclude_lookups)


class TaskRequest(APIView):
    permission_classes=[IsBenefactor, ]
    model=Task
    def get(self,request,task_id):
        task=get_object_or_404(Task,pk=task_id)
        if task.state == "Pending" or task.state == "P":
            task.state="W"

            task.assigned_benefactor=request.user.benefactor
            task.save()
            return Response(data={'detail': 'Request sent.'},status=200)
        
        return Response(data={'detail': 'This task is not pending.'},status=404)

class TaskResponse(APIView):
    permission_classes=[IsCharityOwner, ]
    def post(self,request,task_id):
        if request.data['response'] == "A" or request.data['response'] == "R":
            task=get_object_or_404(Task,pk=task_id)
            if task.state == "W":
                if request.data['response'] == "A":
                    task.state = "A"
                    task.save()
                    return Response(data={'detail': 'Response sent.'},status=200)
                if request.data['response'] == "R":
                    task.state= "P"
                    task.assigned_benefactor=None
                    task.save()
                    return Response(data={'detail': 'Response sent.'},status=200)

            return Response(data={'detail': 'This task is not waiting.'},status=404)
        return Response(data={'detail': 'Required field ("A" for accepted / "R" for rejected)'},status=400)


class DoneTask(APIView):
    pass