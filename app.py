import streamlit as st
import os
import datetime
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from crewai_tools import ScrapeWebsiteTool

today_date = datetime.datetime.now().strftime("%B %d, %Y")

# 1. Page Config
st.set_page_config(page_title="Sarkari Job Auto-Blogger Pro", page_icon="🔬", layout="wide")
st.title("🔬 Sarkari Job Auto-Blogger Pro (Scraper Mode) 🚀")
st.markdown("Enter a job topic and your trusted website URLs. The AI will scrape ONLY these websites and write a detailed Hindi SEO blog.")

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

# 3. Inputs
job_topic = st.text_input("Enter Job Topic:", value="RSSB Lab Assistant Recruitment 2026")

default_urls = "https://www.resultbharat.com/RSSB-Lab-Assistant_Advt-05-2026.html, https://www.freejobalert.com/articles/rssb-lab-assistant-recruitment-2026-apply-online-for-804-posts-3035740, https://www.adda247.com/exams/rajasthan/rssb-lab-assistant-recruitment-2026/"
target_urls = st.text_area("Enter Trusted Website URLs (Comma separated):", value=default_urls, height=100)

# --- TOOL DEFINITION ---
scrape_tool = ScrapeWebsiteTool()

# --- MAIN LOGIC ---
if st.button("🚀 Scrape & Generate LONG Blog Post"):
    if not api_key:
        st.error("❌ Groq API Key missing! Please add it.")
    else:
        with st.spinner('🤖 AI is scraping and writing a detailed 1000+ word blog... (Please wait 1-2 minutes)'):
            try:
                llm = ChatOpenAI(
                    model_name="llama-3.3-70b-versatile",
                    temperature=0.4, # Thoda badhaya taaki lamba likh sake
                    api_key=api_key,
                    base_url="https://api.groq.com/openai/v1"
                )

                # --- AGENTS ---
                researcher = Agent(
                    role='Senior Web Scraper & Fact Checker',
                    goal='Scrape the provided URLs and extract comprehensive and accurate job details.',
                    backstory="You are an expert data extractor. Use the ScrapeWebsiteTool on the provided URLs. Extract Dates, Vacancies, Fees, and deeply detailed Eligibility criteria.",
                    verbose=True,
                    llm=llm,
                    tools=[scrape_tool],
                    allow_delegation=False
                )

                # 👇 WRITER PROMPT ME JADOO KIYA HAI 👇
                writer = Agent(
                    role='Pro Hindi SEO Blogger & Content Expansion Expert',
                    goal='Format the scraped data into a highly structured, LONG, and deeply detailed professional Hindi blog post (Minimum 1000 words).',
                    backstory="You are a top-tier Sarkari Job blogger. You NEVER write short summaries or one-liners. You expand every single point into 2-3 detailed sentences so a 10th-pass student can understand easily. You write in highly engaging Hindi (Devanagari).",
                    verbose=True,
                    llm=llm,
                    allow_delegation=False
                )

                # --- TASKS ---
                task1 = Task(
                    description=f"""
                    Job topic: '{job_topic}'.
                    URLs to scrape: {target_urls}
                    
                    INSTRUCTIONS:
                    1. Use the 'scrape_tool' on these specific URLs.
                    2. Extract exhaustive details: Total Vacancies, Category/Department wise vacancies, All Dates, Application Fees, Age Limit rules, and full Education Qualification details.
                    """,
                    expected_output="A comprehensive factual summary extracted strictly from the provided URLs.",
                    agent=researcher
                )

                task2 = Task(
                    description=f"""
                    Using ONLY the facts from the researcher, write a LONG, detailed, and complete SEO blog post in HINDI (Minimum 800-1000 words).
                    
                    CRITICAL INSTRUCTIONS FOR LENGTH & DETAIL:
                    - Do NOT write short 1-line bullet points. Explain each point properly in full Hindi sentences.
                    - The 'Introduction' MUST be at least 2-3 paragraphs long, explaining the importance of this job and golden opportunity for candidates.
                    - Under 'How to Apply', write detailed step-by-step instructions (e.g., "सबसे पहले उम्मीदवार को आधिकारिक वेबसाइट पर जाना होगा... फिर रिक्रूटमेंट पोर्टल पर क्लिक करें...").
                    - Detail the Selection Process properly.
                    
                    You MUST strictly use the following Markdown template:

                    **Meta Title:** [Catchy Title with Post Name and Vacancy]
                    **Meta Description:** [Short 3 line description]
                    **Tags/Keywords:** [Comma separated tags]
                    ---
                    # 🔬 [Job Name]: [Total Vacancies] पदों पर बम्पर भर्ती, पूरी जानकारी यहाँ देखें
                    
                    [2-3 Detailed paragraphs of introduction]
                    
                    ### 📊 भर्ती का संक्षिप्त विवरण (Overview)
                    [Create a Markdown Table with detailed rows]
                    
                    ### 🗓️ महत्वपूर्ण तिथियां (Important Dates)
                    [Detailed bullet points explaining what each date means]
                    
                    ### 💳 आवेदन शुल्क (Application Fee)
                    [Explain fee structure properly for all categories]
                    
                    ### 🎓 आयु सीमा और शैक्षणिक योग्यता (Age & Eligibility)
                    [Detailed paragraphs explaining age limits, relaxation rules, and exact degree/diploma required]
                    
                    ### 🏢 विभागानुसार रिक्तियों का विवरण (Vacancy Details)
                    [Create a proper Markdown Table for category/department data]
                    
                    ### 📝 चयन प्रक्रिया (Selection Process)
                    [Explain written test, document verification, etc., in detailed points]
                    
                    ### 💻 आवेदन कैसे करें? (How to Apply Online)
                    [Step by step detailed guide - minimum 5-6 steps]
                    
                    ### 🔗 महत्वपूर्ण लिंक्स (Important Links)
                    [List official links]
                    """,
                    expected_output="A perfectly formatted, LONG, and highly detailed Hindi Markdown blog post.",
                    agent=writer
                )

                # Crew
                my_crew = Crew(agents=[researcher, writer], tasks=[task1, task2], process=Process.sequential)
                result = my_crew.kickoff()

                st.success("Detailed Scraping & Writing Complete! ✅")
                if hasattr(result, 'raw'):
                    st.markdown(result.raw)
                else:
                    st.markdown(str(result))
            
            except Exception as e:
                st.error(f"An error occurred: {e}")
