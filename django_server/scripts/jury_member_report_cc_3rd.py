import pandas as pd
import argparse
from collections import Counter


def parse_args():
    parser = argparse.ArgumentParser(description="Analyze Excel files for Challenges and Jury members")
    parser.add_argument("--jury-excel", required=True, help="Path to the jury Excel file")
    parser.add_argument("--challenge-excel", required=True, help="Path to the challenge Excel file")
    return parser.parse_args()


def process_jury_excel(filename):
    # Read the Excel file
    df = pd.read_excel(filename)
    # Drop all rows except 'Challenge', 'Evaluation criteria'
    df = df[["Challenge", "Evaluation criteria"]]
    # df looks like this:
    """
                                                     Challenge                              Evaluation criteria
    0    Aarhus: How can youth interaction with public ...  Impact; Implementation; Excellence; Co-creation
    1    Aarhus: How can youth interaction with public ...  Impact; Implementation; Excellence; Co-creation
    2    Aarhus: How can youth interaction with public ...  Impact; Implementation; Excellence; Co-creation
    3    Aarhus: How can youth interaction with public ...  Impact; Implementation; Excellence; Co-creation
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


def main():
    args = parse_args()

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


if __name__ == "__main__":
    main()
