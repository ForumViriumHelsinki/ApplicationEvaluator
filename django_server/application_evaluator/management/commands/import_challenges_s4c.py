# Create management command to add criteria to application rounds

import json

import pandas as pd
from django.core.management.base import BaseCommand
from django.db.models import Q

from application_evaluator.models import ApplicationRound, Criterion, CriterionGroup

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


def create_criteria_hierarchy(criteria_list):
    """
    Converts flat criteria list to hierarchical structure.

    Args:
        criteria_list: List of dictionaries containing criteria definitions from Excel

    Returns:
        List of dictionaries with hierarchical structure of criterion groups, subgroups and criteria
    """
    result = []
    current_group = None
    current_subgroup = None

    for item in criteria_list:
        # New main group
        if item["Criterion group"]:
            if current_group:
                result.append(current_group)
            current_group = {"criterion_group": {"name": item["Criterion group"]}, "subgroups": []}
            current_subgroup = None

        # New subgroup
        elif item["Criterion subgroup"]:
            if current_group is None:
                raise ValueError("Subgroup found without a main group")

            current_subgroup = {
                "name": item["Criterion subgroup"],
                "abbr": item["abbr"] if item["abbr"] else item["Criterion subgroup"],
                "max_points": item["Weight / max score"],
                "threshold": item["Threshold"],
                "criteria": [],
            }
            current_group["subgroups"].append(current_subgroup)

        # New criterion
        elif item["Criterion"]:
            if current_group is None:
                raise ValueError("Criterion found without a group")

            criterion = {
                "name": f"{item['Criterion']}: {item['Short name']}",
                "abbr": item["abbr"] if item["abbr"] else item["Criterion"],
                "weight": item["Weight / max score"],
            }

            # Add to subgroup if exists, otherwise directly to group
            if current_subgroup:
                current_subgroup["criteria"].append(criterion)
            else:
                if "criteria" not in current_group:
                    current_group["criteria"] = []
                current_group["criteria"].append(criterion)

    # Add last group
    if current_group:
        result.append(current_group)

    return result


def read_criteria_from_xlsx(file_path):
    """
    Reads criteria from an Excel file and returns a list of dictionaries.

    Args:
        file_path: Path to the Excel file containing criteria definitions
    """
    # Lue Excel-tiedoston toinen välilehti DataFrameen ja valitse vain tarvittavat sarakkeet
    df = pd.read_excel(
        file_path,
        sheet_name=3,
        usecols=[
            "Criterion group",
            "Criterion subgroup",
            "Criterion",
            "abbr",
            "Short name",
            "Weight / max score",
            "Threshold",
        ],
    )
    # Drop all rows where all values are NaN
    df = df.dropna(how="all")
    # replace NaN-values with None
    df = df.replace({pd.NA: None, pd.NaT: None, float("nan"): None})
    criteria_list = df.to_dict(orient="records")

    # Convert flat list to hierarchical structure
    criteria_json_new = create_criteria_hierarchy(criteria_list)

    # Save to file for debugging/reference
    criteria_json = json.dumps(criteria_json_new, indent=2)
    with open("criteria.json", "w", encoding="utf-8") as f:
        f.write(criteria_json)
    return criteria_json_new


def setup_criterion_groups_and_criteria(application_rounds, criteria_json):
    """
    Sets up criterion groups and criteria for given application rounds based on JSON configuration.
    Creates a hierarchy of CriterionGroups (main groups and subgroups) and their Criteria.

    Args:
        application_rounds: List of ApplicationRound objects
        criteria_json: List of dictionaries containing criterion group and criteria configurations
    """
    for application_round in application_rounds:
        # Track order for main groups
        group_order = 1

        for group_data in criteria_json:
            group_info = group_data["criterion_group"]

            # Create main criterion group
            main_group, _ = CriterionGroup.objects.get_or_create(
                application_round=application_round,
                name=group_info["name"],
                defaults={
                    "order": group_order,
                    "abbr": group_info["name"][:8],  # Use first 8 chars as abbreviation if not provided
                },
            )
            main_group.order = group_order
            main_group.save()
            group_order += 1

            # Handle subgroups if they exist
            if "subgroups" in group_data and group_data["subgroups"]:
                for subgroup_data in group_data["subgroups"]:
                    # Create subgroup
                    subgroup, _ = CriterionGroup.objects.get_or_create(
                        application_round=application_round,
                        name=subgroup_data["name"],
                        parent=main_group,
                        defaults={
                            "order": group_order,
                            "abbr": subgroup_data["abbr"],
                        },
                    )
                    subgroup.order = group_order
                    subgroup.save()
                    group_order += 1
                    # Create criteria for subgroup
                    criterion_order = 0
                    for criterion_data in subgroup_data["criteria"]:
                        criterion, _ = Criterion.objects.get_or_create(
                            application_round=application_round,
                            name=criterion_data["name"],
                            group=subgroup,
                            defaults={
                                "order": criterion_order,
                                "weight": criterion_data["weight"],
                                # "abbr": criterion_data["abbr"],
                                "public": True,
                            },
                        )
                        criterion.order = criterion_order
                        criterion.weight = criterion_data["weight"]
                        criterion.save()
                        criterion_order += 1

            # Handle direct criteria of main group if they exist
            elif "criteria" in group_data:
                criterion_order = 0
                for criterion_data in group_data["criteria"]:
                    criterion, _ = Criterion.objects.get_or_create(
                        application_round=application_round,
                        name=criterion_data["name"],
                        group=main_group,
                        defaults={
                            "order": criterion_order,
                            "weight": criterion_data["weight"],
                            # "abbr": criterion_data["abbr"],
                            "public": True,
                        },
                    )
                    criterion.order = criterion_order
                    criterion.weight = criterion_data["weight"]
                    criterion.save()
                    criterion_order += 1


class Command(BaseCommand):
    help = "Create criterion groups and criteria for given application rounds"

    def add_arguments(self, parser):
        parser.add_argument(
            "--criteria-xlsx", type=str, required=True, help="Path to Excel file containing criteria definitions"
        )
        parser.add_argument("--application-rounds", required=True, nargs="+", type=str)

    def handle(self, *args, **options):
        criteria_list = read_criteria_from_xlsx(options["criteria_xlsx"])
        # Create Q objects for each application round name prefix
        q_objects = Q()
        for ar_name in options["application_rounds"]:
            q_objects |= Q(name__startswith=ar_name)

        # Search for application rounds matching any of the name prefixes
        ars = ApplicationRound.objects.filter(q_objects)

        if not ars.exists():
            self.stdout.write(self.style.WARNING("No matching application rounds found"))
            return
        setup_criterion_groups_and_criteria(ars, criteria_list)

        self.stdout.write(self.style.SUCCESS(f"Successfully imported criteria for {ars.count()} application round(s)"))
