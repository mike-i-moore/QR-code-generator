#!/usr/bin/env python3
"""
PDF Compiler for QR Codes

This script takes SVG QR codes and compiles them into a single PDF file,
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


def compile_qr_codes_to_pdf(input_dir, output_pdf, page_size='letter', include_code_text=True):
    """
    Compile all SVG QR codes in the input directory into a single PDF file.
    
    Args:
        input_dir (str): Directory containing SVG QR codes.
        output_pdf (str): Path to the output PDF file.
        page_size (str): Page size ('letter' or 'a4').
        include_code_text (bool): Whether to include the promo code text below each QR code.
    """
    # Ensure input directory exists
    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist.")
        return False
    
    # Check if input_dir is the output directory with the new folder structure
    svg_dir = os.path.join(input_dir, "svg")
    if os.path.exists(svg_dir) and os.path.isdir(svg_dir):
        print(f"Found 'svg' subdirectory. Using SVG files from '{svg_dir}'")
        input_dir = svg_dir
    
    # Get all SVG files
    svg_files = glob.glob(os.path.join(input_dir, "*.svg"))
    if not svg_files:
        print(f"Error: No SVG files found in '{input_dir}'.")
        return False
    
    # Sort files alphabetically
    svg_files.sort()
    
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
    story.append(Paragraph(f"Total QR Codes: {len(svg_files)}", styles['Normal']))
    story.append(PageBreak())
    
    # Process each SVG file
    for svg_file in svg_files:
        # Get the promo code (filename without extension)
        promo_code = os.path.splitext(os.path.basename(svg_file))[0]
        
        # Convert SVG to ReportLab graphic
        drawing = svg2rlg(svg_file)
        
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
    print(f"Created PDF with {len(svg_files)} QR codes: {output_pdf}")
    return True


def main():
    parser = argparse.ArgumentParser(description='Compile SVG QR codes into a single PDF file.')
    parser.add_argument('input_dir', help='Directory containing SVG QR codes or parent directory with svg/ subfolder')
    parser.add_argument('output_pdf', help='Path to the output PDF file')
    parser.add_argument('--page-size', choices=['letter', 'a4'], default='letter',
                        help='Page size (letter or a4)')
    parser.add_argument('--no-code-text', action='store_false', dest='include_code_text',
                        help='Do not include promo code text below QR codes')
    
    args = parser.parse_args()
    
    compile_qr_codes_to_pdf(args.input_dir, args.output_pdf, 
                          args.page_size, args.include_code_text)


if __name__ == '__main__':
    main() 