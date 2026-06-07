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

**Chunk size:** I will use recursive, structure-aware chunks of about 300-450 tokens each. The chunker will try to keep natural paragraphs or speaker turns together first, then split oversized sections by sentence if needed. I will avoid splitting in the middle of a sentence or separating a dining location name from the opinion or detail attached to it.

**Overlap:** I will use about 60-80 tokens of overlap between adjacent chunks when a document section has to be split. This should preserve context when a useful fact spans two nearby paragraphs, such as a dining hall name in one sentence and the student's reason or complaint in the next.

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

**Top-k:** I will retrieve the top 5 chunks for each query. This should give the answer generator enough context to compare multiple student opinions or sources, while still keeping the prompt focused. We can increase and decrease this number during testing to find the best balance.

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

| #   | Question | Expected answer |
| --- | -------- | --------------- |
| 1   |          |                 |
| 2   |          |                 |
| 3   |          |                 |
| 4   |          |                 |
| 5   |          |                 |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries.

     TODO: Fill this in when making implementation decisions. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage.

     TODO: Fill this in after choosing the implementation stack. -->

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
