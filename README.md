# The Unofficial Guide - Project 1

## Domain

This project covers student-facing knowledge about UCLA dining halls and on-campus eateries: dining hall tradeoffs, meal plan behavior, wait-time patterns, operational issues, and student opinions about places like Bruin Plate, De Neve, Epicuria, Rendezvous, The Study, and food trucks.

This knowledge is useful because official UCLA Dining pages can list menus, hours, and policies, but they do not capture the practical "what is it actually like?" layer students share with each other. The collected sources include student journalism, blogs, reviews, and data analysis, so the system can answer questions with grounded citations instead of relying on general model knowledge.

## Document Sources

| # | Source | Type | URL or file path |
| --- | --- | --- | --- |
| 1 | Daily Bruin - "Bruin 101: Dining" | Podcast transcript / student discussion | `documents/ucla-dining-hall/ucla-cld/01_dailybruin_bruin101_dining_podcast.txt`; https://dailybruin.com/2022/09/17/bruin101-dining |
| 2 | Daily Bruin - "The Quad: Bruins savor taste of UCLA's No. 1-ranked dining hall food" | Student news feature | `documents/ucla-dining-hall/ucla-cld/02_dailybruin_no1_ranked_dining.txt`; https://dailybruin.com/2021/10/24/the-quad-bruins-savor-taste-of-uclas-no-1-ranked-dining-hall-food |
| 3 | Daily Bruin Stack - "Can students eat healthy at UCLA's dining halls?" | Nutrition-focused article | `documents/ucla-dining-hall/ucla-cld/03_dailybruin_healthy_eating_dining_halls.txt`; https://dailybruin.com/2026/01/31/can-students-eat-healthy-at-uclas-dining-halls |
| 4 | Daily Bruin - "From schedule changes to strikes..." | Student experience / operations article | `documents/ucla-dining-hall/ucla-cld/04_dailybruin_schedule_changes_strikes.txt`; https://dailybruin.com/2025/06/08/from-schedule-changes-to-strikes-students-discuss-ucla-dining-experiences |
| 5 | Daily Bruin pest-control investigation | Investigation | `documents/ucla-dining-hall/ucla-cld/05_dailybruin_pest_control_investigation.txt`; https://dailybruin.com/2026/01/16/investigation-reveals-ucla-dining-cut-pest-control-budget-ahead-of-rat-infestation |
| 6 | Daily Bruin - curated dining hall playlists | Campus culture article | `documents/ucla-dining-hall/ucla-cld/06_dailybruin_music_dining_halls.txt`; https://dailybruin.com/2026/01/30/music-tuned-to-shape-ucla-dining-hall-experiences-through-curated-playlists |
| 7 | BruinLife - "A look into on-campus dining" | Student blog guide | `documents/ucla-dining-hall/ucla-cld/07_bruinlife_oncampus_dining_guide.txt`; https://bruinlife.com/a-look-into-on-campus-dining/ |
| 8 | The Stack - "UCLA's most popular dining halls" | Data journalism / swipe analysis | `documents/ucla-dining-hall/ucla-cld/08_stack_dining_popularity_analysis.txt`; https://stack.dailybruin.com/2022/02/17/dining-halls/ |
| 9 | Wanderlog - Bruin Plate reviews | Aggregated review text | `documents/ucla-dining-hall/ucla-cld/09_wanderlog_bruin_plate_reviews.txt`; https://wanderlog.com/place/details/524688 |
| 10 | Substack - "UCLA's dining halls, authoritatively ranked" | Opinion ranking | `documents/ucla-dining-hall/ucla-cld/10_substack_authoritative_rankings.txt`; https://thefoodconnoisseur.substack.com/p/ranking-uclas-dining-halls |
| 11 | UCLA Alumni - "Campus Eats: Dining Choices Across UCLA" | Alumni newsletter with student quotes | `documents/ucla-dining-hall/ucla-cld/11_alumni_campus_eats_student_reviews.txt`; https://newsletter.alumni.ucla.edu/connect/2022/april/campus-eats/default.html |

## Chunking Strategy

**Chunk size:** target 900 characters, max 1024 characters.

**Overlap:** 180 characters, preserved as whole trailing text units when possible.

**Preprocessing:** `ingest.py` parses source headers, extracts source metadata, unescapes HTML entities, normalizes whitespace, preserves paragraph breaks, and splits oversized paragraphs by sentence before merging units into chunks.

**Why these choices fit the documents:** The UCLA dining corpus mixes a long podcast transcript, news articles, student rankings, aggregated reviews, and a data-focused article about swipe counts. A purely fixed-size split could cut a speaker's dining hall opinion away from the reason behind it, while very large chunks would mix unrelated topics like meal plans, Bruin Plate, strikes, and food trucks. The current chunker tries to keep each chunk large enough to answer a focused question but small enough for precise semantic retrieval.

**Final chunk count:** 148 chunks.

## Sample Chunks

Generated with `python ingest.py --preview-count 5 --seed 7`.

| Chunk | Source | Excerpt |
| --- | --- | --- |
| `06_dailybruin_music_dining_halls_001` | Music tuned to shape UCLA dining hall experiences through curated playlists | Dining managers work with Gray V to curate playlists for dining periods. Epicuria managers curate playlists based on different languages, including Greek, Spanish, Italian, Arabic, and Persian sounds. |
| `01_dailybruin_bruin101_dining_podcast_038` | Bruin 101: Dining | A student worker asks students to treat staff well during staffing shortages, then explains that UCLA dining has variety but may not satisfy students looking for specific foods they eat at home. |
| `08_stack_dining_popularity_analysis_002` | UCLA's most popular dining halls | UCLA's dining options range from artisanal sandwiches at The Study to healthy entrees at Bruin Plate, while some students criticize the lack of halal options. |
| `01_dailybruin_bruin101_dining_podcast_012` | Bruin 101: Dining | Students discuss Epicuria's vegetarian options, pasta, build-your-own pasta bar, rice, soup, and then transition into why Bruin Plate is controversial but useful for some students. |
| `01_dailybruin_bruin101_dining_podcast_018` | Bruin 101: Dining | Students describe Rendezvous West as build-your-own Mexican food with long lines, reliable bowls, tacos, burritos, and customizable toppings. |

## Embedding Model

**Model used:** `sentence-transformers/all-MiniLM-L6-v2`, loaded through ChromaDB's `SentenceTransformerEmbeddingFunction`.

I chose this model because it runs locally, does not require an API key, and is fast enough for a small student-facing corpus. The index currently stores 148 chunks in a persistent ChromaDB collection named `unofficial-guide-chunks`.

**Production tradeoff reflection:** If I were choosing an embedding model for production, I would compare retrieval accuracy against latency, hosting cost, context length, privacy, and maintenance complexity. A stronger API-hosted embedding model might understand slang, nicknames, and messy student language better, but it would add cost and external dependency risk. A local model keeps the project simple and private, but may need keyword or hybrid search support for exact terms like `14P`, `Regular`, and `Premium`.

## Retrieval Test Results

**Index command:** `python retriever.py --rebuild-index --eval-smoke --top-k 5`

| Query | Top relevant chunks | Retrieval notes |
| --- | --- | --- |
| What makes Bruin Plate good for healthy eating or dietary restrictions? | `02_dailybruin_no1_ranked_dining.txt`, `09_wanderlog_bruin_plate_reviews.txt`, `03_dailybruin_healthy_eating_dining_halls.txt`, `01_dailybruin_bruin101_dining_podcast.txt` | Relevant. Top results mention nutrition standards, fresh/healthy options, B-Plate's healthy reputation, and a vegetarian student's experience. |
| How do Regular and Premium meal plans differ, according to Bruin 101? | `01_dailybruin_bruin101_dining_podcast.txt` | Relevant when the query names Bruin 101. The strongest chunk explains 11/14/19 plans, Regular weekly non-carryover swipes, and Premium quarter-level/multiple meal-period swipes. |
| When are dining halls and quick-service/takeout locations usually busiest? | `08_stack_dining_popularity_analysis.txt` | Relevant. Top results mention dinner peaks between 6 p.m. and 7 p.m., De Neve's Sunday 7-7:30 p.m. peak, and The Study traffic patterns. |
| What recent dining problems involved schedule changes, strikes, mobile ordering, and food trucks? | `04_dailybruin_schedule_changes_strikes.txt` | Strongly relevant. Top results mention strikes, takeout shifts, mobile ordering shutdowns, two-hour waits, food truck lines, and ASUCLA swipe restrictions. |
| What do sources say about The Study at Hedrick? | `07_bruinlife_oncampus_dining_guide.txt`, `11_alumni_campus_eats_student_reviews.txt`, `04_dailybruin_schedule_changes_strikes.txt` | Partially relevant. The first two chunks describe The Study well, but tail results focus on strike closures and one irrelevant nearby Rendezvous section. This becomes the main failure case below. |

## Grounded Generation

The generator uses this system instruction in `generator.py`:

> You answer questions for The Unofficial Guide to UCLA dining. Use only the retrieved context provided by the user. Do not use outside knowledge, current menus, current prices, or assumptions. If the context does not contain enough information to answer, say: "I don't have enough information in the provided sources to answer that." Keep the answer concise but specific. Cite claims with the numbered source markers like [1] or [2]. If sources disagree or are time-bound, say so instead of blending them into one certainty.

Before calling Groq, the retrieved chunks are filtered with a cosine-distance threshold of `0.58` to avoid sending very weak evidence to the model. If every chunk is above that threshold, the generator keeps only the top two chunks so the model can still make a context-grounded refusal. If retrieval returns no chunks at all, `generator.py` uses the same documented refusal phrase before calling the LLM. Each chunk is formatted as a numbered context block with source title, URL, date, distance, and text; `generator.py` also appends a programmatic source list so attribution is visible even if the model's wording varies.

## Example System Responses

**In-scope example:** "How do UCLA meal plan types differ between Regular (R) and Premium (P), according to the Bruin 101 podcast?"

System response:

> According to the Bruin 101 podcast [1], UCLA meal plan types differ between Regular (R) and Premium (P) in the following ways: For R, you're only able to swipe once during a meal period and your swipes don't carry over each week. For P, you get all your swipes at the beginning of the quarter and then you have until finals week to use them up, and you're able to swipe as many times as you want within a meal period [1].

Source shown:

1. Bruin 101: Dining (September 17, 2022) - https://dailybruin.com/2022/09/17/bruin101-dining

**Second in-scope example:** "When are UCLA dining halls and quick-service/takeout locations usually busiest, according to The Stack's swipe analysis?"

System response summary:

> UCLA dining halls are usually busiest during dinner, peaking between 6 p.m. and 7 p.m.; quick-service/takeout locations are busiest during lunch, peaking between 11 a.m. and 12 p.m. De Neve peaks around 7 p.m. to 7:30 p.m. Sundays, and The Study has high lunch/dinner traffic plus a weekday breakfast peak around 9 a.m. [1]-[4].

Sources shown were all from `UCLA's most popular dining halls` at https://stack.dailybruin.com/2022/02/17/dining-halls/.

**Out-of-scope example:** "How much does a 14P meal plan cost in dollars per quarter?"

System response:

> I don't have enough information in the provided sources to answer that. The retrieved context [1], [2], [3], [4], and [5] do not mention the cost of a 14P meal plan in dollars per quarter.

This is the desired refusal behavior because the corpus explains how 14P works but does not include a dollar price.

## Query Interface

Run the Gradio chat app from the project root:

```bash
python app.py
```

The app defaults to `http://127.0.0.1:8502`. To choose another port, set `GRADIO_SERVER_PORT`:

```bash
GRADIO_SERVER_PORT=7860 python app.py
```

The interface has one chat input for a UCLA dining question. The output is a chat response with inline source markers and a source list containing source titles, dates, and URLs. A side panel lists the loaded corpus sources so the user can see what the system is grounded in.

**Sample interaction transcript:**

User:

```text
What makes Bruin Plate a good option for healthy eating?
```

Assistant:

```text
Students and reviewers describe Bruin Plate as health-focused, with nutrition standards, fresh ingredients, yogurt, fruit, balanced meals, and vegetarian-friendly options [1]-[5].

Sources:
1. The Quad: Bruins savor taste of UCLA's No. 1-ranked dining hall food - https://dailybruin.com/2021/10/24/the-quad-bruins-savor-taste-of-uclas-no-1-ranked-dining-hall-food
2. Bruin Plate Residential Restaurant - Reviews - https://wanderlog.com/place/details/524688
3. Can students eat healthy at UCLA's dining halls? - https://dailybruin.com/2026/01/31/can-students-eat-healthy-at-uclas-dining-halls
```

## Evaluation Report

Run command:

```bash
.venv/bin/python evaluate_m6.py
```

| # | Question | Expected answer | System response | Retrieved chunks | Retrieval quality | Response accuracy |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | What do students and reviewers say makes Bruin Plate a good option for healthy eating or dietary restrictions? | Mention B-Plate/Bruin Plate as health-focused, fresh, balanced, good for vegetarian/dietary needs, with fruit/salad/protein or gluten-free pantry context. | Mentioned healthy and sustainable options, yogurt, fresh ingredients, diverse stations, vegetarian comfort, fruit/dessert options, and nutrition standards. | Daily Bruin No. 1 dining article; Wanderlog Bruin Plate reviews; Daily Bruin healthy eating article; Bruin 101 podcast. | Relevant | Accurate |
| 2 | How do UCLA meal plan types differ between Regular (R) and Premium (P), according to the Bruin 101 podcast? | Regular allows one swipe per meal period and unused swipes do not carry over weekly; Premium gives quarter-level swipes usable through finals and allows multiple swipes in a meal period. | Correctly explained R versus P and cited Bruin 101. It did not restate 11/14/19 counts in the final answer, but the core distinction was correct. | Bruin 101 ranked first; other tail chunks were less relevant dining overview chunks. | Relevant | Accurate |
| 3 | When are UCLA dining halls and quick-service/takeout locations usually busiest, according to The Stack's swipe analysis? | Dining halls peak at dinner, generally 6-7 p.m.; De Neve peaks around 7-7:30 p.m. Sundays; quick-service/takeout peaks around weekday lunch, 11 a.m.-12 p.m.; The Study is busy across lunch/dinner and peaks around 9 a.m. for weekday breakfast. | Correctly stated the dinner and lunch peaks, De Neve's Sunday peak, and The Study's lunch/dinner and breakfast pattern. | Five chunks from The Stack swipe analysis. | Relevant | Accurate |
| 4 | What recent UCLA Dining problems did students report around schedule changes, strikes, mobile ordering, and food trucks? | Mention long food truck lines, mobile-ordering waits up to two hours or app shutdowns, ASUCLA swipe restrictions, and strike-related takeout/limited options. | Mentioned strikes, takeout shifts, mobile-ordering shutdowns, two-hour waits, food truck lines, ASUCLA lunch-only restrictions, and crowded dining halls. | Five chunks from the 2025 Daily Bruin schedule/strikes article. | Relevant | Accurate |
| 5 | What do the sources say about The Study at Hedrick as a dining option? | Mention customizable sandwiches, salads, pizzas, breakfast items, extended/late-night use, study-friendly atmosphere, consistent food, and long waits including over an hour or around two hours. | Mentioned customizable sandwiches/salads/pizzas, consistent quality, study space, long waits, 5/5 rating, and strike-related closure context. It missed breakfast, late-night/extended dinner, and the strongest quantified wait examples. | BruinLife guide; UCLA Alumni Campus Eats; Daily Bruin schedule/strikes chunks; one repeated/nearby BruinLife chunk. | Partially relevant | Partially accurate |
| 6 | How much does a 14P meal plan cost in dollars per quarter? | The corpus does not include a dollar price, so the correct behavior is to abstain instead of inventing a number. | Correctly refused: "I don't have enough information in the provided sources to answer that." | Five Bruin 101 meal-plan chunks, none with prices. | Relevant for refusal | Accurate |

## Failure Case Analysis

**Question that partially failed:** What do the sources say about The Study at Hedrick as a dining option?

**What the system returned:** The answer correctly described The Study as a customizable sandwich/salad/pizza option with a good study space, consistent quality, and long waits. However, it missed several expected details from the planning evaluation answer: breakfast items, extended/late-night dinner, coffee, and the strongest quantified waits from Bruin 101 and The Stack.

**Root cause tied to the pipeline:** This was mainly a retrieval failure. The query used the broad phrase "what do the sources say," so semantic search favored chunks that explicitly name "The Study at Hedrick" in general descriptions from BruinLife and UCLA Alumni. It also retrieved strike-related chunks because they mention The Study's non-dining area, but it did not retrieve the Bruin 101 chunks that contain the detailed student quotes about build-your-own breakfast, coffee, over-one-hour waits, two-hour waits, and extended dinner. Since generation only uses retrieved context, the LLM could not include facts it was not given.

**What I would change to fix it:** I would add hybrid search or source diversification. Keyword matching for terms like `extended dinner`, `breakfast`, `two hours`, and `wait` would help recover the detailed Bruin 101 and Stack chunks, while a source-diversity step could prevent the final context from being dominated by broad general descriptions or repeated nearby chunks.

## Spec Reflection

**One way the spec helped during implementation:** The planning document forced the project to define the corpus, chunk size, metadata, top-k value, and evaluation questions before building generation. That made it much easier to check whether each implementation stage matched the intended RAG pipeline. For example, the retrieval code knew from the spec that chunks needed title, URL, date, filename, and chunk position metadata so generation could cite sources later.

**One way the implementation diverged from the spec, and why:** The spec anticipated chunks around 900-1200 characters, but the implementation settled on a 900-character target and 1024-character max. I narrowed the max after considering `all-MiniLM-L6-v2`'s short input limit; even so, one measured chunk is slightly above the 256-token embedding limit, so this remains a small known limitation. The implementation also added a `LOW_RELEVANCE_DISTANCE` filter in generation, which was not part of the initial plan but helped reduce weak tail chunks before prompting Groq.

## AI Usage

**Instance 1**

- _What I gave the AI:_ The Documents, Chunking Strategy, and Architecture sections from `planning.md`, plus the requirement to preserve source metadata through ingestion.
- _What it produced:_ A first version of `ingest.py` that loaded local `.txt` documents, parsed metadata headers, cleaned text, split by paragraphs/sentences, and produced chunk dictionaries.
- _What I changed or overrode:_ I tightened the chunk sizes to a 900-character target and 1024-character max, added source-path and chunk-position metadata, and manually inspected representative chunks to confirm they were readable rather than accepting the generated splitter blindly.

**Instance 2**

- _What I gave the AI:_ The Retrieval Approach, Evaluation Plan, and Milestone 4/5 requirements, including the need for ChromaDB retrieval, source attribution, and grounded generation.
- _What it produced:_ Draft retrieval and generation structure using ChromaDB, `all-MiniLM-L6-v2`, Groq, and a Gradio interface.
- _What I changed or overrode:_ I made the retriever use the same Chroma embedding function for indexing and querying, added CLI inspection options, added a distance filter before generation, and appended the final source list programmatically so citations did not depend only on the LLM.

## Assumptions

- The UCLA dining text files in `documents/ucla-dining-hall/ucla-cld` are the intended final corpus for this milestone.
- ChromaDB cosine distance is interpreted as lower-is-more-relevant.
- The evaluation uses the six questions already present in `planning.md`; the assignment asks for at least five, and the sixth is useful as an abstention test.
- The final demo video is still a manual submission step, not something this repository can complete on its own.

## Remaining TODO

- Record the 3-5 minute demo video showing at least three cited queries, one strong success, one failure/partial failure, and a walkthrough of this evaluation report.
