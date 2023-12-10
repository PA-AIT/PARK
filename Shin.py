import imaplib
import email
import pandas as pd
import nltk
import fitz  # PyMuPDF
from transformers import pipeline
import streamlit as st
import base64

# Specify NLTK data path if needed
# nltk.data.path.append("/path/to/nltk_data")

# Download NLTK data
nltk.download('punkt')

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
        st.exception(e)
        st.stop()

    return pdf_text

user = st.text_input("Enter your email address")
password = st.text_input("Enter your email password", type="password")
pdf_email_address = st.text_input("Enter the email address to extract PDFs from")

selected_date = st.text_input("Enter the date (YYYY-MM-DD) to filter emails")

try:
    if pd.notna(selected_date):
        parsed_date = pd.to_datetime(selected_date)
        if not pd.isna(parsed_date):
            imap_date_format = parsed_date.strftime("%d-%b-%Y").upper()
            date_search_criteria = f'(SINCE "{imap_date_format}")'
        else:
            st.error("Please enter a valid date.")
            st.stop()
    else:
        st.error("Please enter a valid date.")
        st.stop()

    download_format = st.selectbox("Select download format", ["Text", "Word"])
    summarization_percentage = st.slider("Select summarization percentage", 1, 100, 50)
    download_button_clicked = st.button(f"Download All Summaries as {download_format} File")

    imap_url = 'imap.gmail.com'

    with imaplib.IMAP4_SSL(imap_url) as my_mail:
        my_mail.login(user, password)
        st.write(f"Logged in successfully as {user}")

        selected = my_mail.select('inbox')
        if selected[0] != 'OK':
            st.error("Error selecting the Inbox.")
            st.stop()

        key = 'FROM'
        value = pdf_email_address

        _, data = my_mail.search(None, key, value, date_search_criteria)
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

    if download_button_clicked:
        try:
            if download_format == "Text":
                all_summaries_text = "\n\n".join(
                    f"{info['Book Title']} - Received Date: {info['Received Date']}\n{info['Summarized Content']}" for
                    info in info_list)
                st.markdown(
                    f'<a href="data:file/txt;base64,{base64.b64encode(all_summaries_text.encode()).decode()}" '
                    f'download="all_summaries.txt">Download All Summaries as Text File</a>',
                    unsafe_allow_html=True
                )
        except Exception as e:
            st.error(f"Error generating download link: {str(e)}")

# Run the Streamlit app
if __name__ == '__main__':
    st.run_app()
# Some code above


