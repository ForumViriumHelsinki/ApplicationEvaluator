# Create management command to import data from Podio excel file to Django
import glob
import logging
from pathlib import Path

import pandas as pd
from django.core.files import File
from django.core.management.base import BaseCommand

from application_evaluator.models import Application, ApplicationAttachment, ApplicationRound

# CSV column headers:
fields = [
    "Tender ID",
    "Name of Tender / Consortium",
    "Lead tenderer name",
    "Lead tenderer contact email",
    "lead-tenderer-country",
    "lead-tenderer-orgtype",
    "lead-tenderer-orgsize",
    "lead-tenderer-foundingyear",
    "partner1-organisation",
    "partner1-country",
    "partner1-orgtype",
    "partner1-orgsize",
    "partner1-foundingyear",
    "partner2-organisation",
    "partner2-country",
    "partner2-orgtype",
    "partner2-orgsize",
    "partner2-foundingyear",
    "partner3-organisation",
    "partner3-country",
    "partner3-orgtype",
    "partner3-orgsize",
    "partner3-foundingyear",
    "partner4-organisation",
    "partner4-country",
    "partner4-orgtype",
    "partner4-orgsize",
    "partner4-foundingyear",
    "partner5-organisation",
    "partner5-country",
    "partner5-orgtype",
    "partner5-orgsize",
    "partner5-foundingyear",
    "Upload here the following completed forms. They should all be in PDF format.",
    "Form A: Technical Offer",
    "Form B: Executive summary",
    "Form C: Financial offer, incl. cost breakdown",
    "Form D: Power of attorney",
    "Form E: Exclusion and compliance criteria (via webform)",
    "Yes",
    "tenderid",
    "folderid",
    "Created By (User Id)",
    "Entry Id",
    "Entry Date",
    "Date Updated",
    "Source Url",
    "Transaction Id",
    "Payment Amount",
    "Payment Date",
    "Payment Status",
    "Post Id",
    "User Agent",
    "User IP",
]


def create_id_name_descriptions(app: dict) -> [str, str, str]:
    """Create id, name and description from application data."""
    app_id = app["Tender Auto ID"]
    name = f"{app['Tender Eval ID']} {app['Tender Name']}"
    description = ""
    return app_id, name, description


def import_attachments(app: Application, filename: str):
    """Add attachments to Application object."""
    # Delele old attachments
    # app.attachments.all().delete()
    filepath = Path(filename)
    # Check if exact filename exists in app.attachments
    # If it does, skip
    # If it doesn't, create ApplicationAttachment object and add it to app.attachments
    for a in app.attachments.all():
        logging.debug(f"ATTACH!\n{a.attachment.name}\n{filepath.name}\n")
        if Path(a.attachment.name).name.endswith(filepath.name.replace(" ", "_")):
            logging.debug(f"Attachment {filepath.name} already exists, skipping")
            return
        else:
            logging.debug(f"Attachment {filepath.name} not found in {a.attachment.name}")
    with open(filename, "rb") as f:
        attachment = ApplicationAttachment.objects.create(
            application=app,
            attachment=File(f),
            name=filepath.name,
        )
        attachment.save()
        logging.debug("New attachment", attachment)


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
    help = "Import data from CSV file to Application objects"

    def add_arguments(self, parser):
        parser.add_argument("--filename", type=str, required=True, help="CSV file to import")
        parser.add_argument("--challenge-name", type=str, required=True, help="Challenge name")
        parser.add_argument("--attachments-dir", type=str, required=True, help="Directory containing attachments")
        parser.add_argument("--attachments-pattern", type=str, required=True, help="Pattern for attachments")
        parser.add_argument("--limit", type=int, help="Limit number of applications to import")
        parser.add_argument(
            "--log", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="Log level"
        )

    def handle(self, *args, **options):
        logging.basicConfig(level=options["log"])
        # Read CSV file using pandas and convert to list of dictionaries
        df = pd.read_csv(options["filename"])
        # Print total number of rows in DataFrame
        # Drop rows where "Tender Auto ID" is empty or NaN
        df = df[df["Tender Auto ID"].notna()]
        # Print all column headers from CSV
        logging.debug("CSV column headers:")
        logging.debug(df.columns.tolist())
        applications = df.to_dict("records")
        logging.info(f"Total number of applications: {len(applications)}")
        application_round = ApplicationRound.objects.get(name=options["challenge_name"])
        logging.info(f"Importing applications for {application_round}")
        new_app_cnt = 0
        existing_app_cnt = 0
        attachment_cnt = 0
        missing_attachment_cnt = 0
        missing_attachments = []
        for a in applications:
            logging.debug(f"{new_app_cnt + existing_app_cnt + 1}. Processing {a['Tender Auto ID']} {a['Tender Name']}")
            dirname = Path(options["attachments_dir"]) / Path(a["Tender Auto ID"])
            if not dirname.exists():
                logging.error(f"Directory {dirname} does not exist, BAD ERROR")
            attachments = glob.glob(f"{dirname}/*{options['attachments_pattern']}*")
            if len(attachments) == 0:
                logging.error(f"No {options['attachments_pattern']} for {a['Tender Auto ID']} {a['Tender Name']}")
                missing_attachment_cnt += 1
                missing_attachments.append(a["Tender Auto ID"])
                continue
            logging.debug(f"Attachments for {a['Tender Auto ID']} {a['Tender Name']}:", ", ".join(attachments))
            app, created = create_application(application_round, a)
            if created:
                new_app_cnt += 1
                logging.debug(f"New application: {app}")
            else:
                existing_app_cnt += 1
                logging.debug(f"Existing application: {app}")
            # Delete existing attachments
            for attachment in app.attachments.all():
                # Delete the actual file from filesystem
                attachment.attachment.delete()
                # Delete the database record
                attachment.delete()
            for filename in attachments:
                logging.debug(filename)
                import_attachments(app, filename)
                attachment_cnt += 1
            logging.debug("----")
            if options["limit"] and new_app_cnt + existing_app_cnt >= options["limit"]:
                logging.info(f"Limit {options['limit']} reached, stopping")
                break
        logging.info(f"New applications: {new_app_cnt}")
        logging.info(f"Existing applications: {existing_app_cnt}")
        logging.info(f"Attachments: {attachment_cnt}")
        logging.info(f"Missing attachments: {missing_attachment_cnt}")
        logging.info(f"Missing attachments: {missing_attachments}")
