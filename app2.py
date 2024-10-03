import tkinter as tk
from tkinter import filedialog, messagebox
from rembg import remove
from PIL import Image
import os
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import subprocess
import io
import uuid
from create_passport_photo_sheet import create_passport_photo_sheet

def merge_alternate_pdfs():
    def select_pdf1():
        pdf1_path = filedialog.askopenfilename(title="Select the first PDF", filetypes=[("PDF Files", "*.pdf")])
        if pdf1_path:
            entry1.delete(0, tk.END)  # Clear existing text
            entry1.insert(0, pdf1_path)  # Insert the selected path

    def select_pdf2():
        pdf2_path = filedialog.askopenfilename(title="Select the second PDF", filetypes=[("PDF Files", "*.pdf")])
        if pdf2_path:
            entry2.delete(0, tk.END)  # Clear existing text
            entry2.insert(0, pdf2_path)  # Insert the selected path

    def submit():
        pdf1_path = entry1.get()
        pdf2_path = entry2.get()
        
        if not pdf1_path or not pdf2_path:
            messagebox.showerror("Error", "Please select two PDF files.")
            return

        try:
            reader1 = PdfReader(pdf1_path)
            reader2 = PdfReader(pdf2_path)

            pages1 = list(reader1.pages)
            pages2 = list(reader2.pages)

            # Reverse the pages if the corresponding checkbox is checked
            if reverse_pdf1_var.get():
                pages1.reverse()

            if reverse_pdf2_var.get():
                pages2.reverse()

            writer = PdfWriter()

            total_pages = max(len(pages1), len(pages2))
            for i in range(total_pages):
                if i < len(pages1):
                    writer.add_page(pages1[i])
                if i < len(pages2):
                    writer.add_page(pages2[i])

            output_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
            if output_path:
                with open(output_path, 'wb') as f:
                    writer.write(f)
                messagebox.showinfo("Success", f"PDFs merged successfully: {output_path}")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    # Create a custom dialog window
    dialog = tk.Toplevel()
    dialog.title("Merge PDFs")

    tk.Label(dialog, text="Select the first PDF:").pack(pady=5)
    entry1 = tk.Entry(dialog, width=50)
    entry1.pack(pady=5)
    button1 = tk.Button(dialog, text="Browse...", command=select_pdf1)
    button1.pack(pady=5)

    # Checkbox to reverse the first PDF
    reverse_pdf1_var = tk.BooleanVar()
    reverse_pdf1_checkbox = tk.Checkbutton(dialog, text="Reverse first PDF", variable=reverse_pdf1_var)
    reverse_pdf1_checkbox.pack(pady=5)

    tk.Label(dialog, text="Select the second PDF:").pack(pady=5)
    entry2 = tk.Entry(dialog, width=50)
    entry2.pack(pady=5)
    button2 = tk.Button(dialog, text="Browse...", command=select_pdf2)
    button2.pack(pady=5)

    # Checkbox to reverse the second PDF
    reverse_pdf2_var = tk.BooleanVar()
    reverse_pdf2_checkbox = tk.Checkbutton(dialog, text="Reverse second PDF", variable=reverse_pdf2_var)
    reverse_pdf2_checkbox.pack(pady=5)

    submit_button = tk.Button(dialog, text="Merge PDFs", command=submit)
    submit_button.pack(pady=10)

    cancel_button = tk.Button(dialog, text="Cancel", command=dialog.destroy)
    cancel_button.pack(pady=5)


def remove_background():

    img_path = filedialog.askopenfilename(title="Select an image", filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.ico")])
    if not img_path:
        return
    
    try:
        print(img_path)
        input_image = Image.open(img_path)
        output_image = remove(input_image)

        # Convert to RGB if the image has an alpha channel (RGBA)
        if output_image.mode == 'RGBA':
            output_image = output_image.convert('RGB')

        output_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if not output_path:
            return

        output_image.save(output_path)
        messagebox.showinfo("Success", f"Background removed: {output_path}")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


def merge_pdfs():
    pdf_paths = filedialog.askopenfilenames(title="Select PDFs to merge", filetypes=[("PDF Files", "*.pdf")])
    
    if len(pdf_paths) < 2:
        messagebox.showerror("Error", "Please select at least two PDFs.")
        return

    try:
        merger = PdfMerger()

        for pdf in pdf_paths:
            merger.append(pdf)

        output_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if output_path:
            with open(output_path, 'wb') as f:
                merger.write(f)
            messagebox.showinfo("Success", f"PDFs merged successfully: {output_path}")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def compress_pdf():
    # Custom dialog to get PDF path and quality
    def get_compression_parameters():
        dialog = tk.Toplevel(root)
        dialog.title("Compress PDF")

        tk.Label(dialog, text="Select the PDF to compress:").pack(pady=5)
        pdf_path_entry = tk.Entry(dialog, width=50)
        pdf_path_entry.pack(pady=5)

        tk.Button(dialog, text="Browse", command=lambda: browse_pdf(pdf_path_entry)).pack(pady=5)

        tk.Label(dialog, text="Enter compression quality (0-100):").pack(pady=5)
        quality_var = tk.IntVar(value=75)
        quality_entry = tk.Entry(dialog, width=10, textvariable=quality_var)
        quality_entry.pack(pady=5)

        def on_submit():
            pdf_path = pdf_path_entry.get()
            quality = quality_entry.get()

            if not pdf_path or not quality.isdigit():
                messagebox.showerror("Error", "Please provide a valid PDF path and quality.")
                return

            quality = int(quality)
            if quality < 0 or quality > 100:
                messagebox.showerror("Error", "Quality must be between 0 and 100.")
                return

            dialog.destroy()
            compress_pdf_with_parameters(pdf_path, quality)

        tk.Button(dialog, text="Compress", command=on_submit).pack(pady=10)

    def browse_pdf(entry):
        pdf_path = filedialog.askopenfilename(title="Select PDF to compress", filetypes=[("PDF Files", "*.pdf")])
        if pdf_path:
            entry.delete(0, tk.END)
            entry.insert(0, pdf_path)

    def compress_pdf_with_parameters(pdf_path, quality):
        output_path = f'/tmp/output_{uuid.uuid4()}.pdf'

        try:
            # Mapping quality to Ghostscript settings
            quality_settings = {
                "screen": "/screen",
                "ebook": "/ebook",
                "printer": "/printer",
                "prepress": "/prepress"
            }

            if quality < 50:
                gs_quality = quality_settings["screen"]
            elif quality < 75:
                gs_quality = quality_settings["ebook"]
            elif quality < 90:
                gs_quality = quality_settings["printer"]
            else:
                gs_quality = quality_settings["prepress"]

            gs_command = [
                'gs',
                '-sDEVICE=pdfwrite',
                '-dCompatibilityLevel=1.4',
                f"-dPDFSETTINGS={gs_quality}",
                '-dNOPAUSE',
                '-dQUIET',
                '-dBATCH',
                f'-sOutputFile={output_path}',
                pdf_path
            ]

            subprocess.run(gs_command, check=True)

            save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
            if save_path:
                os.rename(output_path, save_path)
                messagebox.showinfo("Success", f"PDF compressed successfully: {save_path}")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    get_compression_parameters()

def create_passport_photo():
    img_path = filedialog.askopenfilename(title="Select an image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if not img_path:
        return

    try:
        img_io = create_passport_photo_sheet(img_path)
        
        output_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(img_io.getvalue())
            messagebox.showinfo("Success", f"Passport photo sheet created: {output_path}")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


# Tkinter UI setup
root = tk.Tk()
root.title("PDF and Image Processing App")

# Buttons for each functionality
merge_alternate_btn = tk.Button(root, text="Merge Alternate PDFs", command=merge_alternate_pdfs)
merge_alternate_btn.pack(pady=5)

remove_bg_btn = tk.Button(root, text="Remove Background", command=remove_background)
remove_bg_btn.pack(pady=5)

merge_pdf_btn = tk.Button(root, text="Merge PDFs", command=merge_pdfs)
merge_pdf_btn.pack(pady=5)

compress_pdf_btn = tk.Button(root, text="Compress PDF", command=compress_pdf)
compress_pdf_btn.pack(pady=5)

create_passport_btn = tk.Button(root, text="Create Passport Photo Sheet", command=create_passport_photo)
create_passport_btn.pack(pady=5)

root.mainloop()
