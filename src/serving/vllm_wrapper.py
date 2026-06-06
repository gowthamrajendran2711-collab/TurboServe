"""vLLM engine wrapper with health and metrics hooks"""
from vllm import LLM, SamplingParams
from prometheus_client import Histogram, Gauge
import time

GENERATION_LATENCY = Histogram("vllm_generation_latency_seconds", "Generation latency", ["model"])
BATCH_SIZE = Histogram("vllm_batch_size", "Batch size at generation time", ["model"])
GPU_KV_USAGE = Gauge("vllm_gpu_kv_cache_usage", "GPU KV cache usage fraction", ["model"])

class VLLMWrapper:
    def __init__(self, model: str, gpu_memory_utilization: float = 0.90,
                 max_model_len: int = 8192, tensor_parallel_size: int = 1):
        self.model = model
        self.llm = LLM(
            model=model,
            gpu_memory_utilization=gpu_memory_utilization,
            max_model_len=max_model_len,
            tensor_parallel_size=tensor_parallel_size,
        )

    def generate(self, prompts: list[str], max_tokens: int = 512,
                 temperature: float = 0.7, top_p: float = 0.95) -> list[str]:
        params = SamplingParams(max_tokens=max_tokens, temperature=temperature, top_p=top_p)
        BATCH_SIZE.labels(model=self.model).observe(len(prompts))
        start = time.time()
        outputs = self.llm.generate(prompts, params)
        latency = time.time() - start
        GENERATION_LATENCY.labels(model=self.model).observe(latency)
        return [o.outputs[0].text for o in outputs]

    def warmup(self, prompt: str = "Hello", repeats: int = 3):
        """Warm up CUDA graphs before serving traffic."""
        for _ in range(repeats):
            self.generate([prompt], max_tokens=10, temperature=0)
        print(f"vLLM warmup complete for {self.model}")
