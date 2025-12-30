# Quilt Help Index

A tool to transform pseudo-markup help content into clean, browser-friendly HTML with a modern grid/card layout.

## Overview

This project transforms the `HelpIndex.txt` file into a beautiful, organized HTML page featuring:
- **Grid/card layout** with a light, modern theme
- **Organized content** by brand and category
- **Sections** for HELP, TUTORIALS, VIDEOS, and DESIGNERS
- **Automatic linking** to PDF resources in the Extras folder
- **Skip EMPTY entries** automatically
- **File checklist** generation for referenced PDFs

## Quick Start

1. **Run the transformation:**
   ```bash
   python3 transform.py
   ```

2. **View the output:**
   - Open `index.html` in your browser
   - Check `file-checklist.txt` for a list of all referenced files

## File Structure

```
.
├── HelpIndex.txt          # Input: Pseudo-markup content organized by brand/category
├── newlisting.txt         # Input: Image and PDF mappings
├── images/                # Directory containing product images
├── Extras/                # Directory containing PDF resources
├── transform.py           # Transformation script
├── index.html             # Output: Generated HTML page
└── file-checklist.txt     # Output: Checklist of referenced PDF files
```

## Input File Formats

### HelpIndex.txt

Organized using markdown-style headers:

```
## BRAND: Janome
### CATEGORY: Memory Craft Series
#### HELP
- MC6700P: Getting Started Guide
- MC9900: Threading Instructions
#### TUTORIALS
- MC6700P: Basic Embroidery Tutorial
#### VIDEOS
- EMPTY
#### DESIGNERS
- Designer V5: Installing Fonts
```

### newlisting.txt

Maps images and PDFs to descriptions:

```
# Image Mappings
images/janome-mc6700p.jpg: Janome Memory Craft MC6700P

# PDF References in Extras folder
Extras/janome-mc6700p-getting-started.pdf: MC6700P Getting Started Guide
```

## Features

### Modern UI Design
- Clean, responsive grid layout
- Light gradient background
- Color-coded sections:
  - 📖 HELP (red)
  - 🎓 TUTORIALS (orange)
  - 🎥 VIDEOS (purple)
  - ✨ DESIGNERS (teal)
- Hover effects and smooth transitions
- Mobile-responsive design

### Smart Content Processing
- Automatically skips EMPTY entries
- Fuzzy matching for PDF links
- Validates file references
- Generates comprehensive checklist

### HTML5 Structure
- Semantic HTML5 elements
- Accessible markup
- Modern CSS Grid layout
- No external dependencies

## Output

### index.html
A complete, standalone HTML file with embedded CSS featuring:
- Header with title and subtitle
- Brand sections with category subdivisions
- Grid layout of resource cards
- Footer with generation timestamp and file count

### file-checklist.txt
A text file listing all referenced PDFs with checkmarks:
```
# Referenced Files Checklist
Generated: 2025-12-30 20:16:12
Total Files: 20

✓ 1. Extras/bernina-770qe-bsr.pdf
✓ 2. Extras/bernina-770qe-quickstart.pdf
...
```

## Customization

The script can be modified to:
- Change the color scheme in the CSS section
- Adjust the grid layout (currently `minmax(300px, 1fr)`)
- Add additional sections beyond HELP, TUTORIALS, VIDEOS, DESIGNERS
- Customize the matching algorithm for PDFs

## Requirements

- Python 3.6+
- No external dependencies required

## License

This project is provided as-is for managing quilting machine help resources.