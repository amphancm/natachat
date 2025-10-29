import requests
import logging
import time
from sqlalchemy.orm import Session
from libs.db import SessionLocal
from schemas.models import Setting

# Initialize module logger (fall back to basicConfig only if no handlers configured)
logger = logging.getLogger(__name__)
if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.DEBUG)
logger.debug("llm module initialized")

def load_setting(db: Session):
    return db.query(Setting).first()

def get_llm_response(prompt: str) -> str:
    start_time = time.perf_counter()
    logger.debug("get_llm_response called; prompt (truncated)=%s", (prompt or "")[:200])

    db = SessionLocal()
    try:
        setting = load_setting(db)
        if not setting:
            logger.error("No setting found in DB")
            return "No setting found"

        # Mask API key for logs (do not leak full key)
        api_key_masked = None
        if setting.apiKey:
            k = setting.apiKey
            api_key_masked = ("*" * max(0, len(k) - 4)) + k[-4:] if len(k) > 4 else "*" * len(k)

        logger.debug(
            "Current Setting: isLocal=%s isApi=%s domainName=%s modelName=%s temperature=%s apiKey=%s systemPromptPresent=%s",
            setting.isLocal,
            setting.isApi,
            setting.domainName,
            setting.modelName,
            setting.temperature,
            api_key_masked,
            bool(setting.systemPrompt),
        )

        if setting.isLocal:
            logger.debug("Using local model branch")
            return f"Local model response to: {prompt}"

        elif setting.isApi and setting.domainName == "huggingface":
            logger.debug("Using HuggingFace API: model=%s", setting.modelName)
            url = f"https://api-inference.huggingface.co/models/{setting.modelName}"
            headers = {"Authorization": f"Bearer {setting.apiKey}"}

            full_prompt = prompt
            if setting.systemPrompt:
                full_prompt = f"{setting.systemPrompt}\n\nUser: {prompt}"

            payload = {
                "inputs": full_prompt,
                "parameters": {
                    "max_new_tokens": 512,
                    "temperature": setting.temperature or 0.7
                }
            }

            try:
                req_start = time.perf_counter()
                response = requests.post(url, headers=headers, json=payload, timeout=60)
                req_elapsed = time.perf_counter() - req_start
                logger.debug("HuggingFace request completed in %.3fs; status=%s", req_elapsed, response.status_code)
            except Exception as e:
                logger.exception("HuggingFace request failed")
                return f"HuggingFace request error: {e}"

            if response.status_code != 200:
                logger.error("HuggingFace API Error: status=%s text=%s", response.status_code, (response.text or "")[:500])
                return f"HuggingFace API Error: {response.text}"

            try:
                data = response.json()
            except Exception as e:
                logger.exception("Failed to parse HuggingFace JSON response")
                return f"HuggingFace JSON parse error: {e}"

            logger.debug("HuggingFace response data (truncated)=%s", str(data)[:1000])
            if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
                result = data[0]["generated_text"].replace(full_prompt, "").strip()
                elapsed = time.perf_counter() - start_time
                logger.debug("get_llm_response finished in %.3fs", elapsed)
                return result

            if isinstance(data, dict) and "error" in data:
                logger.error("HuggingFace API returned error field: %s", data.get("error"))
                return f"HuggingFace API Error: {data['error']}"
    finally:
        try:
            db.close()
        except Exception:
            logger.exception("Failed to close DB session")
