import streamlit as st
import os
import datetime
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from crewai_tools import ScrapeWebsiteTool

today_date = datetime.datetime.now().strftime("%B %d, %Y")

# 1. Page Config
st.set_page_config(page_title="Sarkari Job Auto-Blogger Pro", page_icon="📝", layout="wide")
st.title("📝 Sarkari Job Auto-Blogger (Human-Style Mode) 🚀")

# 2. Configuration
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.secrets.get("GROQ_API_KEY", "")
    if not api_key:
        api_key = st.text_input("Enter Groq API Key:", type="password")

if api_key:
    os.environ["OPENAI_API_KEY"] = api_key 
    os.environ["OPENAI_BASE_URL"] = "https://api.groq.com/openai/v1"
    os.environ["OPENAI_MODEL_NAME"] = "llama-3.3-70b-versatile"

# 3. Inputs
job_topic = st.text_input("Job Topic:", value="RSSB Lab Assistant Recruitment 2026")
default_urls = "https://www.resultbharat.com/RSSB-Lab-Assistant_Advt-05-2026.html, https://www.freejobalert.com/articles/rssb-lab-assistant-recruitment-2026-apply-online-for-804-posts-3035740"
target_urls = st.text_area("Target Websites:", value=default_urls, height=80)

scrape_tool = ScrapeWebsiteTool()

if st.button("🚀 Write Human-Style Blog"):
    if not api_key:
        st.error("❌ Please enter API Key!")
    else:
        with st.spinner('🤖 AI ' + 'is writing like a Pro Blogger...'):
            try:
                llm = ChatOpenAI(
                    model_name="llama-3.3-70b-versatile",
                    temperature=0.8, # Thoda creative tone ke liye
                    api_key=api_key
                )

                researcher = Agent(
                    role='Data Expert',
                    goal='Extract real facts from the URLs.',
                    backstory="You extract 100% accurate data. You are the foundation of this blog.",
                    tools=[scrape_tool],
                    llm=llm,
                    verbose=True
                )

                writer = Agent(
                    role='Viral Content Writer',
                    goal='Write a blog that feels like it was written by a human blogger for his audience.',
                    backstory="""You are a famous Indian Job Blogger. You use 'Hinglish' (Hindi + English mix). 
                    You use words like 'Doston', 'Good News', 'Zaroori Baat'. 
                    Your tone is helpful and energetic, not like a boring robot. 
                    You explain things simply, like you are talking to a younger brother.""",
                    llm=llm,
                    verbose=True
                )

                task1 = Task(
                    description=f"Scrape {target_urls} and find every detail about {job_topic}.",
                    expected_output="Detailed factual report.",
                    agent=researcher
                )

                task2 = Task(
                    description=f"""
                    Write a 1000-word blog post in Human-Style Hinglish.
                    
                    RULES:
                    1. NO ROBOTIC LANGUAGE. Use conversational Hindi.
                    2. START with: "नमस्ते दोस्तों! अगर आप भी राजस्थान में सरकारी नौकरी का सपना देख रहे हैं, तो आज आपके लिए एक बहुत बड़ी खुशखबरी लेकर आया हूँ..."
                    3. USE REAL LINKS: 
                       - SSO Portal: https://sso.rajasthan.gov.in/
                       - Official Website: https://rssb.rajasthan.gov.in/
                    4. Tables must be clean and bold.
                    5. Explain the selection process like a mentor.
                    """,
                    expected_output="A viral, human-written style blog post in Markdown.",
                    agent=writer
                )

                my_crew = Crew(agents=[researcher, writer], tasks=[task1, task2])
                result = my_crew.kickoff()

                st.success("Human-Style Blog Ready! ✅")
                st.markdown(result.raw)
            
            except Exception as e:
                st.error(f"Error: {e}")
