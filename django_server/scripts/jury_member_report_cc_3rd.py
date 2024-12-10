import pandas as pd
import argparse
import re
import logging
from collections import Counter

"""
Analyze Excel files for Challenges and Jury members.
This is intended to be used for the CommuniCity 3rd round only.

Jury Excel file format:
Challenge	            string, "<city>[ / <organisation>]: <challenge text> e.g. "Utrecht / HKU: How can...?"
Evaluation criteria	    ';' separated list of strings
First name	            string
Last name	            string
Organisation	        string
E-mail	                email address
Data security policy	string
Submit date and time    empty
"""


def parse_args():
    parser = argparse.ArgumentParser(description="Analyze Excel files for Challenges and Jury members")
    parser.add_argument("--jury-excel", required=True, help="Path to the jury Excel file")
    parser.add_argument("--challenge-excel", required=True, help="Path to the challenge Excel file")
    parser.add_argument("--city", nargs="*", help="City name")
    parser.add_argument("--list-emails", action="store_true", help="List all unique email addresses")
    parser.add_argument("--pilot-managers", action="store_true", help="List all pilot managers")
    # no pilot manager argument
    parser.add_argument(
        "--no-pilot-manager",
        action="store_true",
        help="List the challenges without pilot managers",
    )
    # Multiple pilot managers argument
    parser.add_argument(
        "--multiple-pilot-managers",
        action="store_true",
        help="List the challenges with multiple pilot managers",
    )
    parser.add_argument("--list-duplicates", action="store_true", help="List duplicate jury members")
    parser.add_argument(
        "--list-challenges",
        action="store_true",
        help="List all challenges and their jury members",
    )
    # Log level
    parser.add_argument("--log", default="INFO", help="Log level")
    args = parser.parse_args()
    # Set log level
    logging.basicConfig(level=args.log)
    return args


def read_and_clean_jury_excel(filename: str, sort_by: str = None) -> pd.DataFrame:
    # Read the Excel file
    df = pd.read_excel(filename)
    # Drop unnecessary columns
    df = df[["Challenge", "Evaluation criteria", "E-mail", "First name", "Last name"]]

    # Drop duplicates and log the number of dropped rows
    initial_rows = len(df)
    df = df.drop_duplicates()
    dropped_rows = initial_rows - len(df)
    if dropped_rows > 0:
        logging.info(f"Dropped {dropped_rows} duplicate rows")

    if sort_by:
        df = df.sort_values(sort_by)

    return df


def jury_member_report_excel(filename, cities: list[str]) -> list:
    df = read_and_clean_jury_excel(filename)

    # Filter by city string, which is in the start of the string
    # There can be multiple cities, so we need to filter by each city
    if cities:
        # Create a regex pattern to match any of the provided cities at the start of the Challenge
        city_pattern = "^(" + "|".join(map(re.escape, cities)) + ")"
        df = df[df["Challenge"].str.match(city_pattern)]

    # Replace multiple whitespaces with a single whitespace in the 'Challenge' column
    df["Challenge"] = df["Challenge"].str.replace(r"\s+", " ", regex=True)

    """
    The df looks like this:
                           Challenge                         Evaluation criteria First name             Last name
    0    Aarhus: How can youth ...  Impact; Implementation; Excellence; Co-creation      Emily            Thompson
    1    Aarhus: How can youth ...  Impact; Implementation; Excellence; Co-creation     Robert               Parker
    2    Aarhus: How can youth ...  Impact; Implementation; Excellence; Co-creation     Sophie              Johnson
    3    Aarhus: How can youth ...  Impact; Implementation; Excellence; Co-creation    Michael               Brown
    4    Amsterdam: Wildcard - ...  Impact; Implementation; Excellence; Co-creation      Laura               Davis
    ..                   ...                                              ...        ...                   ...
    136  Utrecht: How to reduce street harassment?          Impact; Implementation      David               Wilson
    137  Utrecht / HKU: How can a personalised calendar...  Implementation; Excellence      Sarah               Taylor
    138  Utrecht / HKU: How can a personalised calendar...  Implementation; Excellence     Daniel               Miller
    139  Utrecht / HKU: How can a personalised calendar...  Impact; Co-creation      Emma               Anderson
    140  Utrecht / HKU: How can a personalised calendar...  Impact; Co-creation     Oliver               Martin
    """

    # List of all evaluation criteria
    # Create a list to store jury member dicts
    jury_members = []

    # Group by First name and Last name
    grouped = df.groupby(["First name", "Last name"])

    # Iterate through each group
    for (first_name, last_name), group in grouped:
        member_dict = {f"{last_name} {first_name}": []}

        # Iterate through each row in the group
        for _, row in group.iterrows():
            challenge = row["Challenge"]
            criteria = row["Evaluation criteria"]

            # Add challenge and criteria to the member's list
            member_dict[f"{last_name} {first_name}"].append({challenge: criteria})

        # Add the member dict to the jury_members list
        jury_members.append(member_dict)
    return jury_members


def process_jury_excel(filename):
    # Read the Excel file
    df = pd.read_excel(filename)
    # Drop all rows except 'Challenge', 'Evaluation criteria'
    df = df[["Challenge", "Evaluation criteria"]]
    # df looks like this:
    """
                                                     Challenge                              Evaluation criteria
    0    Aarhus: How can youth ...  Impact; Implementation; Excellence; Co-creation
    1    Aarhus: How can youth ...  Impact; Implementation; Excellence; Co-creation
    2    Aarhus: How can youth ...  Impact; Implementation; Excellence; Co-creation
    3    Aarhus: How can youth ...  Impact; Implementation; Excellence; Co-creation
    4    Amsterdam: Wildcard - How can an AI solution s...  Impact; Implementation; Excellence; Co-creation
    ..                                                 ...                                              ...
    115          Utrecht: How to reduce street harassment?                           Impact; Implementation
    116  Utrecht / HKU: How can a personalised calendar...                       Implementation; Excellence
    117  Utrecht / HKU: How can a personalised calendar...                       Implementation; Excellence
    118  Utrecht / HKU: How can a personalised calendar...                              Impact; Co-creation
    119  Utrecht / HKU: How can a personalised calendar...                              Impact; Co-creation
    """

    # Replace multiple whitespaces with a single whitespace in the 'Challenge' column
    df["Challenge"] = df["Challenge"].str.replace(r"\s+", " ", regex=True)

    # Count occurrences of each Challenge
    challenge_counts = Counter(df["Challenge"])

    # List of all evaluation criteria
    all_criteria = ["Impact", "Implementation", "Excellence", "Co-creation"]

    # Group by Challenge and aggregate Evaluation criteria
    challenge_criteria = df.groupby("Challenge")["Evaluation criteria"].agg(lambda x: set("; ".join(x).split("; ")))

    # Find missing criteria for each Challenge
    missing_criteria = {}
    for challenge, criteria in challenge_criteria.items():
        missing = set(all_criteria) - criteria
        if missing:
            missing_criteria[challenge] = missing

    # Save the updated DataFrame back to Excel
    output_filename = "updated_" + filename
    df.to_excel(output_filename, index=False)
    return challenge_counts, output_filename, set(df["Challenge"]), missing_criteria


def process_challenge_excel(filename):
    # Read the Excel file
    df = pd.read_excel(filename)
    # Replace multiple whitespaces with a single space in the 'title' column
    df["title"] = df["title"].str.replace(r"\s+", " ", regex=True)

    # Create challenge field
    df["challenge"] = df.apply(
        lambda row: (
            f"{row['city']}: {row['title']}"
            if pd.isna(row["organisation"]) or row["organisation"] == ""
            else f"{row['city']} / {row['organisation']}: {row['title']}"
        ),
        axis=1,
    )

    return set(df["challenge"])


def find_challenges_without_jury(jury_challenges, all_challenges):
    challenges_without_jury = sorted(all_challenges - jury_challenges)
    return challenges_without_jury


def analyze_jury_members(filename):
    # Read the Excel file
    df = pd.read_excel(filename)

    # Count unique jury members by email
    unique_jury_members = df["E-mail"].nunique()

    # Count challenges per jury member
    jury_challenge_counts = df.groupby(["First name", "Last name", "E-mail"])["Challenge"].nunique().reset_index()
    jury_challenge_counts = jury_challenge_counts.sort_values(["Last name", "First name"])

    # Print results
    print(f"\nTotal number of unique jury members: {unique_jury_members}\n")
    print("Jury members and their challenge counts (alphabetically):\n")
    for _, row in jury_challenge_counts.iterrows():
        print(f"{row['Last name']}, {row['First name']} ({row['E-mail']}): {row['Challenge']} challenge(s)")

    return unique_jury_members, jury_challenge_counts


def list_duplicates(filename: str):
    df = pd.read_excel(filename)
    # Drop all columns except E-mail and Challenge and Evaluation criteria
    df = df[["E-mail", "Challenge", "Evaluation criteria"]]
    # Count duplicates by E-mail and Challenge and Evaluation criteria
    duplicate_counts = df.groupby(["E-mail", "Challenge", "Evaluation criteria"]).size().reset_index(name="count")
    # Filter duplicates
    duplicates = duplicate_counts[duplicate_counts["count"] > 1]
    print(duplicates)
    exit()


def list_pilot_managers(filename: str):
    df = pd.read_excel(filename)
    # Keep only the rows where Evaluation criteria contains "pilot manager"
    df = df[df["Evaluation criteria"].str.contains("pilot manager")]
    # Sort by Challenge
    df = df.sort_values("Challenge")
    # Drop all columns except Challenge and E-mail
    df = df[["Challenge", "E-mail"]]
    # Print Challenge, newline and E-mail
    for _, row in df.iterrows():
        print(f"{row['Challenge'][:60]}\t{row['E-mail']}")
    exit()


def find_challenges_without_pilot_manager(filename: str):
    # Read the Excel file
    df = pd.read_excel(filename)

    # Get all unique challenges
    all_challenges = set(df["Challenge"])

    # Filter challenges with pilot manager
    challenges_with_pilot_manager = set(
        df[df["Evaluation criteria"].str.contains("pilot manager", case=False, na=False)]["Challenge"]
    )

    # Find challenges without pilot manager
    challenges_without_pilot_manager = all_challenges - challenges_with_pilot_manager

    # Sort the challenges alphabetically
    challenges_without_pilot_manager = sorted(challenges_without_pilot_manager)

    print("\nChallenges without a pilot manager:\n")
    for challenge in challenges_without_pilot_manager:
        print(challenge)


def list_multiple_pilot_managers(df: pd.DataFrame):
    # Keep only the rows where Evaluation criteria contains "pilot manager"
    df = df[df["Evaluation criteria"].str.contains("pilot manager", case=False, na=False)]

    # Group by Challenge and count occurrences
    challenge_counts = df.groupby("Challenge").size()

    # Get challenges with multiple pilot managers
    multiple_managers = challenge_counts[challenge_counts > 1].index

    # Filter original dataframe to show only challenges with multiple managers
    result = df[df["Challenge"].isin(multiple_managers)]

    # Sort by Challenge for better readability
    result = result.sort_values("Challenge")

    print("\nChallenges with multiple pilot managers:\n")
    for challenge in result["Challenge"].unique():
        print(f"\n{challenge}:")
        managers = result[result["Challenge"] == challenge]["E-mail"].tolist()
        for manager in managers:
            print(f"  - {manager}")


def get_challenges_dict(filename: str) -> dict:
    df = read_and_clean_jury_excel(filename)
    df = df.sort_values("Challenge")
    # Convert DataFrame to dictionary with Challenge as key
    challenges_dict = {}
    for _, row in df.iterrows():
        challenge = row["Challenge"]
        criteria = [criteria.strip() for criteria in row["Evaluation criteria"].split(";")]
        pilot_manager = any("pilot manager" in c.lower() for c in criteria)
        # Remove any criteria containing "pilot manager"
        criteria = [c for c in criteria if "pilot manager" not in c.lower()]
        jury_member = {
            row["E-mail"]: {
                "first_name": row["First name"],
                "last_name": row["Last name"],
                "criteria": criteria,
                "pilot_manager": pilot_manager,
            }
        }

        if challenge not in challenges_dict:
            challenges_dict[challenge] = {}

        email = list(jury_member.keys())[0]
        if email in challenges_dict[challenge]:
            # Update existing jury member
            existing_member = challenges_dict[challenge][email]
            # Add any new criteria
            existing_member["criteria"].extend(
                c for c in jury_member[email]["criteria"] if c not in existing_member["criteria"]
            )
            # Update pilot manager status
            existing_member["pilot_manager"] |= jury_member[email]["pilot_manager"]
        else:
            # Add new jury member
            challenges_dict[challenge].update(jury_member)

    return challenges_dict


def list_challenges(
    filename: str,
    without_pilot_manager: bool = False,
    multiple_pilot_managers: bool = False,
    challenge_regex: str = None,
):
    challenges_dict = get_challenges_dict(filename)

    # Print all challenges in alphabetical order
    for challenge in sorted(challenges_dict.keys()):
        # Get jury members for this challenge
        jury_members = challenges_dict[challenge]

        # Count pilot managers
        pilot_managers = [m for m in jury_members.values() if m["pilot_manager"]]
        num_pilot_managers = len(pilot_managers)

        # Skip based on pilot manager filters
        if without_pilot_manager and num_pilot_managers > 0:
            continue
        if multiple_pilot_managers and num_pilot_managers <= 1:
            continue

        # Skip if challenge doesn't match regex
        if challenge_regex and not re.search(challenge_regex, challenge, re.IGNORECASE):
            continue

        print(f"\n{challenge}")

        # Print pilot manager status
        if num_pilot_managers == 0:
            print("NO PILOT MANAGER")
        elif num_pilot_managers > 1:
            print(f"MULTIPLE ({num_pilot_managers}) PILOT MANAGERS")

        # Sort and print pilot managers first, then regular jury members
        sorted_members = sorted(
            jury_members.items(), key=lambda x: (not x[1]["pilot_manager"], x[1]["last_name"], x[1]["first_name"])
        )

        for email, member in sorted_members:
            pilot_manager_text = " [PILOT MANAGER]" if member["pilot_manager"] else ""
            criteria_text = "; ".join(member["criteria"])
            print(f"  {member['last_name']} {member['first_name']} ({email}):{pilot_manager_text} {criteria_text}")
    exit()


def main():
    args = parse_args()
    df = read_and_clean_jury_excel(args.jury_excel, sort_by="Challenge")
    # Reset index
    df = df.reset_index(drop=True)
    print(df)
    if args.multiple_pilot_managers:
        list_multiple_pilot_managers(df)
        return
    if args.list_emails:
        _, df = analyze_jury_members(args.jury_excel)
        print("List of unique jury members:\n===============================")
        print("\n".join(sorted(df["E-mail"].unique())))
        return

    if args.list_challenges:
        list_challenges(args.jury_excel, challenge_regex="^Porto")
        # list_challenges(args.jury_excel, without_pilot_manager=True)
        return

    if args.pilot_managers:
        list_pilot_managers(args.jury_excel)
        return

    if args.no_pilot_manager:
        find_challenges_without_pilot_manager(args.jury_excel)
        return

    if args.list_duplicates:
        list_duplicates(args.jury_excel)
        return

    if args.city:
        jury_members = jury_member_report_excel(args.jury_excel, args.city)
        print(f"Jury members: {len(jury_members)}\n")
        # print the jury members, their challenges and criteria, in alphabetical order, using the first key
        for member in sorted(jury_members, key=lambda x: list(x.keys())[0]):
            # print the member name
            name = list(member.keys())[0]
            print(f"{name}")
            for challenges in member[name]:
                for challenge in challenges:
                    print(f"  {challenge}")
                    # number of criteria
                    num_criteria = len(challenges[challenge].split(";"))
                    print(f"    Criteria ({num_criteria}): {challenges[challenge]}")
        print("\n")

    # Process jury Excel
    challenge_counts, output_filename, jury_challenges, missing_criteria = process_jury_excel(args.jury_excel)

    print("Challenge counts from jury Excel (in alphabetical order):\n")
    for challenge in sorted(challenge_counts.keys()):
        print(f"{challenge}: {challenge_counts[challenge]}")

    print("\nMissing criteria for each challenge:\n")
    for challenge, criteria in missing_criteria.items():
        print(f"{challenge}:")
        print(f"  Missing: {'; '.join(sorted(criteria))}")

    # Process challenge Excel
    all_challenges = process_challenge_excel(args.challenge_excel)

    print("\nChallenges without any jury members:\n")
    challenges_without_jury = find_challenges_without_jury(jury_challenges, all_challenges)
    for challenge in challenges_without_jury:
        print(challenge)

    # challenges_without_pilot_manager = find_challenges_without_pilot_manager(
    #     jury_challenges, all_challenges
    # )

    unique_jury_members, jury_challenge_counts = analyze_jury_members(args.jury_excel)


if __name__ == "__main__":
    main()
