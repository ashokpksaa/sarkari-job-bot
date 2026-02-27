import streamlit as st
import os
import datetime
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

# 1. Page Config
st.set_page_config(page_title="Sarkari Job Pro Auto-Blogger", page_icon="🔥", layout="wide")
st.title("🔥 Mega Sarkari Blogger (No Data Loss Mode) 🚀")
st.markdown("वेबसाइट से असली जानकारी कॉपी करें। AI बिना कुछ काटे उसे पूरी डिटेल के साथ छापेगा!")

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
raw_data = st.text_area("वेबसाइट का पूरा टेक्स्ट (ज़ोन-वाइज़, फिजिकल टेस्ट, फीस सब कुछ) यहाँ पेस्ट करें:", height=250)

# --- MAIN LOGIC ---
if st.button("🚀 Generate Full Detail SEO Blog"):
    if not api_key:
        st.error("❌ Please enter API Key!")
    elif not raw_data.strip():
        st.error("❌ Kripya Step 2 mein text paste karein!")
    else:
        with st.spinner('🤖 AI is reading your text and generating FULL DETAILS without cutting anything...'):
            try:
                llm = ChatOpenAI(
                    model_name=current_model,
                    temperature=0.1, # Keep it strictly focused on the raw data
                    api_key=api_key,
                    base_url="https://api.groq.com/openai/v1"
                )

                writer = Agent(
                    role='Senior Sarkari Blogger',
                    goal='Format the raw text into a detailed SarkariResult style blog WITHOUT losing any data.',
                    backstory="""You are an expert data formatter. Your biggest rule is: DO NOT SUMMARIZE OR DELETE DATA. 
                    If the user provides Zone-wise vacancies, Physical test details, Refund amounts, or Salary, you MUST create separate markdown tables/sections for them. You capture everything beautifully.""",
                    llm=llm,
                    verbose=True
                )

                task1 = Task(
                    description=f"""
                    Here is the RAW TEXT provided by the user for '{job_topic}':
                    
                    {raw_data}
                    
                    CRITICAL INSTRUCTIONS: 
                    1. DO NOT shortcut the tables. If there are 15 posts, list all 15. If there is a Zone-wise vacancy table, create a complete Zone-wise table.
                    2. If Physical Eligibility (Running/Weight) is mentioned, create a separate section for it.
                    3. Include Fee Refund details if present.
                    4. Include Salary details if present.
                    5. Include FAQs if present.

                    Use this dynamic Markdown template (add extra sections like Zone-Wise Vacancy or Physical Test if they exist in the raw text):

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
                    | **नौकरी का स्थान (Job Location)**| [Infer location, e.g., All India] |
                    | **वेतन (Salary)** | [Add Salary if available in text] |

                    ---

                    ## 🗓️ महत्वपूर्ण तिथियां (Important Dates)
                    * **अधिसूचना जारी होने की तिथि:** [Notification Date]
                    * **ऑनलाइन आवेदन शुरू (Apply Start):** 🟢 [Start Date]
                    * **आवेदन की अंतिम तिथि (Last Date):** 🔴 **[End Date]**
                    * **परीक्षा शुल्क भुगतान अंतिम तिथि:** [Fee Last Date]
                    * **परीक्षा तिथि (Exam Date):** 📅 [Exam Date]

                    ---

                    ## 💳 आवेदन शुल्क और रिफंड (Application Fee & Refund)
                    * **General / OBC / EWS:** ₹ [Amount]
                    * **SC / ST / Divyang / Female:** ₹ [Amount]
                    * **फीस रिफंड (Refund on appearing in CBT):** [Mention refund details exactly as given in text, e.g., Gen/OBC: Rs 400, SC/ST: Rs 250]

                    ---

                    ## 🎓 आयु सीमा (Age Limit) 
                    * **न्यूनतम आयु (Minimum Age):** [Age] वर्ष
                    * **अधिकतम आयु (Maximum Age):** [Age] वर्ष
                    * *आयु में छूट:* सरकारी नियमानुसार लागू।

                    ---

                    ## 🏢 रिक्ति विवरण और शैक्षणिक योग्यता (Vacancy & Eligibility Details)

                    | विभाग / पद का नाम (Department / Post Name) | शैक्षणिक योग्यता (Eligibility Details) |
                    |---|---|
                    | [List EVERY SINGLE POST AND DEPARTMENT found in the text accurately] | [Match the exact eligibility] |

                    ---

                    ## 🏃‍♂️ शारीरिक योग्यता (Physical Eligibility) - [Remove this section ONLY if not in raw text]
                    * **Male Candidates:** [List details like weight lifting, running time exactly as in text]
                    * **Female Candidates:** [List details exactly as in text]

                    ---

                    ## 🌍 ज़ोन-वाइज़ रिक्ति विवरण (Zone-Wise Vacancy Details) - [Remove this section ONLY if not in raw text]
                    | Railway Zone | UR | SC | ST | OBC | EWS | Total |
                    |---|---|---|---|---|---|---|
                    | [List EVERY zone exactly as provided in the raw text with exact numbers] | ... | ... | ... | ... | ... | ... |

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
                    expected_output="A perfectly formatted, exhaustive SarkariResult style blog post containing ALL details from raw text.",
                    agent=writer
                )

                my_crew = Crew(agents=[writer], tasks=[task1])
                result = my_crew.kickoff()

                st.success("✅ Mega Detail SEO Blog Ready!")
                st.markdown(result.raw)
            
            except Exception as e:
                st.error(f"Error: {e}")
