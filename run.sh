#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Usage: $0 [llm service type]"
    exit 1
fi

if [[ "$1" == "local" ]]; then

    MODEL="Mungert/Mistral-Small-3.1-24B-Instruct-2503-GGUF:Q4_K_M"
    PORT=8080

    cleanup() {
        echo "Shutting down llama server"
        kill $SERVER_PID
        exit 1
    }
    trap cleanup EXIT

    # Log rotation: keep the last 3 runs
    for i in 2 1; do
        if [ -f "llama_server_$i.log" ]; then
            mv "llama_server_$i.log" "llama_server_$((i+1)).log"
        fi
    done
    if [ -f "llama_server.log" ]; then
        mv "llama_server.log" "llama_server_1.log"
    fi

    # Start a local OpenAI-compatible server with a web UI:
    llama-server -hf "$MODEL" --port $PORT -ngl 99 --log-disable > llama_server.log 2>&1 & SERVER_PID=$!

    echo "Starting llama-server (PID: $SERVER_PID)"

    echo "Waiting for server to be ready..."
    while ! curl -s "http://localhost:$PORT/health" | grep -q '{"status":"ok"}'; do
        sleep 2
    done

    echo "Server is up, running script"

    pushd ./extraction_service > /dev/null
    uv run main.py --llm-service-type $1 || exit 1
    popd > /dev/null
elif [[ "$1" == "openrouter" ]]; then
    pushd ./extraction_service > /dev/null
    uv run main.py --llm-service-type $1 || exit 1
    popd > /dev/null
else 
    echo "Unknown llm service type"
    exit 1
fi


pushd ./frontend > /dev/null
pnpm build

firebase deploy
popd > /dev/null