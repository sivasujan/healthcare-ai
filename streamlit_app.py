import streamlit as st
from datetime import datetime

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="MediAssist",
    page_icon="💙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>

    /* Remove Streamlit default spacing */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }

    .stApp {
        background: #f7f9fc;
    }

    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }

    /* ---------------- SIDEBAR ---------------- */

    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e6eaf0;
        min-width: 260px;
        max-width: 260px;
    }

    section[data-testid="stSidebar"] > div {
        padding: 0;
    }

    .brand {
        height: 68px;
        display: flex;
        align-items: center;
        padding-left: 18px;
        border-bottom: 1px solid #edf0f4;
    }

    .brand-icon {
        width: 38px;
        height: 38px;
        background: #2563eb;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 20px;
        margin-right: 10px;
    }

    .brand-name {
        font-size: 20px;
        font-weight: 700;
        color: #172033;
    }

    .sidebar-section {
        font-size: 12px;
        font-weight: 700;
        color: #8b96a8;
        padding: 24px 18px 8px;
        letter-spacing: .04em;
    }

    /* ---------------- TOP BAR ---------------- */

    .topbar {
        height: 68px;
        background: white;
        border-bottom: 1px solid #e7ebf0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 25px;
        color: #6d7a8e;
        font-size: 15px;
    }

    .date-text {
        font-weight: 600;
    }

    .moon {
        font-size: 19px;
    }

    /* ---------------- MAIN CONTENT ---------------- */

    .main-area {
        padding: 28px 60px 50px 60px;
    }

    .welcome-title {
        font-size: 32px;
        font-weight: 750;
        color: #111827;
        margin-bottom: 5px;
    }

    .welcome-subtitle {
        color: #7a8798;
        font-size: 16px;
        margin-bottom: 26px;
    }

    /* ---------------- STAT CARDS ---------------- */

    .stat-card {
        background: white;
        border: 1px solid #e5e9ef;
        border-radius: 17px;
        padding: 22px 24px;
        height: 108px;
        box-shadow: 0 2px 5px rgba(15, 23, 42, .04);
    }

    .stat-label {
        color: #8994a5;
        font-size: 14px;
        margin-bottom: 5px;
    }

    .stat-value {
        color: #111827;
        font-size: 26px;
        font-weight: 700;
    }

    .stat-icon {
        float: right;
        margin-top: -40px;
        width: 43px;
        height: 43px;
        background: #eaf1ff;
        color: #2563eb;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 19px;
    }

    /* ---------------- SECTION CARD ---------------- */

    .section-card {
        background: white;
        border: 1px solid #e4e8ee;
        border-radius: 18px;
        padding: 24px;
        box-shadow: 0 2px 5px rgba(15, 23, 42, .04);
        margin-top: 22px;
    }

    .section-title {
        font-size: 17px;
        font-weight: 700;
        color: #172033;
        margin-bottom: 18px;
    }

    /* ---------------- QUICK ACTION ---------------- */

    .action-card {
        background: white;
        border: 1px solid #e5e9ef;
        border-radius: 15px;
        padding: 16px;
        height: 70px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
    }

    .action-icon {
        width: 42px;
        height: 42px;
        background: #eaf1ff;
        color: #2563eb;
        border-radius: 13px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        margin-right: 13px;
    }

    .action-title {
        font-size: 15px;
        font-weight: 650;
        color: #172033;
    }

    .action-subtitle {
        color: #8490a1;
        font-size: 12px;
        margin-top: 2px;
    }

    .arrow {
        margin-left: auto;
        color: #8793a5;
        font-size: 20px;
    }

    /* ---------------- APPOINTMENTS ---------------- */

    .appointment {
        border: 1px solid #e4e8ef;
        border-radius: 14px;
        padding: 14px 16px;
        margin-bottom: 10px;
    }

    .appointment-name {
        font-size: 15px;
        font-weight: 650;
        color: #172033;
    }

    .appointment-specialty {
        color: #8792a2;
        font-size: 13px;
        margin-top: 3px;
    }

    .appointment-date {
        float: right;
        text-align: right;
        font-size: 12px;
        color: #59677a;
    }

    /* ---------------- CHAT ---------------- */

    .chat-item {
        border: 1px solid #e4e8ef;
        border-radius: 14px;
        padding: 13px 15px;
        margin-bottom: 9px;
    }

    .chat-icon {
        display: inline-flex;
        width: 36px;
        height: 36px;
        border-radius: 11px;
        background: #eaf1ff;
        color: #2563eb;
        align-items: center;
        justify-content: center;
        margin-right: 10px;
    }

    .chat-title {
        font-weight: 600;
        font-size: 14px;
        color: #253047;
    }

    .chat-date {
        color: #8994a5;
        font-size: 12px;
        margin-left: 47px;
    }

    .tag {
        float: right;
        background: #eaf1ff;
        color: #315d9e;
        border-radius: 20px;
        padding: 4px 10px;
        font-size: 11px;
    }

    /* ---------------- BUTTONS ---------------- */

    div.stButton > button {
        border-radius: 10px;
        border: none;
        background: transparent;
        color: #617086;
        font-weight: 500;
        text-align: left;
        width: 100%;
        padding: 11px 14px;
    }

    div.stButton > button:hover {
        background: #edf3ff;
        color: #2563eb;
    }

    /* ---------------- MOBILE ---------------- */

    @media (max-width: 900px) {

        .main-area {
            padding: 25px;
        }

        .welcome-title {
            font-size: 25px;
        }

    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("""
    <div class="brand">
        <div class="brand-icon">〽</div>
        <div class="brand-name">MediAssist</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="sidebar-section">MAIN</div>',
        unsafe_allow_html=True
    )

    if "page" not in st.session_state:
        st.session_state.page = "Dashboard"

    pages = [
        ("▦", "Dashboard"),
        ("▢", "AI Chat"),
        ("♡", "Symptom Analysis"),
        ("💊", "Medicine Info"),
        ("♧", "Find a Doctor"),
        ("♧", "Emergency Check"),
        ("▣", "Appointments"),
        ("♙", "Profile"),
    ]

    for icon, name in pages:

        if st.button(
            f"{icon}   {name}",
            key=f"nav_{name}"
        ):
            st.session_state.page = name
            st.rerun()

    st.markdown(
        "<br><br>",
        unsafe_allow_html=True
    )

    st.caption(
        "MediAssist AI\n\n"
        "AI-generated health information is "
        "educational only."
    )


# ============================================================
# TOP BAR
# ============================================================

today = datetime.now().strftime("%A, %B %-d")

# Windows compatibility
try:
    today = datetime.now().strftime("%A, %B %#d")
except:
    pass

st.markdown(
    f"""
    <div class="topbar">
        <div class="date-text">{today}</div>
        <div class="moon">☾</div>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# MAIN
# ============================================================

page = st.session_state.page


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    st.markdown(
        '<div class="main-area">',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="welcome-title">
            Good afternoon, sivasujanrudrakshula 👋
        </div>

        <div class="welcome-subtitle">
            Here's your health overview.
            How can MediAssist help you today?
        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # STATISTICS
    # --------------------------------------------------------

    c1, c2, c3 = st.columns(3)

    with c1:

        st.markdown("""
        <div class="stat-card">
            <div class="stat-label">Chats</div>
            <div class="stat-value">9</div>
            <div class="stat-icon">〽</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:

        st.markdown("""
        <div class="stat-card">
            <div class="stat-label">Appointments</div>
            <div class="stat-value">1</div>
            <div class="stat-icon">〽</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:

        st.markdown("""
        <div class="stat-card">
            <div class="stat-label">Upcoming</div>
            <div class="stat-value">1</div>
            <div class="stat-icon">〽</div>
        </div>
        """, unsafe_allow_html=True)


    # --------------------------------------------------------
    # QUICK ACTIONS
    # --------------------------------------------------------

    st.markdown("""
    <div class="section-card">

        <div class="section-title">
            Quick actions
        </div>

    </div>
    """, unsafe_allow_html=True)

    q1, q2, q3 = st.columns(3)

    actions = [
        ("💬", "AI Chat", "Ask anything"),
        ("♡", "Symptom Analysis", "Check symptoms"),
        ("💊", "Medicine Info", "Look up medicine"),
        ("♧", "Find a Doctor", "Get a specialist"),
        ("♧", "Emergency Check", "Urgent?"),
        ("▣", "Appointments", "Book a visit"),
    ]

    cols = [q1, q2, q3, q1, q2, q3]

    for i, (icon, title, subtitle) in enumerate(actions):

        with cols[i]:

            if st.button(
                f"{icon}   {title}   →",
                key=f"quick_{i}"
            ):

                st.session_state.page = title

                if title == "AI Chat":
                    st.session_state.page = "AI Chat"

                elif title == "Symptom Analysis":
                    st.session_state.page = "Symptom Analysis"

                elif title == "Medicine Info":
                    st.session_state.page = "Medicine Info"

                elif title == "Find a Doctor":
                    st.session_state.page = "Find a Doctor"

                elif title == "Emergency Check":
                    st.session_state.page = "Emergency Check"

                elif title == "Appointments":
                    st.session_state.page = "Appointments"

                st.rerun()


    # --------------------------------------------------------
    # LOWER SECTION
    # --------------------------------------------------------

    left, right = st.columns(2)

    with left:

        st.markdown("""
        <div class="section-card">

            <div class="section-title">
                Upcoming appointments
                <span style="
                    float:right;
                    color:#2563eb;
                    font-size:13px;
                    font-weight:500;
                ">
                    View all
                </span>
            </div>

            <div class="appointment">

                <div class="appointment-date">
                    Sep 10, 2026<br>
                    <span style="color:#8994a5">
                        2:36 PM
                    </span>
                </div>

                <div class="appointment-name">
                    CV RAO
                </div>

                <div class="appointment-specialty">
                    Cardiology
                </div>

            </div>

        </div>
        """, unsafe_allow_html=True)


    with right:

        st.markdown("""
        <div class="section-card">

            <div class="section-title">
                Recent chats
                <span style="
                    float:right;
                    color:#2563eb;
                    font-size:13px;
                    font-weight:500;
                ">
                    Open chat
                </span>
            </div>

            <div class="chat-item">

                <span class="chat-icon">
                    💬
                </span>

                <span class="chat-title">
                    Book an appointment for tomorrow
                </span>

                <span class="tag">
                    general
                </span>

                <div class="chat-date">
                    Sep 10, 2026
                </div>

            </div>

            <div class="chat-item">

                <span class="chat-icon">
                    💬
                </span>

                <span class="chat-title">
                    Book an appointment for tomorrow
                </span>

                <span class="tag">
                    general
                </span>

                <div class="chat-date">
                    Sep 10, 2026
                </div>

            </div>

        </div>
        """, unsafe_allow_html=True)

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# OTHER PAGES
# ============================================================

elif page == "AI Chat":

    st.markdown(
        '<div class="main-area">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="welcome-title">AI Chat</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="welcome-subtitle">'
        'Talk with your MediAssist AI healthcare assistant.'
        '</div>',
        unsafe_allow_html=True
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):
            st.write(message["content"])

    prompt = st.chat_input(
        "Ask MediAssist anything..."
    )

    if prompt:

        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("user"):
            st.write(prompt)

        # Connect this to your existing FastAPI/LangGraph API
        answer = (
            "I'm MediAssist AI. Your request has been "
            "received. Connect this section to the "
            "existing `/chat/send` API from your backend."
        )

        with st.chat_message("assistant"):
            st.write(answer)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

    st.markdown("</div>", unsafe_allow_html=True)


elif page == "Symptom Analysis":

    st.markdown(
        '<div class="main-area">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="welcome-title">'
        'Symptom Analysis'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="welcome-subtitle">'
        'Describe your symptoms and let MediAssist analyze them.'
        '</div>',
        unsafe_allow_html=True
    )

    symptoms = st.text_area(
        "Describe your symptoms",
        height=150,
        placeholder="Example: fever, headache and cough for 2 days..."
    )

    age = st.number_input(
        "Age",
        min_value=1,
        max_value=120,
        value=25
    )

    if st.button(
        "Analyze Symptoms",
        type="primary"
    ):

        if symptoms:

            st.success(
                "Symptom analysis request submitted."
            )

        else:

            st.warning(
                "Please enter your symptoms."
            )

    st.markdown("</div>", unsafe_allow_html=True)


elif page == "Medicine Info":

    st.markdown(
        '<div class="main-area">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="welcome-title">'
        'Medicine Information'
        '</div>',
        unsafe_allow_html=True
    )

    medicine = st.text_input(
        "Search medicine",
        placeholder="Enter medicine name..."
    )

    if st.button(
        "Search",
        type="primary"
    ):

        if medicine:

            st.info(
                f"Searching information for **{medicine}**..."
            )

    st.markdown("</div>", unsafe_allow_html=True)


elif page == "Find a Doctor":

    st.markdown(
        '<div class="main-area">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="welcome-title">'
        'Find a Doctor'
        '</div>',
        unsafe_allow_html=True
    )

    specialty = st.selectbox(
        "Specialty",
        [
            "Cardiology",
            "General Medicine",
            "Dermatology",
            "Neurology",
            "Orthopedics",
            "Pediatrics"
        ]
    )

    if st.button(
        "Find Doctor",
        type="primary"
    ):

        st.success(
            f"Searching for {specialty} specialists..."
        )

    st.markdown("</div>", unsafe_allow_html=True)


elif page == "Emergency Check":

    st.markdown(
        '<div class="main-area">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="welcome-title">'
        'Emergency Check'
        '</div>',
        unsafe_allow_html=True
    )

    st.error(
        "🚨 If this is a life-threatening emergency, "
        "contact your local emergency service immediately."
    )

    symptoms = st.text_area(
        "Describe the situation",
        height=160
    )

    if st.button(
        "Check Emergency Risk",
        type="primary"
    ):

        if symptoms:

            st.warning(
                "AI emergency assessment initiated."
            )

        else:

            st.warning(
                "Please describe the situation."
            )

    st.markdown("</div>", unsafe_allow_html=True)


elif page == "Appointments":

    st.markdown(
        '<div class="main-area">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="welcome-title">'
        'Appointments'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="section-card">

        <div class="section-title">
            Upcoming appointments
        </div>

        <div class="appointment">

            <div class="appointment-date">
                Sep 10, 2026<br>
                2:36 PM
            </div>

            <div class="appointment-name">
                CV RAO
            </div>

            <div class="appointment-specialty">
                Cardiology
            </div>

        </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("</div>", unsafe_allow_html=True)


elif page == "Profile":

    st.markdown(
        '<div class="main-area">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="welcome-title">'
        'Profile'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="section-card">

        <div class="section-title">
            Personal Information
        </div>

        <b>Name</b><br>
        sivasujanrudrakshula

        <br><br>

        <b>Email</b><br>
        test@example.com

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("</div>", unsafe_allow_html=True)
