import os
import asyncio
import platform
from typing import Literal


def is_linux_arm() -> bool:
    """Check if running on Linux with ARM architecture (i.e., Raspberry Pi)."""
    return platform.system() == "Linux" and platform.machine().lower() in (
        "armv7l",
        "aarch64",
    )


def is_docker() -> bool:
    """Check if running inside a Docker container."""
    try:
        with open("/proc/1/sched") as f:
            return "python" in f.readline()
    except:
        return False


def is_running_on_pi_inside_docker() -> bool:
    """High-confidence detection: running inside Docker on Raspberry Pi."""
    docker = is_docker()
    arm = is_linux_arm()
    print(f"🔎 [ENV CHECK] 🐳 Docker={docker}, ⚙️ ARM={arm}")
    return docker and arm


def use_asyncio(callback) -> None:
    loop = asyncio.new_event_loop()
    loop.run_until_complete(callback)
    asyncio.set_event_loop(loop)


def load_secret(
    secret_name: Literal[
        "TELEGRAM_DEFAULT_USER_ID",
        "TELEGRAM_TOKEN",
        # "PI_USER",
        # "PI_HOST",
        # "PI_PATH",
        # "IMAGE_NAME",
        # "IMAGE_FILE",
        "SSH_PASSWORD",
        "MAC_USER",
        "MAC_IP",
        "REPO_ABSOLUTE_PATH",
        # "VIRTUAL_ENV_PATH",
    ],
) -> str:
    return os.getenv(secret_name)
