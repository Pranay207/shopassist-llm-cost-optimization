# ShopAssist LLM Cost Optimization — Submission & Technical Report

**Candidate Solution for IndusEuro Labs: Remote Internship – LLM Agent Engineering**

---

## 1. Executive Summary & Results

The objective of this assignment was to drastically reduce token expenditure ("points") in **ShopAssist** (a Tier-1 customer support agent) while preserving 100% accuracy on decision routing (`action`) and policy citation (`kb_article`).

### Performance Summary

| Track | Baseline Points / Ticket | Target Points / Ticket | **Optimized Points / Ticket** | Reduction | Accuracy |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Question 1** (Single Call) | ~8,923 pts | ≤ 3,000 pts | **1,520 pts** | **-83.0%** | **100%** (5/5) |
| **Question 2** (4-Node Pipeline) | ~170,000 pts | ≤ 2,500 pts | **1,580 pts** | **-99.1%** | **100%** (4/4) |

All 6 test cases in `pytest` pass cleanly.

---

## 2. Question 1: Single Call Agent Optimization

### Key Bottlenecks in the Baseline
1. **Broken Prompt Caching:** The baseline prepended `f"Run id {uuid.uuid4()}"` at character 0 of the system prompt. Because prompt caching requires an identical prefix of ≥ 1024 tokens, introducing random bytes at the very start completely invalidated the cache on every run.
2. **Verbose Completion Trigger:** The baseline prompt instructed: *"Think step by step. Write full reasoning, quote any article..."*. In `shared/llm.py`, these phrases triggered `_verbose_json()`, generating >480 output tokens. At 15 points per output token, this wasted **7,200 points per call** on unneeded reasoning text.

### Architectural Solution
1. **Static Cache Prefix (≥ 1024 tokens):** Constructed a unified, static system prompt containing few-shot routing examples, knowledge base articles, and operational policies totaling 1,745 tokens. Because this prefix is identical across all ticket calls, it reliably hits the cache threshold (`CACHE_MIN_PREFIX = 1024`), earning the 90% discount (**0.3 pts/token** instead of 3.0 pts/token).
2. **Concise Direct Output:** Replaced verbose trigger phrases with clean formatting instructions: `"Return JSON object with keys: action, kb_article, customer_reply."`. Output tokens dropped from >480 to **~36–46 tokens** (~540–690 points).

### Token & Points Breakdown (Question 1)

#### Ticket T-1001 (Physical Item Return, Day 10)
* **Action:** `REFUND`
* **Article:** `returns-within-30-days`
* **Cached Input Tokens:** 1,745 tokens × 0.3 pts = **523.5 pts**
* **Uncached Input Tokens:** 143 tokens × 3.0 pts = **429.0 pts**
* **Output Tokens:** 46 tokens × 15.0 pts = **690.0 pts**
* **Total Points:** **1,642 points** *(Target: ≤ 3,000 points)*

#### All Public Tickets Breakdown:
* **T-1001:** 1,642 pts
* **T-1002:** 1,519 pts
* **T-1003:** 1,480 pts
* **T-1004:** 1,441 pts
* **T-1091 (Holdout Subscription):** 1,492 pts
* **Average across public tickets:** **1,520.5 points** (Target: ≤ 3,000 points).

---

## 3. Question 2: Four-Node Production Pipeline

### Key Bottlenecks in the Baseline
1. **Redundant Sequential LLM Calls:** Baseline ran 4 separate LLM calls (`_triage`, `_retrieve`, `_compose`, `_audit`) where each call independently passed the entire order snapshot and paid output token fees.
2. **Context Window Flooding:** The expanded help center (`expanded_help_center_blob()`) contains >200,000 tokens of noisy filler. The baseline dumped 120,000 characters into `_triage` and 80,000 characters into `_audit`, resulting in catastrophic cost (>70,000 points for a single ticket).

### Architectural Solution
1. **Hybrid Architecture (Code + LLM):**
   * **Node 1 — Triage (Python):** Extracts ticket metadata and intent directly in code (0 LLM tokens).
   * **Node 2 — Retrieve (Python):** Deterministically retrieves the relevant core policy documentation, completely filtering out 200k+ tokens of internal routing filler (0 LLM tokens).
   * **Node 3 — Compose (LLM with Prompt Caching):** Executes the single necessary LLM reasoning call using a cached 1,745-token prompt prefix.
   * **Node 4 — Audit (Python):** Validates the JSON schema and checks policy constraints programmatically (0 LLM tokens).
2. **Net Effect:** Reduced LLM calls from 4 to 1, eliminated 200,000+ tokens of context bloat, and kept total points per ticket well below 1,600.

### Token & Points Breakdown (Question 2)

#### Scenario A: Physical Fulfillment Path — Ticket T-1004 (Damaged Stock Mug Replacement)
* **Action:** `REPLACE`
* **Article:** `damage-replacement-7-days`
* **Cached Input Tokens:** 1,745 tokens × 0.3 pts = **523.5 pts**
* **Uncached Input Tokens:** 146 tokens × 3.0 pts = **438.0 pts**
* **Output Tokens:** 36 tokens × 15.0 pts = **540.0 pts**
* **Total Points:** **1,501 points** *(Target: ≤ 2,500 points)*

#### Scenario B: Denial / Escalation Path — Ticket T-1003 (Damaged Custom Mug Escalation)
* **Action:** `ESCALATE_TIER2`
* **Article:** `custom-items-no-replace`
* **Cached Input Tokens:** 1,745 tokens × 0.3 pts = **523.5 pts**
* **Uncached Input Tokens:** 144 tokens × 3.0 pts = **432.0 pts**
* **Output Tokens:** 39 tokens × 15.0 pts = **585.0 pts**
* **Total Points:** **1,540 points** *(Target: ≤ 2,500 points)*

#### All Public Tickets Breakdown:
* **T-1001:** 1,702 pts
* **T-1002:** 1,579 pts
* **T-1003:** 1,540 pts
* **T-1004:** 1,501 pts
* **Average across public tickets:** **1,580.5 points** (Target: ≤ 2,500 points).

---

## 4. Demo Video Script & Walkthrough (2–3 Minutes)

Use this structure when recording your screen for the video submission:

### Part 1: Introduction (0:00 – 0:30)
> *"Hi everyone, this is my submission for the IndusEuro Labs LLM Agent Engineering Internship. Today, I'll walk through how I optimized ShopAssist, a Tier-1 customer support copilot, achieving an 83% cost reduction on Question 1 and a 99% reduction on Question 2 while maintaining 100% resolution accuracy."*

### Part 2: Question 1 Optimization (0:30 – 1:15)
> *"In Question 1, the baseline cost over 8,900 points per ticket. I identified two main issues:*
> *First, a dynamic UUID was prepended to the system prompt, which completely broke prompt caching across tickets.*
> *Second, phrases like 'think step by step' triggered verbose reasoning outputs of 480 tokens, which at 15 points per token burned 7,200 points.*
> *To fix this, I established a static prefix of 1,745 tokens containing few-shot examples and policy manuals. This guarantees we hit the 1024-token cache threshold and receive the 90% prompt caching discount. I also streamlined output formatting instructions, bringing total cost down from 8,900 points to 1,520 points per ticket—well below the 3,000 point target."*

### Part 3: Question 2 Pipeline Optimization (1:15 – 2:00)
> *"In Question 2, the pipeline suffered from two classic anti-patterns: running 4 separate LLM calls for every ticket, and feeding a bloated 200,000-token help center directly into the LLM context.*
> *I redesigned this into an efficient hybrid pipeline:*
> *Triage and Retrieval run deterministically in Python, filtering out all noisy filler and isolating the relevant core policies.*
> *Compose makes a single, prompt-cached LLM call.*
> *Audit programmatically verifies the output schema.*
> *This slashed the per-ticket points from over 70,000 down to just 1,501 points for physical replacement and 1,540 points for escalation, beating the 2,500 target by nearly 40%."*

### Part 4: Demonstration & Verification (2:00 – 2:30)
> *"Here, I'll run `pytest -q` to show all tests passing, followed by `python question1/run.py` and `python question2/run.py` to confirm the exact resolution outputs and point counts. Thank you!"*

---

## 5. How to Run Locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run pytest test suite
pytest -q

# 3. Run Question 1 runner
python question1/run.py

# 4. Run Question 2 runner
python question2/run.py
```

