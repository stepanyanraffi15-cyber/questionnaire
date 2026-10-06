# Research notes

Sources below were opened during planning on 2026-10-06; re-open before relying on a specific claim.

Notes written by the `researcher` subagent go here, one file per open question (`oq-5-conflicts.md`, …).
Every claim links a source that was actually opened. Label: peer-reviewed · preprint · vendor doc · blog.

## Starting bibliography (collected 2026-10-06 during planning)

### Citations and faithfulness
- ALCE — Gao et al., EMNLP 2023 (peer-reviewed): https://aclanthology.org/2023.emnlp-main.398.pdf
- RAGChecker — Amazon, NeurIPS 2024 D&B (peer-reviewed): https://github.com/amazon-science/RAGChecker
- Correctness is not Faithfulness in RAG Attributions — Wallat et al., ICTIR 2025 (peer-reviewed): https://staff.fnwi.uva.nl/m.derijke/wp-content/papercite-data/pdf/wallat-2025-correctness.pdf
- SelfCite — Chuang et al., Meta FAIR/MIT, ICML 2025 (peer-reviewed): https://arxiv.org/abs/2502.09604
- ContextCite — Cohen-Wang et al., MIT, NeurIPS 2024 (peer-reviewed): https://proceedings.neurips.cc/paper_files/paper/2024/hash/adbea136219b64db96a9941e4249a857-Abstract-Conference.html
- Attributable Post-Rationalization in RAG Citations — Sep 2026 (preprint): https://arxiv.org/html/2609.23053
- Claim-Locked Reporting — Fan et al., EMNLP 2026 (accepted): https://arxiv.org/html/2608.25336
- Faithful by Construction (CAMS) — Guan, UBS, Jul 2026 (preprint): https://arxiv.org/html/2606.23989v2

### Checking support / judges
- MiniCheck — Tang, Laban, Durrett, EMNLP 2024 (peer-reviewed): https://aclanthology.org/2024.emnlp-main.499/
- LLM-AggreFact leaderboard: https://llm-aggrefact.github.io/blog
- FACTS Grounding — Google DeepMind 2025: https://www.alphaxiv.org/overview/2501.03200v1
- Replacing Judges with Juries (PoLL) — Verga et al., 2024: https://huggingface.co/papers/2404.18796
- Who Validates the Validators? — Shankar et al., UIST 2024 (peer-reviewed): https://arxiv.org/abs/2404.12272
- Reliability without Validity — Norman et al., Berkeley, Jun 2026 (preprint): https://arxiv.org/html/2606.19544v1

### Abstention
- Trust-Align / Trust-Score — Song et al., ICLR 2025 oral (peer-reviewed): https://arxiv.org/abs/2409.11242
- FaithEval — Ming et al., Salesforce, ICLR 2025 (peer-reviewed): https://arxiv.org/html/2410.03727
- Know Your Limits (abstention survey) — Wen et al., TACL 2025 (peer-reviewed): https://aclanthology.org/2025.tacl-1.26/

### Conflicting / versioned sources
- DRAGged into Conflicts — Cattan et al., Google Research 2025: https://www.alphaxiv.org/overview/2506.08500v2
- ClashEval — Wu, Wu, Zou, NeurIPS 2024 D&B (peer-reviewed): https://arxiv.org/abs/2404.10198
- Knowledge Conflicts for LLMs: A Survey — Xu et al., EMNLP 2024 (peer-reviewed): https://arxiv.org/abs/2403.08319

### Prompt injection
- Spotlighting — Hines et al., Microsoft 2024: https://www.alphaxiv.org/abs/2403.14720
- Design Patterns for Securing LLM Agents against Prompt Injections — Beurer-Kellner et al., 2025: https://arxiv.org/abs/2506.08837 (summary: https://simonwillison.net/2025/Jun/13/prompt-injection-design-patterns/)
- CaMeL: Defeating Prompt Injections by Design — Debenedetti et al., SaTML 2026: https://css.csail.mit.edu/6.858/2026/readings/camel.pdf

### Answer reuse
- vCache: Verified Semantic Prompt Caching — ICLR 2026 (peer-reviewed): https://arxiv.org/abs/2502.03771
- Vanta Questionnaire Automation implementation guide (vendor doc): https://help.vanta.com/en/articles/11488356-vanta-questionnaire-automation-implementation-guide

### Evaluation
- τ-bench (pass^k) — Yao et al., 2024: https://arxiv.org/abs/2406.12045
- Adding Error Bars to Evals — Miller, 2024: https://arxiv.org/abs/2411.00640
- Demystifying evals for AI agents — Anthropic, Jan 2026 (vendor blog): https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- Let Me Speak Freely? — Tam et al., EMNLP 2024 Industry (peer-reviewed): https://aclanthology.org/2024.emnlp-industry.91/
- Both Ends Count! Text-to-"Big SQL" — Eizaguirre et al., EuroMLSys 2026 (accuracy + cost/latency): https://arxiv.org/html/2602.21480v4
- EnterpriseVal — Ali et al., Sep 2026, MLSys 2027 (preprint): https://arxiv.org/html/2609.21841v1

### Model and API docs
- Gemini 3 developer guide: https://ai.google.dev/gemini-api/docs/gemini-3
- Gemini models: https://ai.google.dev/gemini-api/docs/models
- Gemini File Search: https://ai.google.dev/gemini-api/docs/generate-content/file-search
- Claude models overview: https://platform.claude.com/docs/en/about-claude/models/overview
- Claude Citations: https://platform.claude.com/docs/en/build-with-claude/citations
- Claude strict tool use: https://platform.claude.com/docs/en/agents-and-tools/tool-use/strict-tool-use
- Claude prompting best practices (long context, quotes first): https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- Anthropic: Writing effective tools for agents: https://www.anthropic.com/engineering/writing-tools-for-agents
- LangGraph v1 release notes: https://docs.langchain.com/oss/python/releases/langgraph-v1
- LangChain built-in middleware: https://docs.langchain.com/oss/python/langchain/middleware/built-in

### Role context
- Provectus job post (Junior AI/ML Engineer, GenAI, AWS): https://jobs.lever.co/provectus/af2e5b71-9860-4dd1-a3b1-98341b6d2060
