# Create management command to add criteria to application rounds

from django.core.management.base import BaseCommand
from django.db.models import Q

from application_evaluator.models import ApplicationRound, CriterionGroup, Criterion

# This is just for testing purposes
criteria_json = [
    {
        "criterion_group": {"name": "Functional criteria", "weighting": "40%"},
        "criteria": [
            {"name": "Enabling dynamic management of public areas", "abbr": "EDMA", "max_points": 25, "threshold": 13},
            {"name": "Use of space data", "abbr": "USDa", "max_points": 30, "threshold": 15},
            {"name": "Interoperability", "abbr": "Inte", "max_points": 20, "threshold": 10},
            {"name": "Data Security & Privacy", "abbr": "DSec", "max_points": 15, "threshold": 7},
        ],
    },
    {
        "criterion_group": {"name": "Non-functional criteria", "weighting": "20%"},
        "criteria": [
            {"name": "Innovativeness", "abbr": "Inno", "max_points": 70, "threshold": 35},
            {"name": "Impacts on city and citizens", "abbr": "IoCC", "max_points": 30, "threshold": 15},
        ],
    },
    {
        "criterion_group": {"name": "Project management criteria", "weighting": "20%"},
        "criteria": [
            {"name": "Project management plan", "abbr": "PMPl", "max_points": 50, "threshold": 25},
            {"name": "Composition of the project team", "abbr": "CPro", "max_points": 50, "threshold": 25},
        ],
    },
    {
        "criterion_group": {"name": "Commercial feasibility", "weighting": "10%"},
        "criteria": [
            {
                "name": "Replication & implementation across multiple cities",
                "abbr": "RImp",
                "max_points": 60,
                "threshold": 30,
            },
            {"name": "Business model", "abbr": "Busi", "max_points": 40, "threshold": 20},
        ],
    },
    {
        "criterion_group": {"name": "Price", "weighting": "10%"},
        "criteria": [
            {
                "name": "Binding contract price for carrying out the work in Phase 1",
                "abbr": "BCon",
                "max_points": 30,
                "threshold": 15,
            },
            {
                "name": "indicative price for the work in all 3 PCP phases (total price)",
                "abbr": "IPri",
                "max_points": 70,
                "threshold": 35,
            },
        ],
    },
]


def setup_criterion_groups_and_criteria(application_rounds, criteria_json):
    """
    Sets up criterion groups and criteria for given application rounds based on JSON configuration.

    Args:
        application_rounds: List of ApplicationRound objects
        criteria_json: List of dictionaries containing criterion group and criteria configurations
    """
    for application_round in application_rounds:
        # Track order for groups and criteria
        group_order = 0

        for group_data in criteria_json:
            group_info = group_data["criterion_group"]
            criteria_list = group_data["criteria"]

            # Convert percentage string to float (e.g., "40%" -> 0.4)
            weighting = float(group_info["weighting"].strip("%")) / 100

            # Create or get criterion group
            criterion_group, created = CriterionGroup.objects.get_or_create(
                application_round=application_round,
                name=group_info["name"],
                defaults={
                    "order": group_order,
                    "abbr": group_info["name"][:8],  # Use first 8 chars as abbreviation if not provided
                },
            )

            # Update the group order even if it already existed
            criterion_group.order = group_order
            criterion_group.save()

            # Calculate total max points for this group
            total_max_points = sum(criterion["max_points"] for criterion in criteria_list)

            # Create or update criteria
            for criterion_order, criterion_data in enumerate(criteria_list):
                # Calculate the weighted value for this criterion
                criterion_weight = (criterion_data["max_points"] / total_max_points) * weighting

                # Modify the name to include max points
                criterion_name = f"{criterion_data['name']} [max {criterion_data['max_points']}]"

                criterion, created = Criterion.objects.get_or_create(
                    application_round=application_round,
                    name=criterion_name,  # Using modified name here
                    group=criterion_group,
                    defaults={"order": criterion_order, "weight": criterion_weight, "public": True},
                )

                # Update values even if criterion already existed
                criterion.order = criterion_order
                criterion.weight = criterion_weight
                criterion.save()

            group_order += 1


class Command(BaseCommand):
    help = "Create criterion groups and criteria for given application rounds"

    def add_arguments(self, parser):
        parser.add_argument("--application-rounds", nargs="+", type=str)

    def handle(self, *args, **options):
        # Create Q objects for each application round name prefix
        q_objects = Q()
        for ar_name in options["application_rounds"]:
            q_objects |= Q(name__startswith=ar_name)

        # Search for application rounds matching any of the name prefixes
        ars = ApplicationRound.objects.filter(q_objects)

        if not ars.exists():
            self.stdout.write(self.style.WARNING("No matching application rounds found"))
            return
        setup_criterion_groups_and_criteria(ars, criteria_json)

        self.stdout.write(self.style.SUCCESS(f"Successfully imported criteria for {ars.count()} application round(s)"))
