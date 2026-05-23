"""
backend/app/gateway/config.py
Single source of truth for all ModelGateway provider configuration.
Adding a new provider = add one entry here. No other file changes needed.
"""
from decimal import Decimal

PROVIDER_POOLS: dict[str, list[str]] = {
    "llm": [
        "groq-llama-3.3-70b",
        "together-llama-3.3",
        "siliconflow-qwen",
        "deepseek-v3",
        "openai-gpt4o-mini",
    ],
    "tts": [
        "sarvam-bulbul",
        "elevenlabs-rachel",
    ],
    "i2v": [
        "fal-wan-i2v",
        "atlascloud-wan",
        "minimax-hailuo",
        "replicate-wan",
    ],
    "moderation": [
        "groq-llama-guard",
        "openai-moderation",
    ],
    "vision": [
        "openai-gpt4o-mini",
        "gemini-flash",
    ],
}

TTS_LANGUAGE_AFFINITY: dict[str, str] = {
    "hindi":    "sarvam-bulbul",
    "hinglish": "sarvam-bulbul",
    "marathi":  "sarvam-bulbul",
    "punjabi":  "sarvam-bulbul",
    "bengali":  "sarvam-bulbul",
    "tamil":    "sarvam-bulbul",
    "telugu":   "sarvam-bulbul",
    "english":  "elevenlabs-rachel",
}

SARVAM_LANG_MAP: dict[str, str] = {
    "hindi":    "hi-IN",
    "hinglish": "hi-IN",
    "marathi":  "mr-IN",
    "punjabi":  "pa-IN",
    "bengali":  "bn-IN",
    "tamil":    "ta-IN",
    "telugu":   "te-IN",
    "english":  "en-IN",
}

COST_RATES: dict[str, tuple] = {
    "groq-llama-3.3-70b":  (Decimal("0.000"), Decimal("0.000")),
    "together-llama-3.3":  (Decimal("0.018"), Decimal("0.060")),
    "siliconflow-qwen":    (Decimal("0.005"), Decimal("0.010")),
    "deepseek-v3":         (Decimal("0.022"), Decimal("0.090")),
    "openai-gpt4o-mini":   (Decimal("0.015"), Decimal("0.060")),
    "groq-llama-guard":    (Decimal("0.000"), Decimal("0.000")),
    "openai-moderation":   (Decimal("0.000"), Decimal("0.000")),
    "gemini-flash":        (Decimal("0.000"), Decimal("0.000")),
}

PROVIDER_CONFIG: dict[str, dict] = {
    "groq-llama-3.3-70b": {
        "url":      "https://api.groq.com/openai/v1/chat/completions",
        "key_env":  "GROQ_API_KEY",
        "model_id": "llama-3.3-70b-versatile",
        "timeout_s": 30,
        "cost_inr":  Decimal("0.00"),
    },
    "together-llama-3.3": {
        "url":      "https://api.together.xyz/v1/chat/completions",
        "key_env":  "TOGETHER_API_KEY",
        "model_id": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "timeout_s": 30,
        "cost_inr":  Decimal("0.00"),
    },
    "siliconflow-qwen": {
        "url":      "https://api.siliconflow.cn/v1/chat/completions",
        "key_env":  "SILICONFLOW_API_KEY",
        "model_id": "Qwen/Qwen2.5-7B-Instruct",
        "timeout_s": 30,
        "cost_inr":  Decimal("0.00"),
    },
    "deepseek-v3": {
        "url":      "https://api.deepseek.com/v1/chat/completions",
        "key_env":  "DEEPSEEK_API_KEY",
        "model_id": "deepseek-chat",
        "timeout_s": 30,
        "cost_inr":  Decimal("0.00"),
    },
    "openai-gpt4o-mini": {
        "url":      "https://api.openai.com/v1/chat/completions",
        "key_env":  "OPENAI_API_KEY",
        "model_id": "gpt-4o-mini",
        "timeout_s": 30,
        "cost_inr":  Decimal("0.00"),
    },
    "sarvam-bulbul": {
        "url":      "https://api.sarvam.ai/text-to-speech",
        "key_env":  "SARVAM_API_KEY",
        "model_id": "bulbul:v3",
        "speaker":  "priya",
        "timeout_s": 30,
        "cost_inr":  Decimal("1.50"),
    },
    "elevenlabs-rachel": {
        "url":      "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM",
        "key_env":  "ELEVENLABS_API_KEY",
        "model_id": "eleven_monolingual_v1",
        "timeout_s": 30,
        "cost_inr":  Decimal("3.00"),
    },
    "fal-wan-i2v": {
        "submit_url":      "https://queue.fal.run/fal-ai/wan-i2v",
        "status_url":      "https://queue.fal.run/fal-ai/wan-i2v/requests/{request_id}/status",
        "result_url":      "https://queue.fal.run/fal-ai/wan-i2v/requests/{request_id}",
        "key_env":         "FAL_KEY",
        "auth_prefix":     "Key",
        "timeout_s":       30,
        "poll_interval_s": 5,
        "max_polls":       60,
        "cost_inr":        Decimal("13.00"),
    },
    "atlascloud-wan": {
        "submit_url":      "https://api.atlascloud.ai/api/v1/model/generateVideo",
        "poll_url":        "https://api.atlascloud.ai/api/v1/model/prediction/{prediction_id}",
        "key_env":         "ATLAS_CLOUD_API_KEY",
        "model_id":        "alibaba/wan-2.6/image-to-video",
        "auth_prefix":     "Bearer",
        "timeout_s":       60,
        "poll_interval_s": 5,
        "max_polls":       54,
        "cost_inr":        Decimal("37.00"),
    },
    "minimax-hailuo": {
        "submit_url":      "https://api.minimax.io/v1/video_generation",
        "poll_url":        "https://api.minimax.io/v1/query/video_generation",
        "file_url":        "https://api.minimax.io/v1/files/retrieve",
        "key_env":         "MINIMAX_API_KEY",
        "model_id":        "MiniMax-Hailuo-2.3",
        "auth_prefix":     "Bearer",
        "timeout_s":       30,
        "poll_interval_s": 5,
        "max_polls":       40,
        "cost_inr":        Decimal("18.00"),
    },
    "replicate-wan": {
        "submit_url":  "https://api.replicate.com/v1/predictions",
        "poll_base":   "https://api.replicate.com/v1/predictions/{prediction_id}",
        "key_env":     "REPLICATE_API_TOKEN",
        "model_version": "e2870aa4965fd9ddfd87c16a3c8ab952c18e745e63f3f3b123c2dc8b538ad2b5",
        "auth_prefix": "Token",
        "timeout_s":   30,
        "poll_interval_s": 5,
        "max_polls":   40,
        "cost_inr":    Decimal("12.00"),
    },
    "groq-llama-guard": {
        "url":      "https://api.groq.com/openai/v1/chat/completions",
        "key_env":  "GROQ_API_KEY",
        "model_id": "meta-llama/llama-guard-4-12b",
        "timeout_s": 30,
        "cost_inr":  Decimal("0.00"),
    },
    "openai-moderation": {
        "url":      "https://api.openai.com/v1/moderations",
        "key_env":  "OPENAI_API_KEY",
        "model_id": "omni-moderation-latest",
        "timeout_s": 10,
        "cost_inr":  Decimal("0.00"),
    },
    "gemini-flash": {
        "key_env":  "GEMINI_API_KEY",
        "model_id": "gemini-2.0-flash",
        "timeout_s": 30,
        "cost_inr":  Decimal("0.00"),
    },
}
