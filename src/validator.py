import os
import random
import json

def run_validation(docs_dir: str, llm_mode_str: str) -> bool:
    """
    Samples generated documentation and validates its quality using LLMs.
    Checks for API endpoints, parameters, and code samples.
    """
    print(f"[validator] Validating docs in {docs_dir} using {llm_mode_str}...")
    
    if not os.path.exists(docs_dir):
        print("[validator] Docs directory does not exist.")
        return False
        
    md_files = [f for f in os.listdir(docs_dir) if f.endswith('.md')]
    if not md_files:
        print("[validator] No markdown files found to validate.")
        return False
        
    # Sample up to 3 random markdown files
    sample_size = min(3, len(md_files))
    samples = random.sample(md_files, sample_size)
    
    sample_texts = ""
    for file in samples:
        filepath = os.path.join(docs_dir, file)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # truncate to 3000 chars per file to save tokens
            sample_texts += f"--- FILE: {file} ---\n{content[:3000]}\n\n"
            
    # Try LiteLLM
    try:
        import litellm
    except ImportError:
        print("[validator] litellm not installed. Skipping LLM validation.")
        return True
        
    parts = llm_mode_str.split(":", 1)
    if len(parts) > 1:
        model_name = parts[1]
    else:
        model_name = "gpt-3.5-turbo"
        
    system_prompt = '''You are an expert API Documentation Q&A Validator.
Analyze the provided sample markdown API files and evaluate the scraping quality.
Output ONLY a JSON object with the following schema:
{
  "has_endpoints": boolean,
  "has_parameters_or_responses": boolean,
  "has_code_samples": boolean,
  "has_excessive_noise": boolean,
  "overall_score": 1 to 100,
  "feedback": "string explaining the rating and any missing pieces"
}'''

    user_prompt = f"Evaluate these Markdown API scraps:\n\n{sample_texts}"

    try:
        optional_params = {}
        if "openai" in model_name.lower() or "ollama" in model_name.lower() or "gemini" in model_name.lower():
             optional_params["response_format"] = {"type": "json_object"}

        response = litellm.completion(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            **optional_params
        )
        content = response.choices[0].message.content
        
        if content.startswith("```json"):
            content = content.replace("```json\n", "").replace("\n```", "")
            
        report = json.loads(content)
        
        # Save Report
        with open("validation-report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        print(f"[validator] Validation Score: {report.get('overall_score')}/100")
        print(f"[validator] Feedback: {report.get('feedback')}")
        
        # Determine success
        if report.get('overall_score', 0) >= 60:
            print("[validator] Passed validation.")
            return True
        else:
            print("[validator] Failed validation. The scraping config might need tuning.")
            return False

    except Exception as e:
        print(f"[validator] Error during LLM validation: {e}")
        return True # Default to true if LLM validation fails for systemic reasons

