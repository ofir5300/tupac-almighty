#!/bin/bash
set -euo pipefail

# Load environment variables from .env file
source "$(dirname "$0")/dot_env_loader.sh"

# Define Raspberry Pi details
SSH_PASSWORD="${SSH_PASSWORD:?Environment variable SSH_PASSWORD not set}"

echo "🚀 Starting deployment to Raspberry Pi ($PI_HOST)..."

# Step 1: Estimate build context size
echo "🧮 Estimating build context size... (before addressing .dockerignore)"
du -sh .. | awk '{print "📦 Context size: " $1}'

# Create a .dockerignore file if not present
if [ ! -f .dockerignore ]; then
  echo "Creating .dockerignore file (because not detected)..." 
  echo "__pycache__/" > .dockerignore
  echo "*.pyc" >> .dockerignore
  echo "*.pkl" >> .dockerignore
  echo "*.log" >> .dockerignore
  echo ".git" >> .dockerignore
  echo ".venv" >> .dockerignore
  echo "venv/" >> .dockerignore
  echo "node_modules/" >> .dockerignore
  echo ".DS_Store" >> .dockerignore
  echo "*.tar" >> .dockerignore
  echo "*.zip" >> .dockerignore
  echo "*.gz" >> .dockerignore
  echo "local-models/" >> .dockerignore
  echo ".env" >> .dockerignore
  echo "*.json" >> .dockerignore
  echo "secrets/" >> .dockerignore
fi

# Step 2: Build the Docker image for ARM architecture (note using repo path to find Dockerfile)
export DOCKER_BUILDKIT=1
echo "📦 Building Docker image..."
docker build \
  --platform linux/arm64 \
  -f "$REPO_ABSOLUTE_PATH/Dockerfile" \
  -t "$IMAGE_NAME" \
  "$REPO_ABSOLUTE_PATH"

# Step 3: Save the Docker image as a .tar file
echo "💾 Saving Docker image as $IMAGE_FILE..."
docker save -o $IMAGE_FILE $IMAGE_NAME

# Step 3.5: Check tar file size and warn if too large
TAR_SIZE=$(du -m "$IMAGE_FILE" | cut -f1)
if [ "$TAR_SIZE" -gt 5120 ]; then
  echo "❌ ERROR: Docker image exceeds 5GB (${TAR_SIZE}MB). Aborting deployment."
  exit 1
fi

# Step 4: Transfer the image to the Raspberry Pi using sshpass & rsync
echo "📡 Transferring image and deployment files to Raspberry Pi..."
sshpass -p "$SSH_PASSWORD" rsync -avz --progress $IMAGE_FILE $PI_USER@$PI_HOST:$PI_PATH/
sshpass -p "$SSH_PASSWORD" rsync -avz --progress $REPO_ABSOLUTE_PATH/.env $PI_USER@$PI_HOST:$PI_PATH/
sshpass -p "$SSH_PASSWORD" rsync -avz --progress $REPO_ABSOLUTE_PATH/docker-compose.yml $PI_USER@$PI_HOST:$PI_PATH/
sshpass -p "$SSH_PASSWORD" rsync -avz --progress $REPO_ABSOLUTE_PATH/config/ $PI_USER@$PI_HOST:$PI_PATH/config/

# Step 5: SSH into Raspberry Pi and deploy
echo "🚀 Deploying on Raspberry Pi..."
sshpass -p "$SSH_PASSWORD" ssh -o StrictHostKeyChecking=no $PI_USER@$PI_HOST /bin/bash -s <<EOF
    echo "📦 [RPI] Loading new Docker image..."
    docker load -i $PI_PATH/$IMAGE_FILE

    echo "🚀 [RPI] Deploying with Docker Compose..."
    cd $PI_PATH
    docker compose up -d --force-recreate # docker-compose is python based, docker compose is docker based
    docker image prune -af

    echo "✅ [RPI] Deployment complete!"
EOF

# Cleanup local Docker image file
echo "🧹 Cleaning up local files..."
rm -f $IMAGE_FILE

echo "🎉 Deployment finished successfully!"