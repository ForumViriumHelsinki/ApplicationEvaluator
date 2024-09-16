# Create management command to import challenge texts gathered from a web page to Django
import json

from django.core.management.base import BaseCommand

from application_evaluator.models import ApplicationRound, CriterionGroup, Criterion

criteria_abbr_map = {
    "Impact": "IMP",
    "Implementation quality and efficiency": "IQE",
    "Excellence": "EXC",
    "Co-creation": "Co-C",
    "Technology": "TEC",
}


def create_challenge_and_criterion(challenge: dict) -> ApplicationRound:
    """
    Create ApplicationRound and CriterionGroup and Criterion objects from challenge dict,
    which looks like this:

    challenge =   {
        "city": "Aarhus",
        "organisation": "",
        "sequence": 1,
        "title": "How can youth interaction with public authorities be more inclusive?",
        "description": "Despite being labeled as \"digital natives,\" many young ...",
        "scores": {
          "Impact": [ 3.0, 25 ],
          "Implementation quality and efficiency": [ 2.0, 15 ],
          "Excellence": [ 2.0, 20 ],
          "Co-creation": [ 3.0, 30 ],
          "Technology": [ 2.0, 10 ]
        },
        "id": "CC-301"
    }

    ApplicationRound objects are created as follows:
    - name is generated from identifier and challenge["title"], max length 128
      --> f'challenge["id"]: challenge["title"]'[0:128]
    - description is challenge["description"]

    All objects are created using get_or_create() method, so that existing objects are not duplicated.
    """
    # Create ApplicationRound
    long_ar_name = f"{challenge['id']}: {challenge['title']}"
    ar_name = long_ar_name[:128]
    # try to get existing ApplicationRound using long_ar_name
    created = False
    try:
        ar = ApplicationRound.objects.get(name=long_ar_name)
    except ApplicationRound.DoesNotExist:  # Then with ar_name
        try:
            ar = ApplicationRound.objects.get(name=ar_name)
            ar.name = long_ar_name
            print(f"name changed: {ar_name} -> {long_ar_name}")
            ar.save()
        except ApplicationRound.DoesNotExist:  # create new ApplicationRound with long_ar_name
            ar = ApplicationRound.objects.create(name=long_ar_name, description=challenge["description"])
            created = True
    if not ar.city:
        ar.city = challenge["city"]
        ar.save()
    # ar, created = ApplicationRound.objects.get_or_create(name=ar_name, description=challenge["text"])
    print(ar, created)
    # Create CriterionGroup and Criterion objects
    for i, score_name in enumerate(challenge["scores"], start=1):
        score = challenge["scores"][score_name]
        # Create CriterionGroup
        cg, created = CriterionGroup.objects.get_or_create(
            name=score_name,
            order=i,
            application_round=ar,
            threshold=score[0],
            abbr=criteria_abbr_map[score_name],
        )
        print(cg, created)
        # Create Criterion
        c, created = Criterion.objects.get_or_create(
            name=score_name,
            order=i,
            group=cg,
            application_round=ar,
            weight=score[1],
        )
        print(c, created)
    return ar


class Command(BaseCommand):
    help = "Import data from web page extract json file to Django"

    def add_arguments(self, parser):
        parser.add_argument("--filename", type=str, required=True)

    def handle(self, *args, **options):
        with open(options["filename"], "r") as f:
            challenges = json.load(f)
        for c in challenges:
            create_challenge_and_criterion(c)
        self.stdout.write(self.style.SUCCESS("{} challenges imported".format(len(challenges))))
