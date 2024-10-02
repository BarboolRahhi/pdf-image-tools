from flask import Flask, render_template, request, redirect, send_file
from rembg import remove
from PIL import Image
import os
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import subprocess
import io
import uuid

from create_passport_photo_sheet import create_passport_photo_sheet 

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/merge-alternate-pdf', methods=['GET', 'POST'])
def merge_alternate_pdf_page():
    if request.method == 'POST':
        pdf1 = request.files['pdf1']
        pdf2 = request.files['pdf2']
        reverse_pdf1 = request.form.get('reverse_pdf1') == 'on'
        reverse_pdf2 = request.form.get('reverse_pdf2') == 'on'

        if not pdf1 or not pdf2:
            return redirect(request.url)

        # Read the PDFs
        reader1 = PdfReader(pdf1)
        reader2 = PdfReader(pdf2)

        pages1 = list(reader1.pages)
        pages2 = list(reader2.pages)

        if reverse_pdf1:
            pages1 = pages1[::-1]
        if reverse_pdf2:
            pages2 = pages2[::-1]

        writer = PdfWriter()
        
        # Merge pages in alternate order
        total_pages = max(len(pages1), len(pages2))
        for i in range(total_pages):
            if i < len(pages1):
                writer.add_page(pages1[i])
            if i < len(pages2):
                writer.add_page(pages2[i])

        pdf_bytes_io = io.BytesIO()
        
        # with open(output_path, 'wb') as output_file:
        writer.write(pdf_bytes_io)

        pdf_bytes_io.seek(0)

        writer.close()

        return send_file(pdf_bytes_io, mimetype='application/pdf', as_attachment=True, download_name='output.pdf')
    
    return render_template('merge_alternate_pdf.html', merged_pdf=None)

@app.route('/remove-background')
def remove_background_page():
    return render_template('remove_background.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return redirect(request.url)
    
    file = request.files['image']
    
    if file.filename == '':
        return redirect(request.url)
    
    if file:
        
        # Process the image to remove background
        input_image = Image.open(file)
        output_image = remove(input_image)
        
        # Convert to RGB if the image has an alpha channel (RGBA)
        if output_image.mode == 'RGBA':
            output_image = output_image.convert('RGB')

        
        img_io = io.BytesIO()
        output_image.save(img_io, format='PNG')
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='output.png')

@app.route('/merge-pdf')
def merge_pdf_page():
    return render_template('merge_pdf.html')

@app.route('/merge', methods=['POST'])
def merge_pdf():
    pdf_files = request.files.getlist('pdf_files')
    
    if len(pdf_files) < 2:
        return redirect(request.url)

    merger = PdfMerger()

    for file in pdf_files:
        if file.filename.endswith('.pdf'):
            merger.append(file)

    pdf_bytes_io = io.BytesIO()
        
        # with open(output_path, 'wb') as output_file:
    merger.write(pdf_bytes_io)

    pdf_bytes_io.seek(0)

    merger.close()

    return send_file(pdf_bytes_io, mimetype='application/pdf', as_attachment=True, download_name='output.pdf')

@app.route('/compress-pdf', methods=['POST'])
def compress_pdf():
    pdf = request.files['pdf']
    quality = int(request.form.get('quality', 75))

    if not pdf:
        return redirect(request.url)
    

    input_pdf = io.BytesIO(pdf.read())
    output_pdf = io.BytesIO()

    # Write the input PDF to a temporary file since Ghostscript works with files
    input_path = f'/tmp/input_{uuid.uuid4()}.pdf'
    output_path = f'/tmp/output_{uuid.uuid4()}.pdf'

    with open(input_path, 'wb') as f:
        f.write(input_pdf.getvalue())

    # Save the uploaded PDF
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf.filename)
    pdf.save(pdf_path)

    try:
        # Mapping quality to Ghostscript settings
        quality_settings = {
            "screen": "/screen",
            "ebook": "/ebook",
            "printer": "/printer",
            "prepress": "/prepress"
        }

        # Use 'screen' settings for lower quality (higher compression) and 'prepress' for high quality (lower compression)
        if quality < 50:
            gs_quality = quality_settings["screen"]
        elif quality < 75:
            gs_quality = quality_settings["ebook"]
        elif quality < 90:
            gs_quality = quality_settings["printer"]
        else:
            gs_quality = quality_settings["prepress"]

        # Run Ghostscript command to compress the PDF
        gs_command = [
            'gs',
            '-sDEVICE=pdfwrite',
            '-dCompatibilityLevel=1.4',
            f"-dPDFSETTINGS={gs_quality}",  # Adjust compression quality here
            '-dNOPAUSE',
            '-dQUIET',
            '-dBATCH',
            f'-sOutputFile={output_path}',
            input_path
        ]

        subprocess.run(gs_command, check=True)

        # Read the output PDF from the temporary file
        with open(output_path, 'rb') as f:
            output_pdf.write(f.read())

        # Set the pointer to the beginning of the output stream
        output_pdf.seek(0)

    finally:
        #Delete the temporary files
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)

    # Send the compressed PDF as response
    return send_file(output_pdf, mimetype='application/pdf', as_attachment=True, download_name='compressed_output.pdf')

@app.route('/compress-pdf')
def compress_pdf_page():
    return render_template('compress_pdf.html')

@app.route('/create-passport-photo')
def create_passport_photo_page():
    return render_template('create_passport_photo.html')

@app.route('/create-passport-photo', methods=['POST'])
def create_passport_photo():
    if 'image' not in request.files:
        return redirect(request.url)
    
    file = request.files['image']
    
    if file.filename == '':
        return redirect(request.url)
    
    if file:
        img_io = create_passport_photo_sheet(file)
       
        return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='output.png')

if __name__ == "__main__":
    app.run(debug=True)
