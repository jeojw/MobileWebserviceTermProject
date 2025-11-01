from rest_framework import routers
from django.urls import path
import views

router = routers.DefaultRouter()
router.register('Post', views.BlogImages)

urlpatterns = [
    path("", views)
]