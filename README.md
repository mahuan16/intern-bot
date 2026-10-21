# Internship bot

Scrapes SimplifyJobs/Summer2027-Internships (Software Engineering + Data Science/AI/ML)
and sends new listings to Discord at 12pm and 10pm Pacific.

## Test locally
    pip install -r requirements.txt
    python scraper.py                                # prints a few scraped listings
    FORCE_RUN=1 python main.py                       # dry run, prints instead of sending
    FORCE_RUN=1 DISCORD_WEBHOOK_URL="your-url" python main.py   # real send
(Delete seen.json afterwards if you want the first-run behavior again.)

## Deploy (free, runs even when your laptop is off)
1. Create a PRIVATE GitHub repo and push all these files (keep the .github folder).
2. Repo -> Settings -> Secrets and variables -> Actions -> New repository secret
   Name: DISCORD_WEBHOOK_URL   Value: your webhook URL
3. Repo -> Actions tab -> "Check internships" -> Run workflow (first run seeds seen.json
   and sends a "bot is live" message).
4. Done. It now runs on the schedule.

## Change the schedule or timezone
Edit TIMEZONE and RUN_HOURS in main.py, and the cron lines in .github/workflows/check.yml
(cron is in UTC).
