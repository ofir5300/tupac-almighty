from application.handlers import host_llm
from application.utils import utils, consts
import subprocess
import shlex
import shutil

import shlex
import shutil
import subprocess


def mac_as_a_server(question: str, model: str, with_file: bool = False) -> str:
    print(
        f"[SSH] Calling Mac with model={model}, query={question}, with_file={with_file}"
    )

    REPO_ABSOLUTE_PATH = utils.load_secret("REPO_ABSOLUTE_PATH")
    MAC_USER = utils.load_secret("MAC_USER")
    MAC_IP = utils.load_secret("MAC_IP")
    SSH_PASSWORD = utils.load_secret("SSH_PASSWORD")
    sshpass_path = shutil.which("sshpass") or "sshpass"

    script = f"{REPO_ABSOLUTE_PATH}/scripts/llm_controller.command"

    if with_file:
        # Upload file first using scp
        mac_path = f"{REPO_ABSOLUTE_PATH}/{question}"
        scp_cmd = [
            sshpass_path,
            "-p",
            SSH_PASSWORD,
            "scp",
            "-o",
            "StrictHostKeyChecking=no",
            question,
            f"{MAC_USER}@{MAC_IP}:{shlex.quote(mac_path)}",
        ]
        print(f"[SCP CMD] {' '.join(scp_cmd)}")
        scp_result = subprocess.run(scp_cmd, capture_output=True, text=True)
        if scp_result.returncode != 0:
            print(f"[SCP CMD] FAILED: {scp_result}")
            raise RuntimeError(f"❌ SCP failed:\n{scp_result.stderr}")

        # Remote command for transcription
        # remote_command = f"{script} {model} {mac_path}"
        safe_cmd = f"{shlex.quote(script)} {shlex.quote(model)} {shlex.quote(mac_path)}"
    else:
        # Remote command for LLM query
        safe_cmd = f"{shlex.quote(script)} {shlex.quote(model)} {shlex.quote(question)}"

    remote_command = f"bash -c {shlex.quote(safe_cmd)}"
    ssh_cmd = [
        sshpass_path,
        "-p",
        SSH_PASSWORD,
        "ssh",
        "-o",
        "StrictHostKeyChecking=no",
        f"{MAC_USER}@{MAC_IP}",
        remote_command,
    ]

    print(f"[SSH CMD] {' '.join(ssh_cmd)}")
    result = subprocess.run(ssh_cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"[SSH CMD] FAILED: {result}")
        raise RuntimeError(f"❌ SSH call failed:\n{result.stderr}")

    print(f"[SSH CMD] SUCCESS: {result}")
    return result.stdout.strip()


def ask(query: str) -> str:
    print(f"[CALL] ask() triggered with query: '{query}'")

    if utils.is_running_on_pi_inside_docker():
        print("[ROUTE] Detected Raspberry Pi — calling Mac over SSH.")
        try:
            result = mac_as_a_server(query, "google")
            print(f"[RESULT] SSH call succeeded. Response: {result[:20]}...")
            return result
        except Exception as e:
            print(f"[ERROR] Failed calling Mac, falling back to [meta] model: {e}")
            return host_llm.ask(query, "meta")

    print("[ROUTE] Not running on Pi — using local host_llm.")
    return host_llm.ask(query, "google")


def transcribe(path: str) -> str:
    print(f"[TRANSCRIBE] Offloading audio to Mac: {path}")

    if utils.is_running_on_pi_inside_docker():
        print("[ROUTE] Detected Raspberry Pi — calling Mac over SSH.")
        try:
            result = mac_as_a_server(path, "whisper_from_file", with_file=True)
            print(f"[RESULT] SSH call succeeded. Response: {result[:20]}...")
            return result
        except Exception as e:
            print(
                f"[ERROR] Failed calling Mac, falling back to local [whisper] model: {e}"
            )
            pass

    print("[ROUTE] Not running on Pi — using local host_llm.")
    return host_llm.whisper_from_file(path)
