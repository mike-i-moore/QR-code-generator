# QR Code Generator for Promotional Codes


This tool generates QR code files from promotional codes in a CSV file. Each QR code links to a website where the promo code is included as a UTM parameter. The tool supports multiple output formats:
- SVG vector files for high-quality printing and scaling
- PNG raster images for digital use and easy sharing
- PDF compilation with one QR code per page for easy printing

## Features

- Generates QR codes from promo codes in a CSV file
- Multiple output formats: SVG, PNG, and PDF
- Organized file structure with separate folders for each format
- Customizable PNG size and PDF page size
- Customizable base URL and UTM parameter name
- Command-line and interactive interfaces
- Batch processing capability

## Requirements

- Python 3.7+
- Dependencies listed in `requirements.txt`

## Installation

### Option 1: Install in your current Python environment

1. Clone or download this repository
2. Navigate to the project directory
3. Install the required packages:

```bash
pip install -r requirements.txt
```

### Option 2: Use the dedicated virtual environment (recommended)

To avoid dependency conflicts with other projects, you can use the included virtual environment:

```bash
# Activate the virtual environment
# On macOS/Linux:
source qr_env/bin/activate

# On Windows:
qr_env\Scripts\activate

# Run the QR code generator (see Usage section below)
# When finished, deactivate the virtual environment:
deactivate
```

## Usage

### Preparing Your CSV File

Create a CSV file with a column named `promo_code`. Example:

```
promo_code
SUMMER10
WELCOME15
FALL20
HOLIDAY25
SPRING5
```

A sample CSV file is provided in the `sample_data` directory.

### Command-Line Usage

Run the QR code generator directly from the command line:

```bash
cd src
python qr_generator.py [CSV_FILE] [BASE_URL] [--output-dir OUTPUT_DIR] [--utm-param-name UTM_PARAM_NAME] [--create-pdf] [--pdf-filename PDF_FILE] [--pdf-page-size {letter,a4}] [--create-png] [--png-size SIZE]
```

Example:

```bash
# Generate SVG QR codes only
python qr_generator.py ../sample_data/promo_codes.csv https://example.com/promo --output-dir ../output --utm-param-name promo

# Generate QR codes in SVG and PNG formats
python qr_generator.py ../sample_data/promo_codes.csv https://example.com/promo --create-png --png-size 500

# Generate QR codes in all formats (SVG, PNG, and PDF)
python qr_generator.py ../sample_data/promo_codes.csv https://example.com/promo --create-png --create-pdf --pdf-page-size a4
```

### Interactive Usage

For a more user-friendly experience, use the batch generator:

```bash
cd src
python batch_generator.py
```

Follow the prompts to enter:
- Path to the CSV file
- Base URL
- Output directory (optional)
- UTM parameter name (optional)

### PDF Compilation

You can also compile existing SVG QR codes into a PDF directly:

```bash
cd src
python pdf_compiler.py [INPUT_DIR] [OUTPUT_PDF] [--page-size {letter,a4}] [--no-code-text]
```

Example:

```bash
python pdf_compiler.py ../output ../output/qr_codes.pdf --page-size letter
```

## Output

The QR code generator produces the following outputs, organized in separate directories:

### Output Directory Structure
```
output/
├── svg/               # SVG files directory
│   ├── SUMMER10.svg
│   ├── WELCOME15.svg
│   └── ...
├── png/               # PNG files directory (if enabled)
│   ├── SUMMER10.png
│   ├── WELCOME15.png
│   └── ...
└── qr_codes.pdf       # PDF file (if enabled)
```

### SVG Files (Default)
SVG files are generated in the `svg` subdirectory within the specified output directory. Each file is named after the corresponding promo code (e.g., `svg/SUMMER10.svg`). SVG files are vector-based, making them ideal for high-quality printing and scaling to any size without quality loss.

### PNG Files (Optional)
If PNG generation is enabled, PNG files will be generated in the `png` subdirectory within the specified output directory. Each file is named after the corresponding promo code (e.g., `png/SUMMER10.png`). PNG files are raster images, making them ideal for digital use, websites, and easy sharing.

The size of PNG images can be customized using the `--png-size` option (default is 300 pixels).

### PDF File (Optional)
If PDF generation is enabled, a PDF file will be created in the root of the output directory. The PDF includes:
- A title page with the total number of QR codes
- One QR code per page with the promo code text displayed below each QR code
- Properly sized and centered QR codes for optimal scanning

The QR codes in all formats link to URLs in the format:
```
[BASE_URL]?[UTM_PARAM_NAME]=[PROMO_CODE]
```

Example:
```
https://example.com/promo?promo=SUMMER10
```

## Troubleshooting

### Dependency Conflicts

If you encounter dependency conflicts when installing the required packages, we recommend using the dedicated virtual environment (Option 2 in the Installation section). This creates an isolated environment for the QR Code Generator, preventing conflicts with other Python packages.

#### Numpy/Pandas Compatibility Issues

If you encounter errors related to numpy/pandas compatibility (e.g., `numpy.dtype size changed, may indicate binary incompatibility`), you can fix it by:

1. Ensuring you have the correct version of numpy installed:
   ```bash
   pip uninstall -y numpy pandas
   pip install numpy==1.23.5
   pip install pandas==2.0.3
   ```

2. Then reinstall the other dependencies:
   ```bash
   pip install qrcode==7.4.2 Pillow==10.0.0 svglib==1.5.1 reportlab==3.6.13
   ```

This ordering ensures that numpy and pandas are compatible with each other.

## License

This project is open-source and available under the MIT License.

## Support

For issues or questions, please open an issue in the repository. 