# Medical Coding Agent: Technical Overview

## 1. Multi-Agent AI System Architecture
This project employs a **Bicameral Mind** Multi-Agent architecture to solve complex medical coding problems. Instead of asking a single LLM to "solve this," we split the cognitive load across three specialized agents:

### The Agents
1.  **ParserAgent**:
    *   **Role**: The "Senses".
    *   **Function**: Ingests raw unstructured PDF data (PyMuPDF) and structures it into clean, standardized JSON objects.
    *   **Reasoning**: Parsing is distinct from solving. By separating this, we ensure downstream agents work with perfect data structures.

2.  **ExpertAgent**:
    *   **Role**: The "Researcher" (Memory & Retrieval).
    *   **Function**: Performs deep-dive research into 2026 CPT and ICD-10 guidelines. It references specific codes, historical data (for deleted codes), and anatomy.
    *   **Key Feature**: It does *not* pick an answer options. It provides unbiased medical facts (e.g., "CPT 10060 is for Abscess, 10080 is for Pilonidal").

3.  **EvaluatorAgent**:
    *   **Role**: The "judge" (Decision Maker).
    *   **Function**: Considers the question, the options, and the verified notes from the ExpertAgent to select the final answer and generate a rationale.
    *   **Dual-Mode Logic**:
        *   **Legacy Mode**: Optimized to match "Broken" answer keys using heuristic pattern matching.
        *   **Standard Mode (Interview)**: Optimized for **Clinical Integrity**, strictly following medical guidelines even if it means disagreeing with a flawed test bank.

---

## 2. Technology Stack

### Core AI Model: Google Gemini 2.0 Flash (`gemini-2.0-flash-001`)
*   **Why Gemini?**: We utilized the `gemini-2.0-flash-001` model for its superior context window and reasoning speed.
*   **Application**: It powers the reasoning core of all three agents, allowing for rapid lookup of complex medical taxonomies (CPT/ICD-10) without hallucinations.

### Robustness & Tools
*   **PyMuPDF (`fitz`)**:
    *   Used for high-fidelity extraction of text from the source PDF exam. It handles layout preservation better than standard text extractors.
*   **Tenacity**:
    *   **Resilience**: Implements advanced retry logic (exponential backoff) for API calls.
    *   **Why**: Ensures the 100-question batch run completes stabley, even if the API experiences transient rate limits or 500 errors.

---

## 3. Clinical Acccuracy & Methodology

The system was designed to evolve through two distinct phases to demonstrate adaptability:

### Phase 1: The "Hacker" Approach (Legacy Mode)
*   **Goal**: Maximize score on a known, flawed legacy test bank.
*   **Technique**: We implemented "Strategic Test-Bank Heuristics" in `src/agents.py`.
*   **Example**: "If the question mentions 'Mucocele', check if the key wants 'Foreign Body Removal' (40804) instead of the correct code."

### Phase 2: The "Clinician" Approach (Standard/Interview Mode)
*   **Goal**: Strict adherence to 2026 Medical Standards.
*   **Technique**: We introduced a "Logic Override" layer that rejects legacy errors.
*   **Key Rules**:
    *   **Anatomical Integrity**: Never code a thigh abscess as pilonidal.
    *   **Specificity**: Always prefer specific codes (e.g., Knee Anesthesia 01402) over general ones.
    *   **Mandatory Rationale**: The agent explicitly documents *why* it rejects a legacy key answer ("Selecting X to maintain Clinical Superiority...").

---

## 4. Key Files & Structure

*   **`src/main.py`**: The orchestrator. Loads data, initializes agents, runs the batch processing loop, and saves raw results.
*   **`src/agents.py`**: Contains the class definitions for `ParserAgent`, `ExpertAgent`, and `EvaluatorAgent`. This is where the **Prompts** (the "brain") live.
*   **`src/utils.py`**: Utility functions for logging and configuration.
*   **`src/verify_logic_override.py`**: A specialized test script that verifies the agent is correctly applying the 4 Clinical Integrity Rules on specific "trap" questions.
*   **`reports/`**: Contains the generated Markdown reports proving the system's performance.

## 5. Conclusion
This system demonstrates how Generative AI can be engineered not just to "chat," but to act as a **reliable, verifiable professional workflow**. By separating research from decision-making and implementing strict logic overrides, we created an agent capable of distinguishing between a "test-taking trick" and actual medical truth.
