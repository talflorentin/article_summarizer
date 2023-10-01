from langchain.document_loaders import ArxivLoader
from langchain.chat_models import ChatOpenAI
import streamlit as st
from utils import *


def main():
    if "button1" not in st.session_state:
        st.session_state["button1"] = False

    if "button2" not in st.session_state:
        st.session_state["button2"] = False

    if "docs" not in st.session_state:
        st.session_state["docs"] = None

    if "result_string" not in st.session_state:
        st.session_state["result_string"] = None

    if "first_results" not in st.session_state:
        st.session_state["first_results"] = None

    if "llm_state" not in st.session_state:
        st.session_state["llm_state"] = None
    st.title("Article Summarizer")

    # User input for the query
    query = st.text_input("Search for Arxiv article", value="1706.03762")

    if query:
        if st.button("Search"):
            st.session_state["button1"] = True

            docs = ArxivLoader(query=query, load_max_docs=2).load()
            st.session_state["docs"] = docs

            # Display metadata of the first document
            st.write("Metadata of the first document:")
            result_string = ""
            for key, value in docs[0].metadata.items():
                result_string += f"- **{key}**: {value}\n"
            st.session_state["result_string"] = result_string
            st.write(st.session_state["result_string"])

        if st.session_state["button1"] and st.button("Summarize"):
            st.session_state["button2"] = True
            st.write(st.session_state["result_string"])

            splitter = create_text_splitter()
            split_docs = splitter.split_documents(st.session_state["docs"])
            llm = ChatOpenAI(temperature=0, openai_api_key=st.secrets["openai_key"])  # Defaults to gpt-3.5-turbo
            st.session_state["llm_state"] = llm
            map_chain = create_map_chain(llm)
            reduce_chain = create_reduce_chain(llm)
            combine_documents_chain = stuff_docs_for_reduce(reduce_chain)
            reduce_documents_chain = create_final_reduce_chain(combine_documents_chain)
            map_reduce_chain = create_map_reduce_chain(map_chain, reduce_documents_chain)
            with st.spinner("Loading..."):
                first_results = map_reduce_chain(split_docs)
                st.session_state["first_results"] = first_results

            # Display the output
            st.write("Output Text:")
            st.write(first_results['output_text'])

        if st.session_state["button2"]:
            query2 = st.text_input("Add some modifiers")
            if query2 and st.button("Summarize Again"):
                reduced_docs_arr = create_new_doc_arr_from_res(st.session_state["first_results"])
                prompt_modifiers = query2
                reduce_chain = create_reduce_chain(st.session_state["llm_state"], prompt_modifiers)
                combine_documents_chain = stuff_docs_for_reduce(reduce_chain)
                reduce_documents_chain_new = create_final_reduce_chain(combine_documents_chain)
                with st.spinner("Loading..."):
                    post_change_results = reduce_documents_chain_new(reduced_docs_arr)
                # Display the output
                st.write("New Summary:")
                st.write(post_change_results['output_text'])


if __name__ == "__main__":
    main()
