import sys
import os
import numpy as np
from urllib import response
import torch
import torchaudio
from transformers import (
    AutoModelForCausalLM,
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    AutoProcessor,
    WhisperForConditionalGeneration,
)
from datasets import load_dataset, Audio
from typing import Literal

from application.utils import utils, consts


def get_device():
    return "mps" if torch.backends.mps.is_available() else "cpu"


def whisper_from_file(audio_path: str) -> str:
    whisper_model = "ivrit-ai/whisper-large-v3-turbo"

    processor = AutoProcessor.from_pretrained(whisper_model)
    model = (
        WhisperForConditionalGeneration.from_pretrained(whisper_model)
        .to(get_device())
        .to(torch.float16)
    )

    # Load and preprocess audio
    waveform, original_sr = torchaudio.load(audio_path)
    if original_sr != 16000:
        waveform = torchaudio.functional.resample(
            waveform, orig_freq=original_sr, new_freq=16000
        )
    waveform = waveform.mean(dim=0).numpy()  # mono + numpy

    # Pad waveform to exactly 30s (480k samples)
    target_len = 480_000
    if len(waveform) < target_len:
        pad_len = target_len - len(waveform)
        waveform = np.pad(waveform, (0, pad_len), mode="constant")
    elif len(waveform) > target_len:
        waveform = waveform[:target_len]

    # Wrap in list for batch processing
    audio_batch = [waveform]

    features = processor.feature_extractor(
        audio_batch,
        sampling_rate=16000,
        return_tensors="pt",
        truncation=False,
        padding="longest",
        max_length=3000,
        pad_to_max_length=True,
    )

    input_features = features.input_features.to(get_device()).to(torch.float16)
    generated_ids = model.generate(input_features=input_features)
    transcription = processor.tokenizer.batch_decode(
        generated_ids, skip_special_tokens=True
    )

    os.remove(audio_path)
    return transcription[0]


def whisper(query: str) -> str:
    whisper_model_ivrit = "ivrit-ai/whisper-large-v3-turbo"
    whisper_model_ivrit_fast = "ivrit-ai/faster-whisper-v2-d4"
    whisper_model_openai = "openai/whisper-tiny.en"
    whisper_model = whisper_model_ivrit  # whisper_model_openai

    processor = AutoProcessor.from_pretrained(whisper_model)
    model = (
        WhisperForConditionalGeneration.from_pretrained(whisper_model)
        .to(get_device())
        .to(torch.float16)
    )

    ds = load_dataset("distil-whisper/meanwhile", "default")["test"]
    ds = ds.cast_column("audio", Audio(sampling_rate=16000))
    audio = ds[:8]["audio"]
    audio = [x["array"] for x in audio]
    # make sure to NOT truncate the input audio, to return the `attention_mask` and to pad to the longest audio
    inputs = processor(
        audio,
        return_tensors="pt",
        truncation=False,
        padding="longest",
        return_attention_mask=True,
        sampling_rate=16_000,
    )
    inputs = inputs.to(get_device()).to(torch.float16)
    generated_ids = model.generate(**inputs, return_timestamps=True)

    transcription = processor.batch_decode(generated_ids, skip_special_tokens=True)
    return transcription[0]


def google(query: str) -> str:
    on_rpi = utils.is_running_on_pi_inside_docker()
    REPO_ABSOLUTE_PATH = utils.load_secret("REPO_ABSOLUTE_PATH")
    local_path = f"{REPO_ABSOLUTE_PATH}/local-models/google-flan-t5-small"
    hugging_face_model_name = "google/flan-t5-small"

    google_model = hugging_face_model_name if on_rpi else local_path
    print(
        f"{'🏠 NOT ' if not on_rpi else '🍓 '}On RPI, thus using MODEL: {google_model}"
    )
    tokenizer = AutoTokenizer.from_pretrained(
        google_model, local_files_only="local-models" in google_model
    )
    model = AutoModelForSeq2SeqLM.from_pretrained(
        google_model,
        device_map="auto",
        low_cpu_mem_usage=True,
    )
    return run(query, model, tokenizer)


def run(query, model, tokenizer) -> str:
    inputs = tokenizer(
        query, return_tensors="pt", padding=True, truncation=True, max_length=50
    ).to(get_device())
    outputs = model.generate(**inputs, max_new_tokens=50)  # Faster generation
    text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return text


def meta(query: str) -> str:
    model_name_or_path = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    tokenizer = AutoTokenizer.from_pretrained(
        model_name_or_path, local_files_only="local-models" in model_name_or_path
    )
    model = AutoModelForCausalLM.from_pretrained(
        model_name_or_path,
        device_map="auto",
        low_cpu_mem_usage=True,
    )
    return run(f"answer the user's question:\n {query}", model, tokenizer)

def microsoft(query: str) -> str:
    local_path = f"{consts.repo_absolute_path}/local-models/microsoft-Phi-3-mini-4k-instruct"
    hugging_face_model_name = "microsoft/Phi-3-mini-4k-instruct"
    model_name_or_path = local_path
    # (
    #     local_path if utils.is_running_on_pi_inside_docker() else hugging_face_model_name
    # )
    tokenizer = AutoTokenizer.from_pretrained(
        model_name_or_path, local_files_only="local-models" in model_name_or_path
    )
    model = AutoModelForCausalLM.from_pretrained(
        model_name_or_path,
        device_map="auto",
        low_cpu_mem_usage=True,
    )
    return run(f"answer the user's question:\n {query}", model, tokenizer)


def mistral(query: str) -> str:
    # mistral_model = f"{consts.repo_absolute_path}/local-models/mistral-v0.3"
    mistral_model = f"{consts.repo_absolute_path}/local-models/mistral-v0.1"
    tokenizer = AutoTokenizer.from_pretrained(mistral_model, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        mistral_model, device_map="auto", low_cpu_mem_usage=True
    )
    inputs = tokenizer(query, return_tensors="pt").to(get_device())
    outputs = model.generate(**inputs, max_new_tokens=50)  # Faster generation
    text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return text


def ask(
    query: str,
    model_type: Literal["google", "mistral", "whisper", "whisper_from_file", "meta"],
) -> None:
    if model_type == "google":
        return google(query)
    if model_type == "meta":
        return meta(query)
    elif model_type == "mistral":
        return mistral(query)
    elif model_type == "whisper":
        return whisper(query)
    elif model_type == "whisper_from_file":
        return whisper_from_file(query)
    elif model_type == "microsoft":
        return microsoft(query)
    else:
        raise ValueError(
            "Invalid model type. Choose either 'google', 'mistral', 'whisper', 'whisper_from_file', 'meta'."
        )


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python host_llm.py <model_type> <query>")
        sys.exit(1)

    model_type = sys.argv[1]
    query = sys.argv[2]

    print("🧠 Asking LLM", model_type)
    print("❓ Query:\n", query)
    response = ask(query, model_type)
    print("💬 Response:\n", response)


"""
    rpi@rpi:~ $ ssh $MAC_USER@$MAC_IP '$REPO_ABSOLUTE_PATH/scripts/llm_controller.command $MODEL_TYPE "$QUERY"'
"""