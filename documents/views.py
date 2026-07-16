from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse
from .models import Document
from .forms import DocumentForm
import os


@login_required(login_url="home")
def manage_documents(request):

    # -------------------------------
    # Documents visible by role
    # -------------------------------
    if request.user.role == "ADMIN":
        documents = Document.objects.all()

    elif request.user.role == "TEAM_LEAD":
        documents = Document.objects.filter(
            uploaded_by=request.user
        )

    else:
        return redirect("dashboard")

    # -------------------------------
    # Upload Document
    # -------------------------------
    if request.method == "POST" and "upload_document" in request.POST:

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

    # -------------------------------
    # Search Filters (GET)
    # -------------------------------

    search = request.GET.get(
        "search",
        ""
    )

    department = request.GET.get(
        "department",
        ""
    )

    category = request.GET.get(
        "category",
        ""
    )

    uploaded_by = request.GET.get(
        "uploaded_by",
        ""
    )

    if search:

        documents = documents.filter(
            title__icontains=search
        )

    if department:

        documents = documents.filter(
            department__icontains=department
        )

    if category:

        documents = documents.filter(
            category__icontains=category
        )

    if uploaded_by:

        documents = documents.filter(
            uploaded_by__username__icontains=uploaded_by
        )

    # Always newest first from Django
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

            "uploaded_by": uploaded_by,

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


@login_required(login_url="home")
def download_document(request, document_id):

    document = get_object_or_404(
        Document,
        id=document_id
    )

    return FileResponse(

        document.file.open("rb"),

        as_attachment=True,

        filename=os.path.basename(
            document.file.name
        )

    )