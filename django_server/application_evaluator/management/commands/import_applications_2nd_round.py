# Create management command to import data from Podio excel file to Django
import glob
from pathlib import Path

import openpyxl
from django.core.files import File

from django.core.management.base import BaseCommand
from application_evaluator.models import Application, ApplicationRound, ApplicationAttachment


# fields contains list of fields to be imported from excel file to Django
# first value is heading level (0 not shown in description), original title in excel, new title description field
# 0==ignore/>=1==include (value means heading level), original title, new title
fields = [
    [4, "Title of the application", "Application Title"],
    [4, "Publishable summary of the application. (max. 1000 characters with spaces)", "Summary"],
    [0, "Select city", "City"],
    [4, "Select the challenge", "Challenge"],
    [0, "Organisation", "Organization"],
    [0, "Business ID (if you are individual citizen, just mark XX)", "Business ID"],
    [0, "First name", "First Name"],
    [0, "Last name", "Last Name"],
    [0, "E-mail address", "Email"],
    [0, "Phone number", "Phone Number"],
    [
        0,
        "List here organisations and contact persons of any Piloting Partners",
        "Piloting Partners (Organizations and Contacts)",
    ],
    [
        4,
        "Short description of the application (incl. target groups, objectives, technologies and methods) "
        "and expected impact. (max. 5 000 characters with spaces)",
        "Application Description",
    ],
    [
        4,
        "Work plan including preparatory actions, piloting plan, scale-up and replicability activities as well as "
        "sustainability of the application. (max. 5 000 characters with spaces)",
        "Work Plan",
    ],
    [
        4,
        "Resource plan including personnel, budget and possible self-funding. (max. 3 000 characters with spaces)",
        "Resource Plan (Personnel, Budget, Self-funding)",
    ],
    [4, "Description of the co-creation methods applied. (max. 3 000 characters with spaces)", "Co-creation Methods"],
    [4, "Plan for involving target group members. (max. 3 000 characters with spaces)", "Involvement of Target Group"],
    [6, "In addition to Helsinki, you can offer your solution to", "Offer Solution to Helsinki"],
    [6, "In addition to Amsterdam, you can offer your solution to", "Offer Solution to Amsterdam"],
    [6, "Choose your budget for the Amsterdam pilot", "Budget for Amsterdam Pilot"],
    [6, "Piloting plan for the Amsterdam pilot. (max. 3 000 characters)", "Piloting Plan for Amsterdam"],
    [6, "Choose your budget for the Porto pilot", "Budget for Porto Pilot"],
    [6, "Piloting plan for the Porto pilot. (max. 3 000 characters)", "Piloting Plan for Porto"],
    [6, "Choose your budget for the Tallinn pilot", "Budget for Tallinn Pilot"],
    [6, "Piloting plan for the Tallinn pilot. (max. 3 000 characters)", "Piloting Plan for Tallinn"],
    [6, "Choose your budget for the Prague pilot", "Budget for Prague Pilot"],
    [6, "Piloting plan for the Prague pilot. (max. 3 000 characters)", "Piloting Plan for Prague"],
    [0, "Data privacy", "Data Privacy"],
    [0, "GDPR", "GDPR Compliance"],
    [0, "Ethics", "Ethical Considerations"],
    [0, "I accept storing of personal information", "Accept Storing Personal Information"],
    [0, "Data security policy", "Data Security Policy"],
    [0, "Application ID", "Application ID"],
    [0, "Submit date and time", "Submission Date and Time"],
]


def get_application_round_from_challenge_name(challenge_name: str) -> ApplicationRound:
    """
    Get ApplicationRound from challenge name.
    Challenge name is like "Helsinki: How to do foo bar?"
    """
    # split challenge name to city and title using ':'
    city, name = [x.strip() for x in challenge_name.split(":")]
    # Search for ApplicationRounds with name containing title's first 4 words
    # Pick 4 first words from title:
    words = name.split(" ")
    # remove all words shorter than 3 characters
    words = [w for w in words if len(w) >= 3][:4]
    # create qset for filtering ApplicationRounds where name contains all words
    ars = ApplicationRound.objects.filter(name__startswith="CC-2")
    for w in words:
        ars = ars.filter(name__icontains=w)
    if len(ars) != 1:
        print(f"ApplicationRound not found for {challenge_name}")
        print(f"Words: {words}")
        print(ars.query)
        exit()
    else:
        return ars[0]


def create_id_name_descriptions(app: dict) -> [str, str, str]:
    """Create id, name and description from application data."""
    app_id = app["Application ID"]
    name = app["Application Title"]
    dlist = []
    for f in fields:
        if f[0] > 0:
            # Loop all fields and add to dlist lines like
            dlist.append("#" * f[0] + f" {f[2]}\n\n{app[f[2]]}")
    description = "\n\n".join(dlist)
    return app_id, name, description


def read_excel_sheet(filename: str) -> list:
    """Read Excel sheet and return it as a list of dicts."""
    wb = openpyxl.load_workbook(filename)
    sheet = wb.worksheets[0]
    data_list = []

    for row in sheet.iter_rows(min_row=1, values_only=True):
        if any(value is not None for value in row):  # Skip empty rows
            data_list.append(row)

    column_names = data_list.pop(0)
    # create list of dicts
    data_list = [dict(zip(column_names, row)) for row in data_list]
    # remove items with None values
    # NOTE: this doesn't work because some fields are empty strings in excel
    # data_list = [{k: v for k, v in d.items() if v is not None} for d in data_list]
    return data_list


def import_attachments(app: Application, filename: str):
    """Add attachments to Application object."""
    filepath = Path(filename)
    # Check if exact filename exists in app.attachments
    # If it does, skip
    # If it doesn't, create ApplicationAttachment object and add it to app.attachments
    for a in app.attachments.all():
        print(a.attachment.name, filepath.name)
        if Path(a.attachment.name).name == filepath.name:
            print(f"Attachment {filepath.name} already exists, skipping")
            return
    with open(filename, "rb") as f:
        attachment = ApplicationAttachment.objects.create(
            application=app,
            attachment=File(f),
            name=filepath.name,
        )
        attachment.save()
    print(attachment)


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
        # Replace long column names with short ones. Long column name is fields[][1], short is fields[][2]
        applications = [{f[2]: a[f[1]] for f in fields} for a in applications]
        new_app_cnt = 0
        existing_app_cnt = 0
        attachment_cnt = 0
        for a in applications:
            # if a["Application ID"] != "CC-2HE11-e7aad100-a2c4-98b7-1698756037":
            #     continue
            ar = get_application_round_from_challenge_name(a["Challenge"])
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
                dirname = options["attachments_dir"]
                for subdir in glob.glob(f"{dirname}/{app.other_id}/*"):
                    import_attachments(app, subdir)
                    attachment_cnt += 1
            print("----")
        print(f"New applications: {new_app_cnt}")
        print(f"Existing applications: {existing_app_cnt}")
        print(f"Attachments: {attachment_cnt}")
        # self.stdout.write(self.style.SUCCESS("jee hyvinhän se meni!"))
