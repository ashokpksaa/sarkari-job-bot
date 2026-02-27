import streamlit as st
import os
import datetime
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from crewai_tools import ScrapeWebsiteTool
from crewai.tools import tool
from duckduckgo_search import DDGS

# 1. Page Config
st.set_page_config(page_title="Sarkari Job Auto-Blogger Pro", page_icon="🔥", layout="wide")
st.title("🔥 Fully Automated Sarkari Blogger 🚀")
st.markdown("बस Job Title डालें। AI खुद ResultBharat, FreeJobAlert और Adda247 से डेटा ढूंढकर लाएगा!")

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

# --- CUSTOM TOOLS ---

@tool
def search_trusted_sites(job_title: str):
    """Search for the job strictly on ResultBharat, FreeJobAlert, and Adda247 to find the exact URL."""
    try:
        with DDGS() as ddgs:
            # Query ko chota rakha taaki crash na ho
            short_query = " ".join(job_title.split()[:5])
            # Sirf in 3 websites par search karega
            search_query = f"{short_query} site:resultbharat.com OR site:freejobalert.com OR site:adda247.com/jobs"
            results = [r for r in ddgs.text(search_query, max_results=3)]
            return str(results)
    except Exception as e:
        return f"Search Error: {e}"

scrape_tool = ScrapeWebsiteTool()

# --- INPUT ---
# Ab URL daalne ka box hata diya hai, sirf Title chahiye!
job_topic = st.text_input("🎯 Enter Job Title (e.g., SSC CHSL 2026, Railway ALP, RSSB Lab Assistant):", value="SSC CHSL Recruitment 2026")

# --- MAIN LOGIC ---
if st.button("🚀 Auto-Search & Generate SEO Blog"):
    if not api_key:
        st.error("❌ Please enter API Key!")
    else:
        with st.spinner('🤖 AI is searching ResultBharat/FreeJobAlert, reading data, and designing your blog...'):
            try:
                llm = ChatOpenAI(
                    model_name=current_model,
                    temperature=0.3, # Low temp for strict formatting
                    api_key=api_key,
                    base_url="https://api.groq.com/openai/v1"
                )

                # Researcher Agent (Jo URL dhoondhega aur scrape karega)
                researcher = Agent(
                    role='Auto Data Fetcher',
                    goal='Find the exact job URL from trusted sites and extract pure facts.',
                    backstory="""You are a strict data bot. 
                    FIRST, use 'search_trusted_sites' to find the link for the job. 
                    SECOND, use 'scrape_tool' on that exact link to get dates, fees, and vacancies.""",
                    tools=[search_trusted_sites, scrape_tool],
                    llm=llm,
                    verbose=True
                )

                # Writer Agent (Jo SarkariResult design me likhega)
                writer = Agent(
                    role='SarkariResult Style Formatter',
                    goal='Fill the exact markdown template dynamically without adding fake stories.',
                    backstory="You strictly follow the provided Markdown design. You dynamically detect the Board Name and Location from the data. No essays.",
                    llm=llm,
                    verbose=True
                )

                task1 = Task(
                    description=f"""
                    Job Topic: '{job_topic}'
                    
                    STEP 1: Use 'search_trusted_sites' to search for this job.
                    STEP 2: From the results, find the URL.
                    STEP 3: Use 'scrape_tool' to read that URL.
                    STEP 4: Extract Total Vacancies, Start/End Dates, Fees for all categories, Age Limit, and Eligibility.
                    """,
                    expected_output="Pure factual data extracted from the specific trusted website.",
                    agent=researcher
                )

                task2 = Task(
                    description=f"""
                    You MUST strictly use the exact Markdown format provided below. Fill in the brackets [ ] dynamically with the exact data from the researcher. 
                    Do NOT invent data. If missing, write "जल्द उपलब्ध होगा (Update Soon)".

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
