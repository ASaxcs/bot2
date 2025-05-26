# Activate virtual environment
if [ -f "lacia_env/bin/activate" ]; then
    source lacia_env/bin/activate
else
    echo "❌ Virtual environment not found. Run install.sh first."
    exit 1
fi

# Check if config exists
if [ ! -f "config.json" ]; then
    echo "❌ Config file not found. Run install.sh first."
    exit 1
fi

# Check if model exists
MODEL_PATH=$(python3 -c "import json; print(json.load(open('config.json'))['model']['model_path'])")
if [ ! -f "$MODEL_PATH" ]; then
    echo "⚠️  Model file not found: $MODEL_PATH"
    echo "The system will run in fallback mode."
    echo "To download the model, run install.sh again or download manually."
    echo ""
fi

# Parse arguments
MODE=${1:-cli}

echo "🤖 Starting Lacia AI (GGUF) in $MODE mode..."

# Run based on mode
case $MODE in
    "cli")
        python main.py --mode cli
        ;;
    "gradio")
        echo "🌐 Web interface will be available at: http://localhost:7860"
        python main.py --mode gradio
        ;;
    "api")
        echo "🔗 API will be available at: http://localhost:8000"
        echo "📖 API docs: http://localhost:8000/docs"
        python main.py --mode api
        ;;
    "all")
        echo "🚀 Starting all interfaces..."
        echo "🌐 Web: http://localhost:7860"
        echo "🔗 API: http://localhost:8000"
        python main.py --mode all
        ;;
    *)
        echo "❌ Invalid mode. Use: cli, gradio, api, or all"
        exit 1
        ;;
esac
