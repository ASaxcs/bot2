# install.sh - FIXED untuk GGUF
#!/bin/bash

echo "🚀 Installing Lacia AI System (GGUF Version)..."

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Python version: $python_version"

if python3 -c 'import sys; exit(sys.version_info < (3, 8))'; then
    echo "✅ Python version is compatible"
else
    echo "❌ Python 3.8+ required"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv lacia_env
source lacia_env/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install llama-cpp-python (CUDA or CPU)
echo "🔥 Installing llama-cpp-python..."
if command -v nvidia-smi &> /dev/null; then
    echo "CUDA detected, installing CUDA version..."
    CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python --verbose
else
    echo "CUDA not detected, installing CPU version..."
    pip install llama-cpp-python
fi

# Install other requirements
echo "📚 Installing other dependencies..."
pip install -r requirements.txt

# Create models directory
echo "📁 Creating models directory..."
mkdir -p models

# Create config file - FIXED untuk match main.py
echo "⚙️ Creating default config..."
cat > config.json << 'EOF'
{
    "model": {
        "model_id": "TheBloke/Mistral-7B-Instruct-v0.2-GGUF",
        "model_basename": "mistral-7b-instruct-v0.2.Q4_K_M.gguf",
        "model_path": "models/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
        "n_ctx": 2048,
        "n_batch": 512,
        "n_threads": null,
        "max_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.9,
        "verbose": false
    },
    "personality": {
        "assertiveness": 0.6,
        "empathy": 0.8,
        "curiosity": 0.9,
        "adaptation_rate": 0.1
    },
    "memory": {
        "short_term_capacity": 50,
        "long_term_threshold": 0.7,
        "memory_decay": 0.95
    },
    "emotion": {
        "emotional_sensitivity": 0.6,
        "mood_persistence": 0.8,
        "default_mood": "neutral"
    },
    "interface": {
        "cli_enabled": true,
        "api_enabled": true,
        "gradio_enabled": true,
        "api_port": 8000,
        "gradio_port": 7860
    }
}
EOF

# Download model file if not exists
echo "📥 Checking model file..."
MODEL_URL="https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
MODEL_PATH="models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"

if [ ! -f "$MODEL_PATH" ]; then
    echo "📥 Downloading model file (~4GB)..."
    echo "This may take a while depending on your internet connection..."
    
    if command -v wget &> /dev/null; then
        wget -O "$MODEL_PATH" "$MODEL_URL"
    elif command -v curl &> /dev/null; then
        curl -L -o "$MODEL_PATH" "$MODEL_URL"
    else
        echo "❌ Neither wget nor curl found. Please install one of them or download manually:"
        echo "URL: $MODEL_URL"
        echo "Save to: $MODEL_PATH"
    fi
    
    if [ -f "$MODEL_PATH" ]; then
        echo "✅ Model downloaded successfully!"
    else
        echo "❌ Model download failed. You can download it manually later."
    fi
else
    echo "✅ Model file already exists!"
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "📋 Setup Summary:"
echo "  - Virtual environment: lacia_env"
echo "  - Config file: config.json"
echo "  - Model path: $MODEL_PATH"
echo "  - Model size: ~4GB"
echo ""
echo "🚀 How to run:"
echo "1. Activate environment: source lacia_env/bin/activate"
echo "2. Run CLI mode: python main.py --mode cli"
echo "3. Run web interface: python main.py --mode gradio"
echo "4. Run API server: python main.py --mode api"
echo "5. Run all modes: python main.py --mode all"
echo ""
echo "📝 Configuration file: config.json"
echo "🔧 For GPU support: pip install llama-cpp-python[cuda]"



