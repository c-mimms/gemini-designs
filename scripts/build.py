import os
import shutil
import markdown
import json
from datetime import datetime

# Configuration
PROJECTS_DIR = 'projects'
DIST_DIR = 'build_out'
TEMPLATES_DIR = 'templates'

def build():
    print(f"Starting build in {DIST_DIR}...")
    
    # Ensure output directory exists (do not rmtree to avoid macOS transient locks)
    os.makedirs(DIST_DIR, exist_ok=True)

    projects = []

    # Scan projects
    for item in sorted(os.listdir(PROJECTS_DIR)):
        item_path = os.path.join(PROJECTS_DIR, item)
        
        if os.path.isdir(item_path):
            # Folder project (HTML/JS/CSS)
            print(f"Processing folder project: {item}")
            shutil.copytree(item_path, os.path.join(DIST_DIR, item))
            
            # Simple metadata extraction
            projects.append({
                'id': item,
                'title': item.replace('-', ' ').title(),
                'url': f'./{item}/',
                'description': 'A full web prototype.',
                'tag': 'Web App'
            })
            
        elif item.endswith('.md'):
            # Markdown project
            name = item[:-3]
            print(f"Processing Markdown project: {name}")
            
            with open(item_path, 'r') as f:
                md_content = f.read()
            
            # Extract title from the first # H1
            title = name.replace('-', ' ').title()
            for line in md_content.split('\n'):
                if line.startswith('# '):
                    title = line[2:].strip()
                    break

            html_content = markdown.markdown(md_content, extensions=['extra', 'smarty'])
            
            # Use design template
            template_path = os.path.join(TEMPLATES_DIR, 'design_template.html')
            if not os.path.exists(template_path):
                # Fallback if template missing
                full_html = f"<html><body>{html_content}</body></html>"
            else:
                with open(template_path, 'r') as f:
                    template_text = f.read()
                full_html = template_text.replace('{{content}}', html_content).replace('{{title}}', title)
            
            with open(os.path.join(DIST_DIR, f'{name}.html'), 'w') as f:
                f.write(full_html)
                
            projects.append({
                'id': name,
                'title': title,
                'url': f'./{name}.html',
                'description': 'Markdown-based design document.',
                'tag': 'Design Doc'
            })

    # Build Master Index
    print("Building master index...")
    master_template_path = os.path.join(TEMPLATES_DIR, 'index.html')
    with open(master_template_path, 'r') as f:
        master_template = f.read()
    
    # Generate project cards HTML
    cards_html = ""
    for p in projects:
        cards_html += f"""
        <a href="{p['url']}" class="card">
            <h2>{p['title']} <span class="arrow">→</span></h2>
            <p>{p['description']}</p>
            <span class="tag">{p['tag']}</span>
        </a>
        """
    
    # Simple injection logic (or use jinja2 if available, but let's keep it dependency-light)
    # We look for the grid div content and replace it
    # For now, let's assume we use a placeholder in the template
    if '<!-- PROJECTS_HOLDER -->' in master_template:
        final_html = master_template.replace('<!-- PROJECTS_HOLDER -->', cards_html)
    else:
        # Fallback: find the <div class="grid"> and inject inside
        before, after = master_template.split('<div class="grid">', 1)
        grid_tag, rest = after.split('</div>', 1)
        final_html = before + '<div class="grid">' + cards_html + '</div>' + rest

    with open(os.path.join(DIST_DIR, 'index.html'), 'w') as f:
        f.write(final_html)
    
    print("Build complete!")

if __name__ == "__main__":
    build()
