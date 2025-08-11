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
    
def style_checker(
    source_en: str,
    candidate_fil: str,
    style_guidelines: str = "The translation should maintain a formal, technical tone."
) -> dict:

    prompt = f"""
    Analyze the style of the SOURCE (English) and TRANSLATION (Filipino) texts below.
    Focus on:
    1. Formality (formal, informal, neutral)
    2. Tone (technical, conversational, persuasive)
    3. Domain-appropriateness (e.g., medical, legal, casual)
    4. Consistency between source and translation

    GUIDELINES:
    {style_guidelines}

    SOURCE (English):
    {source_en}

    TRANSLATION (Filipino):
    {candidate_fil}

    Output a JSON with:
    - "source_style": Formality, tone, domain
    - "translation_style": Formality, tone, domain
    - "consistency_score": 0-100 (how well styles match)
    - "mismatches": List of style inconsistencies
    - "suggestions": How to fix mismatches
    """
    
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        response = client.chat.completions.create(
            model="moonshotai/kimi-k2-instruct",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,  # Lower for more deterministic output
            response_format={"type": "json_object"}  # Force JSON output
        )
        
        # Parse LLM response
        evaluation = json.loads(response.choices[0].message.content)
        evaluation["manual"] = f"""
This manual outlines the key principles and specific criteria for evaluating the quality of English to Filipino translations. It emphasizes understanding the translator's purpose, the nature of the source text, and the needs of the target audience, going beyond mere word-for-word equivalence.
I. General Translation Principles and Objectives
1. Understanding the Translator's Role and Intent:
    ◦ Translating is a demanding job that requires unusual training in both languages and in solving common problems of transferring ideas, knowledge, and wordplay from the original to the target language.
    ◦ The primary goal of translation is the transfer of meaning.
    ◦ The translator must decide their purpose: whether to imitate (panggagaya) the original by striving for faithfulness in language, form, and tone, or to reproduce (muling-pagbuo) it by adapting the meaning to the presumed interests and needs of the target society and time, offering more freedom and flexibility.
    ◦ A translation should ultimately enrich the language and knowledge of the target language, or serve as a bridge to provide an important experience of another land and time.
2. Degree of Fidelity vs. Freedom:
    ◦ While often preached as needing to be "faithful" (matapat), it is impossible to be "one hundred percent faithful" because no two languages are identical.
    ◦ John Dryden's "lunggating Dryden" (Dryden's aspiration) aimed for the translated language to be as powerful and beautiful as the original, suggesting the translated language should speak as if the original author were born into that language and time.
    ◦ Cicero's "imperyalistang pribilehiyo" (imperialist privilege) allowed translators from a "superior" culture to freely choose translation methods without considering what might be lost from the original.
    ◦ Translators always balance linguistic limitations with the complexities of the original and their self-imposed duties.
    ◦ Paciano Mercado Rizal's advice (1886): Translation should align with the words when understandable, and be free when obscure, but never stray from the meaning.
3. Accuracy (Eksaktitud) and Appropriateness (Angkop):
    ◦ Accuracy is paramount, meaning the translation is "correct":
        ▪ Correct reading of the text.
        ▪ Clear interpretation.
        ▪ Effective revitalisation of the original.
    ◦ Appropriateness means the translation is suitable for the context, language of the time, place, community, and target sector. For instance, "Magyosi Kadiri!" was deemed inappropriate in Visayas as "ka dirí" means "here" in Cebuano, resulting in a reversed meaning.
    ◦ Honorifics such as "po", and "opo" are used to show respect to the elderly.
II. Criteria for Literary Translation
Literary translation involves playing with language and requires the translator to capture the "illocutionary power" of the original.
1. Capturing Literary Devices and Wordplay:
    ◦ Recognise that creative writing is a "violence on language" (Roman Jakobson), meaning authors creatively alter common language use.
    ◦ Identify and find equivalents for figures of speech (tayutay) and rhetorical devices (kasangkapang panretorika).
    ◦ Rhythm and Meter: Assess if the translation captures the musicality and beat of the original. For poetry, this includes:
        ▪ Tugma (rhyme): Repetition of sounds at the end of lines.
        ▪ Súkat (meter): Repetition of the number of syllables per line.
        ▪ Aliterasyon (alliteration): Repetition of consonants.
        ▪ Asonansiya (assonance): Repetition of vowels.
        ▪ Dramatic repetition: Repeating words or phrases to connect emotions or ideas, as "adiós" in Rizal's poem.
    ◦ Tone (Himig): Accurately convey the author's intended tone (e.g., joyous, sarcastic, contemplative).
        ▪ For example, Rizal's sarcastic tone in the 13th stanza of "Último adiós" regarding faith and God was effectively conveyed by Bonifacio and Tolentino.
    ◦ Word Choice and Nuance: Select words that convey the precise emotional and literary quality of the original.
2. Researching Cultural and Historical Context:
    ◦ Allusions (Alusyon): Identify literary, historical, or cultural allusions embedded in the text.
        ▪ Translators must research the "sources" (pinagkunan) of the original to ensure accurate translation.
        ▪ Example: Rizal's "nuestro perdido Edén" (our lost Eden) alludes to Espronceda and the Biblical paradise, requiring the translator to understand these layers of meaning.
    ◦ Author's Background: Understand the author's personal and public background, as it shapes the text.
        ▪ Example: Rizal's "tersa frente" (smooth forehead) evolved in meaning from "A la Juventud Filipina" to "Último adiós," reflecting his evolving patriotic sentiment.
    ◦ Cultural Content: Be aware that each language is a product of its geography, history, ideology, and experience, making 100% literal translation impossible.
        ▪ Translators may need to introduce foreign concepts (e.g., "winter," "snow," "ice") if appropriate, thus enriching the TL.
        ▪ Translators may choose to borrow foreign terms (e.g., "sipres, lawrel, liryo") or find conceptual equivalents based on the cultural context.
        ▪ Be mindful of substitutions that alter ideological meaning: e.g., replacing "Dios" with "Bathala" by Bonifacio and Tolentino to align with Katipunero ideals.
3. Handling "Halaw" (Abbreviation/Adaptation) vs. Full Translation:
    ◦ "Halaw" and "pinagaang edisyon" (lightened editions) are problematic when presented as full translations. They often sacrifice literary quality and critical details for brevity or commercial gain.
    ◦ True "halaw" (adaptation) can be educationally valuable if its purpose is to simplify for quick learning and to introduce students to literature, potentially leading them to the original.
    ◦ A good "halaw" should still convey the main literary qualities of the original, such as plot and character development in a novel.
    ◦ "Hango" (adaptation) involves reshaping the original into a modern or more appropriate form for the target audience (e.g., comic book, film). This is distinct from "halaw" as it is not simply an abridgement but a creative re-creation.
4. Continuous Improvement:
    ◦ No translation is permanent ("walang panghabàng-panahong salin").
    ◦ Translators should continually review and revise their work, even after publication, to incorporate new insights, better word choices, or corrected interpretations.
III. Criteria for Technical Translation
Technical translation is primarily utilitarian and aims to effectively convey specialised information for practical use.
1. Clarity and Readability:
    ◦ The primary challenge is to ensure all relevant information is conveyed easily, properly, and effectively for the target readers.
    ◦ Write for the target reader and write clearly.
    ◦ Avoid unnecessary repetition.
    ◦ Avoid unnecessary adjectives and modifiers.
    ◦ Use simple words and simple expressions.
    ◦ Use an active voice and affirmative tone.
    ◦ Cite sources, expert opinions, and factual reports/test results.
    ◦ Ensure clean spelling and punctuation.
2. Subject Matter Expertise:
    ◦ The translator must not be ignorant of the subject.
    ◦ They need sufficient knowledge of the topic to translate accurately, and be adept at research to gain additional information if needed.
    ◦ They should be a good researcher, having read related works and studies, and possess a good understanding of general scientific and technological principles.
3. Handling Terminology (Pagtutumbas, Panghihiram, Paglikha):
    ◦ Prioritise meaning over literal word-for-word translation. All words can have multiple meanings depending on context (e.g., "saves" can mean "nagliligtas" or "nagtitipid").
    ◦ Systematic Approach to Vocabulary: Follow KWF's recommended steps for finding equivalents:
        1. Pagtutumbas (Equivalence):
            • First, search for equivalents within the current corpus of the Filipino language. This deepens the translator's knowledge of their own language and avoids excessive unnecessary borrowing.
            • Second, look for equivalents from other indigenous languages of the Philippines. Examples include "katarúngan" (justice) from Cebuano "taróng" and "lungsód" (city) from Boholano.
            • Be aware that true, complete equivalents are rare. Explanations, phrases, or new creations might be necessary.
        2. Panghihiram (Borrowing):
            • Spanish is the first language for borrowing due to historical influence. Be cautious of "siyokoy" words (incorrect forms of borrowed words).
            • English is the second language for borrowing.
            • Borrowing without change: For proper nouns (people, places, titles), scientific and technical terms (e.g., carbon dioxide, jus sanguinis, zeitgeist), and words difficult to immediately respell without causing confusion (e.g., cauliflower, pizza).
            • Respell if appropriate: For words that integrate easily into Filipino orthography (e.g., "istambay," "iskedyul," "pulis"). However, avoid respelling if it makes the word awkward, harder to read, destroys cultural/religious/political meaning, or creates confusion with existing Filipino words.
            • KWF now advises retaining the original scientific and technical terms (English, Spanish, German, Latin) in writing to ease teaching and learning in science and technology.
        3. Paglikha (Creation/Neologism): A valuable method for enriching the TL's vocabulary.
            • Bágong-pagbuô (new construction/neologism): Creating new words from existing Filipino morphemes or concepts (e.g., "banyuhay" for metamorphosis, "takdang-aralin" for assignment).
            • Hirám-sálin (calquing or loan translation): Literal translation of foreign idioms or compounds (e.g., "daambakal" for railway).
            • Bágong-húlog (new meaning/revitalisation): Giving a new, often technical, meaning to an old native word (e.g., "agham" for science, "kawani" for employee, "rabáw" for surface).
    ◦ Consistency (Konsistensi): Maintain consistency in terminology and spelling within the translation. This is crucial for accuracy and clarity in technical texts.
4. Objectivity vs. Subjectivity:
    ◦ Technical texts should generally be objective and factual.
    ◦ However, if the purpose is to popularise or persuade, the translation may adopt a subjective tone or point of view (e.g., news articles, columns). In such cases, the translator's motive becomes important.
    ◦ Even when subjective, the translation should appear free from distortion (bending, exaggeration, or alteration) to maintain credibility, especially if used as evidence.
"""
        return evaluation
    
    except Exception as e:
        return {"error": str(e)}