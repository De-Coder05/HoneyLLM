# Mirror Maze decoy — isolated container image (Phase 3, Step 3.1).
# Contains ONLY the decoy service + the persona + the synthetic bait. No
# production/backend code, so the isolation boundary is also a code boundary.
FROM python:3.12-slim

WORKDIR /app

# Non-root user — the decoy processes attacker-influenced input; do not run as root.
RUN useradd --create-home --uid 10001 decoy

COPY sandbox/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY sandbox/decoy_service.py /app/decoy_service.py
COPY sandbox/persona/ /app/persona/
# Only the source-of-truth doc is copied; the service reads just its INTERNAL
# (synthetic bait) block. All values are non-functional (rules.md §2).
COPY data/nextel_source_of_truth.md /app/data/nextel_source_of_truth.md

USER decoy
EXPOSE 9100
CMD ["uvicorn", "decoy_service:app", "--host", "0.0.0.0", "--port", "9100"]
