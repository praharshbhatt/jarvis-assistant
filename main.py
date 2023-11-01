import os
from dotenv import load_dotenv
import streamlit as st
from jarvis.ai_model import AIModel
from jarvis.url_handler import URLHandler

is_loading = True

# Load environment variables from .env file
load_dotenv()

# Access environment variables
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Define the dictionary of model names and associated model files
model_names = {
    "TheBloke/zephyr-7B-alpha-GGUF": [
        "zephyr-7b-alpha.Q2_K.gguf",
        "zephyr-7b-alpha.Q5_K_M.gguf",
    ],
    "TheBloke/Llama-2-7b-Chat-GGUF": ["modelsllama-2-7b-chat.Q2_K.gguf"],
    "TheBloke/CodeLlama-7B-Instruct-GGUF": [
        "codellama-7b-instruct.Q8_0.gguf",
    ],
    # "meta-llama/Llama-2-7b-chat-hf": ["llama-2-7b-chat.Q2_K.gguf"],
}

# Streamlit UI components
st.set_page_config(
    page_title="JARVIS Assistant",
    page_icon=":robot_face:",
    layout="wide",
    initial_sidebar_state="auto",
)


# Left column for model selection
with st.sidebar:
    st.title('JARVIS Assistant')

    selected_model_name = st.selectbox("Model:", list(model_names.keys()))

    # Determine the available model files for the selected model
    available_model_files = model_names[selected_model_name]

    # Streamlit widget for selecting the model file
    if len(available_model_files) > 0:
        selected_model_file = st.selectbox("Model File:", available_model_files)
        # Determine the full model path (model_name + model_file)
        full_model_path = f"models/{selected_model_file}"
    else:
        selected_model_file = None
        quantization_enabled = False
        full_model_path = None

    # Check if the selected model file requires quantization (GGUF models or GGML models)
    quantization_enabled = (
        "GGUF" in selected_model_name or "GGML" in selected_model_name
    )

    # Mute button
    # should_speak = True
    should_speak = st.toggle("Speak Responses")

    # Initialize AI model
    @st.cache_resource(hash_funcs={AIModel: str}, experimental_allow_widgets=True)
    def load_model(
        selected_model_name, full_model_path, quantization_enabled, HUGGINGFACE_API_KEY
    ) -> AIModel:
        st.write("Loading model..." + selected_model_name)
        return AIModel(
            model_name=selected_model_name,
            model_path=full_model_path,
            quantization=quantization_enabled,
            api_key=HUGGINGFACE_API_KEY,
        )

    st.write("Calling the function...")
    ai_model = load_model(
        selected_model_name,
        full_model_path,
        quantization_enabled,
        HUGGINGFACE_API_KEY,
    )

     # Text input field for entering a URL
    if st.text_input("Enter a URL to train the model", key="url_input", value=""):
        url = st.session_state.url_input
        base_directory = "data/training_data"
        url_handler = URLHandler(base_directory)
        if url_handler.validate_url(url):
            result = url_handler.download_html(url)
            if result == "HTML content downloaded successfully.":
                ai_model.train(hard=True)
    is_loading = False


# The chat interface
def chat_interface():
    # Store LLM generated responses
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [
            {"role": "assistant", "content": "How may I assist you today?"}
        ]

    # Display or clear chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    def clear_chat_history():
        st.session_state.messages = [
            {"role": "assistant", "content": "How may I assist you today?"}
        ]
        ai_model.clear_memory()

    st.sidebar.button("Clear Chat History", on_click=clear_chat_history)

    # Create a chat container to display messages
    chat_container = st.container()
    chat_input = chat_container.chat_input("Your query", key="chat_input")
    if chat_input:
        prompt = chat_input
        with st.chat_message("user"):
            st.session_state.messages.append({"role": "user", "content": chat_input})
            st.write(chat_input)

    # "Continue response" button
    # continue_response_button = chat_container.button(
    #     "Continue response", key="continue_response_button"
    # )

    # if continue_response_button:
    #     chat_input = "/continue"

    # Generate a new response if last message is not from assistant
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                chat_stream = ai_model.query(prompt)
                placeholder = st.empty()
                full_response = ""
                for item in chat_stream:
                    full_response += item
                    placeholder.markdown(full_response)
                placeholder.markdown(full_response)

        # if the last user prompt was "/continue", then remove this prompt, and merge the response with the previous assistant response
        if (
            len(st.session_state.messages) > 1
            and st.session_state.messages[-1]["content"] == "/continue"
        ):
            # remove the "<|> ..." from the starting of the response
            if full_response.startswith("<|> ..."):
                full_response = full_response[7:]
            if full_response.startswith("<|>"):
                full_response = full_response[3:]
            if full_response.startswith("..."):
                full_response = full_response[3:]
            if full_response.startswith("<∣assistant∣>"):
                full_response = full_response[13:]
            
            # merge the response with the previous assistant response
            st.session_state.messages[-2]["content"] = (
                st.session_state.messages[-2]["content"] + full_response
            )
            st.session_state.messages.pop()
        else:
            message = {"role": "assistant", "content": full_response}
            st.session_state.messages.append(message)


if not is_loading:
    chat_interface()
else:
    st.spinner("Loading...")
