import streamlit as st
import os
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI

# 1. Page Config
st.set_page_config(page_title="Sarkari Job Pro Auto-Blogger", page_icon="🔥", layout="wide")
st.title("🔥 SarkariResult 100% Clone Blogger 🚀")
st.markdown("वेबसाइट से टेक्स्ट कॉपी करें, और बिल्कुल असली SarkariResult जैसा ह्यूमन-टोन आर्टिकल पाएं!")

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
raw_data = st.text_area("वेबसाइट का पूरा टेक्स्ट (Dates, Zone-wise, Links, FAQs) यहाँ पेस्ट करें:", height=250)

# --- MAIN LOGIC ---
if st.button("🚀 Generate 100% Exact Clone Blog"):
    if not api_key:
        st.error("❌ Please enter API Key!")
    elif not raw_data.strip():
        st.error("❌ Kripya Step 2 mein text paste karein!")
    else:
        with st.spinner('🤖 AI is building the exact side-by-side SarkariResult layout with Human Tone...'):
            try:
                llm = ChatOpenAI(
                    model_name=current_model,
                    temperature=0.25, # Thodi creativity for human tone, but strict formatting
                    api_key=api_key,
                    base_url="https://api.groq.com/openai/v1"
                )

                writer = Agent(
                    role='Expert SEO Blogger & Sarkari Format Specialist',
                    goal='Re-write the raw text into a 100% plagiarism-free, highly engaging Hindi/Hinglish blog using the EXACT SarkariResult UI format.',
                    backstory="""You are a human blogger. You write in an engaging, exciting tone (using words like 'खुशखबरी', 'बंपर भर्ती'). 
                    You MUST strictly build side-by-side tables for Dates/Fees and Age/Posts. 
                    You capture ALL tables (Zone-wise, Eligibility, Salary) perfectly without skipping a single detail.""",
                    llm=llm,
                    verbose=True
                )

                task1 = Task(
                    description=f"""
                    Here is the RAW TEXT provided by the user for '{job_topic}':
                    
                    {raw_data}
                    
                    **YOUR INSTRUCTIONS:**
                    1. Re-write the introductory paragraphs in a friendly, enthusiastic human tone in Hindi to avoid plagiarism.
                    2. DO NOT skip any data. Capture the Zone-wise table perfectly.
                    3. Structure the output EXACTLY using the Markdown template below. Use `<br>` for new lines inside table cells to create the side-by-side look.
                    4. Keep English terms like "Zone", "UR", "SC", "Fee", "CBT" as they are (Hinglish tone).

                    --- Use the exact format below ---

                    **Meta Title:** [Job Title]: [Total Vacancy] पदों पर बम्पर भर्ती, अभी आवेदन करें
                    **Meta Description:** [Board Name] ने [Job Title] के पदों पर बम्पर भर्ती निकाली है। आयु सीमा, योग्यता, ज़ोन-वाइज़ पद और आवेदन की पूरी प्रक्रिया यहाँ पढ़ें।
                    **Tags:** Sarkari Result, [Board Name], Govt Jobs 2026

                    ---

                    # 🚨 [Job Title] : [Total Vacancy] पदों पर बड़ी भर्ती, ऑनलाइन फॉर्म शुरू

                    **[Board Name]** द्वारा **[Job Title]** के लिए बहुप्रतीक्षित नोटिफिकेशन जारी कर दिया गया है। जो भी युवा इस सरकारी नौकरी का सपना देख रहे थे, उनके लिए यह एक बहुत बड़ी खुशखबरी है! इस भर्ती के तहत कुल **[Total Vacancy]** पदों को भरा जाएगा। योग्य और इच्छुक उम्मीदवार **[Start Date]** से अपना ऑनलाइन फॉर्म भर सकते हैं। 
                    
                    फॉर्म भरने से पहले आयु सीमा, शैक्षणिक योग्यता, चयन प्रक्रिया और ज़ोन-वाइज़ वेकेंसी की पूरी जानकारी नीचे इस आर्टिकल में विस्तार से ज़रूर पढ़ें।

                    ## 📊 भर्ती का संक्षिप्त विवरण (Brief Overview)
                    <br>

                    | 🗓️ महत्वपूर्ण तिथियां (Important Dates) | 💳 आवेदन शुल्क (Application Fee) |
                    | :--- | :--- |
                    | • **Notification Date:** [Date]<br>• **Apply Start:** [Date]<br>• **Last Date:** [Date]<br>• **Fee Last Date:** [Date]<br>• **Correction Date:** [Date]<br>• **Exam Date:** [Date]<br>• **Admit Card:** [Date] | • **Gen/OBC/EWS:** ₹[Amount]<br>• **SC/ST/Female:** ₹[Amount]<br>• **Refund Rules:** [Mention refund details if any]<br>• *Payment Mode:* Online Debit/Credit Card, Net Banking |

                    | 🎓 आयु सीमा (Age Limit) | 📊 कुल पद (Total Posts) |
                    | :--- | :--- |
                    | • **Minimum Age:** [Age] Years<br>• **Maximum Age:** [Age] Years<br>• *Age Relaxation:* नियमानुसार अतिरिक्त छूट मिलेगी। | • **[Total Vacancy] Posts**<br>• अधिक जानकारी के लिए पूरा नोटिफिकेशन पढ़ें। |

                    ---

                    ## 🏢 पद का नाम और शैक्षणिक योग्यता (Eligibility Details)
                    | Post Name | Department | Eligibility (योग्यता एवं शारीरिक मापदंड) |
                    | :--- | :--- | :--- |
                    | [Extract Post Name] | [Extract Department] | [Extract ALL eligibility rules including Physical details like Running/Weight exactly as provided] |

                    *(Add more rows if there are multiple posts)*

                    ---

                    ## 🌍 ज़ोन-वाइज़ रिक्ति विवरण (Zone/Category Wise Vacancy)
                    *(If this data exists in raw text, format it beautifully like this, otherwise skip)*
                    | Railway Zone / Department | UR | SC | ST | OBC | EWS | Total |
                    | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
                    | [Zone Name] | [Count] | [Count] | [Count] | [Count] | [Count] | [Count] |

                    ---

                    ## 💰 वेतन (Salary Details)
                    * **Pay Scale / Salary:** [Extract Salary Details]
                    * **Allowances:** As per government norms.

                    ---

                    ## 📝 चयन प्रक्रिया (Selection Process)
                    इस भर्ती के लिए उम्मीदवारों का चयन निम्नलिखित चरणों के आधार पर किया जाएगा:
                    * [Step 1]
                    * [Step 2]
                    * [Step 3]

                    ---

                    ## 💻 ऑनलाइन आवेदन कैसे करें? (How to Apply)
                    1. सबसे पहले आधिकारिक वेबसाइट पर जाएँ या नीचे दिए गए 'Apply Online' लिंक पर क्लिक करें।
                    2. भर्ती का नोटिफिकेशन डाउनलोड करें और अपनी योग्यता सुनिश्चित करें।
                    3. रजिस्ट्रेशन करें और अपना फॉर्म सावधानीपूर्वक भरें।
                    4. अपनी फोटो, हस्ताक्षर और ज़रूरी दस्तावेज़ अपलोड करें।
                    5. अपनी केटेगरी के अनुसार ऑनलाइन फीस जमा करें।
                    6. फॉर्म को फाइनल सबमिट करने के बाद एक प्रिंटआउट निकालकर सुरक्षित रख लें।

                    ---

                    ## 🔗 महत्वपूर्ण लिंक्स (Important Links)
                    | लिंक का नाम (Link Description) | सीधा लिंक (Direct Link) |
                    | :--- | :--- |
                    | **Apply Online (ऑनलाइन आवेदन करें)** | **[Click Here]** |
                    | **Download Notification (नोटिफिकेशन डाउनलोड करें)** | **[Click Here]** |
                    | **Official Website (आधिकारिक वेबसाइट)** | **[Click Here]** |

                    ---

                    ## 🤔 अक्सर पूछे जाने वाले प्रश्न (FAQs)
                    *(Extract the FAQs from the raw text and format them below)*

                    **Q. [Write Question Here]**
                    Ans. [Write Answer Here]

                    **Q. [Write Question Here]**
                    Ans. [Write Answer Here]

                    """,
                    expected_output="A perfectly formatted SarkariResult clone with side-by-side tables and human tone.",
                    agent=writer
                )

                my_crew = Crew(agents=[writer], tasks=[task1])
                result = my_crew.kickoff()

                st.success("✅ Exact SarkariResult Clone Blog Ready!")
                st.markdown(result.raw)
            
            except Exception as e:
                st.error(f"Error: {e}")
