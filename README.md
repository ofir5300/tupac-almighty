<div align="center">
<table>
  <tr>
    <td>
      <img src="assets/2pac-shakurliza.jpg" alt="2Pac" width="100"/>
    </td>
    <td>
      <span style="font-size:2em;font-weight:bold;">🪓 Tupac Almighty 🔫</span><br>
      <span style="font-size:1.2em;font-weight:bold;">Docker & RPI Deployment Guide</span>
    </td>
  </tr>
</table>
</div>

This guide covers **local development**, **Docker usage**, and **Raspberry Pi deployment**—including systemd integration for robust service management.

---

## 🛡️ Environment Setup

1. Copy `.env.example` to `.env` and fill in all required values:
   ```sh
   cp .env.example .env
   ```

---

## 📦 Local Development

> **Recommended:** Use pyenv & pyenv-virtualenv for Python isolation.

1. _(Optional but recommended)_ **Set up a virtual environment:**

   ```sh
   pyenv install 3.13.2
   pyenv virtualenv 3.13.2 "$PROJECT_NAME"
   pyenv local "$PROJECT_NAME"
   ```

2. **Install dependencies:**

   ```sh
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```sh
   python main.py
   ```

> You can skip the virtualenv steps and use your system Python if you prefer, but isolation is safer for dependencies.

---

## 🐳 Running with Docker

1. **Build the Docker image (ARM64 for RPi):**

   ```sh
   docker build --platform linux/arm64 -t tupac .
   ```

2. **Run the container:**

   ```sh
   docker run --rm -it tupac
   ```

3. **Detached mode:**
   ```sh
   docker run -d --name tupac tupac
   ```

---

## 🔄 Deploying to Raspberry Pi

### 1️⃣ Automated Deployment

Use the deployment script for a full build-transfer-deploy cycle:

```sh
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

- Builds the image locally for ARM64
- Saves as a tarball
- Transfers image, `.env`, `docker-compose.yml`, and `config/` to the Pi
- Loads and runs via Docker Compose on the Pi

**Paths:**

- Script: `scripts/deploy.sh`
- Service file: `config/telegram-bot.service.ini`

### 2️⃣ Manual Deployment (Advanced)

```sh
docker save -o tupac.tar tupac
scp tupac.tar pi@<PI_HOST>:/home/pi/
ssh pi@<PI_HOST> "docker load -i /home/pi/tupac.tar && docker compose up -d --force-recreate"
```

---

## 🛠 Docker Management

- **Check containers:** `docker ps`
- **Logs:** `docker logs tupac`
- **Stop:** `docker stop tupac`
- **Restart:** `docker start tupac`
- **Prune:** `docker system prune -a`

---

## 🖥️ Systemd Integration (Recommended for RPi)

1. **Copy the service file to your Pi:**

   ```sh
   scp config/telegram-bot.service.ini pi@<PI_HOST>:/etc/systemd/system/telegram-bot.service
   ```

2. **Enable and manage the service:**
   ```sh
   sudo systemctl daemon-reload
   sudo systemctl enable telegram-bot
   sudo systemctl start telegram-bot
   sudo systemctl status telegram-bot
   sudo systemctl stop telegram-bot
   ```

- This ensures the bot starts on boot and restarts on failure.
