# pylint: disable=E0611,W0611,C0103,C0303,R0903,E1101,E1102
"""
This module provides functionality for llm.
"""
import os
import asyncio
import json
import markdown2
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from PyQt5.QtWidgets import QMessageBox
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
from src.config import load_config, update_config, configUpdater


class LLM:
    """
    This class represents the LLM (Large Language Model)
    and provides functionality for llm.
    """

    def __init__(self, base_model="gpt-3.5-turbo-0125"):
        """
        Initializes the LLM object with environment variables, document embeddings,
        and sets up the document chain for retrieval.

        Args:
            corpus_filepath (str): Path to the corpus file
            containing data to be processed and vectorized.
        """
        self.config = load_config()
        configUpdater.llm_configChanged.connect(self.update_llm_configs)
        # Load environment variables from .env
        load_dotenv()

        # Set up your API key from OpenAI
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL") or None
        self.base_model = self.config.get("BASE_MODEL")
        self.temperature = self.config.get("TEMPERATURE")

        # Initialize ChatOpenAI
        self.llm = ChatOpenAI(
            openai_api_key=self.api_key,
            base_url=self.base_url,
            model=self.base_model,
            temperature=self.temperature,
        )

        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-ada-002",  # default
            openai_api_key=self.api_key,  # alias:api_key
            base_url=self.base_url,  # If you use proxy api key, set base_url as needed
            chunk_size=1000,  # default
        )

        self.stored_vectors = None
        self.init_vectorstore()

        self.retriever = self.stored_vectors.as_retriever()

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

        return answer

    def vecterize_corpus(self, corpus_filepath, file_type):
        """
        Vectorizes the corpus data from the specified file.

        Args:

        """
        if file_type == ".json":
            with open(corpus_filepath, "r", encoding="utf-8") as file:
                corpus_data = json.load(file)

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

                self.stored_vectors.add_texts(
                    texts=chunks,
                    metadatas=metadata,
                )

                if i % 10 == 0:
                    if i == 0:
                        print("Start Process Json Corpus File!")
                    else:
                        print(f"Processed {i} Items in Corpus!")

        elif file_type in [".txt", ".md", ".py"]:
            with open(corpus_filepath, "r", encoding="utf-8") as file:
                corpus_data = file.read()
            if file_type == ".md":
                corpus_data = BeautifulSoup(
                    markdown2.markdown(corpus_data), "html.parser"
                ).get_text()

            corpus_length = len(corpus_data)
            print(f"Processing Text Corpus File with {corpus_length} Characters...")
            # Splitting text into 1500-character chunks with 100-character overlap
            chunk_size = 1500
            overlap = 100
            chunks = [
                corpus_data[i : i + chunk_size]
                for i in range(0, corpus_length, chunk_size - overlap)
            ]
            self.stored_vectors.add_texts(
                texts=chunks,
            )
            print(f"Successed in Adding {corpus_length} Characters into Vectorstore!")

        print("Vectorization Finished!")
        self.retriever = self.stored_vectors.as_retriever()
        update_config("KNOWLEDGE_SOURCES", corpus_filepath)
        self.llm.update_llm_configs()

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

    def update_llm_configs(self):
        """
        Updates the LLM configurations based on the environment variables and configuration file.
        """
        self.config = load_config()
        load_dotenv()

        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL") or None
        self.base_model = self.config.get("BASE_MODEL")
        self.temperature = self.config.get("TEMPERATURE")

        self.llm = ChatOpenAI(
            openai_api_key=self.api_key,
            base_url=self.base_url,
            model=self.base_model,
            temperature=self.temperature,
        )

        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-ada-002",  # default
            openai_api_key=self.api_key,  # alias:api_key
            base_url=self.base_url,  # If you use proxy api key, set base_url as needed
            chunk_size=1000,  # default
        )

        self.retriever = self.stored_vectors.as_retriever()

        self.set_documents_chain()

        self.retrieval_chain = create_retrieval_chain(
            self.retriever, self.documents_chain
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
        self.base_url = os.getenv("OPENAI_BASE_URL") or None

    def init_vectorstore(self, vectorstore_directory="database"):
        """
        Initializes the vector store with test chunks and metadata.

        Args:
            vectorstore_directory (str): The directory path for the vector store.
            Default is 'database'.

        Returns:
            None
        """

        vectorstore_filepath = os.path.join(vectorstore_directory, "chroma.sqlite3")
        if os.path.exists(vectorstore_filepath):
            self.stored_vectors = Chroma(
                embedding_function=self.embeddings,
                persist_directory=vectorstore_directory,
            )
        else:
            test_chunks = ["Initialize a Chroma Database.", "Hello World!"]

            self.stored_vectors = Chroma.from_texts(
                texts=test_chunks,
                embedding=self.embeddings,
                persist_directory=vectorstore_directory,
            )

            sample_data_filepath = self.config.get("SAMPLE_COURPUS")
            if os.path.exists(sample_data_filepath):
                print("Add Sample Data into Database.")
                self.vecterize_corpus(sample_data_filepath, ".json")

    def update_vectorstore(self, source_path, file_type):
        """
        Update the vector store with data from the specified source file.

        Args:
            source_path (str): The path to the source file.
            file_type (str): The type of the source file (e.g., .json, .txt, .py, .md).

        Returns:
            None
        """
        vectorstore_filepath = self.config.get("VECTORSTORE_FILEPATH")
        # database_directory = os.path.dirname(vectorstore_filepath)

        if not os.path.exists(vectorstore_filepath):
            QMessageBox.warning(
                None,
                "Warning",
                "No existing database file! Initialize a VectorStore first.",
            )
            return

        if file_type not in [".json", ".txt", ".py", ".md"]:
            QMessageBox.warning(
                None, "Warning", f"Invalid source file type: {file_type}!"
            )
            return

        self.vecterize_corpus(source_path, file_type)

    def calculate_cost(self, tokens):
        model_cost_per_1k_tokens = openai_info.MODEL_COST_PER_1K_TOKENS.get(
            self.config.get("BASE_MODEL")
        )
        cost = tokens * model_cost_per_1k_tokens
