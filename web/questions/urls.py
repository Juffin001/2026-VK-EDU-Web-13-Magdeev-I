from django.urls import path
from . import views

app_name = 'questions'

urlpatterns = [
    path('', views.index, name='index'),
    path('hot/', views.hot, name='hot'),
    path('ask/', views.ask, name='ask'),
    path("question/<int:pk>/", views.question, name="question"),
    path('tag/<path:tag_text>/', views.tag, name='tag'),
]
