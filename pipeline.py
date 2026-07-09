from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

def run_research_pipeline(topic:str)->dict:

    state={}

    #search agent working
    print("step 1 search agent working")
    search_agent=build_search_agent()
    search_result=search_agent.invoke(
        {
            "messages":[("user",f"find the recent,reliable and detailed information about{topic}")]
        }
    )
    state["search_results"]=search_result['messages'][-1].content
    print(state['search_results'])

    #step2 reader agent
    print("step 2 reader agent working")
    reader_agent=build_reader_agent()
    reader_result=reader_agent.invoke({"messages":[("user",
        f"beased on the following search results about {topic},"
        f"pick the most relevant URL and scarpe it for deeper content."
        f"search results{state['search_results'][:800]}"
    )]})

    state['scaraped_content']=reader_result['messages'][-1].content

    print(state['scaraped_content'])

    # step 3 writer chain

    print("step 3 writer chian")


    research_combined=(
        f"search results : {state['search_results']}"
        f"detailed results:{state['scaraped_content']}"
    )

    state['report']=writer_chain.invoke({
        'topic':topic,
        'research':research_combined
    })

    print("final report")

    #critic report
    print("step 4 critic")

    state['feedback']=critic_chain.invoke({
        "report":state['report']
    })

    print("critic report",state['feedback'])

    return state



if __name__ =="__main__":
    topic=input("enetr research topic")
    run_research_pipeline(topic)
