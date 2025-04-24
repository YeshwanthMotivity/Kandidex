import re
import ollama

# Extract names
def extract_names_from_transcript(transcript):
    candidate_name = "Unknown"
    interviewer_name = "Unknown"
    confidence = 0
    lines = transcript.splitlines()

    for line in lines:
        if "Interviewer" in line or line.strip().startswith("I:"):
            match = re.search(r"(?:Interviewer|I)[:\-]?\s*(?:Hi|Hello)?[, ]*(?:I am|I'm|This is)?\s*([A-Z][a-z]+)", line)
            if match:
                interviewer_name = match.group(1)
                confidence += 2
        elif "Candidate" in line or line.strip().startswith("C:"):
            match = re.search(r"(?:Candidate|C)[:\-]?\s*(?:Hi|Hello)?[, ]*(?:I am|I'm|This is)?\s*([A-Z][a-z]+)", line)
            if match:
                candidate_name = match.group(1)
                confidence += 2

    greetings = re.findall(r"\bhi[, ]+([A-Z][a-z]+)", transcript, re.IGNORECASE)
    greetings = [g.capitalize() for g in greetings]
    if len(greetings) >= 2:
        interviewer_name = greetings[0]
        candidate_name = greetings[1]
        confidence += 1
    elif len(greetings) == 1:
        if interviewer_name == "Unknown":
            interviewer_name = greetings[0]
            confidence += 0.5

    iam_matches = re.findall(r"\b(?:I am|I'm|This is)\s+([A-Z][a-z]+)", transcript)
    for name in iam_matches:
        if interviewer_name == "Unknown":
            interviewer_name = name
            confidence += 0.5
        elif candidate_name == "Unknown" and name != interviewer_name:
            candidate_name = name
            confidence += 0.5

    return candidate_name, interviewer_name, confidence

# Extract role
def extract_job_role(prompt_text):
    match = re.search(r"\b(?:for a|for an|as a)\s+([A-Z][\w\s/&-]+?)\s+(?:position|role)?[.,\n]", prompt_text, re.IGNORECASE)
    return match.group(1).strip() if match else "Software Engineer"

# Determine experience level from job role
def extract_experience_level_from_role(role_name):
    role_name = role_name.lower()
    if "senior" in role_name:
        return "senior"
    elif "junior" in role_name:
        return "junior"
    else:
        return "unknown"

# Auto-detect skills used
def detect_skills(text):
    common_skills = [
        "Python", "Java", "C++", "C#", "JavaScript", "TypeScript",
        "HTML", "CSS", "SQL", "NoSQL", "MongoDB", "PostgreSQL",
        "React", "Node.js", "Express.js", "Django", "Flask",
        "Spring Boot", "Git", "REST API", "JSON", "AJAX"
    ]
    detected = set()
    for skill in common_skills:
        if re.search(rf"\b{re.escape(skill)}\b", text, re.IGNORECASE):
            detected.add(skill)
    return sorted(detected)

# Final evaluation generation
def generate_evaluation(transcript, test, prompt_text):
    candidate_name, interviewer_name, _ = extract_names_from_transcript(transcript)
    job_role = extract_job_role(prompt_text)
    experience_level = extract_experience_level_from_role(job_role)

    all_text = transcript + "\n" + test
    skills_to_rate = detect_skills(all_text)

    skills_prompt = "\n".join([f" - {skill} (Rate 1–5 + comment)" for skill in skills_to_rate]) if skills_to_rate else \
        " - Python\n - SQL\n - Problem Solving\n - Technical Communication"

    experience_instruction = {
        "senior": "The candidate is a senior. Be stricter in your evaluation. Senior candidates are expected to demonstrate deep technical knowledge, clarity, and confidence. Lack of depth should reduce scores.",
        "junior": "The candidate is a junior. Moderate expectations accordingly. Basic understanding is acceptable, but the potential to learn should be noted.",
        "unknown": "No clear experience level was detected. Use standard evaluation."
    }.get(experience_level, "")

    prompt = f"""
You are a strict technical evaluator assessing a candidate for a {job_role} position.

🔍 Evaluation Criteria:
- **Strictly** rate skills based **only on the coding test performance**. Do not consider soft skills or irrelevant topics.
- Base **70%** of your judgment on the coding test.
- Base **30%** on the transcript, but only for technical depth and clarity.
- Ignore any irrelevant information. Focus solely on **code knowledge** and **technical clarity**.

🎯 Experience Level:
{experience_instruction}

📝 Instructions:
- Review the following:
- Interview Transcript: {transcript}
- Problem Solving Test: {test}

📌 Your evaluation email to HR must include:
1. **Candidate Name**: {candidate_name}
2. A **brief summary** (max 100 words) highlighting strengths and weaknesses.
3. A **Skill Ratings Table**:
{skills_prompt}
   - Rate each skill on a **1–5 scale** and give a **short justification**.
   - Emphasize **coding test performance only**.
4. **Final Evaluation Metric** (based on average skill score):
   - **Above 3** → Hire
   - **Exactly 3** → Hold
   - **Below 3** → Not Hire / Reject
5. A final **recommendation**: Strong Hire / Hire / Hold / Reject
6. A **justification** for your recommendation (max 100 words).

Tone: Technical, strict, unbiased. Be honest — do not give the benefit of doubt unless the **code** proves strong capability.
    """

    response = ollama.chat(
        model='openchat',
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.3, "top_p": 0.9, "num_predict": 512}
    )

    return response['message']['content']




# import re
# import ollama

# # Extract names
# def extract_names_from_transcript(transcript):
#     candidate_name = "Unknown"
#     interviewer_name = "Unknown"
#     confidence = 0
#     lines = transcript.splitlines()

#     for line in lines:
#         if "Interviewer" in line or line.strip().startswith("I:"):
#             match = re.search(r"(?:Interviewer|I)[:\-]?\s*(?:Hi|Hello)?[, ]*(?:I am|I'm|This is)?\s*([A-Z][a-z]+)", line)
#             if match:
#                 interviewer_name = match.group(1)
#                 confidence += 2
#         elif "Candidate" in line or line.strip().startswith("C:"):
#             match = re.search(r"(?:Candidate|C)[:\-]?\s*(?:Hi|Hello)?[, ]*(?:I am|I'm|This is)?\s*([A-Z][a-z]+)", line)
#             if match:
#                 candidate_name = match.group(1)
#                 confidence += 2

#     greetings = re.findall(r"\bhi[, ]+([A-Z][a-z]+)", transcript, re.IGNORECASE)
#     greetings = [g.capitalize() for g in greetings]
#     if len(greetings) >= 2:
#         interviewer_name = greetings[0]
#         candidate_name = greetings[1]
#         confidence += 1
#     elif len(greetings) == 1:
#         if interviewer_name == "Unknown":
#             interviewer_name = greetings[0]
#             confidence += 0.5

#     iam_matches = re.findall(r"\b(?:I am|I'm|This is)\s+([A-Z][a-z]+)", transcript)
#     for name in iam_matches:
#         if interviewer_name == "Unknown":
#             interviewer_name = name
#             confidence += 0.5
#         elif candidate_name == "Unknown" and name != interviewer_name:
#             candidate_name = name
#             confidence += 0.5

#     return candidate_name, interviewer_name, confidence

# # Extract role
# def extract_job_role(prompt_text):
#     match = re.search(r"\b(?:for a|for an|as a)\s+([A-Z][\w\s/&-]+?)\s+(?:position|role)?[.,\n]", prompt_text, re.IGNORECASE)
#     return match.group(1).strip() if match else "Software Engineer"

# # Extract exp level
# def extract_experience_level(transcript):
#     match = re.search(r"(\d+)\+?\s+years? of experience", transcript, re.IGNORECASE)
#     if match:
#         years = int(match.group(1))
#         return "senior" if years >= 5 else "junior"
#     return "unknown"

# # Auto-detect skills used
# def detect_skills(text):
#     common_skills = [
#         "Python", "Java", "C++", "C#", "JavaScript", "TypeScript",
#         "HTML", "CSS", "SQL", "NoSQL", "MongoDB", "PostgreSQL",
#         "React", "Node.js", "Express.js", "Django", "Flask",
#         "Spring Boot", "Git", "REST API", "JSON", "AJAX"
#     ]
#     detected = set()
#     for skill in common_skills:
#         if re.search(rf"\b{re.escape(skill)}\b", text, re.IGNORECASE):
#             detected.add(skill)
#     return sorted(detected)

# # Final evaluation generation
# def generate_evaluation(transcript, test, prompt_text):
#     candidate_name, interviewer_name, _ = extract_names_from_transcript(transcript)
#     job_role = extract_job_role(prompt_text)
#     experience_level = extract_experience_level(transcript)

#     all_text = transcript + "\n" + test
#     skills_to_rate = detect_skills(all_text)

#     skills_prompt = "\n".join([f" - {skill} (Rate 1–5 + comment)" for skill in skills_to_rate]) if skills_to_rate else \
#         " - Python\n - SQL\n - Problem Solving\n - Technical Communication"

#     experience_instruction = {
#         "senior": "The candidate is a senior. Be stricter in your evaluation. Senior candidates are expected to demonstrate deep technical knowledge, clarity, and confidence. Lack of depth should reduce scores.",
#         "junior": "The candidate is a junior. Moderate expectations accordingly. Basic understanding is acceptable, but the potential to learn should be noted.",
#         "unknown": "No clear experience level was detected. Use standard evaluation."
#     }.get(experience_level, "")

#     prompt = f"""
# You are a strict technical evaluator assessing a candidate for a {job_role} position.

# 🔍 Evaluation Criteria:
# - Base **70%** of your judgment on the candidate’s coding test performance.
# - Base **30%** on the interview transcript.
# - Do **not** over-focus on soft skills or irrelevant details.
# - Only focus on **coding-related skills**.

# 🎯 Experience Level:
# {experience_instruction}

# 📝 Instructions:
# - Review the following:
# - Interview Transcript: {transcript}
# - Problem Solving Test: {test}

# 📌 Your evaluation email to HR must include:
# 1. **Candidate Name**: {candidate_name}
# 2. A **brief summary** (max 100 words) highlighting strengths and weaknesses.
# 3. A **Skill Ratings Table**:
# {skills_prompt}
#    - Rate each skill on a **1–5 scale** and give a **short justification**.
#    - Emphasize test-based evaluation.
# 4. **Final Evaluation Metric**:
#    - 0–3 → Reject
#    - Exactly 3 → Hold
#    - Above 3 → Hire / Strong Hire (only if well deserved)
# 5. A final **recommendation**: Strong Hire / Hire / Hold / Reject
# 6. A **justification** for your recommendation (max 100 words).

# Tone: Technical, strict, unbiased. Be honest — avoid giving benefit of doubt unless the coding skills clearly justify it.
#     """

#     response = ollama.chat(
#         model='openchat',
#         messages=[{"role": "user", "content": prompt}],
#         options={"temperature": 0.3, "top_p": 0.9, "num_predict": 512}
#     )

#     return response['message']['content']

# import re
# import ollama

# # Extract names
# def extract_names_from_transcript(transcript):
#     candidate_name = "Unknown"
#     interviewer_name = "Unknown"
#     confidence = 0
#     lines = transcript.splitlines()

#     for line in lines:
#         if "Interviewer" in line or line.strip().startswith("I:"):
#             match = re.search(r"(?:Interviewer|I)[:\-]?\s*(?:Hi|Hello)?[, ]*(?:I am|I'm|This is)?\s*([A-Z][a-z]+)", line)
#             if match:
#                 interviewer_name = match.group(1)
#                 confidence += 2
#         elif "Candidate" in line or line.strip().startswith("C:"):
#             match = re.search(r"(?:Candidate|C)[:\-]?\s*(?:Hi|Hello)?[, ]*(?:I am|I'm|This is)?\s*([A-Z][a-z]+)", line)
#             if match:
#                 candidate_name = match.group(1)
#                 confidence += 2

#     greetings = re.findall(r"\bhi[, ]+([A-Z][a-z]+)", transcript, re.IGNORECASE)
#     greetings = [g.capitalize() for g in greetings]
#     if len(greetings) >= 2:
#         interviewer_name = greetings[0]
#         candidate_name = greetings[1]
#         confidence += 1
#     elif len(greetings) == 1:
#         if interviewer_name == "Unknown":
#             interviewer_name = greetings[0]
#             confidence += 0.5

#     iam_matches = re.findall(r"\b(?:I am|I'm|This is)\s+([A-Z][a-z]+)", transcript)
#     for name in iam_matches:
#         if interviewer_name == "Unknown":
#             interviewer_name = name
#             confidence += 0.5
#         elif candidate_name == "Unknown" and name != interviewer_name:
#             candidate_name = name
#             confidence += 0.5

#     return candidate_name, interviewer_name, confidence

# # Extract role
# def extract_job_role(prompt_text):
#     match = re.search(r"\b(?:for a|for an|as a)\s+([A-Z][\w\s/&-]+?)\s+(?:position|role)?[.,\n]", prompt_text, re.IGNORECASE)
#     return match.group(1).strip() if match else "Software Engineer"

# # Extract exp level
# def extract_experience_level(transcript):
#     match = re.search(r"(\d+)\+?\s+years? of experience", transcript, re.IGNORECASE)
#     if match:
#         years = int(match.group(1))
#         return "senior" if years >= 5 else "junior"
#     return "unknown"

# # Auto-detect skills used
# def detect_skills(text):
#     common_skills = [
#         "Python", "Java", "C++", "C#", "JavaScript", "TypeScript",
#         "HTML", "CSS", "SQL", "NoSQL", "MongoDB", "PostgreSQL",
#         "React", "Node.js", "Express.js", "Django", "Flask",
#         "Spring Boot", "Git", "REST API", "JSON", "AJAX"
#     ]
#     detected = set()
#     for skill in common_skills:
#         if re.search(rf"\b{re.escape(skill)}\b", text, re.IGNORECASE):
#             detected.add(skill)
#     return sorted(detected)

# # Final evaluation generation
# # Final evaluation generation
# def generate_evaluation(transcript, test, prompt_text):
#     candidate_name, interviewer_name, _ = extract_names_from_transcript(transcript)
#     job_role = extract_job_role(prompt_text)
#     experience_level = extract_experience_level(transcript)

#     all_text = transcript + "\n" + test
#     skills_to_rate = detect_skills(all_text)

#     skills_prompt = "\n".join([f" - {skill} (Rate 1–5 + comment)" for skill in skills_to_rate]) if skills_to_rate else \
#         " - Python\n - SQL\n - Problem Solving\n - Technical Communication"

#     experience_instruction = {
#         "senior": "The candidate is a senior. Be stricter in your evaluation. Senior candidates are expected to demonstrate deep technical knowledge, clarity, and confidence. Lack of depth should reduce scores.",
#         "junior": "The candidate is a junior. Moderate expectations accordingly. Basic understanding is acceptable, but the potential to learn should be noted.",
#         "unknown": "No clear experience level was detected. Use standard evaluation."
#     }.get(experience_level, "")

#     prompt = f"""
# You are a strict technical evaluator assessing a candidate for a {job_role} position.

# 🔍 Evaluation Criteria:
# - **Strictly** rate skills based **only on the coding test performance**. Do not consider soft skills or irrelevant topics.
# - Base **70%** of your judgment on the coding test.
# - Base **30%** on the transcript, but only for technical depth and clarity.
# - Ignore any irrelevant information. Focus solely on **code knowledge** and **technical clarity**.

# 🎯 Experience Level:
# {experience_instruction}

# 📝 Instructions:
# - Review the following:
# - Interview Transcript: {transcript}
# - Problem Solving Test: {test}

# 📌 Your evaluation email to HR must include:
# 1. **Candidate Name**: {candidate_name}
# 2. A **brief summary** (max 100 words) highlighting strengths and weaknesses.
# 3. A **Skill Ratings Table**:
# {skills_prompt}
#    - Rate each skill on a **1–5 scale** and give a **short justification**.
#    - Emphasize **coding test performance only**.
# 4. **Final Evaluation Metric** (based on average skill score):
#    - **Above 3** → Hire
#    - **Exactly 3** → Hold
#    - **Below 3** → Not Hire / Reject
# 5. A final **recommendation**: Strong Hire / Hire / Hold / Reject
# 6. A **justification** for your recommendation (max 100 words).

# Tone: Technical, strict, unbiased. Be honest — do not give the benefit of doubt unless the **code** proves strong capability.
#     """

#     response = ollama.chat(
#         model='openchat',
#         messages=[{"role": "user", "content": prompt}],
#         options={"temperature": 0.3, "top_p": 0.9, "num_predict": 512}
#     )

#     return response['message']['content']









# import re
# import ollama
# import requests
# import json

# def extract_names_from_transcript(transcript):
#     candidate_name = "Unknown"
#     interviewer_name = "Unknown"
#     confidence = 0
#     lines = transcript.splitlines()

#     for line in lines:
#         if "Interviewer" in line or line.strip().startswith("I:"):
#             match = re.search(r"(?:Interviewer|I)[:\-]?\s*(?:Hi|Hello)?[, ]*(?:I am|I'm|This is)?\s*([A-Z][a-z]+)", line)
#             if match:
#                 interviewer_name = match.group(1)
#                 confidence += 2
#         elif "Candidate" in line or line.strip().startswith("C:"):
#             match = re.search(r"(?:Candidate|C)[:\-]?\s*(?:Hi|Hello)?[, ]*(?:I am|I'm|This is)?\s*([A-Z][a-z]+)", line)
#             if match:
#                 candidate_name = match.group(1)
#                 confidence += 2

#     # Greeting fallback
#     greetings = re.findall(r"\bhi[, ]+([A-Z][a-z]+)", transcript, re.IGNORECASE)
#     greetings = [g.capitalize() for g in greetings]
#     if len(greetings) >= 2:
#         interviewer_name = greetings[0]
#         candidate_name = greetings[1]
#         confidence += 1
#     elif len(greetings) == 1:
#         if interviewer_name == "Unknown":
#             interviewer_name = greetings[0]
#             confidence += 0.5

#     # "I am" fallback
#     iam_matches = re.findall(r"\b(?:I am|I'm|This is)\s+([A-Z][a-z]+)", transcript)
#     for name in iam_matches:
#         if interviewer_name == "Unknown":
#             interviewer_name = name
#             confidence += 0.5
#         elif candidate_name == "Unknown" and name != interviewer_name:
#             candidate_name = name
#             confidence += 0.5

#     return candidate_name, interviewer_name, confidence


# def extract_job_role(prompt_text):
#     match = re.search(r"\b(?:for a|for an|as a)\s+([A-Z][\w\s/&-]+?)\s+(?:position|role)?[.,\n]", prompt_text, re.IGNORECASE)
#     return match.group(1).strip() if match else "Software Engineer"


# def extract_experience_level(transcript):
#     """Try to extract years of experience from transcript"""
#     match = re.search(r"(\d+)\+?\s+years? of experience", transcript, re.IGNORECASE)
#     if match:
#         years = int(match.group(1))
#         return "senior" if years >= 5 else "junior"
#     return "unknown"  # fallback


# def generate_evaluation(transcript, test, prompt_text, skills_to_rate):
#     candidate_name, interviewer_name, _ = extract_names_from_transcript(transcript)
#     job_role = extract_job_role(prompt_text)
#     experience_level = extract_experience_level(transcript)

#     # Skill prompt
#     skills_prompt = "\n".join([f" - {skill} (Rate 1–5 + comment)" for skill in skills_to_rate]) if skills_to_rate else \
#         " - Python\n - SQL\n - Problem Solving\n - Technical Communication"

#     experience_instruction = ""
#     if experience_level == "senior":
#         experience_instruction = "The candidate is a senior. Be stricter in your evaluation. Senior candidates are expected to demonstrate deep technical knowledge, clarity, and confidence. Lack of depth should reduce scores."
#     elif experience_level == "junior":
#         experience_instruction = "The candidate is a junior. Moderate expectations accordingly. Basic understanding is acceptable, but the potential to learn should be noted."
#     else:
#         experience_instruction = "No clear experience level was detected. Use standard evaluation."

#     prompt = f"""
# You are a strict technical evaluator assessing a candidate for a {job_role} position.

# 🔍 Evaluation Criteria:
# - Base **70%** of your judgment on the candidate’s coding test performance.
# - Base **30%** on the interview transcript.
# - Do **not** over-focus on soft skills or irrelevant details.
# - Use **relevant technical skills** if the skills list is empty, focusing on core coding languages like **Python, SQL**.

# 🎯 Experience Level:
# {experience_instruction}

# 📝 Instructions:
# - Review the following:
# - Interview Transcript: {transcript}
# - Problem Solving Test: {test}

# 📌 Your evaluation email to HR must include:
# 1. **Candidate Name**: {candidate_name}
# 2. A **brief summary** (max 100 words) highlighting strengths and weaknesses.
# 3. A **Skill Ratings Table**: 
# {skills_prompt}
#    - Rate each skill on a **1–5 scale** and give a **short justification**.
#    - Emphasize test-based evaluation.
# 4. **Final Evaluation Metric**:
#    - 0–3 → Reject
#    - Exactly 3 → Hold
#    - Above 3 → Hire / Strong Hire (only if well deserved)
# 5. A final **recommendation**: Strong Hire / Hire / Hold / Reject
# 6. A **justification** for your recommendation (max 100 words).

# Tone: Technical, strict, unbiased. Be honest — avoid giving benefit of doubt unless the coding skills clearly justify it.
#     """

#     response = ollama.chat(
#         model='openchat',
#         messages=[{"role": "user", "content": prompt}],
#         options={"temperature": 0.3, "top_p": 0.9, "num_predict": 512}
#     )

#     return response['message']['content']




# import re
# import ollama
# import requests
# import json

# def extract_names_from_transcript(transcript):
#     candidate_name = "Unknown"
#     interviewer_name = "Unknown"
#     confidence = 0

#     lines = transcript.splitlines()

#     # 1️⃣ Detect from labeled lines
#     for line in lines:
#         if "Interviewer" in line or line.strip().startswith("I:"):
#             match = re.search(r"(?:Interviewer|I)[:\-]?\s*(?:Hi|Hello)?[, ]*(?:I am|I'm|This is)?\s*([A-Z][a-z]+)", line)
#             if match:
#                 interviewer_name = match.group(1)
#                 confidence += 2
#         elif "Candidate" in line or line.strip().startswith("C:"):
#             match = re.search(r"(?:Candidate|C)[:\-]?\s*(?:Hi|Hello)?[, ]*(?:I am|I'm|This is)?\s*([A-Z][a-z]+)", line)
#             if match:
#                 candidate_name = match.group(1)
#                 confidence += 2

#     # 2️⃣ Fallback: greetings
#     greetings = re.findall(r"\bhi[, ]+([A-Z][a-z]+)", transcript, re.IGNORECASE)
#     greetings = [g.capitalize() for g in greetings]
#     if len(greetings) >= 2:
#         interviewer_name = greetings[0]
#         candidate_name = greetings[1]
#         confidence += 1
#     elif len(greetings) == 1:
#         if interviewer_name == "Unknown":
#             interviewer_name = greetings[0]
#             confidence += 0.5

#     # 3️⃣ Fallback: "I am", "This is"
#     iam_matches = re.findall(r"\b(?:I am|I'm|This is)\s+([A-Z][a-z]+)", transcript)
#     for name in iam_matches:
#         if interviewer_name == "Unknown":
#             interviewer_name = name
#             confidence += 0.5
#         elif candidate_name == "Unknown" and name != interviewer_name:
#             candidate_name = name
#             confidence += 0.5

#     return candidate_name, interviewer_name, confidence


# def extract_job_role(prompt_text):
#     match = re.search(r"\b(?:for a|for an|as a)\s+([A-Z][\w\s/&-]+?)\s+(?:position|role)?[.,\n]", prompt_text, re.IGNORECASE)
#     if match:
#         return match.group(1).strip()
#     return "Software Engineer"  # default fallback


# def generate_evaluation(transcript, test, prompt_text, skills_to_rate):
#     candidate_name, interviewer_name, _ = extract_names_from_transcript(transcript)
#     job_role = extract_job_role(prompt_text)

#     # Build skill section dynamically
#     if skills_to_rate:
#         skills_prompt = "\n".join([f"   - {skill} (Rate 1–5 + comment)" for skill in skills_to_rate])
#     else:
#         skills_prompt = "   - Python\n   - SQL\n   - Problem Solving\n   - Technical Communication"

#     prompt = f"""
# You are a strict technical evaluator assessing a candidate for a {job_role} position.

# 🔍 Evaluation Criteria:
# - Base **70%** of your judgment on the candidate’s coding test performance.
# - Base **30%** on the interview transcript.
# - Do **not** over-focus on soft skills or irrelevant details.
# - Use **relevant technical skills** if the skills list is empty, but keep your focus on core coding languages like **Python, SQL**.

# 📝 Instructions:
# - Review the following:
#     - Interview Transcript: 
#       {transcript}
#     - Problem Solving Test:
#       {test}

# 📌 Your evaluation email to HR must include:
# 1. **Candidate Name**: {candidate_name}
# 2. A **brief summary** (max 100 words) highlighting strengths and weaknesses.
# 3. A **Skill Ratings Table**:
# {skills_prompt}
#     - Strictly rate each skill on a **1–5 scale** and give a **short justification**.
#     - Emphasize test-based evaluation.

# 4. **Final Evaluation Metric**:
#     - 0–3 → Reject
#     - Exactly 3 → Hold
#     - Above 3 → Hire / Strong Hire (only if well deserved)

# 5. A final **recommendation**: Strong Hire / Hire / Hold / Reject
# 6. A **justification** for your recommendation (max 100 words).

# Tone: Technical, strict, unbiased. Be honest — avoid giving benefit of doubt unless the coding skills clearly justify it.
# """

#     response = ollama.chat(
#         model='openchat',
#         messages=[{"role": "user", "content": prompt}],
#         options={"temperature": 0.3, "top_p": 0.9, "num_predict": 512}
#     )

#     return response['message']['content']




# # import requests
# # import json
# # import ollama
# # import re

# # import re

# # def extract_names_from_transcript(transcript):
# #     import re

# #     candidate_name = "Unknown"
# #     interviewer_name = "Unknown"
# #     confidence = 0

# #     lines = transcript.splitlines()

# #     # 1️⃣ Try detecting using explicit labels first
# #     for line in lines:
# #         if "Interviewer" in line or line.strip().startswith("I:"):
# #             match = re.search(r"(?:Interviewer|I)[:\-]?\s*(?:Hi|Hello)?[, ]*(?:I am|I'm|This is)?\s*([A-Z][a-z]+)", line)
# #             if match:
# #                 interviewer_name = match.group(1)
# #                 confidence += 2
# #         elif "Candidate" in line or line.strip().startswith("C:"):
# #             match = re.search(r"(?:Candidate|C)[:\-]?\s*(?:Hi|Hello)?[, ]*(?:I am|I'm|This is)?\s*([A-Z][a-z]+)", line)
# #             if match:
# #                 candidate_name = match.group(1)
# #                 confidence += 2

# #     # 2️⃣ Greeting-based fallback: "Hi <Name>" order
# #     if candidate_name == "Unknown" or interviewer_name == "Unknown":
# #         greetings = re.findall(r"\bhi[, ]+([A-Z][a-z]+)", transcript, re.IGNORECASE)
# #         greetings = [g.capitalize() for g in greetings]

# #         if len(greetings) >= 2:
# #             # First speaks = Interviewer, Second = Candidate
# #             interviewer_name = greetings[0]
# #             candidate_name = greetings[1]
# #             confidence += 1
# #         elif len(greetings) == 1:
# #             if interviewer_name == "Unknown":
# #                 interviewer_name = greetings[0]
# #                 confidence += 0.5

# #     # 3️⃣ Fallback to "I am" / "This is"
# #     iam_matches = re.findall(r"\b(?:I am|I'm|This is)\s+([A-Z][a-z]+)", transcript)
# #     if iam_matches:
# #         if interviewer_name == "Unknown":
# #             interviewer_name = iam_matches[0]
# #             confidence += 0.5
# #         elif candidate_name == "Unknown" and iam_matches[0] != interviewer_name:
# #             candidate_name = iam_matches[0]
# #             confidence += 0.5

# #     return candidate_name, interviewer_name, confidence



# # def generate_evaluation(transcript, test, job_role, skills_to_rate):
# #     if skills_to_rate:
# #         skills_prompt = ""
# #         for skill in skills_to_rate:
# #             skills_prompt += f"   - {skill} (Rate 1–5 + comment)\n"
# #     else:
# #         skills_prompt = "   - Python\n   - SQL\n   - Problem Solving\n   - Technical Communication"

# #     prompt = f"""
# # You are a strict technical evaluator assessing a candidate for a {job_role} position.

# # 🔍 Evaluation Criteria:
# # - Base **70%** of your judgment on the candidate’s coding test performance.
# # - Base **30%** on the interview transcript.
# # - Do **not** over-focus on soft skills or irrelevant details.
# # - Use **relevant technical skills** if the skills list is empty, but keep your focus on core coding languages like **Python, SQL**.

# # 📝 Instructions:
# # - Review the following:
# #     - Interview Transcript: 
# #       {transcript}
# #     - Problem Solving Test:
# #       {test}

# # 📌 Your evaluation email to HR must include:
# # 1. **Candidate Name** (if available from transcript).
# # 2. A **brief summary** (max 100 words) highlighting strengths and weaknesses.
# # 3. A **Skill Ratings Table**:
# # {skills_prompt}
# #     - Strictly rate each skill on a **1–5 scale** and give a **short justification**.
# #     - Emphasize test-based evaluation.

# # 4. **Final Evaluation Metric**:
# #     - 0–3 → Reject
# #     - Exactly 3 → Hold
# #     - Above 3 → Hire / Strong Hire (only if well deserved)

# # 5. A final **recommendation**: Strong Hire / Hire / Hold / Reject
# # 6. A **justification** for your recommendation (max 100 words).

# # Tone: Technical, strict, unbiased. Be honest — avoid giving benefit of doubt unless the coding skills clearly justify it.
# # """

# #     response = ollama.chat(
# #         model='openchat',
# #         messages=[{"role": "user", "content": prompt}],
# #         options={
# #             "temperature": 0.3,
# #             "top_p": 0.9,
# #             "num_predict": 512
# #         }
# #     )

# #     result = response['message']['content']
# #     return result


# # def generate_evaluation(transcript, test, job_role, skills_to_rate):
# #     if skills_to_rate:
# #         skills_prompt = ""
# #         for skill in skills_to_rate:
# #             skills_prompt += f"   - {skill} (Rate 1-5 + comment)\n"
# #     else:
# #         # Use default if empty
# #         skills_prompt = "   - Python\n   - SQL\n   - Problem Solving\n   - Technical Communication"

# #     prompt = f"""
# # You are a strict technical evaluator assessing a candidate for a Data Engineer role.

# # Base 70% of your judgment on the candidate’s coding test performance and only 30% on the interview transcript. Be critical and realistic — if the test responses do not meet expectations, do not hesitate to give a "No Hire" recommendation in the email.

# # Strictly evaluate the candidate based on **coding skills** such as Python, SQL. Do not overemphasize soft skills — only mention them if relevant. Use relevant skills if none are provided, but keep the focus on technical depth.

# # Instructions:
# # - Evaluate the candidate for this role: **{job_role}**
# # - Candidate Interview Transcript:
# #     {transcript}
# # - Problem Solving Test Submission:
# #     {test}

# # Please generate a **formal evaluation email for the HR Team** that includes:
# # 1. **Candidate Name** (if extractable from the transcript)
# # 2. **Short Summary** (100 words max): Key strengths and weaknesses
# # 3. **Skill Ratings Table**: Rate strictly each skill from 1 to 5 and provide brief justifications.
# #    - Skills to rate:
# # {skills_prompt}
# # 4. **Overall Recommendation** (Strong Hire / Hire / Hold / Reject)
# # 5. **Justification for Recommendation** (within 100 words)

# # Ensure the tone is objective and technical. Avoid fluff or over-praise. Emphasize evaluation based mostly on test quality.
# # """

# #     response = ollama.chat(
# #         model='llama3:8b',
# #         messages=[{"role": "user", "content": prompt}],
# #         options={
# #             "temperature": 0.3,
# #             "top_p": 0.9,
# #             "num_predict": 512
# #         }
# #     )

# #     result = response['message']['content']
# #     return result



# # def generate_evaluation(transcript, test, job_role, skills_to_rate):
# #     skills_prompt = ""
# #     for skill in skills_to_rate:
# #         skills_prompt += f"   - {skill} (Rate 1-5 + comment)\n"

# #     # Final refined prompt
# #     prompt = f"""
# # You are a strict technical evaluator assessing a candidate for a Data Engineer role.

# # Base 70% of your judgment on the candidate’s coding test performance and only 30% on the interview transcript. Be critical and realistic — if the test responses do not meet expectations, do not hesitate to give a "No Hire" recommendation in the email.

# # Strictly evaluate the candidate based on **coding skills** such as Python, SQL, problem-solving, and technical understanding. Do not overemphasize soft skills — only mention them if relevant. Use relevant skills if none are provided, but keep the focus on technical depth.

# # Instructions:
# # - Evaluate the candidate for this role: **{job_role}**
# # - Candidate Interview Transcript:
# #     {transcript}
# # - Problem Solving Test Submission:
# #     {test}

# # Please generate a **formal evaluation email for the HR Team** that includes:
# # 1. **Candidate Name** (if extractable from the transcript)
# # 2. **Short Summary** (100 words max): Key strengths and weaknesses
# # 3. **Skill Ratings Table**: Rate strictly each skill from 1 to 5 and provide brief justifications.
# #    - Skills to rate:
# # {skills_prompt if skills_prompt else '     - Python\n     - SQL\n     - Problem Solving\n     - Technical Communication'}
# # 4. **Overall Recommendation** (Strong Hire / Hire / Hold / Reject)
# # 5. **Justification for Recommendation** (within 100 words)

# # Ensure the tone is objective and technical. Avoid fluff or over-praise. Emphasize evaluation based mostly on test quality.
# # """

# #     response = ollama.chat(
# #         model='llama3:8b',
# #         messages=[{"role": "user", "content": prompt}],
# #         options={
# #             "temperature": 0.3,      # Balanced response
# #             "top_p": 0.9,            # Controlled randomness
# #             "num_predict": 512       # Moderate length
# #         }
# #     )
    
# #     result = response['message']['content']
# #     return result



# # def generate_evaluation(transcript, test, job_role, skills_to_rate):
# #     skills_prompt = ""
# #     for skill in skills_to_rate:
# #         skills_prompt += f"   - {skill} (Rate 1-5 + comment)\n"

# #     prompt = f"""
# # Draft a short formal email for HR Team by Evaluating the candidate as a interviewer for [ROLE] based on:
# # -Interview Transcript:
# #     {transcript}
# # - Problem Solving Test Submission:
# #     {test}
# # - Job Role:
# #     {job_role}
# # Points to be included in the email:
# # - Candidate Name
# # - Summarize strengths and weaknesses (max 100 words)
# # - Strictly Rate these skills: [SKILLS] and give comments on each skill. 
# # - If skills are empty, rate the candidate on the relavent skills to the role.
# # - Striclth Rate each skill from 1 to 5, with 1 being the lowest and 5 being the highest.
# # - stricly rate and evalute candidate  based on coding skills
# # - Give a final recommendation: Strong Hire / Hire / Hold / Reject based on the  skills
# # - Add justification for the recommendation (max 100 words)
# #     """
    
# #     response = ollama.chat(
# #     model='llama3:8b',
# #     messages=[{"role": "user", "content": prompt}],
# #     options={
# #         "temperature": 0.3,      # More focused answers
# #         "top_p": 0.9,            # Reduces randomness
# #         "num_predict": 512       # Limits max tokens to speed up response
# #     }
# # )
    
# #     result = response['message']['content']
# #     return result



#     # response = requests.post(
#     #     'http://localhost:11434/api/generate',
#     #     # json={"model": "mistral", "prompt": prompt, "stream": True},
#     #     json={"model": "llama3:8b", "prompt": prompt, "stream": True},
#     #     stream=True
#     # )

#     # output = ""
#     # if response.status_code == 200:
#     #     for line in response.iter_lines():
#     #         if line:
#     #             try:
#     #                 data = json.loads(line.decode("utf-8"))
#     #                 output += data.get("response", "")
#     #             except json.JSONDecodeError as e:
#     #                 print(f"JSON decode error: {e}")
#     #     return output
#     # else:
#     #     return "Failed to generate evaluation from LLAMA3."
