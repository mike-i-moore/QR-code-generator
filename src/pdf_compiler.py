#!/usr/bin/env python3
"""
PDF Compiler for QR Codes

This script takes QR codes (PNG or SVG format) and compiles them into a single PDF file,
with each QR code on a separate page. Each page is sized to match the dimensions of its QR code.
"""

import os
import argparse
import glob
from reportlab.platypus import SimpleDocTemplate, Image, PageBreak, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter, A4
from svglib.svglib import svg2rlg
from reportlab.lib import pagesizes


def compile_qr_codes_to_pdf(input_dir, output_pdf, include_code_text=False, use_png=False):
    """
    Compile QR codes in the input directory into a single PDF file,
    with each page sized to match the dimensions of its QR code.
    
    Args:
        input_dir (str): Directory containing QR codes.
        output_pdf (str): Path to the output PDF file.
        include_code_text (bool): Whether to include the promo code text below each QR code (deprecated).
        use_png (bool): Whether to use PNG files instead of SVG files.
    """
    # Ensure input directory exists
    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist.")
        return False
    
    # Determine file format and subdirectory
    file_format = "png" if use_png else "svg"
    format_dir = os.path.join(input_dir, file_format)
    
    # Check if input_dir is the output directory with the folder structure
    if os.path.exists(format_dir) and os.path.isdir(format_dir):
        print(f"Found '{file_format}' subdirectory. Using {file_format.upper()} files from '{format_dir}'")
        input_dir = format_dir
    
    # Get all QR code files
    qr_files = glob.glob(os.path.join(input_dir, f"*.{file_format}"))
    if not qr_files:
        print(f"Error: No {file_format.upper()} files found in '{input_dir}'.")
        return False
    
    # Sort files alphabetically
    qr_files.sort()
    
    # Create PDF document with a temporary default page size
    # We'll set actual page sizes during document building
    doc = SimpleDocTemplate(output_pdf, pagesize=letter)
    
    # Process each QR code file to get sizes and prepare content
    pages = []
    page_sizes = []
    
    for qr_file in qr_files:
        # Get the promo code (filename without extension)
        promo_code = os.path.splitext(os.path.basename(qr_file))[0]
        
        page_content = []
        
        # Process based on file type
        if use_png:
            # For PNG files, use the Image class
            img = Image(qr_file)
            # Get original dimensions in points (1/72 inch)
            width, height = img.imageWidth, img.imageHeight
            
            # Use original dimensions without scaling
            img.drawWidth = width
            img.drawHeight = height
            
            # Add to content
            page_content.append(img)
            
            # Set page size to match image size
            page_sizes.append((width, height))
            
        else:
            # Convert SVG to ReportLab graphic
            drawing = svg2rlg(qr_file)
            
            # Get original dimensions
            width = drawing.width
            height = drawing.height
            
            # Add to content
            page_content.append(drawing)
            
            # Set page size to match drawing size
            page_sizes.append((width, height))
        
        # Add page break
        if len(qr_files) > 1:  # Only add page break if there's more than one file
            page_content.append(PageBreak())
        
        pages.append(page_content)
    
    # Build PDF with custom page sizes
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
    
    # Create a canvas with the output PDF filename
    c = canvas.Canvas(output_pdf)
    
    # Add each page with its custom size
    for i, (page_content, page_size) in enumerate(zip(pages, page_sizes)):
        # Set page size for this specific page
        c.setPageSize(page_size)
        
        # Draw the content on the canvas
        for item in page_content:
            if isinstance(item, Image):
                # For PIL Images
                item.drawOn(c, 0, 0)
            else:
                # For SVG drawings
                item.drawOn(c, 0, 0)
        
        if i < len(pages) - 1:  # Don't add a new page after the last one
            c.showPage()
    
    # Save the PDF
    c.save()
    print(f"Created PDF with {len(qr_files)} QR codes: {output_pdf}")
    return True


def main():
    parser = argparse.ArgumentParser(description='Compile QR codes into a single PDF file with custom page sizes.')
    parser.add_argument('input_dir', help='Directory containing QR codes or parent directory with svg/ or png/ subfolder')
    parser.add_argument('output_pdf', help='Path to the output PDF file')
    parser.add_argument('--no-code-text', action='store_false', dest='include_code_text',
                        help='Do not include promo code text below QR codes (deprecated, no text is added)')
    parser.add_argument('--use-png', action='store_true', 
                        help='Use PNG files instead of SVG files (default: use SVG)')
    
    args = parser.parse_args()
    
    compile_qr_codes_to_pdf(args.input_dir, args.output_pdf, 
                          args.include_code_text, args.use_png)


if __name__ == '__main__':
    main() 