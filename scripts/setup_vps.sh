#!/bin/bash
# Setup script for Contabo Linux VPS (Ubuntu/Debian)

set -e

echo "=========================================="
echo " Polymarket Intelligence Lab VPS Setup"
echo "=========================================="

# 1. Update system packages
echo "--> Updating system packages..."
sudo apt-get update && sudo apt-get upgrade -y

# 2. Install dependencies (Python 3.12, Poetry, Git)
echo "--> Installing Python and Git..."
sudo apt-get install -y python3.12 python3.12-venv python3-pip git cron curl

# 3. Install Poetry
echo "--> Installing Poetry..."
curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
export PATH="/root/.local/bin:$PATH"
echo 'export PATH="/root/.local/bin:$PATH"' >> ~/.bashrc

# 4. Clone repository (User should run this script inside the cloned repo, or we clone it here)
# Since the script is inside the repo, we assume the user already cloned it.
echo "--> Installing Project Dependencies..."
cd "$(dirname "$0")/.." || exit
python3 -m poetry install

# 5. Environment Variables Setup
echo "--> Setting up environment..."
if [ ! -f .env ]; then
    echo "OPENAI_API_KEY=tu_clave_aqui" > .env
    echo "Created .env file. PLEASE EDIT IT with your OpenAI API Key: nano .env"
fi

echo "=========================================="
echo " Setup Complete! "
echo " Next steps:"
echo " 1. Edit .env with your OPENAI_API_KEY"
echo " 2. Add the cron jobs using: crontab -e"
echo "    (See scripts/crontab_example.txt)"
echo "=========================================="
