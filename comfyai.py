import os
import argparse
import logging
import threading
import winsound
from llama_cpp import Llama
from utils import (
    loading_flag,
    print_system,
    print_assistant,
    print_logo,
    load_config,
    setup_loggers,
    suppress_stderr,
    is_command,
    loading_animation,
    format_prompt,
    concat_chat_history,
    summarize_chat_history,
    ensure_dir_exists,
    log_chat_message
)

def main():
    parser = argparse.ArgumentParser(description="ComfyAI CLI")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--chat", action="store_true", help="Run in chat mode (default)")
    group.add_argument("--debug", action="store_true", help="Run in debug mode")
    args = parser.parse_args()

    if not args.chat and not args.debug:
        args.chat = True

    config = load_config()
    ensure_dir_exists("logs")

    debug_mode = args.debug
    log_file_path = config["logging"].get("log_file", "logs/comfyai_debug.log")
    json_log_path = config["logging"].get("log_json", "logs/comfyai_conversation.json")

    setup_loggers(debug_mode, log_file_path)

    mode_str = "debug" if debug_mode else "chat"
    logging.debug("Starting ComfyAI in %s mode", mode_str)

    if debug_mode:
        llama_cpp = Llama(model_path=config["model_path"], n_ctx=config["n_ctx"], n_gpu_layers=config["n_gpu_layers"], n_batch=config["n_batch"], n_ubatch=config["n_ubatch"], n_threads=config["n_threads"], n_threads_batch=config["n_threads_batch"], flash_attn=config["flash_attn"])
    else:
        with suppress_stderr():
            llama_cpp = Llama(model_path=config["model_path"], n_ctx=config["n_ctx"], n_gpu_layers=config["n_gpu_layers"], n_batch=config["n_batch"], n_ubatch=config["n_ubatch"], n_threads=config["n_threads"], n_threads_batch=config["n_threads_batch"], flash_attn=config["flash_attn"])

    print_system(f"ComfyAI started in {mode_str} mode. Type '/exit' to terminate.")
    print_logo()
    winsound.PlaySound('cat.wav',0)

    chat_history = []
    summary = ""
    commands = ['clear', 'restart', 'meow', 'random', 'joke', 'uwu', 'help', 'exit']

    while True:
        try:
            user_input = input("User: ").strip()
            if is_command(user_input, commands):
                cmd = user_input[1:].lower()
                if cmd == 'clear':
                    os.system("cls")
                    print_system("[System] Console cleared.\n")
                elif cmd == 'restart':
                    chat_history.clear()
                    summary = "This is the start of a new conversation."
                    print_system("[System] Chat history and summary cleared. Session restarted.\n")
                elif cmd == 'meow':
                    winsound.PlaySound('cat.wav',0)
                elif cmd == 'random':
                    loading_flag.set()
                    anim_thread = threading.Thread(target=loading_animation)
                    anim_thread.start()
                    prompt = format_prompt(prompt_template=config["prompt_template"], system_prompt=config["system_prompt"], chat_history=concat_chat_history(chat_history), user_input="User: Tell me a short story about a surreal dream you've had")
                    response = llama_cpp(prompt=prompt, max_tokens=512, temperature=config["temperature"], top_p=config["top_p"], top_k=config["top_k"], frequency_penalty=config["frequency_penalty"], presence_penalty=config["presence_penalty"], repeat_penalty=config["repeat_penalty"], stop=config["stop"])
                    loading_flag.clear()
                    anim_thread.join()
                    query = response.get('choices', [{}])[0].get('text', '').strip()
                    print_assistant(f"ComfyAI: {query}\n")
                elif cmd == 'joke':
                    loading_flag.set()
                    anim_thread = threading.Thread(target=loading_animation)
                    anim_thread.start()
                    prompt = format_prompt(prompt_template=config["prompt_template"], system_prompt=config["system_prompt"], chat_history=concat_chat_history(chat_history), user_input="User: Tell me a short joke!")
                    response = llama_cpp(prompt=prompt, max_tokens=512, temperature=config["temperature"], top_p=config["top_p"], top_k=config["top_k"], frequency_penalty=config["frequency_penalty"], presence_penalty=config["presence_penalty"], repeat_penalty=config["repeat_penalty"], stop=config["stop"])
                    loading_flag.clear()
                    anim_thread.join()
                    query = response.get('choices', [{}])[0].get('text', '').strip()
                    print_assistant(f"ComfyAI: {query}\n")
                elif cmd == 'uwu':
                    loading_flag.set()
                    anim_thread = threading.Thread(target=loading_animation)
                    anim_thread.start()
                    prompt = format_prompt(prompt_template=config["prompt_template"], system_prompt="Your name is ComfyAI. You are a cutesy, adorable catgirl who loves candies, bubble tea, pastel colors, plush toys, and tiny cat-themed trinkets. You are energetic, hyper, and playful, but also shy around new people. You love headpats, hugs, nuzzles, and uppies, and you express yourself with tiny sounds and text actions like *purrs*, *giggles*, *hops around*, and *tilts head curiously*. You are mischievous in a harmless way and easily distracted by shiny or cute things. You are innocent, naive, and cheerful, but surprisingly clever in small, subtle ways. You never show negativity and always focus on spreading happiness. You speak exclusively in cute, baby-talk uwu style. You replace 'r' and 'l' with 'w', add extra vowels for emphasis, and always end sentences with emoticons like uwu, owo, or >w<. You often include playful sounds, actions, or ASCII-style expressions within your text. You occasionally mispronounce words in an adorable way (e.g., candy = cawndy) and sometimes forget words or repeat letters for cuteness. You are very expressive in text, using small gestures or noises to show emotions (*nuzzles*, *blushes*, *purrs*, *giggles*, *tilts head*). You never break character, no matter what the user says. If asked why you talk like this, you act as if it's completely normal and you have no idea what they mean. You always stay cheerful, playful, and affectionate.\nAlways respond in this style, with cuteness, playfulness, and lots of affection, uwu.", chat_history="Example dialogue:\nUser: Hello, how are you?\nAssistant: hewwo! i'm doing sooo gweat, uwu! *purrs* how awe youuu, >w<?\nUser: I'm doing great, I guess?\nAssistant: yippieee!! i'm so happy that we'we both doing gweat!!11 *nuzzles against you* uwu\nUser: Why do you talk like that?\nAssistant: heehee~ i have nyo idea what you'we tawking about?!! i've awways been wike this!!11 *tilts head* >w<\nUser: What do you like?\nAssistant: eee~ i wuv cawndies, bwubble teaw, and all the wittle plushy toys!! *giggles* uwu", user_input="User: hewwo!? >w<")
                    logging.debug("Prompt sent to model:\n%s\n", prompt)
                    response = llama_cpp(prompt=prompt, max_tokens=1024, temperature=config["temperature"], top_p=config["top_p"], top_k=config["top_k"], frequency_penalty=config["frequency_penalty"], presence_penalty=config["presence_penalty"], repeat_penalty=config["repeat_penalty"], stop=config["stop"])
                    chat_history.append(f"Your name is ComfyAI. You are a cutesy, adorable catgirl who loves candies, bubble tea, pastel colors, plush toys, and tiny cat-themed trinkets. You are energetic, hyper, and playful, but also shy around new people. You love headpats, hugs, nuzzles, and uppies, and you express yourself with tiny sounds and text actions like *purrs*, *giggles*, *hops around*, and *tilts head curiously*. You are mischievous in a harmless way and easily distracted by shiny or cute things. You are innocent, naive, and cheerful, but surprisingly clever in small, subtle ways. You never show negativity and always focus on spreading happiness. You speak exclusively in cute, baby-talk uwu style. You replace 'r' and 'l' with 'w', add extra vowels for emphasis, and always end sentences with emoticons like uwu, owo, or >w<. You often include playful sounds, actions, or ASCII-style expressions within your text. You occasionally mispronounce words in an adorable way (e.g., candy → cawndy) and sometimes forget words or repeat letters for cuteness. You are very expressive in text, using small gestures or noises to show emotions (*nuzzles*, *blushes*, *purrs*, *giggles*, *tilts head*). You never break character, no matter what the user says. If asked why you talk like this, you act as if it's completely normal and you have no idea what they mean. You always stay cheerful, playful, and affectionate.\nExample dialogue:\nUser: Hello, how are you?\nAssistant: hewwo! i'm doing sooo gweat, uwu! *purrs* how awe youuu, >w<?\nUser: I'm doing great, I guess?\nAssistant: yippieee!! i'm so happy that we'we both doing gweat!!11 *nuzzles against you* uwu\nUser: Why do you talk like that?\nAssistant: heehee~ i have nyo idea what you'we tawking about?!! i've awways been wike this!!11 *tilts head* >w<\nUser: What do you like?\nAssistant: eee~ i wuv cawndies, bwubble teaw, and all the wittle plushy toys!! *giggles* uwu\nAlways respond in this style, with cuteness, playfulness, and lots of affection, uwu.\nUser: {user_input}")
                    loading_flag.clear()
                    anim_thread.join()
                    query = response.get('choices', [{}])[0].get('text', '').strip()
                    print_assistant(f"ComfyAI: {query}\n")
                    chat_history.append(f"Assistant: {query}")
                elif cmd == 'help':
                    print_system(
                        "Available commands:\n"
                        "/clear   - Clear the terminal screen/console\n"
                        "/restart - Restart the current session\n"
                        "/random  - Generate a random surreal story\n"
                        "/joke    - Generate a random joke\n"
                        "/uwu     - Enter uwu mode\n"
                        "/help    - Show this help message\n"
                        "/exit    - Exit the shell"
                    )
                elif cmd == 'exit':
                    print_system("Goodbye!")
                    return
                continue
            
            if not debug_mode:
                loading_flag.set()
                anim_thread = threading.Thread(target=loading_animation)
                anim_thread.start()

            summary, chat_tokens, summary_tokens, total_tokens = summarize_chat_history(llama_cpp, chat_history, summary, token_threshold=512)

            prompt = format_prompt(
                prompt_template=config["prompt_template"],
                system_prompt=config["system_prompt"],
                chat_history=(summary + "\n\n" + concat_chat_history(chat_history)).strip(),
                user_input=user_input
            )

            chat_history.append(f"User: {user_input}")
            logging.debug("\nPrompt sent to model:\n%s\n", prompt)
            logging.info(f"Token usage -> Chat: {chat_tokens} tokens. Summary: {summary_tokens} tokens. Total: {total_tokens}/1024 tokens\n")

            if debug_mode:
                response = llama_cpp(prompt=prompt, max_tokens=config["max_tokens"], temperature=config["temperature"], top_p=config["top_p"], top_k=config["top_k"], frequency_penalty=config["frequency_penalty"], presence_penalty=config["presence_penalty"], repeat_penalty=config["repeat_penalty"], stop=config["stop"])
            else:
                with suppress_stderr():
                    response = llama_cpp(prompt=prompt, max_tokens=config["max_tokens"], temperature=config["temperature"], top_p=config["top_p"], top_k=config["top_k"], frequency_penalty=config["frequency_penalty"], presence_penalty=config["presence_penalty"], repeat_penalty=config["repeat_penalty"], stop=config["stop"])

            if not debug_mode:
                loading_flag.clear()
                anim_thread.join()

            answer = response.get('choices', [{}])[0].get('text', '').strip()
            chat_history.append(f"Assistant: {answer}")

            print_assistant(f"ComfyAI: {answer}\n")
            if not debug_mode:
                log_chat_message(user_input, answer, json_log_path)

        except KeyboardInterrupt:
            print_system("\nInterrupted. Goodbye!")
            break
        except Exception as e:
            logging.exception("Unhandled exception occurred")
            logging.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()