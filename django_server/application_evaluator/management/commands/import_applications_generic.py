# Management command to import data from Podio excel file to Django
import glob
from collections import OrderedDict
from pathlib import Path

import openpyxl
from django.core.files import File
from django.core.management.base import BaseCommand

from application_evaluator.models import Application, ApplicationAttachment, ApplicationRound


def get_application_round_from_challenge_name(challenge_name: str) -> ApplicationRound:
    """
    Get ApplicationRound from challenge name.
    """
    ars = ApplicationRound.objects.filter(name=challenge_name)
    # in the database titles are like "CC-310: How to do foo bar?", name should exist there as is
    if len(ars) != 1:
        print(f"ApplicationRound not found for {challenge_name}")
        print(f"Searched for: {challenge_name}")
        print(ars.query)
        exit()
    else:
        return ars[0]


def create_id_name_descriptions(app: dict) -> [str, str, str]:
    """Create id, name and description from application data."""
    app_id = app["Unique ID"]
    name = app.pop("Pilot name")
    dlist = []
    for f in app:
        # Loop all fields and add to dlist lines like
        dlist.append(f"## {f}\n{app[f]}")
    description = "\n\n".join(dlist)
    return app_id, name, description


def read_excel_sheet(filename: str) -> list:
    """
    Read Excel sheet and return it as a list of dicts.
    Skips the first header row and uses the second row as column names.
    Ignores columns where the second row header is empty.
    Keeps the original column order.
    """
    wb = openpyxl.load_workbook(filename)
    sheet = wb.worksheets[0]
    data_list = []

    # Get the second row as column names (skip first row)
    column_names = [cell.value for cell in sheet[2]]

    # Create a list of valid column indices where header is not empty
    valid_columns = [i for i, name in enumerate(column_names) if name is not None and name.strip() != ""]
    valid_headers = [column_names[i] for i in valid_columns]

    # Read data rows starting from third row
    for row in sheet.iter_rows(min_row=3, values_only=True):
        if any(value is not None for value in row):  # Skip empty rows
            # Only include values from valid columns
            row_data = [row[i] for i in valid_columns]
            # Use OrderedDict to preserve column order
            data_list.append(OrderedDict(zip(valid_headers, row_data)))

    return data_list


def import_attachments(app: Application, filename: str):
    """Add attachments to Application object."""
    # Delele old attachments
    # app.attachments.all().delete()
    filepath = Path(filename)
    # Check if exact filename exists in app.attachments
    # If it does, skip
    # If it doesn't, create ApplicationAttachment object and add it to app.attachments
    for a in app.attachments.all():
        print(f"ATTACH!\n{a.attachment.name}\n{filepath.name}\n")
        if Path(a.attachment.name).name.endswith(filepath.name.replace(" ", "_")):
            print(f"Attachment {filepath.name} already exists, skipping")
            return
        else:
            print(f"Attachment {filepath.name} not found in {a.attachment.name}")
    with open(filename, "rb") as f:
        attachment = ApplicationAttachment.objects.create(
            application=app,
            attachment=File(f),
            name=filepath.name,
        )
        attachment.save()
    print("New attachment", attachment)


def create_application(application_round: ApplicationRound, app: dict) -> [Application, bool]:
    """Create Application object from app dict."""
    app_id, name, description = create_id_name_descriptions(app)
    application, created = Application.objects.get_or_create(other_id=app_id, application_round=application_round)
    application.name = name
    application.description = description
    application.application_round = application_round
    application.save()
    return application, created


class Command(BaseCommand):
    help = "Import data from Podio excel file to Django"

    def add_arguments(self, parser):
        parser.add_argument("--filename", type=str, help="Excel file to import")
        parser.add_argument("--attachments-dir", type=str, required=False, help="Directory containing attachments")

    def handle(self, *args, **options):
        applications = read_excel_sheet(options["filename"])
        new_app_cnt = 0
        existing_app_cnt = 0
        attachment_cnt = 0
        for a in applications:
            ar = get_application_round_from_challenge_name(a["Open Call name"])
            print(ar)
            app, created = create_application(ar, a)
            if created:
                new_app_cnt += 1
                print(f"New application: {app}")
            else:
                existing_app_cnt += 1
                print(f"Existing application: {app}")
            # Check if there is a subdirectory with same name as app.other_id
            # If there is, import all files from that directory as attachments
            if options["attachments_dir"]:
                dirname = Path(options["attachments_dir"]) / Path(a["Unique ID"])
                for subdir in glob.glob(f"{dirname}/*"):
                    import_attachments(app, subdir)
                    attachment_cnt += 1
            print("----")
        print(f"New applications: {new_app_cnt}")
        print(f"Existing applications: {existing_app_cnt}")
        print(f"Attachments: {attachment_cnt}")
