import streamlit as st
import requests

# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="MediAssist - AI Healthcare Assistant",
    page_icon="🏥",
    layout="wide"
)

API_URL = st.secrets.get(
    "API_URL",
    "http://localhost:8000/api"
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>
        .main {
            background-color: #f8fafc;
        }

        .block-container {
            padding-top: 2rem;
            max-width: 1200px;
        }

        .title {
            font-size: 42px;
            font-weight: 700;
            color: #0f172a;
        }

        .subtitle {
            font-size: 18px;
            color: #64748b;
            margin-bottom: 30px;
        }

        .card {
            background: white;
            padding: 20px;
            border-radius: 15px;
            border: 1px solid #e2e8f0;
            margin-bottom: 20px;
        }

        .warning {
            background: #fff7ed;
            padding: 15px;
            border-radius: 10px;
            border-left: 5px solid #f97316;
        }

        .danger {
            background: #fef2f2;
            padding: 15px;
            border-radius: 10px;
            border-left: 5px solid #ef4444;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# SESSION STATE
# ============================================================

if "access_token" not in st.session_state:
    st.session_state.access_token = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ============================================================
# API HELPERS
# ============================================================

def get_headers():
    headers = {
        "Content-Type": "application/json"
    }

    if st.session_state.access_token:
        headers["Authorization"] = (
            f"Bearer {st.session_state.access_token}"
        )

    return headers


def api_post(endpoint, payload):
    try:
        response = requests.post(
            f"{API_URL}{endpoint}",
            json=payload,
            headers=get_headers(),
            timeout=60
        )

        if response.status_code >= 400:
            st.error(
                f"API Error {response.status_code}: "
                f"{response.text}"
            )
            return None

        return response.json()

    except requests.exceptions.RequestException as e:
        st.error(f"Could not connect to backend: {e}")
        return None


def api_get(endpoint):
    try:
        response = requests.get(
            f"{API_URL}{endpoint}",
            headers=get_headers(),
            timeout=30
        )

        if response.status_code >= 400:
            st.error(
                f"API Error {response.status_code}: "
                f"{response.text}"
            )
            return None

        return response.json()

    except requests.exceptions.RequestException as e:
        st.error(f"Could not connect to backend: {e}")
        return None


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="title">🏥 MediAssist</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'AI-powered healthcare assistant'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("Navigation")

    page = st.radio(
        "Choose a feature",
        [
            "🤖 AI Chat",
            "🩺 Symptom Analyzer",
            "💊 Medicine Information",
            "👨‍⚕️ Doctor Recommendation",
            "🚨 Emergency Check",
            "📅 Appointments",
            "👤 Profile"
        ]
    )

    st.divider()

    st.caption(
        "AI-generated health information is educational "
        "only and is not a substitute for professional "
        "medical advice."
    )


# ============================================================
# LOGIN
# ============================================================

with st.sidebar:

    st.divider()

    st.subheader("Authentication")

    if st.session_state.access_token:

        st.success("Logged in")

        if st.button("Logout"):
            st.session_state.access_token = None
            st.session_state.chat_history = []
            st.rerun()

    else:

        email = st.text_input(
            "Email",
            key="login_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button("Login", use_container_width=True):

            result = api_post(
                "/auth/login",
                {
                    "email": email,
                    "password": password
                }
            )

            if result:

                data = result.get("data", result)

                token = data.get("access_token")

                if token:
                    st.session_state.access_token = token
                    st.success("Login successful")
                    st.rerun()


# ============================================================
# AI CHAT
# ============================================================

if page == "🤖 AI Chat":

    st.header("🤖 AI Healthcare Assistant")

    st.write(
        "Ask questions about symptoms, medicines, "
        "health concerns, or healthcare."
    )

    for message in st.session_state.chat_history:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input(
        "Describe your health question..."
    )

    if prompt:

        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": prompt
            }
        )

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):

            with st.spinner("Analyzing..."):

                result = api_post(
                    "/chat/send",
                    {
                        "message": prompt
                    }
                )

            if result:

                data = result.get("data", result)

                answer = (
                    data.get("response")
                    or data.get("message")
                    or str(data)
                )

                st.markdown(answer)

                st.session_state.chat_history.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )


# ============================================================
# SYMPTOM ANALYZER
# ============================================================

elif page == "🩺 Symptom Analyzer":

    st.header("🩺 Symptom Analyzer")

    symptoms = st.text_area(
        "Describe your symptoms",
        placeholder=(
            "Example: fever, headache, cough "
            "and sore throat for 2 days"
        )
    )

    col1, col2 = st.columns(2)

    with col1:

        age = st.number_input(
            "Age",
            min_value=1,
            max_value=120,
            value=25
        )

    with col2:

        gender = st.selectbox(
            "Gender",
            [
                "Prefer not to say",
                "Male",
                "Female",
                "Other"
            ]
        )

    duration = st.text_input(
        "Duration",
        placeholder="e.g. 2 days"
    )

    medical_history = st.text_area(
        "Medical history",
        placeholder="Optional"
    )

    medications = st.text_area(
        "Current medications",
        placeholder="Optional"
    )

    allergies = st.text_area(
        "Allergies",
        placeholder="Optional"
    )

    if st.button(
        "Analyze Symptoms",
        type="primary"
    ):

        if not symptoms.strip():

            st.warning(
                "Please describe your symptoms."
            )

        else:

            payload = {
                "symptoms": symptoms,
                "age": age,
                "gender": gender,
                "duration": duration,
                "medical_history": medical_history,
                "current_medications": medications,
                "allergies": allergies
            }

            with st.spinner(
                "Analyzing symptoms..."
            ):

                result = api_post(
                    "/symptom/analyze",
                    payload
                )

            if result:

                data = result.get(
                    "data",
                    result
                )

                st.subheader(
                    "Possible Conditions"
                )

                conditions = data.get(
                    "possible_conditions",
                    []
                )

                for condition in conditions:

                    st.markdown(
                        f"""
                        **{condition.get('name', 'Unknown')}**

                        Confidence: \
                        {condition.get('confidence', 'N/A')}

                        Severity: \
                        {condition.get('severity', 'N/A')}
                        """
                    )

                    st.divider()

                severity = data.get(
                    "overall_severity"
                )

                if severity:
                    st.info(
                        f"Overall severity: {severity}"
                    )

                st.subheader(
                    "Recommendations"
                )

                for recommendation in data.get(
                    "recommendations",
                    []
                ):

                    st.markdown(
                        f"""
                        ### {recommendation.get('title', '')}

                        {recommendation.get('detail', '')}
                        """
                    )

                specialty = data.get(
                    "doctor_specialty"
                )

                if specialty:

                    st.info(
                        f"Recommended specialist: "
                        f"{specialty}"
                    )

                if data.get(
                    "emergency_detected"
                ):

                    st.error(
                        "🚨 Emergency warning detected. "
                        "Please seek immediate professional "
                        "medical assistance."
                    )


# ============================================================
# MEDICINE SEARCH
# ============================================================

elif page == "💊 Medicine Information":

    st.header("💊 Medicine Information")

    query = st.text_input(
        "Search for a medicine",
        placeholder="Example: paracetamol"
    )

    if st.button(
        "Search Medicine",
        type="primary"
    ):

        if not query.strip():

            st.warning(
                "Enter a medicine name."
            )

        else:

            result = api_post(
                "/medicine/search",
                {
                    "query": query
                }
            )

            if result:

                data = result.get(
                    "data",
                    result
                )

                st.json(data)


# ============================================================
# DOCTOR RECOMMENDATION
# ============================================================

elif page == "👨‍⚕️ Doctor Recommendation":

    st.header("👨‍⚕️ Doctor Recommendation")

    symptoms = st.text_area(
        "What symptoms are you experiencing?"
    )

    age = st.number_input(
        "Age",
        min_value=1,
        max_value=120,
        value=25
    )

    medical_history = st.text_area(
        "Medical history"
    )

    medications = st.text_area(
        "Current medications"
    )

    if st.button(
        "Find Recommended Specialist",
        type="primary"
    ):

        result = api_post(
            "/doctor/recommend",
            {
                "symptoms": symptoms,
                "age": age,
                "medical_history": medical_history,
                "current_medications": medications
            }
        )

        if result:

            data = result.get(
                "data",
                result
            )

            st.success(
                f"Specialty: "
                f"{data.get('specialty', 'N/A')}"
            )

            st.write(
                "**Reason:**",
                data.get("reason", "N/A")
            )

            st.write(
                "**Urgency:**",
                data.get("urgency", "N/A")
            )

            st.subheader(
                "Preparation Tips"
            )

            for tip in data.get(
                "preparation_tips",
                []
            ):
                st.write(f"• {tip}")

            st.subheader(
                "Nearby Hospitals"
            )

            for hospital in data.get(
                "nearby_hospitals",
                []
            ):
                st.write(f"🏥 {hospital}")


# ============================================================
# EMERGENCY CHECK
# ============================================================

elif page == "🚨 Emergency Check":

    st.header("🚨 Emergency Check")

    st.warning(
        "If someone is experiencing a life-threatening "
        "emergency, contact your local emergency service "
        "immediately."
    )

    symptoms = st.text_area(
        "Describe the symptoms"
    )

    age = st.number_input(
        "Age",
        min_value=1,
        max_value=120,
        value=25
    )

    history = st.text_area(
        "Medical history"
    )

    medications = st.text_area(
        "Current medications"
    )

    if st.button(
        "Check Emergency Risk",
        type="primary"
    ):

        result = api_post(
            "/emergency/check",
            {
                "symptoms": symptoms,
                "age": age,
                "medical_history": history,
                "current_medications": medications
            }
        )

        if result:

            data = result.get(
                "data",
                result
            )

            emergency = data.get(
                "emergency_detected",
                False
            )

            if emergency:

                st.error(
                    "🚨 POSSIBLE EMERGENCY DETECTED"
                )

                for action in data.get(
                    "immediate_actions",
                    []
                ):
                    st.write(
                        f"🚑 {action}"
                    )

                st.write(
                    "Emergency number:",
                    data.get(
                        "emergency_number",
                        "Contact your local emergency service"
                    )
                )

            else:

                st.success(
                    "No emergency red flags were detected "
                    "by the AI system."
                )

            st.json(data)


# ============================================================
# APPOINTMENTS
# ============================================================

elif page == "📅 Appointments":

    st.header("📅 Appointments")

    if not st.session_state.access_token:

        st.info(
            "Please login to manage appointments."
        )

    else:

        appointments = api_get(
            "/appointments/upcoming"
        )

        if appointments:

            data = appointments.get(
                "data",
                appointments
            )

            st.json(data)

        st.subheader(
            "Book an Appointment"
        )

        title = st.text_input(
            "Appointment title"
        )

        doctor = st.text_input(
            "Doctor name"
        )

        specialty = st.text_input(
            "Specialty"
        )

        hospital = st.text_input(
            "Hospital"
        )

        appointment_date = st.date_input(
            "Date"
        )

        appointment_time = st.time_input(
            "Time"
        )

        notes = st.text_area(
            "Notes"
        )

        if st.button(
            "Book Appointment",
            type="primary"
        ):

            result = api_post(
                "/appointments",
                {
                    "title": title,
                    "doctor_name": doctor,
                    "specialty": specialty,
                    "hospital": hospital,
                    "appointment_date":
                        str(appointment_date),
                    "appointment_time":
                        str(appointment_time),
                    "notes": notes
                }
            )

            if result:

                st.success(
                    "Appointment booked successfully!"
                )

                st.json(result)


# ============================================================
# PROFILE
# ============================================================

elif page == "👤 Profile":

    st.header("👤 Health Profile")

    if not st.session_state.access_token:

        st.info(
            "Please login to view your profile."
        )

    else:

        profile = api_get(
            "/profile"
        )

        if profile:

            data = profile.get(
                "data",
                profile
            )

            st.json(data)

# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "MediAssist | AI Healthcare Assistant | "
    "For educational purposes only. "
    "Not a substitute for professional medical advice."
)
