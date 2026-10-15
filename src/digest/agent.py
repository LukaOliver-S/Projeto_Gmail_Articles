import os, time
from pathlib import Path
import json

import re
from dotenv import load_dotenv
from google import genai
from openai import OpenAI
from digest.config import Config
load_dotenv()
cfg = Config("config.yaml").parse_config()

_gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
_local = OpenAI(base_url="", api_key = "local")





def _parse_json(text:str):
    if "</think>" in text:
        text = text.split("</think>")[-1]
    json_start = text.find("{")
    if json_start != -1:
        text = text[json_start:]
    text = re.sub(r",\s*([}\]])", r"\1", text)
    
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r'"overall_summary"\s*:\s*"([^"]*)"', text)
        summary = match.group(1) if match else ""
        print("JSON parse failed, recovered summary only. Raw:", text[:500])
        return {"overall_summary": summary, "stories": []} 


def _generate_gemini(prompt: str, model: str, fallback: list[str],
                     max_output_tokens: int = 1024, temperature: float = 0.2):   # 0.2 for extraction
    last_err = None
    model = model or "gemini-2.5-flash-lite"
    fallback = fallback or []
    for m in [model] + fallback:
        print(f"Trying model {m}...")
        try:
            response = _gemini_client.models.generate_content(
                model=m,
                contents=prompt,
                config={"max_output_tokens": max_output_tokens, "temperature": temperature},
            )
            return response.text
        except Exception as e:
            last_err = e
            print(f"Error with model {m}: {e}. Trying fallback...")    # {m}, not {model}
    raise last_err


def _generate_local(prompt: str, model: str, fallback: list[str],
                    max_output_tokens: int = 1024, temperature: float = 0.2):
    last_err = None
    model = model or "llama3.1"
    fallback = fallback or []
    for m in [model] + fallback:
        print(f"Trying local model {m}...")
        try:
            response = _local.chat.completions.create(
                model=m,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_output_tokens,     
                temperature=temperature,
                seed=42,
            )
            return response.choices[0].message.content
        except Exception as e:
            last_err = e
            if "connection" in str(e).lower() or "refused" in str(e).lower():
                raise RuntimeError(
                    f"Ollama not reachable at {_local.base_url}. "
                    f"Start it with `ollama serve`."
                ) from e
            print(f"Error with local model {m}: {e}. Trying fallback...")
    raise last_err


def extract_stories(clean_text: str):
    prompt_path = Path("prompts/extract_stories.txt")
    prompt_template = prompt_path.read_text(encoding="utf-8")
    full_prompt = prompt_template + "\n\n" + clean_text

    if cfg.generator == "gemini":
        raw = _generate_gemini(full_prompt, model=cfg.gen_model,
                               fallback=cfg.fallback_chain,
                               max_output_tokens=cfg.max_output_tokens)
    else:
        raw = _generate_local(full_prompt, model=cfg.local_model,
                              fallback=cfg.local_fallback,
                              max_output_tokens=cfg.max_output_tokens)

    result = _parse_json(raw)                  # ← parse ONCE, keep it
    result.setdefault("overall_summary", "")   # ← set defaults on THAT dict
    result.setdefault("stories", [])
    return result                              # ← return the same dict