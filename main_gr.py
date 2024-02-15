# pylint: disable=E0611,C0103,C0303
"""
A Gradio interface for a chatbot using the LLM model from 'src.llm' module.
This version updates the user-defined settings by setting the range for 'Base Model Temperature' to 0-1,
and replacing 'Prompt Template' with a 'Mode' control providing three options.
"""
import gradio as gr
from src.llm import LLM

# Initialize the LLM model
llm = LLM()
BASE_MODEL_LIST = [
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-0125",
    "gpt-3.5-turbo-0301",
    "gpt-3.5-turbo-0613",
    "gpt-3.5-turbo-1106",
    "gpt-3.5-turbo-instruct",
    "gpt-3.5-turbo-16k",
    "gpt-3.5-turbo-16k-0613",
]


def process_input(
    user_text, api_key, base_url, base_model, model_temperature, mode, avatar_user
):
    """
    Process user input along with user-defined settings and return a response.
    This function should be replaced with actual logic for processing user input using the LLM model.
    """
    # Placeholder for processing logic with LLM and user-defined settings
    return user_text  # Placeholder for actual LLM response


# Define the Gradio interface using Blocks
with gr.Blocks() as demo:
    gr.Markdown(
        "<h2 style='text-align: center; font-size: 24px;'>🔥 DST-GPT : A Large Language Model for Don't Starve & Don't Starve Together</h2>"
    )
    # Chatbox display at the top
    chatbox = gr.Textbox(
        label="Chat Window",
        lines=10,
        interactive=False,
        value="Welcome to the chatbot!",
    )

    # User input textbox
    user_input = gr.Textbox(label="Enter your question")

    # Submission button
    submit_button = gr.Button("Submit")

    # User-defined settings in two columns at the bottom
    with gr.Row():
        with gr.Column():
            api_key_input = gr.Textbox(label="API Key")
            base_url_input = gr.Textbox(label="Base URL")
            base_model_input = gr.Dropdown(
                label="Base Model", choices=BASE_MODEL_LIST
            )  # Placeholder model options
        with gr.Column():
            model_temperature_input = gr.Slider(
                label="Base Model Temperature",
                minimum=0,
                maximum=1,
                step=0.01,
                value=0.7,
            )
            mode_input = gr.Radio(
                label="Mode",
                choices=["DST-GPT only", "OpenAI GPT only", "Comparation Mode"],
                value="DST-GPT only",
            )
            avatar_user_input = gr.Textbox(label="Avatar: User")

    # Define the action to take when the submit button is clicked
    submit_button.click(
        fn=process_input,
        inputs=[
            user_input,
            api_key_input,
            base_url_input,
            base_model_input,
            model_temperature_input,
            mode_input,
            avatar_user_input,
        ],
        outputs=chatbox,
    )

# Launch the Gradio interface
demo.launch()
