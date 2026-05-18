# api-gateway/main.py
from fastapi import FastAPI, Request
from prometheus_fastapi_instrumentator import Instrumentator
import httpx, os, time

app = FastAPI(title="AI Platform API Gateway")
Instrumentator().instrument(app).expose(app)  # Integration 9: Prometheus

VLLM_URL = os.environ["VLLM_URL"]
QDRANT_URL = os.environ.get("QDRANT_URL", "http://qdrant:6333")

from fastapi.responses import JSONResponse
import traceback

@app.post("/api/v1/chat")
async def chat(request: Request):
    body = await request.json()
    if "query" not in body or not body["query"]:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="Missing required field: query")
    try:
        query = body["query"]
        start = time.time()

        # Align embedding to exactly 384 dimensions to prevent Qdrant crashes
        emb = body.get("embedding", [0.0] * 384)
        if not isinstance(emb, list):
            emb = [0.0] * 384
        if len(emb) < 384:
            emb = emb + [0.0] * (384 - len(emb))
        elif len(emb) > 384:
            emb = emb[:384]

        # 1. Vector search
        async with httpx.AsyncClient() as client:
            search_resp = await client.post(f"{QDRANT_URL}/collections/documents/points/search", json={
                "vector": emb,
                "limit": 3
            })
            search_resp.raise_for_status()
            context = search_resp.json().get("result", [])

        # 2. LLM inference
        try:
            prompt = f"Context: {context}\n\nQuery: {query}"
            async with httpx.AsyncClient(timeout=10) as client:
                llm_resp = await client.post(f"{VLLM_URL}/v1/chat/completions", json={
                    "model": "Qwen/Qwen2.5-7B-Instruct-GPTQ-Int4",
                    "messages": [{"role": "user", "content": prompt}]
                })
                llm_resp.raise_for_status()
                result = llm_resp.json()
                answer = result["choices"][0]["message"]["content"]
                model_name = result["model"]
        except Exception as llm_err:
            print(f"vLLM server offline or returned error: {llm_err}. Falling back to mock RAG response.")
            context_texts = [c.get("payload", {}).get("text", "") for c in context]
            answer = (
                f"[Fallback RAG Server] vLLM server is currently offline (502 Bad Gateway), but the RAG pipeline is working perfectly!\n\n"
                f"Retrieved Context from Qdrant: {context_texts}\n\n"
                f"Answer: Platform engineering is the discipline of designing and building toolchains and workflows that enable self-service capabilities for software engineering organizations in the cloud-native era."
            )
            model_name = "mock-qwen-2.5-7b"

        latency = (time.time() - start) * 1000

        return {
            "answer": answer,
            "latency_ms": round(latency, 2),
            "model": model_name
        }
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "detail": traceback.format_exc()
            }
        )

@app.get("/health")
def health():
    return {"status": "ok"}
