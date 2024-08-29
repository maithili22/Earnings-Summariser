Here's a README file formatted for GitHub:

---

# PDF Transcript Analyzer

## Overview

The PDF Transcript Analyzer is a web application built using LangChain, Gemini-PRO, and Streamlit. It allows users to upload a PDF transcript, extract and analyze key sections like opening remarks and question-answer summaries, and interact with the content through a chatbot. The application provides detailed tables summarizing speaker contributions, topic-wise summaries, and more.

## Features

- **PDF Upload and Analysis**: Upload a PDF file and extract text for detailed analysis.
  
- **Opening Remarks Summary**:
  - Displays a table summarizing the opening remarks.
  - Provides detailed summaries of each speaker’s contributions.
  - Extracts and displays key topics discussed in the opening remarks, along with concise summaries.

- **Question-Answer Summary**:
  - Displays a table summarizing the Q&A session.
  - Summarizes each speaker's questions and answers, including their company affiliation.
  - Extracts and displays topics discussed in the Q&A session with detailed summaries.

- **Chatbot Interface**:
  - Interact with the PDF content using natural language queries.
  - Receive relevant and concise answers based on the transcript content.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/maithili22/Earnings-Summariser

2. **Run the application**:
   ```bash
   streamlit run app.py
   ```

## Usage

1. **PDF Upload**: Navigate to the "Analyze PDF" section, upload your PDF transcript, and click "Submit" to analyze the file.

2. **Opening Remarks Summary**:
   - View a table summarizing the opening remarks.
   - Click "Get topics" to see the topics discussed.
   - Click "Topic wise summary" to see detailed summaries of each topic.

3. **Question-Answer Summary**:
   - View a table summarizing the Q&A session.
   - Click "Get topics" to see the topics discussed.
   - Click "Topic wise summary" to see detailed summaries of each topic.

4. **Chatbot**:
   - Enter your query in the chatbot interface to ask questions about the PDF content.
   - Receive concise and relevant answers directly from the transcript.

## Dependencies

- **PyPDF2**: For extracting text from PDF files.
- **re (Regular Expressions)**: For text processing and pattern matching.
- **LangChain**: For natural language processing and generating analyses.
- **Gemini-PRO**: To power the AI-driven chatbot interface.
- **Streamlit**: For creating the web-based user interface.
- **Pandas**: For handling and displaying tabular data.

