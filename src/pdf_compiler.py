#!/usr/bin/env python3
"""
PDF Compiler for QR Codes

This script takes QR codes (PNG or SVG format) and compiles them into a single PDF file,
with each QR code on a separate page.
"""

import os
import argparse
import glob
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Image, PageBreak, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from svglib.svglib import svg2rlg


def compile_qr_codes_to_pdf(input_dir, output_pdf, page_size='letter', include_code_text=True, use_png=False):
    """
    Compile QR codes in the input directory into a single PDF file.
    
    Args:
        input_dir (str): Directory containing QR codes.
        output_pdf (str): Path to the output PDF file.
        page_size (str): Page size ('letter' or 'a4').
        include_code_text (bool): Whether to include the promo code text below each QR code.
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
    
    # Set page size
    if page_size.lower() == 'a4':
        doc_page_size = A4
    else:
        doc_page_size = letter
    
    # Create the PDF document
    doc = SimpleDocTemplate(output_pdf, pagesize=doc_page_size)
    styles = getSampleStyleSheet()
    story = []
    
    # Add a title page
    title_style = styles['Title']
    story.append(Paragraph("QR Codes for Promotional Codes", title_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(f"Total QR Codes: {len(qr_files)}", styles['Normal']))
    story.append(PageBreak())
    
    # Process each QR code file
    for qr_file in qr_files:
        # Get the promo code (filename without extension)
        promo_code = os.path.splitext(os.path.basename(qr_file))[0]
        
        # Process based on file type
        if use_png:
            # For PNG files, use the Image class directly
            max_width = 5 * inch
            max_height = 5 * inch
            
            # Create an Image object
            img = Image(qr_file)
            
            # Scale to fit within max dimensions
            orig_width, orig_height = img.imageWidth, img.imageHeight
            scale = min(max_width/orig_width, max_height/orig_height)
            img.drawWidth = orig_width * scale
            img.drawHeight = orig_height * scale
            
            # Add PNG image to the PDF
            story.append(img)
        else:
            # Convert SVG to ReportLab graphic
            drawing = svg2rlg(qr_file)
            
            # Calculate QR code size (maintain aspect ratio)
            max_width = 5 * inch
            max_height = 5 * inch
            width = drawing.width
            height = drawing.height
            
            # Scale to fit within max dimensions
            scale = min(max_width/width, max_height/height)
            drawing.width = width * scale
            drawing.height = height * scale
            
            # Add QR code to the PDF
            story.append(drawing)
        
        # Add the promo code text below the QR code if requested
        if include_code_text:
            code_style = styles['Normal']
            story.append(Spacer(1, 0.25*inch))
            story.append(Paragraph(f"Promo Code: {promo_code}", code_style))
        
        # Add a page break after each QR code except the last one
        story.append(PageBreak())
    
    # Build the PDF
    doc.build(story)
    print(f"Created PDF with {len(qr_files)} QR codes: {output_pdf}")
    return True


def main():
    parser = argparse.ArgumentParser(description='Compile QR codes into a single PDF file.')
    parser.add_argument('input_dir', help='Directory containing QR codes or parent directory with svg/ or png/ subfolder')
    parser.add_argument('output_pdf', help='Path to the output PDF file')
    parser.add_argument('--page-size', choices=['letter', 'a4'], default='letter',
                        help='Page size (letter or a4)')
    parser.add_argument('--no-code-text', action='store_false', dest='include_code_text',
                        help='Do not include promo code text below QR codes')
    parser.add_argument('--use-png', action='store_true', 
                        help='Use PNG files instead of SVG files (default: use SVG)')
    
    args = parser.parse_args()
    
    compile_qr_codes_to_pdf(args.input_dir, args.output_pdf, 
                          args.page_size, args.include_code_text, args.use_png)


if __name__ == '__main__':
    main() 