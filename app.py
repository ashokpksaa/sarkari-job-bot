import streamlit as st
import os
import datetime
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from crewai_tools import ScrapeWebsiteTool

# 1. Page Config
st.set_page_config(page_title="Sarkari Job Auto-Blogger Pro", page_icon="🔥", layout="wide")
st.title("🔥 SarkariResult Style Auto-Blogger 🚀")

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

# 3. Inputs
job_topic = st.text_input("Enter Job Topic:", value="RSSB Lab Assistant Recruitment 2026")
default_urls = "https://www.resultbharat.com/RSSB-Lab-Assistant_Advt-05-2026.html, https://www.freejobalert.com/articles/rssb-lab-assistant-recruitment-2026-apply-online-for-804-posts-3035740"
target_urls = st.text_area("Target Links:", value=default_urls, height=80)

scrape_tool = ScrapeWebsiteTool()

if st.button("🚀 Generate SEO Professional Blog"):
    if not api_key:
        st.error("❌ Please enter API Key!")
    else:
        with st.spinner('🤖 Extracting data and formatting like SarkariResult...'):
            try:
                llm = ChatOpenAI(
                    model_name=current_model,
                    temperature=0.3, # Temperature bilkul kam taaki template follow kare
                    api_key=api_key,
                    base_url="https://api.groq.com/openai/v1"
                )

                researcher = Agent(
                    role='Data Extractor',
                    goal='Extract all exact dates, vacancy tables, and fees.',
                    backstory="You extract pure facts from job websites. No fluff.",
                    tools=[scrape_tool],
                    llm=llm,
                    verbose=True
                )

                writer = Agent(
                    role='Pro SEO Sarkari Blogger',
                    goal='Fill the extracted data into the strict markdown template.',
                    backstory="You are a strict data formatter. You DO NOT write essays or long boring paragraphs. You strictly fill the provided Markdown template with facts.",
                    llm=llm,
                    verbose=True
                )

                task1 = Task(
                    description=f"Scrape {target_urls} for {job_topic}. Extract Category-wise vacancies, Fees, Dates, and specific Eligibility.",
                    expected_output="Pure factual data points.",
                    agent=researcher
                )

                task2 = Task(
                    description=f"""
                    You MUST strictly use the exact Markdown format provided below. Do NOT add extra paragraphs. Just fill in the brackets [ ] with the data from the researcher. If a piece of data is missing, write "जल्द उपलब्ध होगा (Update Soon)".

                    **Meta Title:** [Job Title]: [Total Vacancy] पदों पर बम्पर भर्ती
                    **Meta Description:** राजस्थान कर्मचारी चयन बोर्ड (RSSB) द्वारा [Job Title] के [Total Vacancy] पदों पर अधिसूचना जारी। आयु, योग्यता और ऑनलाइन आवेदन की जानकारी यहाँ पढ़ें।
                    **Tags:** Sarkari Result, RSSB Recruitment 2026, Rajasthan Govt Jobs

                    ---

                    # 🚨 [Job Title]: [Total Vacancy] पदों पर बम्पर भर्ती, ऑनलाइन आवेदन शुरू
                    
                    > **📌 संक्षिप्त जानकारी (Short Info):** राजस्थान कर्मचारी चयन बोर्ड (RSSB) ने [Post Name] के **[Total Vacancy]** पदों पर सीधी भर्ती के लिए आधिकारिक अधिसूचना जारी कर दी है। जो भी उम्मीदवार इस भर्ती में रुचि रखते हैं और पात्रता पूरी करते हैं, वे **[Start Date]** से **[End Date]** तक ऑनलाइन आवेदन कर सकते हैं। आयु सीमा, सिलेबस, चयन प्रक्रिया और वेतन की पूरी जानकारी के लिए नीचे दिया गया आर्टिकल पढ़ें।

                    ---

                    ## 📊 भर्ती का अवलोकन (Recruitment Overview 2026)
                    | संगठन का नाम (Board) | राजस्थान कर्मचारी चयन बोर्ड (RSSB) |
                    |---|---|
                    | **पद का नाम (Post Name)** | [Post Name] |
                    | **कुल पद (Total Vacancy)** | [Total Vacancy] पद |
                    | **नौकरी का स्थान (Job Location)**| राजस्थान |
                    | **आधिकारिक वेबसाइट** | https://rssb.rajasthan.gov.in/ |

                    ---

                    ## 🗓️ महत्वपूर्ण तिथियां (Important Dates)
                    * **अधिसूचना जारी होने की तिथि:** [Date]
                    * **ऑनलाइन आवेदन शुरू (Apply Start):** 🟢 [Date]
                    * **आवेदन की अंतिम तिथि (Last Date):** 🔴 **[Date]**
                    * **परीक्षा शुल्क भुगतान अंतिम तिथि:** [Date]
                    * **परीक्षा तिथि (Exam Date):** 📅 [Date]
                    * **एडमिट कार्ड उपलब्ध:** परीक्षा से पहले

                    ---

                    ## 💳 आवेदन शुल्क (Application Fee)
                    * **General / OBC / EWS:** ₹ [Amount]
                    * **SC / ST / Divyang:** ₹ [Amount]
                    * *नोट:* परीक्षा शुल्क का भुगतान केवल ऑनलाइन माध्यम (Debit Card / Credit Card / Net Banking / E-Mitra) से करें।

                    ---

                    ## 🎓 आयु सीमा (Age Limit) 
                    * **न्यूनतम आयु (Minimum Age):** [Age] वर्ष
                    * **अधिकतम आयु (Maximum Age):** [Age] वर्ष
                    * *आयु में छूट (Age Relaxation):* सरकारी नियमानुसार (SC/ST/OBC को ऊपरी आयु सीमा में 5-10 वर्ष की छूट मिलेगी)।

                    ---

                    ## 🏢 रिक्ति विवरण और शैक्षणिक योग्यता (Vacancy Details & Eligibility)

                    | पद का नाम (Post Name) | कुल पद | शैक्षणिक योग्यता (Eligibility Details) |
                    |---|---|---|
                    | [Post Name 1] | [Count] | [Strictly mention the exact Degree/Diploma/12th pass requirements here in bullet points] |
                    | [Post Name 2] | [Count] | [Eligibility Details] |

                    *(यदि अलग-अलग विभागों की जानकारी उपलब्ध है, तो उसे यहाँ विस्तार से लिखें)*

                    ---

                    ## 📝 चयन प्रक्रिया (Selection Process)
                    1.  **लिखित परीक्षा (Written Exam):** [Explain in 1 line]
                    2.  **दस्तावेज़ सत्यापन (Document Verification):** [Explain in 1 line]
                    3.  **मेडिकल फिटनेस टेस्ट (Medical Test):** [Explain in 1 line]

                    ---

                    ## 💻 ऑनलाइन आवेदन कैसे करें? (How to Apply Online)
                    1.  सबसे पहले उम्मीदवार आधिकारिक वेबसाइट **https://sso.rajasthan.gov.in/** पर जाएं।
                    2.  लॉगिन करें या नया 'Registration' (SSO ID) बनाएं।
                    3.  'Recruitment Portal' पर क्लिक करें और **[Job Title]** के लिंक पर जाएं।
                    4.  अपना आवेदन फॉर्म ध्यानपूर्वक भरें और आवश्यक दस्तावेज़, फोटो और हस्ताक्षर अपलोड करें।
                    5.  अपनी श्रेणी के अनुसार आवेदन शुल्क का भुगतान करें।
                    6.  फॉर्म को 'Final Submit' करें और भविष्य के संदर्भ के लिए प्रिंट आउट ज़रूर लें।

                    ---

                    ## 🔗 महत्वपूर्ण लिंक्स (Important Links)
                    * **ऑनलाइन आवेदन करें (Apply Online):** [SSO Portal Link](https://sso.rajasthan.gov.in/)
                    * **आधिकारिक वेबसाइट (Official Website):** [RSSB Link](https://rssb.rajasthan.gov.in/)

                    """,
                    expected_output="A perfectly formatted SarkariResult style blog post.",
                    agent=writer
                )

                my_crew = Crew(agents=[researcher, writer], tasks=[task1, task2])
                result = my_crew.kickoff()

                st.success("Professional SEO Blog Ready! ✅")
                st.markdown(result.raw)
            
            except Exception as e:
                st.error(f"Error: {e}")
