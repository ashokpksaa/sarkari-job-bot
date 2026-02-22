import streamlit as st
import os
import datetime
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from crewai_tools import ScrapeWebsiteTool

# 1. Page Config
st.set_page_config(page_title="Sarkari Job Pro Auto-Blogger", page_icon="📝", layout="wide")
st.title("🔥 Mega Sarkari Job Blogger v4.0 (Full Details) 🚀")

# 2. Configuration
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.secrets.get("GROQ_API_KEY", "")
    if not api_key:
        api_key = st.text_input("Enter Groq API Key:", type="password")

current_model = "llama-3.1-8b-instant"

if api_key:
    os.environ["OPENAI_API_KEY"] = api_key 
    os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
    os.environ["OPENAI_MODEL_NAME"] = current_model

# 3. Inputs
job_topic = st.text_input("Enter Job Topic:", value="RSSB Lab Assistant Recruitment 2026")
default_urls = "https://www.resultbharat.com/RSSB-Lab-Assistant_Advt-05-2026.html, https://www.freejobalert.com/articles/rssb-lab-assistant-recruitment-2026-apply-online-for-804-posts-3035740"
target_urls = st.text_area("Trusted Links (Data Source):", value=default_urls, height=100)

scrape_tool = ScrapeWebsiteTool()

if st.button("🚀 Generate High-Quality Detailed Blog"):
    if not api_key:
        st.error("❌ API Key is missing!")
    else:
        with st.spinner('🤖 Scraping multiple sources and writing a massive 1500-word blog...'):
            try:
                llm = ChatOpenAI(
                    model_name=current_model,
                    temperature=0.6,
                    api_key=api_key
                )

                # Researcher: Saara data nikaalne ke liye
                researcher = Agent(
                    role='Data Mining Expert',
                    goal='Extract 100% accurate and deep details from the provided URLs.',
                    backstory="You are a specialist in Government Job Data. You extract table data, specific dates, department-wise vacancies, and full eligibility rules.",
                    tools=[scrape_tool],
                    llm=llm,
                    verbose=True
                )

                # Writer: Designer blog likhne ke liye
                writer = Agent(
                    role='Viral SEO Content Architect',
                    goal='Write a MASSIVE, 1500-word, highly attractive Hindi blog post.',
                    backstory="""You are the king of Sarkari Job Blogging. You write long, engaging, and detailed posts. 
                    You use beautiful Markdown tables, big bold headings, and a friendly human tone (Doston, Big Update, etc.). 
                    You explain things so clearly that no one needs to check another website.""",
                    llm=llm,
                    verbose=True
                )

                task1 = Task(
                    description=f"Scrape these links: {target_urls} for {job_topic}. Extract Vacancies, Dates, Fees, Department-wise posts, and full Eligibility.",
                    expected_output="Exhaustive factual report with all tables found.",
                    agent=researcher
                )

                task2 = Task(
                    description=f"""
                    Write a VERY LONG (1500 words) Hindi blog post. 
                    
                    DESIGN RULES:
                    1. **Attractive Title**: Use Emojis (e.g., 🔬, 🚀, ✅).
                    2. **Engaging Intro**: Start with "नमस्कार दोस्तों! राजस्थान के बेरोजगार युवाओं के लिए मुख्यमंत्री भजनलाल शर्मा सरकार ने एक और बड़ी सौगात दी है..." (Write 3 long paragraphs).
                    3. **Mega Overview Table**: A big, bold table with board name, vacancy, salary, and website.
                    4. **Full Vacancy Table**: Create a detailed Department-wise table (Education, Agriculture, Forensic, etc.).
                    5. **Age & Eligibility**: Explain rules in detail. Mention Age Relaxation (SC/ST/OBC - 5 years, etc.).
                    6. **Step-by-Step Guide**: Write 7 detailed steps on 'How to Apply' via SSO Portal.
                    7. **Exam Pattern**: If found, explain the paper pattern.
                    
                    STRICTLY use these links: https://sso.rajasthan.gov.in/ and https://rssb.rajasthan.gov.in/
                    """,
                    expected_output="Mega-detailed, high-quality Markdown blog post.",
                    agent=writer
                )

                my_crew = Crew(agents=[researcher, writer], tasks=[task1, task2], process=Process.sequential)
                result = my_crew.kickoff()

                st.success("Mega Blog Generated! ✅")
                st.markdown("---")
                st.markdown(result.raw)
            
            except Exception as e:
                st.error(f"Error: {e}")
