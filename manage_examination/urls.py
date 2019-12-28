from django.urls import path
from . import views

urlpatterns = [
    path('select_subject/', views.create_paper),
    path("paper_detail/<int:pk>/", views.PaperDetailView.as_view(), name='paper_detail'),
    path('upload/', views.upload_file, name="upload_file"),
    path('doc/<int:paper_id>',views.get_document),
]
