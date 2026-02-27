import streamlit as st
import os
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI

# 1. Page Config
st.set_page_config(page_title="Sarkari Job Pro Auto-Blogger", page_icon="🔥", layout="wide")
st.title("🔥 SarkariResult 100% Exact Clone 🚀")

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
raw_data = st.text_area("वेबसाइट का पूरा टेक्स्ट यहाँ पेस्ट करें:", height=250)

# --- MAIN LOGIC ---
if st.button("🚀 Generate 100% Exact Clone Blog"):
    if not api_key:
        st.error("❌ Please enter API Key!")
    elif not raw_data.strip():
        st.error("❌ Kripya Step 2 mein text paste karein!")
    else:
        with st.spinner('🤖 Fixing Tables, Links, and generating exact UI...'):
            try:
                llm = ChatOpenAI(
                    model_name=current_model,
                    temperature=0.1, # Creativity bilkul kam kardi hai taaki hallucinate na kare
                    api_key=api_key,
                    base_url="https://api.groq.com/openai/v1"
                )

                writer = Agent(
                    role='Data Accuracy & Formatting Expert',
                    goal='Create a 100% accurate SarkariResult clone without messing up numbers or links.',
                    backstory="""You are strictly focused on accuracy. You NEVER invent data (like replacing numbers with letters in tables). You format links properly as Markdown.""",
                    llm=llm,
                    verbose=True
                )

                task1 = Task(
                    description=f"""
                    RAW TEXT for '{job_topic}':
                    {raw_data}
                    
                    **CRITICAL RULES (READ CAREFULLY):**
                    1. **Zone-Wise Table FIX:** Extract EXACT NUMBERS for UR, SC, ST, OBC, EWS, Total. DO NOT write letters (B, V, T, G). Match the numbers row by row exactly as in the raw text.
                    2. **Eligibility Table FIX:** Do not leave empty cells (like '-'). If the qualification (e.g., 10th Pass) is the same for all posts, write that same qualification against EVERY single post row.
                    3. **Important Links FIX:** You MUST use correct Markdown link syntax: `[Click Here](actual_url_here)`. Do not just write plain text `[Click Here]`. If the exact URL is missing, use the official website URL.
                    4. Keep the intro paragraph in a highly engaging, human Hindi tone.
                    5. Use `<br>` exactly as shown in the template to create side-by-side lists inside table cells.

                    --- EXACT FORMAT TO FOLLOW ---

                    **Meta Title:** [Job Title]: [Total Vacancy] पदों पर बम्पर भर्ती, अभी आवेदन करें
                    **Meta Description:** [Board Name] ने [Job Title] के पदों पर बम्पर भर्ती निकाली है। आयु सीमा, योग्यता, ज़ोन-वाइज़ पद और आवेदन की प्रक्रिया यहाँ पढ़ें।
                    **Tags:** Sarkari Result, [Board Name], Govt Jobs 2026

                    ---

                    # 🚨 [Job Title] : [Total Vacancy] पदों पर बड़ी भर्ती, ऑनलाइन फॉर्म शुरू

                    **[Board Name]** द्वारा **[Job Title]** के लिए बहुप्रतीक्षित नोटिफिकेशन जारी कर दिया गया है। जो भी युवा इस सरकारी नौकरी का सपना देख रहे थे, उनके लिए यह एक बहुत बड़ी खुशखबरी है! इस भर्ती के तहत कुल **[Total Vacancy]** पदों को भरा जाएगा। योग्य और इच्छुक उम्मीदवार **[Start Date]** से अपना ऑनलाइन फॉर्म भर सकते हैं। 
                    
                    फॉर्म भरने से पहले आयु सीमा, शैक्षणिक योग्यता, चयन प्रक्रिया और ज़ोन-वाइज़ वेकेंसी की पूरी जानकारी नीचे इस आर्टिकल में विस्तार से ज़रूर पढ़ें।

                    ## 📊 भर्ती का संक्षिप्त विवरण (Brief Overview)

                    | 🗓️ महत्वपूर्ण तिथियां (Important Dates) | 💳 आवेदन शुल्क (Application Fee) |
                    | :--- | :--- |
                    | • **Notification Date:** [Date]<br>• **Apply Start:** [Date]<br>• **Last Date:** [Date]<br>• **Fee Last Date:** [Date]<br>• **Correction Date:** [Date]<br>• **Exam Date:** [Date]<br>• **Admit Card:** [Date] | • **Gen/OBC/EWS:** ₹[Amount]<br>• **SC/ST/Female:** ₹[Amount]<br>• **Refund Rules:** [Refund details]<br>• *Payment Mode:* Online |

                    | 🎓 आयु सीमा (Age Limit) | 📊 कुल पद (Total Posts) |
                    | :--- | :--- |
                    | • **Minimum Age:** [Age] Years<br>• **Maximum Age:** [Age] Years<br>• *Age Relaxation:* नियमानुसार छूट | • **[Total Vacancy] Posts**<br>• अधिक जानकारी के लिए नोटिफिकेशन पढ़ें। |

                    ---

                    ## 🏢 पद का नाम और शैक्षणिक योग्यता (Eligibility Details)
                    | Post Name | Department | Eligibility (योग्यता एवं शारीरिक मापदंड) |
                    | :--- | :--- | :--- |
                    | [Extract Post Name] | [Extract Department] | [Write exact eligibility HERE for EVERY row. No blank dashes] |

                    ---

                    ## 🌍 ज़ोन-वाइज़ रिक्ति विवरण (Zone/Category Wise Vacancy)
                    | Railway Zone / Department | UR | SC | ST | OBC | EWS | Total |
                    | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
                    | [Zone Name] | [Exact Number] | [Exact Number] | [Exact Number] | [Exact Number] | [Exact Number] | [Exact Number] |

                    ---

                    ## 💰 वेतन (Salary Details)
                    * **Pay Scale / Salary:** [Extract Salary Details]

                    ---

                    ## 📝 चयन प्रक्रिया (Selection Process)
                    इस भर्ती के लिए चयन निम्नलिखित चरणों के आधार पर किया जाएगा:
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
                    6. फॉर्म को फाइनल सबमिट करने के बाद प्रिंटआउट निकाल लें।

                    ---

                    ## 🔗 महत्वपूर्ण लिंक्स (Important Links)
                    | लिंक का नाम (Link Description) | सीधा लिंक (Direct Link) |
                    | :--- | :--- |
                    | **Apply Online (ऑनलाइन आवेदन करें)** | [Click Here]([URL]) |
                    | **Download Notification (नोटिफिकेशन डाउनलोड करें)** | [Click Here]([URL]) |
                    | **Official Website (आधिकारिक वेबसाइट)** | [Click Here]([URL]) |

                    ---

                    ## 🤔 अक्सर पूछे जाने वाले प्रश्न (FAQs)
                    **Q. [Question]**
                    Ans. [Answer]

                    """,
                    expected_output="Perfectly formatted blog.",
                    agent=writer
                )

                my_crew = Crew(agents=[writer], tasks=[task1])
                result = my_crew.kickoff()

                st.success("✅ Exact SarkariResult Clone Blog Ready!")
                
                # 👇 YAHI THI SABSE BADI PROBLEM: HTML KO RENDER KARNA 👇
                st.markdown(result.raw, unsafe_allow_html=True)
            
            except Exception as e:
                st.error(f"Error: {e}")
