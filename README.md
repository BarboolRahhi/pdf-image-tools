# Flask PDF and Image Processing API

This Flask application provides several endpoints for processing PDFs and images, including merging PDFs, removing backgrounds from images, compressing PDFs, and creating passport photo sheets.

## Features

- **Merge PDFs**: Merge two PDFs in an alternate order.
- **Remove Background**: Remove the background from an uploaded image.
- **Merge Multiple PDFs**: Merge multiple PDFs into one.
- **Compress PDF**: Compress a PDF with adjustable quality settings.
- **Create Passport Photo**: Generate a passport photo from an uploaded image.

## Requirements

- Python 3.7+
- Flask
- Pillow (PIL)
- PyPDF2
- rembg
- Ghostscript (for PDF compression)
