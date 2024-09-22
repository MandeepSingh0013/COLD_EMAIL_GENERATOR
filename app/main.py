import streamlit as st
from langchain_community.document_loaders import WebBaseLoader

from chains import Chain
from portfolio import Portfolio
from utils import clean_text 



def create_streamlit_app(llm, portfolio,clean_text):
    # Check if 'email' exists in session state, if not initialize it
    if 'email' not in st.session_state:
        st.session_state.email = ""
    st.title("📧 Cold Mail Generator")
    
    col1, col2 = st.columns(2)
    #Column 1:LLM Selection Radip button
    with col1:
        st.subheader("Select LLM Model")
        model_choice = st.radio(
        "Select the LLM model:",
        ("LLama", "Gemma", "Mixtral"),
        index=0
    )
    with col2:
        st.subheader("Uploader Protfolio CSV")
        st.write("Please upload a CSV with the following structure:")
        st.code('''"Techstack","Links"\n"React, Node.js, MongoDB","https://example.com/react-portfolio"\n"Angular,.NET, SQL Server","https://example.com/angular-portfolio"\n...''')

        # CSV file uploader
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        if uploaded_file:
                status=portfolio.load_csv(uploaded_file)
                if status == "success":
                    st.success("CSV Uploaded and Validated Successfully!")
                else:
                    st.error("Invalid CSV format. Please make sure the file contains 'Techstack' and 'Links' columns.")
                # st.success("CSV Uploaded and Validated Successfully!") if status == "success" else st.error("Invalid CSV format. Please make sure the file contains 'Techstack' and 'Links' columns.")
    
    url_input= st.text_input("Enter a URL",value="https://jobs.nike.com/job/R-31388?from=job%20search%20funnel")
    submit_button= st.button("Submit")

    
    # Add a radio button for language selection
    selected_language = st.radio(
        "Choose the target language for translation:",
        ("English", "French", "Hindi", "German")
    )
    translate_button= st.button("Translate")



    if submit_button:
        try:

            loader = WebBaseLoader([url_input])
            data = clean_text(loader.load().pop().page_content)
            portfolio.load_portfolio()
            
            jobs = llm.extract_jobs(model_choice,data)
            for job in jobs:
                skills = job.get('skills',[])
                links = portfolio.query_links(skills)
                st.session_state.email = llm.write_mail(model_choice,job,links)
                st.code(st.session_state.email,language="markdown")
              
        except Exception as e:
            st.error(f"AN Error Occurred: {e}")

    if translate_button:
        try:
            teranslated_mail=llm.translate_text(model_choice,st.session_state.email,selected_language)
            st.subheader(f"Translated Email ({selected_language}) by ({model_choice}) model")
            st.code(teranslated_mail,language="markdown")
            
        except Exception as e:
            st.error(f"An Error Occurred:{e}")

if __name__=="__main__":
    chain=Chain()
    portfolio=Portfolio()
    st.set_page_config(layout="wide",page_title="Cold Email Generator",page_icon="📧")
    create_streamlit_app(chain,portfolio,clean_text)