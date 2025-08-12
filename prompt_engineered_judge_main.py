import streamlit as st
from openai import OpenAI

translation_manual = translation_manual = """

# Manual/Criteria for Judging English to Filipino Translations
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

judge_prompt = f"""
You are a translation quality judge for ENGLISH → FILIPINO translations.

TASK:
Evaluate one translation pair using the six criteria below:
1. Accuracy – Does the translation preserve the original meaning?
2. Fluency – Is it grammatically correct and natural in Filipino?
3. Coherence – Is the flow and structure logical in Filipino?
4. Cultural Appropriateness – Does it fit the cultural and social context?
5. Guideline Adherence – Does it follow any provided domain-specific rules?
6. Completeness – Does it retain all important details from the source?

EXAMPLES:
      And below are some examples of good and bad translations:
      Example 1: Overly literal translation (3)
      Original: You broke my heart.
      Good: Dinurog mo ang puso ko.
      Flawed: Sinira mo ang aking puso.
      Reason: broke is literally translated to sinira. not idiomatic Filipino


      Example 2: Unnatural but correct grammar (4)
      Original: The pictures of Jessica Soho and Korina Sanchez were made fun of
      Good: Pinagtawanan ang mga larawan nina Jessica Soho at Korina Sanchez.
      Flawed: Ang mga larawan nina Jessica Soho at Korina Sanchez ay pinagtatawanan.
      Reason: Ay-inversions are generally used to emphasize the topic—typically when introducing a concept or when the sentence has no real action, such as with linking verbs (e.g., “Ang mitochondria ay powerhouse ng cell”).

      Example 3: wrong verb tense (3)
      Original: Arthel tore his ACL while playing basketball
      Good: Napunit ni Arthel ang kanyang ACL habang naglalaro ng basketbol.
      Flawed: Pinunit ni Arthel ang ACL niya habang naglalaro ng basketball.
      Reason: tore is translated as Pinunit, which implies that the ACL tear was intentional, this really shouldn't be a case.

      Example 4: mistranslation (1)
      Original: You can't improve until you make mistakes
      Good: Hindi ka gagaling kung hindi ka magkakamali.
      Flawed: Hindi ka mapaayos hangga't hindi ka nagkakamali.
      Reason: Improve is mistakenly translated as mapaayos, which is wrong for this context.

      Example 5: Forced Filipinization (3)
      Original: A digital signature verifies the authenticity and integrity of digital messages.
      Good: Tinitiyak ng digital signature ang pagiging totoo at integridad ng digital na mensahe.
      Flawed: Tinitiyak ng dijital na pirma ang pagiging tunay at kabuuan ng digital na mensahe.
      Reason: Digital Signature is an established terminology in cryptography, not to be confused with E-signature. Technical jargon shouldn't be translated forcefully to Filipino if it doesn't have an established equivalent

      Example 6: Conversational/quiz style questions
      Original: Which of the following is not a flavor of Ben & Jerry's Ice Cream?
      Good: Alin sa mga sumusunod ay hindi flavor ng Ben & Jerry's Ice Cream?
      Flawed: Alin sa mga sumusunod ang hindi lasa ng Ben & Jerry's Ice Cream?
      Reason: unnecessary translation of jargon 'flavor'

      Example 7: Cultural insensitivity/bias (2)
      Original: All men are equal.
      Good: Lahat ng tao ay pantay-pantay.
      Flawed: Lahat ng lalaki ay pantay-pantay.
      Reason: The word men is translated to lalaki, showing gender bias as the original statement refers to men in the sense of humankind.

      Example 8: missed idiom leading to unnatural sentence (2)
      Original: : You’ve got some nerve. Just because I’m rich doesn’t mean I don’t have problems.
      Good:Ang kapal ng mukha mo. Dahil lang mayaman ako hindi ibig sabihin na wala akong problema.
      Flawed: Meron kang nerbiyo. Dahil lang mayaman ako hindi ibig sabihin na wala akong problema.

GUIDELINE_START:
{translation_manual}

GUIDELINE_END

SCORING RULE:
- Each criterion: 0 points (fails) or 1 point (meets standard)
- Add up the points (0–6 total)
- Map the sum to a final score:
    - 5–6 → Score = 5 (Excellent)
    - 3–4 → Score = 3 (Good)
    - 0–2 → Score = 1 (Poor)

OUTPUT:
- Present your evaluation in a clear, well-structured way
- Format the result as a table
- Don't use big headers.
- Include:
    • Final score (1–5) and label ("excellent", "good", or "poor")
    • The score and explanation for each criterion
    • Any notable highlights (problematic phrases or strong points)
    • A suggested fix if there are serious errors
    • Your confidence level (optional, 0–100)

Be thorough but concise.


"""

def clear_chat_history():
    st.session_state["messages"] = [{"role": "system", "content": "You are a translation judge."}]

# Setup
client = OpenAI(api_key=st.secrets["GEMINI_API_KEY"], base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
model_types = ["gemini-2.5-flash-lite"]

# Streamlit App
st.set_page_config(page_title="Chatbot", page_icon="🤖")

with st.sidebar:
    st.title('Translation Judge')
    st.write('This chatbot was created by Joel Ethan Batac and Boris Victoria')
    st.button('Clear Chat History', on_click=clear_chat_history)
    
    streaming_enabled = st.checkbox("Enable Streaming", value=True)
    append_judge_prompt = st.checkbox("Append Judge Prompt", value=False)

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "system", "content": "You are a translation judge."}]

for message in st.session_state["messages"]:
    print(message)
    if message["role"] == "system":
        with st.chat_message(message["role"], avatar="🦖"):
            st.markdown(message["content"])
            continue
    
    with st.chat_message(message["role"]):
        if message.get("content"):
            st.markdown(message["content"])

# Chat input
user_input = st.chat_input("Type your message here...")

if user_input:
    # Add user message to session state and display
    if append_judge_prompt:
        st.session_state["messages"].append({"role": "user", "content": judge_prompt + user_input})
        with st.chat_message("user"):
            st.markdown(judge_prompt + user_input)
    else:
        st.session_state["messages"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

    
    # Assistant response container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # Process the conversation
        full_response = ""
        
        if streaming_enabled:
            # Streaming completion
            stream = client.chat.completions.create(
                model=model_types[0],
                messages=st.session_state["messages"],
                temperature=0.6,
                stream=True,
            )
            
            # Collect the streaming response
            full_response = ""
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    # Regular content streaming
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            if full_response:
                message_placeholder.markdown(full_response)
                st.session_state["messages"].append({"role": "assistant", "content": full_response})

        else:
            # Non-streaming completion
            completion = client.chat.completions.create(
                model=model_types[0],
                messages=st.session_state["messages"],
                temperature=0.6,
                stream=False,
            )
            
            choice = completion.choices[0]
            full_response = choice.message.content or ""
            
            if full_response:
                message_placeholder.markdown(full_response)
                st.session_state["messages"].append({"role": "assistant", "content": full_response})
            