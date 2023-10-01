from langchain.document_loaders import ArxivLoader
from langchain.chat_models import ChatOpenAI
import streamlit as st
from utils import *

# Quantum something - 2309.00021
# Attention is all you need - 1706.03762
user_input = input("Enter Arxiv Article to Query:")
docs = ArxivLoader(query=user_input, load_max_docs=2).load()
splitter = create_text_splitter()
split_docs = splitter.split_documents(docs)

for key, value in docs[0].metadata.items():
    print(f"- **{key}**: {value}\n")

llm = ChatOpenAI(temperature=0, openai_api_key=st.secrets["openai_key"])  # Defaults to gpt-3.5-turbo

map_chain = create_map_chain(llm)
reduce_chain = create_reduce_chain(llm)
combine_documents_chain = stuff_docs_for_reduce(reduce_chain)
reduce_documents_chain = create_final_reduce_chain(combine_documents_chain)
map_reduce_chain = create_map_reduce_chain(map_chain, reduce_documents_chain)
print("Summarizing with the power of LLMs...")
first_results = map_reduce_chain(split_docs)

print("First Summary: ")
print("\n#########################")
print(first_results['output_text'])
print("#########################\n")

reduced_docs_arr = create_new_doc_arr_from_res(first_results)

while True:
    user_input = input("Enter your modification: ")
    if user_input != "":
        prompt_modifiers = user_input
        reduce_chain = create_reduce_chain(llm, prompt_modifiers)
        combine_documents_chain = stuff_docs_for_reduce(reduce_chain)
        reduce_documents_chain_new = create_final_reduce_chain(combine_documents_chain)
        post_change_results = reduce_documents_chain_new(reduced_docs_arr)
        print("New Summary:")
        print(post_change_results['output_text'])
