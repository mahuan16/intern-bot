from database import Session, Posting

session = Session()
one = session.query(Posting).first()
print(one.company, one.url)   # note down which one you're deleting
session.delete(one)
session.commit()
session.close()

# import csv
# import random

# with open("affirmations.csv", mode="r") as f:
#     reader = csv.reader(f)
    
#     random_row = random.choice(list(reader))
#     print(random_row)



# import requests

# url = "https://raw.githubusercontent.com/SimplifyJobs/Summer2027-Internships/dev/README.md"
# response = requests.get(url)
# print(response.status_code)
# print(response.text[5000:8000])