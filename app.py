import streamlit as st
import os
from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai.tools import tool
from duckduckgo_search import DDGS

# 1. Page Config
st.set_page_config(page_title="Sarkari Job Auto-Blogger", page_icon="📝")
st.title("📝 Sarkari Job Auto-Blogger AI")
st.markdown("Enter a government job topic (e.g., **SSC CGL 2026 Notification**) to generate an SEO-friendly blog post.")

# 2. SECURE API KEY HANDLING (No Hardcoding!)
with st.sidebar:
    st.header("⚙️ Configuration")
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ API Key Loaded Securely from Secrets!")
    except:
        api_key = st.text_input("Enter Google API Key manually:", type="password")
        if not api_key:
            st.warning("⚠️ Please enter your API Key to proceed.")

if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key
    os.environ["GEMINI_API_KEY"] = api_key

# 3. Input Box
job_topic = st.text_input("Enter Job Topic:", value="SSC CGL 2026 Notification details")

# --- TOOL DEFINITION ---
@tool
def search_internet(query: str):
    """Search the internet for official details about government jobs, dates, and eligibility."""
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=3)]
            return str(results)
    except Exception as e:
        return f"Error searching internet: {e}"

# --- MAIN LOGIC ---
if st.button("🚀 Generate Blog Post"):
    if not api_key:
        st.error("❌ API Key missing! Please add it.")
    else:
        with st.spinner('🤖 AI Agents are researching and writing... (Please wait)'):
            try:
                # Brain setup - Using stable flash model
                llm = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash",
                    verbose=True,
                    temperature=0.7,
                    api_key=api_key 
                )

                # Agents
                researcher = Agent(
                    role='Government Job Researcher',
                    goal='Search the internet to find 100% accurate details about government job notifications.',
                    backstory="Expert researcher who finds official dates, vacancies, fees, and eligibility.",
                    verbose=True,
                    llm=llm,
                    tools=[search_internet]
                )

                writer = Agent(
                    role='SEO Blog Writer',
                    goal='Write a highly engaging, SEO-optimized, and plagiarism-free blog post in Hinglish/Hindi.',
                    backstory="Expert content writer for a Sarkari Job website. Uses Headings, Bullet points, and bold text.",
                    verbose=True,
                    llm=llm
                )

                # Tasks
                task1 = Task(
                    description=f"Use the tool to find official details about '{job_topic}'. Find: Vacancies, Eligibility, Age Limit, Dates, and Fee.",
                    expected_output="A bulleted list of factual details.",
                    agent=researcher
                )

                task2 = Task(
                    description=f"Write an SEO-friendly blog post about '{job_topic}' in Hinglish based on the researcher's data. Include sections for Important Dates, Eligibility, Vacancy Details, and How to Apply.",
                    expected_output="A fully formatted Markdown blog post.",
                    agent=writer
                )

                # Crew
                my_crew = Crew(agents=[researcher, writer], tasks=[task1, task2], process=Process.sequential)
                result = my_crew.kickoff()

                st.success("Blog Post Generated! ✅")
                if hasattr(result, 'raw'):
                    st.markdown(result.raw)
                else:
                    st.markdown(str(result))
            
            except Exception as e:
                st.error(f"An error occurred: {e}")
