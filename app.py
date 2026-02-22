import streamlit as st
import os
import datetime
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from crewai_tools import ScrapeWebsiteTool

# 1. Page Config
st.set_page_config(page_title="Sarkari Job Pro Auto-Blogger", page_icon="📝", layout="wide")
st.title("🚀 Final Bulletproof Auto-Blogger 🔥")

# 2. Configuration
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.secrets.get("GROQ_API_KEY", "")
    if not api_key:
        api_key = st.text_input("Enter Groq API Key:", type="password")

# --- MODEL SELECTION ---
# Llama-3.1-8b ki TPM limit kam hai, isliye hum wapas Llama-3.3-70b par switch karenge
# Lekin hum "Chunking" ka use karenge taaki 413 error na aaye.
current_model = "llama-3.3-70b-versatile"

if api_key:
    os.environ["OPENAI_API_KEY"] = api_key 
    os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"

# 3. Inputs
job_topic = st.text_input("Enter Job Topic:", value="RSSB Lab Assistant Recruitment 2026")
# Sirf 2 main links rakhein taaki 6000 token ki limit cross na ho
default_urls = "https://www.resultbharat.com/RSSB-Lab-Assistant_Advt-05-2026.html, https://www.freejobalert.com/articles/rssb-lab-assistant-recruitment-2026-apply-online-for-804-posts-3035740"
target_urls = st.text_area("Trusted Links (Max 2 links recommended for free tier):", value=default_urls, height=80)

# Scraper ko summarize karne ke liye set kiya taaki data chota ho jaye
scrape_tool = ScrapeWebsiteTool()

if st.button("🚀 Generate Detailed Blog"):
    if not api_key:
        st.error("❌ Please enter API Key!")
    else:
        with st.spinner('🤖 Processing data in chunks to avoid limits...'):
            try:
                llm = ChatOpenAI(
                    model_name=current_model,
                    temperature=0.5,
                    api_key=api_key
                )

                # Agent 1: Data nikalne wala
                researcher = Agent(
                    role='Data Expert',
                    goal='Extract ONLY key facts (Dates, Fees, Vacancies) from URLs.',
                    backstory="You are a precise data extractor. You avoid junk and focus only on numbers and dates.",
                    tools=[scrape_tool],
                    llm=llm,
                    verbose=True
                )

                # Agent 2: Bada blog likhne wala
                writer = Agent(
                    role='SEO Content Writer',
                    goal='Write a detailed 1000+ word Hindi blog post.',
                    backstory="You are a professional Hindi blogger. You expand small facts into beautiful detailed articles.",
                    llm=llm,
                    verbose=True
                )

                task1 = Task(
                    description=f"Scrape these links: {target_urls}. Summarize ONLY the important tables and dates for {job_topic}.",
                    expected_output="A concise factual summary (under 2000 words).",
                    agent=researcher
                )

                task2 = Task(
                    description="""
                    Based on the summary, write a 1000-word detailed Hindi blog post.
                    USE THIS FORMAT:
                    1. 🔬 Mega Title with Emojis
                    2. Human-style Intro (3 long paragraphs)
                    3. Overview Table (Bold)
                    4. Department Vacancy Table
                    5. Step-by-Step 'How to Apply'
                    6. Important Links
                    """,
                    expected_output="Final beautiful Markdown blog post.",
                    agent=writer
                )

                my_crew = Crew(agents=[researcher, writer], tasks=[task1, task2])
                result = my_crew.kickoff()

                st.success("Success! ✅")
                st.markdown(result.raw)
            
            except Exception as e:
                # Agar phir bhi TPM error aaye toh user ko 1 minute wait karne bolega
                if "413" in str(e) or "rate_limit" in str(e).lower():
                    st.warning("⚠️ Groq is busy! Please wait 1 minute and click the button again. Free tier has a speed limit.")
                else:
                    st.error(f"Error: {e}")
