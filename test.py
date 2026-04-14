# from datetime import datetime


# print(datetime.now().strftime("%Y-%m-%d"))

# list_ = ["hello are you", "Where are you"]

# print(f"Articles are {' '.join(list_)} ")
import json
# check = {
#     "a":1999,
#     "b":18,
#     "c":"Hello are "}

# print(check)
# with open("a.txt","w") as f:
#     json.dump(check,f)

from rich.console import Console 
from rich.markdown import Markdown 

console = Console()

with open("a.txt","r") as f:
    data = json.load(f)

console.print(Markdown(data['summary']['Bitcoin price']))




