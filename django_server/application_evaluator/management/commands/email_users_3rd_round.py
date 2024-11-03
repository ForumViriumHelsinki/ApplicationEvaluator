# Management command to send emails to users (pilot manager and jury members)
# of a specific application round.

import openpyxl
from django.core import mail
from django.core.management.base import BaseCommand

from application_evaluator.models import ApplicationRound


def read_challenge_doc(filename: str) -> dict:
    """Read Excel sheet and return it as a dict."""
    wb = openpyxl.load_workbook(filename)
    sheet = wb.worksheets[0]
    data_list = []

    for row in sheet.iter_rows(min_row=1, values_only=True):
        if any(value is not None for value in row):  # Skip empty rows
            data_list.append(row)

    column_names = data_list.pop(0)
    # create list of dicts
    data_list = [dict(zip(column_names, row)) for row in data_list]
    # Convert data_list to a dict where key is id and value is doc_link
    doc_dict = {d["id"]: d["doc_link"] for d in data_list}
    return doc_dict


def read_templates(pilot_manager_template: str, jury_template: str, vars: dict) -> [str, str]:
    pilot_manager_email, jury_email = None, None
    if pilot_manager_template:
        with open(pilot_manager_template, "r") as f:
            pilot_manager_email = f.read()
            pilot_manager_email = pilot_manager_email.format(**vars)
    if jury_template:
        with open(jury_template, "r") as f:
            jury_email = f.read()
            jury_email = jury_email.format(**vars)
    return pilot_manager_email, jury_email


def send_emails(
    subject: str,
    pilot_manager_email_address: str,
    jury_email_addresses: list,
    pilot_manager_email: str,
    jury_email: str,
):
    connection = mail.get_connection()
    connection.open()

    emails = []
    if pilot_manager_email_address:
        emails.append(
            mail.EmailMessage(
                f"Pilot manager: {subject}",
                pilot_manager_email,
                "noreply-evaluator-message@mg.forumvirium.fi",
                [pilot_manager_email_address],
                connection=connection,
            )
        )
    for email_address in jury_email_addresses:
        emails.append(
            mail.EmailMessage(
                f"Jury member: {subject}",
                jury_email,
                "noreply-evaluator-message@mg.forumvirium.fi",
                [email_address],
                connection=connection,
            )
        )

    connection.send_messages(emails)
    connection.close()


class Command(BaseCommand):
    help = "Import user data from Podio excel file to Django"

    def add_arguments(self, parser):
        parser.add_argument("--application-round", type=str, required=True)
        parser.add_argument("--challenge-doc", type=str, help="CSV file containing challenge document links")
        parser.add_argument("--emails", nargs="+", type=str, help="Limit sending to these email addresses")
        parser.add_argument("--pilot-manager-template", type=str, help="Pilot manager's email template file")
        parser.add_argument("--jury-template", type=str, help="Jury member's email template file")
        parser.add_argument("--dry-run", action="store_true", help="Don't save to database")

    def handle(self, *args, **options):
        application_round_id = options["application_round"]
        # Read excel file containing challenge document links
        doc_dict = read_challenge_doc(options["challenge_doc"])
        if application_round_id not in doc_dict:
            print(f"Application round {application_round_id} not found in challenge document links")
            exit(1)
        doc_link = doc_dict[application_round_id]
        ar = ApplicationRound.objects.get(name__startswith=application_round_id)
        ar_admin = ar.admin
        ar_jury = ar.evaluators.all()
        vars = {
            "challenge_id": application_round_id,
            "challenge_name": ar.name,
            "doc_link": doc_link,
        }
        pilot_manager_email, jury_email = read_templates(
            options["pilot_manager_template"], options["jury_template"], vars
        )
        if options["dry_run"]:
            exit()
        # Check if emails are limited to certain addresses
        if options["emails"]:
            ar_jury = ar_jury.filter(email__in=options["emails"])
            if ar_admin.email not in options["emails"]:
                ar_admin = None
        # Send emails
        subject = f"CommuniCity application [{application_round_id}] ready for evaluation"
        send_emails(subject, ar_admin.email, [u.email for u in ar_jury], pilot_manager_email, jury_email)
