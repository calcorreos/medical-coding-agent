import os
import json
import tqdm
import time
from google import genai
import difflib
from utils import load_environment, logger, extract_text_from_pdf, save_json, load_json, parse_answer_key, parse_answer_key_content
from agents import configure_genai, ParserAgent, ExpertAgent, EvaluatorAgent

def main():
    load_environment()
    try:
        configure_genai()
    except ValueError as e:
        logger.error(e)
        print(f"Error: {e}")
        return

    # File paths
    input_pdf = "data/practice_test_no_answers (1) (3) (1).pdf"
    answer_key_pdf = "data/practice_test_answers (1) (3) (1).pdf"
    output_file = "data/final_results.json"
    
    # 1. Parsing
    if os.path.exists("data/questions.json"):
        logger.info("Loading existing questions.json...")
        questions = load_json("data/questions.json")
    else:
        logger.info("Parsing PDF...")
        raw_text = extract_text_from_pdf(input_pdf)
        if not raw_text:
            logger.error("No text extracted. Exiting.")
            return
        
        # Split text into chunks to avoid token limits if necessary
        # For simplicity, assuming one shot or user can split manually if it fails
        # A 100q test is likely long. Let's do a naive split by lines or roughly.
        # Actually, let's try to parse the whole thing. The 1M (or 2M) context window of Gemini 1.5 Pro should handle it easily!
        parser = ParserAgent()
        questions = parser.parse(raw_text)
        if not questions:
            logger.error("Parsing failed.")
            return
        save_json(questions, "questions.json")

    # Limit for testing/demonstration due to Free Tier Rate Limits (5 RPM)
    # PAID TIER CONFIRMED: Processing all questions at full speed.
    # VERIFICATION RUN: Retrying Batch 2 (Q11-Q20) with new prompts.
    # questions = questions[10:20] 

    # 2. Research & Evaluation
    expert = ExpertAgent()
    evaluator = EvaluatorAgent()
    
    results = []
    
    # Load previous results if resuming?
    # For now, start fresh or overwrite

    # Load answer key early for real-time grading/stopping logic
    answer_key = parse_answer_key(answer_key_pdf)
    answer_key_content = parse_answer_key_content(answer_key_pdf)
    
    def check_content_match(user_question, key_content_map):
        """Returns True if the user question likely matches the key question."""
        uid = str(user_question.get('id'))
        if uid not in key_content_map:
            return False
            
        key_text = key_content_map[uid]
        user_text = user_question.get('question', '')
        
        # Fuzzy match using first 100 chars
        s = difflib.SequenceMatcher(None, user_text[:100], key_text[:100])
        return s.ratio() > 0.8 # 80% similarity threshold
    if not answer_key:
        logger.warning("Could not parse answer key. Real-time accuracy check disabled.")

    batch_size = 10
    total_questions = len(questions)
    
    for i in range(0, total_questions, batch_size):
        batch = questions[i : i + batch_size]
        logger.info(f"Starting Batch {i//batch_size + 1}: Questions {i+1} to {min(i+batch_size, total_questions)}")
        
        batch_results = []

        for q in tqdm.tqdm(batch, desc=f"Processing Batch {i//batch_size + 1}"):
            # Check if already processed (idempotency could be added)
            # PAID TIER: No sleep needed.
            # time.sleep(35) 
            
            # Research
            research_notes = expert.research(q)
            q['research_notes'] = research_notes
            
            # Evaluate
            evaluation = evaluator.evaluate(q, research_notes)
            q['selected_option'] = evaluation.get('selected_option')
            q['rationale'] = evaluation.get('rationale')
            
            batch_results.append(q)
            results.append(q)
            
            # Save incrementally
            save_json(results, output_file)

        # Batch Grading & Early Stopping
        if answer_key:
            correct_count = 0
            for q in batch_results:
                qid = str(q.get('id'))
                selected = q.get('selected_option', '').strip().upper()
                correct = answer_key.get(qid, '').strip().upper()
                if selected == correct:
                    correct_count += 1
            
            batch_score = (correct_count / len(batch_results)) * 100
            logger.info(f"Batch {i//batch_size + 1} Score: {correct_count}/{len(batch_results)} ({batch_score:.1f}%)")
            
            if batch_score < 70.0:
                logger.warning(f"Batch accuracy ({batch_score:.1f}%) is low. Continuing for Heuristic Optimization.")
                # No early stopping during audit phase
    else:
        logger.info("All batches completed successfully.")

    # 3. Grading & Report
    logger.info("Grading results...")
    # Answer key already parsed above
    
    if not answer_key:
        logger.warning("Could not parse answer key. Skipping auto-grading.")
    
    score = 0
    total = len(results)
    
    # Identify missed questions for reflection
    missed_questions = []
    
    for q in results:
        qid = str(q.get('id'))
        selected = q.get('selected_option', '').strip().upper()
        correct = answer_key.get(qid, '').strip().upper()
        
        if selected != correct and correct:
            q['correct_answer'] = correct
            missed_questions.append(q)

    # 4. Self-Reflection Loop
    if missed_questions:
        logger.info(f"Reflecting on {len(missed_questions)} missed questions...")
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        
        for q in tqdm.tqdm(missed_questions, desc="Reflecting"):
            prompt = f"""
            You previously answered this medical coding question incorrectly.
            
            Question: {q.get('question')}
            Options: {q.get('options')}
            
            Your Research: {q.get('research_notes')}
            Your Selected Answer: {q.get('selected_option')}
            Actual Correct Answer: {q.get('correct_answer')}
            
            Task:
            Analyze WHY you got it wrong. Was it a missed hierarchy rule? A misunderstanding of the modifier? Misreading the text?
            Provide a brief "Self-Reflection" explaining the error and the correct logic.
            """
            
            try:
                response = client.models.generate_content(
                    model="gemini-2.0-flash-001",
                    contents=prompt
                )
                q['self_reflection'] = response.text
            except Exception as e:
                logger.error(f"Reflection failed for Q{q.get('id')}: {e}")
                q['self_reflection'] = "Reflection failed."
                
    # Generate Report
    report_lines = ["# Medical Coding Practice Test Walkthrough (Dual Score Audit)\n\n"]
    
    # Calculate Dual Scores
    total_processed = len(results)
    raw_correct = 0
    verified_correct = 0
    verified_total = 0
    
    mismatched_questions = []

    for q in results:
        qid = str(q.get('id'))
        is_match = check_content_match(q, answer_key_content)
        
        selected = q.get('selected_option', '').strip().upper()
        correct = answer_key.get(qid, '').strip().upper()
        
        is_correct = (selected == correct)
        
        if is_correct:
            raw_correct += 1
            if is_match:
                verified_correct += 1
        
        if is_match:
            verified_total += 1
        else:
            mismatched_questions.append(qid)

    raw_score = (raw_correct / total_processed * 100) if total_processed else 0
    verified_score = (verified_correct / verified_total * 100) if verified_total else 0

    logger.info(f"Raw Score: {raw_correct}/{total_processed} ({raw_score:.1f}%)")
    logger.info(f"Audit Score (Verified Content): {verified_correct}/{verified_total} ({verified_score:.1f}%)")

    report_lines.append(f"**Raw Score**: {raw_correct}/{total_processed} ({raw_score:.1f}%)")
    report_lines.append(f"**Audit Score (Verified Content)**: {verified_correct}/{verified_total} ({verified_score:.1f}%)")
    
    if mismatched_questions:
        report_lines.append(f"\n> [!WARNING] Mismatched Questions Detected (Excluded from Audit Score): {', '.join(mismatched_questions)}")

    report_lines.append(f"\n**Date**: {time.strftime('%Y-%m-%d')}\n")
    report_lines.append("\n---\n")
    score = len(results) - len(missed_questions)
    
    report_lines.append(f"**Final Score**: {score}/{total} ({(score/total)*100:.1f}%)\n")
    report_lines.append(f"**Date**: {time.strftime('%Y-%m-%d')}\n\n")
    report_lines.append("---\n")
    
    for q in results:
        qid = str(q.get('id'))
        selected = q.get('selected_option', '').strip().upper()
        correct = answer_key.get(qid, '').strip().upper() if answer_key else "?"
        
        is_correct = (selected == correct)
        status = "✅ CORRECT" if is_correct else "❌ INCORRECT"
        
        report_lines.append(f"## Question {qid} - {status}\n")
        report_lines.append(f"**Question**: {q.get('question')}\n\n")
        report_lines.append(f"**Selected**: {selected}\n")
        if correct:
            report_lines.append(f"**Correct Answer**: {correct}\n")
        
        report_lines.append(f"**Rationale**:\n{q.get('rationale')}\n\n")
        
        if not is_correct and 'self_reflection' in q:
             report_lines.append(f"> [!WARNING] Self-Reflection\n> {q.get('self_reflection')}\n\n")
             
        report_lines.append(f"**Research Notes**:\n_{q.get('research_notes')}_\n")
        report_lines.append("---\n")

    with open("walkthrough.md", "w") as f:
        f.writelines(report_lines)
    
    logger.info(f"Complete. Score: {score}/{total}. Report saved to walkthrough.md")

if __name__ == "__main__":
    import time
    main()
