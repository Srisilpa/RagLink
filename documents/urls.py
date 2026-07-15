from django.urls import path

from . import views

urlpatterns = [

    path(
        "manage/",
        views.manage_documents,
        name="manage_documents"
    ),

    path(
        "delete/<int:document_id>/",
        views.delete_document,
        name="delete_document"
    ),

]