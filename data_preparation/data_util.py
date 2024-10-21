import os
import markdown
from bs4 import BeautifulSoup

from pathlib import Path
import ray

def convert_folder_to_sections(folder_path:str, patterns: list[str]=[ '*.md'] ):
    DOCS_DIR = Path(folder_path)
    # Collect matched files  
    matched_files = []  
    for pattern in patterns:  
        matched_files.extend(DOCS_DIR.rglob(pattern))  
    ds = ray.data.from_items([{"path": str(path)} for path in matched_files if not path.is_dir()])
    sections = ds.flat_map(parse_sections)
    return sections

def parse_sections(input:dict):
    file_path = str(input['path'])
    if file_path.endswith('.md'):
        return parse_markdown_sections(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path}")

def parse_markdown_sections(file_path:str):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        md_content = file.read()
    
    html = markdown.markdown(md_content)
    soup = BeautifulSoup(html, 'html.parser')
    
    sections = []
    
    def extract_sections(element, parent_headings):
        if element and element.name and element.name.startswith('h') and element.name[1].isdigit():
            heading_level = int(element.name[1])
            heading_text = element.get_text()
            current_headings = parent_headings[:heading_level-1] + [heading_text]
            section_text = ""
            for sibling in element.find_next_siblings():
                if sibling.name and sibling.name.startswith('h') and sibling.name[1].isdigit() and int(sibling.name[1]) <= heading_level:
                    break
                section_text += sibling.get_text() + "\n"
            sections.append({
                'path': file_path,
                'text': section_text.strip(),
                'heading': heading_text,
                'parent_headings': parent_headings,
                'children_headings': [sibling.get_text() for sibling in element.find_next_siblings() if sibling.name and sibling.name.startswith('h') and sibling.name[1].isdigit() and int(sibling.name[1]) > heading_level]
            })
            extract_sections(element.find_next_sibling(), current_headings)
        elif element:
            extract_sections(element.find_next_sibling(), parent_headings)
    
    extract_sections(soup.find('h1'), [])
    
    return sections