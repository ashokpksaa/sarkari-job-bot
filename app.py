import streamlit as st
import os
import datetime
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from crewai_tools import ScrapeWebsiteTool

# 1. Page Config
st.set_page_config(page_title="Sarkari Job Auto-Blogger Pro", page_icon="📝", layout="wide")
st.title("🚀 1000+ Words Job Blogger (100% Fixed Mode) 🔥")

# 2. Configuration
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.secrets.get("GROQ_API_KEY", "")
    if not api_key:
        api_key = st.text_input("Enter Groq API Key:", type="password")

# 3.1-70b model (Taaki 429 limit error na aaye)
current_model = "gemma2-9b-it"

if api_key:
    os.environ["OPENAI_API_KEY"] = api_key 
    # 👇 YAHAN MERI GALTI THI JO MAINE THEEK KAR DI HAI (BASE_URL) 👇
    os.environ["OPENAI_BASE_URL"] = "https://api.groq.com/openai/v1"

# 3. Inputs
job_topic = st.text_input("Enter Job Topic:", value="RSSB Lab Assistant Recruitment 2026")
default_urls = "https://www.resultbharat.com/RSSB-Lab-Assistant_Advt-05-2026.html, https://www.freejobalert.com/articles/rssb-lab-assistant-recruitment-2026-apply-online-for-804-posts-3035740"
target_urls = st.text_area("Target Links:", value=default_urls, height=80)

scrape_tool = ScrapeWebsiteTool()

if st.button("🚀 Generate 1000+ Words Detailed Blog"):
    if not api_key:
        st.error("❌ Please enter API Key!")
    else:
        with st.spinner('🤖 Researching and writing a deep 1000-word article...'):
            try:
                llm = ChatOpenAI(
                    model_name=current_model,
                    temperature=0.6,
                    api_key=api_key,
                    base_url="https://api.groq.com/openai/v1" # Double safety
                )

                # Researcher Agent
                researcher = Agent(
                    role='Senior Data Researcher',
                    goal='Extract all tables, dates, and vacancy numbers accurately.',
                    backstory="You are an expert at finding hidden details in job notifications. You provide deep facts.",
                    tools=[scrape_tool],
                    llm=llm,
                    verbose=True
                )

                # Writer Agent
                writer = Agent(
                    role='Pro SEO Content Writer',
                    goal='Write a massive 1000+ words Hindi blog post.',
                    backstory="""You are a professional blogger. You never write short posts. 
                    You expand every detail into long, helpful paragraphs for students. 
                    You use a friendly human tone like a mentor.""",
                    llm=llm,
                    verbose=True
                )

                task1 = Task(
                    description=f"Scrape {target_urls} for {job_topic}. Get all dates, vacancies, and fees.",
                    expected_output="Detailed factual report.",
                    agent=researcher
                )

                task2 = Task(
                    description=f"""
                    Write a 1000-word detailed Hindi/Hinglish blog post.
                    
                    STRICT RULES FOR 1000 WORDS:
                    1. **Introduction**: Write 4 long paragraphs (300 words). Explain why this is a golden chance.
                    2. **Detailed Overview Table**: All board details.
                    3. **Dates Section**: Explain each date's importance in 2 sentences.
                    4. **Category-wise Vacancy**: Create a BIG Table for all departments.
                    5. **Qualification**: Explain the educational requirements in deep detail for each post.
                    6. **Step-by-Step Guide**: Minimum 8 detailed steps to apply via SSO.
                    7. **Selection Process**: Detailed breakdown of exam and DV.
                    
                    Use real links: https://sso.rajasthan.gov.in/ and https://rssb.rajasthan.gov.in/
                    """,
                    expected_output="Final Mega 1000-word Markdown Blog Post.",
                    agent=writer
                )

                my_crew = Crew(agents=[researcher, writer], tasks=[task1, task2])
                result = my_crew.kickoff()

                st.success("Success! ✅")
                st.markdown(result.raw)
            
            except Exception as e:
                st.error(f"Error: {e}")
