"""
Gradio UI for the conversational AI application.
"""

import uuid
import requests
import json
import gradio as gr
import time

# Backend API URL
API_URL = "http://localhost:8000/api"


def get_session_id():
    """Generate a unique session ID."""
    return str(uuid.uuid4())


def fetch_available_models():
    """Fetch available models from the API."""
    try:
        response = requests.get(f"{API_URL}/models")
        data = response.json()
        return data["providers"], data["models"]
    except Exception as e:
        print(f"Error fetching models: {e}")
        return [], {}


def configure_model(session_id, provider, model_name, api_key):
    """Configure the model for the session."""
    try:
        response = requests.post(
            f"{API_URL}/configure",
            json={
                "session_id": session_id,
                "provider": provider,
                "model_name": model_name,
                "api_key": api_key,
            },
        )
        if response.status_code == 200:
            return response.json()["message"]
        else:
            return f"Error: {response.json()['detail']}"
    except Exception as e:
        return f"Error configuring model: {e}"


def chat(session_id, message, chat_history):
    """Send a message to the API and get a response."""
    if not session_id:
        return "", [chat_history + [(message, "Please configure a model first.")]]

    # Add user message to chat history
    chat_history = chat_history + [(message, "")]

    try:
        # Send request to API (non-streaming)
        response = requests.post(
            f"{API_URL}/chat", json={"session_id": session_id, "message": message}
        )

        if response.status_code == 200:
            ai_message = response.json()["response"]
        else:
            ai_message = f"Error: {response.json()['detail']}"

        # Update the last message in chat history
        chat_history[-1] = (message, ai_message)

    except Exception as e:
        chat_history[-1] = (message, f"Error: {str(e)}")

    return "", chat_history


def chat_stream(session_id, message, chat_history):
    """Send a message to the API and get a streaming response."""
    if not session_id:
        return "", [chat_history + [(message, "Please configure a model first.")]]

    # Add user message to chat history
    chat_history = chat_history + [(message, "")]
    full_response = ""

    try:
        # Send request to API (streaming)
        response = requests.post(
            f"{API_URL}/chat/stream",
            json={"session_id": session_id, "message": message},
            stream=True,
        )

        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    line = line.decode("utf-8")
                    if line.startswith("data: "):
                        content = line[6:]
                        if content == "[DONE]":
                            break
                        full_response += content
                        # Update the last message in chat history with the partial response
                        chat_history[-1] = (message, full_response)
                        yield "", chat_history
        else:
            error_message = f"Error: {response.text}"
            chat_history[-1] = (message, error_message)
            yield "", chat_history

    except Exception as e:
        chat_history[-1] = (message, f"Error: {str(e)}")
        yield "", chat_history


def reset_conversation(session_id, chat_history):
    """Reset the conversation."""
    if not session_id:
        return "Please configure a model first.", chat_history

    try:
        response = requests.post(
            f"{API_URL}/reset", json={"session_id": session_id, "message": ""}
        )
        if response.status_code == 200:
            return "Conversation reset successfully.", []
        else:
            return f"Error: {response.json()['detail']}", chat_history
    except Exception as e:
        return f"Error resetting conversation: {e}", chat_history


def update_model_dropdown(provider):
    """Update the model dropdown based on the selected provider."""
    _, models = fetch_available_models()
    if provider in models:
        return gr.Dropdown(
            choices=models[provider],
            value=models[provider][0] if models[provider] else None,
        )
    return gr.Dropdown(choices=[])


def create_ui():
    """Create the Gradio UI."""
    # Get available models
    providers, models = fetch_available_models()
    default_provider = providers[0] if providers else None
    default_models = models.get(default_provider, [])
    default_model = default_models[0] if default_models else None

    # Generate a session ID
    session_id = get_session_id()

    with gr.Blocks(title="Conversational AI") as demo:
        # Hidden session ID
        session_id_state = gr.State(session_id)

        gr.Markdown("# Conversational AI with LangChain")
        gr.Markdown(
            "Select a model provider, choose a specific model, and enter your API key to get started."
        )

        with gr.Row():
            with gr.Column(scale=1):
                # Model configuration
                with gr.Group():
                    gr.Markdown("### Model Configuration")

                    provider_dropdown = gr.Dropdown(
                        choices=providers, value=default_provider, label="Provider"
                    )

                    model_dropdown = gr.Dropdown(
                        choices=default_models, value=default_model, label="Model"
                    )

                    api_key_input = gr.Textbox(
                        type="password",
                        label="API Key",
                        placeholder="Enter your API key",
                    )

                    configure_btn = gr.Button("Configure Model")
                    config_output = gr.Textbox(label="Configuration Status")

                # Reset conversation
                reset_btn = gr.Button("Reset Conversation")
                reset_output = gr.Textbox(label="Reset Status")

            with gr.Column(scale=2):
                # Chat interface
                chatbot = gr.Chatbot(height=500, label="Conversation")
                message_input = gr.Textbox(
                    placeholder="Type your message here...", label="Message"
                )
                submit_btn = gr.Button("Send")

        # Update model dropdown when provider changes
        provider_dropdown.change(
            fn=update_model_dropdown, inputs=provider_dropdown, outputs=model_dropdown
        )

        # Configure model button
        configure_btn.click(
            fn=configure_model,
            inputs=[session_id_state, provider_dropdown, model_dropdown, api_key_input],
            outputs=config_output,
        )

        # Reset conversation button
        reset_btn.click(
            fn=reset_conversation,
            inputs=[session_id_state, chatbot],
            outputs=[reset_output, chatbot],
        )

        # Chat submission
        submit_fn = chat_stream  # Use streaming by default
        submit_btn.click(
            fn=submit_fn,
            inputs=[session_id_state, message_input, chatbot],
            outputs=[message_input, chatbot],
        )

        message_input.submit(
            fn=submit_fn,
            inputs=[session_id_state, message_input, chatbot],
            outputs=[message_input, chatbot],
        )

    return demo


if __name__ == "__main__":
    demo = create_ui()
    demo.launch(share=True)
