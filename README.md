# ComfyAI
![Build](https://img.shields.io/badge/build-experimental-orange?logoColor=979da5&labelColor=292e33)
![Docs](https://img.shields.io/badge/docs-none-red?logo=github&logoColor=979da5&labelColor=292e33)
![Tests](https://img.shields.io/badge/tests-failing-red?logo=github&logoColor=979da5&labelColor=292e33)
![Last Commit](https://img.shields.io/github/last-commit/hydeously/comfyai?logo=github&logoColor=979da5&labelColor=292e33)
![Repo Size](https://img.shields.io/github/repo-size/hydeously/comfyai?logoColor=979da5&labelColor=292e33)
![Python](https://img.shields.io/badge/Made%20with-%E2%9D%A4%20Python-red?logoColor=979da5&labelColor=292e33&link=https%3A%2F%2Fwww.python.org)
![License](https://img.shields.io/badge/license-MIT-blue?logoColor=979da5&labelColor=292e33&link=https%3A%2F%2Fopensource.org%2Flicense%2FMIT)

**ComfyAI** is a fully local, offline, and private AI chatbot project that leverages the [`llama.cpp`](https://github.com/ggml-org/llama.cpp) inference engine through the [`llama-cpp-python`](https://github.com/abetlen/llama-cpp-python) bindings. It is designed to provide a flexible and user-friendly command-line interface for interacting with large language models (LLMs).

## Features

- **Local & offline LLM inference:** Runs powerful large language models fully offline with GPU acceleration for responsive and private AI conversations.

- **Integrated Long-Term Memory:** Manages memory via a helper model that classifies, summarizes, and stores knowledge seamlessly in your Obsidian vault using the REST API. [^1]

- **Vector Semantic Search:** Employs SentenceTransformer embeddings with ChromaDB for efficient, context-aware retrieval of relevant knowledge from your entire Obsidian vault, improving AI responses.

- **Dynamic Memory Retrieval and Saving:** Automatically decides when to retrieve relevant facts or save new insights based on intelligent classification of user inputs and AI outputs.

- **Robust CLI Interface:** User-friendly terminal interface with customizable commands to control chat history, memory management, vault indexing, and help.

- **Configurable Multi-Mode Operation:** Supports chat and debug modes with detailed logging and verbose output when needed.

- **Threaded Background Tasks:** Asynchronous memory save and classification operations to keep the main conversation loop snappy.

- **Comprehensive Logging:** Logs both to console and detailed log files for further analysis, plus JSON conversation history for LoRA training purposes.

- **Manual and Auto Vault Indexing:** Vault indexing triggers automatically on startup and can be manually invoked via CLI commands.

## Setup

### Requirements
   - Python 3.10+
   - GPU with CUDA support and at least 8GB of VRAM (recommended for faster inference)
   - Obsidian with the Obsidian REST API plugin installed and running
   - Installed dependencies

1. Clone the repository and create a Python 3.10+ virtual environment.
2. Activate the virtual environment and install dependencies:
   ```bash
   pip install -r requirements.txt
3. Place your GGUF model files in the `models/` directory.
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

## ⚠️ WARNING: Experimental and Personal Use Only

> [!WARNING]
> ComfyAI is a deeply personal, highly experimental project in active development. It is designed primarily for my own exploration and development. Although this repository is public, it is not intended for general use or cloning. Please do not expect this codebase to be stable, fully functional, or ready to run by following these instructions.

### Why shouldn’t you clone or expect it to work?

- The project is in constant flux, with frequent major changes, incomplete features, and possibly broken code.
- There are minimal instructions and no guarantees on environment setup or dependencies.
- Most (if not all) components rely on local files, specific system configurations, or proprietary models that are not included.
- The code prioritizes experimentation over maintainability, robustness, or security.
- It lacks formal testing, error handling, and comprehensive documentation.

If you are looking for a reliable AI assistant or chatbot, I recommend exploring established, well-maintained projects instead.

## Disclaimer
<sub>Disclaimer of Warranty:
This software is provided "as is," without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and non-infringement. Use at your own risk.

<sub>Limitation of Liability:
In no event shall the authors or copyright holders be liable for any claim, damages, or other liability arising from, out of, or in connection with the software or its use.

<sub>No Support or Maintenance:
This project is provided for experimental purposes only. No guarantees are made regarding updates, bug fixes, or technical support.

<sub>No Endorsement:
References to any companies, products, or services do not imply endorsement by the authors.</sub>

## License
<sub>Legal Notice:<br>
This repository, including any and all of its forks and derivatives is licensed, distributed and released under the terms of the [MIT License](https://opensource.org/license/mit). The use, reproduction, modification, and distribution of this software are permitted solely in accordance with the conditions set forth by the [MIT License](https://opensource.org/license/mit). By accessing or utilizing this repository, you acknowledge and agree to abide with the full terms of the license. Unauthorized use beyond these terms is strictly prohibited.</sub>
[^1]: [obsidian-local-rest-api](https://github.com/coddingtonbear/obsidian-local-rest-api?tab=readme-ov-file)