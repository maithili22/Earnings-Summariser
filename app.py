import PyPDF2
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
import streamlit as st
import pandas as pd
from fpdf import FPDF


def extract_chunks_from_pdf(file):
    chunks = []
    reader = PyPDF2.PdfReader(file)
    for page in reader.pages:
        text = page.extract_text()
        page_chunks = re.split(r'\n\n+', text)
        chunks.extend(page_chunks)

    st.session_state.extracted_chunks = chunks
    return chunks

def analyze_transcript(full_text):
    prompt_template = PromptTemplate(
        input_variables=["transcript"],
        template="""
        From the following transcript, extract the names and roles of the management team members and the moderator. 
        Present the results in a structured format.

        Transcript:
        {transcript}

        Extract and format the information as follows:
        Company name: [Name]

        ...
        Quarter : [Name]

        ...
        Con call date : [Date]

        ...
        No of pages in transcript : [Number]

        ...
        Management Info:
        1. [Name] - [Role]
        2. [Name] - [Role]

        ...
        Moderator:
        [Name] - [Company]
        """
    )

    chain = LLMChain(llm=llm, prompt=prompt_template)
    result = chain.run(transcript=full_text)

    return result

def extract_opening_remarks(text):
    start = text.lower().find("opening remarks")
    if start == -1:
        start = 0
        st.warning("Opening remarks not found, starting from the beginning.")

    end_phrase_pattern = re.compile(r'question[-\s]+and[-\s]+answer session\. ', re.IGNORECASE)

    match = end_phrase_pattern.search(text[start:])
    if match:
        end = match.start() + start
    else:
        end = len(text)

    opening_text = text[start:end]
    question_answer_text = text[end:-1]

    return opening_text,question_answer_text

def analyze_opening_remarks(opening_remarks):
    prompt_template2 = PromptTemplate(
        input_variables=["opening_remarks"],
        template="""
        From the following transcript, extract ALL speaker names, provide a detailed summary of what they said, and count how many times each speaker spoke.
        Present the results in a pipe-separated format where each entry contains:
        - Speaker: The name of the speaker.
        - Lines: A detailed summary of what the speaker said, capturing key points and context.
        - Chunk_Counter: The number of times the speaker spoke.

        Transcript:
        {opening_remarks}

        Extract the output in the following pipe-separated format, including the header:

        Speaker | Lines | Chunk_Counter
        Speaker1 Name | Detailed summary of what Speaker1 said, including main points and context | Number
        Speaker2 Name | Detailed summary of what Speaker2 said, including main points and context | Number
        ...

        Ensure that the Lines column provides a comprehensive summary that captures the essence of each speaker's remarks.
        Do not use pipes (|) within the text of any field.
        """
    )

    chain2 = LLMChain(llm=llm, prompt=prompt_template2)
    result = chain2.run(opening_remarks=opening_remarks)

    return result

def analyze_question_answer(question_answer):
    prompt_template6 = PromptTemplate(
        input_variables=["question_answer"],
        template="""
        From the following transcript, extract ALL speaker names, provide a detailed summary of what they said,whether it was a question or answer, the company they represent and count how many times each speaker spoke.
        Present the results in a pipe-separated format where each entry contains:
        - Speaker: The name of the speaker.
        - Lines: A detailed summary of what the speaker said, capturing key points and context.
        - Chunk_Counter: The number of times the speaker spoke.
        - question_answer : Question or answer
        - company : Company name
        

        Transcript:
        {question_answer}

        Extract the output in the following pipe-separated format, including the header:

        Speaker | Lines | Chunk_Counter | question_answer | company
        Speaker1 Name | Detailed summary of what Speaker1 said, including main points and context | Number | Question or Answer , just one word | Company name
        Speaker2 Name | Detailed summary of what Speaker2 said, including main points and context | Number | Question or Answer , just one word | Company name

        Ensure that the Lines column provides a comprehensive summary that captures the essence of each speaker's remarks.
        Do not use pipes (|) within the text of any field.
        """
    )

    chain6 = LLMChain(llm=llm, prompt=prompt_template6)
    result = chain6.run(question_answer=question_answer)

    return result
def display_table(num):
    if not st.session_state.extracted_chunks:
        st.error("Please upload and analyze a PDF first.")
        return

    full_text = " ".join(st.session_state.extracted_chunks)
    if num == 1 :
        opening_remarks,_ = extract_opening_remarks(full_text)
        st.session_state.opening_remarks = opening_remarks  # Store in session state

        result = analyze_opening_remarks(opening_remarks)

    if num == 2 :
        _ , question_answers = extract_opening_remarks(full_text)
        st.session_state.question_answers = question_answers  # Store in session state

        result = analyze_question_answer(question_answers)

    try:
        lines = result.strip().split('\n')
        cleaned_lines = [line.strip() for line in lines if line.strip() and '|' in line]

        df = pd.DataFrame([line.split('|') for line in cleaned_lines])
        df.columns = df.columns.str.strip()
        df = df[1:]
        df = df.reset_index(drop=True)

        for col in df.columns:
            df[col] = df[col].str.strip()
        
        return df  # Return the dataframe instead of displaying it
    except Exception as e:
        st.error(f"An error occurred while processing the data: {str(e)}")
        st.text("Raw output:")
        st.code(result)
        return None

def get_topics_from_transcript(transcript):
    prompt_template3 = PromptTemplate(
        input_variables=["transcript"],
        template="""
        From the following transcript, extract ALL topics, and display a summary heading in one line of each topic and a one line summary.

        Transcript:
        {transcript}

        Extract the output in the following format:

        1. Topic1 heading : Summary1
        2. Topic2 heading : Summary2
        3. Topic3 heading : Summary3
        ...

        Ensure that each topic heading is a title of the topic and summary in one line
        """
    )

    chain3 = LLMChain(llm=llm, prompt=prompt_template3)
    result = chain3.run(transcript=transcript)

    return result

def get_topic_summary(topics,full_text):
    prompt_template4 = PromptTemplate(
        input_variables=["topics","full_text"],
        template="""
        For the following topics get a detailed summary for each of them. Write the summary in bullet points.

        Topics:
        {topics}

        Transcript:
        {full_text}

        Extract the output in the following format:

        - Topic1 heading: 
          - Summary1
        - Topic2 heading: 
          - Summary2
        ...

        Ensure that each topic heading is a title of the topic, and each summary is in bullet points and elaborate.
        """
    )

    chain4 = LLMChain(llm=llm, prompt=prompt_template4)
    result = chain4.run(topics=topics,full_text=full_text)

    return result

def answer_question(question,full_text):
    prompt_template5 = PromptTemplate(
        input_variables=["question","full_text"],
        template="""
        For the following pdf text generate and answer for the question asked.Keep the answer relevant and concise

        Question:
        {question}

        Text:
        {full_text}



        """
    )

    chain5 = LLMChain(llm=llm, prompt=prompt_template5)
    result = chain5.run(question=question,full_text=full_text)

    return result

def create_dataframe(result):
    try:
        lines = result.strip().split('\n')
        cleaned_lines = [line.strip() for line in lines if line.strip() and '|' in line]

        df = pd.DataFrame([line.split('|') for line in cleaned_lines])
        df.columns = df.iloc[0]
        df = df[1:]
        df = df.reset_index(drop=True)

        for col in df.columns:
            df[col] = df[col].str.strip()
        
        return df
    except Exception as e:
        st.error(f"An error occurred while processing the data: {str(e)}")
        st.text("Raw output:")
        st.code(result)
        return None
    
def generate_pdf(summary, title):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=title, ln=True, align='C')

    pdf.set_font("Arial", size=10)
    for line in summary.split('\n'):
        pdf.multi_cell(0, 10, txt=line)

    return pdf


def main():
    if 'extracted_chunks' not in st.session_state:
        st.session_state.extracted_chunks = []
    if 'opening_remarks_table' not in st.session_state:
        st.session_state.opening_remarks_table = None
    if 'opening_remarks' not in st.session_state:
        st.session_state.opening_remarks = None
    if 'topics' not in st.session_state:
        st.session_state.topics = None
    if 'topic_summary' not in st.session_state:
        st.session_state.topic_summary = None
    if 'question_answers_table' not in st.session_state:
        st.session_state.question_answers_table = None
    if 'question_answers' not in st.session_state:
        st.session_state.question_answers = None

    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Analyze PDF", "Opening Remarks Summary", "Question Answer Summary", "Chatbot"])

    if page == "Analyze PDF":
        st.title("PDF Transcript Analyzer")

        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

        if uploaded_file is not None:
            st.write("Uploaded file: ", uploaded_file.name)

            if st.button("Submit"):
                # Extract text from the PDF
                extract_chunks_from_pdf(uploaded_file)

                if not st.session_state.extracted_chunks:
                    st.error("Couldn't extract any text from the PDF.")
                    return

                full_text = " ".join(st.session_state.extracted_chunks)

                result = analyze_transcript(full_text)
                st.write("Analysis Result:")
                st.write(result)

    elif page == "Opening Remarks Summary":
        st.title("Opening Remarks Summary")

        if st.session_state.opening_remarks_table is None and st.session_state.extracted_chunks:
            full_text = " ".join(st.session_state.extracted_chunks)
            opening_remarks, _ = extract_opening_remarks(full_text)
            st.session_state.opening_remarks = opening_remarks
            result = analyze_opening_remarks(opening_remarks)
            st.session_state.opening_remarks_table = create_dataframe(result)

        if st.session_state.opening_remarks_table is not None:
            st.write(st.session_state.opening_remarks_table)

        get_topics = st.button("Get topics")
        if get_topics:
            if st.session_state.opening_remarks:
                st.session_state.topics = get_topics_from_transcript(st.session_state.opening_remarks)
                st.write(st.session_state.topics)

        if st.session_state.topics:
            topic_summary = st.button("Topic wise summary")
            if topic_summary:
                if not st.session_state.topic_summary:
                    st.session_state.topic_summary = get_topic_summary(st.session_state.topics,st.session_state.opening_remarks)
                st.write(st.session_state.topic_summary)

                pdf = generate_pdf(st.session_state.topic_summary, "Opening Remarks Topic Summary")
                st.download_button(
                    label="Download PDF",
                    data=pdf.output(dest='S').encode('latin1'),
                    file_name="opening_remarks_summary.pdf",
                    mime="application/pdf"
                )

    elif page == "Question Answer Summary":
        st.title("Question Answer Summary")

        if st.session_state.question_answers_table is None and st.session_state.extracted_chunks:
            full_text = " ".join(st.session_state.extracted_chunks)
            _, question_answers = extract_opening_remarks(full_text)
            st.session_state.question_answers = question_answers
            result = analyze_question_answer(question_answers)
            st.session_state.question_answers_table = create_dataframe(result)

        if st.session_state.question_answers_table is not None:
            st.write(st.session_state.question_answers_table)

        get_topics = st.button("Get topics")
        if get_topics:
            if st.session_state.question_answers:
                st.session_state.topics = get_topics_from_transcript(st.session_state.question_answers)
                st.write(st.session_state.topics)

        if st.session_state.topics:
            topic_summary = st.button("Topic wise summary")
            if topic_summary:
                if not st.session_state.topic_summary:
                    st.session_state.topic_summary = get_topic_summary(st.session_state.topics,st.session_state.question_answers)
                st.write(st.session_state.topic_summary)
                pdf = generate_pdf(st.session_state.topic_summary, "Question Answer Topic Summary")
                st.download_button(
                    label="Download PDF",
                    data=pdf.output(dest='S').encode('latin1'),
                    file_name="question_answer_summary.pdf",
                    mime="application/pdf"
                )

    elif page == "Chatbot":
        st.title("Chatbot")
        question = st.text_input("Ask your question")
        if question:
            answer = answer_question(question, " ".join(st.session_state.extracted_chunks))
            st.write(answer)

os.environ["GOOGLE_API_KEY"] = "YOUR-API-KEY"
llm = ChatGoogleGenerativeAI(model="gemini-pro")

if __name__ == "__main__":
    main()
