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
    page_title="PragyanAI OTP Verification",
    page_icon="🔐",
    layout="wide"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* ================================
       MAIN PAGE
       ================================ */

    .stApp {
        background-color: #ffffff;
        color: #000000;
    }

    .main {
        background-color: #ffffff;
        color: #000000;
    }

    /* ================================
       ALL TEXT BLACK
       ================================ */

    p,
    span,
    label,
    div,
    h1,
    h2,
    h3,
    h4,
    h5,
    h6 {
        color: #000000;
    }

    /* ================================
       SIDEBAR
       ================================ */

    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #dddddd;
    }

    section[data-testid="stSidebar"] * {
        color: #000000 !important;
    }

    .sidebar-title {
        font-size: 26px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 5px;
        color: #000000 !important;
    }

    .sidebar-subtitle {
        font-size: 14px;
        text-align: center;
        color: #000000 !important;
        margin-bottom: 25px;
    }

    /* ================================
       MAIN TITLE
       ================================ */

    .title {
        text-align: center;
        font-size: 42px;
        font-weight: 800;
        color: #000000 !important;
        margin-top: 10px;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        color: #000000 !important;
        margin-bottom: 35px;
    }

    /* ================================
       CARD
       ================================ */

    .card {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 18px;
        border: 1px solid #dddddd;
        box-shadow: 0px 5px 20px rgba(0, 0, 0, 0.08);
        margin: auto;
        max-width: 850px;
    }

    .card-title {
        font-size: 28px;
        font-weight: 700;
        color: #000000 !important;
        margin-bottom: 20px;
    }

    .card-description {
        font-size: 16px;
        color: #000000 !important;
        margin-bottom: 20px;
    }

    /* ================================
       INPUT BOXES
       ================================ */

    input {
        color: #000000 !important;
        background-color: #ffffff !important;
    }

    textarea {
        color: #000000 !important;
        background-color: #ffffff !important;
    }

    [data-baseweb="input"] {
        background-color: #ffffff !important;
    }

    [data-baseweb="input"] input {
        color: #000000 !important;
        background-color: #ffffff !important;
    }

    /* ================================
       INPUT LABELS
       ================================ */

    .stTextInput label {
        color: #000000 !important;
        font-weight: 600;
    }

    /* ================================
       BUTTONS
       ================================ */

    .stButton > button {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 1px solid #000000 !important;
        border-radius: 10px;
        font-weight: 600;
        height: 48px;
    }

    .stButton > button:hover {
        background-color: #333333 !important;
        color: #ffffff !important;
        border-color: #333333 !important;
    }

    .stButton > button p {
        color: #ffffff !important;
    }

    /* ================================
       RADIO BUTTON
       ================================ */

    div[data-testid="stRadio"] label {
        color: #000000 !important;
        font-weight: 600;
    }

    div[data-testid="stRadio"] label p {
        color: #000000 !important;
    }

    /* ================================
       FOOTER
       ================================ */

    .footer {
        text-align: center;
        color: #000000 !important;
        font-size: 14px;
        margin-top: 30px;
        padding: 20px;
    }

    /* ================================
       STATUS BOX
       ================================ */

    .info-box {
        background-color: #f5f5f5;
        border-left: 5px solid #000000;
        padding: 15px;
        border-radius: 8px;
        margin-top: 15px;
        color: #000000 !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# TITLE
# =========================================================

st.markdown(
    '<div class="title">🔐 PragyanAI OTP Verification</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Secure OTP verification using Email, SMS and WhatsApp'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# LOAD SECRETS
# =========================================================

EMAIL_ADDRESS = st.secrets["EMAIL_ADDRESS"]
EMAIL_APP_PASSWORD = st.secrets["EMAIL_APP_PASSWORD"]

TWILIO_ACCOUNT_SID = st.secrets["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = st.secrets["TWILIO_AUTH_TOKEN"]
TWILIO_VERIFY_SERVICE_SID = st.secrets["TWILIO_VERIFY_SERVICE_SID"]


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

    # Email OTP storage
    "email_otp_value": None,
    "email_otp_time": None,

    # Verification status
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
# VIRTUAL PARTY BLAST
# =========================================================

def party_booster():

    st.markdown(
        """
        <style>

        /* Main celebration */

        .party-center {
            position: relative;
            text-align: center;
            height: 100px;
            overflow: visible;
            z-index: 9999;
        }

        .party-main {
            position: absolute;
            left: 50%;
            top: 10px;
            transform: translateX(-50%) scale(0.1);
            font-size: 65px;
            animation: party-pop 0.8s ease-out forwards;
        }

        @keyframes party-pop {

            0% {
                transform: translateX(-50%) scale(0.1);
                opacity: 0;
            }

            50% {
                transform: translateX(-50%) scale(1.5);
                opacity: 1;
            }

            75% {
                transform: translateX(-50%) scale(0.9);
            }

            100% {
                transform: translateX(-50%) scale(1);
                opacity: 1;
            }

        }

        /* Explosion particles */

        .blast {
            position: fixed;
            left: 50%;
            top: 45%;
            font-size: 28px;
            z-index: 99999;
            opacity: 0;
            animation: blast-animation 1.8s ease-out forwards;
        }

        @keyframes blast-animation {

            0% {
                transform: translate(0, 0) scale(0.2) rotate(0deg);
                opacity: 1;
            }

            20% {
                opacity: 1;
            }

            100% {
                transform:
                    translate(var(--x), var(--y))
                    scale(1.2)
                    rotate(720deg);
                opacity: 0;
            }

        }

        </style>

        <div class="party-center">

            <div class="party-main">
                🎉
            </div>

        </div>

        <!-- TOP LEFT -->
        <div class="blast"
             style="--x:-320px; --y:-220px; animation-delay:0s;">
            🎊
        </div>

        <div class="blast"
             style="--x:-250px; --y:-300px; animation-delay:0.05s;">
            ✨
        </div>

        <div class="blast"
             style="--x:-150px; --y:-350px; animation-delay:0.1s;">
            🎉
        </div>

        <!-- TOP CENTER -->
        <div class="blast"
             style="--x:-50px; --y:-380px; animation-delay:0.05s;">
            🎊
        </div>

        <div class="blast"
             style="--x:50px; --y:-380px; animation-delay:0.1s;">
            ✨
        </div>

        <div class="blast"
             style="--x:150px; --y:-350px; animation-delay:0.05s;">
            🎉
        </div>

        <div class="blast"
             style="--x:250px; --y:-300px; animation-delay:0.1s;">
            🎊
        </div>

        <div class="blast"
             style="--x:320px; --y:-220px; animation-delay:0s;">
            ✨
        </div>

        <!-- LEFT -->
        <div class="blast"
             style="--x:-400px; --y:-80px; animation-delay:0.1s;">
            🎉
        </div>

        <div class="blast"
             style="--x:-450px; --y:20px; animation-delay:0.05s;">
            🎊
        </div>

        <div class="blast"
             style="--x:-400px; --y:120px; animation-delay:0.1s;">
            ✨
        </div>

        <!-- RIGHT -->
        <div class="blast"
             style="--x:400px; --y:-80px; animation-delay:0.05s;">
            🎊
        </div>

        <div class="blast"
             style="--x:450px; --y:20px; animation-delay:0.1s;">
            🎉
        </div>

        <div class="blast"
             style="--x:400px; --y:120px; animation-delay:0.05s;">
            ✨
        </div>

        <!-- BOTTOM -->
        <div class="blast"
             style="--x:-300px; --y:220px; animation-delay:0.1s;">
            🎉
        </div>

        <div class="blast"
             style="--x:-180px; --y:280px; animation-delay:0.05s;">
            🎊
        </div>

        <div class="blast"
             style="--x:0px; --y:320px; animation-delay:0.1s;">
            ✨
        </div>

        <div class="blast"
             style="--x:180px; --y:280px; animation-delay:0.05s;">
            🎉
        </div>

        <div class="blast"
             style="--x:300px; --y:220px; animation-delay:0.1s;">
            🎊
        </div>

        """,
        unsafe_allow_html=True
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

    # Store generated OTP separately
    # from the text input widget
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

    # OTP expires after 5 minutes
    if elapsed > 300:

        st.session_state.email_otp_value = None
        st.session_state.email_otp_time = None

        return False, "OTP expired. Please request a new OTP."

    if entered_otp == st.session_state.email_otp_value:

        st.session_state.email_verified = True

        st.session_state.email_otp_value = None
        st.session_state.email_otp_time = None

        return True, "Email verified successfully."

    return False, "Invalid OTP."


# =========================================================
# SMS / WHATSAPP OTP
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
        '<div class="sidebar-title">🔐 PragyanAI</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-subtitle">'
        'OTP Verification System'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.markdown(
        "### Select Verification Method"
    )

    selected_method = st.radio(
        "Choose one",
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
        **Available Services**

        📧 Email OTP

        📱 SMS OTP

        💬 WhatsApp OTP
        """
    )


# =========================================================
# EMAIL VERIFICATION
# =========================================================

if selected_method == "📧 Email":

    st.markdown(
        '<div class="card">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="card-title">'
        '📧 Email Verification'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="card-description">'
        'Enter your email address and receive a secure OTP.'
        '</div>',
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

    st.markdown("")

    email_otp_input = st.text_input(
        "Enter Email OTP",
        max_chars=6,
        key="email_otp_input",
        placeholder="Enter 6-digit OTP"
    )

    if st.button(
        "✅ Verify Email OTP",
        key="verify_email",
        use_container_width=True
    ):

        success, message = verify_email_otp(
            email_otp_input
        )

        if success:

            st.success(
                "🎉 Email verification successful!"
            )

            party_booster()

        else:

            st.error(message)

    if st.session_state.email_verified:

        st.success(
            "🟢 Email is verified."
        )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


# =========================================================
# SMS VERIFICATION
# =========================================================

elif selected_method == "📱 SMS":

    st.markdown(
        '<div class="card">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="card-title">'
        '📱 SMS Verification'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="card-description">'
        'Enter your mobile number and receive an OTP through SMS.'
        '</div>',
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

    st.markdown("")

    sms_otp = st.text_input(
        "Enter SMS OTP",
        max_chars=6,
        key="sms_otp",
        placeholder="Enter 6-digit OTP"
    )

    if st.button(
        "✅ Verify SMS OTP",
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

                    st.success(
                        "🎉 SMS verification successful!"
                    )

                    party_booster()

                else:

                    st.error(
                        "❌ Invalid OTP."
                    )

            except Exception as e:

                st.error(
                    f"❌ Verification failed: {e}"
                )

    if st.session_state.sms_verified:

        st.success(
            "🟢 SMS number is verified."
        )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


# =========================================================
# WHATSAPP VERIFICATION
# =========================================================

elif selected_method == "💬 WhatsApp":

    st.markdown(
        '<div class="card">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="card-title">'
        '💬 WhatsApp Verification'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="card-description">'
        'Enter your WhatsApp number and receive an OTP through WhatsApp.'
        '</div>',
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

    st.markdown("")

    whatsapp_otp = st.text_input(
        "Enter WhatsApp OTP",
        max_chars=6,
        key="whatsapp_otp",
        placeholder="Enter 6-digit OTP"
    )

    if st.button(
        "✅ Verify WhatsApp OTP",
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

                    st.success(
                        "🎉 WhatsApp verification successful!"
                    )

                    party_booster()

                else:

                    st.error(
                        "❌ Invalid OTP."
                    )

            except Exception as e:

                st.error(
                    f"❌ Verification failed: {e}"
                )

    if st.session_state.whatsapp_verified:

        st.success(
            "🟢 WhatsApp number is verified."
        )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.markdown(
    '<div class="footer">'
    'PragyanAI • Secure OTP Verification System'
    '</div>',
    unsafe_allow_html=True
)
