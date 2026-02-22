import streamlit as st
import os
import datetime
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from crewai_tools import ScrapeWebsiteTool # <--- Naya Tool (Web Scraper)

today_date = datetime.datetime.now().strftime("%B %d, %Y")

# 1. Page Config
st.set_page_config(page_title="Sarkari Job Auto-Blogger Pro", page_icon="🔬", layout="wide")
st.title("🔬 Sarkari Job Auto-Blogger Pro (Scraper Mode) 🚀")
st.markdown("Enter a job topic and your trusted website URLs. The AI will scrape ONLY these websites and write a perfect Hindi SEO blog.")

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

# Yahan user apni pasand ki websites daal sakta hai
default_urls = "https://www.resultbharat.com/RSSB-Lab-Assistant_Advt-05-2026.html, https://www.freejobalert.com/articles/rssb-lab-assistant-recruitment-2026-apply-online-for-804-posts-3035740, https://www.adda247.com/exams/rajasthan/rssb-lab-assistant-recruitment-2026/"
target_urls = st.text_area("Enter Trusted Website URLs (Comma separated):", value=default_urls, height=100)

# --- TOOL DEFINITION ---
# Ye tool kisi bhi website ke andar ghuskar uska data padh sakta hai
scrape_tool = ScrapeWebsiteTool()

# --- MAIN LOGIC ---
if st.button("🚀 Scrape & Generate Blog Post"):
    if not api_key:
        st.error("❌ Groq API Key missing! Please add it.")
    else:
        with st.spinner('🤖 AI is scraping your provided websites and writing the blog... (This may take 1-2 minutes)'):
            try:
                llm = ChatOpenAI(
                    model_name="llama-3.3-70b-versatile",
                    temperature=0.3, # Low creativity for factual accuracy
                    api_key=api_key,
                    base_url="https://api.groq.com/openai/v1"
                )

                # --- AGENTS ---
                researcher = Agent(
                    role='Senior Web Scraper & Fact Checker',
                    goal='Scrape the provided URLs and extract 100% accurate job details.',
                    backstory="You are an expert data extractor. You will use the ScrapeWebsiteTool to read the content of the specific URLs provided by the user. Extract exact Dates, Vacancy numbers, Fees, and Eligibility. Do not search the whole internet, ONLY scrape the provided links.",
                    verbose=True,
                    llm=llm,
                    tools=[scrape_tool],
                    allow_delegation=False
                )

                writer = Agent(
                    role='Pro Hindi SEO Blogger',
                    goal='Format the scraped data into a highly structured, professional Hindi blog post.',
                    backstory="You are a top-tier Sarkari Job blogger. You strictly follow formatting templates. You write in professional Hindi (Devanagari) mixed with common English terms.",
                    verbose=True,
                    llm=llm,
                    allow_delegation=False
                )

                # --- TASKS ---
                task1 = Task(
                    description=f"""
                    The job topic is: '{job_topic}'.
                    Here are the URLs you MUST scrape: {target_urls}
                    
                    INSTRUCTIONS:
                    1. Use the 'scrape_tool' on these specific URLs to extract information.
                    2. Find the exact Total Vacancies, Category-wise vacancies, Start Date, Last Date, Exam Date, Application Fees, Age Limit, and Education Qualification.
                    3. Compile this into a detailed factual summary.
                    """,
                    expected_output="A comprehensive factual summary extracted strictly from the provided URLs.",
                    agent=researcher
                )

                task2 = Task(
                    description=f"""
                    Using ONLY the facts from the researcher, write a complete SEO blog post in HINDI.
                    You MUST strictly use the following Markdown template and emojis:

                    **Meta Title:** [Catchy Title with Post Name and Vacancy]
                    **Meta Description:** [Short 2 line description]
                    **Tags/Keywords:** [Comma separated tags]
                    ---
                    # 🔬 [Job Name]: [Total Vacancies] पदों पर बम्पर भर्ती
                    
                    [1-2 paragraphs of introduction in Hindi]
                    
                    ### 📊 भर्ती का संक्षिप्त विवरण (Overview)
                    [Create a Markdown Table with Board, Post Name, Total Vacancy, Location, Salary, Website]
                    
                    ### 🗓️ महत्वपूर्ण तिथियां (Important Dates)
                    [Bullet points with emojis for dates]
                    
                    ### 💳 आवेदन शुल्क (Application Fee)
                    [Bullet points for category wise fees]
                    
                    ### 🎓 आयु सीमा और शैक्षणिक योग्यता (Age & Eligibility)
                    [Detailed bullets]
                    
                    ### 🏢 विभागानुसार रिक्तियों का विवरण (Vacancy Details)
                    [Create a Markdown Table if category/department data is available, otherwise normal bullets]
                    
                    ### 📝 चयन प्रक्रिया (Selection Process)
                    [Numbered list]
                    
                    ### 💻 आवेदन कैसे करें? (How to Apply Online)
                    [Step by step numbered list]
                    
                    ### 🔗 महत्वपूर्ण लिंक्स (Important Links)
                    [List the official links if found]
                    """,
                    expected_output="A perfectly formatted Hindi Markdown blog post following the exact template provided.",
                    agent=writer
                )

                # Crew
                my_crew = Crew(agents=[researcher, writer], tasks=[task1, task2], process=Process.sequential)
                result = my_crew.kickoff()

                st.success("Scraping Complete! Factual Blog Post Generated! ✅")
                if hasattr(result, 'raw'):
                    st.markdown(result.raw)
                else:
                    st.markdown(str(result))
            
            except Exception as e:
                st.error(f"An error occurred: {e}")
