#!/usr/bin/env python3
"""
Transform HelpIndex.txt into clean, browser-friendly HTML.
Generates a grid/card layout with a light theme, organized by brand and category.
"""

import re
import html
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from urllib.parse import quote


class HelpIndexTransformer:
    """Transform XML-like HelpIndex.txt to HTML"""
    
    # Configuration constants
    SECTION_ORDER = ['HELP', 'TUTORIALS', 'VIDEOS', 'DESIGNERS']
    
    # Directory mappings based on listing.txt
    PDF_DIRS = {
        'help pdh': 'Extras/Help/Help',
        'tutorial pdt': 'Extras/Help/Tutorials',
    }
    IMAGE_DIR = 'images'
    
    def __init__(self, help_index_path):
        self.help_index_path = Path(help_index_path)
        self.referenced_files = []
        
    def parse_help_index(self):
        """Parse HelpIndex.txt and organize content by brand/section"""
        if not self.help_index_path.exists():
            raise FileNotFoundError(f"{self.help_index_path} not found")
            
        brands = []  # Use list to preserve order
        brand_dict = {}  # Temp dict for current brand
        brand_order = []  # Track brand order
        current_brand = None
        current_section = None
        
        with open(self.help_index_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # Check for section markers FIRST (e.g., <HELP>, <TUTORIALS>)
                section_match = re.match(r'^<(HELP|TUTORIALS|VIDEOS|DESIGNERS)>$', line)
                if section_match:
                    current_section = section_match.group(1)
                    continue
                    
                # Check for closing section marker
                if re.match(r'^</(HELP|TUTORIALS|VIDEOS|DESIGNERS)>$', line):
                    current_section = None
                    continue
                
                # Check for brand markers (e.g., <QUILTMOTION>, <NOLTING>)
                brand_match = re.match(r'^<([A-Z]+[A-Z0-9]*)>$', line)
                if brand_match:
                    current_brand = brand_match.group(1)
                    if current_brand not in brand_order:
                        brand_order.append(current_brand)
                        brand_dict[current_brand] = defaultdict(list)
                    continue
                    
                # Check for closing brand marker
                if re.match(r'^</[A-Z]+[A-Z0-9]*>$', line):
                    current_brand = None
                    continue
                
                # Parse content items: <number>Title,Resource,Image,Category</number>
                if current_brand and current_section:
                    item_match = re.match(r'<(\d+)>(.*?)</\1>$', line)
                    if item_match:
                        content = item_match.group(2).strip()
                        if content and content.upper() != 'EMPTY':
                            # Split on comma - don't strip to preserve spacing in filenames
                            parts = content.split(',')
                            
                            # Determine format based on number of parts and known categories
                            # Format: Title,Resource,Image,Category (Image and Category optional)
                            if len(parts) >= 2:
                                title = parts[0].strip()
                                
                                # Check if last part is a category
                                has_category = parts[-1].strip() in ['help pdh', 'tutorial pdt']
                                
                                if len(parts) == 2:
                                    # Title,Resource
                                    resource = parts[1].strip()
                                    image = ''
                                    category = ''
                                elif len(parts) == 3:
                                    if has_category:
                                        # Title,Resource,Category
                                        resource = parts[1].strip()
                                        image = ''
                                        category = parts[2].strip()
                                    else:
                                        # Title,Resource,Image
                                        resource = parts[1].strip()
                                        image = parts[2].strip()
                                        category = ''
                                elif len(parts) == 4:
                                    # Title,Resource,Image,Category
                                    resource = parts[1].strip()
                                    image = parts[2].strip()
                                    category = parts[3].strip()
                                else:
                                    # 5+ parts: resource contains comma(s)
                                    # Resource is everything from parts[1] up to (but not including) image and category
                                    if has_category:
                                        # Has category, so parts are: Title, Resource..., Image, Category
                                        resource = ','.join(parts[1:-2])
                                        image = parts[-2].strip()
                                        category = parts[-1].strip()
                                    else:
                                        # No category, so parts are: Title, Resource..., Image
                                        resource = ','.join(parts[1:-1])
                                        image = parts[-1].strip()
                                        category = ''
                                
                                if title and resource:
                                    item = {
                                        'title': title,
                                        'resource': resource,  # PDF filename or URL
                                        'image': image,
                                        'category': category
                                    }
                                    brand_dict[current_brand][current_section].append(item)
        
        # Convert to ordered list
        for brand_name in brand_order:
            brands.append((brand_name, brand_dict[brand_name]))
                        
        return brands
        
    def get_resource_path(self, item):
        """Get the full path to a resource (PDF or URL)"""
        resource = item['resource']
        category = item['category']
        
        # Check if it's a URL
        if resource.startswith('http'):
            return resource
            
        # Get the directory based on category
        pdf_dir = self.PDF_DIRS.get(category, 'Extras/Help/Help')
        full_path = f"{pdf_dir}/{resource}"
        
        self.referenced_files.append(full_path)
        return full_path
        
    def get_image_path(self, item):
        """Get the full path to an image"""
        image = item['image']
        if image:
            return f"{self.IMAGE_DIR}/{image}"
        return None
        
    def generate_html(self, brands):
        """Generate the HTML output with tabbed interface and image display"""
        html_parts = []
        
        # HTML head with modern CSS including tabs
        html_parts.append('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quilt Help Index</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        header {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
            text-align: center;
        }
        
        h1 {
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: #7f8c8d;
            font-size: 1.1em;
        }
        
        /* Tab Navigation */
        .tab-container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }
        
        .tab-nav {
            display: flex;
            flex-wrap: wrap;
            background: #ecf0f1;
            border-bottom: 2px solid #3498db;
        }
        
        .tab-button {
            flex: 1;
            min-width: 120px;
            padding: 15px 20px;
            background: #ecf0f1;
            border: none;
            cursor: pointer;
            font-size: 1em;
            font-weight: 600;
            color: #7f8c8d;
            transition: all 0.3s ease;
            border-bottom: 3px solid transparent;
        }
        
        .tab-button:hover {
            background: #d5dbdb;
            color: #2c3e50;
        }
        
        .tab-button.active {
            background: white;
            color: #3498db;
            border-bottom: 3px solid #3498db;
        }
        
        .tab-content {
            display: none;
            padding: 30px;
            animation: fadeIn 0.3s ease-in;
        }
        
        .tab-content.active {
            display: block;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .brand-title {
            color: #3498db;
            font-size: 2em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #3498db;
        }
        
        .section-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .section-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .section-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        
        .section-card.help { border-left-color: #e74c3c; }
        .section-card.tutorials { border-left-color: #f39c12; }
        .section-card.videos { border-left-color: #9b59b6; }
        .section-card.designers { border-left-color: #1abc9c; }
        
        .section-header {
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .section-header.help { color: #e74c3c; }
        .section-header.tutorials { color: #f39c12; }
        .section-header.videos { color: #9b59b6; }
        .section-header.designers { color: #1abc9c; }
        
        .icon {
            font-size: 1.3em;
        }
        
        .item-list {
            list-style: none;
        }
        
        .item-list li {
            margin-bottom: 15px;
            padding: 12px;
            background: white;
            border-radius: 8px;
            transition: background 0.2s, box-shadow 0.2s;
        }
        
        .item-list li:hover {
            background: #e8f4f8;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        
        .item-content {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .item-image {
            width: 60px;
            height: 60px;
            object-fit: cover;
            border-radius: 8px;
            border: 2px solid #ecf0f1;
            flex-shrink: 0;
        }
        
        .item-link {
            color: #3498db;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 8px;
            flex: 1;
        }
        
        .item-link:hover {
            text-decoration: underline;
        }
        
        .pdf-icon, .video-icon {
            font-weight: bold;
            flex-shrink: 0;
        }
        
        .pdf-icon {
            color: #e74c3c;
        }
        
        .video-icon {
            color: #9b59b6;
        }
        
        footer {
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-top: 30px;
            text-align: center;
            color: #7f8c8d;
        }
        
        @media (max-width: 768px) {
            .tab-button {
                min-width: 100px;
                padding: 12px 15px;
                font-size: 0.9em;
            }
            
            .section-grid {
                grid-template-columns: 1fr;
            }
            
            h1 {
                font-size: 1.8em;
            }
            
            .brand-title {
                font-size: 1.5em;
            }
            
            .item-image {
                width: 50px;
                height: 50px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🧵 Quilt Help Index</h1>
            <p class="subtitle">Your comprehensive guide to quilting machine resources</p>
        </header>
        
        <div class="tab-container">
            <div class="tab-nav">
''')
        
        # Generate tab buttons
        for idx, (brand, sections) in enumerate(brands):
            brand_display = brand.replace('GEN2', ' Gen 2').replace('APQSGEN2', 'APQS Gen 2')
            brand_display = brand_display.title() if brand_display.isupper() else brand_display
            active_class = ' active' if idx == 0 else ''
            brand_id = brand.lower().replace(' ', '-')
            
            html_parts.append(f'''
                <button class="tab-button{active_class}" onclick="switchTab('{brand_id}')">{html.escape(brand_display)}</button>''')
        
        html_parts.append('''
            </div>
            
''')
        
        # Generate tab content for each brand
        for idx, (brand, sections) in enumerate(brands):
            brand_display = brand.replace('GEN2', ' Gen 2').replace('APQSGEN2', 'APQS Gen 2')
            brand_display = brand_display.title() if brand_display.isupper() else brand_display
            active_class = ' active' if idx == 0 else ''
            brand_id = brand.lower().replace(' ', '-')
            
            html_parts.append(f'''
            <div id="{brand_id}" class="tab-content{active_class}">
                <h2 class="brand-title">{html.escape(brand_display)}</h2>
                <div class="section-grid">
''')
            
            # Section icons
            section_icons = {
                'HELP': '📖',
                'TUTORIALS': '🎓',
                'VIDEOS': '🎥',
                'DESIGNERS': '✨'
            }
            
            for section_name in self.SECTION_ORDER:
                items = sections.get(section_name, [])
                if not items:
                    continue
                    
                section_class = section_name.lower()
                icon = section_icons.get(section_name, '📄')
                
                html_parts.append(f'''
                    <div class="section-card {section_class}">
                        <div class="section-header {section_class}">
                            <span class="icon">{icon}</span>
                            <span>{section_name}</span>
                        </div>
                        <ul class="item-list">
''')
                
                for item in items:
                    title = item['title']
                    resource_path = self.get_resource_path(item)
                    image_path = self.get_image_path(item)
                    is_video = resource_path.startswith('http')
                    icon_html = '<span class="video-icon">🎥</span>' if is_video else '<span class="pdf-icon">📄</span>'
                    
                    # Build item HTML with optional image
                    if image_path:
                        html_parts.append(f'''
                            <li>
                                <div class="item-content">
                                    <img src="{quote(image_path)}" alt="{html.escape(title)}" class="item-image" onerror="this.style.display='none'">
                                    <a href="{quote(resource_path)}" class="item-link" target="_blank">
                                        {icon_html}
                                        <span>{html.escape(title)}</span>
                                    </a>
                                </div>
                            </li>
''')
                    else:
                        html_parts.append(f'''
                            <li>
                                <a href="{quote(resource_path)}" class="item-link" target="_blank">
                                    {icon_html}
                                    <span>{html.escape(title)}</span>
                                </a>
                            </li>
''')
                
                html_parts.append('''
                        </ul>
                    </div>
''')
            
            html_parts.append('''
                </div>
            </div>
''')
        
        html_parts.append('''
        </div>
''')
        
        # Footer
        html_parts.append(f'''
        <footer>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Total resources: {len(self.referenced_files)} files referenced</p>
        </footer>
    </div>
    
    <script>
        function switchTab(tabId) {{
            // Hide all tab contents
            const contents = document.querySelectorAll('.tab-content');
            contents.forEach(content => content.classList.remove('active'));
            
            // Deactivate all tab buttons
            const buttons = document.querySelectorAll('.tab-button');
            buttons.forEach(button => button.classList.remove('active'));
            
            // Show selected tab content
            const selectedContent = document.getElementById(tabId);
            if (selectedContent) {{
                selectedContent.classList.add('active');
            }}
            
            // Activate selected tab button
            const selectedButton = Array.from(buttons).find(btn => 
                btn.textContent.toLowerCase().replace(/\\s+/g, '-') === tabId ||
                btn.onclick.toString().includes(tabId)
            );
            if (selectedButton) {{
                selectedButton.classList.add('active');
            }}
        }}
    </script>
</body>
</html>
''')
        
        return ''.join(html_parts)
        
    def generate_checklist(self):
        """Generate a text checklist of referenced PDF files"""
        checklist = []
        checklist.append("# Referenced Files Checklist\n")
        checklist.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        checklist.append(f"Total Files: {len(self.referenced_files)}\n\n")
        
        unique_files = sorted(set(self.referenced_files))
        for i, pdf_path in enumerate(unique_files, 1):
            exists = Path(pdf_path).exists()
            status = "✓" if exists else "✗"
            checklist.append(f"{status} {i}. {pdf_path}\n")
            
        return ''.join(checklist)
        
    def transform(self, output_html='index.html', output_checklist='file-checklist.txt'):
        """Main transformation process"""
        print("Parsing HelpIndex.txt...")
        brands = self.parse_help_index()
        
        print("Generating HTML...")
        html_content = self.generate_html(brands)
        
        print(f"Writing HTML to {output_html}...")
        with open(output_html, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print("Generating file checklist...")
        checklist = self.generate_checklist()
        
        print(f"Writing checklist to {output_checklist}...")
        with open(output_checklist, 'w', encoding='utf-8') as f:
            f.write(checklist)
            
        print(f"\n✓ Transformation complete!")
        print(f"  - HTML output: {output_html}")
        print(f"  - File checklist: {output_checklist}")
        print(f"  - Referenced files: {len(self.referenced_files)}")


def main():
    """Main entry point"""
    # Use paths relative to script location
    base_dir = Path(__file__).parent
    
    transformer = HelpIndexTransformer(
        help_index_path=base_dir / 'HelpIndex.txt'
    )
    
    transformer.transform(
        output_html=base_dir / 'index.html',
        output_checklist=base_dir / 'file-checklist.txt'
    )


if __name__ == '__main__':
    main()
