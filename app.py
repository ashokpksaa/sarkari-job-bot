import streamlit as st
import os
import re
import datetime # <--- NEW: AI ko aaj ki date batane ke liye
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from crewai.tools import tool
from duckduckgo_search import DDGS

# Aaj ki date nikalna taaki AI update rahe
today_date = datetime.datetime.now().strftime("%B %d, %Y")

# 1. Page Config
st.set_page_config(page_title="Sarkari Job Auto-Blogger", page_icon="📝")
st.title("📝 Sarkari Job Auto-Blogger (Powered by Groq 🚀)")
st.markdown("Enter a government job topic (e.g., **SSC CGL 2026 Notification**) to generate an SEO-friendly blog post.")

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
job_topic = st.text_input("Enter Job Topic:", value="RSSB Lab Assistant Recruitment 2026 official details")

# --- Clean the topic for the Search Tool ---
safe_topic = re.sub(r'[^a-zA-Z0-9\s]', ' ', job_topic)

# --- TOOL DEFINITION ---
@tool
def search_internet(query: str):
    """Search the internet for official details about government jobs, dates, and eligibility."""
    try:
        with DDGS() as ddgs:
            # Fake sites se bachne ke liye thode zyada results nikal rahe hain
            results = [r for r in ddgs.text(query + " official notification date vacancy", max_results=5)]
            return str(results)
    except Exception as e:
        return f"Error: {e}"

# --- MAIN LOGIC ---
if st.button("🚀 Generate Blog Post"):
    if not api_key:
        st.error("❌ Groq API Key missing! Please add it.")
    else:
        with st.spinner('🤖 AI is strictly researching real facts... (Please wait)'):
            try:
                llm = ChatOpenAI(
                    model_name="llama-3.3-70b-versatile",
                    temperature=0.3, # <--- CREATIVITY KAM KAR DI TAAKI JHOOTH NA BOLE
                    api_key=api_key,
                    base_url="https://api.groq.com/openai/v1"
                )

                # STRICT AGENTS
                researcher = Agent(
                    role='Senior Government Job Fact-Checker',
                    goal='Search the internet to find ONLY 100% accurate and official details.',
                    backstory="""You are a strict, no-nonsense fact checker. You ONLY rely on the exact data returned by your search tool. 
                    If a specific detail (like exact exam date, application fee, or total vacancies) is NOT found in the search text, 
                    you MUST state 'Not Officially Announced Yet'. NEVER invent, guess, or hallucinate data.""",
                    verbose=True,
                    llm=llm,
                    tools=[search_internet],
                    allow_delegation=False
                )

                writer = Agent(
                    role='SEO Blog Writer',
                    goal='Write a highly engaging, factual, and plagiarism-free blog post in Hinglish.',
                    backstory="""You write clear, SEO-friendly articles for job seekers. 
                    You MUST strictly use the facts provided by the Researcher. 
                    If the Researcher says 'Not Officially Announced Yet', you must write 'Abhi aadhikarik ghoshna nahi hui hai (To Be Announced)'. 
                    DO NOT make up any dates or numbers.""",
                    verbose=True,
                    llm=llm,
                    allow_delegation=False
                )

                # STRICT TASKS
                task1 = Task(
                    description=f"""Today's date is {today_date}. Use the tool to search for '{safe_topic}'. 
                    Extract the following: Total Vacancies, Eligibility Criteria, Age Limit, Important Dates, and Application Fee.
                    Remember: Do not guess. If missing, write 'Not Announced'.""",
                    expected_output="A strict factual bulleted list. Missing info must be marked as 'Not Announced'.",
                    agent=researcher
                )

                task2 = Task(
                    description=f"""Write an SEO-friendly blog post about '{job_topic}' in Hinglish based ONLY on the researcher's data. 
                    Structure:
                    1. Catchy Title
                    2. Introduction
                    3. Important Dates (Use 'To be announced' if facts say so)
                    4. Eligibility & Age Limit
                    5. Vacancy Details
                    6. How to Apply""",
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
