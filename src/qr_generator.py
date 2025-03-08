#!/usr/bin/env python3
"""
QR Code Generator for Promotional Codes

This script takes a CSV file containing promo codes and generates QR code vector files (SVG)
where each QR code links to a website with the promo code as a UTM parameter.
It can also generate PNG files and compile QR codes into a PDF.
"""

import os
import argparse
import pandas as pd
import qrcode
from qrcode.image.svg import SvgFragmentImage
from qrcode.image.pil import PilImage

# Import PDF compiler if available
try:
    from pdf_compiler import compile_qr_codes_to_pdf
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False


def generate_qr_codes(csv_file, base_url, output_dir, utm_param_name='promo', 
                    create_pdf=False, pdf_filename=None, pdf_page_size='letter',
                    create_png=False, png_size=300):
    """
    Generate QR codes from promo codes in a CSV file.
    
    Args:
        csv_file (str): Path to the CSV file containing promo codes.
        base_url (str): Base URL to which the promo code will be appended.
        output_dir (str): Directory where QR code files will be saved.
        utm_param_name (str): Name of the UTM parameter. Default is 'promo'.
        create_pdf (bool): Whether to create a PDF with all QR codes. Default is False.
        pdf_filename (str): Path to the output PDF file. Default is None (auto-generated).
        pdf_page_size (str): Page size for the PDF ('letter' or 'a4'). Default is 'letter'.
        create_png (bool): Whether to create PNG images. Default is False.
        png_size (int): Size of PNG images in pixels. Default is 300.
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create subdirectories for SVG and PNG files
    svg_dir = os.path.join(output_dir, "svg")
    os.makedirs(svg_dir, exist_ok=True)
    
    png_dir = None
    if create_png:
        png_dir = os.path.join(output_dir, "png")
        os.makedirs(png_dir, exist_ok=True)
    
    # Read the CSV file
    try:
        df = pd.read_csv(csv_file)
        if 'promo_code' not in df.columns:
            raise ValueError("CSV file must contain a 'promo_code' column")
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
    
    # Ensure base_url ends with a question mark or ampersand for proper parameter appending
    if '?' not in base_url:
        base_url += '?'
    elif not base_url.endswith('?') and not base_url.endswith('&'):
        base_url += '&'
    
    # Generate QR code for each promo code
    for index, row in df.iterrows():
        promo_code = row['promo_code']
        # Create the full URL with the promo code as a UTM parameter
        full_url = f"{base_url}{utm_param_name}={promo_code}"
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(full_url)
        qr.make(fit=True)
        
        # Create SVG image
        svg_img = qr.make_image(image_factory=SvgFragmentImage)
        svg_output_file = os.path.join(svg_dir, f"{promo_code}.svg")
        svg_img.save(svg_output_file)
        print(f"Generated SVG QR code for {promo_code}: {full_url}")
        
        # Create PNG image if requested
        if create_png:
            png_img = qr.make_image(image_factory=PilImage, fill_color="black", back_color="white")
            # Resize the image to the specified size
            png_img = png_img.resize((png_size, png_size))
            png_output_file = os.path.join(png_dir, f"{promo_code}.png")
            png_img.save(png_output_file)
            print(f"Generated PNG QR code for {promo_code}")
    
    print(f"SVG QR codes have been generated in the '{svg_dir}' directory.")
    if create_png:
        print(f"PNG QR codes have been generated in the '{png_dir}' directory.")
    
    # Create a PDF with all QR codes if requested
    if create_pdf and PDF_SUPPORT:
        if pdf_filename is None:
            # Auto-generate PDF filename based on output directory
            pdf_filename = os.path.join(output_dir, "qr_codes.pdf")
        
        # Compile QR codes into a PDF - use the SVG directory as source
        success = compile_qr_codes_to_pdf(svg_dir, pdf_filename, pdf_page_size, True)
        if success:
            print(f"PDF with QR codes has been generated: {pdf_filename}")
        else:
            print("Failed to generate PDF with QR codes.")
    elif create_pdf and not PDF_SUPPORT:
        print("PDF creation is not available. Make sure 'pdf_compiler.py' is in the same directory.")


def main():
    parser = argparse.ArgumentParser(description='Generate QR codes from promo codes in a CSV file.')
    parser.add_argument('csv_file', help='Path to the CSV file containing promo codes')
    parser.add_argument('base_url', help='Base URL to which the promo code will be appended')
    parser.add_argument('--output-dir', default='../output', help='Directory where QR code files will be saved')
    parser.add_argument('--utm-param-name', default='promo', help='Name of the UTM parameter (default: promo)')
    
    # Add PDF options
    parser.add_argument('--create-pdf', action='store_true', help='Create a PDF with all QR codes')
    parser.add_argument('--pdf-filename', help='Path to the output PDF file (default: [output_dir]/qr_codes.pdf)')
    parser.add_argument('--pdf-page-size', choices=['letter', 'a4'], default='letter', help='Page size for the PDF (letter or a4)')
    
    # Add PNG options
    parser.add_argument('--create-png', action='store_true', help='Create PNG images of QR codes')
    parser.add_argument('--png-size', type=int, default=300, help='Size of PNG images in pixels (default: 300)')
    
    args = parser.parse_args()
    
    generate_qr_codes(args.csv_file, args.base_url, args.output_dir, args.utm_param_name,
                     args.create_pdf, args.pdf_filename, args.pdf_page_size,
                     args.create_png, args.png_size)


if __name__ == '__main__':
    main() 