import streamlit as st
import os
import datetime
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from crewai_tools import ScrapeWebsiteTool

today_date = datetime.datetime.now().strftime("%B %d, %Y")

# 1. Page Config
st.set_page_config(page_title="Sarkari Job Pro Auto-Blogger", page_icon="📝", layout="wide")
st.title("🔥 Professional Sarkari Job Blogger v3.0 🚀")

# 2. Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.secrets.get("GROQ_API_KEY", "")
    if not api_key:
        api_key = st.text_input("Enter Groq API Key:", type="password")

if api_key:
    os.environ["OPENAI_API_KEY"] = api_key 
    os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
    os.environ["OPENAI_MODEL_NAME"] = "mixtral-8x7b-32768"

# 3. Inputs
job_topic = st.text_input("Enter Job Topic:", value="RSSB Lab Assistant Recruitment 2026")
default_urls = "https://www.resultbharat.com/RSSB-Lab-Assistant_Advt-05-2026.html, https://www.freejobalert.com/articles/rssb-lab-assistant-recruitment-2026-apply-online-for-804-posts-3035740, https://www.adda247.com/exams/rajasthan/rssb-lab-assistant-recruitment-2026/"
target_urls = st.text_area("Target URL Links (Comma separated):", value=default_urls, height=100)

scrape_tool = ScrapeWebsiteTool()

# --- MAIN LOGIC ---
if st.button("🚀 Generate Mega-Detailed Blog"):
    if not api_key:
        st.error("❌ API Key missing!")
    else:
        with st.spinner('🤖 AI is researching from multiple sources and designing your blog...'):
            try:
                llm = ChatOpenAI(
                    model_name="mixtral-8x7b-32768",
                    temperature=0.5,
                    api_key=api_key
                )

                # Researcher: Data extract karne ke liye
                researcher = Agent(
                    role='Expert Data Miner',
                    goal='Scrape and provide every single tiny detail from the provided URLs.',
                    backstory="You are the best at finding table data, dates, and fees from job websites.",
                    tools=[scrape_tool],
                    llm=llm,
                    verbose=True
                )

                # Writer: Detailed content aur table design ke liye
                writer = Agent(
                    role='Senior SEO Content Architect',
                    goal='Create a MASSIVE, 1200+ word, beautifully designed Hindi blog post.',
                    backstory="""You are a professional blogger who knows that long articles rank better. 
                    You use beautiful Markdown tables, bold headings, and detailed paragraphs. 
                    You never write short text. Your style is clean, professional, and exhaustive.""",
                    llm=llm,
                    verbose=True
                )

                task1 = Task(
                    description=f"Deeply scrape {target_urls} and find vacancies, dates, fees, and eligibility for {job_topic}.",
                    expected_output="Detailed factual breakdown of the job.",
                    agent=researcher
                )

                task2 = Task(
                    description=f"""
                    Using the data, write a MEGA-DETAILED blog post in Hindi/Hinglish (Minimum 1000-1200 words).
                    
                    STRUCTURE RULES:
                    1. **INTRODUCTION**: Minimum 3 long paragraphs. Talk about Rajasthan Govt's initiative and why this lab assistant role is important.
                    2. **OVERVIEW TABLE**: Use a clean, wide Markdown table.
                    3. **IMPORTANT DATES**: Don't just list them. Explain each date's significance in a bulleted paragraph.
                    4. **APPLICATION FEE**: Create a separate detailed section with a table or bold bullets.
                    5. **ELIGIBILITY & AGE**: Give a massive explanation. Include age relaxation details for SC/ST/OBC.
                    6. **VACANCY BREAKDOWN**: Create a विभागानुसार (Department-wise) table.
                    7. **HOW TO APPLY**: Write a 7-step guide, explaining each step in 2 lines.
                    8. **LINKS**: Provide working links for SSO (https://sso.rajasthan.gov.in) and RSSB (https://rssb.rajasthan.gov.in).

                    TONE: Encouraging, Factual, and Professional.
                    """,
                    expected_output="A massive, high-quality Markdown blog post ready for WordPress.",
                    agent=writer
                )

                my_crew = Crew(agents=[researcher, writer], tasks=[task1, task2], process=Process.sequential)
                result = my_crew.kickoff()

                st.success("Mega-Detailed Blog Generated! ✅")
                st.markdown("---")
                st.markdown(result.raw)
            
            except Exception as e:
                st.error(f"Error occurred: {e}")

# --- FOOTER ---
st.markdown("---")
st.caption("AI-Powered Auto-Blogger for AK Unlocks Project")
