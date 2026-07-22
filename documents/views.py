from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib.auth.decorators import login_required

from django.contrib import messages

from django.http import FileResponse

from .models import Document

from .forms import DocumentForm

import os


# =========================================================
# MANAGE DOCUMENTS
# =========================================================

@login_required(login_url="home")
def manage_documents(request):

    # -----------------------------------------------------
    # Check user role
    # -----------------------------------------------------

    if request.user.role == "ADMIN":

        # ADMIN can see all documents
        documents = Document.objects.all()

    elif request.user.role == "TEAM_LEAD":

        # TEAM LEAD can see only their own documents
        documents = Document.objects.filter(
            uploaded_by=request.user
        )

    else:

        messages.error(
            request,
            "You do not have permission to manage documents."
        )

        return redirect(
            "dashboard"
        )


    # -----------------------------------------------------
    # Upload Document
    # -----------------------------------------------------

    if request.method == "POST":

        form = DocumentForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            # Do not save immediately
            doc = form.save(
                commit=False
            )

            # Set current logged-in user
            doc.uploaded_by = request.user

            # Save document
            doc.save()

            messages.success(
                request,
                "Document uploaded successfully."
            )

            return redirect(
                "manage_documents"
            )

        else:

            messages.error(
                request,
                "Please correct the errors below."
            )

    else:

        form = DocumentForm()


    # -----------------------------------------------------
    # Search Filters
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # Search by title
    # -----------------------------------------------------

    if search:

        documents = documents.filter(
            title__icontains=search
        )


    # -----------------------------------------------------
    # Filter by department
    # -----------------------------------------------------

    if department:

        documents = documents.filter(
            department__icontains=department
        )


    # -----------------------------------------------------
    # Filter by category
    # -----------------------------------------------------

    if category:

        documents = documents.filter(
            category__icontains=category
        )


    # -----------------------------------------------------
    # Filter by uploaded user
    # -----------------------------------------------------

    if uploaded_by:

        documents = documents.filter(
            uploaded_by__username__icontains=uploaded_by
        )


    # -----------------------------------------------------
    # Newest documents first
    # -----------------------------------------------------

    documents = documents.order_by(
        "-upload_date"
    )


    # -----------------------------------------------------
    # Render page
    # -----------------------------------------------------

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


# =========================================================
# DELETE DOCUMENT
# =========================================================

@login_required(login_url="home")
def delete_document(
    request,
    document_id
):

    # -----------------------------------------------------
    # Only ADMIN can delete
    # -----------------------------------------------------

    if request.user.role != "ADMIN":

        messages.error(
            request,
            "Permission Denied."
        )

        return redirect(
            "manage_documents"
        )


    # -----------------------------------------------------
    # Get document
    # -----------------------------------------------------

    document = get_object_or_404(
        Document,
        id=document_id
    )


    # -----------------------------------------------------
    # Delete physical file
    # -----------------------------------------------------

    if document.file:

        if os.path.exists(
            document.file.path
        ):

            os.remove(
                document.file.path
            )


    # -----------------------------------------------------
    # Delete database record
    # -----------------------------------------------------

    document.delete()


    messages.success(
        request,
        "Document deleted successfully."
    )


    return redirect(
        "manage_documents"
    )


# =========================================================
# DOWNLOAD DOCUMENT
# =========================================================

@login_required(login_url="home")
def download_document(
    request,
    document_id
):

    # -----------------------------------------------------
    # Get document
    # -----------------------------------------------------

    document = get_object_or_404(
        Document,
        id=document_id
    )


    # -----------------------------------------------------
    # TEAM LEAD can download only own document
    # ADMIN can download any document
    # -----------------------------------------------------

    if request.user.role == "TEAM_LEAD":

        if document.uploaded_by != request.user:

            messages.error(
                request,
                "You do not have permission to download this document."
            )

            return redirect(
                "manage_documents"
            )


    # -----------------------------------------------------
    # Return file
    # -----------------------------------------------------

    return FileResponse(

        document.file.open(
            "rb"
        ),

        as_attachment=True,

        filename=os.path.basename(
            document.file.name
        )

    )