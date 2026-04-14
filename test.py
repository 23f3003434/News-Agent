# # from datetime import datetime


# # print(datetime.now().strftime("%Y-%m-%d"))

# # list_ = ["hello are you", "Where are you"]

# # print(f"Articles are {' '.join(list_)} ")
# import json
# # check = {
# #     "a":1999,
# #     "b":18,
# #     "c":"Hello are "}

# # print(check)
# # with open("a.txt","w") as f:
# #     json.dump(check,f)

# from rich.console import Console 
# from rich.markdown import Markdown 

# console = Console()

# with open("a.txt","r") as f:
#     data = json.load(f)

# console.print(Markdown(data['summary']['Bitcoin price']))




from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import TypedDict, List, Dict
import requests
import os
load_dotenv()



llm = ChatGoogleGenerativeAI(
    model='gemini-2.5-flash-lite',
    api_key=os.environ.get('GOOGLE_API_KEY')
)

response = llm.invoke("hello")
print(response.content)