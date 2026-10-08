# Retrieval, a small search agent, and measuring retrieval

Researched 2026-10-08. Every link below was opened on that date. Labels: peer-reviewed, preprint, vendor doc, code.
Where a page did not say something, this note says so instead of guessing.

## 1. Question

We are adding four things to the drafting step:

1. Hybrid retrieval over current passages: BM25 plus Gemini embeddings, merged with reciprocal rank fusion (RRF),
   keep the top k.
2. A read-only search loop: the model may call one tool, `search_passages(query)`, at most 2 times, then it must
   answer. Approval, reuse and routing stay in code.
3. Retrieval recall@k for each answer-key row in the results.
4. A larger fictional dataset with distractor passages and gold passages picked by hand.

What are the best primary sources for each part, what do they actually say, and what do the current Gemini API docs
say about embeddings, structured output with function calling, and thought signatures?

## 2. Short answer

- BM25 + dense + RRF is a well-supported, standard choice. BM25 is a strong baseline on its own (BEIR). Hybrids beat
  dense-only out of domain. RRF with k = 60 needs no score tuning, which suits a tiny corpus with no training data.
- The Gemini embeddings page now centres on `gemini-embedding-2`. **That model does not take `task_type`.** You put
  the task in the text instead (`task: search result | query: …`, `title: … | text: …`). `RETRIEVAL_QUERY` /
  `RETRIEVAL_DOCUMENT` apply to `gemini-embedding-001`. The docs disagree on whether `gemini-embedding-2` is stable
  or preview, so check the ID with a live call before recording.
- Search loops like ReAct, Self-Ask and IRCoT help most on multi-step questions. Questionnaire questions are mostly
  one step, so the loop's main value here is a second try when the first search misses. Self-RAG is a training
  method and cannot be used with an API model. A small hard cap (2 calls) matches the budget literature.
- For Gemini 3, the docs say structured output can be combined with function calling (marked Preview, named for
  `gemini-3.1-pro-preview` and `gemini-3.8-flash`). Thought signatures must be sent back during function calling, or
  the call fails with a 4xx error.
- Measure retrieval apart from generation (RAGAS, ARES, eRAG). Distractors are justified: related but wrong passages
  hurt answers more than random ones (Power of Noise; Shi et al.). Hand-built test sets are easier than real ones and
  only support relative comparisons, so report counts and say so.

## 3. Evidence table

### 3a. Retrieval: BM25, fusion, hybrid

| Source | Type | Key claim or number (quoted) | What it supports here | Link |
|---|---|---|---|---|
| Stephen Robertson, Hugo Zaragoza. *The Probabilistic Relevance Framework: BM25 and Beyond*. Foundations and Trends in Information Retrieval 3(4):333–389, 2009. DOI 10.1561/1500000019 | peer-reviewed | Section 3.5: "the model provides no guidance on how these should be set … values such as 0.5 < b < 0.8 and 1.2 < k1 < 2 are reasonably good in many circumstances. However, there is also evidence that optimal values do depend on other factors (such as the type of documents or queries)." | Pick k1 and b from the stated range and do not tune them on our tiny set. | [author PDF](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf) · [publisher](https://nowpublishers.com/article/Details/INR-019) |
| Christopher D. Manning, Prabhakar Raghavan, Hinrich Schütze. *Introduction to Information Retrieval*, Cambridge University Press, 2008, §11.4.3 | peer-reviewed (textbook) | "reasonable values are to set k1 and k3 to a value between 1.2 and 2 and b = 0.75" | The usual one-line default (b = 0.75) that the README can cite. | [link](https://nlp.stanford.edu/IR-book/html/htmledition/okapi-bm25-a-non-binary-model-1.html) |
| `rank_bm25` (Dorian Brown), `BM25Okapi` | code | `def __init__(self, corpus, tokenizer=None, k1=1.5, b=0.75, epsilon=0.25)`. Terms in more than half the documents get negative IDF, which the code raises to `epsilon * average_idf`. | If we use this library, its defaults sit inside the range above. In a very small corpus, common words hit the IDF floor. Know this when a score looks odd. | [source](https://raw.githubusercontent.com/dorianbrown/rank_bm25/master/rank_bm25.py) |
| Gordon V. Cormack, Charles L. A. Clarke, Stefan Büttcher. *Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods*. SIGIR 2009, pp. 758–759. DOI 10.1145/1571941.1572114 | peer-reviewed | Formula: "RRFscore(d ∈ D) = Σ(r∈R) 1/(k + r(d))". "k = 60 was fixed during a pilot investigation and not altered during subsequent validation." The pilot "indicated that k = 60 was near-optimal, but that the choice was not critical." | RRF with k = 60 is the standard, untuned way to merge the BM25 list and the embedding list. | [PDF](http://cormack.uwaterloo.ca/cormacksigir09-rrf.pdf) (read via a text extractor; venue and pages confirmed on [OpenAlex](https://api.openalex.org/works/doi:10.1145/1571941.1572114)) |
| Sebastian Bruch, Siyu Gai, Amir Ingber. *An Analysis of Fusion Functions for Hybrid Retrieval*. ACM TOIS 42(1), 2023. DOI 10.1145/3596512 | peer-reviewed | Finds "RRF to be sensitive to its parameters" and that convex combination "outperforms RRF in in-domain and out-of-domain settings" and needs "only a small set of training examples to tune its only parameter". | Honest counterpoint: score blending can beat RRF, but only after tuning. We have too few rows to tune without overfitting, so RRF is the safer pick. | [arXiv](https://arxiv.org/abs/2210.11934) (venue confirmed on [OpenAlex](https://api.openalex.org/works/doi:10.1145/3596512)) |
| Nandan Thakur, Nils Reimers, Andreas Rücklé, Abhishek Srivastava, Iryna Gurevych. *BEIR: A Heterogenous Benchmark for Zero-shot Evaluation of Information Retrieval Models*. NeurIPS 2021 Datasets and Benchmarks | peer-reviewed | "Our results show BM25 is a robust baseline … dense and sparse-retrieval models are computationally more efficient but often underperform other approaches, highlighting the considerable room for improvement in their generalization capabilities." | Keeping BM25 in the mix is not old-fashioned. It is the strong zero-shot baseline, and our fictional product terms are out of domain for any embedding model. | [link](https://arxiv.org/abs/2104.08663) |
| Tao Chen, Mingyang Zhang, Jing Lu, Michael Bendersky, Marc Najork. *Out-of-Domain Semantics to the Rescue! Zero-Shot Hybrid Retrieval Models*. ECIR 2022 | peer-reviewed | "The performance of a deep retrieval model is significantly deteriorated when the target domain is very different from the source domain." The lexical + deep hybrid gives "an average of 20.4% relative gain over the deep retrieval model" out of domain. | Direct evidence that hybrid beats dense-only when the domain is new, which is our case. | [link](https://arxiv.org/abs/2201.10582) |
| Xueguang Ma, Kai Sun, Ronak Pradeep, Jimmy Lin. *A Replication Study of Dense Passage Retriever*. 2021 | preprint (venue not checked) | "the original authors under-report the effectiveness of the BM25 baseline and hence also dense--sparse hybrid retrieval results" | Supporting: BM25 and dense–sparse hybrids are easy to under-sell. The abstract does not itself state "hybrid beats both"; I did not read the body. | [link](https://arxiv.org/abs/2104.05740) |
| Kyle McCleary, James Ghawaly. *Quantifying the Accuracy and Cost Impact of Design Decisions in Budget-Constrained Agentic LLM Search*. LREC 2026 (per arXiv comment) | peer-reviewed (per arXiv comment) | "Accuracy improves with additional searches up to a small cap"; "Hybrid lexical and dense retrieval with lightweight re-ranking produces the largest average gains". | Recent support for both choices together: hybrid retrieval and a small search cap. | [link](https://arxiv.org/abs/2603.08877) |

### 3b. RAG and Gemini embeddings

| Source | Type | Key claim or number (quoted) | What it supports here | Link |
|---|---|---|---|---|
| Patrick Lewis, Ethan Perez, Aleksandra Piktus, Fabio Petroni, Vladimir Karpukhin, Naman Goyal, Heinrich Küttler, Mike Lewis, Wen-tau Yih, Tim Rocktäschel, Sebastian Riedel, Douwe Kiela. *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. NeurIPS 2020 | peer-reviewed | Models with "a differentiable access mechanism to explicit non-parametric memory can overcome this issue"; "Providing provenance for their decisions and updating their world knowledge remain open research problems." | The base idea: answer from retrieved text, not from model memory. Note their retriever is trained end to end; ours is not. | [link](https://arxiv.org/abs/2005.11401) |
| Jinhyuk Lee, Feiyang Chen, Sahil Dua, Daniel Cer, et al. (47 authors). *Gemini Embedding: Generalizable Embeddings from Gemini*. arXiv, 10 Mar 2025 | preprint | On MMTEB, "Gemini Embedding substantially outperforms prior state-of-the-art models". | Background for the embedding half. It predates `gemini-embedding-2`; I did not check which API model ID the paper describes. | [link](https://arxiv.org/abs/2503.07891) |
| Google. *Embeddings*, Gemini API docs (last updated 2026-09-17) | vendor doc | See section 3e for exact quotes on model IDs, task types, dimensions, normalisation and batching. | How to call the embedding model correctly. | [link](https://ai.google.dev/gemini-api/docs/embeddings) |
| Google. *Embeddings* API reference (last updated 2026-08-28) | vendor doc | `taskType`: "Optional task type for which the embeddings will be used. Not supported on earlier models (`models/embedding-001`)." No maximum number of requests per `batchEmbedContents` call is stated. | Lists the `TaskType` values. Confirms the batch limit is not documented there. | [link](https://ai.google.dev/api/embeddings) |
| Google. *Gemini models* (last updated 2026-10-06) | vendor doc | Lists "Gemini Embedding 2" with endpoint `gemini-embedding-2-preview`, and `gemini-embedding-001`. Lists `gemini-3.8-flash` as stable. | Shows the ID mismatch with the embeddings page (see 3e). | [link](https://ai.google.dev/gemini-api/docs/models) |

### 3c. Search loops where the model writes its own queries

| Source | Type | Key claim or number (quoted) | What it supports here | Link |
|---|---|---|---|---|
| Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, Yuan Cao. *ReAct: Synergizing Reasoning and Acting in Language Models*. ICLR 2023 | peer-reviewed | The model generates "both reasoning traces and task-specific actions in an interleaved manner" and "overcomes issues of hallucination and error propagation … by interacting with a simple Wikipedia API". | The basic pattern of our loop: think, call search, read, answer. Works with prompting only, so it fits an API model. | [link](https://arxiv.org/abs/2210.03629) |
| Ofir Press, Muru Zhang, Sewon Min, Ludwig Schmidt, Noah A. Smith, Mike Lewis. *Measuring and Narrowing the Compositionality Gap in Language Models* (Self-Ask). Findings of EMNLP 2023 | peer-reviewed | "the model explicitly asks itself (and answers) follow-up questions before answering"; it lets you "easily plug in a search engine to answer the follow-up questions". | Shows that model-written follow-up queries are useful. Its gains are on two-hop questions, which our dataset has few of. | [link](https://arxiv.org/abs/2210.03350) |
| Harsh Trivedi, Niranjan Balasubramanian, Tushar Khot, Ashish Sabharwal. *Interleaving Retrieval with Chain-of-Thought Reasoning for Knowledge-Intensive Multi-Step Questions* (IRCoT). ACL 2023 | peer-reviewed | Improves "retrieval (up to 21 points) as well as downstream QA (up to 15 points)" on HotpotQA, 2WikiMultihopQA, MuSiQue and IIRC; "IRCoT reduces model hallucination". | Retrieval guided by the model's own reasoning can raise recall. The numbers are on multi-hop sets, so do not expect them here. | [link](https://arxiv.org/abs/2212.10509) |
| Zhengbao Jiang, Frank F. Xu, Luyu Gao, Zhiqing Sun, Qian Liu, Jane Dwivedi-Yu, Yiming Yang, Jamie Callan, Graham Neubig. *Active Retrieval Augmented Generation* (FLARE). EMNLP 2023 | peer-reviewed | Methods "that actively decide when and what to retrieve"; retrieve again "if it contains low-confidence tokens". | The idea that the model, not a fixed rule, decides whether to search again. FLARE's trigger needs token confidences; our loop instead lets the model decide by calling the tool. | [link](https://arxiv.org/abs/2305.06983) |
| Akari Asai, Zeqiu Wu, Yizhong Wang, Avirup Sil, Hannaneh Hajishirzi. *Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection*. ICLR 2024 | peer-reviewed | Trains "a single arbitrary LM that adaptively retrieves passages on-demand" using "special tokens, called reflection tokens". | **Training-time method. Cannot be applied to the Gemini API.** Cite only as background for "retrieve on demand". | [arXiv](https://arxiv.org/abs/2310.11511) · [OpenReview](https://openreview.net/forum?id=hSyW5go0v8) |
| Tengxiao Liu, Zifeng Wang, Jin Miao, et al. (15 authors). *Budget-Aware Tool Use Enables Effective Agent Scaling*. COLM 2026 (per arXiv comment) | peer-reviewed (per arXiv comment) | "simply increasing the tool-call budget fails to improve performance, as agents lack 'budget awareness' and quickly hit a performance ceiling". | Supports a small, fixed cap, and telling the model how many searches it has left. | [link](https://arxiv.org/abs/2511.17006) |

### 3d. Safety of tool-using agents

| Source | Type | Key claim or number (quoted) | What it supports here | Link |
|---|---|---|---|---|
| Luca Beurer-Kellner, Beat Buesser, Ana-Maria Creţu, Edoardo Debenedetti, Daniel Dobos, Daniel Fabian, Marc Fischer, David Froelicher, Kathrin Grosse, Daniel Naeff, Ezinwanne Ozoani, Andrew Paverd, Florian Tramèr, Václav Volhejn. *Design Patterns for Securing LLM Agents against Prompt Injections*. arXiv, Jun 2025 (v3) | preprint | "Once an LLM agent has ingested untrusted input, it must be constrained so that it is impossible for that input to trigger any consequential actions." Patterns include Action-Selector, Plan-Then-Execute and Context-Minimization. | The one tool is a read over local current passages. It has no consequential action. Approve, reuse and route stay in code. | [link](https://arxiv.org/abs/2506.08837) · [HTML](https://arxiv.org/html/2506.08837) |
| Edoardo Debenedetti, Ilia Shumailov, Tianqi Fan, Jamie Hayes, Nicholas Carlini, Daniel Fabian, Christoph Kern, Chongyang Shi, Andreas Terzis, Florian Tramèr. *Defeating Prompt Injections by Design* (CaMeL). arXiv, Mar 2025 (v2 Jun 2025) | preprint (SaTML 2026 acceptance not verified by me) | "the untrusted data retrieved by the LLM can never impact the program flow"; solves "77% of tasks with provable security (compared to 84% with an undefended system) in AgentDojo". | Shows the strong end of the scale: control flow fixed in code. Our loop is far simpler; CaMeL is more machinery than this design needs. | [link](https://arxiv.org/abs/2503.18813) |

### 3e. Gemini API: exact wording

All quotes from pages opened on 2026-10-08.

**Embedding models** ([Embeddings](https://ai.google.dev/gemini-api/docs/embeddings), updated 2026-09-17):

- Model table: `gemini-embedding-2`, "Versions: Stable: `gemini-embedding-2`", "Latest update: April 2026", input token
  limit 8,192. `gemini-embedding-001`, "Stable: `gemini-embedding-001`", "Latest update: June 2025", input token limit
  2,048. Both: "Flexible, supports: 128 - 3072 (Recommended: 768, 1536, 3072)".
- **Mismatch:** the [Models](https://ai.google.dev/gemini-api/docs/models) page (updated 2026-10-06) gives the
  endpoint for Gemini Embedding 2 as `gemini-embedding-2-preview`. I could not settle which ID the API accepts.
- Space change: "The embedding spaces between `gemini-embedding-001` and `gemini-embedding-2` are incompatible …
  If you are upgrading to `gemini-embedding-2`, you must re-embed all of your existing data."

**Python call**:

```python
from google import genai
from google.genai import types

client = genai.Client()
result = client.models.embed_content(
    model="gemini-embedding-2",
    contents="What is the meaning of life?",
    config=types.EmbedContentConfig(output_dimensionality=768),
)
```

**Task types**:

- "With `gemini-embedding-2`, the `task_type` parameter is not supported. Instead, you should include task
  instructions directly in the prompt for text-only tasks."
- Retrieval query format: `task: search result | query: {content}`. Document format: `title: {title} | text:
  {content}` (or `title: none`).
- For `gemini-embedding-001`, `task_type` takes `RETRIEVAL_QUERY` / `RETRIEVAL_DOCUMENT` (and `SEMANTIC_SIMILARITY`,
  `CLASSIFICATION`, `CLUSTERING`, `CODE_RETRIEVAL_QUERY`, `QUESTION_ANSWERING`, `FACT_VERIFICATION`).

**Normalisation**:

- "`gemini-embedding-2` introduces automatic renormalization for non-default dimensions. While the default
  3072-dimension embeddings are always normalized, Gemini Embedding 2 also auto-normalizes truncated dimensions
  (e.g., 768, 1536)."
- "If you are using `gemini-embedding-001`, you must manually normalize non-3072 dimensions."

**Several texts in one call**:

- "Multiple parts (aggregated): Adding multiple inputs directly to the contents parameter produces one aggregated
  embedding for all inputs. Multiple Content objects (separate): Wrapping each input in a Content object and passing
  them in the contents parameter returns separate embeddings for each entry."
- This sits in a multimodal section. The docs show the "separate" case with `types.Content(parts=[...])` per input.
- **Not stated:** a maximum number of inputs per `embed_content` call, on both the guide and the API reference.

**Structured output with function calling**
([Structured output](https://ai.google.dev/gemini-api/docs/generate-content/structured-output), updated 2026-09-02):

- "Preview: This capability is currently available only to Gemini 3 series models, specifically
  `gemini-3.1-pro-preview` and `gemini-3.8-flash`."
- "Gemini 3 lets you combine Structured Outputs with built-in tools, including Grounding with Google Search, URL
  Context, Code Execution, File Search, and Function Calling."
- The [function calling page](https://ai.google.dev/gemini-api/docs/generate-content/function-calling) (updated
  2026-09-16) agrees: "For Gemini 3 series models, you can use function calling with structured output."

**Function calling controls** (same page):

- Modes: AUTO, ANY, VALIDATED, and "NONE: The model is _prohibited_ from making function calls."
- Python SDK: automatic function calling can be turned off with
  `automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)`.
- "aim to provide only the relevant tools … ideally keeping the active set to a maximum of 10-20."
- That page says "Use a low temperature (e.g., 0)". The [Gemini 3 guide](https://ai.google.dev/gemini-api/docs/gemini-3)
  (updated 2026-09-23) says "For all Gemini 3 models, we strongly recommend keeping the temperature parameter at its
  default value of `1.0`" and warns that lower values "may lead to unexpected behavior, such as looping". These
  conflict. For Gemini 3 the model-specific guide is the more specific source.

**Thought signatures**
([Thought signatures, generateContent](https://ai.google.dev/gemini-api/docs/generate-content/thought-signatures),
updated 2026-09-04):

- "When using Gemini 3 models, you must pass back thought signatures during function calling, otherwise you will get
  a validation error (4xx status code)."
- "The first functionCall part in each step of the current turn must include its thought_signature."
- "If the model generates parallel function calls in a response, the thought_signature is attached only to the first
  functionCall part."
- "Thought signatures are handled automatically when you use the official Google Gen AI SDKs and append the full
  model response object directly to history."
- For injected history it gives dummy values (`"context_engineering_is_the_way_to_go"` or
  `"skip_thought_signature_validator"`). We should not need them.
- The function calling page adds: "passing back thought signatures is mandatory for function calling."

### 3f. Measuring retrieval, distractors, and test sets

| Source | Type | Key claim or number (quoted) | What it supports here | Link |
|---|---|---|---|---|
| Shahul Es, Jithin James, Luis Espinosa Anke, Steven Schockaert. *RAGAs: Automated Evaluation of Retrieval Augmented Generation*. EACL 2024 System Demonstrations, pp. 150–158 | peer-reviewed | Scores "the ability of the retrieval system to identify relevant and focused context passages" apart from "the ability of the LLM to exploit such passages in a faithful way". | Score retrieval and generation separately. We use hand gold labels, not RAGAS's LLM scoring. | [ACL](https://aclanthology.org/2024.eacl-demo.16/) · [arXiv](https://arxiv.org/abs/2309.15217) |
| Jon Saad-Falcon, Omar Khattab, Christopher Potts, Matei Zaharia. *ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems*. NAACL 2024 | peer-reviewed | Evaluates "along the dimensions of context relevance, answer faithfulness, and answer relevance"; uses "a small set of human-annotated datapoints". | Context quality is its own axis, and a small human-labelled set is the anchor. | [link](https://arxiv.org/abs/2311.09476) |
| Alireza Salemi, Hamed Zamani. *Evaluating Retrieval Quality in Retrieval-Augmented Generation* (eRAG). SIGIR 2024, best short paper. DOI 10.1145/3626772.3657957 | peer-reviewed | "evaluation of the retrieval model's performance based on query-document relevance labels shows a small correlation with the RAG system's downstream performance." | Caution: high recall@k does not promise good answers. Report both, side by side. | [arXiv](https://arxiv.org/abs/2404.13781) · [award note](https://ciir.cs.umass.edu/node/814) |
| Hao Yu, Aoran Gan, Kai Zhang, Shiwei Tong, Qi Liu, Zhaofeng Liu. *Evaluation of Retrieval-Augmented Generation: A Survey*. 2024 | preprint | Compares "quantifiable metrics of the Retrieval and Generation components, such as relevance, accuracy, and faithfulness". | Survey that treats retrieval and generation metrics as separate parts. | [link](https://arxiv.org/abs/2405.07437) |
| Nelson F. Liu, Kevin Lin, John Hewitt, Ashwin Paranjape, Michele Bevilacqua, Fabio Petroni, Percy Liang. *Lost in the Middle: How Language Models Use Long Contexts*. TACL 12:157–173, 2024 | peer-reviewed | "performance is often highest when relevant information occurs at the beginning or end of the input context, and significantly degrades when models must access relevant information in the middle of long contexts." | Keep k small and pass passages in fused-rank order. | [ACL](https://aclanthology.org/2024.tacl-1.9/) · [arXiv](https://arxiv.org/abs/2307.03172) |
| Freda Shi, Xinyun Chen, Kanishka Misra, Nathan Scales, David Dohan, Ed Chi, Nathanael Schärli, Denny Zhou. *Large Language Models Can Be Easily Distracted by Irrelevant Context*. ICML 2023 | peer-reviewed | "the model performance is dramatically decreased when irrelevant information is included"; one mitigation is "adding to the prompt an instruction that tells the language model to ignore the irrelevant information". | Why the dataset needs distractors, and support for the prompt saying "use only passages that answer this question". | [link](https://arxiv.org/abs/2302.00093) |
| Florin Cuconasu, Giovanni Trappolini, Federico Siciliano, Simone Filice, Cesare Campagnano, Yoelle Maarek, Nicola Tonellotto, Fabrizio Silvestri. *The Power of Noise: Redefining Retrieval for RAG Systems*. SIGIR 2024. DOI 10.1145/3626772.3657834 | peer-reviewed | "the retriever's highest-scoring documents that are not directly relevant to the query … negatively impact the effectiveness of the LLM"; "adding random documents in the prompt improves the LLM accuracy by up to 35%." | Distractors must be close to the topic (same feature, other plan or product) to be a real test. Random filler is not. | [link](https://arxiv.org/abs/2401.14887) |
| Hossein A. Rahmani, Nick Craswell, Emine Yilmaz, Bhaskar Mitra, Daniel Campos. *Synthetic Test Collections for Retrieval Evaluation*. SIGIR 2024 | peer-reviewed | "systems consistently achieve higher performance on synthetic test collections when compared to real queries, suggesting that synthetic test collections tend to be easier than real queries"; "our results are based on one test collection". | Limit to state in the results: a made-up set probably flatters the system. | [link](https://arxiv.org/abs/2405.07767) |
| Ellen M. Voorhees. *The Philosophy of Information Retrieval Evaluation*. CLEF 2001 | peer-reviewed | Test collections are used "to compare the relative effectiveness of different retrieval approaches". | Use our recall@k to compare BM25 vs dense vs hybrid vs loop on the same rows, not as an absolute quality claim. | [link](https://www.nist.gov/publications/philosophy-information-retrieval-evaluation-0) |
| Evan Miller. *Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations*. 2024 | preprint | Treats eval questions "as having been drawn from an unseen super-population". | With a few dozen rows, report counts (for example 11/12) and say the uncertainty is large. | [link](https://arxiv.org/abs/2411.00640) |

## 4. Options for this project

Rule IDs below: RULE-1 to RULE-4 are the four rules in `data/seed/domain.md`. MIN-1 to MIN-5 are the minimum checks.
GEN-2 is record and replay. Nothing here adds or changes a business rule. Retrieval only changes which current
passages the model sees.

### A. Retrieval

| Option | Effort | Risk | Helps |
|---|---|---|---|
| A1. BM25 only | Low. No API call, fully offline and deterministic. | Misses paraphrases ("export a spreadsheet" vs "CSV"). | MIN-1, MIN-2 if the gold passage is still found |
| A2. Embeddings only | Medium. Vectors must be recorded for replay. | Weaker on rare product terms and IDs out of domain (BEIR; Chen et al.). | Same |
| A3. BM25 + embeddings, RRF k = 60, top k (planned) | Medium. Two rankers and a 10-line fusion. | Small. With few passages, k = 60 makes rank gaps tiny, so RRF mostly rewards passages both rankers like. Sort ties by passage ID so runs repeat. | MIN-1 to MIN-3 when the corpus has distractors; RULE-1 (only current supplied passages) |
| A4. Score blending (convex combination) | Medium plus tuning. | Bruch et al. say it can win, but tuning on our few rows would overfit the answer key. | Not worth it here |

Embedding details to get right:

- **Which model.** With `gemini-embedding-2`, do not send `task_type`. Prefix the text instead: queries as
  `task: search result | query: …`, passages as `title: none | text: …` (or the document ID as title). With
  `gemini-embedding-001`, send `task_type="RETRIEVAL_QUERY"` / `"RETRIEVAL_DOCUMENT"` and normalise vectors yourself
  when the size is not 3072. Normalising in code either way costs one line and makes the cosine step model-independent.
- **The ID mismatch.** Pin the ID in `config/models.toml`, make one live call at record time, and save the ID that
  answered next to the vectors.
- **Batching.** Wrap each passage in its own `types.Content` to get one vector per passage. Check
  `len(result.embeddings) == len(passages)` and fail loudly if not. The docs give no per-call count limit, so with a
  small corpus one call per short batch is fine.
- **Replay (GEN-2).** Save every vector with model ID, dimension, task prefix and a hash of the exact text. Replay
  then needs no key. A changed passage text gives a new hash, so it is re-embedded and never silently reused.
- **Superseded text (RULE-2).** Index only current passages, as today. Replaced text is still shown to reviewers by
  code. A new risk: if two current passages conflict and only one makes the top k, the model cannot report the
  conflict. The gold set for such rows must list both passages, so recall@k exposes the miss.

### B. Search loop

| Option | Effort | Risk | Helps |
|---|---|---|---|
| B1. No loop: one hybrid retrieval, then draft | Low | A missed passage means a wrong "unresolved". That is safe under RULE-1 but leaves a supported question unanswered. | Baseline |
| B2. Read-only `search_passages`, max 2 calls, then a forced answer (planned) | Medium. Manual tool loop, signatures, recording each step. | More calls to record. Injected passage text could steer a query. The worst case is reading other current passages, because the tool cannot write. | MIN-1, MIN-2 on paraphrased questions. Shows ReAct-style use without giving up control. |
| B3. Adopt Self-RAG or FLARE as published | — | Self-RAG needs a fine-tuned model. FLARE triggers on low-confidence tokens. | Not applicable to this API setup |

How to build B2 so the docs' rules hold:

- Turn off automatic function calling and run the loop in our own code, so code counts calls.
- After the second call, send the last request with function calling mode `NONE`. The model then must return the
  JSON answer. Say in the prompt how many searches remain (Liu et al. 2025).
- Send back the full model `Content` each step, so thought signatures are kept. Record the whole exchange (queries,
  tool results, signatures) for replay. A missing signature is a 4xx error, so a failed replay shows up clearly.
- `search_passages` returns current passages only, from the same hybrid index, with IDs and text. It never returns
  replaced passages, reviewer notes or approved answers. Approve, reuse and route stay outside the model
  (Beurer-Kellner et al.).
- Keep temperature at the default 1.0 for Gemini 3, as the project does now. The Gemini 3 guide is more specific
  than the general "temperature 0" tip.
- Structured output plus function calling is marked Preview. If it fails for `gemini-3.8-flash`, a safe fallback:
  run the search turns without a schema, then make one final call with the schema and no tools.

### C. Recall@k per answer-key row

- recall@k = (gold passages found in the top k) / (gold passages). Store gold passage IDs in `reference/`. Derive
  them by reading passages and metadata, never from application output.
- Rows whose gold set is empty (undocumented features, like JSON export): recall is undefined. Show "n/a, no gold
  passage" and do not count them as 0 or 1.
- For the loop, report two numbers: recall of the first retrieval, and recall over every passage the model saw
  across its searches. That separates "the retriever missed" from "the agent recovered".
- Put recall next to the answer result in the same row. eRAG warns that the two can disagree, and that disagreement
  is the useful part.

### D. Extended dataset

- Distractors should be near misses: same feature on another plan, a similar feature, an older replaced version.
  Random text does not test much (Power of Noise).
- Write the gold passages and distractors before running retrieval, and record how in `data/GENERATION.md`. That
  avoids picking distractors the system already handles.
- State the limits in the results: one author, small, fictional, likely easier than real questionnaires (Rahmani et
  al.). Use the numbers to compare retrieval modes, not as a quality claim (Voorhees). Report counts, not percentages
  alone (Miller).

## 5. Recommendation

Build A3 (BM25 with k1 = 1.2 and b = 0.75, inside the published range, plus Gemini embeddings, RRF k = 60, small top k such as 3–5).
Build B2 exactly as listed: manual loop, cap of 2 enforced in code, mode `NONE` on the final turn, full contents sent
back and recorded. Report recall@k per row with "n/a" for empty gold sets, and two recall numbers for the loop. Record
the choices (model ID, prefixes, k1, b, RRF k, top k, cap) in one decision record.

What would change my mind:

- If a live call shows `gemini-embedding-2` is not served under that ID, use `gemini-embedding-001` with `task_type`
  and manual normalisation. Record which one answered.
- If BM25 alone already reaches full recall@k on the extended set, the embedding half adds cost and replay data for
  no measured gain. Say so in the results instead of hiding it.
- If structured output plus function calling fails on `gemini-3.8-flash`, use the two-phase fallback above.
- If the loop gives no recall or answer gain over B1 on the extended set, keep it as an option but turn it off by
  default, and report the result.

## Could not verify

- Whether the API accepts `gemini-embedding-2` or `gemini-embedding-2-preview` today. The two doc pages disagree, and
  I made no API call.
- A maximum number of texts per `embed_content` or `batchEmbedContents` call. Neither page I opened states one.
- Whether a list of plain strings in `contents` gives one vector per string or one combined vector for text-only
  input. The docs' "aggregated" wording sits in a multimodal section. Test it with the length check above.
- CaMeL's SaTML 2026 acceptance. I saw only the arXiv record.
- The publication venue of Ma et al. 2021. I read only the arXiv abstract.
- Which API model ID the Gemini Embedding paper describes.
- The BM25 and RRF PDFs could not be read directly. I read them through a text extractor (r.jina.ai) and confirmed
  RRF's and Bruch et al.'s venues on OpenAlex. The ACM pages returned 403.
