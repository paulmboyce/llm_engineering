#!/bin/bash

echo "🚀 Setting up Node.js environment for Website Summariser..."

# Install nvm
echo "📦 Installing nvm..."
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash

# Load nvm
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Verify nvm installation
if ! command -v nvm &> /dev/null; then
    echo "❌ nvm installation failed. Please install nvm manually."
    exit 1
fi

echo "✅ nvm installed successfully"

# Install Node.js 18
echo "📦 Installing Node.js 18..."
nvm install 18

# Use Node.js 18
echo "🔄 Switching to Node.js 18..."
nvm use 18

# Set default Node.js version
echo "⚙️ Setting Node.js 18 as default..."
nvm alias default 18

# Verify Node.js version
NODE_VERSION=$(node --version)
echo "✅ Node.js version: $NODE_VERSION"

# Clean and reinstall dependencies
echo "🧹 Cleaning node_modules..."
rm -rf node_modules

echo "📦 Installing dependencies..."
npm install cross-env node-fetch
npm install

# Verify Ollama installation
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama is not installed. Please install Ollama from: https://ollama.ai"
    echo "   After installing, run: ollama serve"
else
    echo "✅ Ollama is installed"
fi

echo "🎉 Setup complete! You can now run the application with 'npm start'"
echo "   Make sure Ollama is running with: ollama serve" 