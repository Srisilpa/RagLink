import os

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib.auth.decorators import (
    login_required
)

from django.contrib import messages

from django.http import FileResponse

from django.utils import timezone

from .models import Document

from .forms import DocumentForm

from rag.ingestion.dynamic_ingestion import (
    DynamicIngestionManager
)


# =========================================================
# MANAGE DOCUMENTS
# =========================================================

@login_required(login_url="home")
def manage_documents(request):

    # -----------------------------------------------------
    # DOCUMENT VISIBILITY
    # -----------------------------------------------------

    if request.user.role == "ADMIN":

        documents = Document.objects.all()

    elif request.user.role == "TEAM_LEAD":

        documents = Document.objects.filter(

            uploaded_by=request.user

        )

    else:

        messages.error(

            request,

            "You do not have permission "
            "to manage documents."

        )

        return redirect(
            "dashboard"
        )

    # -----------------------------------------------------
    # UPLOAD DOCUMENT
    # -----------------------------------------------------

    if request.method == "POST":

        form = DocumentForm(

            request.POST,

            request.FILES

        )

        if form.is_valid():

            # ---------------------------------------------
            # SAVE DOCUMENT DATABASE RECORD
            # ---------------------------------------------

            doc = form.save(
                commit=False
            )

            doc.uploaded_by = (
                request.user
            )

            doc.save()

            # ---------------------------------------------
            # DYNAMIC RAG INGESTION
            # ---------------------------------------------

            try:

                ingestion_manager = (

                    DynamicIngestionManager()

                )

                # -----------------------------------------
                # DETERMINE DOCUMENT TYPE
                # -----------------------------------------

                if request.user.role == "ADMIN":

                    document_type = (
                        "company"
                    )

                elif request.user.role == "TEAM_LEAD":

                    document_type = (
                        "project"
                    )

                else:

                    document_type = (
                        "other"
                    )

                # -----------------------------------------
                # INGEST
                # -----------------------------------------

                result = (

                    ingestion_manager
                    .ingest_document(

                        file_path=(
                            doc.file.path
                        ),

                        document_id=(
                            doc.id
                        ),

                        document_type=(
                            document_type
                        )

                    )

                )

                # -----------------------------------------
                # UPDATE INDEXING STATUS
                # -----------------------------------------

                doc.indexed = True

                doc.indexed_chunk_count = (

                    result.get(
                        "chunks",
                        0
                    )

                )

                doc.indexed_at = (
                    timezone.now()
                )

                doc.indexing_error = ""

                doc.save(

                    update_fields=[

                        "indexed",

                        "indexed_chunk_count",

                        "indexed_at",

                        "indexing_error"

                    ]

                )

                messages.success(

                    request,

                    "Document uploaded and "
                    "indexed successfully."

                )

            except Exception as e:

                # -----------------------------------------
                # INDEXING FAILED
                # -----------------------------------------

                doc.indexed = False

                doc.indexed_chunk_count = 0

                doc.indexing_error = str(
                    e
                )

                doc.save(

                    update_fields=[

                        "indexed",

                        "indexed_chunk_count",

                        "indexing_error"

                    ]

                )

                messages.warning(

                    request,

                    "Document uploaded successfully, "
                    "but RAG indexing failed."

                )

                print(

                    "DYNAMIC INGESTION ERROR:",

                    repr(e)

                )

            return redirect(

                "manage_documents"

            )

        else:

            messages.error(

                request,

                "Please correct the "
                "errors below."

            )

    else:

        form = DocumentForm()

    # -----------------------------------------------------
    # SEARCH FILTERS
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
    # FILTER BY TITLE
    # -----------------------------------------------------

    if search:

        documents = documents.filter(

            title__icontains=search

        )

    # -----------------------------------------------------
    # FILTER BY DEPARTMENT
    # -----------------------------------------------------

    if department:

        documents = documents.filter(

            department__icontains=department

        )

    # -----------------------------------------------------
    # FILTER BY CATEGORY
    # -----------------------------------------------------

    if category:

        documents = documents.filter(

            category__icontains=category

        )

    # -----------------------------------------------------
    # FILTER BY USER
    # -----------------------------------------------------

    if uploaded_by:

        documents = documents.filter(

            uploaded_by__username__icontains=(
                uploaded_by
            )

        )

    # -----------------------------------------------------
    # ORDER
    # -----------------------------------------------------

    documents = documents.order_by(

        "-upload_date"

    )

    # -----------------------------------------------------
    # RENDER
    # -----------------------------------------------------

    return render(

        request,

        "documents/manage_documents.html",

        {

            "form":
                form,

            "documents":
                documents,

            "search":
                search,

            "department":
                department,

            "category":
                category,

            "uploaded_by":
                uploaded_by,

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

    # =====================================================
    # PERMISSION
    # =====================================================

    if request.user.role != "ADMIN":

        messages.error(

            request,

            "Permission Denied."

        )

        return redirect(

            "manage_documents"

        )

    # =====================================================
    # GET DOCUMENT
    # =====================================================

    document = get_object_or_404(

        Document,

        id=document_id

    )

    document_title = document.title

    document_file_path = None

    if document.file:

        document_file_path = (

            document.file.path

        )

    # =====================================================
    # DELETE FROM RAG INDEX
    # =====================================================

    try:

        ingestion_manager = (

            DynamicIngestionManager()

        )

        result = (

            ingestion_manager
            .delete_document(

                document.id

            )

        )

        print(

            "Removed chunks:",

            result[
                "removed_chunks"
            ]

        )

    except Exception as e:

        print(

            "RAG deletion error:",

            e

        )

        messages.error(

            request,

            "Failed to remove document "
            "from RAG index."

        )

        return redirect(

            "manage_documents"

        )

    # =====================================================
    # DELETE PHYSICAL FILE
    # =====================================================

    if (

        document_file_path

        and

        os.path.exists(

            document_file_path

        )

    ):

        try:

            os.remove(

                document_file_path

            )

        except Exception as e:

            print(

                "File deletion warning:",

                e

            )

    # =====================================================
    # DELETE DATABASE RECORD
    # =====================================================

    document.delete()

    messages.success(

        request,

        f"Document '{document_title}' "
        "and all indexed RAG data deleted successfully."

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
    # GET DOCUMENT
    # -----------------------------------------------------

    document = get_object_or_404(

        Document,

        id=document_id

    )

    # -----------------------------------------------------
    # TEAM LEAD PERMISSION
    # -----------------------------------------------------

    if request.user.role == "TEAM_LEAD":

        if document.uploaded_by != request.user:

            messages.error(

                request,

                "You do not have permission "
                "to download this document."

            )

            return redirect(

                "manage_documents"

            )

    # -----------------------------------------------------
    # RETURN FILE
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