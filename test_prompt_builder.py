from src.retrieval.retrieval_pipeline import retrieve
from src.generation.context_builder import ContextBuilder
from src.generation.prompt_builder import PromptBuilder


# ============================================================
# NESNELER
# ============================================================

context_builder = ContextBuilder()
prompt_builder = PromptBuilder()


# ============================================================
# TEST SORUSU
# ============================================================

query = (
    "Malatya-Güney OSB'de kaç boş parsel var?"
)


print("=" * 70)
print("PROMPT BUILDER TESTİ")
print("=" * 70)


# ============================================================
# 1. RETRIEVAL
# ============================================================

retrieval_result = retrieve(
    query=query
)

print(
    f"\nRetrieval status: "
    f"{retrieval_result.get('status')}"
)


# ============================================================
# 2. CONTEXT BUILDER
# ============================================================

context_result = context_builder.build(
    retrieval_result
)

print(
    f"Context status: "
    f"{context_result.get('status')}"
)


# ============================================================
# 3. PROMPT BUILDER
# ============================================================

prompt_result = prompt_builder.build(
    query=query,
    context_result=context_result,
)

print(
    f"Prompt status: "
    f"{prompt_result.get('status')}"
)

print(
    f"LLM allowed: "
    f"{prompt_result.get('llm_allowed')}"
)


# ============================================================
# 4. SYSTEM PROMPT
# ============================================================

print("\n" + "=" * 70)
print("SYSTEM PROMPT")
print("=" * 70)

print(
    prompt_result.get(
        "system_prompt",
        ""
    )
)


# ============================================================
# 5. USER PROMPT
# ============================================================

print("\n" + "=" * 70)
print("USER PROMPT")
print("=" * 70)

print(
    prompt_result.get(
        "user_prompt",
        ""
    )
)


print("\n" + "=" * 70)
print("TEST TAMAMLANDI")
print("=" * 70)