import streamlit as st
import os
import re
import datetime
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from crewai.tools import tool
from duckduckgo_search import DDGS

today_date = datetime.datetime.now().strftime("%B %d, %Y")

# 1. Page Config
st.set_page_config(page_title="Sarkari Job Auto-Blogger", page_icon="📝")
st.title("📝 Sarkari Job Auto-Blogger (Powered by Groq 🚀)")
st.markdown("Enter a government job topic to generate an SEO-friendly blog post.")

# 2. SECURE API KEY HANDLING 
with st.sidebar:
    st.header("⚙️ Configuration")
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        st.success("✅ Groq API Key Loaded Securely!")
    except:
        api_key = st.text_input("Enter Groq API Key (starts with gsk_):", type="password")
        if not api_key:
            st.warning("⚠️ Please enter your Groq API Key to proceed.")

if api_key:
    os.environ["OPENAI_API_KEY"] = api_key 
    os.environ["OPENAI_BASE_URL"] = "https://api.groq.com/openai/v1"
    os.environ["OPENAI_MODEL_NAME"] = "llama-3.3-70b-versatile"

# 3. Input Box
job_topic = st.text_input("Enter Job Topic:", value="LAB. ASSISTANT/JUNIOR LAB. ASSISTANT COMBINED DIRECT RECRUITMENT-2026 (RSSB)")

# --- Text Cleaner ---
safe_topic = re.sub(r'[^a-zA-Z0-9\s]', ' ', job_topic)

# --- TOOL DEFINITION ---
@tool
def search_internet(query: str):
    """Search the internet for official details. Keep the query VERY short."""
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query + " official vacancy notification details", max_results=4)]
            return str(results)
    except Exception as e:
        return f"Error: {e}"

# --- MAIN LOGIC ---
if st.button("🚀 Generate Blog Post"):
    if not api_key:
        st.error("❌ Groq API Key missing! Please add it.")
    else:
        with st.spinner('🤖 AI is researching securely... (Please wait)'):
            try:
                llm = ChatOpenAI(
                    model_name="llama-3.3-70b-versatile",
                    temperature=0.2, # Low creativity to prevent hallucination
                    api_key=api_key,
                    base_url="https://api.groq.com/openai/v1"
                )

                # STRICT AGENTS
                researcher = Agent(
                    role='Government Job Researcher',
                    goal='Search the internet to find factual details about government jobs.',
                    backstory="You are a strict fact checker. Never guess data. If not found, say 'Not Announced'. When using tools, ALWAYS use very short search queries (max 4-5 words).",
                    verbose=True,
                    llm=llm,
                    tools=[search_internet],
                    allow_delegation=False
                )

                writer = Agent(
                    role='SEO Blog Writer',
                    goal='Write a highly engaging, factual, and plagiarism-free blog post in Hinglish/Hindi.',
                    backstory="You write SEO-friendly articles. Strictly use the facts provided by the Researcher. Do not invent dates or numbers.",
                    verbose=True,
                    llm=llm,
                    allow_delegation=False
                )

                # THE FIX: Instructed AI to use a SHORT query for the tool
                task1 = Task(
                    description=f"""Today's date is {today_date}. The user wants details for: '{safe_topic}'.
                    CRITICAL INSTRUCTION: Do NOT pass this entire long name into the search_internet tool. It will crash the system.
                    Instead, create a VERY SHORT 4-word summary (e.g., 'RSSB Lab Assistant 2026') and pass ONLY that short string into the search_internet tool.
                    Extract: Total Vacancies, Eligibility, Age Limit, Dates, and Fee. If missing, write 'Not Announced'.""",
                    expected_output="A strict factual bulleted list. Missing info must be 'Not Announced'.",
                    agent=researcher
                )

                task2 = Task(
                    description=f"Write an SEO-friendly blog post about '{job_topic}' in Hinglish based ONLY on the researcher's data. Use Headings, Bullet points, and bold text.",
                    expected_output="A fully formatted Markdown blog post based strictly on facts.",
                    agent=writer
                )

                # Crew
                my_crew = Crew(agents=[researcher, writer], tasks=[task1, task2], process=Process.sequential)
                result = my_crew.kickoff()

                st.success("Factual Blog Post Generated! ✅")
                if hasattr(result, 'raw'):
                    st.markdown(result.raw)
                else:
                    st.markdown(str(result))
            
            except Exception as e:
                st.error(f"An error occurred: {e}")
