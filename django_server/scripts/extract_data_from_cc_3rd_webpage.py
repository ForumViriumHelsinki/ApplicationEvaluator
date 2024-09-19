import argparse
import json
import re
from pathlib import Path
from urllib.parse import urljoin

import httpx
import pandas as pd
from bs4 import BeautifulSoup

translation_table = str.maketrans(
    {
        "“": '"',  # Left double quote
        "”": '"',  # Right double quote
        "‘": "'",  # Left single quote
        "’": "'",  # Right single quote
        "«": '"',  # Left double angle quote
        "»": '"',  # Right double angle quote
        "‹": "'",  # Left single angle quote
        "›": "'",  # Right single angle quote
        "„": '"',  # Low-9 double quote
        "‟": '"',  # Double high-reversed-9 quote
        "‚": "'",  # Single low-9 quote
        "‛": "'",  # Single high-reversed-9 quote
    }
)

CC_ID = 301


def parse_args():
    parser = argparse.ArgumentParser(description="Extract challenges from the Communicity webpage")
    parser.add_argument(
        "--url",
        type=str,
        default="https://communicity-project.eu/third-open-call-challenges/",
        help="URL of the webpage with challenges",
    )
    parser.add_argument(
        "--filebase",
        type=str,
        default="challenges_parsed",
        help="filename body for the output files",
    )
    # output directory
    parser.add_argument("--output-dir", type=str, default="parsed", help="directory to save the output files")
    return parser.parse_args()


def extract_links(url: str) -> list:
    response = httpx.get(url, follow_redirects=True)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all(
            "a",
            class_="raven-button raven-button-widget-normal-effect-none raven-button-text-align-center "
            "raven-button-link elementor-animation-none",
        )
        return [urljoin(url, link.get("href")) for link in links]
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        exit()


def get_page_content(url: str) -> list:
    response = httpx.get(url, follow_redirects=True)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        # Get all text in this tag before the word "Challenge
        # <h1 class="elementor-heading-title elementor-size-default">Amsterdam Challenges </h1>
        city_name = (
            soup.find("h1", class_="elementor-heading-title elementor-size-default").get_text().split(" Challenge")[0]
        )
        return city_name, soup.get_text(separator="\n", strip=True)
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        exit()


def parse_challenges(city: str, content: str) -> list:
    challenges = []
    challenge_sections = re.split(r"(?=^.*? Challenge \d+:)", content, flags=re.MULTILINE)

    for section in challenge_sections:
        if not section.strip():
            continue

        challenge = {"city": city}
        lines = section.strip().split("\n")

        # Parse challenge header
        header = lines[0]
        match = re.match(r"^(.*) Challenge (\d+):", header)
        if match:
            challenge["organisation"] = match.group(1)
            challenge["sequence"] = int(match.group(2))
        else:
            continue  # Skip if not a valid challenge header

        # Parse title and description
        challenge["title"] = lines[1].strip().translate(translation_table)
        # Remove double spaces from title
        challenge["title"] = re.sub(r"\s+", " ", challenge["title"])
        description_end = next(
            (i for i, line in enumerate(lines) if "Minimum scores and weightings:" in line),
            len(lines),
        )
        challenge["description"] = "\n".join(lines[2:description_end]).strip().translate(translation_table)

        # Parse scores
        scores = {}
        score_lines = lines[description_end + 1 :]
        i = 0
        while i < len(score_lines):
            category_match = re.match(r"(\d+\.\s*)(.*)", score_lines[i])
            if category_match and i + 1 < len(score_lines):
                category = category_match.group(2).strip()
                # Some challenges have a different format for scores
                score_match = re.match(
                    r".*inimum score:?\s*([\d,.]+)\s*\|\s*Weighting:\s*(\d+)\s*%",
                    score_lines[i + 1],
                )
                if score_match:
                    min_score = float(score_match.group(1).replace(",", "."))  # Convert comma to dot
                    weighting = int(score_match.group(2))
                    scores[category] = [min_score, weighting]
                    i += 2
                else:
                    i += 1
            else:
                i += 1

        challenge["scores"] = scores

        # Check if total weighting is 100%
        total_weighting = sum(score[1] for score in scores.values())
        if total_weighting != 100:
            print(
                f"Error in {challenge['city']} Challenge {challenge['sequence']}: "
                f"Total weighting is {total_weighting}%, not 100%"
            )
            print("\n".join(score_lines[:10]))
            # exit()
        challenges.append(challenge)
    return challenges


def process_links(extracted_links):
    global CC_ID

    # List to store all challenges
    challenges = []

    # Process each link
    for link in extracted_links:
        print(f"Processing link: {link}")
        city, content = get_page_content(link)
        print(city)
        if content:
            challenges += parse_challenges(city, content)
            print("Have now {} challenges".format(len(challenges)))
        else:
            print(f"Failed to retrieve content from {link}")
            exit()
    # Make organisation is empty if it is the same as city
    for challenge in challenges:
        challenge["organisation"] = "" if challenge["city"] == challenge["organisation"] else challenge["organisation"]
    # sort challenges by ["city", "organisation", "sequence", "title"]
    challenges = sorted(challenges, key=lambda x: (x["city"], x["organisation"], x["sequence"], x["title"]))
    # Add unique ID, starting from CC-301
    for challenge in challenges:
        challenge["id"] = f"CC-{CC_ID}"
        print(
            f"{challenge['id']} {challenge['city']} {challenge['organisation']} "
            f"{challenge['sequence']} {challenge['title']}"
        )
        CC_ID += 1

    return challenges


def print_challenges(challenges):
    # Print all extracted challenges
    print("\nAll extracted challenges:")
    for c in challenges:
        # Count the number of scores
        num_scores = len(c["scores"])
        # Count the total weighting
        total_weighting = sum(score[1] for score in c["scores"].values())
        print(
            f"""City: {c['city']} (Organisation {c['organisation']} {c['sequence']})
Title: {c['title']}
Description: {c['description'][0:60]}...
Scores ({num_scores}, {total_weighting}/100): {c['scores']}
========================"""
        )


def create_df(challenges):
    # Create a DataFrame from the challenges
    df = pd.DataFrame(challenges)
    # Create dropdown menu values from city, organisation and title. If city == organisation, only show city
    df["city_organisation_title"] = df.apply(
        lambda x: (
            f"{x['city']} / {x['organisation']}: {x['title']}"
            if x["organisation"] != ""
            else f"{x['city']}: {x['title']}"
        ),
        axis=1,
    )
    # Make organisation empty if it is the same as city
    df["organisation"] = df.apply(lambda x: "" if x["city"] == x["organisation"] else x["organisation"], axis=1)
    df = df.sort_values(by=["city", "organisation", "sequence", "title"])
    # Reset the index
    df = df.reset_index(drop=True)
    df["score count"] = df["scores"].apply(lambda x: len(x))
    df["weighting"] = df["scores"].apply(lambda x: sum([score[1] for score in x.values()]))
    # sort dataframe by city, organisation, sequence, title
    possible_score_names = [
        "Impact",
        "Implementation quality and efficiency",
        "Excellence",
        "Co-creation",
        "Technology",
    ]

    for score_name in possible_score_names:
        df[f"{score_name}_min"] = df["scores"].apply(lambda x: x.get(score_name, [None, None])[0])
        df[f"{score_name}_weight"] = df["scores"].apply(lambda x: x.get(score_name, [None, None])[1])

    # drop the scores column
    df = df.drop("scores", axis=1)
    return df


args = parse_args()
output_dir = Path(args.output_dir)
output_dir.mkdir(parents=True, exist_ok=True)
# Create the output file paths and add date and time to the filename
dt = pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S")

output_file_csv = output_dir / f"{args.filebase}_{dt}.csv"
output_file_xlsx = output_dir / f"{args.filebase}_{dt}.xlsx"
output_file_json = output_dir / f"{args.filebase}_{dt}.json"


# Extract and process the links
extracted_links = extract_links(args.url)
challenges = process_links(extracted_links)


df = create_df(challenges)
print(df)

# Save json file
with open(output_file_json, "w") as file:
    file.write(json.dumps(challenges, indent=2))

# Save the DataFrame to a CSV / excel file
df.to_csv(output_file_csv, index=False)
df.to_excel(output_file_xlsx, index=False)
