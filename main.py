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



class NewsState(TypedDict):
    queries: List[str]
    summary: Dict[str,str]
    sentiment: Dict[str,str]
    articles : Dict[str,Dict]



def read_query(state: NewsState) -> dict:
    print("Reading queries")
    return {
        "queries": state.get("queries",[])
        }


def fetch_articles(state: NewsState) -> dict:
    print("Fetching last 3 days articles")
    BASE_URL= os.environ.get('NEWS_BASE_URL')
    news_key = os.environ.get('NEWS_API_KEY')
    date = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
    articles = dict()
    for query in state.get("queries",[]):
        url = f"{BASE_URL}q={query}&from={date}&pageSize=5&sortBy=popularity&apiKey={news_key}"
        result = requests.get(url).json()
        articles[query] = result['articles'] if len(result['articles']) >=1 else [{"articles":"No information latest available"}]
    return {
        "articles":articles
    }


def summary(state: NewsState):
    print("Using LLM to summarise the latest articles")
    summary = dict()
    articles = state.get("articles",dict())
    for query in articles:
        prompt = f"""
            You are a professional news analyst creating a structured news brief.

            Query: "{query}"

            Instructions:
            1. Extract key developments from the articles.
            2. Preserve important details like:
            - Dates
            - Sources (publication names)
            - Major events and outcomes
            3. Merge overlapping information, but DO NOT lose attribution.
            4. Ignore irrelevant metadata, HTML, or truncated text.

            Output Format:

            Summary:
            - Write a clear, well-structured narrative (200–250 words)
            - Focus on major developments and their implications
            - Maintain chronological clarity if possible

            Key Developments:
            - [Date] – [Event] (Source)
            - [Date] – [Event] (Source)

            Notes:
            - No fluff or repetition
            - No hallucinated facts
            - Keep it factual and journalistic

            Articles:
            {articles[query]}
            """
        response = llm.invoke(prompt)
        summary[query] = response.content 
    
    return {
        "summary":summary
    }
    

def sentiment_analysis(state: NewsState):
    print("Using LLM for sentiment analysis on the summary")
    sentiment = dict()
    summaries = state.get("summary",dict())
    sentiment = dict()
    for query in summaries:
        prompt = f"Answer in one word and classify the news summary into positive negative or neutral for the query {query} and the summary {summaries[query]}  "
        response = llm.invoke(prompt).content
        response = response.strip().lower()
        if "positive" in response:
            sentiment[query] = "Positive"

        if "negative" in response:
            sentiment[query] = "Negative"        
        else:
            sentiment[query] = "Neutral"
    return {
        "sentiment":sentiment
    }





graph = StateGraph(NewsState)

graph.add_node("read_query",read_query)
graph.add_node("fetch_articles",fetch_articles)
graph.add_node("summary",summary)
graph.add_node("sentiment_analysis",sentiment_analysis)

graph.add_edge(START,"read_query")
graph.add_edge("read_query","fetch_articles")
graph.add_edge("fetch_articles","summary")
graph.add_edge("summary","sentiment_analysis")
graph.add_edge("sentiment_analysis",END)




compiled_graph = graph.compile()






from fastapi import FastAPI
import json

app = FastAPI()

@app.get("/{query}")
def serve(query: str):
    inital_state = {"queries":[query]}
    output = compiled_graph.invoke(inital_state)
    with open("last_output.json","r") as f:
        json.dump(output,f)
    return output




