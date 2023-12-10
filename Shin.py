import imaplib
import email
import pandas as pd
import nltk
from io import BytesIO
import fitz  # PyMuPDF
import streamlit as st # bert-extractive-summarizer
from summarizer import Summarizer as BERTSummarizer


# Download NLTK resources
nltk.download('punkt')

# Streamlit app title
st.title("Automate2PDF: Simplified Data Transfer")

# Function to extract text from PDF using PyMuPDF
def extract_text_from_pdf(pdf_bytes):
    pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page_num in range(pdf_document.page_count):
        text += pdf_document[page_num].get_text()
    return text

# Function to summarize text using BERT-based summarizer
def summarize_text_bert(text):
    summarizer = Summarizer()
    summary = summarizer(text)
    return summary

# Create input fields for the user, password, and email address
user = st.text_input("Enter your email address")
password = st.text_input("Enter your email password", type="password")
pdf_email_address = st.text_input("Enter the email address from which to extract PDFs")

# Specify the date for filtering
selected_date = st.text_input("Enter the date (YYYY-MM-DD) to filter emails")

# Convert date format for IMAP search
try:
    imap_date_format = pd.to_datetime(selected_date).strftime("%d-%b-%Y").upper()
except Exception as e:
    st.error(f"Error converting date format: {str(e)}")
    st.stop()

if st.button("Fetch and Display PDF Summaries"):
    try:
        # URL for IMAP connection
        imap_url = 'imap.gmail.com'

        # Connection with GMAIL using SSL
        with imaplib.IMAP4_SSL(imap_url) as my_mail:
            # Log in using user and password
            my_mail.login(user, password)

            # Select the Inbox to fetch messages
            my_mail.select('inbox')

            # Define the key and value for email search
            key = 'SINCE'
            value = imap_date_format  # Use the user-specified date to search
            _, data = my_mail.search(None, key, value)

            mail_id_list = data[0].split()

            info_list = []

            # Iterate through messages
            for num in mail_id_list:
                typ, data = my_mail.fetch(num, '(RFC822)')
                msg = email.message_from_bytes(data[0][1])

                for part in msg.walk():
                    if part.get_content_type() == 'application/pdf':
                        # Extract email date
                        email_date = msg["Date"]

                        # Extract text from PDF using PyMuPDF
                        pdf_bytes = part.get_payload(decode=True)
                        pdf_text = extract_text_from_pdf(pdf_bytes)

                        # Summarize the PDF content using BERT-based summarizer
                        summary = summarize_text_bert(pdf_text)

                        info = {"Summarized Content": summary, "Received Date": email_date}
                        info_list.append(info)

            # Display the summarized content
            for info in info_list:
                st.subheader(f"Received Date: {info['Received Date']}")
                st.write(info["Summarized Content"])

            # Download button
            if st.button("Download Summaries as Text File"):
                summary_text = "\n\n".join(f"Received Date: {info['Received Date']}\n{info['Summarized Content']}" for info in info_list)
                st.download_button(
                    label="Download Summaries",
                    data=summary_text,
                    key="download_summaries_txt",
                    file_name="summaries.txt",
                )

    except Exception as e:
        st.error(f"An error occurred during IMAP connection: {str(e)}")
