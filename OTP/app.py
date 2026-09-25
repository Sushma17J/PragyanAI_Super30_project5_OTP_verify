import streamlit as st
import secrets
import time
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from twilio.rest import Client


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="PragyanAI | OTP Verification",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* =====================================================
       GLOBAL
       ===================================================== */

    .stApp {
        background: #f7f7f8;
    }

    .main {
        background: #f7f7f8;
    }

    html, body, [class*="css"] {
        color: #000000 !important;
    }

    p, span, label, div {
        color: #000000;
    }


    /* =====================================================
       SIDEBAR
       ===================================================== */

    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e5e5e5;
    }

    section[data-testid="stSidebar"] * {
        color: #000000 !important;
    }

    .sidebar-logo {
        text-align: center;
        font-size: 30px;
        font-weight: 800;
        margin-top: 10px;
        margin-bottom: 4px;
    }

    .sidebar-subtitle {
        text-align: center;
        font-size: 13px;
        color: #666666 !important;
        margin-bottom: 25px;
    }

    .sidebar-section {
        font-size: 13px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 20px;
        margin-bottom: 10px;
    }


    /* =====================================================
       MAIN HEADER
       ===================================================== */

    .hero {
        background: linear-gradient(
            135deg,
            #000000 0%,
            #222222 100%
        );

        padding: 38px 35px;
        border-radius: 24px;
        margin-bottom: 30px;

        box-shadow:
            0 15px 40px rgba(0, 0, 0, 0.15);
    }

    .hero-title {
        color: #ffffff !important;
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .hero-subtitle {
        color: #dddddd !important;
        font-size: 17px;
        margin-bottom: 0;
    }


    /* =====================================================
       VERIFICATION CARD
       ===================================================== */

    .verification-card {
        background: #ffffff;
        border: 1px solid #e5e5e5;

        border-radius: 24px;

        padding: 35px;

        box-shadow:
            0 12px 35px rgba(0, 0, 0, 0.07);

        margin-bottom: 25px;
    }

    .method-icon {
        font-size: 45px;
        margin-bottom: 8px;
    }

    .method-title {
        font-size: 28px;
        font-weight: 800;
        color: #000000 !important;
        margin-bottom: 8px;
    }

    .method-description {
        font-size: 15px;
        color: #666666 !important;
        margin-bottom: 25px;
    }


    /* =====================================================
       INPUTS
       ===================================================== */

    .stTextInput label {
        color: #000000 !important;
        font-weight: 700 !important;
    }

    .stTextInput input {
        background-color: #ffffff !important;
        color: #000000 !important;

        border: 1px solid #cccccc !important;

        border-radius: 12px !important;

        padding: 13px !important;
    }

    .stTextInput input:focus {
        border: 2px solid #000000 !important;
        box-shadow: none !important;
    }


    /* =====================================================
       BUTTONS
       ===================================================== */

    .stButton > button {
        width: 100%;

        height: 48px;

        border-radius: 12px !important;

        background: #000000 !important;

        color: #ffffff !important;

        border: none !important;

        font-size: 15px;

        font-weight: 700;

        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        background: #333333 !important;

        transform: translateY(-2px);

        box-shadow:
            0 8px 18px rgba(0, 0, 0, 0.18);
    }

    .stButton > button p {
        color: #ffffff !important;
    }


    /* =====================================================
       DIVIDER
       ===================================================== */

    .soft-divider {
        height: 1px;
        background: #eeeeee;
        margin: 25px 0;
    }


    /* =====================================================
       VERIFIED BOX
       ===================================================== */

    .verified-box {
        background: #f0fff4;

        border: 1px solid #b7ebc6;

        border-radius: 14px;

        padding: 16px;

        text-align: center;

        margin-top: 20px;

        font-weight: 700;

        color: #166534 !important;
    }


    /* =====================================================
       PARTY POPPER CELEBRATION
       ===================================================== */

    .party-container {
        position: relative;

        text-align: center;

        margin: 20px 0;

        height: 85px;

        overflow: hidden;
    }

    .party {
        position: absolute;

        font-size: 38px;

        animation:
            party-fall 1.8s ease-out forwards;
    }

    .party:nth-child(1) {
        left: 15%;
        animation-delay: 0s;
    }

    .party:nth-child(2) {
        left: 28%;
        animation-delay: 0.15s;
    }

    .party:nth-child(3) {
        left: 40%;
        animation-delay: 0.25s;
    }

    .party:nth-child(4) {
        left: 52%;
        animation-delay: 0.1s;
    }

    .party:nth-child(5) {
        left: 64%;
        animation-delay: 0.2s;
    }

    .party:nth-child(6) {
        left: 76%;
        animation-delay: 0.05s;
    }

    @keyframes party-fall {

        0% {
            transform:
                translateY(-80px)
                rotate(0deg)
            scale(0.5);

            opacity: 0;
        }

        30% {
            opacity: 1;
        }

        100% {
            transform:
                translateY(70px)
                rotate(30deg)
            scale(1.2);

            opacity: 0;
        }
    }


    /* =====================================================
       FOOTER
       ===================================================== */

    .footer {
        text-align: center;

        color: #777777 !important;

        font-size: 13px;

        margin-top: 35px;

        padding: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# FUNCTIONS
# =========================================================

def show_party_booster(message):
    """
    Shows a party-popper celebration.
    No balloons are used.
    """

    st.markdown(
        """
        <div class="party-container">

            <div class="party">🎉</div>
            <div class="party">🎊</div>
            <div class="party">🎉</div>
            <div class="party">🎊</div>
            <div class="party">🎉</div>
            <div class="party">🎊</div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.success(message)


# =========================================================
# LOAD SECRETS
# =========================================================

EMAIL_ADDRESS = st.secrets["EMAIL_ADDRESS"]
EMAIL_APP_PASSWORD = st.secrets["EMAIL_APP_PASSWORD"]

TWILIO_ACCOUNT_SID = st.secrets["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = st.secrets["TWILIO_AUTH_TOKEN"]
TWILIO_VERIFY_SERVICE_SID = st.secrets[
    "TWILIO_VERIFY_SERVICE_SID"
]


# =========================================================
# TWILIO CLIENT
# =========================================================

twilio_client = Client(
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN
)


# =========================================================
# SESSION STATE
# =========================================================

defaults = {

    "email_otp_value": None,
    "email_otp_time": None,

    "email_verified": False,
    "sms_verified": False,
    "whatsapp_verified": False
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# OTP GENERATOR
# =========================================================

def generate_otp():

    return str(
        secrets.randbelow(900000) + 100000
    )


# =========================================================
# EMAIL OTP
# =========================================================

def send_email_otp(email):

    otp = generate_otp()

    subject = "PragyanAI Verification OTP"

    body = f"""
Hello,

Your PragyanAI verification OTP is:

{otp}

This OTP is valid for 5 minutes.

Do not share this OTP with anyone.

Regards,
PragyanAI
"""

    message = MIMEMultipart()

    message["From"] = EMAIL_ADDRESS
    message["To"] = email
    message["Subject"] = subject

    message.attach(
        MIMEText(body, "plain")
    )

    with smtplib.SMTP(
        "smtp.gmail.com",
        587
    ) as server:

        server.starttls()

        server.login(
            EMAIL_ADDRESS,
            EMAIL_APP_PASSWORD
        )

        server.sendmail(
            EMAIL_ADDRESS,
            email,
            message.as_string()
        )

    st.session_state.email_otp_value = otp

    st.session_state.email_otp_time = time.time()


def verify_email_otp(entered_otp):

    if not entered_otp:

        return False, "Please enter the OTP."

    if st.session_state.email_otp_value is None:

        return False, "Please request a new OTP."

    elapsed = (
        time.time()
        - st.session_state.email_otp_time
    )

    if elapsed > 300:

        st.session_state.email_otp_value = None

        st.session_state.email_otp_time = None

        return False, (
            "OTP expired. Please request a new OTP."
        )

    if entered_otp == st.session_state.email_otp_value:

        st.session_state.email_verified = True

        st.session_state.email_otp_value = None

        st.session_state.email_otp_time = None

        return True, "Email verified successfully."

    return False, "Invalid OTP."


# =========================================================
# TWILIO OTP
# =========================================================

def send_twilio_otp(phone, channel):

    verification = (
        twilio_client
        .verify
        .v2
        .services(TWILIO_VERIFY_SERVICE_SID)
        .verifications
        .create(
            to=phone,
            channel=channel
        )
    )

    return verification.status


def verify_twilio_otp(phone, otp):

    result = (
        twilio_client
        .verify
        .v2
        .services(TWILIO_VERIFY_SERVICE_SID)
        .verification_checks
        .create(
            to=phone,
            code=otp
        )
    )

    return result.status == "approved"


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        '<div class="sidebar-logo">🔐 PragyanAI</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-subtitle">'
        'Secure OTP Verification'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.markdown(
        '<div class="sidebar-section">'
        'Verification Methods'
        '</div>',
        unsafe_allow_html=True
    )

    selected_method = st.radio(
        "Select method",
        [
            "📧 Email",
            "📱 SMS",
            "💬 WhatsApp"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")

    st.markdown(
        """
        **PragyanAI**

        🔐 Secure

        ⚡ Fast

        🛡️ OTP Protected
        """
    )


# =========================================================
# HERO HEADER
# =========================================================

st.markdown(
    """
    <div class="hero">

        <div class="hero-title">
            🔐 PragyanAI OTP Verification
        </div>

        <div class="hero-subtitle">
            Verify your identity securely using
            Email, SMS or WhatsApp.
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# EMAIL
# =========================================================

if selected_method == "📧 Email":

    st.markdown(
        """
        <div class="verification-card">

            <div class="method-icon">
                📧
            </div>

            <div class="method-title">
                Email Verification
            </div>

            <div class="method-description">
                Enter your email address to receive
                a secure 6-digit verification code.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    email = st.text_input(
        "Email Address",
        placeholder="example@gmail.com",
        key="email_address"
    )

    if st.button(
        "📨 Send Email OTP",
        key="send_email",
        use_container_width=True
    ):

        if not email:

            st.error(
                "Please enter your email address."
            )

        else:

            try:

                send_email_otp(email)

                st.success(
                    "✅ OTP sent successfully to your email."
                )

            except Exception as e:

                st.error(
                    f"❌ Email sending failed: {e}"
                )

    st.markdown(
        '<div class="soft-divider"></div>',
        unsafe_allow_html=True
    )

    email_otp_input = st.text_input(
        "Enter Email OTP",
        max_chars=6,
        placeholder="Enter 6-digit OTP",
        key="email_otp_input"
    )

    if st.button(
        "🔓 Verify Email OTP",
        key="verify_email",
        use_container_width=True
    ):

        success, message = verify_email_otp(
            email_otp_input
        )

        if success:

            show_party_booster(
                "🎉 Email verified successfully!"
            )

        else:

            st.error(message)

    if st.session_state.email_verified:

        st.markdown(
            """
            <div class="verified-box">
                ✓ Email verification completed
            </div>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# SMS
# =========================================================

elif selected_method == "📱 SMS":

    st.markdown(
        """
        <div class="verification-card">

            <div class="method-icon">
                📱
            </div>

            <div class="method-title">
                SMS Verification
            </div>

            <div class="method-description">
                Enter your mobile number to receive
                a secure verification code through SMS.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    phone = st.text_input(
        "Phone Number",
        placeholder="+919876543210",
        key="sms_phone"
    )

    if st.button(
        "📲 Send SMS OTP",
        key="send_sms",
        use_container_width=True
    ):

        if not phone:

            st.error(
                "Please enter your phone number."
            )

        else:

            try:

                send_twilio_otp(
                    phone,
                    "sms"
                )

                st.success(
                    "✅ SMS OTP sent successfully."
                )

            except Exception as e:

                st.error(
                    f"❌ SMS failed: {e}"
                )

    st.markdown(
        '<div class="soft-divider"></div>',
        unsafe_allow_html=True
    )

    sms_otp = st.text_input(
        "Enter SMS OTP",
        max_chars=6,
        placeholder="Enter 6-digit OTP",
        key="sms_otp"
    )

    if st.button(
        "🔓 Verify SMS OTP",
        key="verify_sms",
        use_container_width=True
    ):

        if not phone:

            st.error(
                "Please enter your phone number first."
            )

        elif not sms_otp:

            st.error(
                "Please enter the OTP."
            )

        else:

            try:

                verified = verify_twilio_otp(
                    phone,
                    sms_otp
                )

                if verified:

                    st.session_state.sms_verified = True

                    show_party_booster(
                        "🎉 SMS verification successful!"
                    )

                else:

                    st.error(
                        "❌ Invalid OTP."
                    )

            except Exception as e:

                st.error(
                    f"❌ Verification failed: {e}"
                )

    if st.session_state.sms_verified:

        st.markdown(
            """
            <div class="verified-box">
                ✓ SMS verification completed
            </div>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# WHATSAPP
# =========================================================

elif selected_method == "💬 WhatsApp":

    st.markdown(
        """
        <div class="verification-card">

            <div class="method-icon">
                💬
            </div>

            <div class="method-title">
                WhatsApp Verification
            </div>

            <div class="method-description">
                Enter your WhatsApp number to receive
                a secure verification code through WhatsApp.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    whatsapp = st.text_input(
        "WhatsApp Number",
        placeholder="+919876543210",
        key="whatsapp_phone"
    )

    if st.button(
        "💬 Send WhatsApp OTP",
        key="send_whatsapp",
        use_container_width=True
    ):

        if not whatsapp:

            st.error(
                "Please enter your WhatsApp number."
            )

        else:

            try:

                send_twilio_otp(
                    whatsapp,
                    "whatsapp"
                )

                st.success(
                    "✅ WhatsApp OTP sent successfully."
                )

            except Exception as e:

                st.error(
                    f"❌ WhatsApp failed: {e}"
                )

    st.markdown(
        '<div class="soft-divider"></div>',
        unsafe_allow_html=True
    )

    whatsapp_otp = st.text_input(
        "Enter WhatsApp OTP",
        max_chars=6,
        placeholder="Enter 6-digit OTP",
        key="whatsapp_otp"
    )

    if st.button(
        "🔓 Verify WhatsApp OTP",
        key="verify_whatsapp",
        use_container_width=True
    ):

        if not whatsapp:

            st.error(
                "Please enter your WhatsApp number first."
            )

        elif not whatsapp_otp:

            st.error(
                "Please enter the OTP."
            )

        else:

            try:

                verified = verify_twilio_otp(
                    whatsapp,
                    whatsapp_otp
                )

                if verified:

                    st.session_state.whatsapp_verified = True

                    show_party_booster(
                        "🎉 WhatsApp verification successful!"
                    )

                else:

                    st.error(
                        "❌ Invalid OTP."
                    )

            except Exception as e:

                st.error(
                    f"❌ Verification failed: {e}"
                )

    if st.session_state.whatsapp_verified:

        st.markdown(
            """
            <div class="verified-box">
                ✓ WhatsApp verification completed
            </div>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">

        🔐 PragyanAI OTP Verification
        <br>
        Secure • Simple • Reliable

    </div>
    """,
    unsafe_allow_html=True
)
