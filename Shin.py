import imaplib
import email
import pandas as pd
import fitz  # PyMuPDF
from transformers import pipeline
import streamlit as st

# Define extract_text_from_pdf function
def extract_text_from_pdf(pdf_bytes):
    pdf_text = ""
    try:
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        for page_number in range(pdf_document.page_count):
            page = pdf_document[page_number]
            pdf_text += page.get_text()
        pdf_document.close()
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        st.stop()
    return pdf_text

# Streamlit UI
user = st.text_input("Enter your email address")
password = st.text_input("Enter your email password", type="password")
pdf_email_address = st.text_input("Enter the email address to extract PDFs from")
date_search_criteria = st.text_input("Enter the date in the format 'DD-MMM-YYYY' (e.g., 01-Jan-2023)")

# IMAP connection and email processing
imap_url = 'imap.gmail.com'
try:
    with imaplib.IMAP4_SSL(imap_url) as my_mail:
        my_mail.login(user, password)
        st.write(f"Logged in successfully as {user}")

        selected = my_mail.select('inbox')
        if selected[0] != 'OK':
            st.error("Error selecting the Inbox.")
            st.stop()

        key = 'FROM'
        value = pdf_email_address
        date_criteria = f'SINCE "{date_search_criteria}"'  # Corrected the date format

        _, data = my_mail.search(None, key, value, date_criteria)
        mail_id_list = data[0].split()

        info_list = []
        summarizer = pipeline("summarization")

        for num in mail_id_list:
            typ, data = my_mail.fetch(num, '(RFC822)')
            msg = email.message_from_bytes(data[0][1])

            book_title = msg["Subject"]
            email_date = msg["Date"]

            for part in msg.walk():
                if part.get_content_type() == 'application/pdf':
                    pdf_bytes = part.get_payload(decode=True)
                    pdf_text = extract_text_from_pdf(pdf_bytes)

                    # Increase the max_length for better summarization
                    max_length = min(len(pdf_text) * 2, 1024)  # Limit max_length to avoid very long summaries
                    summarized_content = summarizer(pdf_text, max_length=max_length)[0]['summary']

                    info = {"Book Title": book_title, "Received Date": email_date,
                            "Summarized Content": summarized_content}
                    info_list.append(info)

        for info in info_list:
            st.subheader(f"{info['Book Title']} - Received Date: {info['Received Date']}")
            st.write(info["Summarized Content"])

except imaplib.IMAP4.error as e:
    st.error(f"IMAP error occurred: {str(e)}")
except Exception as e:
    st.error(f"An error occurred: {str(e)}")
