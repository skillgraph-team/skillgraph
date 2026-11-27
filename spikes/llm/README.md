# LLM spike (M2.1)

Throwaway code that compares free LLMs on 5 made-up profiles. It is not part of the app: the real LLM client is `backend/app/llm` (M2.2). Method, results and how to run it: `docs/spikes/llm.md`.

- `profiles.py`: the 5 profiles and the reference answers a person would give.
- `run_spike.py`: asks one provider (`groq`, `gemini`, `ollama`, or `fake` for an offline check) and saves every answer to `results/`.
- `score.py`: turns the saved answers into the comparison tables.
- `test_score.py`: checks the scorer (`uv run --project backend pytest spikes/llm -p no:cacheprovider --rootdir spikes/llm`).

Standard library only; any Python 3.12+ runs it.
