import streamlit as st
import os
import datetime
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from crewai_tools import ScrapeWebsiteTool
from duckduckgo_search import DDGS

# 1. Page Config
st.set_page_config(page_title="Sarkari Job Auto-Blogger Pro", page_icon="🔥", layout="wide")
st.title("🔥 Fully Automated Sarkari Blogger 🚀")
st.markdown("बस Job Title डालें। सिस्टम खुद लिंक ढूंढेगा और ब्लॉग छापेगा!")

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

# --- SMART SEARCH FUNCTION (Python Base, No AI Lazy-ness) ---
def get_job_urls(job_title):
    """Sikha-sikhaya Python code jo sirf un 3 websites se exact URL nikalega."""
    try:
        with DDGS() as ddgs:
            # ResultBharat, FreeJobAlert aur Adda247 par search
            search_query = f"{job_title} site:resultbharat.com OR site:freejobalert.com OR site:adda247.com/jobs"
            results = [r for r in ddgs.text(search_query, max_results=2)]
            # Sirf links (URLs) bahar nikalna
            urls = [res['href'] for res in results if 'href' in res]
            return urls
    except Exception as e:
        return []

scrape_tool = ScrapeWebsiteTool()

# --- INPUT ---
job_topic = st.text_input("🎯 Enter Job Title (e.g., SSC CHSL 2026, Rajasthan CET):", value="SSC CHSL Recruitment 2026")

# --- MAIN LOGIC ---
if st.button("🚀 Auto-Search & Generate SEO Blog"):
    if not api_key:
        st.error("❌ Please enter API Key!")
    else:
        # STEP 1: Pehle Python khud link dhoondhega
        with st.spinner('🔍 Searching for the exact job links on ResultBharat & FreeJobAlert...'):
            found_urls = get_job_urls(job_topic)
            
        if not found_urls:
            st.error("❌ In 3 websites par is job ka koi link nahi mila. Kripya naam thoda theek se likhein.")
        else:
            st.success(f"✅ Direct Links Found: {', '.join(found_urls)}")
            
            # STEP 2: Ab AI sirf un links ko padhega (No confusion)
            with st.spinner('🤖 AI is reading the data and filling your SarkariResult template...'):
                try:
                    llm = ChatOpenAI(
                        model_name=current_model,
                        temperature=0.3,
                        api_key=api_key,
                        base_url="https://api.groq.com/openai/v1"
                    )

                    researcher = Agent(
                        role='Data Extractor',
                        goal='Extract strict facts (Dates, Vacancies, Fees) from the given URLs.',
                        backstory="You extract pure facts from job websites. Do not guess any data.",
                        tools=[scrape_tool],
                        llm=llm,
                        verbose=True
                    )

                    writer = Agent(
                        role='SarkariResult Style Formatter',
                        goal='Fill the exact markdown template dynamically.',
                        backstory="You strictly follow the Markdown design. Fill the data accurately.",
                        llm=llm,
                        verbose=True
                    )

                    # Task 1 me hum direct wo URL de rahe hain jo Python ne dhoondha hai
                    target_urls_str = ", ".join(found_urls)
                    task1 = Task(
                        description=f"""
                        Scrape these specific URLs: {target_urls_str}
                        Extract Total Vacancies, Start/End Dates, Fees for all categories, Age Limit, and Eligibility for '{job_topic}'.
                        """,
                        expected_output="Pure factual data extracted from the specific websites.",
                        agent=researcher
                    )

                    task2 = Task(
                        description=f"""
                        You MUST strictly use the exact Markdown format provided below. Fill in the brackets [ ] dynamically with the exact data from the researcher. 
                        If missing, write "जल्द उपलब्ध होगा (Update Soon)".

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
                        2.  **[Step 2 - e.g., Document Verification (DV)]**

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

                    st.success("✅ Fully Automated SEO Blog Ready!")
                    st.markdown(result.raw)
                
                except Exception as e:
                    st.error(f"Error: {e}")
