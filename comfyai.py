import sys
import os
import argparse
import logging
import json
import time
import threading
from datetime import datetime
from contextlib import contextmanager
from llama_cpp import Llama
from memory_manager import MemoryManager
from vector_db_manager import VectorDBManager
from utils import (
    load_config,
    format_prompt,
    concat_chat_history,
    ensure_dir_exists,
    init_tokenizer_for_utils,
)

# Global threading Event for animation control
loading_flag = threading.Event()

# Load helper models (paths & vault_path from config)
vault_path = "C:/Users/Hyde/Documents/Obsidian/obsidianlib"
memory_model_path = "models/rocket-3b.Q4_K_M.gguf"
embedding_model_name = "all-MiniLM-L6-v2"
memory_manager = MemoryManager(memory_model_path, vault_path)

# ANSI color codes for CMD compatibility
COLOR_RESET = "\033[0m"
COLOR_RED = "\033[31m"
COLOR_YELLOW = "\033[33m"
COLOR_GRAY = "\033[90m"
COLOR_LAVENDER = "\033[95m"  # Bright magenta as lavender approx.

def print_error(text):
    print(f"{COLOR_RED}{text}{COLOR_RESET}", flush=True)

def print_warning(text):
    print(f"{COLOR_YELLOW}{text}{COLOR_RESET}", flush=True)

def print_system(text):
    print(f"{COLOR_GRAY}{text}{COLOR_RESET}", flush=True)

def print_ai(text):
    print(f"{COLOR_LAVENDER}{text}{COLOR_RESET}", flush=True)

@contextmanager
def suppress_stderr():
    """
    Context manager to suppress only stderr output temporarily.
    """
    with open(os.devnull, "w") as devnull:
        old_stderr = sys.stderr
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stderr = old_stderr


def setup_loggers(debug_mode, log_file_path):
    """
    Set up file and console loggers.
    File logger always logs DEBUG.
    Console logger logs DEBUG if debug_mode else only errors.
    """
    logger = logging.getLogger()
    if logger.hasHandlers():
        logger.handlers.clear()  # prevent duplicate logs on re-run
    logger.setLevel(logging.DEBUG)

    # File handler - verbose logs
    fh = logging.FileHandler(log_file_path, mode='a', encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger.addHandler(fh)

    # Console handler - filtered by debug_mode
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG if debug_mode else logging.ERROR)
    ch.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(ch)

    return logger


def log_chat_message(user_msg, assistant_msg, json_log_path):
    """
    Append a chat entry to the conversation JSON log.
    """
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "user": user_msg,
        "assistant": assistant_msg,
    }
    with open(json_log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def summarizer_fn(llama, messages):
    """
    Summarizes a list of chat messages using the llama model.
    Returns a short text summary of key facts.
    """
    if not messages:
        return ""
    text_block = "\n\n".join(messages)
    prompt = f"Summarize the following conversation in 3-5 sentences, keeping key facts:\n\n{text_block}\n\nSummary:"
    with suppress_stderr():
        result = llama(prompt=prompt, max_tokens=128, stop=["\n"])
    return "Summary: " + result.get('choices', [{}])[0].get('text', '').strip()


def loading_animation():
    """
    Displays an animated "ComfyAI is thinking..." message with dots.
    Hides cursor during animation and clears line on stop.
    """
    # Hide cursor
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()
    i = 0
    while loading_flag.is_set():
        dots = "." * (i % 4)
        sys.stdout.write(f"\r\033[90mComfyAI is thinking{dots}{' ' * (3 - len(dots))}")
        sys.stdout.flush()
        time.sleep(0.5)
        i += 1
    # Clear line and show cursor again
    sys.stdout.write("\r" + " " * 50 + "\r")
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()


def is_command(input_str, commands):
    """
    Returns True if input_str is a command starting with '/' and matches commands list.
    """
    input_str = input_str.strip()
    if not input_str.startswith('/'):
        return False
    cmd = input_str[1:]
    return cmd.lower() in [c.lower() for c in commands]


def main():
    """
    Main CLI loop: parses arguments, loads config and model, handles user input,
    shows loading animation while model generates response, logs and prints output.
    """
    config = load_config()
    auto_index = config.get("auto_index_on_startup", True)
    vector_db_manager = VectorDBManager(vault_path, auto_index=auto_index)

    parser = argparse.ArgumentParser(description="ComfyAI CLI")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--chat", action="store_true", help="Run in chat mode (default)")
    group.add_argument("--debug", action="store_true", help="Run in debug mode")
    args = parser.parse_args()

    # Default to chat mode if neither specified
    if not args.chat and not args.debug:
        args.chat = True

    config = load_config()
    ensure_dir_exists("logs")

    debug_mode = args.debug
    log_file_path = config["logging"].get("log_file", "logs/comfyai_debug.log")
    json_log_path = config["logging"].get("log_json", "logs/comfyai_conversation.json")

    logger = setup_loggers(debug_mode, log_file_path)

    mode_str = "debug" if debug_mode else "chat"
    logging.debug("Starting ComfyAI in %s mode", mode_str)
    model_path = config["model_path"]
    context_length = config["context_length"]

    # Initialize tokenizer for utils (count_tokens, concat_chat_history)
    init_tokenizer_for_utils(model_path, context_length)

    if debug_mode:
        llama = Llama(
            model_path=model_path,
            n_ctx=context_length,
            n_gpu_layers=config.get("n_gpu_layers", 30),
        )
    else:
        with suppress_stderr():
            llama = Llama(
                model_path=model_path,
                n_ctx=context_length,
                n_gpu_layers=config.get("n_gpu_layers", 30),
            )

    print_system(f"ComfyAI started in {mode_str} mode. Type 'exit' or 'quit' to stop.\n")

    chat_history = []
    system_prompt = config["system_prompt"]
    llama_template = config["prompt_templates"]["llama_cpp"]
    commands = ['clear', 'restart', 'help', 'exit', 'memory', 'memorylast', 'reindex']

    global loading_flag

    while True:
        try:
            user_input = input("User: ").strip()
            if user_input.lower() in ("exit", "quit"):
                print_system("Goodbye!")
                break

            # Handle internal commands without sending to model
            if is_command(user_input, commands):
                cmd = user_input[1:].lower()
                if cmd == 'clear':
                    chat_history.clear()
                    print_system("[System] Chat history cleared.\n")
                elif cmd == 'restart':
                    chat_history.clear()
                    print_system("[System] Session restarted.\n")
                elif cmd == 'help':
                    print_system(
                        "Available commands:\n"
                        "/clear   - Clear chat history\n"
                        "/restart - Restart AI session\n"
                        "/help    - Show this help message\n"
                        "/exit    - Quit the program"
                    )
                elif cmd == 'memory':
                    text_to_save = user_input[len('/memory'):].strip()
                    if text_to_save:
                        saved = memory_manager.save_explicit_memory(text_to_save)
                        if saved:
                            print_system("[System] Text summarized and saved to memory inbox.\n")
                        else:
                            print_error("[Error] Failed to save text to memory.\n")
                    else:
                        print_warning("[Warning] No text provided to save.\n")
                elif cmd == 'memorylast':
                    last_ai_msgs = [msg for msg in reversed(chat_history) if msg.startswith("Assistant:")]
                    if last_ai_msgs:
                        last_response = last_ai_msgs[0][len("Assistant:"):].strip()
                        saved = memory_manager.save_last_response_memory(last_response)
                        if saved:
                            print_system("[System] Last AI response summarized and saved to memory inbox.\n")
                        else:
                            print_error("[Error] Failed to save last AI response to memory.\n")
                    else:
                        print_warning("[Warning] No AI response found to save.\n")
                elif cmd == 'reindex':
                    print_system("[System] Re-indexing Obsidian vault, please wait...")
                    try:
                        vector_db_manager.index_vault()
                        print_system("[System] Re-indexing completed.")
                        logging.debug("[Command] Vault re-index triggered manually.")
                    except Exception as e:
                        print_error(f"[System] Re-indexing failed: {e}")
                elif cmd == 'exit':
                    print_system("Goodbye!")
                    sys.exit(0)  # Immediate exit
                continue  # Skip sending to model

            chat_history.append(f"User: {user_input}")

            # Determine if retrieval is needed
            need_retrieval = memory_manager.classify_need_retrieval(user_input)
            retrieved_chunks = []

            if need_retrieval:
                retrieved_chunks = vector_db_manager.query(user_input, top_k=5)

            # Prepend retrieved chunks to chat history
            if retrieved_chunks:
                retrieved_text = "\n\n".join(retrieved_chunks)
                chat_history.append(f"[Retrieved knowledge]:\n{retrieved_text}")


            chat_text = concat_chat_history(
                chat_history,
                system_prompt=system_prompt,
                max_tokens=context_length,
                summarizer=lambda msgs: summarizer_fn(llama, msgs)
            )

            prompt = format_prompt(
                llama_template,
                system_prompt=system_prompt,
                chat_history=chat_text,
                user_input=user_input
            )

            logging.debug("Prompt to model:\n%s\n", prompt)

            # Start animation thread
            loading_flag.set()
            anim_thread = threading.Thread(target=loading_animation)
            anim_thread.start()

            if debug_mode:
                response = llama(prompt=prompt, max_tokens=256, stop=["[/INST]"])
            else:
                with suppress_stderr():
                    response = llama(prompt=prompt, max_tokens=256, stop=["[/INST]"])

            # Stop animation thread
            loading_flag.clear()
            anim_thread.join()

            answer = response.get('choices', [{}])[0].get('text', '').strip()

            chat_history.append(f"Assistant: {answer}")

            logging.debug("Model response:\n%s\n", answer)

            # Async save check (can be threaded or immediate)
            def async_save_check(text):
                if memory_manager.classify_need_save(text):
                    summary = memory_manager.summarize_text(text)
                    filename = f"memory_{int(time.time())}.md"
                    memory_manager.save_to_inbox(filename, summary)

            import threading
            threading.Thread(target=async_save_check, args=(answer,)).start()


            # Output depending on mode
            if debug_mode:
                print(f"User (prompt):\n{prompt}\n")
                print_ai(f"ComfyAI: {answer}\n")
            else:
                print_ai(f"ComfyAI: {answer}\n")
                # Log for future LoRA training
                log_chat_message(user_input, answer, json_log_path)

        except KeyboardInterrupt:
            print_system("\nInterrupted. Goodbye!")
            break
        except Exception as e:
            logging.exception("Unhandled exception occurred")
            print_error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()