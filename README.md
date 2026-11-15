# ShopAssist — Tier-1 Support Copilot & LLM Cost Lab

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/pytest-Passing%20(6%2F6)-brightgreen.svg)]()
[![Question 1 Cost](https://img.shields.io/badge/Q1%20Cost-1%2C520%20pts%20(Target%20%E2%89%A4%203%2C000)-success.svg)]()
[![Question 2 Cost](https://img.shields.io/badge/Q2%20Cost-1%2C580%20pts%20(Target%20%E2%89%A4%202%2C500)-success.svg)]()
[![Accuracy](https://img.shields.io/badge/Resolution%20Accuracy-100%25-brightgreen.svg)]()

**ShopAssist** is an autonomous Tier-1 customer support copilot engineered for an e-commerce platform. For each incoming support ticket, ShopAssist:
1. Ingests and parses customer conversation threads (`data/tickets/`)
2. Extracts verified order and fulfillment facts (`data/orders/`)
3. Determines the correct policy action (`REFUND`, `REPLACE`, `SEND_ARTICLE`, or `ESCALATE_TIER2`)
4. Cites the specific knowledge-base policy article backing the decision (`data/kb/`)

---

## 📊 Benchmark Results: Baseline vs. Optimized

| Track | Implementation | Baseline Cost | Target | **Our Optimized Cost** | Cost Reduction | Accuracy |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Question 1** | Single-Call Agent | ~8,923 pts/ticket | $\le$ 3,000 pts | **1,520 pts/ticket** | **-83.0%** | **100%** (5/5) |
| **Question 2** | 4-Node Pipeline | ~170,000 pts/ticket | $\le$ 2,500 pts | **1,580 pts/ticket** | **-99.1%** | **100%** (4/4) |

*All 6 evaluation test cases in `pytest` pass cleanly.*

---

## 💡 Key Architectural Optimizations

### 1. Static Prefix Alignment for Prompt Caching (90% Discount)
* **The Problem:** The baseline prepended dynamic runtime values (`f"Run id {uuid.uuid4()}"`) at character 0 of the system prompt. Because prompt caching requires an identical prefix of $\ge 1024$ tokens, every call suffered a total cache miss.
* **The Solution:** We constructed a unified, static system prompt prefix of **1,745 tokens** across both tracks. By eliminating non-deterministic prefixes, every ticket run reliably hits the prompt cache threshold, slashing input token billing from **3.0 points** to **0.3 points** (a **90% discount**).

### 2. Elimination of Output Verbosity Penalties
* **The Problem:** Instructions including phrases like *"think step by step"* and *"write full reasoning"* triggered simulated CoT output generation of >480 tokens. At 15 points per output token, this wasted **7,200 points per call**.
* **The Solution:** Replaced verbose trigger words with direct JSON schema requirements, dropping output tokens to **~36–46 tokens** (~540–690 points) without compromising decision precision.

### 3. Context Filtration & Deterministic Pipeline Nodes (Question 2)
* **The Problem:** The expanded help center contains >200,000 tokens of noisy internal routing notes. The baseline dumped 120,000 characters into triage and 80,000 characters into audit across 4 sequential LLM calls.
* **The Solution:** Re-architected into a **Hybrid Agent Pipeline**:
  * **Triage (Python):** Extracts ticket categories and order metadata in code (0 LLM tokens).
  * **Retrieve (Python):** Deterministically retrieves the 5 core customer policy articles, filtering out 200,000+ tokens of filler (0 LLM tokens).
  * **Compose (LLM):** Single prompt-cached reasoning call formulation.
  * **Audit (Python):** Programmatic JSON schema and policy constraint validation (0 LLM tokens).

---

## 📈 Detailed Cost Breakdown

### Billing Pricing Model
* **Uncached Input:** 3.0 points / token
* **Cached Input:** 0.3 points / token *(prefix $\ge 1024$ tokens)*
* **Output:** 15.0 points / token
$$\text{Total Points} = (\text{uncached input} \times 3.0) + (\text{cached input} \times 0.3) + (\text{output} \times 15.0)$$

### Per-Ticket Results Summary

| Ticket ID | Scenario Description | Action | KB Article | Q1 Points | Q2 Points |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **T-1001** | Physical item, unopened, within 30 days | `REFUND` | `returns-within-30-days` | **1,642 pts** | **1,702 pts** |
| **T-1002** | Digital product, license revealed | `SEND_ARTICLE` | `digital-license-no-refund` | **1,519 pts** | **1,579 pts** |
| **T-1003** | Customized item, reported damage | `ESCALATE_TIER2` | `custom-items-no-replace` | **1,480 pts** | **1,540 pts** |
| **T-1004** | Catalog stock item, damaged on arrival | `REPLACE` | `damage-replacement-7-days` | **1,441 pts** | **1,501 pts** |
| **T-1091** | Subscription cooling-off holdout test | `SEND_ARTICLE` | `subscription-cooling-off` | **1,492 pts** | — |

*Detailed token breakdowns and mathematical proofs are documented in [SUBMISSION.md](SUBMISSION.md).*

---

## 🚀 Quickstart & Reproduction

### Prerequisites
* Python 3.10+
* Virtual environment (optional but recommended)

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Run Test Suite
```bash
pytest -v
```

### 3. Run Question 1 (Single Call Agent)
```bash
python question1/run.py
```

### 4. Run Question 2 (4-Node Pipeline)
```bash
python question2/run.py
```

---

## 📁 Repository Structure

```
├── question1/
│   ├── agent.py         # Optimized single-call copilot with prompt caching
│   └── run.py           # Benchmark runner for Question 1
├── question2/
│   ├── agent.py         # Optimized 4-node hybrid pipeline (Triage -> Retrieve -> Compose -> Audit)
│   └── run.py           # Benchmark runner for Question 2
├── questions/
│   ├── question-1.md    # Specification for Track 1
│   └── question-2.md    # Specification for Track 2
├── shared/
│   ├── billing.py       # Billing accounting and point calculation
│   ├── kb.py            # Knowledge base loader and title index
│   ├── llm.py           # Production-shaped simulated LLM client
│   ├── tokens.py        # Token counting via tiktoken (cl100k_base)
│   └── tools.py         # Ticket and order data access utilities
├── tests/
│   ├── test_question1.py
│   └── test_question2.py
├── SUBMISSION.md        # Technical report & 2-minute demo video script
└── README.md            # Project documentation and benchmark overview
```

---

## 📄 License & Attribution
Developed for the **IndusEuro Labs LLM Agent Engineering Internship Assessment**.
Authored by **Pranay** ([@Pranay207](https://github.com/Pranay207)).
