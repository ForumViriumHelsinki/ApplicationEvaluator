# Create management command to move a challenge to tech evaluation or close challenge evaluation round
import pathlib
from datetime import datetime

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from application_evaluator.models import ApplicationRound, Application

LOG_DIR = "close_logs"


def sort_groups(groups):
    desired_order = ["IMP", "IQE", "EXC", "Co-C", "TEC"]
    return dict(
        sorted(
            groups.items(),
            key=lambda x: desired_order.index(x[1]["abbr"]) if x[1]["abbr"] in desired_order else len(desired_order),
        )
    )


def print_evaluation_table(application_id):
    """
    Prints evaluation table for given application showing scores by evaluators and criteria.
    Returns False if any group average is below threshold.
    """
    from django.db import connection

    query = """
    WITH evaluator_scores AS (
        SELECT
            au.first_name || ' ' || au.last_name as evaluator_name,
            cg.abbr as group_abbr,
            cg.threshold,
            c.name as criterion_name,
            c.weight,
            s.score,
            c.id as criterion_id,
            cg.id as group_id
        FROM application_evaluator_score s
        JOIN auth_user au ON s.evaluator_id = au.id
        JOIN application_evaluator_criterion c ON s.criterion_id = c.id
        JOIN application_evaluator_criteriongroup cg ON c.group_id = cg.id
        WHERE s.application_id = %s
        ORDER BY au.first_name, cg.abbr, c.name
    )
    SELECT * FROM evaluator_scores
    """

    with connection.cursor() as cursor:
        cursor.execute(query, [application_id])
        rows = cursor.fetchall()

    if not rows:
        return True

    evaluators = {}
    groups = {}
    criteria_by_group = {}
    has_below_threshold = False

    for row in rows:
        evaluator_name, group_abbr, threshold, criterion_name, weight, score, criterion_id, group_id = row

        if group_id not in groups:
            groups[group_id] = {"abbr": group_abbr, "threshold": threshold}
            criteria_by_group[group_id] = set()

        criteria_by_group[group_id].add(criterion_id)

        if evaluator_name not in evaluators:
            evaluators[evaluator_name] = {}

        if criterion_id not in evaluators[evaluator_name]:
            evaluators[evaluator_name][criterion_id] = {"score": score, "group_id": group_id, "weight": weight}
    app = Application.objects.get(id=application_id)
    print("\nEvaluation Table: ", app.name)
    print("-" * 80)

    header = "Evaluator"
    for group_id, group in groups.items():
        header += f"\t{group['abbr']}"
    print(header)
    print("-" * 80)
    groups = sort_groups(groups)
    for evaluator_name, scores in evaluators.items():
        line = evaluator_name[:24].ljust(24)
        for group_id, group in groups.items():
            group_scores = [scores.get(crit_id, {"score": 0, "weight": 0}) for crit_id in criteria_by_group[group_id]]

            total_weight = sum(score["weight"] for score in group_scores)
            if total_weight > 0:
                weighted_avg = sum(score["score"] * score["weight"] for score in group_scores) / total_weight
            else:
                weighted_avg = 0

            threshold_marker = "!" if weighted_avg < group["threshold"] else ""
            line += f"\t{weighted_avg:.3f}{threshold_marker}"

        print(line)

    print("-" * 80)
    print("Total".ljust(24), end="")
    for group_id, group in groups.items():
        all_group_scores = []
        total_weight = 0

        for evaluator_scores in evaluators.values():
            for crit_id in criteria_by_group[group_id]:
                if crit_id in evaluator_scores:
                    score_data = evaluator_scores[crit_id]
                    all_group_scores.append({"score": score_data["score"], "weight": score_data["weight"]})
                    total_weight += score_data["weight"]

        if total_weight > 0:
            weighted_avg = sum(score["score"] * score["weight"] for score in all_group_scores) / total_weight
        else:
            weighted_avg = 0

        if weighted_avg < group["threshold"]:
            has_below_threshold = True
            threshold_marker = "!"
        else:
            threshold_marker = ""

        print(f"\t{weighted_avg:.3f}{threshold_marker}", end="")
    print()
    print("-" * 80)

    return not has_below_threshold


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
            will_proceed = print_evaluation_table(app.id)
            log.append(f"  {app.id}: {app.name} ({app.visibility}) {will_proceed}")
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
            will_proceed = print_evaluation_table(app.id)
            if will_proceed is False:
                app.visibility = 0
                app.save()
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
