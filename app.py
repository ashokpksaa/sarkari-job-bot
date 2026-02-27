import streamlit as st
import os
import requests
from bs4 import BeautifulSoup
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from crewai.tools import tool

# 1. Page Config
st.set_page_config(page_title="Sarkari Job Pro Auto-Blogger", page_icon="🔥", layout="wide")
st.title("🔥 100% Accurate Sarkari Blogger (Surgeon Mode) 🚀")
st.markdown("अब यह टूल वेबसाइट का साइडबार और कचरा हटाकर सिर्फ असली जॉब पढ़ेगा!")

# 2. Configuration
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.secrets.get("GROQ_API_KEY", "")
    if not api_key:
        api_key = st.text_input("Enter Groq API Key:", type="password")

current_model = "llama-3.3-70b-versatile"

if api_key:
    os.environ["OPENAI_API_KEY"] = api_key 
    os.environ["OPENAI_BASE_URL"] = "https://api.groq.com/openai/v1"

# --- CUSTOM SURGEON SCRAPER TOOL ---
@tool
def smart_scraper(url: str):
    """Scrapes ONLY the main content of a job website, destroying sidebars, menus, and ads."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')

        # कचरा साफ़ करना (Removing Sidebar, Header, Footer, Nav)
        for junk in soup(['aside', 'nav', 'footer', 'header', 'script', 'style', 'div.sidebar', 'div.widget']):
            junk.decompose()

        # सिर्फ मुख्य आर्टिकल खोजना
        main_content = soup.find('article') or soup.find('main') or soup.body
        if main_content:
            # फालतू स्पेस हटाकर क्लीन टेक्स्ट निकालना
            text = main_content.get_text(separator='\n', strip=True)
            # AI को कन्फ्यूज़न से बचाने के लिए शुरूआती 6000 अक्षर ही भेजना (जहाँ मेन डिटेल्स होती हैं)
            return text[:6000] 
        return "No main content found."
    except Exception as e:
        return f"Error scraping: {e}"

# --- INPUT SECTION ---
st.subheader("🎯 Step 1: Job Details")
job_topic = st.text_input("Enter Job Title (e.g., RRB Group D Recruitment 2026):", value="RRB Group D Recruitment 2026")

st.subheader("🔗 Step 2: Paste Direct Link")
target_url = st.text_input("Job Website का सीधा लिंक यहाँ पेस्ट करें:", placeholder="https://jobapply24.in/...")

# --- MAIN LOGIC ---
if st.button("🚀 Generate 100% Accurate Blog"):
    if not api_key:
        st.error("❌ Please enter API Key!")
    elif not target_url.strip():
        st.error("❌ Kripya Step 2 mein website ka link zaroor dalein!")
    else:
        with st.spinner('✂️ Cleaning website junk and reading main article...'):
            try:
                llm = ChatOpenAI(
                    model_name=current_model,
                    temperature=0.1, 
                    api_key=api_key,
                    base_url="https://api.groq.com/openai/v1"
                )

                researcher = Agent(
                    role='Targeted Data Extractor',
                    goal=f'Extract strict facts for "{job_topic}" from the cleaned text.',
                    backstory="You are an expert data extractor. The text provided to you has been cleaned of sidebars. Extract the exact Dates, Vacancies, and Fees.",
                    tools=[smart_scraper], # Custom tool lagaya hai
                    llm=llm,
                    verbose=True
                )

                writer = Agent(
                    role='SarkariResult Style Formatter',
                    goal='Fill the exact markdown template dynamically.',
                    backstory="You strictly follow the Markdown design. Fill the data accurately. If missing, write 'जल्द उपलब्ध होगा (Update Soon)'.",
                    llm=llm,
                    verbose=True
                )

                task1 = Task(
                    description=f"""
                    Use the 'smart_scraper' tool on this URL: {target_url}
                    Extract Total Vacancies, Start/End Dates, Fees for all categories, Age Limit, and Eligibility SPECIFICALLY for '{job_topic}'.
                    """,
                    expected_output="Pure factual data.",
                    agent=researcher
                )

                task2 = Task(
                    description=f"""
                    You MUST strictly use the exact Markdown format provided below. Fill in the brackets [ ] dynamically with the exact data from the researcher. 

                    **Meta Title:** [Job Title]: [Total Vacancy] पदों पर बम्पर भर्ती
                    **Meta Description:** [Board Name] द्वारा [Job Title] के पदों पर अधिसूचना जारी। आयु, योग्यता और ऑनलाइन आवेदन की जानकारी यहाँ पढ़ें।
                    **Tags:** Sarkari Result, [Board Name], Govt Jobs 2026

                    ---

                    # 🚨 [Job Title]: [Total Vacancy] पदों पर बम्पर भर्ती, ऑनलाइन आवेदन शुरू
                    
                    > **📌 संक्षिप्त जानकारी (Short Info):** [Board Name] ने [Job Title] के **[Total Vacancy]** पदों पर सीधी भर्ती के लिए आधिकारिक अधिसूचना जारी कर दी है। जो भी उम्मीदवार इस भर्ती में रुचि रखते हैं और पात्रता पूरी करते हैं, वे **[Start Date]** से **[End Date]** तक ऑनलाइन आवेदन कर सकते हैं। 

                    ---

                    ## 📊 भर्ती का अवलोकन (Recruitment Overview)
                    | संगठन का नाम (Board) | [Board Name] |
                    |---|---|
                    | **पद का नाम (Post Name)** | [Job Title] |
                    | **कुल पद (Total Vacancy)** | [Total Vacancy] पद |
                    | **नौकरी का स्थान (Job Location)**| [Location - e.g., All India / State Name] |
                    | **आधिकारिक वेबसाइट** | [Official Website URL] |

                    ---

                    ## 🗓️ महत्वपूर्ण तिथियां (Important Dates)
                    * **अधिसूचना जारी होने की तिथि:** [Notification Date]
                    * **ऑनलाइन आवेदन शुरू (Apply Start):** 🟢 [Start Date]
                    * **आवेदन की अंतिम तिथि (Last Date):** 🔴 **[End Date]**
                    * **परीक्षा शुल्क भुगतान अंतिम तिथि:** [Fee Last Date]
                    * **परीक्षा तिथि (Exam Date):** 📅 [Exam Date]

                    ---

                    ## 💳 आवेदन शुल्क (Application Fee)
                    * **General / OBC / EWS:** ₹ [Amount]
                    * **SC / ST / Divyang / Female:** ₹ [Amount]
                    * *नोट:* परीक्षा शुल्क का भुगतान ऑनलाइन माध्यम से करें।

                    ---

                    ## 🎓 आयु सीमा (Age Limit) 
                    * **न्यूनतम आयु (Minimum Age):** [Age] वर्ष
                    * **अधिकतम आयु (Maximum Age):** [Age] वर्ष
                    * *आयु में छूट:* सरकारी नियमानुसार लागू।

                    ---

                    ## 🏢 रिक्ति विवरण और शैक्षणिक योग्यता (Vacancy Details & Eligibility)

                    | पद का नाम (Post Name) | कुल पद | शैक्षणिक योग्यता (Eligibility Details) |
                    |---|---|---|
                    | [Post Name 1] | [Count] | [Strictly mention the exact 10th/12th/Degree requirements] |
                    | [Post Name 2] | [Count] | [Eligibility Details] |

                    ---

                    ## 📝 चयन प्रक्रिया (Selection Process)
                    1.  **[Step 1 - e.g., Written Exam / CBT]**
                    2.  **[Step 2 - e.g., Physical Test (PET/PST) if applicable]**
                    3.  **[Step 3 - e.g., Document Verification (DV)]**

                    ---

                    ## 💻 ऑनलाइन आवेदन कैसे करें? (How to Apply Online)
                    1.  सबसे पहले आधिकारिक वेबसाइट **[Official Website URL]** पर जाएं।
                    2.  लॉगिन करें या नया 'Registration' बनाएं।
                    3.  'Recruitment Portal' या 'Latest Jobs' में जाकर **[Job Title]** पर क्लिक करें।
                    4.  अपना आवेदन फॉर्म भरें और दस्तावेज़ अपलोड करें।
                    5.  अपनी श्रेणी के अनुसार आवेदन शुल्क का भुगतान करें।
                    6.  फॉर्म को 'Final Submit' करें और प्रिंट आउट लें।

                    ---

                    ## 🔗 महत्वपूर्ण लिंक्स (Important Links)
                    * **ऑनलाइन आवेदन करें (Apply Online):** [Direct Link]
                    * **आधिकारिक वेबसाइट (Official Website):** [Official Link]

                    """,
                    expected_output="A perfectly formatted SarkariResult style blog post filled dynamically.",
                    agent=writer
                )

                my_crew = Crew(agents=[researcher, writer], tasks=[task1, task2])
                result = my_crew.kickoff()

                st.success("✅ 100% Accurate SEO Blog Ready!")
                st.markdown(result.raw)
            
            except Exception as e:
                st.error(f"Error: {e}")
