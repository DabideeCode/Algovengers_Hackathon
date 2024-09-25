from flask import Flask, request, jsonify, send_file, render_template
import PyPDF2
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from openai import OpenAI
import os

# Set up OpenAI API key
client = OpenAI(api_key='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')

app = Flask(__name__, template_folder=os.path.join(os.path.pardir, 'Site'))

@app.route('/')

def home():
    return render_template('index.html')

# Step 1: Upload and Extract Text from CV
def extract_text_from_pdf(pdf_path):
    # Extract text from PDF
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
    return text

# Step 2: Modify CV Text Using OpenAI
def anonymize_cv(cv_text):
    prompt = f"""
    Please modify the following CV by removing any gender-identifying information such as:
    1. Name (replace with "Candidate").
    2. Pronouns (replace with gender-neutral terms or remove altogether).
    3. Gender-specific titles (e.g., "Mr.", "Ms.", "Mrs.", "Miss" — replace with "Candidate").
    4. References to gender-specific organizations, activities, or experiences (either anonymize or remove).
    5. Any other information that could reveal the candidate’s gender.
    Keep the qualifications, work experience, and other details intact.
    
    CV Text:
    {cv_text}
    """

    response = client.chat.completions.create(
        model="gpt-4o", 
        messages=[
        {"role": "user", "content": prompt}
    ],
    )
    return response.choices[0].message.content

# Step 3: Generate New CV (PDF Format Example) using reportlab
def generate_new_cv(modified_text, output_pdf_path):
    # Create a PDF document with the modified text
    c = canvas.Canvas(output_pdf_path, pagesize=letter)
    text_object = c.beginText(40, 750)  # Starting position of the text
    text_object.setFont("Helvetica", 12)
    
    # Add each line to the PDF
    for line in modified_text.split("\n"):
        text_object.textLine(line)
    
    c.drawText(text_object)
    c.showPage()
    c.save()

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # Save the file to a temporary location
    file_path = os.path.join("uploads", file.filename)
    file.save(file_path)

    # Step 4: Extract text and anonymize it
    original_text = extract_text_from_pdf(file_path)
    modified_text = anonymize_cv(original_text)

    # Generate the anonymized CV as a PDF
    output_pdf_path = os.path.join("outputs", "anonymized_cv.pdf")
    generate_new_cv(modified_text, output_pdf_path)

    # Create the outputs directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__), 'outputs')
    output_pdf_path = os.path.join(output_dir, "anonymized_cv.pdf")
    # Return the anonymized PDF to the user
    return send_file(output_pdf_path, as_attachment=True)

if __name__ == '__main__':
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)
    app.run(debug=True)
