import requests
import logging
from llama_cpp import Llama

class MemoryManager:
    def __init__(self, model_path, obsidian_vault_path, inbox_folder="inbox", diary_folder="diary"):
        self.llm = Llama(
            model_path=model_path,
            n_ctx=2048,
            # Other args you need for Rocket 3B
        )
        self.vault_path = obsidian_vault_path
        self.inbox_path = f"{vault_path}/{inbox_folder}"
        self.diary_path = f"{vault_path}/{diary_folder}"
        self.rest_base_url = "http://localhost:27123"  # Default for Obsidian REST plugin
        logging.info(f"MemoryManager initialized with vault at {self.vault_path}")

    def _format_prompt(self, system_message, user_prompt):
        # ChatML template for Rocket 3B
        return (
            f"<|im_start|>system\n{system_message}<|im_end|>\n"
            f"<|im_start|>user\n{user_prompt}<|im_end|>\n"
            "<|im_start|>assistant"
        )

    def classify_need_retrieval(self, text) -> bool:
        system_msg = "Classify if this user input requires searching long-term memory for relevant info. Answer yes or no."
        prompt = self._format_prompt(system_msg, text)
        result = self.llm(prompt=prompt, max_tokens=16, stop=["<|im_end|>"])
        output = result.get("choices", [{}])[0].get("text", "").strip().lower()
        return "yes" in output

    def classify_need_save(self, text) -> bool:
        system_msg = "Decide if this text contains new or important info that should be remembered. Answer yes or no."
        prompt = self._format_prompt(system_msg, text)
        result = self.llm(prompt=prompt, max_tokens=16, stop=["<|im_end|>"])
        output = result.get("choices", [{}])[0].get("text", "").strip().lower()
        return "yes" in output

    def summarize_text(self, text) -> str:
        system_msg = "Summarize the following text in 3-5 sentences, focusing on key facts and info."
        prompt = self._format_prompt(system_msg, text)
        result = self.llm(prompt=prompt, max_tokens=256, stop=["<|im_end|>"])
        return result.get("choices", [{}])[0].get("text", "").strip()

    def _create_note(self, folder_path, filename, content):
        url = f"{self.rest_base_url}/create"
        file_path = f"{folder_path}/{filename}"
        payload = {
            "path": file_path,
            "content": content
        }
        try:
            resp = requests.post(url, json=payload)
            if resp.status_code == 200:
                logging.info(f"Created note {file_path} in Obsidian")
                return True
            else:
                logging.error(f"Failed to create note {file_path}: {resp.text}")
                return False
        except Exception as e:
            logging.error(f"Exception while creating note {file_path}: {e}")
            return False

    def save_to_inbox(self, filename, content):
        return self._create_note(self.inbox_path, filename, content)

    def save_to_diary(self, filename, content):
        return self._create_note(self.diary_path, filename, content)

    # New method to save explicit text from /memory command (summarizes first)
    def save_explicit_memory(self, text):
        summary = self.summarize_text(text)
        filename = f"memory_explicit_{int(time.time())}.md"
        return self.save_to_inbox(filename, summary)

    # New method to save last AI response from /memorylast (summarizes first)
    def save_last_response_memory(self, text):
        summary = self.summarize_text(text)
        filename = f"memory_last_response_{int(time.time())}.md"
        return self.save_to_inbox(filename, summary)