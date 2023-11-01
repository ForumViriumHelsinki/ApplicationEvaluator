# Create management command to import challenge texts gathered from a web page to Django
import re

from django.core.management.base import BaseCommand

from application_evaluator.models import ApplicationRound, CriterionGroup, Criterion

criteria_abbr_map = {
    "Impact": "IMP",
    "Implementation quality and efficiency": "IQE",
    "Excellence": "EXC",
    "Co-creation": "Co-C",
}


def get_ccs(text: str):
    # Find all matches in the document, === is manually added separator
    cc_pattern = r"(.+?) Challenge (\d+): (.*?)=========="
    matches = re.findall(cc_pattern, text, re.DOTALL | re.MULTILINE)
    return matches


def get_scores(text: str):
    # Find all score matches in the document
    score_pattern = r"(\d+)\. (.*?)\nMinimum score: ([\d.]+) \| Weighting: (\d+)%"
    matches = re.findall(score_pattern, text, re.DOTALL | re.MULTILINE)
    return matches


def read_text_file(filename: str) -> list:
    """Read text file, return a list of dicts."""
    challenges = []
    with open(filename, "r") as f:
        document_text = f.read()
    matches = get_ccs(document_text)
    for match in matches:
        text, scoring = match[2].split("Minimum scores and weightenings:")
        text_lines = text.splitlines()
        title = text_lines.pop(0)
        text = "\n".join(text_lines)
        c = {
            "city": match[0].strip(),
            "order": match[1].strip(),
            "title": title,
            "text": text,
            "scores": get_scores(scoring),
        }
        challenges.append(c)
    return challenges


def create_challenge_and_criterion(identifier: str, challenge: dict) -> ApplicationRound:
    """
    Create ApplicationRound and CriterionGroup and Criterion objects from challenge dict, which looks like this:

    challenge = {
        "city": "Turku",
        "order": "1",
        "scores": [
            ("1", "Impact", "3", "30"),
            ("2", "Implementation quality and efficiency", "3", "25"),
            ("3", "Excellence", "2", "25"),
            ("4", "Co-creation", "2", "20"),
        ],
        "text": "International employees relocating lorem ipsum " "Development.\n",
        "title": "Lorem ipsum foo bar?",
    }

    ApplicationRound objects are created as follows:
    - name is generated from identifier and challenge["title"]
    - description is challenge["text"]

    CriterionGroup and Criterion objects are created as follows:
    - CriterionGroup has fields name from score[1], order from score[0], application_round is ApplicationRound,
     threshold from score[2], abbr from criteria_abbr_map[score[1]]
    - Criterion has fields name from score[1], order from score[0], group is CriterionGroup, application_round is
      ApplicationRound, weight from score[3]

    All objects are created using get_or_create() method, so that existing objects are not duplicated.
    """
    # Create ApplicationRound
    long_ar_name = f"{identifier}: {challenge['title']}"
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
            ar = ApplicationRound.objects.create(name=long_ar_name, description=challenge["text"])
            created = True
    if not ar.city:
        ar.city = challenge["city"]
        ar.save()
    # ar, created = ApplicationRound.objects.get_or_create(name=ar_name, description=challenge["text"])
    print(ar, created)
    # Create CriterionGroup and Criterion objects
    for score in challenge["scores"]:
        # Create CriterionGroup
        cg, created = CriterionGroup.objects.get_or_create(
            name=score[1],
            order=score[0],
            application_round=ar,
            threshold=score[2],
            abbr=criteria_abbr_map[score[1]],
        )
        print(cg, created)
        # Create Criterion
        c, created = Criterion.objects.get_or_create(
            name=score[1],
            order=score[0],
            group=cg,
            application_round=ar,
            weight=score[3],
        )
        print(c, created)
    return ar


class Command(BaseCommand):
    help = "Import data from Podio excel file to Django"

    def add_arguments(self, parser):
        parser.add_argument("--filename", type=str, required=True)

    def handle(self, *args, **options):
        start_identifier = 201
        challenges = read_text_file(options["filename"])
        for c in challenges:
            identifier = f"CC-{start_identifier}"
            create_challenge_and_criterion(identifier, c)
            start_identifier += 1
        self.stdout.write(self.style.SUCCESS("{} challenges imported".format(len(challenges))))
