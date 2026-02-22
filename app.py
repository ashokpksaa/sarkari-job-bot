import streamlit as st
import os
import datetime
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from crewai_tools import ScrapeWebsiteTool

# 1. Page Config
st.set_page_config(page_title="Sarkari Job Pro Auto-Blogger", page_icon="📝", layout="wide")
st.title("🔥 Professional Sarkari Job Blogger (Power Version) 🚀")

# 2. Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.secrets.get("GROQ_API_KEY", "")
    if not api_key:
        api_key = st.text_input("Enter Groq API Key:", type="password")

# WAPAS 70B MODEL PAR SWITCH (Reset ke baad best yahi hai)
current_model = "llama-3.3-70b-versatile"

if api_key:
    os.environ["OPENAI_API_KEY"] = api_key 
    os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
    os.environ["OPENAI_MODEL_NAME"] = current_model

# 3. Inputs
job_topic = st.text_input("Enter Job Topic:", value="RSSB Lab Assistant Recruitment 2026")
default_urls = "https://www.resultbharat.com/RSSB-Lab-Assistant_Advt-05-2026.html, https://www.freejobalert.com/articles/rssb-lab-assistant-recruitment-2026-apply-online-for-804-posts-3035740, https://www.adda247.com/exams/rajasthan/rssb-lab-assistant-recruitment-2026/"
target_urls = st.text_area("Target URL Links (Max 3 links):", value=default_urls, height=100)

scrape_tool = ScrapeWebsiteTool()

if st.button("🚀 Write My Mega-Detailed Blog"):
    if not api_key:
        st.error("❌ Please enter Groq API Key!")
    else:
        with st.spinner('🤖 17 Minutes over! AI is now writing your massive 1200+ word blog...'):
            try:
                llm = ChatOpenAI(
                    model_name=current_model,
                    temperature=0.5,
                    api_key=api_key
                )

                # Researcher Agent
                researcher = Agent(
                    role='Data Mining Expert',
                    goal='Extract deep facts from the provided URLs without missing a single date or fee.',
                    backstory="You are a specialist in Government Job Data Extraction. You find all tables and details.",
                    tools=[scrape_tool],
                    llm=llm,
                    verbose=True
                )

                # Pro-Writer Agent
                writer = Agent(
                    role='Senior Hindi Content Strategist',
                    goal='Write a MASSIVE, 1200+ word SEO blog post that looks 100% human-written.',
                    backstory="""You are a top-tier blogger for 'AK Unlocks'. You use a mix of Hindi and English (Hinglish).
                    You never write short text. You use words like 'Doston', 'Maja Aa Gaya', 'Zaroori Notice'.
                    Your tables are large and your explanations are very detailed (minimum 1200 words).""",
                    llm=llm,
                    verbose=True
                )

                task1 = Task(
                    description=f"Scrape these links: {target_urls} and find every single detail for {job_topic}.",
                    expected_output="Exhaustive factual data breakdown.",
                    agent=researcher
                )

                task2 = Task(
                    description=f"""
                    Write a VERY LONG (1200+ words) professional Hindi/Hinglish blog post.
                    
                    STRUCTURE RULES:
                    1. **Intro**: 3 LONG paragraphs starting with "Namaste doston! Rajasthan ke berozgar yuvaon ke liye..."
                    2. **Detailed Overview Table**: Include all general info.
                    3. **Date Section**: Explain each date's importance in a long bullet point.
                    4. **Full Vacancy Table**: Must show Department-wise posts (Education, Agriculture, Forensic, etc.).
                    5. **Age & Qualification**: Give a massive explanation for each department.
                    6. **How to Apply**: Write 7 detailed steps for SSO Portal.
                    7. **Exam Pattern**: Detailed points.
                    
                    LINKS TO USE: https://sso.rajasthan.gov.in/ and https://rssb.rajasthan.gov.in/
                    """,
                    expected_output="Final Mega-Detailed Markdown Blog Post.",
                    agent=writer
                )

                my_crew = Crew(agents=[researcher, writer], tasks=[task1, task2])
                result = my_crew.kickoff()

                st.success("Mega Blog Ready! ✅")
                st.markdown("---")
                st.markdown(result.raw)
            
            except Exception as e:
                st.error(f"Error: {e}")
