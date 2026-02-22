import streamlit as st
import os
import datetime
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from crewai_tools import ScrapeWebsiteTool

# 1. Page Config
st.set_page_config(page_title="Sarkari Job Auto-Blogger Pro", page_icon="📝", layout="wide")
st.title("🚀 Final Stable Auto-Blogger (Llama 3.1 Edition) 🔥")

# 2. Configuration
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.secrets.get("GROQ_API_KEY", "")
    if not api_key:
        api_key = st.text_input("Enter Groq API Key:", type="password")

# --- MODEL FIX ---
# Mixtral aur Purana Llama hat gaya hai, isliye 3.1-8b-instant sabse best hai
current_model = "llama-3.1-8b-instant"

if api_key:
    os.environ["OPENAI_API_KEY"] = api_key 
    os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
    os.environ["OPENAI_MODEL_NAME"] = current_model

# 3. Inputs
job_topic = st.text_input("Enter Job Topic:", value="RSSB Lab Assistant Recruitment 2026")
default_urls = "https://www.resultbharat.com/RSSB-Lab-Assistant_Advt-05-2026.html, https://www.freejobalert.com/articles/rssb-lab-assistant-recruitment-2026-apply-online-for-804-posts-3035740"
target_urls = st.text_area("Target URL Links (Comma separated):", value=default_urls, height=100)

scrape_tool = ScrapeWebsiteTool()

if st.button("🚀 Write My Mega Blog Now"):
    if not api_key:
        st.error("❌ API Key is missing!")
    else:
        with st.spinner('🤖 AI is fetching data and writing a 1200+ word human-style blog...'):
            try:
                # LLM Setup
                llm = ChatOpenAI(
                    model_name=current_model,
                    temperature=0.7,
                    api_key=api_key
                )

                # Agents
                researcher = Agent(
                    role='Expert Researcher',
                    goal='Extract deep details from the provided links.',
                    backstory="You find every date, fee, and vacancy detail accurately.",
                    tools=[scrape_tool],
                    llm=llm,
                    verbose=True
                )

                writer = Agent(
                    role='Professional Blogger',
                    goal='Write a MASSIVE, 1200+ word SEO blog in Hindi/Hinglish.',
                    backstory="""You are a pro blogger. You write long paragraphs, use large tables, 
                    and maintain a helpful human tone (Doston, Khushkhabri, etc.). 
                    You never skip details and expand every point.""",
                    llm=llm,
                    verbose=True
                )

                # Tasks
                task1 = Task(
                    description=f"Scrape these links: {target_urls} for {job_topic}.",
                    expected_output="Detailed factual report.",
                    agent=researcher
                )

                task2 = Task(
                    description=f"""
                    Write a VERY LONG (1200+ words) Hindi/Hinglish blog.
                    
                    MUST INCLUDE:
                    1. Catchy Human-Style Intro (3 paragraphs).
                    2. BIG Overview Table.
                    3. Detailed Dates Section with explanations.
                    4. Massive Eligibility & Age Section (Detail every point).
                    5. Department-wise vacancy table.
                    6. Step-by-Step 'How to Apply' guide.
                    
                    Use real links: https://sso.rajasthan.gov.in/ and https://rssb.rajasthan.gov.in/
                    """,
                    expected_output="Full length high-quality Markdown blog.",
                    agent=writer
                )

                my_crew = Crew(agents=[researcher, writer], tasks=[task1, task2])
                result = my_crew.kickoff()

                st.success("Blog Generated Successfully! ✅")
                st.markdown(result.raw)
            
            except Exception as e:
                st.error(f"Error: {e}")
