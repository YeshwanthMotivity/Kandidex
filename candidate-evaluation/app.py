# from flask import Flask, request, jsonify
# import os
# from utils.extract_text import extract_text_from_file
# import time
# from utils.llama_prompt import generate_evaluation
# from utils.summarizer import summarize_text
# from flask_cors import CORS



# app = Flask(__name__)
# CORS(app)
# UPLOAD_FOLDER = 'uploads'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# def shorten_text(text, max_chars=1600):
#     return text[:max_chars]


# @app.route('/upload', methods=['POST'])
# def upload_files():
#     start = time.time()
#     transcript = request.files.get('transcript')
#     test = request.files.get('test')
#     job_role = request.form.get('job_role', '')  # Default fallback
#     skills_input = request.form.get('skills_to_rate', '')

#     # If empty, fallback to default skills
#     skills_to_rate = [s.strip() for s in skills_input.split(',')] if skills_input else [
#     "Communication Skills", "Technical Knowledge", "Problem Solving"
# ]
    
#     print("Transcript received:", transcript is not None)
#     print("Test received:", test is not None)

#     if not transcript or not test:
#         return jsonify({'error': 'Both files are required'}), 400

#     transcript_path = os.path.join(UPLOAD_FOLDER, transcript.filename)
#     test_path = os.path.join(UPLOAD_FOLDER, test.filename)
#     transcript.save(transcript_path)
#     test.save(test_path)
    
#     print("Extracting text from files...")

#     # Extract text
#     transcript_raw = extract_text_from_file(transcript_path)
#     test_raw = extract_text_from_file(test_path)

#     transcript_text = shorten_text(transcript_raw)
#     test_text = shorten_text(test_raw)


#     print("Transcript text:", transcript_text[:100])  # Print first 100 characters for debugging
#     # Generate evaluation email
#     print("Trying to summarize the context.... \n⏳ Please wait....\n")

#     # email_draft = generate_evaluation(transcript_text, test_text)
#     summarized_transcript = summarize_text(transcript_text)
#     summarized_test = summarize_text(test_text)
    
    
#     print("Generating mail... Please wait...\n⏳ Feeding into model...\n")

#     email_draft = generate_evaluation(summarized_transcript, summarized_test, job_role, skills_to_rate)

#     print("Email draft generated successfully!\n")
#     print("Time taken for email generation:", time.time() - start)

#     return jsonify({'result': email_draft})
#     # return email_draft

# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, request, jsonify
import os
from utils.extract_text import extract_text_from_file
import time
from utils.llama_prompt import generate_evaluation
from utils.summarizer import summarize_text
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def shorten_text(text, max_chars=1600):
    return text[:max_chars]

@app.route('/upload', methods=['POST'])
def upload_files():
    start = time.time()

    transcript = request.files.get('transcript')
    test = request.files.get('test')
    job_role_input = request.form.get('job_role', '')  # Optional
    skills_input = request.form.get('skills_to_rate', '')  # Optional

    if not transcript or not test:
        return jsonify({'error': 'Both transcript and test files are required'}), 400

    # Save uploaded files
    transcript_path = os.path.join(UPLOAD_FOLDER, transcript.filename)
    test_path = os.path.join(UPLOAD_FOLDER, test.filename)
    transcript.save(transcript_path)
    test.save(test_path)

    print("Extracting text from uploaded files...")

    # Extract and shorten text
    transcript_raw = extract_text_from_file(transcript_path)
    test_raw = extract_text_from_file(test_path)

    transcript_text = shorten_text(transcript_raw)
    test_text = shorten_text(test_raw)

    print("Summarizing transcript and test...")
    summarized_transcript = summarize_text(transcript_text)
    summarized_test = summarize_text(test_text)

    print("Generating evaluation email...")

    # If user provided skills or job role, pass them along; else auto-detect inside generate_evaluation
    email_draft = generate_evaluation(
        summarized_transcript,
        summarized_test,
        prompt_text=job_role_input or "",  # fallback to ""
    )

    print("Email draft generated successfully.")
    print("Time taken:", time.time() - start)

    return jsonify({'result': email_draft})

if __name__ == '__main__':
    app.run(debug=True)



# from flask import Flask, request, jsonify
# import os
# import time
# from flask_cors import CORS
# from utils.llama_prompt import generate_evaluation, extract_names_from_transcript
# from utils.extract_text import extract_text_from_file
# from utils.summarizer import summarize_text

# app = Flask(__name__)
# CORS(app)

# UPLOAD_FOLDER = 'uploads'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# def shorten_text(text, max_chars=1600):
#     return text[:max_chars]


# @app.route('/upload', methods=['POST'])
# def upload_files():
#     start = time.time()

#     transcript = request.files.get('transcript')
#     test = request.files.get('test')
#     job_role = request.form.get('job_role', '')
#     skills_input = request.form.get('skills_to_rate', '')

#     skills_to_rate = [s.strip() for s in skills_input.split(',')] if skills_input else [
#         "Communication Skills", "Technical Knowledge", "Problem Solving"
#     ]

#     if not transcript or not test:
#         return jsonify({'error': 'Both files are required'}), 400

#     transcript_path = os.path.join(UPLOAD_FOLDER, transcript.filename)
#     test_path = os.path.join(UPLOAD_FOLDER, test.filename)
#     transcript.save(transcript_path)
#     test.save(test_path)

#     print("Extracting text from files...")
#     transcript_raw = extract_text_from_file(transcript_path)
#     test_raw = extract_text_from_file(test_path)

#     transcript_text = shorten_text(transcript_raw)
#     test_text = shorten_text(test_raw)

#     print("Transcript text (partial):", transcript_text[:100])

#     print("Summarizing transcript and test...\n⏳")
#     summarized_transcript = summarize_text(transcript_text)
#     summarized_test = summarize_text(test_text)

#     print("Extracting names from transcript...")
    
#     # 🆕 Use the updated function and get confidence score
#     candidate_name, interviewer_name, confidence_score = extract_names_from_transcript(transcript_text)

#     print(f"Candidate: {candidate_name}, Interviewer: {interviewer_name}, Confidence: {confidence_score}/4")

#     print("Generating evaluation draft...")
#     email_draft = generate_evaluation(summarized_transcript, summarized_test, job_role, skills_to_rate)

#     # Replace placeholders in the email draft
#     email_draft = email_draft.replace("[Candidate Name]", candidate_name)
#     email_draft = email_draft.replace("[ROLE]", job_role)

#     print("✅ Email draft generated successfully!")
#     print("⏱️ Time taken:", round(time.time() - start, 2), "seconds")

#     # 🆕 Return extra info
#     return jsonify({
#         'result': email_draft,
#         'candidate_name': candidate_name,
#         'interviewer_name': interviewer_name,
#         'confidence_score': confidence_score
#     })
# if __name__ == '__main__':
#     app.run(debug=True)
# if __name__ == '__main__':
#     app.run(debug=True)