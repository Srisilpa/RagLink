import os
import sys
from pathlib import Path

# =========================================================
# PROJECT ROOT
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# Add project root to Python path
sys.path.insert(
    0,
    str(BASE_DIR)
)

# =========================================================
# DJANGO SETTINGS
# =========================================================

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)

import django

django.setup()


# =========================================================
# IMPORT DJANGO MODELS
# =========================================================

from django.contrib.auth import get_user_model
from documents.models import Document


User = get_user_model()


# =========================================================
# GET USERS
# =========================================================

try:

    admin = User.objects.get(
        username="siri"
    )

except User.DoesNotExist:

    print(
        "ERROR: Admin user 'siri' does not exist."
    )

    sys.exit(1)


try:

    team_lead = User.objects.get(
        username="Hanu"
    )

except User.DoesNotExist:

    print(
        "ERROR: Team Lead user 'Hanu' does not exist."
    )

    sys.exit(1)


print(
    f"Admin found: {admin.username} | Role: {admin.role}"
)

print(
    f"Team Lead found: {team_lead.username} | Role: {team_lead.role}"
)


# =========================================================
# COMPANY DOCUMENT METADATA
# =========================================================

company_documents = [

    {
        "filename": "Series_Tech_Software_Engineering_Handbook.pdf",
        "title": "Series_Tech_Software_Engineering_Handbook",
        "department": "Software Development",
        "category": "Technical",
        "version": "1.0",
    },

    {
        "filename": "Series_Tech_QA_and_DevOps_Framework.txt",
        "title": "Series_Tech_QA_and_DevOps_Framework",
        "department": "DevOps",
        "category": "Technical",
        "version": "1.0",
    },

    {
        "filename": "Series_Tech_Payroll_and_Finance.pdf",
        "title": "Series_Tech_Payroll_and_Finance",
        "department": "Finance",
        "category": "Financial Policy",
        "version": "1.0",
    },

    {
        "filename": "Series_Tech_Limited_Operations_and_Support.txt",
        "title": "Series_Tech_Limited_Operations_and_Support",
        "department": "Operations",
        "category": "Support",
        "version": "1.0",
    },

    {
        "filename": "Series_Tech_Learning_and_Career_Development.pdf",
        "title": "Series_Tech_Learning_and_Career_Development",
        "department": "Human Resources",
        "category": "Career Development",
        "version": "1.1",
    },

    {
        "filename": "Series_Tech_IT_Services_and_Employee_Assets_v3.txt",
        "title": "Series_Tech_IT_Services_and_Employee_Assets_v3",
        "department": "IT",
        "category": "IT Policy",
        "version": "1.1",
    },

    {
        "filename": "Series_Tech_HR_Policies.pdf",
        "title": "Series_Tech_HR_Policies",
        "department": "Human Resources",
        "category": "HR Policy",
        "version": "1.0",
    },

    {
        "filename": "Series_Tech_Employee_Handbook.docx",
        "title": "Series_Tech_Employee_Handbook",
        "department": "Human Resources",
        "category": "HR Policy",
        "version": "2.0",
    },

    {
        "filename": "Series_Tech_Cybersecurity_and_Compliance.docx",
        "title": "Series_Tech_Cybersecurity_and_Compliance",
        "department": "Security",
        "category": "Compliance",
        "version": "1.0",
    },

    {
        "filename": "Series_Tech_Company_Profile.docx",
        "title": "Series_Tech_Company_Profile",
        "department": "Corporate",
        "category": "Company Profile",
        "version": "1.0",
    },

    {
        "filename": "Series_Tech_Cloud_Infrastructure.pdf",
        "title": "Series_Tech_Cloud_Infrastructure",
        "department": "Software Development",
        "category": "Infrastructure",
        "version": "1.0",
    },

]


# =========================================================
# PROJECT DOCUMENT METADATA
# =========================================================

project_documents = [

    {
        "filename": "Project_Meridian_Comprehensive_Technical_Specification.pdf",
        "title": "Project Meridian Technical & Architecture Specification",
        "department": "Software Development",
        "category": "Project Blueprint",
        "version": "2.1",
    },

]


# =========================================================
# RESTORE DOCUMENT FUNCTION
# =========================================================

def restore_document(
    item,
    folder,
    uploaded_by
):

    filename = item["filename"]

    # -----------------------------------------------------
    # Relative path stored in Django FileField
    # -----------------------------------------------------

    relative_file_path = os.path.join(
        folder,
        filename
    ).replace(
        "\\",
        "/"
    )

    # -----------------------------------------------------
    # Physical file path
    # -----------------------------------------------------

    full_file_path = (
        BASE_DIR
        / "media"
        / folder
        / filename
    )

    # -----------------------------------------------------
    # Check physical file
    # -----------------------------------------------------

    if not full_file_path.exists():

        print(
            f"FILE NOT FOUND: {full_file_path}"
        )

        return


    # -----------------------------------------------------
    # Find existing document by file path
    # -----------------------------------------------------

    document = Document.objects.filter(
        file=relative_file_path
    ).first()


    # -----------------------------------------------------
    # UPDATE EXISTING DOCUMENT
    # -----------------------------------------------------

    if document:

        document.title = item["title"]

        document.department = item["department"]

        document.category = item["category"]

        document.version = item["version"]

        document.uploaded_by = uploaded_by

        document.save(
            update_fields=[
                "title",
                "department",
                "category",
                "version",
                "uploaded_by",
            ]
        )

        print(
            f"UPDATED: {document.title}"
        )

        return


    # -----------------------------------------------------
    # CREATE NEW DOCUMENT
    # -----------------------------------------------------

    document = Document.objects.create(

        title=item["title"],

        department=item["department"],

        category=item["category"],

        version=item["version"],

        file=relative_file_path,

        uploaded_by=uploaded_by,

    )


    print(
        f"CREATED: {document.title}"
    )


# =========================================================
# RESTORE COMPANY DOCUMENTS
# =========================================================

print(
    "\n========================================"
)

print(
    "RESTORING COMPANY DOCUMENTS"
)

print(
    "========================================"
)


for item in company_documents:

    restore_document(

        item=item,

        folder="Company",

        uploaded_by=admin

    )


# =========================================================
# RESTORE PROJECT DOCUMENTS
# =========================================================

print(
    "\n========================================"
)

print(
    "RESTORING PROJECT DOCUMENTS"
)

print(
    "========================================"
)


for item in project_documents:

    restore_document(

        item=item,

        folder="Projects",

        uploaded_by=team_lead

    )


# =========================================================
# FINAL SUMMARY
# =========================================================

print(
    "\n========================================"
)

print(
    "RESTORATION COMPLETED"
)

print(
    "========================================"
)


print(
    "Total Document Records:",
    Document.objects.count()
)


print(
    "\nDocuments in database:"
)


for document in Document.objects.all().order_by(
    "id"
):

    print(

        f"ID: {document.id} | "

        f"Title: {document.title} | "

        f"Department: {document.department} | "

        f"Category: {document.category} | "

        f"Version: {document.version} | "

        f"Uploaded By: {document.uploaded_by.username} | "

        f"File: {document.file.name}"

    )