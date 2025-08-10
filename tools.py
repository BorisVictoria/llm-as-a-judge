import streamlit as st
from groq import Groq
import json
from comet import download_model, load_from_checkpoint
import numpy as np

def evaluate_translation_with_reflection(source_en, candidate_fil, reference_fil="", domain_guidelines=""):
    """
    Performs translation evaluation with reflection loop
    """
    while True:
        try:
          client = Groq(api_key=st.secrets["GROQ_API_KEY"])
          model = "moonshotai/kimi-k2-instruct"
    
          # Stage 1: Initial Evaluation
          initial_prompt = f"""You are a translation quality judge for ENGLISH → FILIPINO translations. Your job is to evaluate one translation pair at a time using exactly the six criteria listed below: Accuracy, Fluency, Coherence, Cultural Appropriateness, Guideline Adherence, and Completeness. Each criterion is worth 1 point. Sum the points then map to a final numerical score 1–5 using this rule:
 - Sum 5–6 → 5
 - Sum 3–4 → 3
 - Sum 0–2 → 1

Evaluate the following translation pair. ALWAYS return valid JSON only, with the exact keys shown in the JSON schema. Do NOT include chain-of-thought or extra text. Return only raw JSON without any markdown code fences or syntax highlighting.

INPUT:
{{
  "source_en": "{source_en}",
  "candidate_fil": "{candidate_fil}",
  "reference_fil": "{reference_fil}",
  "domain_guidelines": "{domain_guidelines}"
}}

JSON_SCHEMA:
{{
  "score": integer,             // 1-5 final mapped score
  "sum_of_criteria": integer,   // 0-6 raw sum of criteria points
  "label": string,              // "excellent" (5), "good" (3), "poor" (1)
  "criteria": {{
    "Accuracy": {{ "point": 0|1, "reason": string }},
    "Fluency": {{ "point": 0|1, "reason": string }},
    "Coherence": {{ "point": 0|1, "reason": string }},
    "Cultural Appropriateness": {{ "point": 0|1, "reason": string }},
    "Guideline Adherence": {{ "point": 0|1, "reason": string }},
    "Completeness": {{ "point": 0|1, "reason": string }}
  }},
  "highlights": [              // optional; at least one item when point==0 for any criterion
    {{ "criterion": string, "source_span": string, "candidate_span": string, "explanation": string }}
  ],
  "suggested_fix": string,     // optional short corrected version or patch (if severe issues)
  "confidence": number         // 0-100; optional but recommended
}}"""

          # Get initial evaluation
          initial_response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": initial_prompt}],
            temperature=0.2,
            max_completion_tokens=2048
          )
          # print(initial_response.choices[0].message.content)
          initial_evaluation = json.loads(initial_response.choices[0].message.content)
    
          # Stage 2: Reflection Phase
          reflection_prompt = f"""You previously evaluated an English-to-Filipino translation. Now critically examine your own judgment for potential errors or oversights.

ORIGINAL EVALUATION:
{json.dumps(initial_evaluation, indent=2)}

TRANSLATION PAIR:
Source (English): "{source_en}"
Candidate (Filipino): "{candidate_fil}"
Reference (Filipino): "{reference_fil}"
Domain Guidelines: "{domain_guidelines}"

REFLECTION CHECKLIST - Answer each question honestly:

1. ACCURACY REFLECTION:
   - Did I miss any subtle meaning differences?
   - Are there alternative valid interpretations I didn't consider?
   - Did I properly assess semantic preservation?

2. FLUENCY REFLECTION:
   - Did I adequately assess Filipino grammatical correctness?
   - Are there natural Filipino expressions I might have overlooked?
   - Did I consider regional variation acceptability?

3. COHERENCE REFLECTION:
   - Does the translation maintain logical flow in Filipino context?
   - Did I check discourse markers and connectives properly?

4. CULTURAL APPROPRIATENESS REFLECTION:
   - Did I properly assess formality levels (po/opo usage)?
   - Are there cultural nuances I may have missed?
   - Did I consider appropriate Filipino social registers?

5. GUIDELINE ADHERENCE REFLECTION:
   - Did I apply domain-specific knowledge consistently?
   - Are there specialized terms I should reconsider?

6. COMPLETENESS REFLECTION:
   - Did I verify all source elements are represented?
   - Are there subtle omissions or inappropriate additions?

BIAS CHECK:
- Am I showing preference for longer/shorter translations?
- Am I consistently applying Filipino linguistic standards?
- Did I consider multiple valid translation approaches?

Return only raw JSON without any markdown code fences or syntax highlighting with your reflection analysis:
{{
  "reflection_findings": {{
    "concerns_identified": [list of specific concerns],
    "confidence_issues": [criteria where you have lower confidence],
    "potential_bias_detected": string,
    "missed_considerations": [things you may have overlooked]
  }},
  "recommendation": "maintain" | "revise",
  "revision_needed_for": [list of criteria that should be reconsidered]
}}"""

          # Get reflection analysis
          reflection_response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": reflection_prompt}],
            temperature=0.2,
            max_completion_tokens=2048
          )
          # print(reflection_response.choices[0].message.content)
          reflection_analysis = json.loads(reflection_response.choices[0].message.content)
    
          # Stage 3: Final Evaluation (if revision needed)
          if reflection_analysis.get("recommendation") == "revise":
            revision_prompt = f"""Based on your reflection analysis, provide a REVISED evaluation of the translation pair. Consider the concerns you identified and provide an updated assessment.

ORIGINAL EVALUATION:
{json.dumps(initial_evaluation, indent=2)}

REFLECTION FINDINGS:
{json.dumps(reflection_analysis, indent=2)}

TRANSLATION PAIR:
Source (English): "{source_en}"
Candidate (Filipino): "{candidate_fil}"
Reference (Filipino): "{reference_fil}"
Domain Guidelines: "{domain_guidelines}"

Provide your FINAL revised evaluation using the same JSON schema as before. Include a "revision_notes" field explaining what you changed and why.
Return only raw JSON without any markdown code fences or syntax highlighting. Make sure that the score match the sum_of_criteria. Recall that 5-6 -> 5, 3-4 -> 3, 0-2 -> 1.
JSON_SCHEMA (same as before, plus):
{{
  "score": integer,
  "sum_of_criteria": integer,
  "label": string,
  "criteria": {{ ... }},
  "highlights": [...],
  "suggested_fix": string,
  "confidence": number,
  "revision_notes": string  // NEW: explain changes made during reflection
}}"""

            # Get final evaluation
            final_response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": revision_prompt}],
                temperature=0.2,
                max_completion_tokens=2048
            )
            # print(final_response.choices[0].message.content)
            final_evaluation = json.loads(final_response.choices[0].message.content)
          else:
            final_evaluation = initial_evaluation
            final_evaluation["revision_notes"] = "No revision needed after reflection"
    
          # Compile complete result
   
          result = {
            "initial_evaluation": initial_evaluation,
            "reflection_analysis": reflection_analysis,
            "final_evaluation": final_evaluation,
            "reflection_triggered": reflection_analysis.get("recommendation") == "revise"
          }
          # print(result)
          return result
        except Exception as e:
           print(f"We encountered an error but we will try again kekw. {e}")

def predict_translation_quality(
    source_en: str, 
    candidate_fil: str, 
    model_name: str = "Unbabel/wmt20-comet-qe-da"
) -> dict:
    try:
        # Download and load the model (cached after first run)
        model_path = download_model(model_name)
        model = load_from_checkpoint(model_path)
        
        # Prepare input data
        data = [{"src": source_en, "mt": candidate_fil}]
        
        # Predict quality score
        model_output = model.predict(data, batch_size=1, gpus=0)  # Use gpus=1 if available
        
        # Extract scores and convert to interpretable metrics
        score = float(np.mean(model_output.scores))
        return {
            "comet_score": score,
            "interpretation": interpret_comet_score(score),
            "model": model_name,
            "warnings": [] if score > 0.5 else ["Low quality detected"]
        }
    except Exception as e:
        return {"error": str(e), "comet_score": None}
    
def interpret_comet_score(score: float) -> str:
    if score >= 0.8:
        return "Excellent (Likely indistinguishable from human translation)"
    elif score >= 0.6:
        return "Good (Minor errors, but meaning preserved)"
    elif score >= 0.4:
        return "Fair (Noticeable errors, but understandable)"
    else:
        return "Poor (Significant distortion or nonsense)"