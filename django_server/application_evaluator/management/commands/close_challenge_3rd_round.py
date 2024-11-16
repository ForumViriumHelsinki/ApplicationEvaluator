# Create management command to move a challenge to tech evaluation or close challenge evaluation round
import pathlib
from datetime import datetime

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from application_evaluator.models import ApplicationRound

LOG_DIR = "close_logs"


def move_to_tech_evaluation(ar, options):
    log = [f"ApplicationRound: {ar.name}"]
    # Add current evaluators' email addresses to log
    for evaluator in ar.evaluators.all():
        log.append(f"Removed: {evaluator.first_name} {evaluator.last_name} <{evaluator.email}>")
    # Remove all existing Evaluators from the ApplicationRound
    ar.evaluators.clear()
    # Check that ApplicationRound has at least 1 Application with visibility=1
    visible_apps = ar.applications.filter(visibility=1)
    if visible_apps.exists():
        log.append("ApplicationRound has visible applications:")
        for app in visible_apps:
            log.append(f"  {app.id}: {app.name}")
            # Remove tech evaluation comments and scores
            comments = app.comments.filter(criterion_group__abbr="TEC")
            for c in comments:
                # Replace all possible newlines (\n \r) with spaces
                c_text = c.comment.replace("\n", " ").replace("\r", " ")
                log.append(f"    Removed: {c} {c_text}")
                c.delete()
            scores = app.scores.filter(criterion__name="Technology")
            for s in scores:
                log.append(f"    Removed: {s}")
                s.delete()

    else:
        log.append("ApplicationRound has no visible applications")
        return log
    # Check that there is CriterionGroup for tech evaluation, abbr=TEC
    has_tech = ar.criterion_groups.filter(abbr="TEC").exists()
    if has_tech:
        log.append("ApplicationRound has Tech evaluation criterion group")
        # Test if tech evaluator exists:
        try:
            tech_evaluator = User.objects.get(username=options["tech_email"])
        except User.DoesNotExist:
            log.append("Tech evaluator not found")
            tech_evaluator = None
        print(tech_evaluator)
        if not tech_evaluator:
            if options["create_user"]:
                tech_evaluator = User.objects.create_user(username=options["tech_email"], email=options["tech_email"])
                # Set username to email address
                log.append(f"Created new tech evaluator: {tech_evaluator.email}")
            else:
                log.append("Tech evaluator not created")
                return log
        ar.evaluators.add(tech_evaluator)
        log.append(f"Added tech evaluator to ApplicationRound: {tech_evaluator.email}")
    else:
        log.append("ApplicationRound has no Tech evaluation criterion group")
    return log


class Command(BaseCommand):
    help = "Import data from web page extract json file to Django"

    def add_arguments(self, parser):
        parser.add_argument("--application-round", type=str, required=True, help="Application round search string")
        parser.add_argument("--move-to-tech-evaluation", action="store_true", help="Move to tech evaluation")
        parser.add_argument("--tech-email", type=str, required=True, help="Tech evaluator's email address")
        parser.add_argument("--create-user", action="store_true", help="Create tech user if not found")
        parser.add_argument("--close", action="store_true", help="Move to tech evaluation")
        parser.add_argument("--dry-run", action="store_true", help="Don't save changes to database")

    def handle(self, *args, **options):
        # use pathlib to create log directory, if it doesn't exist
        pathlib.Path(LOG_DIR).mkdir(parents=True, exist_ok=True)
        # Create log file from name until ':' and current datetime

        log_file = "{}-{}.txt".format(options["application_round"].split(":")[0], datetime.now().isoformat())
        log_file = pathlib.Path(LOG_DIR) / pathlib.Path(log_file)
        ar = ApplicationRound.objects.get(name__contains=options["application_round"])
        with transaction.atomic():
            if options["move_to_tech_evaluation"]:
                if options["tech_email"]:
                    log = move_to_tech_evaluation(ar, options)
                    self.stdout.write(self.style.SUCCESS("Moved to tech evaluation: {}".format(ar.name)))
                else:
                    self.stdout.write(self.style.ERROR("Tech evaluator email is required"))
                    exit(1)
            if options["dry_run"]:
                transaction.set_rollback(True)
                log.append("Dry-run, rolling back transaction")
        log.append("")
        with open(log_file, "w") as f:
            f.write("\n".join(log))
        print("\n".join(log))
