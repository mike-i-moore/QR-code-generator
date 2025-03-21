#!/usr/bin/env python3
"""
QR Code Generator for Promotional Codes

This script takes a CSV file containing promo codes or a TXT file with one code per line,
and generates QR code vector files (SVG) where each QR code links to a website with 
the promo code as a UTM parameter. It can also generate PNG files and compile QR codes into a PDF.
"""

import os
import argparse
import pandas as pd
import qrcode
from qrcode.image.svg import SvgFragmentImage
from qrcode.image.pil import PilImage
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Import PDF compiler if available
try:
    from pdf_compiler import compile_qr_codes_to_pdf
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False


def generate_qr_codes(input_file, base_url, output_dir, utm_param_name='promo', 
                    create_pdf=False, pdf_filename=None, pdf_page_size='letter',
                    create_png=False, png_size=300, create_svg=True,
                    pdf_prepared_for=None, pdf_title="QR Codes Collection"):
    """
    Generate QR codes from promo codes in a CSV or TXT file.
    
    Args:
        input_file (str): Path to the CSV or TXT file containing promo codes.
        base_url (str): Base URL to which the promo code will be appended.
        output_dir (str): Directory where QR code files will be saved.
        utm_param_name (str): Name of the UTM parameter. Default is 'promo'.
        create_pdf (bool): Whether to create a PDF with all QR codes. Default is False.
        pdf_filename (str): Path to the output PDF file. Default is None (auto-generated).
        pdf_page_size (str): Page size for the PDF ('letter' or 'a4'). Default is 'letter'.
        create_png (bool): Whether to create PNG images. Default is False.
        png_size (int): Size of PNG images in pixels. Default is 300.
        create_svg (bool): Whether to create SVG files. Default is True.
        pdf_prepared_for (str): Name of the recipient for whom the PDF is prepared. Default is None.
        pdf_title (str): Title to display on the PDF title page. Default is "QR Codes Collection".
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create subdirectories for SVG and PNG files
    svg_dir = None
    if create_svg:
        svg_dir = os.path.join(output_dir, "svg")
        os.makedirs(svg_dir, exist_ok=True)
    
    png_dir = None
    if create_png:
        png_dir = os.path.join(output_dir, "png")
        os.makedirs(png_dir, exist_ok=True)
    
    # Determine file type based on extension
    file_extension = os.path.splitext(input_file)[1].lower()
    
    # Read the input file based on its type
    promo_codes = []
    
    if file_extension == '.csv':
        # Read CSV file
        try:
            df = pd.read_csv(input_file)
            if 'promo_code' not in df.columns:
                raise ValueError("CSV file must contain a 'promo_code' column")
            promo_codes = df['promo_code'].tolist()
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return
    elif file_extension == '.txt':
        # Read TXT file - one promo code per line
        try:
            with open(input_file, 'r') as f:
                # Strip whitespace and filter out empty lines
                promo_codes = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"Error reading TXT file: {e}")
            return
    else:
        print(f"Unsupported file type: {file_extension}. Please use .csv or .txt files.")
        return
    
    if not promo_codes:
        print("No promo codes found in the input file.")
        return
        
    # Ensure base_url ends with a question mark or ampersand for proper parameter appending
    if '?' not in base_url:
        base_url += '?'
    elif not base_url.endswith('?') and not base_url.endswith('&'):
        base_url += '&'
    
    # Generate QR code for each promo code
    for promo_code in promo_codes:
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
        
        # Create SVG image if requested
        if create_svg:
            svg_img = qr.make_image(image_factory=SvgFragmentImage)
            svg_output_file = os.path.join(svg_dir, f"{promo_code}.svg")
            svg_img.save(svg_output_file)
            print(f"Generated SVG QR code for {promo_code}: {full_url}")
        
        # Create PNG image if requested
        if create_png:
            # Create QR code PNG with transparent background
            png_img = qr.make_image(image_factory=PilImage, fill_color="black", back_color="white")
            # Resize the image to the specified size
            png_img = png_img.resize((png_size, png_size))
            
            # Convert to RGBA to support transparency
            qr_rgba = png_img.convert('RGBA')
            
            # Replace white with transparent in QR code
            qr_data = qr_rgba.getdata()
            new_data = []
            for item in qr_data:
                # If pixel is white (or close to white), make it transparent
                if item[0] > 240 and item[1] > 240 and item[2] > 240:
                    new_data.append((255, 255, 255, 0))  # White with alpha=0 (transparent)
                else:
                    new_data.append(item)  # Keep the original color
            qr_rgba.putdata(new_data)
            
            # Create a text image for the promo code with transparency
            # Create at a much higher resolution for better downsampling later
            scale_factor = 8  # Increased for even better quality but balanced for font size
            font_size = (png_size // 12) * scale_factor  # Reduced font size with a larger divisor (was 8)
            text_height = font_size * 2  # Height for text section
            text_width_prelim = png_size * scale_factor  # Initial width at high resolution
            
            # Create a high-resolution transparent image for text with padding
            text_img_high_res = Image.new('RGBA', (text_width_prelim, text_height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(text_img_high_res)
            
            # Find a suitable font - prioritize regular (non-bold) fonts for better scaling
            font = None
            # Try different fonts with larger size for better quality - prioritize regular fonts
            font_names = [
                "Arial", "Helvetica", "DejaVuSans", "Verdana", "Tahoma",
                "SF Pro Text", "Roboto", "Open Sans"
            ]
            
            for font_name in font_names:
                try:
                    font = ImageFont.truetype(font_name, font_size)
                    break
                except IOError:
                    continue
            
            # If none of the preferred fonts are available, fall back to system fonts
            if font is None:
                try:
                    # On macOS, try these common system fonts - prioritize regular fonts
                    mac_fonts = [
                        "/System/Library/Fonts/SFNSText-Regular.otf",
                        "/System/Library/Fonts/Helvetica.ttc", 
                        "/Library/Fonts/Arial.ttf",
                        "/System/Library/Fonts/SFNSDisplay.ttf",
                        "/System/Library/Fonts/SFNSText.ttf"
                    ]
                    for mac_font in mac_fonts:
                        try:
                            font = ImageFont.truetype(mac_font, font_size)
                            break
                        except IOError:
                            continue
                except Exception:
                    # Last resort: use default font
                    font = ImageFont.load_default()
                    # Adjust for default font which may be lower quality
                    font_size = text_height // 3
            
            # Calculate text width and position it centered
            if hasattr(draw, "textlength"):
                # Newer Pillow versions
                text_width = draw.textlength(promo_code, font=font)
            else:
                # For older Pillow versions
                text_width, _ = draw.textsize(promo_code, font=font)
                
            text_position = ((text_width_prelim - text_width) // 2, (text_height - font_size) // 2)
            
            # Draw the text with advanced anti-aliasing techniques
            
            # 1. First add a subtle shadow/glow for better edge definition
            shadow_offsets = [(1, 1), (-1, -1), (1, -1), (-1, 1)]
            
            for offset_x, offset_y in shadow_offsets:
                draw.text((text_position[0] + offset_x, text_position[1] + offset_y), 
                         promo_code, fill=(0, 0, 0, 20), font=font)
            
            # 2. Draw outline/stroke around the text for better definition (thinner outline for non-bold)
            stroke_offsets = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            
            for offset_x, offset_y in stroke_offsets:
                draw.text((text_position[0] + offset_x, text_position[1] + offset_y), 
                         promo_code, fill=(0, 0, 0, 100), font=font)
            
            # 3. Draw the main text
            draw.text(text_position, promo_code, fill=(0, 0, 0, 255), font=font)
            
            # 4. Apply a very slight blur for anti-aliasing (reduced for sharper text)
            text_img_high_res = text_img_high_res.filter(ImageFilter.GaussianBlur(0.3))
            
            # 5. Sharpen more to maintain crispness while keeping anti-aliasing
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Sharpness(text_img_high_res)
            text_img_high_res = enhancer.enhance(1.5)  # Increased sharpening for better definition
            
            # 6. Downscale the high-resolution text image to the target size
            # using high-quality resampling for smoother results
            text_img = text_img_high_res.resize(
                (png_size, text_height // scale_factor), 
                Image.Resampling.LANCZOS
            )
            
            # Combine the QR code and text images with a slight spacing
            spacing = 5  # Add a small spacing between QR code and text
            combined_height = qr_rgba.height + text_img.height + spacing
            combined_img = Image.new('RGBA', (png_size, combined_height), (0, 0, 0, 0))
            combined_img.paste(qr_rgba, (0, 0), qr_rgba)
            combined_img.paste(text_img, (0, qr_rgba.height + spacing), text_img)
            
            # Save the combined image with transparency and optimal compression
            png_output_file = os.path.join(png_dir, f"{promo_code}.png")
            combined_img.save(png_output_file, format='PNG', optimize=True, compression=9)
            print(f"Generated high-quality transparent PNG QR code with text for {promo_code}")
    
    if create_svg:
        print(f"SVG QR codes have been generated in the '{svg_dir}' directory.")
    if create_png:
        print(f"Transparent PNG QR codes with text have been generated in the '{png_dir}' directory.")
    
    # Create a PDF with all QR codes if requested
    if create_pdf and PDF_SUPPORT:
        if pdf_filename is None:
            # Auto-generate PDF filename based on output directory
            pdf_filename = os.path.join(output_dir, "qr_codes.pdf")
        
        # Determine which type of files to use for PDF generation
        # If SVG files were created, use them
        # If only PNG files were created, use those instead
        use_png = not create_svg and create_png
        
        if not create_svg:
            if not create_png:
                # Neither SVG nor PNG files were created, generate temporary SVG files for PDF
                temp_svg_dir = os.path.join(output_dir, "temp_svg")
                os.makedirs(temp_svg_dir, exist_ok=True)
                
                for promo_code in promo_codes:
                    full_url = f"{base_url}{utm_param_name}={promo_code}"
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
                    )
                    qr.add_data(full_url)
                    qr.make(fit=True)
                    
                    svg_img = qr.make_image(image_factory=SvgFragmentImage)
                    svg_output_file = os.path.join(temp_svg_dir, f"{promo_code}.svg")
                    svg_img.save(svg_output_file)
                
                # Compile QR codes into a PDF using the temporary SVG directory
                success = compile_qr_codes_to_pdf(
                    temp_svg_dir, pdf_filename, False, False,
                    pdf_prepared_for, pdf_title
                )
                
                # Clean up temporary SVG files
                import shutil
                shutil.rmtree(temp_svg_dir)
            else:
                # Only PNG files were created, use them for the PDF
                success = compile_qr_codes_to_pdf(
                    output_dir, pdf_filename, False, True,
                    pdf_prepared_for, pdf_title
                )
        else:
            # SVG files were created, use them for the PDF
            success = compile_qr_codes_to_pdf(
                output_dir, pdf_filename, False, False,
                pdf_prepared_for, pdf_title
            )
        
        if success:
            print(f"PDF with QR codes has been generated: {pdf_filename}")
        else:
            print("Failed to generate PDF with QR codes.")
    elif create_pdf and not PDF_SUPPORT:
        print("PDF creation is not available. Make sure 'pdf_compiler.py' is in the same directory.")


def main():
    parser = argparse.ArgumentParser(description='Generate QR codes from promo codes in a CSV or TXT file.')
    parser.add_argument('input_file', help='Path to the file containing promo codes (CSV with a "promo_code" column or TXT with one code per line)')
    parser.add_argument('base_url', help='Base URL to which the promo code will be appended')
    parser.add_argument('--output-dir', default='../output', help='Directory where QR code files will be saved')
    parser.add_argument('--utm-param-name', default='promo', help='Name of the UTM parameter (default: promo)')
    
    # Add SVG options
    parser.add_argument('--create-svg', action='store_true', default=True, help='Create SVG vector files (default: True)')
    parser.add_argument('--no-svg', dest='create_svg', action='store_false', help='Do not create SVG vector files')
    
    # Add PDF options
    parser.add_argument('--create-pdf', action='store_true', help='Create a PDF with all QR codes')
    parser.add_argument('--pdf-filename', help='Path to the output PDF file (default: [output_dir]/qr_codes.pdf)')
    parser.add_argument('--pdf-page-size', choices=['letter', 'a4'], default='letter', help='Page size for the PDF (letter or a4)')
    parser.add_argument('--pdf-prepared-for', help='Name of the recipient for whom the PDF is prepared')
    parser.add_argument('--pdf-title', default="QR Codes Collection", help='Title to display on the PDF title page')
    
    # Add PNG options
    parser.add_argument('--create-png', action='store_true', help='Create transparent PNG images of QR codes with text')
    parser.add_argument('--png-size', type=int, default=300, help='Size of PNG images in pixels (default: 300)')
    
    # Add interactive mode flag
    parser.add_argument('--interactive', '-i', action='store_true', help='Run in interactive mode, prompting for file type choices')
    
    args = parser.parse_args()
    
    # Interactive mode: Ask user for preferences if --interactive flag is set
    if args.interactive:
        # Ask about SVG creation
        svg_response = input("Generate SVG vector files? (y/n, default: y): ").strip().lower()
        create_svg = not (svg_response == 'n' or svg_response == 'no')
        
        # Ask about PNG creation
        png_response = input("Generate PNG files? (y/n, default: n): ").strip().lower()
        create_png = png_response.startswith('y')
        
        png_size = args.png_size
        if create_png:
            size_response = input(f"PNG size in pixels (default: {png_size}): ").strip()
            if size_response and size_response.isdigit():
                png_size = int(size_response)
                
        # Ask about PDF creation
        pdf_response = input("Generate PDF file? (y/n, default: n): ").strip().lower()
        create_pdf = pdf_response.startswith('y')
        
        pdf_filename = args.pdf_filename
        pdf_page_size = args.pdf_page_size
        pdf_prepared_for = args.pdf_prepared_for
        pdf_title = args.pdf_title
        
        if create_pdf:
            if PDF_SUPPORT:
                # Ask for PDF title
                pdf_title_input = input(f"PDF title [default: {pdf_title}]: ").strip()
                if pdf_title_input:
                    pdf_title = pdf_title_input
                
                # Ask for PDF recipient
                pdf_prepared_for_input = input("PDF prepared for (leave blank for manual entry): ").strip()
                if pdf_prepared_for_input:
                    pdf_prepared_for = pdf_prepared_for_input
            else:
                print("Warning: PDF creation is not available. Make sure 'pdf_compiler.py' is in the same directory.")
                create_pdf = False
    else:
        # Use command line arguments
        create_svg = args.create_svg
        create_png = args.create_png
        png_size = args.png_size
        create_pdf = args.create_pdf
        pdf_filename = args.pdf_filename
        pdf_page_size = args.pdf_page_size
        pdf_prepared_for = args.pdf_prepared_for
        pdf_title = args.pdf_title
    
    # Confirm the selected options
    print("\nGenerating QR codes with the following options:")
    print(f"- Input file: {args.input_file}")
    print(f"- Base URL: {args.base_url}")
    print(f"- Output directory: {args.output_dir}")
    print(f"- Creating SVG files: {'Yes' if create_svg else 'No'}")
    print(f"- Creating PNG files: {'Yes' if create_png else 'No'}")
    if create_png:
        print(f"  - PNG size: {png_size}px")
    print(f"- Creating PDF file: {'Yes' if create_pdf else 'No'}")
    if create_pdf:
        print(f"  - PDF page size: Custom (matches QR code dimensions)")
        print(f"  - PDF title: {pdf_title}")
        if pdf_prepared_for:
            print(f"  - PDF prepared for: {pdf_prepared_for}")
        else:
            print(f"  - PDF prepared for: [Manual entry]")
    print()
    
    generate_qr_codes(args.input_file, args.base_url, args.output_dir, args.utm_param_name,
                     create_pdf, pdf_filename, pdf_page_size,
                     create_png, png_size, create_svg,
                     pdf_prepared_for, pdf_title)


if __name__ == '__main__':
    main() 