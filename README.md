# ComfyAI

ComfyAI is a local AI chatbot project using llama-cpp-python as the backend, designed to provide a flexible and user-friendly command-line interface for chatting with large language models (LLMs) such as MythoMax-L2-13B-GGUF.

## Project Structure

- `venv/` - Python virtual environment with required dependencies.
- `llama_cpp_python/` - Cloned llama-cpp-python repository with CUDA support.
- `models/` - Directory to store your LLM model files.
- `comfyai.py` - Main Python script handling the CLI chat interface and interaction with the LLM.
- `utils.py` - Utility functions for prompt formatting and token counting.
- `config.json` - Configuration file for model paths and prompt templates.
- `logs/` - Directory for chat logs and debugging output.
- `scripts/` - Helper scripts such as batch files for launching the application.

## Setup Instructions

1. Clone the repository and create a Python 3.11.9 virtual environment.
2. Activate the virtual environment and install dependencies:
   ```bash
   pip install -r requirements.txt
3. Place your GGUF model files in the models/ directory.
4. Run the chat interface:
   ```bash
   Copy
   Edit
   python comfyai.py --chat

## Usage

--chat mode: Launch the chat CLI interface.

--debug mode: View detailed logs and debug information.

## Notes

Currently supports models compatible with llama-cpp-python.

CUDA acceleration requires compatible GPU and drivers.

Future updates planned to improve multi-tab support and chat history handling."# comfyai" 
"# comfyai" 
