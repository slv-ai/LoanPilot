from dotenv import load_dotenv
load_dotenv()
import asyncio
import nest_asyncio

nest_asyncio.apply()

from typing import TypedDict

from langgraph.graph import StateGraph, END

from playwright.async_api import async_playwright

from langchain_openai import ChatOpenAI


# -----------------------------------
# STATE
# -----------------------------------
class State(TypedDict):
    query: str
    page_text: str
    answer: str


# -----------------------------------
# LLM
# -----------------------------------
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
)


# -----------------------------------
# PLAYWRIGHT NODE
# -----------------------------------
async def browser_node(state: State):

    async with async_playwright() as p:

:

        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ]
        )

        page = await browser.new_page()

        await page.goto("https://example.com")

        title = await page.title()

        content = await page.text_content("body")

        await browser.close()

    text = f"""
    TITLE:
    {title}

    CONTENT:
    {content}
    """

    print("\nBROWSER DATA:\n")
    print(text)

    return {
        "page_text": text
    }


# -----------------------------------
# LLM NODE
# -----------------------------------
def summarize_node(state: State):

    prompt = f"""
    Based on this webpage:

    {state['page_text']}

    Answer the user's question:

    {state['query']}
    """

    response = llm.invoke(prompt)

    return {
        "answer": response.content
    }


# -----------------------------------
# GRAPH
# -----------------------------------
graph = StateGraph(State)

graph.add_node("browser", browser_node)

graph.add_node("summarize", summarize_node)

graph.set_entry_point("browser")

graph.add_edge("browser", "summarize")

graph.add_edge("summarize", END)

app = graph.compile()


# -----------------------------------
# RUN
# -----------------------------------
result = asyncio.run(
    app.ainvoke({
        "query": """
        Tell me:
        1. Page title
        2. Main topic
        3. Short summary
        """
    })
)

print("\nFINAL ANSWER:\n")

print(result["answer"])