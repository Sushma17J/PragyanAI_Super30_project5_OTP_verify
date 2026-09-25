import streamlit as st
import smtplib
import random
import time
import re
import hashlib
import requests

from email.message import EmailMessage
from twilio.rest import Client


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="PragyanAI OTP Verification",
    page_icon="🔐",
    layout="wide"
)


# ============================================================
# CUSTOM DESIGN
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: bold;
        margin-bottom: 5px;
    }

    .sub-title {
        text-align: center;
        font-size: 18px;
        color: gray;
        margin-bottom: 30px;
    }

    .channel-box {
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #dddddd;
        margin-bottom: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🔐 PragyanAI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">Secure Multi-Channel OTP Verification System</div>',
    unsafe_allow_html=True
)

st.divider()


# ============================================================
# LOAD STREAMLIT SECRETS
# ============================================================

try:

    EMAIL_ADDRESS = st.secrets["EMAIL_ADDRESS"]
    EMAIL_APP_PASSWORD = st.secrets["EMAIL_APP_PASSWORD"]

    TWILIO_ACCOUNT_SID = st.secrets["TWILIO_ACCOUNT_SID"]
    TWILIO_AUTH_TOKEN = st.secrets["TWILIO_AUTH_TOKEN"]
    TWILIO_VERIFY_SERVICE_SID = st.secrets[
        "TWILIO_VERIFY_SERVICE_SID"
    ]

    TELEGRAM_BOT_TOKEN = st.secrets["TELEGRAM_BOT_TOKEN"]

except Exception:

    st.error("❌ Streamlit Secrets are not configured.")

    st.info(
        """
        Add these values in Streamlit Cloud → Settings → Secrets:

        EMAIL_ADDRESS
        EMAIL_APP_PASSWORD
        TWILIO_ACCOUNT_SID
        TWILIO_AUTH_TOKEN
        TWILIO_VERIFY_SERVICE_SID
        TELEGRAM_BOT_TOKEN
        """
    )

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

session_defaults = {

    "email_hash": None,
    "email_time": None,
    "email_verified": False,

    "telegram_hash": None,
    "telegram_time": None,
    "telegram_verified": False,

    "sms_verified": False,
    "whatsapp_verified": False
}


for key, value in session_defaults.items():

    if key not in st.session_state:

        st.session_state[key] = value


# ============================================================
# COMMON FUNCTIONS
# ============================================================

def generate_otp():

    return f"{random.SystemRandom().randint(0, 999999):06d}"


def hash_otp(otp):

    return hashlib.sha256(
        otp.encode("utf-8")
    ).hexdigest()


def valid_email(email):

    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    return re.fullmatch(
        pattern,
        email or ""
    ) is not None


def valid_phone(phone):

    pattern = r"^\+[1-9]\d{7,14}$"

    return re.fullmatch(
        pattern,
        phone or ""
    ) is not None


# ============================================================
# EMAIL OTP
# ============================================================

def send_email_otp(email):

    if not email:

        return False, "❌ Please enter your email address."

    if not valid_email(email):

        return False, "❌ Please enter a valid email address."

    try:

        otp = generate_otp()

        message = EmailMessage()

        message["Subject"] = (
            "PragyanAI - Email Verification OTP"
        )

        message["From"] = EMAIL_ADDRESS

        message["To"] = email

        message.set_content(
            f"""
Hello,

Your PragyanAI verification OTP is:

{otp}

This OTP is valid for 5 minutes.

Please do not share this OTP with anyone.

Regards,
PragyanAI
"""
        )

        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465
        ) as smtp:

            smtp.login(
                EMAIL_ADDRESS,
                EMAIL_APP_PASSWORD
            )

            smtp.send_message(message)

        st.session_state.email_hash = hash_otp(otp)

        st.session_state.email_time = time.time()

        return True, "✅ Email OTP sent successfully."

    except Exception as e:

        return False, f"❌ Email sending failed: {e}"


def verify_email_otp(otp):

    if not otp:

        return False, "❌ Please enter the Email OTP."

    if not otp.isdigit() or len(otp) != 6:

        return False, "❌ OTP must contain exactly 6 digits."

    if st.session_state.email_hash is None:

        return False, "❌ Please send an Email OTP first."

    if (
        time.time()
        - st.session_state.email_time
        > 300
    ):

        st.session_state.email_hash = None

        st.session_state.email_time = None

        return False, "⏰ OTP expired. Please request a new OTP."

    if (
        hash_otp(otp)
        == st.session_state.email_hash
    ):

        st.session_state.email_verified = True

        st.session_state.email_hash = None

        st.session_state.email_time = None

        return True, "🎉 Email verified successfully."

    return False, "❌ Invalid Email OTP."


# ============================================================
# TWILIO SMS / WHATSAPP
# ============================================================

def send_twilio_otp(phone, channel):

    if not phone:

        return False, "❌ Please enter your phone number."

    if not valid_phone(phone):

        return (
            False,
            "❌ Use international format, e.g. +919876543210."
        )

    try:

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

        return (
            True,
            f"✅ {channel.upper()} OTP sent successfully. "
            f"Status: {verification.status}"
        )

    except Exception as e:

        return (
            False,
            f"❌ {channel.upper()} sending failed: {e}"
        )


def verify_twilio_otp(phone, otp):

    if not phone:

        return False, "❌ Please enter your phone number."

    if not otp:

        return False, "❌ Please enter the OTP."

    if not valid_phone(phone):

        return (
            False,
            "❌ Use international format, e.g. +919876543210."
        )

    if not otp.isdigit() or len(otp) != 6:

        return False, "❌ OTP must contain exactly 6 digits."

    try:

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

        if verification_check.status == "approved":

            return True, "🎉 OTP verified successfully."

        return False, "❌ Invalid or expired OTP."

    except Exception as e:

        return (
            False,
            f"❌ OTP verification failed: {e}"
        )


# ============================================================
# TELEGRAM OTP
# ============================================================

def send_telegram_otp(chat_id):

    if not chat_id:

        return False, "❌ Please enter your Telegram Chat ID."

    otp = generate_otp()

    url = (
        "https://api.telegram.org/"
        f"bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    )

    message = (
        "🔐 PragyanAI OTP Verification\n\n"
        f"Your OTP is: {otp}\n\n"
        "This OTP is valid for 5 minutes.\n"
        "Do not share this OTP with anyone."
    )

    try:

        response = requests.post(
            url,
            json={
                "chat_id": chat_id.strip(),
                "text": message
            },
            timeout=15
        )

        data = response.json()

        if response.ok and data.get("ok"):

            st.session_state.telegram_hash = hash_otp(
                otp
            )

            st.session_state.telegram_time = time.time()

            return (
                True,
                "✅ Telegram OTP sent successfully."
            )

        return (
            False,
            "❌ Telegram failed: "
            + str(
                data.get(
                    "description",
                    "Unknown error"
                )
            )
        )

    except Exception as e:

        return False, f"❌ Telegram failed: {e}"


def verify_telegram_otp(otp):

    if not otp:

        return False, "❌ Please enter the Telegram OTP."

    if not otp.isdigit() or len(otp) != 6:

        return False, "❌ OTP must contain exactly 6 digits."

    if st.session_state.telegram_hash is None:

        return False, "❌ Please send a Telegram OTP first."

    if (
        time.time()
        - st.session_state.telegram_time
        > 300
    ):

        st.session_state.telegram_hash = None

        st.session_state.telegram_time = None

        return False, "⏰ Telegram OTP expired."

    if (
        hash_otp(otp)
        == st.session_state.telegram_hash
    ):

        st.session_state.telegram_verified = True

        st.session_state.telegram_hash = None

        st.session_state.telegram_time = None

        return (
            True,
            "🎉 Telegram verified successfully."
        )

    return False, "❌ Invalid Telegram OTP."


# ============================================================
# TABS
# ============================================================

email_tab, sms_tab, whatsapp_tab, telegram_tab = st.tabs(
    [
        "📧 Email",
        "📱 SMS",
        "🟢 WhatsApp",
        "✈️ Telegram"
    ]
)


# ============================================================
# EMAIL TAB
# ============================================================

with email_tab:

    st.subheader("📧 Email OTP Verification")

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

        success, message = send_email_otp(
            email
        )

        if success:

            st.success(message)

        else:

            st.error(message)

    email_otp = st.text_input(
        "Enter Email OTP",
        placeholder="6-digit OTP",
        max_chars=6,
        type="password",
        key="email_otp"
    )

    if st.button(
        "✅ Verify Email",
        key="verify_email",
        use_container_width=True
    ):

        success, message = verify_email_otp(
            email_otp
        )

        if success:

            st.success(message)

            st.balloons()

        else:

            st.error(message)

    if st.session_state.email_verified:

        st.success(
            "🎉 Email verification completed."
        )


# ============================================================
# SMS TAB
# ============================================================

with sms_tab:

    st.subheader("📱 SMS OTP Verification")

    sms_phone = st.text_input(
        "Phone Number",
        placeholder="+919876543210",
        key="sms_phone"
    )

    if st.button(
        "📨 Send SMS OTP",
        key="send_sms",
        use_container_width=True
    ):

        success, message = send_twilio_otp(
            sms_phone,
            "sms"
        )

        if success:

            st.success(message)

        else:

            st.error(message)

    sms_otp = st.text_input(
        "Enter SMS OTP",
        placeholder="6-digit OTP",
        max_chars=6,
        type="password",
        key="sms_otp"
    )

    if st.button(
        "✅ Verify SMS",
        key="verify_sms",
        use_container_width=True
    ):

        success, message = verify_twilio_otp(
            sms_phone,
            sms_otp
        )

        if success:

            st.session_state.sms_verified = True

            st.success(message)

            st.balloons()

        else:

            st.error(message)

    if st.session_state.sms_verified:

        st.success(
            "🎉 SMS verification completed."
        )


# ============================================================
# WHATSAPP TAB
# ============================================================

with whatsapp_tab:

    st.subheader("🟢 WhatsApp OTP Verification")

    st.info(
        "WhatsApp OTP requires WhatsApp to be enabled "
        "and configured in your Twilio Verify Service."
    )

    whatsapp_phone = st.text_input(
        "WhatsApp Number",
        placeholder="+919876543210",
        key="whatsapp_phone"
    )

    if st.button(
        "💬 Send WhatsApp OTP",
        key="send_whatsapp",
        use_container_width=True
    ):

        success, message = send_twilio_otp(
            whatsapp_phone,
            "whatsapp"
        )

        if success:

            st.success(message)

        else:

            st.error(message)

    whatsapp_otp = st.text_input(
        "Enter WhatsApp OTP",
        placeholder="6-digit OTP",
        max_chars=6,
        type="password",
        key="whatsapp_otp"
    )

    if st.button(
        "✅ Verify WhatsApp",
        key="verify_whatsapp",
        use_container_width=True
    ):

        success, message = verify_twilio_otp(
            whatsapp_phone,
            whatsapp_otp
        )

        if success:

            st.session_state.whatsapp_verified = True

            st.success(message)

            st.balloons()

        else:

            st.error(message)

    if st.session_state.whatsapp_verified:

        st.success(
            "🎉 WhatsApp verification completed."
        )


# ============================================================
# TELEGRAM TAB
# ============================================================

with telegram_tab:

    st.subheader("✈️ Telegram OTP Verification")

    st.info(
        "Open your Telegram bot and press START before "
        "requesting an OTP."
    )

    chat_id = st.text_input(
        "Telegram Chat ID",
        placeholder="Example: 123456789",
        key="telegram_chat_id"
    )

    if st.button(
        "✈️ Send Telegram OTP",
        key="send_telegram",
        use_container_width=True
    ):

        success, message = send_telegram_otp(
            chat_id
        )

        if success:

            st.success(message)

        else:

            st.error(message)

    telegram_otp = st.text_input(
        "Enter Telegram OTP",
        placeholder="6-digit OTP",
        max_chars=6,
        type="password",
        key="telegram_otp"
    )

    if st.button(
        "✅ Verify Telegram",
        key="verify_telegram",
        use_container_width=True
    ):

        success, message = verify_telegram_otp(
            telegram_otp
        )

        if success:

            st.success(message)

            st.balloons()

        else:

            st.error(message)

    if st.session_state.telegram_verified:

        st.success(
            "🎉 Telegram verification completed."
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🔐 PragyanAI Multi-Channel OTP Verification System"
)

st.caption(
    "API credentials are loaded securely from Streamlit Secrets."
)
