import os
from dataclasses import dataclass

from openai import OpenAI


class AIProviderError(Exception):
    """Raised when the configured AI provider cannot complete a request."""


@dataclass
class ProviderResult:
    text: str
    provider_mode: str


TEMPLATES = {
    "general": "Answer the user's request clearly and concisely.\n\nUser prompt:\n{prompt}",
    "explain": "Explain the following topic step by step for a technical beginner. Include a small example when useful.\n\nTopic:\n{prompt}",
    "summarize": "Summarize the following text into concise bullet points. Preserve important facts and action items.\n\nText:\n{prompt}",
    "interview": "Answer the following as if you are helping a candidate prepare for a technical interview. Give a concise, interview-ready answer first, then a short explanation.\n\nQuestion:\n{prompt}",
}


def _mock_response(prompt, template_name):
    label = template_name.replace("_", " ").title()
    return ProviderResult(
        text=(
            f"[MOCK MODE — {label}]\n\n"
            f"Received prompt ({len(prompt)} characters): {prompt}\n\n"
            "This deterministic response is used because no real AI API key is configured."
        ),
        provider_mode="mock",
    )


def _openrouter_response(prompt, template_name):
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    model = os.getenv(
        "OPENROUTER_MODEL",
        "openai/gpt-oss-20b:free",
    ).strip()
    timeout = float(os.getenv("AI_TIMEOUT_SECONDS", "20"))

    if not api_key:
        raise AIProviderError(
            "OpenRouter mode is enabled, but OPENROUTER_API_KEY is not configured."
        )

    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            timeout=timeout,
        )

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": TEMPLATES[template_name].format(prompt=prompt),
                }
            ],
        )

        text = (response.choices[0].message.content or "").strip()

        if not text:
            raise AIProviderError("OpenRouter returned an empty response.")

        return ProviderResult(
            text=text,
            provider_mode="openrouter",
        )

    except AIProviderError:
        raise
    except TimeoutError:
        raise
    except Exception as exc:
        raise AIProviderError(
            "OpenRouter could not complete the request. Check your API key, "
            "model, quota, network connection, and provider status."
        ) from exc


def _gemini_response(prompt, template_name):
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
    timeout = float(os.getenv("AI_TIMEOUT_SECONDS", "20"))

    if not api_key:
        raise AIProviderError(
            "Gemini mode is enabled, but GEMINI_API_KEY is not configured."
        )

    try:
        from google import genai

        client = genai.Client(
            api_key=api_key,
            http_options={"timeout": int(timeout * 1000)},
        )
        response = client.models.generate_content(
            model=model,
            contents=TEMPLATES[template_name].format(prompt=prompt),
        )
        text = (response.text or "").strip()

        if not text:
            raise AIProviderError("Gemini returned an empty response.")

        return ProviderResult(text=text, provider_mode="gemini")
    except AIProviderError:
        raise
    except TimeoutError:
        raise
    except Exception as exc:
        raise AIProviderError(
            "Gemini could not complete the request. Check your API key, model, "
            "network connection, quota, and provider status."
        ) from exc


def _openai_response(prompt, template_name):
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    model = os.getenv("OPENAI_MODEL", "gpt-5-mini").strip()
    timeout = float(os.getenv("AI_TIMEOUT_SECONDS", "20"))

    if not api_key:
        raise AIProviderError(
            "OpenAI mode is enabled, but OPENAI_API_KEY is not configured."
        )

    try:
        client = OpenAI(api_key=api_key, timeout=timeout)
        response = client.responses.create(
            model=model,
            input=TEMPLATES[template_name].format(prompt=prompt),
        )
        text = (response.output_text or "").strip()

        if not text:
            raise AIProviderError("OpenAI returned an empty response.")

        return ProviderResult(text=text, provider_mode="openai")
    except AIProviderError:
        raise
    except TimeoutError:
        raise
    except Exception as exc:
        raise AIProviderError(
            "OpenAI could not complete the request. Check your API key, model, "
            "network connection, quota, and provider status."
        ) from exc


def generate_response(prompt, template_name):
    mode = os.getenv("AI_PROVIDER", "auto").strip().lower()

    if mode == "mock":
        return _mock_response(prompt, template_name)

    if mode == "openrouter":
        return _openrouter_response(prompt, template_name)

    if mode == "gemini":
        return _gemini_response(prompt, template_name)

    if mode == "openai":
        return _openai_response(prompt, template_name)

    if mode == "auto":
        if os.getenv("OPENROUTER_API_KEY", "").strip():
            return _openrouter_response(prompt, template_name)
        if os.getenv("GEMINI_API_KEY", "").strip():
            return _gemini_response(prompt, template_name)
        if os.getenv("OPENAI_API_KEY", "").strip():
            return _openai_response(prompt, template_name)
        return _mock_response(prompt, template_name)

    raise AIProviderError(
        "Unsupported AI_PROVIDER. Use auto, openrouter, gemini, openai, or mock."
    )
