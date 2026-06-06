# TurboServe Error Log

## [ERR-001] vLLM CUDA graph capture OOM on first request
**Date:** 2024-03-05 | **Severity:** High | **Status:** Resolved

**Description:** First request after startup caused CUDA OOM during graph capture phase.
**Root Cause:** `gpu_memory_utilization=0.95` left insufficient memory for CUDA graph capture overhead.
**Fix:** Set `gpu_memory_utilization=0.90`. Added warm-up call at startup.
**Impact:** Zero OOM events in 10,000+ subsequent requests.

---

## [ERR-002] HPA queue depth metric not found
**Date:** 2024-03-22 | **Severity:** Medium | **Status:** Resolved

**Description:** HPA failed to scale on queue_depth custom metric — `unable to fetch metrics` error.
**Root Cause:** Prometheus adapter ConfigMap metric selector did not match gauge name (underscore vs hyphen).
**Fix:** Updated adapter config to use exact metric name `turboserve_queue_depth`.
**Impact:** Autoscaling works correctly, scales to 8 pods in < 90s under load.

---

## [ERR-003] Streaming SSE connection drops after 30s
**Date:** 2024-04-14 | **Severity:** Medium | **Status:** Resolved

**Description:** Long streaming completions dropped after exactly 30s — client received incomplete output.
**Root Cause:** AWS ALB idle timeout default of 30s terminated long-lived SSE connections.
**Fix:** Set ALB idle_timeout to 300s via Terraform annotation on the K8s service.
**Impact:** Streaming connections stable for full duration (tested to 8 min for 4096-token outputs).
