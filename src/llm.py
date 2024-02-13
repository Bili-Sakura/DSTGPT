# pylint: disable=E0611,W0611,C0103,C0303,R0903,E1101,E1102
"""
This module provides functionality for llm.
"""
import os
import asyncio
import json
from dotenv import load_dotenv
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_community.callbacks import get_openai_callback, openai_info
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.text_splitter import (
    CharacterTextSplitter,
    TextSplitter,
    RecursiveJsonSplitter,
)
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from src.config import load_config


class LLM:
    """
    This class represents the LLM (Large Language Model)
    and provides functionality for llm.
    """

    def __init__(self, corpus_filepath, base_model="gpt-3.5-turbo-0125"):
        """
        Initializes the LLM object with environment variables, document embeddings,
        and sets up the document chain for retrieval.

        Args:
            corpus_filepath (str): Path to the corpus file
            containing data to be processed and vectorized.
        """
        # Load environment variables from .env
        load_dotenv()

        # Set up your API key from OpenAI
        self.api_key = os.getenv("OPENAI_API_KEY")
        if os.getenv("OPENAI_BASE_URL") != "":
            self.base_url = os.getenv("OPENAI_BASE_URL")
        else:
            self.base_url = None
        # Initialize ChatOpenAI
        self.llm = ChatOpenAI(
            openai_api_key=self.api_key,
            base_url=self.base_url,
            model=base_model,
            temperature=0,  # default=0.7; 1 to be creative; 0 to be firm
        )

        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-ada-002",  # default
            openai_api_key=self.api_key,  # alias:api_key
            base_url=self.base_url,  # If you use proxy api key, set base_url as needed
            chunk_size=1000,  # default
        )

        self.stored_vectors = None
        self.retriever = None

        self.vecterize_corpus(corpus_filepath)

        self.documents_chain = None
        self.set_documents_chain()

        self.retrieval_chain = create_retrieval_chain(
            self.retriever, self.documents_chain
        )

    async def get_answer_async(self, question):
        """
        Retrieves the answer to the given question asynchronously.

        Args:
            question (str): The question to be answered.

        Returns:
            str: The answer to the question.
        """

        # response = await self.llm.ainvoke(question)
        # answer = response.content
        response = await self.retrieval_chain.ainvoke({"input": question})
        answer = response["answer"]
        # print(answer)
        return answer

    def vecterize_corpus(self, corpus_filepath):
        """
        Vectorizes the corpus data from the specified file.

        Args:
            corpus_filepath (str): Path to the corpus file
            containing data to be processed and vectorized.
        """
        with open(corpus_filepath, "r", encoding="utf-8") as file:
            corpus_data = json.load(file)

        database_directory = "./database"
        if os.path.exists(os.path.join(database_directory, "chroma.sqlite3")):
            self.stored_vectors = Chroma(
                persist_directory=database_directory, embedding_function=self.embeddings
            )

        else:

            # process large json file
            for i, data in enumerate(corpus_data):
                # Splitting text into 1500-character chunks with 100-character overlap
                chunk_size = 1500
                overlap = 100
                chunks = [
                    data["text"][i : i + chunk_size]
                    for i in range(0, len(data["text"]), chunk_size - overlap)
                ]
                metadata = [{k: v for k, v in data.items() if k != "text"}]

                if i == 0:
                    self.stored_vectors = Chroma.from_texts(
                        texts=chunks,
                        metadatas=metadata,
                        embedding=self.embeddings,
                        persist_directory=database_directory,
                    )
                else:
                    self.stored_vectors.add_texts(
                        texts=chunks,
                        metadatas=metadata,
                    )

                if i % 100 == 0:
                    if i == 0:
                        print("Start Process Corpus!")
                    else:
                        print(f"Processed {i} Items in Corpus!")

        self.retriever = self.stored_vectors.as_retriever()

    def set_documents_chain(self):
        """
        Sets up the chain of documents to be used for retrieving information in response to queries.
        """
        retreival_prompt = ChatPromptTemplate.from_template(
            """Answer the following question based on the provided knowledge:

        <knowledge>
        {context}
        </knowledge>
        
        Question: {input}"""
        )

        self.documents_chain = create_stuff_documents_chain(
            llm=self.llm,
            prompt=retreival_prompt,
        )

    def update_api_key(self):
        """
        Updates the API Key with new values.

        Returns:
            None
        """
        # Load environment variables from .env
        load_dotenv()

        # Set up your API key from OpenAI
        self.api_key = os.getenv("OPENAI_API_KEY")
        if os.getenv("OPENAI_BASE_URL") != "":
            self.base_url = os.getenv("OPENAI_BASE_URL")
        else:
            self.base_url = None

    def update_vectorstore(self, source_path, file_type):
        if file_type == ".txt":
            print()
        elif file_type == ".json":
            print()
        else:
            print(f"Invalid new source type{file_type}!")
