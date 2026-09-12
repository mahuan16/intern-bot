from database import Session, Posting
from datetime import datetime
import requests
import re


README_URLS = [
    "https://raw.githubusercontent.com/vanshb03/Summer2027-Internships/refs/heads/dev/README.md",
    "https://raw.githubusercontent.com/SimplifyJobs/Summer2027-Internships/refs/heads/dev/README.md",
]

# what the name says
def already_exists(session, url):
    return session.query(Posting).filter_by(url=url).first() is not None

def parse_rows(readme_text):
    pattern = r"^\|.+\|$"
    data_rows = re.findall(pattern, readme_text, re.MULTILINE)

    parsed = []
    for row in data_rows:
        if "---" in row:
            continue
        columns = row.split("|")[1:-1]
        columns = [c.strip() for c in columns]
        if len(columns) < 5:
            continue

        apply_column = columns[3]
        href_pattern = r'href="([^"]+)"'
        match = re.search(href_pattern, apply_column)
        apply_url = match.group(1) if match else None

        parsed.append({
            "source": "github",
            "company": columns[0],
            "position": columns[1],
            "location": columns[2],
            "description": None,
            "pay": None,
            "url": apply_url,
            "first_seen": datetime.now()
        })
    return parsed

def scrape_and_save():
    session = Session()
    all_new_postings = []

    for readme_url in README_URLS:
        response = requests.get(readme_url)
        parsed_rows = parse_rows(response.text)

        for row in parsed_rows:
            if row["url"] is None:
                continue
            if already_exists(session, row["url"]):
                continue
            new_posting = Posting(**row)
            session.add(new_posting)
            all_new_postings.append(new_posting)

    session.commit()
    session.close()
    print(f"Added {len(all_new_postings)} new postings.")
    return all_new_postings

if __name__ == "__main__":
    scrape_and_save()


