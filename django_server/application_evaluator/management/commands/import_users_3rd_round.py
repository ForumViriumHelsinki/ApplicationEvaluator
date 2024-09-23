# Create management command to import challenge texts gathered from a web page to Django

import openpyxl
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from application_evaluator.models import ApplicationRound


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


def merge_duplicate_users(users: list) -> list:
    """
    Merge duplicate users from Podio export. Example user dict:

    user = {
        "Challenge": "Cityname: How to do foo bar?",
        "Created by": "CommuniCity podio app",
        "Created on": datetime.datetime(2023, 10, 30, 9, 48, 13),
        "Data security policy": "I have read the data security policy...",
        "E-mail": "user@example.com",
        "Evaluation criteria": "Impact; Excellence; Implementation; Co-creation",
        "First name": "User",
        "Last name": "Name",
        "Organization": None,
        "Tags": None,
    }

    There can be the same user, but with different challenge name. In this case, we want to merge the user data
    and add the challenge name to the list of challenges.
    """

    # Create a dict with email as key and list of user dicts as value
    user_dict = {}
    for user in users:
        # Remove obsolete keys ['Created on', 'Created by',  'Organization', 'Data security policy', 'Tags']
        for k in ["Created on", "Created by", "Organization", "Data security policy", "Tags"]:
            if k in user:
                del user[k]
        email = user["E-mail"]
        challenge = [user["Challenge"], user["Evaluation criteria"]]
        if email not in user_dict:
            user_dict[email] = user
            user_dict[email]["Challenge"] = [challenge]
        else:
            user_dict[email]["Challenge"].append(challenge)
    return list(user_dict.values())


class Command(BaseCommand):
    help = "Import user data from Podio excel file to Django"

    def add_arguments(self, parser):
        parser.add_argument("--filename", type=str, required=True)
        parser.add_argument("--dry-run", action="store_true", help="Don't save to database")
        parser.add_argument("--only-new", action="store_true", help="Only create new users")

    def handle(self, *args, **options):
        users = read_excel_sheet(options["filename"])
        new_users = merge_duplicate_users(users)
        # Do everything in a transaction
        for u in new_users:
            u["ApplicationRounds"] = []
            for c in u["Challenge"]:
                name, criteria = c
                # split challenge name to city and title using ':'
                city, title = [x.strip() for x in name.split(":")]
                # create qset for filtering ApplicationRounds where name contains all words
                ars = ApplicationRound.objects.filter(name__startswith="CC-3")
                ars = ars.filter(name__contains=title)
                if len(ars) != 1:
                    print(f"ApplicationRound not found for {c}")
                    print(f"Title: {title}")
                    print(ars.query)
                    exit()
                else:
                    u["ApplicationRounds"].append(ars.first())
        with transaction.atomic():
            # Create users
            for u in new_users:
                # Replace get_or_create with equivalent try/except
                try:
                    user = User.objects.get(username=u["E-mail"].lower())
                    created = False
                    if options["only_new"]:  # If only_new, skip existing users
                        continue
                except User.DoesNotExist:
                    user = User.objects.create(username=u["E-mail"].lower())
                    created = True
                    # Set first_name and last_name only if user is created
                    user.first_name = u["First name"]
                    user.last_name = u["Last name"]
                    user.email = u["E-mail"].lower()
                    # Set random password
                    user.set_password(User.objects.make_random_password())
                    user.save()
                # Add ApplicationRounds to user
                for ar in u["ApplicationRounds"]:
                    ar.evaluators.add(user)
                print("{}, new: {}".format(user, created))
                for c in u["Challenge"]:
                    # replace all words (Impact; Excellence; Implementation; Co-creation)
                    # with abbreviations IMP EXC IQE Co-C
                    cri = (
                        c[1]
                        .replace("Impact", "IMP")
                        .replace("Excellence", "EXC")
                        .replace("Implementation", "IQE")
                        .replace("Co-creation", "Co-C")
                    )
                    print(f"  {c[0][:60]} ({cri})")
            # Rollback transaction if dry-run
            if options["dry_run"]:
                transaction.set_rollback(True)
                print("Dry-run, rolling back transaction")
