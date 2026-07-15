from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Document
from .forms import DocumentForm

import os


@login_required(login_url="home")
def manage_documents(request):

    # Admin can see all documents
    if request.user.role == "ADMIN":

        documents = Document.objects.all()

    # Team Lead sees only their uploads
    elif request.user.role == "TEAM_LEAD":

        documents = Document.objects.filter(
            uploaded_by=request.user
        )

    else:

        return redirect("dashboard")

    # Upload
    if request.method == "POST":

        form = DocumentForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            doc = form.save(commit=False)

            doc.uploaded_by = request.user

            doc.save()

            messages.success(
                request,
                "Document uploaded successfully."
            )

            return redirect("manage_documents")

    else:

        form = DocumentForm()

    # Search
    search = request.GET.get("search", "")

    if search:

        documents = documents.filter(
            title__icontains=search
        )

    # Department Filter
    department = request.GET.get("department", "")

    if department:

        documents = documents.filter(
            department__icontains=department
        )

    # Category Filter
    category = request.GET.get("category", "")

    if category:

        documents = documents.filter(
            category__icontains=category
        )

    documents = documents.order_by(
        "-upload_date"
    )

    return render(

        request,

        "documents/manage_documents.html",

        {

            "form": form,

            "documents": documents,

            "search": search,

            "department": department,

            "category": category,

        }

    )


@login_required(login_url="home")
def delete_document(request, document_id):

    document = get_object_or_404(
        Document,
        id=document_id
    )

    if request.user.role != "ADMIN":

        messages.error(
            request,
            "Permission Denied."
        )

        return redirect(
            "manage_documents"
        )

    if document.file:

        if os.path.exists(
            document.file.path
        ):

            os.remove(
                document.file.path
            )

    document.delete()

    messages.success(
        request,
        "Document deleted successfully."
    )

    return redirect(
        "manage_documents"
    )