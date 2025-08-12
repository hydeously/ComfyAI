import json
import sys
import os
import logging
from llama_cpp import Llama
from contextlib import contextmanager

# Tokenizer-only llama instance for counting tokens, minimal RAM use
_tokenizer_llama = None

@contextmanager
def suppress_stderr():
    """
    Context manager to suppress both stdout and stderr temporarily.
    """
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = devnull
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

def _init_tokenizer(model_path, context_length):
    """
    Initializes a tokenizer-only Llama instance (vocab_only=True).
    """
    global _tokenizer_llama
    if _tokenizer_llama is None:
        with suppress_stderr():
            _tokenizer_llama = Llama(model_path=model_path, n_ctx=context_length, vocab_only=True)

def load_config(config_path="config.json"):
    """
    Loads JSON config file and returns dictionary.
    """
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

def format_prompt(template: str, system_prompt: str, chat_history: str, user_input: str) -> str:
    """
    Formats prompt string from template with system prompt, chat history, and user input.
    """
    return template.format(system_prompt=system_prompt, chat_history=chat_history, user_input=user_input)

def count_tokens(text: str) -> int:
    """
    Returns number of tokens in text using the tokenizer llama instance.
    """
    if _tokenizer_llama is None:
        raise RuntimeError("Tokenizer not initialized. Call init_tokenizer_for_utils first.")
    return len(_tokenizer_llama.tokenize(text.encode("utf-8")))

def concat_chat_history(
    chat_history: list,
    max_tokens: int,
    system_prompt: str,
    reserve_tokens: int = 256,
    summarizer=None,
    compress_fraction: float = 0.3
) -> str:
    """
    Concatenates chat history messages into a single string to fit within max_tokens - reserve_tokens.
    Compresses oldest messages with summarizer if available, then drops oldest messages if still over budget.

    Logs compression and dropping events in debug.
    """
    budget = max_tokens - reserve_tokens
    total_tokens = count_tokens(system_prompt)

    kept_messages = list(chat_history)
    all_tokens = total_tokens + sum(count_tokens(msg) for msg in kept_messages)

    compressed_count = 0
    dropped_count = 0

    # Compress oldest messages fraction if over budget and summarizer exists
    if all_tokens > budget and summarizer is not None and len(kept_messages) > 3:
        compress_count = max(1, int(len(kept_messages) * compress_fraction))
        oldest_chunk = kept_messages[:compress_count]
        summary_text = summarizer(oldest_chunk)
        kept_messages = [summary_text] + kept_messages[compress_count:]
        compressed_count = compress_count
        all_tokens = total_tokens + sum(count_tokens(msg) for msg in kept_messages)

    # Drop oldest messages until fits budget
    while kept_messages and all_tokens > budget:
        kept_messages.pop(0)
        dropped_count += 1
        all_tokens = total_tokens + sum(count_tokens(msg) for msg in kept_messages)

    # Debug logs
    if compressed_count > 0:
        logging.debug(f"[concat_chat_history] Compressed {compressed_count} messages into summary.")
    if dropped_count > 0:
        logging.debug(f"[concat_chat_history] Dropped {dropped_count} oldest messages to fit token budget.")
    if compressed_count == 0 and dropped_count == 0:
        logging.debug("[concat_chat_history] No messages compressed or dropped.")

    return "\n\n".join(kept_messages)

def ensure_dir_exists(path):
    """
    Ensures a directory exists, creating it if necessary.
    """
    if not os.path.exists(path):
        os.makedirs(path)

def init_tokenizer_for_utils(model_path, context_length):
    """
    Public function to initialize tokenizer instance for utils.
    """
    _init_tokenizer(model_path, context_length)