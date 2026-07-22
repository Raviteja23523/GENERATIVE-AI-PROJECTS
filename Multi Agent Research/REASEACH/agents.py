from langchain.agents import create_agent
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

try:
    from .tools import web_search, scrape_url
except ImportError:  # pragma: no cover - fallback for direct script execution
    from tools import web_search, scrape_url
load_dotenv()


# model setup
llm=ChatMistralAI(model="mistral-small-2506",temperature=0)

# creating agents
def build_search_agent():
    return create_agent(
        model=llm,
        tools=[web_search]
    )

def build_reader_agent():
    return create_agent(
        model=llm,
        tools=[scrape_url]
    )

#writer chain
writer_prompt=ChatPromptTemplate.from_messages(
    [
        ("system","you are an expert research writer. write clear,structured and insightful reports"),
        ("human","""write a detailed research report on the topic below
        topic:{topic}
        research gathered:{research}
        
        structure the report as:
        introduction
        key findings (minimum 3 well explained points)
        conclusion
        sources(list of all URLs found in the research)
        
        be detailed, factual and professional."""),

    ]
)

writer_chain=writer_prompt|llm|StrOutputParser()

# critic chain

critic_prompt=ChatPromptTemplate.from_messages(
    [
        ("system","you are an sharp and constructive research critic.be honest and specific"),
        ("human","""review the research report below and evaluate it strictly.
        report:{report}
        respond in this exact format:

        score:x/10

        stregths:

        areas to improve:

        one line verdict:
        
        """)
    ]
)

critic_chain=critic_prompt|llm|StrOutputParser()