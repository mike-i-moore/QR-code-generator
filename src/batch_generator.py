#!/usr/bin/env python3
"""
Batch QR Code Generator

This script provides a user-friendly interface for generating QR codes from promo codes
in a CSV file (with a 'promo_code' column) or a TXT file (with one code per line).
"""

import os
import sys
from qr_generator import generate_qr_codes, PDF_SUPPORT


def get_user_input():
    """
    Prompt the user for input parameters.
    
    Returns:
        tuple: (input_file, base_url, output_dir, utm_param_name, create_pdf, pdf_filename, pdf_page_size, create_png, png_size)
    """
    print("=== QR Code Generator for Promotional Codes ===")
    
    # Get the input file path
    while True:
        input_file = input("Enter the path to the file with promo codes (CSV or TXT): ").strip()
        if os.path.exists(input_file):
            # Check file extension
            _, ext = os.path.splitext(input_file)
            if ext.lower() not in ['.csv', '.txt']:
                print(f"Warning: File '{input_file}' does not have a .csv or .txt extension.")
                confirm = input("Continue anyway? (y/n): ").strip().lower()
                if confirm not in ['y', 'yes']:
                    continue
            break
        print(f"Error: File '{input_file}' does not exist. Please enter a valid path.")
    
    # Get the base URL
    base_url = input("Enter the base URL (e.g., https://example.com/promo): ").strip()
    
    # Get the output directory
    output_dir = input("Enter the output directory for QR codes [default: ../output]: ").strip()
    if not output_dir:
        output_dir = "../output"
    
    # Get the UTM parameter name
    utm_param_name = input("Enter the UTM parameter name [default: promo]: ").strip()
    if not utm_param_name:
        utm_param_name = "promo"
    
    # PNG options
    create_png_input = input("Do you want to create PNG images of QR codes? (y/n) [default: n]: ").strip().lower()
    create_png = create_png_input == 'y' or create_png_input == 'yes'
    
    png_size = 300  # default
    if create_png:
        png_size_input = input("Enter the size of PNG images in pixels [default: 300]: ").strip()
        if png_size_input and png_size_input.isdigit():
            png_size = int(png_size_input)
    
    # PDF options
    create_pdf = False
    pdf_filename = None
    pdf_page_size = 'letter'
    
    if PDF_SUPPORT:
        create_pdf_input = input("Do you want to create a PDF with all QR codes? (y/n) [default: n]: ").strip().lower()
        create_pdf = create_pdf_input == 'y' or create_pdf_input == 'yes'
        
        if create_pdf:
            pdf_filename_input = input("Enter the path to the output PDF file [default: [output_dir]/qr_codes.pdf]: ").strip()
            if pdf_filename_input:
                pdf_filename = pdf_filename_input
            
            pdf_page_size_input = input("Enter the page size for the PDF (letter/a4) [default: letter]: ").strip().lower()
            if pdf_page_size_input == 'a4':
                pdf_page_size = 'a4'
    
    return input_file, base_url, output_dir, utm_param_name, create_pdf, pdf_filename, pdf_page_size, create_png, png_size


def main():
    try:
        # Get user input
        input_file, base_url, output_dir, utm_param_name, create_pdf, pdf_filename, pdf_page_size, create_png, png_size = get_user_input()
        
        # Generate QR codes
        print("\nGenerating QR codes...")
        generate_qr_codes(input_file, base_url, output_dir, utm_param_name, 
                        create_pdf, pdf_filename, pdf_page_size,
                        create_png, png_size)
        
        print("\nDone!")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 