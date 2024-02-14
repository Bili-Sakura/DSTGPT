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
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from src.config import load_config, update_config, configUpdater


class LLM:
    """
    This class represents the Large Language Model (LLM)
    and provides functionality for language processing.
    """

    def __init__(self):
        self.load_configs_and_envs()  # Load configurations and environment variables
        configUpdater.llm_configChanged.connect(self.update_llm_configs)
        self.init_llm()  # Initialize Large Language Model (LLM)
        self.init_embeddings()  # Initialize embeddings
        self.init_vectorstore()  # Initialize vector store
        self.set_retrieval_chain()

    def load_configs_and_envs(self):
        """Load configuration files and environment variables."""
        self.config = load_config()
        load_dotenv()

        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL", None)
        self.base_model = self.config.get("BASE_MODEL")
        self.temperature = self.config.get("TEMPERATURE")
        self.prompt_template = self.config.get("PROMPT_TEMPLATE")
        self.retrieval_chain = None

    def init_llm(self):
        """Initialize LLM."""
        self.llm = ChatOpenAI(
            openai_api_key=self.api_key,
            base_url=self.base_url,
            model=self.base_model,
            temperature=self.temperature,
        )

    def init_embeddings(self):
        """Initialize embeddings."""
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-ada-002",
            openai_api_key=self.api_key,
            base_url=self.base_url,
            chunk_size=1000,
        )

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

    def set_retrieval_chain(self):
        """Set up the document chain for retrieval."""
        retrieval_prompt = ChatPromptTemplate.from_template(self.prompt_template)

        self.documents_chain = create_stuff_documents_chain(
            llm=self.llm,
            prompt=retrieval_prompt,
        )

        self.retrieval_chain = create_retrieval_chain(
            self.stored_vectors.as_retriever(), self.documents_chain
        )

    def update_llm_configs(self):
        """Update LLM configurations."""
        self.load_configs_and_envs()  # Reload configurations and environment variables
        self.init_llm()  # Reinitialize LLM
        self.init_embeddings()  # Reinitialize embeddings
        self.set_retrieval_chain()  # Reset

    async def get_answer_async(self, question, rag_status="enabled"):
        """Retrieve answer asynchronously for a given question."""
        answer = {"rag": "", "pure": ""}
        if rag_status == "enabled":
            response = await self.retrieval_chain.ainvoke({"input": question})
            answer["rag"] = response["answer"]
        elif rag_status == "disabled":
            response = await self.llm.ainvoke(question)
            answer["pure"] = response.content
        elif rag_status == "both":
            response_rag = await self.retrieval_chain.ainvoke({"input": question})
            answer["rag"] = response_rag["answer"]
            response_pure = await self.llm.ainvoke(question)
            answer["pure"] = response_pure.content
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

        elif file_type in [".txt", ".md", ".py", ".lua"]:
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
        update_config("KNOWLEDGE_SOURCES", corpus_filepath)

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

    def calculate_cost(self, dict_tokens):
        """
        Calculate the cost of using the language model based on the number of tokens in the prompt and completion.

        Args:
            dict_tokens (dict): A dictionary containing the number of tokens in the prompt and completion.

        Returns:
            float: The total cost of using the language model.
        """
        use_model_name = self.base_model
        prompt_model_name = use_model_name
        completion_model_name = prompt_model_name + "-completion"
        prompt_tokens = dict_tokens["prompt_tokens"]
        completion_tokens = dict_tokens["completion_tokens"]

        # copy from langchain_community.callbacks.openai_info.py on 2024/2/14
        MODEL_COST_PER_1K_TOKENS = {
            # GPT-3.5 input
            "gpt-3.5-turbo": 0.0015,
            "gpt-3.5-turbo-0125": 0.0005,
            "gpt-3.5-turbo-0301": 0.0015,
            "gpt-3.5-turbo-0613": 0.0015,
            "gpt-3.5-turbo-1106": 0.001,
            "gpt-3.5-turbo-instruct": 0.0015,
            "gpt-3.5-turbo-16k": 0.003,
            "gpt-3.5-turbo-16k-0613": 0.003,
            # GPT-3.5 output
            "gpt-3.5-turbo-completion": 0.002,
            "gpt-3.5-turbo-0125-completion": 0.0015,
            "gpt-3.5-turbo-0301-completion": 0.002,
            "gpt-3.5-turbo-0613-completion": 0.002,
            "gpt-3.5-turbo-1106-completion": 0.002,
            "gpt-3.5-turbo-instruct-completion": 0.002,
            "gpt-3.5-turbo-16k-completion": 0.004,
            "gpt-3.5-turbo-16k-0613-completion": 0.004,
        }
        for model, cost_per_1k_tokens in MODEL_COST_PER_1K_TOKENS.items():
            if model == prompt_model_name:
                prompt_cost = (prompt_tokens / 1000.0) * cost_per_1k_tokens
            elif model == completion_model_name:
                completion_cost = (completion_tokens / 1000.0) * cost_per_1k_tokens

        if prompt_cost == 0 and completion_cost == 0:
            raise ValueError("Model cost not found for the specified base model")

        total_cost = prompt_cost + completion_cost
        return total_cost
