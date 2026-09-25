import streamlit as st
import random
import time
import smtplib
import requests

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

st.markdown("""
<style>

.main {
    background-color: #f5f7fb;
}

.title {
    text-align: center;
    font-size: 42px;
    font-weight: 700;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    color: #666;
    font-size: 18px;
    margin-bottom: 30px;
}

.card {
    background: white;
    padding: 25px;
    border-radius: 18px;
    box-shadow: 0px 4px 18px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

.card-title {
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 15px;
}

.footer {
    text-align: center;
    color: #777;
    margin-top: 30px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# TITLE
# =========================================================

st.markdown(
    '<div class="title">🔐 PragyanAI OTP Verification</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Secure verification using Email, SMS, WhatsApp and Telegram'
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

TELEGRAM_GATEWAY_TOKEN = st.secrets["TELEGRAM_GATEWAY_TOKEN"]


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

    "email_otp": None,
    "email_time": None,

    "telegram_request_id": None,

    "email_verified": False,
    "sms_verified": False,
    "whatsapp_verified": False,
    "telegram_verified": False
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# OTP GENERATOR
# =========================================================

def generate_otp():

    return str(
        random.randint(100000, 999999)
    )


# =========================================================
# EMAIL
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

    st.session_state.email_otp = otp
    st.session_state.email_time = time.time()


def verify_email_otp(entered_otp):

    if not entered_otp:

        return False, "Please enter the OTP."

    if st.session_state.email_otp is None:

        return False, "Please request a new OTP."

    elapsed = (
        time.time()
        - st.session_state.email_time
    )

    if elapsed > 300:

        st.session_state.email_otp = None

        return False, "OTP expired. Please request a new OTP."

    if entered_otp == st.session_state.email_otp:

        st.session_state.email_verified = True

        st.session_state.email_otp = None

        return True, "Email verified successfully."

    return False, "Invalid OTP."


# =========================================================
# TWILIO SMS / WHATSAPP
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
# TELEGRAM GATEWAY
# =========================================================

TELEGRAM_URL = (
    "https://gatewayapi.telegram.org"
)


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


def verify_telegram_otp(
    request_id,
    otp
):

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

    return data["result"]["status"] == "code_valid"


# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📧 Email",
        "📱 SMS",
        "💬 WhatsApp",
        "✈️ Telegram"
    ]
)


# =========================================================
# EMAIL TAB
# =========================================================

with tab1:

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

    email_otp = st.text_input(
        "Enter Email OTP",
        max_chars=6,
        key="email_otp"
    )

    if st.button(
        "✅ Verify Email OTP",
        key="verify_email",
        use_container_width=True
    ):

        success, message = verify_email_otp(
            email_otp
        )

        if success:

            st.success(
                f"🎉 {message}"
            )

        else:

            st.error(message)

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


# =========================================================
# SMS TAB
# =========================================================

with tab2:

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

                status = send_twilio_otp(
                    phone,
                    "sms"
                )

                st.success(
                    f"✅ OTP sent successfully. Status: {status}"
                )

            except Exception as e:

                st.error(
                    f"❌ SMS failed: {e}"
                )

    sms_otp = st.text_input(
        "Enter SMS OTP",
        max_chars=6,
        key="sms_otp"
    )

    if st.button(
        "✅ Verify SMS OTP",
        key="verify_sms",
        use_container_width=True
    ):

        if not sms_otp:

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


# =========================================================
# WHATSAPP TAB
# =========================================================

with tab3:

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

                status = send_twilio_otp(
                    whatsapp,
                    "whatsapp"
                )

                st.success(
                    f"✅ WhatsApp OTP sent successfully. Status: {status}"
                )

            except Exception as e:

                st.error(
                    f"❌ WhatsApp failed: {e}"
                )

    whatsapp_otp = st.text_input(
        "Enter WhatsApp OTP",
        max_chars=6,
        key="whatsapp_otp"
    )

    if st.button(
        "✅ Verify WhatsApp OTP",
        key="verify_whatsapp",
        use_container_width=True
    ):

        if not whatsapp_otp:

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


# =========================================================
# TELEGRAM TAB
# =========================================================

with tab4:

    st.markdown(
        '<div class="card">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="card-title">'
        '✈️ Telegram Verification'
        '</div>',
        unsafe_allow_html=True
    )

    telegram_phone = st.text_input(
        "Telegram Phone Number",
        placeholder="+919876543210",
        key="telegram_phone"
    )

    if st.button(
        "✈️ Send Telegram OTP",
        key="send_telegram",
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

    telegram_otp = st.text_input(
        "Enter Telegram OTP",
        max_chars=8,
        key="telegram_otp"
    )

    if st.button(
        "✅ Verify Telegram OTP",
        key="verify_telegram",
        use_container_width=True
    ):

        if not st.session_state.telegram_request_id:

            st.error(
                "Please request a Telegram OTP first."
            )

        elif not telegram_otp:

            st.error(
                "Please enter the OTP."
            )

        else:

            try:

                verified = verify_telegram_otp(
                    st.session_state.telegram_request_id,
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
