import streamlit as st
import time
import smtplib
import requests
import secrets as py_secrets

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="PragyanAI OTP Verification",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

    /* Main background */
    .stApp {
        background: #f5f7fb;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #111827;
    }

    section[data-testid="stSidebar"] * {
        color: white;
    }

    /* Main title */
    .main-title {
        font-size: 42px;
        font-weight: 800;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        color: #6b7280;
        font-size: 18px;
        margin-bottom: 30px;
    }

    /* Card */
    .otp-card {
        background: white;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0px 5px 20px rgba(0,0,0,0.08);
        max-width: 800px;
        margin: auto;
    }

    .card-title {
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .card-description {
        color: #6b7280;
        margin-bottom: 25px;
    }

    /* Status */
    .info-box {
        padding: 12px;
        border-radius: 10px;
        background: #eef2ff;
        margin-top: 15px;
    }

    /* Sidebar title */
    .sidebar-title {
        font-size: 25px;
        font-weight: 800;
        text-align: center;
        margin-bottom: 20px;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #6b7280;
        margin-top: 40px;
        padding: 20px;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# LOAD SECRETS
# ============================================================

try:

    EMAIL_ADDRESS = st.secrets["EMAIL_ADDRESS"]
    EMAIL_APP_PASSWORD = st.secrets["EMAIL_APP_PASSWORD"]

    TWILIO_ACCOUNT_SID = st.secrets["TWILIO_ACCOUNT_SID"]
    TWILIO_AUTH_TOKEN = st.secrets["TWILIO_AUTH_TOKEN"]
    TWILIO_VERIFY_SERVICE_SID = st.secrets[
        "TWILIO_VERIFY_SERVICE_SID"
    ]

    TELEGRAM_BOT_TOKEN = st.secrets[
        "TELEGRAM_BOT_TOKEN"
    ]

except Exception as e:

    st.error("❌ Streamlit Secrets are not configured correctly.")

    st.info("""
    Go to:

    Streamlit Cloud → Your App → Settings → Secrets

    Required secrets:

    EMAIL_ADDRESS
    EMAIL_APP_PASSWORD
    TWILIO_ACCOUNT_SID
    TWILIO_AUTH_TOKEN
    TWILIO_VERIFY_SERVICE_SID
    TELEGRAM_GATEWAY_TOKEN
    """)

    st.stop()


# ============================================================
# TWILIO CLIENT
# ============================================================

twilio_client = Client(
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN
)


# ============================================================
# SESSION STATE
# ============================================================

# IMPORTANT:
# Widget keys and stored OTP keys are DIFFERENT.
#
# This prevents:
# StreamlitWidgetAlreadyInstantiatedError

if "email_otp_value" not in st.session_state:
    st.session_state.email_otp_value = None

if "email_otp_time" not in st.session_state:
    st.session_state.email_otp_time = None

if "email_verified" not in st.session_state:
    st.session_state.email_verified = False

if "telegram_request_id" not in st.session_state:
    st.session_state.telegram_request_id = None


# ============================================================
# OTP GENERATOR
# ============================================================

def generate_otp():

    return str(
        py_secrets.randbelow(900000) + 100000
    )


# ============================================================
# EMAIL OTP
# ============================================================

def send_email_otp(email):

    otp = generate_otp()

    subject = "PragyanAI Verification OTP"

    body = f"""
Hello,

Your PragyanAI verification OTP is:

{otp}

This OTP is valid for 5 minutes.

Please do not share this OTP with anyone.

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

    # IMPORTANT:
    # This is NOT the widget key.
    st.session_state.email_otp_value = otp
    st.session_state.email_otp_time = time.time()


def verify_email_otp(entered_otp):

    if not entered_otp:

        return False, "Please enter the OTP."

    saved_otp = st.session_state.email_otp_value

    if saved_otp is None:

        return False, "Please request a new OTP."

    if st.session_state.email_otp_time is None:

        return False, "Please request a new OTP."

    elapsed = (
        time.time()
        - st.session_state.email_otp_time
    )

    # 5 minutes
    if elapsed > 300:

        st.session_state.email_otp_value = None
        st.session_state.email_otp_time = None

        return False, "OTP expired. Please request a new OTP."

    if entered_otp == saved_otp:

        st.session_state.email_verified = True

        # Clear STORAGE key, not widget key
        st.session_state.email_otp_value = None
        st.session_state.email_otp_time = None

        return True, "Email verified successfully."

    return False, "Invalid OTP."


# ============================================================
# TWILIO SMS / WHATSAPP
# ============================================================

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

    verification_check = (
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

    return verification_check.status == "approved"


# ============================================================
# TELEGRAM GATEWAY
# ============================================================

TELEGRAM_URL = "https://gatewayapi.telegram.org"


def send_telegram_otp(phone):

    url = (
        f"{TELEGRAM_URL}/sendVerificationMessage"
    )

    headers = {
        "Authorization":
        f"Bearer {TELEGRAM_BOT_TOKEN}",

        "Content-Type":
        "application/json"
    }

    payload = {
        "phone_number": phone,
        "code_length": 6,
        "ttl": 300
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=20
    )

    data = response.json()

    if not data.get("ok"):

        raise Exception(
            data.get(
                "error",
                "Telegram OTP failed"
            )
        )

    return data["result"]["request_id"]


def verify_telegram_otp(request_id, otp):

    url = (
        f"{TELEGRAM_URL}/checkVerificationStatus"
    )

    headers = {
        "Authorization":
        f"Bearer {TELEGRAM_BOT_TOKEN}",

        "Content-Type":
        "application/json"
    }

    payload = {
        "request_id": request_id,
        "code": otp
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=20
    )

    data = response.json()

    if not data.get("ok"):

        raise Exception(
            data.get(
                "error",
                "Telegram verification failed"
            )
        )

    status = data["result"]["verification_status"]["status"]

    return status == "code_valid"


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        '<div class="sidebar-title">'
        '🔐 PragyanAI'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        "### OTP Verification"
    )

    st.write(
        "Choose a verification method:"
    )

    selected_method = st.radio(
        "Select",
        [
            "📧 Email",
            "📱 SMS",
            "💬 WhatsApp",
            "✈️ Telegram"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    st.info(
        "Enter your details, send an OTP, "
        "and then verify the OTP."
    )

    st.divider()

    st.caption(
        "PragyanAI OTP System"
    )


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">'
    '🔐 PragyanAI OTP Verification'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Secure multi-channel OTP verification'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# EMAIL PAGE
# ============================================================

if selected_method == "📧 Email":

    st.markdown(
        '<div class="otp-card">',
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
        'Receive a verification code through email.'
        '</div>',
        unsafe_allow_html=True
    )

    email = st.text_input(
        "Email Address",
        placeholder="example@gmail.com",
        key="email_address_input"
    )

    if st.button(
        "📨 Send Email OTP",
        key="email_send_button",
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

    st.write("")

    # DIFFERENT KEY FROM email_otp_value
    email_otp_input = st.text_input(
        "Enter Email OTP",
        placeholder="Enter 6-digit OTP",
        max_chars=6,
        key="email_otp_input"
    )

    if st.button(
        "✅ Verify Email OTP",
        key="email_verify_button",
        use_container_width=True
    ):

        success, message = verify_email_otp(
            email_otp_input
        )

        if success:

            st.success(
                f"🎉 {message}"
            )

        else:

            st.error(message)

    if st.session_state.email_verified:

        st.success(
            "🟢 Email verification completed."
        )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


# ============================================================
# SMS PAGE
# ============================================================

elif selected_method == "📱 SMS":

    st.markdown(
        '<div class="otp-card">',
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
        'Receive a verification code through SMS.'
        '</div>',
        unsafe_allow_html=True
    )

    phone = st.text_input(
        "Phone Number",
        placeholder="+919876543210",
        key="sms_phone_input"
    )

    if st.button(
        "📲 Send SMS OTP",
        key="sms_send_button",
        use_container_width=True
    ):

        if not phone:

            st.error(
                "Please enter your phone number."
            )

        else:

            try:

                status = send_twilio_otp(
                    phone,
                    "sms"
                )

                st.success(
                    f"✅ OTP sent successfully. "
                    f"Status: {status}"
                )

            except Exception as e:

                st.error(
                    f"❌ SMS failed: {e}"
                )

    st.write("")

    sms_otp = st.text_input(
        "Enter SMS OTP",
        placeholder="Enter 6-digit OTP",
        max_chars=6,
        key="sms_otp_input"
    )

    if st.button(
        "✅ Verify SMS OTP",
        key="sms_verify_button",
        use_container_width=True
    ):

        if not phone:

            st.error(
                "Please enter your phone number."
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

                    st.success(
                        "🎉 Phone number verified successfully."
                    )

                else:

                    st.error(
                        "❌ Invalid OTP."
                    )

            except Exception as e:

                st.error(
                    f"❌ Verification failed: {e}"
                )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


# ============================================================
# WHATSAPP PAGE
# ============================================================

elif selected_method == "💬 WhatsApp":

    st.markdown(
        '<div class="otp-card">',
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
        'Receive a verification code through WhatsApp.'
        '</div>',
        unsafe_allow_html=True
    )

    whatsapp = st.text_input(
        "WhatsApp Number",
        placeholder="+919876543210",
        key="whatsapp_phone_input"
    )

    if st.button(
        "💬 Send WhatsApp OTP",
        key="whatsapp_send_button",
        use_container_width=True
    ):

        if not whatsapp:

            st.error(
                "Please enter your WhatsApp number."
            )

        else:

            try:

                status = send_twilio_otp(
                    whatsapp,
                    "whatsapp"
                )

                st.success(
                    f"✅ WhatsApp OTP sent successfully. "
                    f"Status: {status}"
                )

            except Exception as e:

                st.error(
                    f"❌ WhatsApp failed: {e}"
                )

    st.write("")

    whatsapp_otp = st.text_input(
        "Enter WhatsApp OTP",
        placeholder="Enter 6-digit OTP",
        max_chars=6,
        key="whatsapp_otp_input"
    )

    if st.button(
        "✅ Verify WhatsApp OTP",
        key="whatsapp_verify_button",
        use_container_width=True
    ):

        if not whatsapp:

            st.error(
                "Please enter your WhatsApp number."
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

                    st.success(
                        "🎉 WhatsApp number verified successfully."
                    )

                else:

                    st.error(
                        "❌ Invalid OTP."
                    )

            except Exception as e:

                st.error(
                    f"❌ Verification failed: {e}"
                )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


# ============================================================
# TELEGRAM PAGE
# ============================================================

elif selected_method == "✈️ Telegram":

    st.markdown(
        '<div class="otp-card">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="card-title">'
        '✈️ Telegram Verification'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="card-description">'
        'Receive a verification code through Telegram.'
        '</div>',
        unsafe_allow_html=True
    )

    telegram_phone = st.text_input(
        "Telegram Phone Number",
        placeholder="+919876543210",
        key="telegram_phone_input"
    )

    if st.button(
        "✈️ Send Telegram OTP",
        key="telegram_send_button",
        use_container_width=True
    ):

        if not telegram_phone:

            st.error(
                "Please enter your phone number."
            )

        else:

            try:

                request_id = send_telegram_otp(
                    telegram_phone
                )

                st.session_state.telegram_request_id = (
                    request_id
                )

                st.success(
                    "✅ Telegram OTP sent successfully."
                )

            except Exception as e:

                st.error(
                    f"❌ Telegram OTP failed: {e}"
                )

    st.write("")

    telegram_otp = st.text_input(
        "Enter Telegram OTP",
        placeholder="Enter 6-digit OTP",
        max_chars=8,
        key="telegram_otp_input"
    )

    if st.button(
        "✅ Verify Telegram OTP",
        key="telegram_verify_button",
        use_container_width=True
    ):

        request_id = st.session_state.telegram_request_id

        if not request_id:

            st.error(
                "Please send a Telegram OTP first."
            )

        elif not telegram_otp:

            st.error(
                "Please enter the OTP."
            )

        else:

            try:

                verified = verify_telegram_otp(
                    request_id,
                    telegram_otp
                )

                if verified:

                    st.success(
                        "🎉 Telegram number verified successfully."
                    )

                    st.session_state.telegram_request_id = None

                else:

                    st.error(
                        "❌ Invalid or expired OTP."
                    )

            except Exception as e:

                st.error(
                    f"❌ Verification failed: {e}"
                )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    '<div class="footer">'
    'PragyanAI • Email • SMS • WhatsApp • Telegram'
    '</div>',
    unsafe_allow_html=True
)
