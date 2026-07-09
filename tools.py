from langchain.tools import tool
import requests
import os
from bs4 import BeautifulSoup
from tavily import TavilyClient
from dotenv import load_dotenv
load_dotenv()
from rich import print
tavily=TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

#TOOL0-1
@tool
def web_search(query:str)->str:
    """Search the web for recent and reliable information on a topic.Returns Titles ,URLs,and snippets."""
    results=tavily.search(query=query,max_results=5)

    #return results
    # print(web_search.invoke("what are the recent newws about cricket"))
    out=[]
    for r in results['results']:
        out.append(
            f"Title:{r['title']}\nURL:{r['url']}\nSnippet:{r['content'][:300]}\n"
        )
    return "\n-----\n".join(out)
    # print(web_search.invoke("what are the recent newws about cricket"))

#TOOL-2
@tool
def scrape_url(url:str)->str:
    """ Scarapr and return clean text content from given URL for deeper reading"""
    try:
        resp=requests.get(url,timeout=8,headers={"User-Agent":"Mozilla/5.0"})
        soup=BeautifulSoup(resp.text,"html.parser")
        for tag in soup(["script","style","nav","footer"]):
            tag.decompose()
        return soup.get_text(separator=" ",strip=True)[:300]
    except Exception as e:
        return f"could not scrape URL:{e}"
print(scrape_url.invoke("https://www.cricbuzz.com/"))