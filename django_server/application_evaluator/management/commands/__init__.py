from django.db import connection

from application_evaluator.models import Application


def sort_groups(groups):
    desired_order = ["IMP", "IQE", "EXC", "Co-C", "TEC"]
    return dict(
        sorted(
            groups.items(),
            key=lambda x: desired_order.index(x[1]["abbr"]) if x[1]["abbr"] in desired_order else len(desired_order),
        )
    )


def print_evaluation_table(application_id, print_output=True):
    """
    Prints evaluation table for given application showing scores by evaluators and criteria.
    Returns False if any group average is below threshold.
    """
    output = []

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
    output.append(f"\nEvaluation Table: {app.name}")
    output.append("-" * 80)

    header = "Evaluator"
    for group_id, group in groups.items():
        header += f"\t{group['abbr']}"
    output.append(header)
    output.append("-" * 80)
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

        output.append(line)

    output.append("-" * 80)
    total_line = "Total".ljust(24)
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

        total_line += f"\t{weighted_avg:.3f}{threshold_marker}"
    output.append(total_line)
    output.append("-" * 80)
    if print_output:
        print("\n".join(output))
    return not has_below_threshold
