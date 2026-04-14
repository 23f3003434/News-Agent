from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import TypedDict, List, Dict
import requests
import os
load_dotenv()



llm = ChatGoogleGenerativeAI(
    model='gemini-2.5-flash',
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
        print(f"Passing query {query}")
        url = f"{BASE_URL}q={query}&from={date}&pageSize=5&sortBy=popularity&apiKey={news_key}"
        result = requests.get(url).json()
        articles[query] = result['articles'] if len(result['articles']) >=1 else [{"articles":"No information latest available"}]
    return {
        "articles":articles
    }


def summary(state: NewsState):
    summary = dict()
    articles = state.get("articles",dict())
    for query in articles:
        prompt = f"""
            You are an expert news summarizer.

            Query: "{query}"

            Analyze the articles below and produce a clear, factual summary.

            Requirements:
            - Exactly 100 words (not more, not less)
            - Focus on major developments, causes, and implications
            - Combine overlapping information across articles
            - No opinions, speculation, or fluff
            - Write in a professional, journalistic tone

            Articles:
            {articles[query]}

            Final Answer (100 words only):
            """
        response = llm.invoke(prompt)
        summary[query] = response.content 
    
    return {
        "summary":summary
    }
    

def sentiment_analysis(state: NewsState):
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


inital_state = {"queries":["Bitcoin price"]}

compiled_graph = graph.compile()

output = compiled_graph.invoke(inital_state)









