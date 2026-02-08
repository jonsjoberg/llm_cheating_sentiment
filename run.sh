#!/bin/bash

MODEL="Mungert/Mistral-Small-3.1-24B-Instruct-2503-GGUF:Q4_K_M"
PORT=8080

cleanup() {
    echo "Shutting down llama server"
    kill $SERVER_PID
}
trap cleanup EXIT

# Start a local OpenAI-compatible server with a web UI:
llama-server -hf "$MODEL" --port $PORT -ngl 99 > llama_server.log 2>&1 & SERVER_PID=$!

echo "Starting llama-server (PID: $SERVER_PID)"

echo "Waiting for server to be ready..."
while ! curl -s "http://localhost:$PORT/health" | grep -q '{"status":"ok"}'; do
    sleep 2
done

echo "Server is up, running script"

pushd ./extraction_service > /dev/null
uv run main.py
popd > /dev/null

pushd ./frontend > /dev/null
pnpm build

firebase deploy
popd > /dev/null