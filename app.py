import streamlit as st
import os
import datetime
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

# 1. Page Config
st.set_page_config(page_title="Sarkari Job Pro Auto-Blogger", page_icon="🔥", layout="wide")
st.title("🔥 100% Accurate Sarkari Blogger (Manual Text Mode) 🚀")
st.markdown("वेबसाइट से असली जानकारी कॉपी करें और यहाँ पेस्ट करें। AI उसे SarkariResult स्टाइल में सजा देगा!")

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

# --- INPUT SECTION ---
st.subheader("🎯 Step 1: Job Details")
job_topic = st.text_input("Enter Job Title (e.g., RRB Group D Recruitment 2026):", value="RRB Group D Recruitment 2026")

st.subheader("📝 Step 2: Paste Raw Content")
raw_data = st.text_area("किसी भी वेबसाइट (ResultBharat/Adda247) से सिर्फ काम का टेक्स्ट (तारीखें, फीस, पद) कॉपी करके यहाँ पेस्ट करें:", height=200)

# --- MAIN LOGIC ---
if st.button("🚀 Generate SEO Blog from Text"):
    if not api_key:
        st.error("❌ Please enter API Key!")
    elif not raw_data.strip():
        st.error("❌ Kripya Step 2 mein text paste karein!")
    else:
        with st.spinner('🤖 AI is formatting your exact text into the template...'):
            try:
                llm = ChatOpenAI(
                    model_name=current_model,
                    temperature=0.0, # Zero creativity, strict formatting
                    api_key=api_key,
                    base_url="https://api.groq.com/openai/v1"
                )

                writer = Agent(
                    role='SarkariResult Style Formatter',
                    goal='Fill the exact markdown template dynamically using ONLY the provided raw text.',
                    backstory="You strictly follow the Markdown design. You ONLY use the text provided by the user. If data is missing in the text, write 'जल्द उपलब्ध होगा (Update Soon)'.",
                    llm=llm,
                    verbose=True
                )

                task1 = Task(
                    description=f"""
                    Here is the RAW TEXT provided by the user for '{job_topic}':
                    
                    {raw_data}
                    
                    You MUST strictly use the exact Markdown format provided below. Fill in the brackets [ ] dynamically with the exact data from the RAW TEXT above. 
                    Do not guess or invent data. If a specific detail is not in the text, write "जल्द उपलब्ध होगा (Update Soon)".

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
                    expected_output="A perfectly formatted SarkariResult style blog post filled ONLY with the provided raw text.",
                    agent=writer
                )

                # Ab sirf ek hi task aur ek hi agent hai (Fast & Accurate)
                my_crew = Crew(agents=[writer], tasks=[task1])
                result = my_crew.kickoff()

                st.success("✅ 100% Accurate SEO Blog Ready!")
                st.markdown(result.raw)
            
            except Exception as e:
                st.error(f"Error: {e}")
