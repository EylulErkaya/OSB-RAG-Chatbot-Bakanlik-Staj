from src.retrieval.retrieval_pipeline import retrieve
from src.generation.context_builder import ContextBuilder
from src.generation.prompt_builder import PromptBuilder
from src.generation.answer_generator import AnswerGenerator


context_builder = ContextBuilder()
prompt_builder = PromptBuilder()
answer_generator = AnswerGenerator()


queries = [
    "Malatya-Güney OSB'de kaç boş parsel var?",
    "Malatya-Güney OSB'de kaç fabrika üretim yapıyor?",
    "Malatya-Güney OSB'de kaç kişi istihdam ediliyor?",
    "Malatya-Güney OSB hangi bölgede bulunuyor?",
    "Malatya-Güney OSB'de gıda sektöründe kaç kişi çalışıyor?",
]


print("=" * 70)
print("END-TO-END RAG TESTİ")
print("=" * 70)


for query in queries:

    print("\n" + "=" * 70)
    print(f"SORU: {query}")
    print("=" * 70)

    retrieval_result = retrieve(
        query=query
    )

    print(
        f"\n[1] Retrieval: "
        f"{retrieval_result.get('status')}"
    )

    context_result = context_builder.build(
        retrieval_result
    )

    print(
        f"[2] Context: "
        f"{context_result.get('status')}"
    )

    prompt_result = prompt_builder.build(
        query=query,
        context_result=context_result,
    )

    print(
        f"[3] Prompt: "
        f"{prompt_result.get('status')}"
    )

    print(
        f"    LLM allowed: "
        f"{prompt_result.get('llm_allowed')}"
    )

    answer_result = answer_generator.generate(
        prompt_result
    )

    print(
        f"[4] Generation: "
        f"{answer_result.get('status')}"
    )

    print(
        f"\nCEVAP:\n"
        f"{answer_result.get('answer')}"
    )


print("\n" + "=" * 70)
print("END-TO-END TEST TAMAMLANDI")
print("=" * 70)