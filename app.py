# Standard Python Libraries
import os
import io

# Third-party libraries
from openai import OpenAI
from flask import Flask, request, jsonify, send_file, render_template, send_from_directory
import PyPDF2
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Get the API key from the environment variable
api_key = os.getenv('OPENAI_API_KEY')

# Check if the API key is loaded correctly
if not api_key:
    raise ValueError("OpenAI API key is missing. Please set it in the environment variables.")

# Set up OpenAI API key
client = OpenAI(api_key=api_key)

# Initialize Flask app and configure the template and static folder paths
app = Flask(__name__)

# Route for the index page (landing page)
@app.route('/')
def home():
    return render_template('index.html')  # Render the index page

# Route for other pages like account, contact, and demo
@app.route('/<page_name>.html')
def render_page(page_name):
    return render_template(f'{page_name}.html')  # Render any page based on the URL

# Serving static files (CSS, JS, Images)
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)  # Send the requested static file from the static directory

# Step 1: Extract text from the uploaded PDF file
def extract_text_from_pdf(file_stream):
    # Extract text from the PDF (file_stream is the in-memory file)
    reader = PyPDF2.PdfReader(file_stream)
    text = ''
    for page in reader.pages:
        text += page.extract_text()  # Extract text from each page and append it
    return text

# Step 2: Use OpenAI to anonymize the CV text
def anonymize_cv(cv_text):
    # The prompt tells OpenAI to remove gender-identifying information and format the output in markdown
    prompt = f"""
        Please modify the following CV by removing any gender-identifying information such as:
        1. Name (replace with "Candidate").
        2. Pronouns (replace with gender-neutral terms or remove altogether).
        3. Gender-specific titles (e.g., "Mr.", "Ms.", "Mrs.", "Miss" — replace with "Candidate").
        4. References to gender-specific organizations, activities, or experiences (either anonymize or remove).
        5. Any other information that could reveal the candidate’s gender.

        After anonymizing, please output **only the anonymized CV text** in markdown format with no additional information or commentary. The markdown format should include:
        - Use `###` for headings (e.g., `Work Experience`, `Education`, etc.)
        - Regular text for bullet points and descriptions.

        CV Text:
        {cv_text}
    """
    # Send the prompt to OpenAI and get the anonymized CV text in markdown format
    response = client.chat.completions.create(
        model="gpt-4o", 
        messages=[
        {"role": "user", "content": prompt}
    ],
    )
    # Return the anonymized text from OpenAI's response
    return response.choices[0].message.content

# Step 3: Generate a new CV in PDF format from the markdown text
def generate_new_cv(markdown_text):
    # Create a BytesIO object to store the PDF in memory
    pdf_file = io.BytesIO()

    # Create a new PDF using the reportlab library and write the modified markdown text to it
    c = canvas.Canvas(pdf_file, pagesize=letter)
    text_object = c.beginText(40, 750)  # Starting position of the text
    text_object.setFont("Helvetica", 12)  # Set the font to Helvetica, size 12
    
    # Parse the markdown text to a structured format
    parsed_lines = parse_markdown(markdown_text)
    
    # Add each line to the PDF based on its type (heading, bullet point, or regular text)
    for line_type, content in parsed_lines:
        if line_type == "heading":
            text_object.setFont("Helvetica-Bold", 14)  # Use bold font for headings
            text_object.textLine(content)
            text_object.setFont("Helvetica", 12)  # Reset to default after heading
        elif line_type == "bullet":
            text_object.textLine(content)  # Add bullet points
        else:
            text_object.textLine(content)  # Add regular text
    
    c.drawText(text_object)
    c.showPage()
    c.save()

    # Move the BytesIO cursor to the beginning of the file to prepare for reading
    pdf_file.seek(0)
    
    # Return the in-memory BytesIO object containing the PDF data
    return pdf_file

# Helper function: Parse markdown to structured lines for rendering in the PDF
def parse_markdown(markdown_text):
    """Converts markdown text into structured lines for PDF rendering."""
    lines = markdown_text.split("\n")  # Split the markdown text into lines
    parsed_lines = []
    
    for line in lines:
        if line.startswith("### "):  # Handle headings in markdown (### indicates a heading)
            parsed_lines.append(("heading", line.replace("### ", "")))  # Add as a heading
        elif line.startswith("- "):  # Handle bullet points in markdown (- indicates a bullet point)
            parsed_lines.append(("bullet", line.replace("- ", u"• ")))  # Convert markdown bullets to actual bullets
        else:  # Handle regular text
            parsed_lines.append(("text", line))  # Add as regular text
    
    return parsed_lines

# Step 4: Upload the CV, process it, and return the anonymized CV as a PDF
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400  # Return error if no file is uploaded

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400  # Return error if file name is empty

    # Step 1: Extract text from the uploaded PDF file
    original_text = extract_text_from_pdf(file)

    # Step 2: Anonymize the text using OpenAI
    modified_text = anonymize_cv(original_text)

    # Step 3: Generate a new CV in PDF format from the anonymized text
    pdf_file = generate_new_cv(modified_text)

    # Step 4: Return the generated PDF file as a downloadable attachment
    return send_file(pdf_file, as_attachment=True, download_name="anonymized_cv.pdf", mimetype='application/pdf')

# Run the Flask app in debug mode
if __name__ == '__main__':
    app.run(debug=True)
