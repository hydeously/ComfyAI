import sys
import os
import time
import json
import logging
import threading
from llama_cpp import Llama
from datetime import datetime
from contextlib import contextmanager

# ==========================================================
#                        GLOBALS
# ==========================================================
loading_flag = threading.Event()                                # threading event for loading animation

color_reset = "\033[0m"                                         # reset
color_system = "\033[90m"                                       # gray
color_assistant = "\033[38;2;203;163;255m"                      # lavender

# ==========================================================
#                       PRINT HELPERS
# ==========================================================
def print_system(text):
    print(f"{color_system}{text}{color_reset}", flush=True)     # print system messages in gray

def print_assistant(text):
    print(f"{color_assistant}{text}{color_reset}", flush=True)  # print assistant messages in lavender

def print_logo():
    print_system(r"""
========================================================================
                                        ▄▄▄▄                            
  ▄▄█▀▀▀█▄█                           ▄█▀ ▀▀               ██     ▀████▀
▄██▀     ▀█                           ██▀                 ▄██▄      ██  
██▀       ▀ ▄██▀██▄▀████████▄█████▄  █████ ▀██▀   ▀██▀   ▄█▀██▄     ██  
██         ██▀   ▀██ ██    ██    ██   ██     ██   ▄█    ▄█  ▀██     ██  
██▄        ██     ██ ██    ██    ██   ██      ██ ▄█     ████████    ██  
▀██▄     ▄▀██▄   ▄██ ██    ██    ██   ██       ███     █▀      ██   ██  
  ▀▀█████▀  ▀█████▀▄████  ████  ████▄████▄     ▄█    ▄███▄   ▄████▄████▄
                                             ▄█                         
                                           ██▀                          
========================================================================
            ComfyAI v1.0 - Command Line Interface Program
              Type '/help' for commands, 'exit' to quit.
========================================================================
""")

# ==========================================================
#                CONFIG AND LOGGING HELPERS
# ==========================================================
def load_config(config_path="config.json"):
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"Config file {config_path} not found.")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"Config file {config_path} contains invalid JSON: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error loading config: {e}")
        raise

def setup_loggers(debug_mode, log_file_path):
    class ColorFormatter(logging.Formatter):
        LEVEL_COLORS = {
            logging.DEBUG: "\033[90m",                          # bright gray
            logging.INFO: "\033[34m",                           # dark blue
            logging.WARNING: "\033[33m",                        # dark yellow
            logging.ERROR: "\033[31m",                          # dark red
            logging.CRITICAL: "\033[91m",                       # bright red
        }
        RESET = "\033[0m"

        def format(self, record):
            color = self.LEVEL_COLORS.get(record.levelno, "\033[90m")
            msg = super().format(record)
            if record.exc_info:
                tb = logging.formatException(record.exc_info)
                msg = f"{msg}\n\033[31m{tb}{self.RESET}"
            return f"{color}{msg}{self.RESET}"

    logger = logging.getLogger()
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_file_path, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if debug_mode else logging.ERROR)
    console_handler.setFormatter(ColorFormatter('%(message)s'))
    logger.addHandler(console_handler)

    return logger

# ==========================================================
#                      CLI UTILITIES
# ==========================================================
@contextmanager
def suppress_stderr():
    with open(os.devnull, "w") as devnull:
        original_stderr = sys.stderr
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stderr = original_stderr

def is_command(input_str, commands):
    input_str = input_str.strip()
    if not input_str.startswith('/'):
        return False
    cmd = input_str[1:]
    return cmd.lower() in [c.lower() for c in commands]

def loading_animation():
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()
    i = 0
    while loading_flag.is_set():
        dots = "." * (i % 4)
        sys.stdout.write(f"\r\033[90mComfyAI is thinking{dots}{' ' * (3 - len(dots))}")
        sys.stdout.flush()
        time.sleep(0.5)
        i += 1
    sys.stdout.write("\r" + " " * 50 + "\r")
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()

# ==========================================================
#                      PROMPT HELPERS
# ==========================================================
def format_prompt(prompt_template: str, system_prompt: str, chat_history: str, user_input: str) -> str:
    """
    Formats prompt string from prompt_template with system prompt, chat history, and user input.
    """
    return prompt_template.format(system_prompt=system_prompt, chat_history=chat_history, user_input=user_input)

def concat_chat_history(chat_history: list) -> str:
    return "\n".join(chat_history)

# ==========================================================
#                 SUMMARIZATION HELPERS
# ==========================================================
config = load_config("config.json")
summarizer_llm = None

def get_summarizer():
    """Load the summarizer only when first needed."""
    global summarizer_llm
    if summarizer_llm is None:
        logging.debug("Loading summarizer model...")
        summarizer_llm = Llama(model_path=config["summarizer_path"], n_ctx=config["n_ctx"])
    return summarizer_llm

def summarize_chat_history(llama_cpp, chat_history: list, summary: str, token_threshold: int = 512) -> str:
    summarizer_llm = get_summarizer()
    
    if not summary:
        summary = "This is the start of a new conversation."

    if not chat_history:
        chat_tokens = 0
        summary_tokens = len(llama_cpp.tokenize(summary.encode("utf-8")))
        total_tokens = chat_tokens + summary_tokens
        return summary, chat_tokens, summary_tokens, total_tokens

    chat_text = "\n".join(chat_history)
    chat_tokens = len(llama_cpp.tokenize(chat_text.encode("utf-8")))
    
    if chat_tokens < token_threshold:
        summary_tokens = len(llama_cpp.tokenize(summary.encode("utf-8")))
        total_tokens = chat_tokens + summary_tokens
        return summary, chat_tokens, summary_tokens, total_tokens

    # Build summarization prompt
    summarizer_prompt = f"<|user|>\nSummarize the following conversation between a user and an assistant into a concise paragraph, keeping important key facts and context:\n{summary}\n{chat_text}<|end|>\n<|assistant|>"

    # Log the prompt before sending to model
    logging.debug("\nSummarizer prompt sent to model:\n%s\n", summarizer_prompt)

    # Use default config values if none provided
    response = summarizer_llm(
    prompt=summarizer_prompt,
    max_tokens=512,
    stop=["</s>", "User:"]
    )

    # Log the raw response from the model
    logging.debug("Raw summarizer response:\n%s\n", response)

    # Extract summarized text
    new_summary = response.get("choices", [{}])[0].get("text", "").strip()
    summary = new_summary if new_summary else summary

    # Clear chat history after summarization
    chat_history.clear()

    # Token counts for logging
    summary_tokens = len(llama_cpp.tokenize(summary.encode("utf-8")))
    total_tokens = chat_tokens + summary_tokens

    return summary, chat_tokens, summary_tokens, total_tokens

# ==========================================================
#               FILESYSTEM / LOGGING
# ==========================================================
def ensure_dir_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

def log_chat_message(user_msg, assistant_msg, json_log_path):
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "user": user_msg,
        "assistant": assistant_msg,
    }
    with open(json_log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")