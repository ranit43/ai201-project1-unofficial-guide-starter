# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

My domain is student-facing knowledge about UCLA dining halls and on-campus eateries, especially the practical details students care about: which dining halls are best for different diets, when lines get bad, how meal plans work, and which locations are reliable. This information is valuable because official UCLA Dining pages list menus and policies, but they do not fully capture student opinions, wait-time patterns, tradeoffs between locations, or operational issues like strikes, mobile-ordering delays, pest concerns, and overcrowding.

---

## Documents

| #   | Source                                                                                     | Description                                                                                                                                                    | URL or location                                                                                                                                                                                          |
| --- | ------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Daily Bruin - "Bruin 101: Dining"                                                          | Podcast transcript where UCLA students explain meal plans and review dining halls, takeout locations, food trucks, and favorites.                              | `documents/ucla-dining-hall/ucla-cld/01_dailybruin_bruin101_dining_podcast.txt`; https://dailybruin.com/2022/09/17/bruin101-dining                                                                       |
| 2   | Daily Bruin - "The Quad: Bruins savor taste of UCLA's No. 1-ranked dining hall food"       | Student opinions about UCLA's highly ranked dining, including Bruin Plate, Epicuria, atmosphere, and variety.                                                  | `documents/ucla-dining-hall/ucla-cld/02_dailybruin_no1_ranked_dining.txt`; https://dailybruin.com/2021/10/24/the-quad-bruins-savor-taste-of-uclas-no-1-ranked-dining-hall-food                           |
| 3   | Daily Bruin Stack - "Can students eat healthy at UCLA's dining halls?"                     | Nutrition-focused article about whether students can eat healthy at UCLA dining halls, with discussion of Bruin Plate, De Neve, Epicuria, and student choices. | `documents/ucla-dining-hall/ucla-cld/03_dailybruin_healthy_eating_dining_halls.txt`; https://dailybruin.com/2026/01/31/can-students-eat-healthy-at-uclas-dining-halls                                    |
| 4   | Daily Bruin - "From schedule changes to strikes, students discuss UCLA Dining experiences" | Student experiences with 2024-2025 dining challenges, including long food truck lines, mobile-ordering delays, strikes, and modified dining options.           | `documents/ucla-dining-hall/ucla-cld/04_dailybruin_schedule_changes_strikes.txt`; https://dailybruin.com/2025/06/08/from-schedule-changes-to-strikes-students-discuss-ucla-dining-experiences            |
| 5   | Daily Bruin - pest control investigation                                                   | Investigation about pest-control budgeting and a rat infestation that affected UCLA residential dining halls.                                                  | `documents/ucla-dining-hall/ucla-cld/05_dailybruin_pest_control_investigation.txt`; https://dailybruin.com/2026/01/16/investigation-reveals-ucla-dining-cut-pest-control-budget-ahead-of-rat-infestation |
| 6   | Daily Bruin - curated dining hall playlists                                                | Article about music and atmosphere in dining halls, especially Bruin Plate and Epicuria.                                                                       | `documents/ucla-dining-hall/ucla-cld/06_dailybruin_music_dining_halls.txt`; https://dailybruin.com/2026/01/30/music-tuned-to-shape-ucla-dining-hall-experiences-through-curated-playlists                |
| 7   | BruinLife - "A look into on-campus dining"                                                 | Student blog guide with ratings and practical summaries for UCLA dining halls and takeout locations.                                                           | `documents/ucla-dining-hall/ucla-cld/07_bruinlife_oncampus_dining_guide.txt`; https://bruinlife.com/a-look-into-on-campus-dining/                                                                        |
| 8   | The Stack - "UCLA's most popular dining halls"                                             | Data journalism article using swipe counts to describe popularity, traffic, peak times, and wait-time patterns.                                                | `documents/ucla-dining-hall/ucla-cld/08_stack_dining_popularity_analysis.txt`; https://stack.dailybruin.com/2022/02/17/dining-halls/                                                                     |
| 9   | Wanderlog - Bruin Plate reviews                                                            | Aggregated visitor/student review text focused on Bruin Plate's healthy food, freshness, crowding, and access rules.                                           | `documents/ucla-dining-hall/ucla-cld/09_wanderlog_bruin_plate_reviews.txt`; https://wanderlog.com/place/details/524688                                                                                   |
| 10  | Substack - "UCLA's dining halls, authoritatively ranked"                                   | Opinionated student ranking of UCLA dining halls and takeout spots, with specific praise and criticism.                                                        | `documents/ucla-dining-hall/ucla-cld/10_substack_authoritative_rankings.txt`; https://thefoodconnoisseur.substack.com/p/ranking-uclas-dining-halls                                                       |
| 11  | UCLA Alumni - "Campus Eats: Dining Choices Across UCLA"                                    | Alumni newsletter page with short descriptions and student quotes about Hill, North Campus, South Campus, and Central Campus eateries.                         | `documents/ucla-dining-hall/ucla-cld/11_alumni_campus_eats_student_reviews.txt`; https://newsletter.alumni.ucla.edu/connect/2022/april/campus-eats/default.html                                          |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ.

     TODO: Fill this in when starting Milestone 2. -->

**Chunk size:** I will use recursive, structure-aware chunks of about 900-1200 characters each. The chunker will try to keep natural paragraphs or speaker turns together first, then split oversized sections by sentence, then by spaces only as a fallback. I will avoid splitting in the middle of a sentence or separating a dining location name from the opinion or detail attached to it.

**Overlap:** I will use about 150-200 characters of overlap between adjacent chunks when a document section has to be split. This should preserve context when a useful fact spans two nearby paragraphs, such as a dining hall name in one sentence and the student's reason or complaint in the next.

**Reasoning:** The UCLA dining corpus is mixed: one long podcast transcript, several short news/blog articles, rankings, reviews, and a data-focused article about swipe counts and wait times. A fixed-size character split could cut podcast dialogue or article paragraphs in half, while very large chunks would mix unrelated topics like meal plans, Bruin Plate, De Neve, The Study, food trucks, and pest concerns. Following the lecture's guidance, the goal is a chunk that is just large enough to answer a student question on its own, but small enough that retrieval returns a focused piece of evidence. This strategy should work well for questions about specific dining halls, dietary restrictions, peak wait times, atmosphere, reliability, and operational issues.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency?

     TODO: Fill this in before building retrieval. -->

**Embedding model:** I will use `sentence-transformers/all-MiniLM-L6-v2` through the `sentence-transformers` library. This matches the recommended project setup, runs locally without an API key, and is strong enough for semantic search over short student-facing articles, reviews, and podcast transcript chunks. I will store the resulting vectors in ChromaDB with metadata for the source document, source URL, title, and chunk position so retrieved evidence can be cited later.

**Query approach:** The retrieval function will call ChromaDB's `collection.query()` with `query_texts=[query]`, `n_results=5`, and `include=["documents", "metadatas", "distances"]`. Because ChromaDB returns nested lists to support batched queries, I will read from index `[0]` to get the documents, metadata, and distances for the single user query. Each returned result will include the chunk text, source title or file path, source URL, chunk position, and distance score.

**Top-k:** I will retrieve the top 5 chunks for each query. This should give the answer generator enough context to compare multiple student opinions or sources, while still keeping the prompt focused. During evaluation, I will inspect the returned distance scores and relevance of each chunk. If weak or off-topic chunks consistently appear in the top 5, I may add a cosine-distance threshold so the generator does not receive irrelevant context.

**Production tradeoff reflection:** For this class project, a local MiniLM model is a good fit because it is free, fast, private, and simple to run.
In a production version, I would compare it against stronger embedding models that may better handle slang, nicknames, exact dining-location names, and messy student language.
I would weigh retrieval accuracy against latency, cost, context length, and whether the model is local or API-hosted. I would also consider hybrid search where keyword matching can help semantic search avoid missing the right source.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable.

     TODO: Fill this in after skimming the UCLA sources more closely and before implementation. -->

| #   | Question                                                                                                                 | Expected answer                                                                                                                                                                                                                                                                                                                                                                                                     |
| --- | ------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | What do students and reviewers say makes Bruin Plate a good option for healthy eating or dietary restrictions?           | The answer should mention that Bruin Plate/B-Plate is repeatedly described as health-focused, with fresh ingredients, salad/fruit options, balanced nutrition standards, and student praise for protein/healthy food. It should also mention that students with dietary restrictions describe B-Plate as easier to navigate, including references to vegetarian options and a gluten-free pantry.                   |
| 2   | How do UCLA meal plan types differ between Regular (R) and Premium (P), according to the Bruin 101 podcast?              | The answer should state that meal plans combine a number of meals per week, such as 11, 14, or 19, with a type, Regular or Premium. Regular plans allow one swipe per meal period and unused swipes do not carry over each week. Premium plans give swipes at the beginning of the quarter, allow multiple swipes in a meal period, and can be used through finals week.                                            |
| 3   | When are UCLA dining halls and quick-service/takeout locations usually busiest, according to The Stack's swipe analysis? | The answer should state that residential dining halls are busiest at dinner, generally peaking between 6 p.m. and 7 p.m., with De Neve's busiest period around 7 p.m. to 7:30 p.m. on Sundays. Quick-service/takeout locations usually peak around weekday lunch, especially between 11 a.m. and 12 p.m.; The Study stays busy across lunch and dinner and peaks around 9 a.m. for weekday breakfast.               |
| 4   | What recent UCLA Dining problems did students report around schedule changes, strikes, mobile ordering, and food trucks? | The answer should mention long food truck lines, mobile-ordering wait times up to two hours or temporary shutdowns of Transact Mobile Ordering, restricted ASUCLA meal-swipe hours, and dining-worker strikes that limited options or shifted dining halls such as De Neve, Feast, and Epicuria to takeout models.                                                                                                  |
| 5   | What do the sources say about The Study at Hedrick as a dining option?                                                   | The answer should mention that The Study is known for customizable sandwiches, salads, pizzas, breakfast items, extended/late-night dinner, and a study-friendly atmosphere. It should also capture the tradeoff: students describe the food as consistent or worth it, but lines and waits can be very long, with examples of waits over an hour or even around two hours.                                         |
| 6   | How much does a 14P meal plan cost in dollars per quarter?                                                               | This is an out-of-scope / abstention test. The corpus discusses how meal plans work (meal counts, R vs P, switching fees) but never states a dollar price for any plan. A correct system should say it does not have that information in the provided sources rather than inventing a number. This checks that the generator abstains instead of hallucinating when the retrieved chunks do not contain the answer. |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries.

     TODO: Fill this in when making implementation decisions. -->

1. **Chunks may split a useful dining-hall opinion away from its context.** The podcast transcript moves quickly from one location to another, and a speaker may name a dining hall in one sentence and explain the reason in the next. If the chunker splits those apart, retrieval might return a fragment like "I don't like De Neve" without the details about heaviness, distance, gluten-free pantry concerns, or vegetarian options.

2. **Similar dining terms could cause off-target retrieval.** Many documents mention overlapping ideas like "healthy," "popular," "long lines," "meal swipes," and "takeout." A query about The Study's wait times could accidentally retrieve general wait-time chunks from The Stack, food truck lines, or B-Caf online ordering unless chunks preserve location names and metadata clearly.

3. **Student opinion sources may disagree or vary in tone.** Some sources praise B-Plate as healthy and reliable, while others describe it as controversial or bland. The generator needs to summarize tradeoffs rather than flatten disagreement into one confident ranking.
   My thought is "the generation prompt should instruct the model to attribute and compare ("some students say... while others...") rather than pick a winner."

4. **The system may be tempted to answer beyond the documents.** Questions about current prices, today's menus, exact hours, or live wait times may not be answered by the collected sources. The generation prompt and evaluation should check that the system abstains when the retrieved chunks do not contain the answer, instead of inventing facts from general knowledge.

5. **The embedding model silently truncates long chunks.** `all-MiniLM-L6-v2` has a 256-token max sequence length and truncates anything longer. My planned 900-1200 character chunks are roughly 225-300 tokens, so the larger chunks (especially after adding overlap) can exceed the limit, meaning the tail of a chunk is never embedded even though it is stored and shown as a citation.
   This can cause "the text is right there but retrieval missed it" failures. Mitigation: measure token counts during chunking and either cap chunk size closer to ~256 tokens or accept the limit knowingly.

6. **Stale and conflicting information across a multi-year corpus.** Sources span 2021 to 2026 (rankings, strikes, the 2024-2025 schedule changes, the rat-infestation investigation). A dining hall's reputation, hours, or operating model may have changed between sources, so two retrieved chunks can contradict each other for reasons of _time_, not just opinion. Without publication dates in the metadata and in the prompt, the generator may blend outdated and current facts.
   Possible Mitigation is to store the source date in metadata and ask the generator to note when a claim is time-bound.

7. **A small corpus plus top-k=5 can return redundant or thin evidence.** With only 11 documents, popular topics (B-Plate, meal swipes) are over-represented while narrow topics (pest control, music/playlists) appear in just one source. Retrieval may return five near-duplicate chunks from the same article — inflating apparent agreement — or, for a narrow query, pad the top-5 with weak off-topic chunks. My planned distance threshold helps the second case; for the first, we can consider deduplicating by source or noting source diversity when judging answers.

8. **Citation/attribution mismatch.** Because chunks are embedded as plain text but cited via metadata, any bug that misaligns a chunk's text with its `source`/`url`/`position` metadata will produce confident answers with wrong citations — arguably worse than abstaining.
   Possible Mitigation is to spot-check that retrieved chunk text actually appears in the cited source file during evaluation.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage.

     TODO: Fill this in after choosing the implementation stack. -->

This project will use a RAG pipeline with five main stages:

```
User question
    |
    v
[1] DOCUMENT INGESTION       -> Load UCLA dining .txt files from documents/ucla-dining-hall/ucla-cld
    Python file loader          Keep source document, source URL, title, and chunk position metadata
    |
    v
[2] CHUNKING                 -> Split documents into focused, retrievable pieces
    Recursive chunker           Paragraphs/speaker turns first, sentences as fallback
    |                           Target: ~225-256 tokens (900-1200 chars),
    |                           ~40-50 token (150-200 char) overlap, capped at the
    |                           256-token MiniLM limit
    v
[3] EMBEDDING + VECTOR STORE -> Embed chunks and store them with metadata
    all-MiniLM-L6-v2             sentence-transformers for embeddings
    ChromaDB                     ChromaDB for local similarity search
    |
    v
[4] RETRIEVAL                -> Embed the user question and retrieve top matches
    ChromaDB query               top-k = 5 chunks, ranked by semantic similarity
                                Pin the same MiniLM embedding function for indexing
                                and query so vectors are comparable
    |
    v
[5] GENERATION               -> Build a grounded prompt from retrieved chunks
    Groq LLM                     Answer using only retrieved context
                                Include source names/URLs in the final response
```

The most important data flow is the chunk metadata. Each chunk should stay attached to its source file, source URL, title, and chunk position from ingestion through retrieval. That metadata is what makes citation possible in the final answer.

Technical decisions:

- **Documents:** Plain `.txt` files already collected in the UCLA dining corpus.
- **Chunking:** Recursive, structure-aware splitting because the corpus mixes podcast dialogue, student reviews, rankings, and news-style articles.
- **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2` because it runs locally and matches the recommended project setup.
- **Vector store:** ChromaDB because it supports local semantic search and can store chunk metadata. Indexing and querying must use the same MiniLM embedding function so the stored vectors and query vector live in the same space.
- **Retrieval:** Start with `top-k = 5` to balance enough context against prompt noise.
- **Generation:** Groq LLM with a grounding instruction that tells the model to answer only from retrieved chunks and abstain when the answer is not present.
  (Optional) This abstention behavior is what evaluation question 6 is designed to test.

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     TODO: Fill this in when moving into Milestone 2. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
