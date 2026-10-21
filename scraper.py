"""Scrapes the SimplifyJobs Summer 2027 internship list and returns listings
for the categories we care about."""

import re

import requests
from bs4 import BeautifulSoup

README_URL = (
    "https://raw.githubusercontent.com/SimplifyJobs/Summer2027-Internships/dev/README.md"
)

# Section headings in the README that we want to keep.
# We match on a keyword so small wording/emoji changes don't break us.
WANTED_SECTIONS = {
    "Software Engineering": "Software Engineering",
    "Data Science, AI": "Data Science / AI / ML",
}


def fetch_readme() -> str:
    resp = requests.get(README_URL, timeout=30)
    resp.raise_for_status()  # raises an error on 404/500 etc. instead of failing silently
    return resp.text


def split_sections(markdown: str) -> dict[str, str]:
    """Split the README into {heading: text} using the '## ' markdown headings."""
    parts = re.split(r"^## (.+)$", markdown, flags=re.MULTILINE)
    # re.split with a capture group gives: [intro, heading1, body1, heading2, body2, ...]
    return {parts[i].strip(): parts[i + 1] for i in range(1, len(parts) - 1, 2)}


def parse_table_rows(section_html: str, category: str) -> list[dict]:
    soup = BeautifulSoup(section_html, "html.parser")
    listings = []
    last_company = ""

    for tr in soup.find_all("tr"):
        cells = tr.find_all("td")
        if len(cells) < 4:  # header rows use <th>, so they have no <td>
            continue

        company = cells[0].get_text(strip=True)
        if company == "↳":  # "↳" means "same company as the row above"
            company = last_company
        else:
            company = company.replace("🔥", "").strip()
            last_company = company

        role = cells[1].get_text(strip=True)
        location = cells[2].get_text(separator=", ", strip=True)
        # Collapsed multi-location cells look like "4 locations, London, UK, ..."
        location = re.sub(r"^\d+ locations?,\s*", "", location)

        links = [a["href"] for a in cells[3].find_all("a", href=True)]
        if not links:
            continue  # no apply link -> nothing useful to send
        apply_url = links[0]
        # The second link is the Simplify page, whose UUID makes a stable unique ID.
        match = re.search(r"simplify\.jobs/p/([0-9a-f-]+)", " ".join(links))
        listing_id = match.group(1) if match else apply_url

        listings.append(
            {
                "id": listing_id,
                "category": category,
                "company": company,
                "role": role,
                "location": location,
                "url": apply_url,
            }
        )
    return listings


def get_listings() -> list[dict]:
    sections = split_sections(fetch_readme())
    results = []
    for heading, body in sections.items():
        for keyword, category in WANTED_SECTIONS.items():
            if keyword in heading:
                results.extend(parse_table_rows(body, category))
    return results


if __name__ == "__main__":
    found = get_listings()
    print(f"Found {len(found)} listings")
    for item in found[:5]:
        print(item)
