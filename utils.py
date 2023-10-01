from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import ReduceDocumentsChain, MapReduceDocumentsChain
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.docstore.document import Document


def create_new_doc_arr_from_res(results):
    new_arr = []
    for step in results['intermediate_steps']:
        new_arr.append(Document(page_content=step))
    return new_arr


def create_text_splitter():
    splitter = RecursiveCharacterTextSplitter(chunk_size=7000, chunk_overlap=300)
    return splitter


def create_map_chain(llm):
    map_template = """The following is a set of documents
  {docs}
  Based on this list of docs, please identify the main themes
  Helpful Answer:"""
    map_prompt = PromptTemplate.from_template(map_template)
    map_chain = LLMChain(llm=llm, prompt=map_prompt)
    return map_chain


def create_reduce_chain(llm,prompt_modifiers=""):
    reduce_template = f"""The following is set of summaries:
  {"{doc_summaries}"}
  Take these and distill it into a final, consolidated summary of the main themes.
  f{prompt_modifiers}
  Helpful Answer:"""
    reduce_prompt = PromptTemplate.from_template(reduce_template)
    reduce_chain = LLMChain(llm=llm, prompt=reduce_prompt)
    return reduce_chain


def stuff_docs_for_reduce(reduce_chain):
    # Takes a list of documents, combines them into a single string, and passes this to an LLMChain
    combine_documents_chain = StuffDocumentsChain(llm_chain=reduce_chain,
                                                  document_variable_name="doc_summaries")
    return combine_documents_chain


def create_final_reduce_chain(combine_documents_chain):
    # Combines and iteratively reduces the mapped documents
    reduce_documents_chain = ReduceDocumentsChain(
        combine_documents_chain=combine_documents_chain,  # This is final chain that is called.
        collapse_documents_chain=combine_documents_chain,  # If documents exceed context for `StuffDocumentsChain`
        token_max=2000,  # The maximum number of tokens to group documents into.
    )
    return reduce_documents_chain


def create_map_reduce_chain(map_chain, reduce_documents_chain):
    map_reduce_chain = MapReduceDocumentsChain(
        llm_chain=map_chain,  # Map chain
        reduce_documents_chain=reduce_documents_chain,  # Reduce chain
        document_variable_name="docs",  # The variable name in the llm_chain to put the documents in
        return_intermediate_steps=True,  # Return the results of the map steps in the output
    )
    return map_reduce_chain
