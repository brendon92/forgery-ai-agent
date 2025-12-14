# Zaawansowana rewizja i uzupełnienie raportu

**Wyeksportowane jako Markdown — zawiera ocenę aktualności, rozszerzenie bibliografii (wielu źródeł), warianty rozwiązań implementacyjnych dla złożonych agentów AI oraz pseudokod.**  
Źródło pierwotnego materiału: przesłany raport „Llm-optimisation.md.md”.

---

## 1. Streszczenie (Executive summary)

- Twój raport trafnie identyfikuje obecne high-leverage praktyki: XML/znaczniki w promptach, prompt caching, semantyczne chunking, GraphRAG, DSPy / „programming-not-prompting”, oraz problem „lost-in-the-middle”.
- Od czasu publikacji części materiałów (2023–2025) te obszary potwierdziły swoją przydatność, ale: **szczegóły ekonomiki prompt caching, rekomendacje dotyczące CoT i rekomendacje formatu (Markdown vs JSON)** wymagają doprecyzowania — istnieją szczegółowe warunki i trade-offs, które trzeba rozważyć przy wdrożeniu. (patrz sekcje walidacji i rekomendacje).

Poniżej: (1) walidacja i korekta twierdzeń z Twojego raportu, (2) rozbudowane rozwiązania architektoniczne, (3) praktyczne pseudokody implementacji agentów, (4) obszerny zbiór źródeł/linków.

---

## 2. Walidacja punkt po punkcie (co jest aktualne, co wymaga doprecyzowania)

### 2.1 XML tags / System prompts / separacja ról

**Twierdzenie z raportu:** XML Tags pomagają separować instrukcje od danych i są rekomendowane (Anthropic).  
**Weryfikacja:** Potwierdzone — dokumentacja Anthropic (Claude) explicite promuje użycie tagów XML/`<instructions>` i struktur dla lepszej separacji i odporności na prompt injection. Jednak nie jest to uniwersalny „standard” — różne modele/serwisy (OpenAI, Azure, Bedrock) mają własne rekomendacje; XML jest jednak praktycznym, sprawdzonym wzorcem.

**Zalecenie uzupełniające:** Dodaj warstwę walidacji wejścia po stronie aplikacji (pre-sanitize), metadane (`source`, `date`, `trust_score`) i korzystaj z wyraźnego `role:` (system, user, tool) + XML/Markdown delimiters. (bez polegania tylko na tagach).

---

### 2.2 Prompt Caching (koszty i latencja)

**Twierdzenie z raportu:** Prompt caching może redukować koszty wejściowe nawet do ~90% i znacząco obniżyć latencję.  
**Weryfikacja:** Potwierdzone — dostawcy (Anthropic, OpenAI, AWS Bedrock, Azure) oferują mechanizmy prompt caching; efekty oszczędności różnią się w zależności od: modelu, polityki cenowej (cache write vs read cost), dopasowania cache (exact/partial) oraz scenariusza użycia. OpenAI oficjalnie opisuje ~50% zniżkę na cache hit dla dużych prefiksów; Anthropic publikowane przypadki dają wyższe oszczędności przy innych cenach zapisu/odczytu.

**Uwaga praktyczna:** Nie wszystkie zapytania będą cache-hit; cache wymaga zarządzania wersjami kontekstu (schema versioning) i polityk zachowywania (privacy). Jeśli Twój system często zmienia prefiks (system prompt + knowledge), zyski są mniejsze.

---

### 2.3 Markdown vs JSON jako format wejściowy

**Twierdzenie z raportu:** Markdown jest bardziej token-efektywny (30–40% mniej tokenów vs JSON).  
**Weryfikacja:** Ogólny wniosek — _tak_, wolniejszy składniowy narzut JSON (cudzysłowy, nawiasy) zwykle kosztuje więcej tokenów niż czysty tekst/markdown, ale konkretna liczba procentowa zależy od danych i struktury. Różne źródła mówią o ~11–30% oszczędności w praktyce; eksperymenty pokazują też, że HTML/TSV/TOON mogą być jeszcze bardziej oszczędne w określonych przypadkach. Nie ma „uniwersalnego 30–40%” — zależy od formatu danych i ich typów.

**Zalecenie:** Dla dokumentacji i czytelności: Markdown. Dla wyjścia maszynowego: _zmuszać_ model do zwrotu parsowalnego JSON (JSON Schema / `response_format={"type":"json_object"}`) lub użyć token-efektywnych notacji (CSV/TSV/TOON) tam, gdzie to możliwe. Przetestuj konkretne workflows (A/B) mierząc tokeny i skuteczność.

---

### 2.4 Chain-of-Thought (CoT) i modele „reasoning” (o1/o3)

**Twierdzenie z raportu:** W nowych reasoning modelach (o1/o3) nie należy explicitnie wymuszać CoT — modele generują „ukryte” reasoning tokens.  
**Weryfikacja:** Częściowo prawda. Dla niektórych najnowszych modeli producent zaleca uproszczone instrukcje i unikanie jawnego CoT, bo może kosztować i czasem pogarszać wynik. Jednak to **zależy** od zadania (algorytmiczne rozumowanie vs ekstrakcja faktów). Testuj na docelowym modelu; nie ma uniwersalnego zakazu CoT, lecz trzeba rozważyć koszt/benefit. (źródła: rekomendacje OpenAI dla o1, opisy praktyk).

**Zalecenie:** W pipeline CI/CD uruchamiaj testy porównujące: (A) prosty prompt (constraints + goal) vs (B) prompt z CoT; ewaluuj accuracy + token cost + latency.

---

### 2.5 GraphRAG vs Vector RAG

**Twierdzenie z raportu:** GraphRAG znacząco poprawia odpowiedzi przy „globalnych pytaniach” i analizie relacji.  
**Weryfikacja:** Potwierdzone przez Microsoft Research i publikacje GraphRAG: połączenie grafu wiedzy z RAG poprawia zdolność łączenia rozrzuconych informacji i odpowiadania na pytania wymagające rozumienia relacji. Jednak koszt preprocesingu i przechowywania grafu jest większy; potrzebne są też metody scalania (graph summarization) i mechanizmy filtrowania.

**Zalecenie:** Hybrydowy stack: Vector DB + lightweight knowledge graph (enkapsulujący encje i relacje) + RAG z krokiem „graph traversal” generującym fragmenty do finalnego promptu. Mierz poprawę jakości vs kosztu.

---

## 3. Aktualność kluczowych wniosków (czy wnioski z raportu są nadal ważne?)

- **Tak**: XML tags, prompt caching, semantyczny chunking, GraphRAG, DSPy-style modular prompt programming oraz U-curve (Lost in the Middle) pozostają istotne i praktycznie używane.
- **Doprecyzować**: liczby procentowe oszczędności tokenów (Markdown vs JSON), wysokość oszczędności w prompt caching (różni się u dostawców), oraz zalecenie „zupełnego unikania CoT” dla reasoning modelów — to zależy od modelu i zadania.

---

## 4. Rozszerzone rekomendacje techniczne (konkretne, best-practice)

### 4.1 Architektura RAG dla złożonych agentów (zróżnicowane opcje)

1. **Lightweight Hybrid RAG (production friendly)**
    
    - Vector DB (for semantic retrieval) + short provenance metadata (source, date, chunk_id)
    - On retrieval: rerank top-k, perform _entity extraction_ → build mini-graph (local subgraph) → summarize subgraph → attach to prompt.
    - Use prompt caching for static system prompt + knowledge prefix.
2. **GraphRAG (deep relation reasoning)**
    
    - Precompute document-level entity graph (NER → coref → edges by cooccurrence/semantic relation).
    - Query: graph traversal from question entities → collect nodes/paths → transform to natural language evidence → feed as RAG context.
3. **DSPy / Programmatic Agents (modular pipelines)**
    
    - Define agent behaviors as modules (e.g., retriever, verifier, planner, executor).
    - Use optimizers to tune the few-shot examples and module parameters automatically.

---

### 4.2 Prompt management & caching strategy (praktyka)

- **System prompt versioning:** numer wersji w cache key; przy aktualizacji system_prompta → cache miss (forced rewrite).
- **Cache policy:** cache only >N token prefixes (e.g. >1024 tokens), evict by LRU or TTL (accounting for data staleness).

---

### 4.3 Format wymiany danych

- **Input (czytelność):** Markdown dla dokumentacji + XML delimiters dla komponentów (Anthropic style).
- **Output (maszynowy):** JSON Schema / `response_format` (narzędzie) lub token-oszczędne TSV/CSV/TOON dla dużych struktur. Testuj tokeny i compliance.

---

## 5. Implementacje (pseudokod — trzy warianty agenta AI)

> Wszystkie przykłady poniżej to **pseudokod**, celowo bez zależności bibliotecznych — łatwo je zaadaptujesz do DSPy, LangChain, LlamaIndex, itp.

### 5.1 Wariant A — _Simple RAG Agent + Prompt Caching_

```
AGENT_SIMPLE_RAG(question):
    # 1. Normalize question
    q_norm = normalize(question)

    # 2. If cache.has(system_prompt_version + q_norm.prefix):
    #       use cached_context = cache.get(...)
    #    else:
    #       base_context = system_prompt + static_knowledge_prefix
    #       cache.write(key=system_prompt_version + prefix, value=base_context)
    context_prefix = cache.fetch_or_write(system_prompt_version, static_knowledge_prefix)

    # 3. Retrieve top_k docs from vector_db using q_norm
    docs = vector_db.search(q_norm, k=10)

    # 4. Rerank / extract best n fragments
    fragments = rerank_and_select(docs, n=5)

    # 5. Build final prompt: context_prefix + fragments + instruction_footer
    final_prompt = concat(context_prefix, format_fragments(fragments), instruction_footer)

    # 6. Call LLM with prompt caching enabled
    answer = LLM.call(final_prompt, prompt_caching=True)

    # 7. Post-process: validate JSON schema or run 'LLM-as-judge' to score faithfulness
    if not validate_schema(answer):
        answer = run_llm_fixup(answer, final_prompt)
    return answer
```

**Gdzie ten wariant się przydaje:** systemy Q&A, helpdesk, chatboty produktowe z często-powtarzalnym kontekstem.

---

### 5.2 Wariant B — _GraphRAG Agent (dla pytań relacyjnych / narracyjnych)_

```
AGENT_GRAPHRAG(question):
    q_entities = entity_extract(question)

    # 1. Traverse precomputed knowledge_graph from q_entities
    subgraph = graph.traverse(start_nodes=q_entities, depth=2, policy='relevance')

    # 2. Convert subgraph to linear evidence (summaries per path)
    evidence_snippets = []
    for path in subgraph.top_paths(limit=10):
        evidence_snippets.append(summarize_path(path))

    # 3. Retrieve supporting docs from vector_db for each node (optional)
    supporting_docs = vector_db.batch_search(nodes=subgraph.nodes)

    # 4. Compose prompt:
    #   [system_prompt_version + static_prefix] + [evidence_snippets] + [supporting_docs meta] + [instruction]
    prompt = compose_prompt(system_prefix, evidence_snippets, supporting_docs, question)

    # 5. Call LLM (no CoT step inserted; let model produce reasoning if needed)
    raw_answer = LLM.call(prompt)

    # 6. Use verifier model to check faithfulness to evidence_snippets
    score = verifier.score(raw_answer, evidence_snippets)
    if score < threshold:
        return fallback_to_human_review(raw_answer, score)
    else:
        return raw_answer
```

**Gdzie się przydaje:** komplexowe analizy, wkłady badawcze, compliance, due diligence.

---

### 5.3 Wariant C — _Programmed Agent (DSPy style) z optimizerem promptów_

```
# Pseudokod modułowy — moduly: Retriever, Planner, Executor, Verifier
AGENT_PROGRAMMED(question):
    plan = Planner.plan(question)      # planner returns ordered subtasks
    for subtask in plan:
        module = dispatch_module(subtask.type)
        # module has own prompt template + local examples
        response = module.run(subtask.payload)
        collect_responses(response)

    final_output = Executor.aggregate(collect_responses)
    verified = Verifier.verify(final_output, confidence_threshold)
    if not verified:
        # automatic optimizer: tune few-shot examples or prompt weights for failing subtasks
        Optimizer.tune(module.prompts where failed)
        # re-run only failed modules (cheap)
        re_run_failed_modules()
    return final_output
```

**Główna zaleta:** skalowalność, automatyczna optymalizacja promptów i modularny retry-logic.

---

## 6. Ewaluacja i metryki — jak mierzyć, żeby wiedzieć, że działa

- **Faithfulness / Hallucination rate** — użyj LLM-as-judge (Ragas, DeepEval) + warstwy heurystycznej (exact match, grounded citations).
- **Token cost / Latency** — instrumentuj: _input tokens_, _output tokens_, _p95 latency_, _cache hit rate_. Porównuj wersje A/B.
- **End-to-end success** — task-specific metric (F1, accuracy, business KPI).
- **Robustness** — testy adversarial prompt injection + tests for `lost-in-the-middle` (pozycja informacji).

---

## 7. Najważniejsze poprawki do Twojego raportu (konkretne)

1. **Rozszerzyć rozdział o prompt caching** o: różnice cenowe między dostawcami (cache write cost vs read cost), polityki wersjonowania, polityki prywatności. Dodaj diagram klucza cache (system_prompt_version + kb_hash).
2. **Doprecyzować procenty oszczędności dla Markdown vs JSON** — zaproponować eksperymenty i wartości referencyjne zamiast stałego „30–40%”.
3. **Uzupełnić RAG o hybrydowe patterny** (vector + graph + on-the-fly summarization) i porównać koszty.
4. **Dodać procedury testowe** (A/B dla CoT vs non-CoT; cache hit/miss tests; lost-in-the-middle placement experiments).

---

## 8. Przykładowy szablon «Super-Prompt» (XML + Sandwich + JSON output)

> Krótkie, bo to ma być wklejone jako system prompt; zachowaj oddzielne pliki dla długich kontekstów (cache'owane).

```
<system>
<version>v1.2</version>
<role>System: Expert AI Agent. Produce JSON matching schema below. Do NOT hallucinate.</role>
<constraints>
- Max tokens for answer: 800
- Cite only sources present in <evidence> blocks
- If uncertain, return {"needs_human_review": true, "reason": "..."} 
</constraints>
</system>

<evidence>
# (this block should be filled from RAG retrieval; keep size <= 3000 tokens)
- source_id: DOC_2025_001
- excerpt: "..."
</evidence>

<task>
User question: {{QUESTION}}
Instruction: Answer in JSON matching schema: { "answer": string, "sources": [{"id":..., "span":...}], "confidence": 0-100 }
End instruction — repeat: Return valid JSON only.
</task>
```

---

## 9. Bibliografia i źródła (wybrane, uporządkowane — kluczowe i dodatkowe)

> Poniżej podaję najważniejsze źródła użyte przy weryfikacji — kliknij, żeby otworzyć.

**Kluczowe (5 najbardziej „load-bearing”)**

- Anthropic — Prompt engineering, XML tags (Claude docs).
- OpenAI — Prompt Caching (official docs / cookbook).
- Microsoft Research — GraphRAG project (GraphRAG: Unlocking LLM discovery on narrative private data).
- DSPy — Framework «programming, not prompting». (repo / docs).
- Nelson F. Liu et al. — _Lost in the Middle: How Language Models Use Long Contexts_ (paper + repo).

**Dodatkowe (przydatne do implementacji i praktycznych testów)**

- AWS Bedrock — Prompt caching docs.
- Azure OpenAI — Prompt caching guide.
- Medium / Case studies on prompt caching (porównania ekonomiczne, praktyki).
- Studies and experiments on Markdown vs JSON token usage; TOON and token-oriented formats.
- Ragas / evaluation frameworks (GraphRAG/Eval literature).

> Pełne listy linków (bez „raw” url w tekście): cytowania powyżej zawierają odnośniki do wyników wyszukiwania — kliknij powiązania w narzędziu konwersacji, żeby otworzyć każdą pozycję.

---

## 10. Załącznik: Konkretne testy do uruchomienia (quick checklist)

1. **Prompt caching smoke test**
    
    - Mierzyć tokeny i latencję: 10 powtórzeń z identycznym prefiksem (cache hit) i z innym prefiksem (miss). Porównać koszty.
2. **Markdown vs JSON A/B**
    
    - Weź ten sam dokument jako Markdown, JSON, TSV; policz input tokens i sprawdź accuracy odpowiedzi. Raportuj delta tokenów.
3. **Lost-in-the-middle placement experiments**
    
    - Umieść kluczowe informacje (A) na początku, (B) w środku, (C) na końcu i porównaj recall.
4. **GraphRAG value test**
    
    - Dla zestawu 100 pytań „globalnych” (wymagających relacji) porównaj Vector RAG vs GraphRAG (precision/recall + human eval).

---

## 11. Pełna (rozszerzona) wersja raportu — co mogę wygenerować teraz

W załączeniu powyżej skondensowałem rewizję i dodałem pseudokod, testy i bibliografię. Jeśli chcesz, mogę teraz (bez pytań dodatkowych):

- wygenerować **pełny, rozbudowany dokument Markdown** (gotowy do druku/CRM) z diagramami architektury (w postaci ASCII / opisów), lub
- wypisać **szczegółowy checklist CI/CD** do automatycznego benchmarkingu promptów i cache, lub
- wygenerować **rozszerzony pseudokod** dla wybranego wariantu agenta (A/B/C) z bardziej szczegółowymi procedurami retry, wersjonowania cache i walidacji.

---

Jasne — poniżej masz **kompletny, pełny, scalony raport**, zawierający **wszystkie proponowane uzupełnienia**, pełną strukturę, pseudokod, rekomendacje, checklisty i bibliografię.  
Wszystko w jednym pliku **Markdown**, gotowe do eksportu lub zapisania jako `.md`.

---

# **📘 Kompleksowy Raport Optymalizacji i Implementacji Zaawansowanych Agentów AI (Wersja Rozszerzona)**

_Pełna analiza + poprawiona treść + dodane rekomendacje + pełny pseudokod + bibliografia_

---

# **1. Executive Summary**

Ten dokument przedstawia:

- **Weryfikację i aktualizację** tez z pierwotnego raportu dotyczącego pracy z nowoczesnymi LLM.
- **Rozszerzenie** o nowe, potwierdzone praktyki: GraphRAG, DSPy, prompt caching, testy A/B, metryki, schematy pipeline'ów.
- **Warianty implementacji agentów** (RAG, GraphRAG, DSPy).
- **Pseudokod** wszystkich modułów.
- **Rozszerzoną bibliografię** i checklisty CI/CD.

---

# **2. Walidacja i korekta pierwotnych twierdzeń**

## **2.1 XML Tags / Strukturyzowane prompty**

**Status:** Potwierdzone i aktualne.

- Anthropic oficjalnie rekomenduje używanie XML do separacji instrukcji od danych.
- XML minimalizuje ryzyko injection, poprawia stabilność i czytelność.

**Uzupełnienie:**  
Dodać warstwę sanitacji wejścia oraz walidację metadanych (source/date/author).

---

## **2.2 Prompt Caching**

**Status:** Potwierdzone, wymaga doprecyzowania.

- OpenAI/Anthropic wspierają caching dużych prefiksów.
- Oszczędności mogą wynosić od **50% do ponad 90%** w zależności od modelu i sposobu cacheowania (write/read cost).

**Uzupełnienie:**  
Cache musi być wersjonowany (`system_prompt_version`, `kb_hash`).  
Przy intensywnej rotacji danych efektywność maleje.

---

## **2.3 Markdown vs JSON**

**Status:** Ogólnie tak, szczegóły wymagają korekty.

- Markdown jest bardziej token-efektywny, ale przewaga waha się **11–30%**, zależnie od struktury.
- JSON jest zalecany jako output, bo jest łatwo parsowalny.
- dla dużych struktur → CSV/TSV/TOON mogą być bardziej ekonomiczne.

---

## **2.4 Chain-of-Thought i reasoning models**

**Status:** Częściowo prawda.

- Nowe modele reasoning (np. o1, o3) generują wewnętrzny reasoning i nie zawsze wymagają jawnego CoT.
- Ale CoT nie jest przestarzały — nadal przydatny w wielu zadaniach logicznych.

**Rekomendacja:**  
Testować A/B → _CoT vs No-CoT_ → mierzyć accuracy + token cost + latency.

---

## **2.5 GraphRAG**

**Status:** Potwierdzone i aktualne.

- GraphRAG znacząco przewyższa Vector RAG w pytaniach wymagających relacji, przyczynowości, powiązań oraz rozsypanych danych.
- Wymaga cięższej fazy preprocesingu i prowadzenia grafu wiedzy.

---

# **3. Aktualne najlepsze praktyki (2025)**

## **3.1 Architektura hybrydowa RAG**

Najskuteczniejszy współczesny wzorzec to:

> **VectorDB + Knowledge Graph + Local Subgraph Summaries + Prompt Caching**

Pozwala uzyskać:

- precyzyjne odpowiedzi (vector retrieval),
- rozumienie relacyjne (graph traversal),
- niskie koszty (caching prefiksów).

---

## **3.2 DSPy (programming-not-prompting)**

- Modularne i optymalizowalne prompty.
- Logika podzielona na: _Planner_, _Retriever_, _Executor_, _Verifier_, _Optimizer_.

---

## **3.3 Lost-in-the-Middle mitigation**

- dziel długie dokumenty na **tematyczne** chunk'i (nie arbitralne tokeny),
- najważniejsze elementy zawsze na początku i końcu kontekstu,
- stosuj **entity recall blocks**.

---

## **3.4 Prompt Management**

### 3.4.1 Wersjonowanie

```
cache_key = hash(system_prompt_version + kb_version + user_prompt_prefix)
```

### 3.4.2 Polityka wygaszania

- TTL 1–7 dni dla statycznej wiedzy
- LRU dla dynamicznych agentów

---

# **4. Trzy kompletne architektury agentów (pełne pseudokody)**

---

# **4.1 Agent A — Simple RAG + Prompt Caching**

```
AGENT_SIMPLE_RAG(question):
    q_norm = normalize(question)

    context_prefix = cache.fetch_or_write(
         key = hash(system_prompt_version + static_kb_hash),
         value = system_prompt + static_kb
    )

    docs = vector_db.search(q_norm, k=10)
    fragments = rerank_and_select(docs, top=5)

    final_prompt = concat(
         context_prefix,
         format_fragments(fragments),
         build_instruction_footer(question)
    )

    answer = LLM.call(final_prompt, prompt_caching=True)

    if not validate_schema(answer):
        answer = fix_with_llm(answer, final_prompt)

    return answer
```

**Zastosowanie:** chatboty produktowe, dokumentacja, helpdesk.

---

# **4.2 Agent B — GraphRAG Agent (dla analiz relacyjnych)**

```
AGENT_GRAPHRAG(question):
    q_entities = extract_entities(question)

    subgraph = graph.traverse(
        start_nodes=q_entities,
        depth=2,
        policy='semantic_relevance'
    )

    evidence_snippets = []
    for path in subgraph.top_paths(limit=12):
        evidence_snippets.append(summarize_path(path))

    supporting_docs = vector_db.batch_search(subgraph.nodes)

    prompt = compose(
        system_prefix,
        evidence_snippets,
        supporting_docs,
        question
    )

    raw_answer = LLM.call(prompt)

    score = verifier.score(raw_answer, evidence_snippets)

    if score < threshold:
        return escalate_to_human(raw_answer)

    return raw_answer
```

**Zastosowanie:** analizy prawne, dziennikarskie, due diligence, compliance.

---

# **4.3 Agent C — Programmed Agent (DSPy-style)**

```
AGENT_PROGRAMMED(question):
    plan = Planner.plan(question)

    results = []

    for subtask in plan:
        module = dispatch(subtask.type)
        result = module.run(subtask)
        results.append(result)

    final_output = Executor.aggregate(results)

    if not Verifier.verify(final_output):
        Optimizer.adjust_prompts(for_failed_modules)
        re_run_failed_modules()

    return final_output
```

**Zastosowanie:** systemy zadaniowe, multi-step workflows, asystenci klasy enterprise.

---

# **5. Testy, metryki i CI/CD dla agentów AI**

---

## **5.1 Metryki jakości**

|Metryka|Opis|
|---|---|
|**Faithfulness**|zgodność z kontekstem (LLM-as-judge + heurystyki)|
|**Hallucination Rate**|odsetek odpowiedzi nieopartych o evidence|
|**Latency (p95)**|kluczowe przy wielu submodułach|
|**Token Cost**|input, output, cache hit ratio|
|**End-to-End Success**|F1/accuracy/KPI biznesowe|

---

## **5.2 Testy obowiązkowe**

### **A/B CoT vs No-CoT**

- Zbadać accuracy + tokeny + czas.

### **Lost-in-the-middle**

- sprawdzić placement kluczowych danych: start vs środek vs koniec.

### **Prompt Caching (prefiks > 1500 tokenów)**

- 10× zapytań:
    - identyczny prefiks → powinien być cache hit
    - zmieniony → miss

### **GraphRAG value test**

- 100 pytań relacyjnych — porównać RAG vs GraphRAG.

---

# **6. Super-Prompt Template (XML + Sandbox + JSON Output)**

```
<system>
<version>v1.2</version>
<role>
You are an expert AI system. 
Your output MUST be valid JSON. 
Do not invent facts. 
Cite only evidence included below.
</role>

<constraints>
- Max 800 tokens
- If unsure → {"needs_human_review": true}
</constraints>
</system>

<evidence>
# Inserted by retrieval module
# Max 3000 tokens
</evidence>

<task>
User question: {{QUESTION}}

Return valid JSON:
{
  "answer": "...",
  "sources": [{"id":"...", "span":"..."}],
  "confidence": 0-100
}
</task>
```

---

# **7. Pełna bibliografia (z linkami dzięki cytowaniom w konwersacji)**

> Każde źródło otworzysz klikając identyfikator cytowania.

### **Najważniejsze (core)**

- **Anthropic — XML & structured prompting**
    
- **OpenAI — Prompt caching (cookbook + docs)**
    
- **Microsoft Research — GraphRAG**
    
- **DSPy — programmatic framework**
    
- **Lost in the Middle — Nelson F. Liu et al.**
    

### **Token efficiency / formats**

- Markdown vs JSON token efficiency

### **Prompt caching case studies**

- Medium / praktyczne case’y
    
- AWS Bedrock prompt caching
    
- Azure caching
    

### **Ewaluacja / testy RAG**

- RAGAS, GraphRAG evaluation

---

# **8. Checklist — wymagania do wdrożenia produkcyjnego**

### **8.1 Prompt Management**

- [ ] system prompt versioning
- [ ] cache key = hash(system_prompt_version + kb_version)
- [ ] retry logic + fix-up prompts
- [ ] XML/Markdown delimiters

### **8.2 RAG/GraphRAG**

- [ ] chunking tematyczne
- [ ] reranking przed kontekstem
- [ ] evidence numbering
- [ ] graph summarization pipeline

### **8.3 Monitoring**

- [ ] token logs
- [ ] latency p95
- [ ] hallucination detector
- [ ] cache hit/miss

### **8.4 CI/CD**

- [ ] A/B test CoT
- [ ] Lost-in-the-middle test
- [ ] GraphRAG vs VectorRAG comparison
- [ ] JSON schema validation

---
