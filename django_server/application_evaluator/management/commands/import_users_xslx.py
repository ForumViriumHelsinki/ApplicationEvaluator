# Create management command to import challenge texts gathered from a web page to Django
import re

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

# import excel module
import openpyxl


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
        if email not in user_dict:
            user_dict[email] = user
            user_dict[email]["Challenge"] = [user_dict[email]["Challenge"]]
        else:
            if user["Challenge"] not in user_dict[email]["Challenge"]:
                user_dict[email]["Challenge"].append(user["Challenge"])

    return list(user_dict.values())


x = [
    "CC-201: How can technology ease the process of setting up a bank account for foreigners",
    "CC-202: How to support parents in online (sex)education and safety",
    "CC-203: How to ensure accessible acceptance of a local payment system among "
    "residents and local entrepreneurs in Amsterdam Nieuw",
    "CC-204: How to encourage girls in Nieuw-West to take part in sports and " "exercise",
    "CC-205: How to involve residents in a community savings and credit "
    "cooperative that supports social initiatives in the city",
    "CC-206: How to include deaf and hearing impaired in broadcasting information on public transport",
    "CC-207: How to adapt an existing technological solution for a specific group",
    "CC-208: How to strengthen the broad, positive health of youth through attractive and playful technology",
    "CC-209: How can resilient role models help families to develop healthy relationships",
    "CC-210: Wildcard – Propose any technological solution which contributes to a "
    "breakthrough in intergenerational problems\t0\t0\tFalse",
    "CC-211: How to reliably measure the digital skills of long-term unemployed citizens",
    "CC-212: How to support the recognition of competence with help of a digital tool",
    "CC-213: How to prevent pressure ulcers of wheelchair patients",
    "CC-214: How to enhance the quality of life and foster inclusion for citizens "
    "with severe disabilities through digital innovation",
    "CC-215: How to collect and generate accessible pedestrian route information "
    "through participatory data collection methods",
    "CC-216: How to utilise existing data and data sources for activating " "digitally hard-to-reach residents",
    "CC-217: How to reduce school absenteeism through an innovative and inclusive " "educational solution",
    "CC-218: How to improve the thermal comfort and overall health in residential "
    "buildings, focusing on passive strategies",
    "CC-219: How to engage the citizens from socially and economically "
    "disconnected localities in participatory planning",
    "CC-220: How to better inform the public with limited access to digital tools " "about urban data analysis",
]


class Command(BaseCommand):
    help = "Import user data from Podio excel file to Django"

    def add_arguments(self, parser):
        parser.add_argument("--filename", type=str, required=True)

    def handle(self, *args, **options):
        users = read_excel_sheet(options["filename"])
        new_users = merge_duplicate_users(users)
        # for u in users:
        #     pprint(u)
        #     break
        for u in new_users:
            # pprint(u)
            u["ApplicationRounds"] = []
            for c in u["Challenge"]:
                # if "Breda" not in c:
                #     continue
                # split challenge name to city and title using ':'
                city, title = [x.strip() for x in c.split(":")]
                # Search for ApplicationRounds with name containing title's first 4 words
                # Pick 4 first words from title:
                words = title.split(" ")
                # remove all words shorter than 3 characters
                words = [w for w in words if len(w) >= 3][:4]

                # create qset for filtering ApplicationRounds where name contains all words
                ars = ApplicationRound.objects.filter(name__startswith="CC-2")
                for w in words:
                    ars = ars.filter(name__icontains=w)
                # ars = ApplicationRound.objects.filter(name__contains=title.strip("?")[:20])
                # print(ars)

                if len(ars) != 1:
                    print(f"ApplicationRound not found for {c}")
                    print(f"Words: {words}")
                    print(ars.query)
                    exit()
                else:
                    u["ApplicationRounds"].append(ars[0])

                # print(city, title, ars)
            name, domain = u["E-mail"].lower().split("@")
            name = re.sub(r"[aeiouAEIOU]", "y", name)
            name = re.sub(r"[bcdfghjklmnpqrstvxz]", "x", name)
            # korvaa vokaalit y-kirjaimella ja konsonantit x:llä
            # name = re.sub(r"[aeiouy]", "y", name, re.IGNORECASE)
            # name = re.sub(r"[bcdfghjklmnpqrstvxz.]", "x", name, re.IGNORECASE)

            print(f"@{domain}", len(u["ApplicationRounds"]))
            # if u["E-mail"] == "gd.hollander@breda.nl":
            #     pprint(u)
            #     exit()
            # break
        # self.stdout.write(self.style.SUCCESS("{} challenges imported".format(len(challenges))))
        # pprint(new_users)
        # Create users
        for u in new_users:
            user, created = User.objects.get_or_create(username=u["E-mail"].lower())
            if created:  # Set first_name and last_name only if user is created
                user.first_name = u["First name"]
                user.last_name = u["Last name"]
                # Set random password
                user.set_password(User.objects.make_random_password())
            # Add ApplicationRounds to user
            for ar in u["ApplicationRounds"]:
                ar.evaluators.add(user)
                print(ar.evaluators.all())
            user.save()
            print(user, created)
            exit()
