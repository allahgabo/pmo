from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, RiskViewSet, TaskViewSet, ResourceViewSet, MilestoneViewSet

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'risks', RiskViewSet, basename='risk')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'resources', ResourceViewSet, basename='resource')
router.register(r'milestones', MilestoneViewSet, basename='milestone')

urlpatterns = [
    path('', include(router.urls)),
]
