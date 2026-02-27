import streamlit as st
import os
import datetime
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

# 1. Page Config
st.set_page_config(page_title="Sarkari Job Pro Auto-Blogger", page_icon="🔥", layout="wide")
st.title("🔥 100% Accurate Sarkari Blogger (Smart Text Mode) 🚀")
st.markdown("वेबसाइट से असली जानकारी कॉपी करें और यहाँ पेस्ट करें। AI उसे समझकर परफेक्ट डिज़ाइन करेगा!")

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
raw_data = st.text_area("वेबसाइट का टेक्स्ट यहाँ पेस्ट करें (AI खुद समझकर टेबल सेट कर लेगा):", height=200)

# --- MAIN LOGIC ---
if st.button("🚀 Generate Smart SEO Blog"):
    if not api_key:
        st.error("❌ Please enter API Key!")
    elif not raw_data.strip():
        st.error("❌ Kripya Step 2 mein text paste karein!")
    else:
        with st.spinner('🤖 AI is applying Common Sense and formatting your blog...'):
            try:
                llm = ChatOpenAI(
                    model_name=current_model,
                    temperature=0.2, # Thodi si common sense allow ki hai
                    api_key=api_key,
                    base_url="https://api.groq.com/openai/v1"
                )

                writer = Agent(
                    role='Senior Sarkari Blogger',
                    goal='Format the raw text beautifully using common sense.',
                    backstory="""You are a smart blogger. When users paste raw text, tables often break. 
                    YOUR RULES:
                    1. Use common sense. If a general eligibility (like 10th Pass/ITI) is mentioned, apply it to all related posts. 
                    2. DO NOT create 15 rows of 'Update Soon' for posts if their individual vacancies aren't listed. Combine them into one row like 'Various Group D Posts'.
                    3. If links say 'Click Here', use the Official Website URL instead of writing 'Update Soon'.
                    4. If job is Railways, SSC, etc., set Job Location to 'All India' automatically.""",
                    llm=llm,
                    verbose=True
                )

                task1 = Task(
                    description=f"""
                    Here is the RAW TEXT for '{job_topic}':
                    
                    {raw_data}
                    
                    Fill the exact Markdown format below. Use your intelligence to fix broken tables from the raw text. 

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
                    | **नौकरी का स्थान (Job Location)**| [Infer location, e.g., All India or Specific State] |
                    | **आधिकारिक वेबसाइट** | [Extract or infer Official Website URL] |

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
                    | [Smartly combine post names if needed, e.g., 'Various Group D Posts'] | [Total Vacancy] | [Apply the general eligibility found in text (e.g., 10th Pass/ITI)] |

                    ---

                    ## 📝 चयन प्रक्रिया (Selection Process)
                    [List the selection steps exactly as found in the text, using bullet points]

                    ---

                    ## 💻 ऑनलाइन आवेदन कैसे करें? (How to Apply Online)
                    1.  सबसे पहले आधिकारिक वेबसाइट पर जाएं।
                    2.  लॉगिन करें या नया 'Registration' बनाएं।
                    3.  'Recruitment Portal' में जाकर **[Job Title]** पर क्लिक करें।
                    4.  अपना आवेदन फॉर्म भरें और दस्तावेज़ अपलोड करें।
                    5.  अपनी श्रेणी के अनुसार आवेदन शुल्क का भुगतान करें।
                    6.  फॉर्म को 'Final Submit' करें और प्रिंट आउट लें।

                    ---

                    ## 🔗 महत्वपूर्ण लिंक्स (Important Links)
                    * **ऑनलाइन आवेदन करें (Apply Online):** [Official Website URL]
                    * **आधिकारिक वेबसाइट (Official Website):** [Official Website URL]

                    """,
                    expected_output="A perfectly formatted SarkariResult style blog post, with intelligently formatted tables.",
                    agent=writer
                )

                my_crew = Crew(agents=[writer], tasks=[task1])
                result = my_crew.kickoff()

                st.success("✅ Smart SEO Blog Ready!")
                st.markdown(result.raw)
            
            except Exception as e:
                st.error(f"Error: {e}")
