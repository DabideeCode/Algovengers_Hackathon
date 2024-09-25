from flask import Flask, request, jsonify, send_file, render_template, send_from_directory
import PyPDF2
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from openai import OpenAI
import os

# Set up OpenAI API key
client = OpenAI(api_key='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')

app = Flask(__name__, 
            template_folder=os.path.join(os.path.pardir, 'Site'),
            static_folder='../static')

# Route for the index page
@app.route('/')
def home():
    return render_template('index.html')

# Route for other pages (e.g., account, contact, demo)
@app.route('/<page_name>.html')
def render_page(page_name):
    return render_template(f'{page_name}.html')

# Serving static files (CSS, JS, Images) is handled automatically by Flask
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

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

    please froa
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

    output_pdf_path = '/Users/colemei/Library/Mobile Documents/com~apple~CloudDocs/01.Work/04.Master/Course/24 S2/2024 Hackathon/Algovengers_Hackathon/outputs/anonymized_cv.pdf'
    # Return the anonymized PDF to the user
    return send_file(output_pdf_path, as_attachment=True)

if __name__ == '__main__':
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)
    app.run(debug=True)
