# Syntra Interview Prep Guide

Based on your implementation of the Medical Coding Agent and the specific job description provided, here is a breakdown of the questions you should expect and how to prepare.

## 1. The "Meta" Strategy (The Strongest Talking Point)

You discovered a critical insight: **The answer key was flawed (using outdated or incorrect logic), but the goal was to "score high."**

*   **Likely Question:** "You noticed the answer key had errors. Walk us through your decision-making process on how to handle that."
    *   **Your Answer:** Explain the "Dual Mode" architecture. You built a **Legacy Mode** to demonstrate you can hit the metric (reverse-engineering their logic) and an **Interview Mode** (Standard Mode) to demonstrate you can build a product that is actually *useful* and clinically accurate.
    *   **The "Why":** This proves you have "Product Sense" — you understand that in the real world (RCM), strict accuracy prevents denials, but in a test environment, hitting the metric proves capability.

## 2. Code & Architecture Questions

### "Why this Architecture?"
*   **Question:** "Why did you split the agent into Parser, Expert, and Evaluator? Why not one big prompt?"
*   **Answer:** Reliability and Debuggability.
    *   **Parser:** PDFs are messy; isolating this ensures clean input.
    *   **Expert:** Hallucination mitigation. Forcing an "Expert" step to retrieve context before answering grounds the "Evaluator" in facts.
    *   **Evaluator:** Separation of concerns. The evaluator makes the final decision based on the Expert's data, mimicking a "Coding Auditor" reviewing a coder's work.

### "Performance & Scaling"
*   **Question:** "Your agent takes about X minutes to run 100 questions. How would you speed this up to process 10,000 charts a night?"
*   **Answers to study:**
    *   **Parallelism:** You used `batch_process` with a semaphore. Explain how you'd scale this horizontally (e.g., AWS Lambda, queues like SQS) rather than just threading on one machine.
    *   **Caching:** "We call the LLM for every question. In production, we'd hash the clinical text and cache the codes if the exact text appears again (common for standard procedures)."
    *   **Smaller Models:** "We used Gemini 2.0 Flash. For simple cases (e.g., standard office visits), we could distill this into a smaller model or use regex/heuristics to save on cost/latency, only calling the Big LLM for complex cases."

### "The Tech Stack Gap"
*   **Question:** "You wrote this in Python, but our stack is Node/TypeScript. How would you port this?"
*   **Preparation:**
    *   Acknowledge that Python is the lingua franca of AI (libraries, data support), hence the choice for the take-home.
    *   Explain that the *architecture* (Prompt Engineering, Agent Logic, RAG) is language-agnostic.
    *   Mention **LangChain.js** or **Vercel AI SDK** as the TypeScript equivalents you'd use.

## 3. Role-Specific Technicals (The "Browser Automation Wizard" Part)

The JD emphasizes **"Browser Automation Wizards"** and **"Integrating in healthcare is hard and not pretty."** Your take-home was clean (PDF -> API), but the job is dirty (Scraping -> API).

### Key Study Concept: The Integration Layer
In the real world, you don't get a PDF. You have to log in to a portal (Citrix, Epic Hyperspace, etc.) to get the data.

*   **Likely Question:** "How would you design a system that needs to log into a slow insurance portal, navigate 5 pages, download a generic PDF, and then run your agent? What if the portal crashes?"
*   **Study Topics:**
    *   **Playwright / Puppeteer:** The standard for modern browser automation. Know how they differ from Selenium (faster, more stable, handles heavy JS better).
    *   **Resilience:** Retry logic (which you showed with `tenacity`!), exponential backoff, handling CAPTCHAs (conceptually).
    *   **Headless Browsers:** Running efficiently in AWS Lambda/Fargate.

### Key Study Concept: FHIR
They mentioned **FHIR** (Fast Healthcare Interoperability Resources).
*   **Question:** "Our partners send us FHIR resources. How would your agent handle a `Claim` resource instead of text?"
*   **Study:** Briefly read up on the **FHIR `Claim` and `Patient` resources**.
    *   *Answer:* "Instead of parsing raw text, we'd digest the structured JSON from the FHIR object. It's actually easier/cleaner than the PDF approach because the fields (Diagnosis codes, Procedure codes) are structured."

## 4. "Arm the Rebels" (Cultural Fit)

*   **Question:** "We fight insurance companies (The Empire) for clinics (The Rebels). Tell us about a time you had to deal with an unfair system."
    *   **Reference your Project:** You literally fought an unfair system (the Flawed Legacy Key) by proving it wrong with "Clinical Integrity Overrides." This is a perfect narrative fit for their culture.

## Summary Checklist for Study

1.  [ ] **TypeScript/Node Basics:** Be ready to read/write basic TS syntax since that's their daily language.
2.  [ ] **Playwright:** Watch a 10-minute crash course on what it does.
3.  [ ] **FHIR:** Glance at a sample FHIR JSON object.
4.  [ ] **Review your Overrides:** Memorize *one* specific example (e.g., The "Mucocele" Q17 or "Thigh Abscess" Q57) where the key was wrong and you fixed it. Being able to cite specific clinical codes from memory is impressive.

Good luck! You have a very strong submission here.
