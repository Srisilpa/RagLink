from django.urls import path
from . import views

urlpatterns = [

    path(
        "manage/",
        views.manage_documents,
        name="manage_documents"
    ),

    path(
        "download/<int:document_id>/",
        views.download_document,
        name="download_document"
    ),

    path(
        "delete/<int:document_id>/",
        views.delete_document,
        name="delete_document"
    ),

]