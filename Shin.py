import imaplib
import email
import pandas as pd
import nltk
from io import BytesIO
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import fitz  # PyMuPDF
import streamlit as st

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

# ... (other parts of your code)

if st.button("Fetch and Display PDF Summaries"):
    try:
        # ... (other parts of your code)

        info_list = []

        # Iterate through messages
        for num in mail_id_list:
            # ... (other parts of your code)

            for part in msg.walk():
                if part.get_content_type() == 'application/pdf':
                    # ... (other parts of your code)

                    # Summarize each chapter
                    for i, chapter in enumerate(chapters):
                        # ... (other parts of your code)

                        # Summarize the chapter content
                        parser = PlaintextParser.from_string(chapter, Tokenizer('english'))
                        summarizer = LsaSummarizer()
                        summary = summarizer(parser.document, 3)  # Summarize into 3 sentences
                        summarized_text = ' '.join(str(sentence) for sentence in summary)

                        info = {"Chapter": i + 1, "Summarized Chapter Content": summarized_text, "Received Date": email_date}
                        info_list.append(info)

        # ... (other parts of your code)

    except Exception as e:
        st.error(f"An error occurred during IMAP connection: {str(e)}")

# ... (other parts of your code)
