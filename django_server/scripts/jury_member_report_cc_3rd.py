import pandas as pd
import argparse
import re
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
    return parser.parse_args()


def jury_member_report_excel(filename, cities: list[str]) -> list:
    jury_members = []
    # Read the Excel file
    df = pd.read_excel(filename)
    # Drop unnecessary columns
    df = df[["Challenge", "Evaluation criteria", "First name", "Last name"]]
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
    # Filter by city string, which is in the start of the string
    # There can be multiple cities, so we need to filter by each city
    if cities:
        # Create a regex pattern to match any of the provided cities at the start of the Challenge
        city_pattern = "^(" + "|".join(map(re.escape, cities)) + ")"
        df = df[df["Challenge"].str.match(city_pattern)]

    # Replace multiple whitespaces with a single whitespace in the 'Challenge' column
    df["Challenge"] = df["Challenge"].str.replace(r"\s+", " ", regex=True)

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


def main():
    args = parse_args()

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

    # Find challenges without jury
    challenges_without_jury = find_challenges_without_jury(jury_challenges, all_challenges)

    print("\nChallenges without any jury members:\n")
    for challenge in challenges_without_jury:
        print(challenge)

    unique_jury_members, jury_challenge_counts = analyze_jury_members(args.jury_excel)


if __name__ == "__main__":
    main()
