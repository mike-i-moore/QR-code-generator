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
                    create_png=False, png_size=300):
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
        
        # Create SVG image
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
    
    print(f"SVG QR codes have been generated in the '{svg_dir}' directory.")
    if create_png:
        print(f"Transparent PNG QR codes with text have been generated in the '{png_dir}' directory.")
    
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
    parser = argparse.ArgumentParser(description='Generate QR codes from promo codes in a CSV or TXT file.')
    parser.add_argument('input_file', help='Path to the file containing promo codes (CSV with a "promo_code" column or TXT with one code per line)')
    parser.add_argument('base_url', help='Base URL to which the promo code will be appended')
    parser.add_argument('--output-dir', default='../output', help='Directory where QR code files will be saved')
    parser.add_argument('--utm-param-name', default='promo', help='Name of the UTM parameter (default: promo)')
    
    # Add PDF options
    parser.add_argument('--create-pdf', action='store_true', help='Create a PDF with all QR codes')
    parser.add_argument('--pdf-filename', help='Path to the output PDF file (default: [output_dir]/qr_codes.pdf)')
    parser.add_argument('--pdf-page-size', choices=['letter', 'a4'], default='letter', help='Page size for the PDF (letter or a4)')
    
    # Add PNG options
    parser.add_argument('--create-png', action='store_true', help='Create transparent PNG images of QR codes with text')
    parser.add_argument('--png-size', type=int, default=300, help='Size of PNG images in pixels (default: 300)')
    
    args = parser.parse_args()
    
    generate_qr_codes(args.input_file, args.base_url, args.output_dir, args.utm_param_name,
                     args.create_pdf, args.pdf_filename, args.pdf_page_size,
                     args.create_png, args.png_size)


if __name__ == '__main__':
    main() 