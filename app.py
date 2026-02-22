import streamlit as st
import os
from crewai import Agent, Task, Crew, Process
from langchain_groq import ChatGroq
from crewai.tools import tool
from duckduckgo_search import DDGS

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
    os.environ["GROQ_API_KEY"] = api_key
    # 👇 CrewAI ko chup karane ke liye ek "Dummy" OpenAI key de di
    os.environ["OPENAI_API_KEY"] = "sk-dummy-key-to-keep-crewai-happy-12345"

# 3. Input Box
job_topic = st.text_input("Enter Job Topic:", value="Railway ALP Vacancy 2026 details")

# --- TOOL DEFINITION ---
@tool
def search_internet(query: str):
    """Search the internet for official details about government jobs, dates, and eligibility."""
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=3)]
            return str(results)
    except Exception as e:
        return f"Error: {e}"

# --- MAIN LOGIC ---
if st.button("🚀 Generate Blog Post"):
    if not api_key:
        st.error("❌ Groq API Key missing! Please add it.")
    else:
        with st.spinner('🤖 AI is researching and writing... (Super Fast! ⚡)'):
            try:
                # 👇 OFFICIAL GROQ CONNECTION (Ab tools perfectly kaam karenge)
                groq_llm = ChatGroq(
                    groq_api_key=api_key,
                    model_name="llama-3.3-70b-versatile",
                    temperature=0.5
                )

                # Agents
                researcher = Agent(
                    role='Government Job Researcher',
                    goal='Search the internet to find 100% accurate details about government job notifications.',
                    backstory="Expert researcher who finds official dates, vacancies, fees, and eligibility.",
                    verbose=True,
                    llm=groq_llm,
                    tools=[search_internet],
                    allow_delegation=False
                )

                writer = Agent(
                    role='SEO Blog Writer',
                    goal='Write a highly engaging, SEO-optimized, and plagiarism-free blog post in Hinglish/Hindi.',
                    backstory="Expert content writer for a Sarkari Job website. Uses Headings, Bullet points, and bold text.",
                    verbose=True,
                    llm=groq_llm,
                    allow_delegation=False
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
