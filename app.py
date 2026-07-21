import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from google import genai

from prompts import QUICK_ACTION_PROMPTS, SYSTEM_PROMPT


load_dotenv()

MAX_CHARACTERS = 200
EMERGENCY_KEYWORDS = (
    "chest pain",
    "heart attack",
    "stroke",
    "unconscious",
    "severe bleeding",
    "difficulty breathing",
    "suicide",
    "overdose",
    "poisoning",
)
EMERGENCY_MESSAGE = """🚨 Medical Emergency

Call 112 or 108 immediately.

Visit the nearest hospital.

This chatbot cannot assist during emergencies."""


def load_css() -> None:
    css_path = Path(__file__).parent / "styles" / "style.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def init_session_state():
    defaults = {
        "messages": [],
        "pending_prompt": None,
        "last_prompt_length": 0,
        "show_bmi": True,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def is_emergency(prompt: str) -> bool:
    lowered = prompt.lower()
    return any(keyword in lowered for keyword in EMERGENCY_KEYWORDS)


def is_greeting_prompt(prompt: str) -> bool:
    lowered = prompt.strip().lower()
    if not lowered:
        return False

    greetings = (
        "hello",
        "hi",
        "hey",
        "good morning",
        "good afternoon",
        "good evening",
        "greetings",
    )
    return any(
        lowered == greeting or lowered.startswith(f"{greeting} ") or lowered.startswith(f"{greeting}!") or lowered.startswith(f"{greeting},")
        for greeting in greetings
    )


def get_greeting_response() -> str:
    return "Hello! I am your Healthyfy AI Assistant. How can I help you today?"


def render_sidebar():
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-hero">
                <div class="sidebar-logo">🧠</div>
                <h2>Healthyfy AI</h2>
                <div class="version-pill">Version 1.0</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="sidebar-card">
                <h3>🧠 About AI</h3>
                <p>This app provides general health information through Gemini AI in a warm, easy-to-use chat experience.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="sidebar-card">
                <h3>📞 Telemedicine</h3>
                <p>Connect with a clinician quickly for non-emergency advice, follow-ups, and virtual care guidance.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="sidebar-card">
                <h3>🚑 Emergency Numbers</h3>
                <p>112 · Emergency</p>
                <p>108 · Ambulance</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="sidebar-card">
                <h3>👨‍🎓 Student Details</h3>
                <p><strong>Name:</strong> Abu Hanzala Ansari</p>
                <p><strong>University:</strong> KIET Deemed to be University</p>
                <p><strong>Department:</strong> B.Tech CSE (AI & ML)</p>
                <p><strong>Academic Year:</strong> 2026–2027</p>
                <p><strong>Version:</strong> 1.0</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("🧮 BMI Calculator", use_container_width=True):
            st.session_state.show_bmi = True

        st.markdown(
            """
            <div class="sidebar-card">
                <h3>💡 Health Tips</h3>
                <ul>
                    <li>Stay hydrated and rest well.</li>
                    <li>Seek urgent care for severe symptoms.</li>
                    <li>Keep medical records handy.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="sidebar-footer">
                <div class="footer-title">⚡ Healthyfy AI</div>
                <div class="footer-subtitle">Developed by Abu Hanzala Ansari</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def get_gemini_response(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set. Please add it to your environment or .env file.")

    client = genai.Client(api_key=api_key)
    combined_prompt = f"{SYSTEM_PROMPT}\n\nUser Prompt: {prompt}"

    MODELS = [
        "gemini-3.5-flash",
        "gemini-2.5-flash",
        "gemini-flash-latest",
    ]

    for model_name in MODELS:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=combined_prompt,
            )
            print("Model used:", model_name)
            print("Response object:", response)
            print("Response text:", repr(response.text))
            return response.text
        except Exception:
            continue

    return "Sorry, the AI service is currently unavailable."


def render_header():
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-badge">⚡ Tech-powered healthcare assistant</div>
            <h1>🩺 Healthyfy AI Assistant</h1>
            <p>Ask general health questions, get wellness guidance, and access supportive healthcare insights in a calm and intelligent experience.</p>
            <div class="hero-pill-row">
                <span class="hero-pill">🌿 Preventive care</span>
                <span class="hero-pill">🧠 Gemini AI</span>
                <span class="hero-pill">💬 Smart chat</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def calculate_bmi(height_cm: float, weight_kg: float):
    """Calculate BMI from height in centimeters and weight in kilograms."""
    if height_cm <= 0 or weight_kg <= 0:
        return None
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 1)


def get_bmi_category(bmi_value: float):
    """Return the BMI category and advice for a given BMI value."""
    if bmi_value is None:
        return "Unknown", "Please enter valid height and weight.", "neutral"
    if bmi_value < 18.5:
        return "Underweight", "Consider consulting a healthcare professional about healthy weight gain.", "underweight"
    if bmi_value < 25:
        return "Normal", "Great! Maintain your healthy lifestyle.", "normal"
    if bmi_value < 30:
        return "Overweight", "Regular exercise and a balanced diet can help improve your health.", "overweight"
    return "Obese", "Please consult a qualified healthcare professional for guidance.", "obese"


def render_bmi_calculator():
    """Render a modular BMI calculator section with a result card."""
    st.markdown(
        """
        <div class="bmi-section">
            <h3>🧮 BMI Calculator</h3>
            <p>Check your body mass index using your height and weight.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        height = st.number_input(
            "Height (cm)",
            min_value=50.0,
            max_value=250.0,
            value=170.0,
            step=1.0,
        )
    with col2:
        weight = st.number_input(
            "Weight (kg)",
            min_value=10.0,
            max_value=300.0,
            value=70.0,
            step=1.0,
        )

    if st.button("Calculate BMI", use_container_width=True):
        bmi_value = calculate_bmi(height, weight)
        category, advice, tone = get_bmi_category(bmi_value)

        st.markdown(
            f"""
            <div class="bmi-card {tone}">
                <div class="bmi-icon">{'⚖️' if tone == 'normal' else '⚠️' if tone == 'underweight' else '🟡' if tone == 'overweight' else '🔴'}</div>
                <h4>BMI Value: {bmi_value if bmi_value is not None else 'N/A'}</h4>
                <p><strong>Category:</strong> {category}</p>
                <p><strong>Health Advice:</strong> {advice}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_metric_cards():
    st.markdown('<div class="metrics-grid">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    cards = [
        ("📈", "24/7 Support", "Helpful health guidance any time"),
        ("🧪", "Trusted AI", "General wellness information"),
        ("🩹", "First Aid", "Quick steps for common concerns"),
        ("🧭", "Care Guidance", "Encourages professional help when needed"),
    ]
    for col, card in zip([col1, col2, col3, col4], cards):
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-icon">{card[0]}</div>
                    <h4>{card[1]}</h4>
                    <p>{card[2]}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    st.markdown('</div>', unsafe_allow_html=True)


def render_quick_actions():
    st.markdown('<div class="quick-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">⚡ Quick actions</div>', unsafe_allow_html=True)
    action_buttons = ["Dengue", "Fever", "Cold", "First Aid", "Nutrition"]
    cols = st.columns(len(action_buttons))
    for col, label in zip(cols, action_buttons):
        with col:
            if st.button(label, key=f"quick_{label.lower()}", use_container_width=True):
                st.session_state.pending_prompt = QUICK_ACTION_PROMPTS[label]
                st.session_state.last_quick_action = label

    if "last_quick_action" in st.session_state:
        st.caption(f"Selected quick action: {st.session_state.last_quick_action}")
    st.markdown('</div>', unsafe_allow_html=True)


def render_clear_chat_button():
    if st.button("🧹 Clear Chat", use_container_width=False):
        st.session_state.messages.clear()
        st.session_state.pending_prompt = None
        st.session_state.last_quick_action = None
        st.session_state.last_prompt_length = 0


def render_chat_history():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def render_disclaimer():
    st.info(
        "This chatbot provides educational information only and is not a substitute for "
        "professional medical advice."
    )


def render_emergency_notice() -> None:
    st.markdown(
        f"""
        <div class="emergency-card">
            <h3>🚨 Medical Emergency</h3>
            <p>{EMERGENCY_MESSAGE.replace(chr(10), '<br>')}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def process_prompt(prompt: str) -> None:
    prompt = prompt.strip()
    if not prompt:
        return

    if len(prompt) > MAX_CHARACTERS:
        prompt = prompt[:MAX_CHARACTERS]

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.last_prompt_length = len(prompt)

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if is_greeting_prompt(prompt):
            response_text = get_greeting_response()
            st.write(response_text)
        elif is_emergency(prompt):
            render_emergency_notice()
            response_text = EMERGENCY_MESSAGE
        else:
            with st.spinner("Dr. AI is thinking..."):
                print("Reached get_gemini_response")
                try:
                    response_text = get_gemini_response(prompt)
                    print("Gemini Response:", response_text)
                except Exception as e:
                    print("FULL ERROR:", repr(e))
                    raise

            st.write(response_text)
            render_disclaimer()

    st.session_state.messages.append({"role": "assistant", "content": response_text})


def main():
    st.set_page_config(
        page_title="Healthyfy AI Assistant",
        page_icon="🩺",
        layout="wide",
    )

    load_css()

    init_session_state()
    st.markdown('<div class="app-shell">', unsafe_allow_html=True)
    render_sidebar()
    render_header()
    if st.session_state.get("show_bmi", True):
        render_bmi_calculator()
    render_metric_cards()
    render_quick_actions()
    render_clear_chat_button()
    render_chat_history()

    st.markdown('<div class="composer-shell">', unsafe_allow_html=True)
    prompt = st.chat_input("Ask your health question...")
    st.caption(f"Characters: {st.session_state.last_prompt_length}/{MAX_CHARACTERS}")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.get("pending_prompt"):
        pending_prompt = st.session_state.pending_prompt
        st.session_state.pending_prompt = None
        process_prompt(pending_prompt)
    elif prompt is not None:
        process_prompt(prompt)


if __name__ == "__main__":
    main()