import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email_validator import validate_email, EmailNotValidError
# cxrd svwc aiuh pszk
class EmailApp:
    def __init__(self):
        self.sender_email = None
        self.sender_password = None
        self.recipient_email = None
        self.subject = None
        self.body = None
        self.attachment = None
    
    # Determine SMTP server and port based on sender's email domain
    def get_smtp_details(self, sender_email):
        if "gmail.com" in sender_email:
            return "smtp.gmail.com", 587
        elif "outlook.com" in sender_email or "hotmail.com" in sender_email:
            return "smtp.office365.com", 587
        elif "yahoo.com" in sender_email:
            return "smtp.mail.yahoo.com", 587
        elif "icloud.com" in sender_email:
            return "smtp.mail.me.com", 587
        elif "zoho.com" in sender_email:
            return "smtp.zoho.com", 587
        else:
            return None, None  # Return None if no matching domain found

    # Email sending function
    def send_email(self):
        try:
            smtp_server, smtp_port = self.get_smtp_details(self.sender_email)
            if not smtp_server:
                return "Unsupported email provider"

            # Setup MIME
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = self.subject

            # Attach the body with the msg instance
            msg.attach(MIMEText(self.body, 'plain'))

            # Attach file if provided
            if self.attachment is not None:
                mimeBase = MIMEBase('application', 'octet-stream')
                mimeBase.set_payload(self.attachment.getvalue())
                encoders.encode_base64(mimeBase)
                mimeBase.add_header('Content-Disposition', f'attachment; filename={self.attachment.name}')
                msg.attach(mimeBase)

            # Create SMTP session for sending the email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()  # Start TLS for security
            server.login(self.sender_email, self.sender_password)  # Login with sender's email and password
            text = msg.as_string()
            server.sendmail(self.sender_email, self.recipient_email, text)  # Send the email
            server.quit()  # Quit the session

            return True
        except Exception as e:
            return str(e)

    # Email validation
    def validate_email_address(self, email):
        try:
            validate_email(email)
            return True
        except EmailNotValidError as e:
            st.error(f"Invalid email address: {str(e)}")
            return False
    
    # Streamlit form to collect input
    def display_form(self):
        st.title("Send Email")
        st.write("This app allows you to send an email with an optional attachment.")

        # Input fields
        self.sender_email = st.text_input("Your Email")
        self.sender_password = st.text_input("Your Email Password (will not be saved)", type="password")
        self.recipient_email = st.text_input("Recipient Email")
        self.subject = st.text_input("Subject")
        self.body = st.text_area("Email Body", height=200)
        self.attachment = st.file_uploader("Attach a file (Optional)", type=["pdf", "docx", "xlsx", "png", "jpg", "csv"])

        # Gmail-specific instructions for app-specific passwords
        if "gmail.com" in self.sender_email:
            st.warning("Gmail users with 2-Step Verification enabled must use an app-specific password.")
            st.info("Visit https://myaccount.google.com/apppasswords to generate one.")

        # Button to send email
        if st.button("Send Email"):
            # Validate inputs
            if not self.sender_email or not self.sender_password or not self.recipient_email:
                st.error("Please fill in all the required fields.")
            elif not self.validate_email_address(self.sender_email) or not self.validate_email_address(self.recipient_email):
                st.error("Please enter valid email addresses.")
            else:
                with st.spinner("Sending email..."):
                    result = self.send_email()

                if result is True:
                    st.success("Email sent successfully!")
                else:
                    st.error(f"Failed to send email. Error: {result}")


# Initialize and run the app
if __name__ == "__main__":
    email_app = EmailApp()
    email_app.display_form()