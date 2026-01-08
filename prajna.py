#!/usr/bin/env python3
"""
Prajna - A Jekyll-like static site generator for rendering markdown posts as book pages
"""

import os
import re
import yaml
import markdown
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom


class PrajnaRenderer:
    """Main class for rendering Jekyll-format markdown posts to HTML"""
    
    def __init__(self, config_path: str = "_config.yml"):
        """Initialize the renderer with configuration"""
        self.root_dir = Path.cwd()
        self.config = self._load_config(config_path)
        self.posts_dir = self.root_dir / self.config.get('book', {}).get('posts_dir', '_posts')
        self.layouts_dir = self.root_dir / self.config.get('book', {}).get('template_dir', '_layouts')
        self.output_dir = self.root_dir / self.config.get('book', {}).get('output_dir', '_site')
        
        # Initialize markdown parser with common extensions
        self.md = markdown.Markdown(extensions=[
            'extra',
            'codehilite',
            'toc',
            'fenced_code',
            'tables'
        ])
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        config_file = self.root_dir / config_path
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def _parse_front_matter(self, content: str) -> Tuple[Dict, str]:
        """Parse YAML front matter from markdown content"""
        # Jekyll front matter is between --- markers
        front_matter_pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
        match = re.match(front_matter_pattern, content, re.DOTALL)
        
        if match:
            try:
                front_matter = yaml.safe_load(match.group(1)) or {}
                markdown_content = match.group(2)
                return front_matter, markdown_content
            except yaml.YAMLError as e:
                print(f"Error parsing front matter: {e}")
                return {}, content
        
        return {}, content
    
    def _load_template(self, layout_name: str = 'post') -> str:
        """Load HTML template"""
        template_path = self.layouts_dir / f"{layout_name}.html"
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        # Default template if none found
        return """<!DOCTYPE html>
<html>
<head><title>{{ title }}</title></head>
<body>
<h1>{{ title }}</h1>
{{ content }}
</body>
</html>"""
    
    def _render_template(self, template: str, context: Dict) -> str:
        """Simple template rendering (replaces {{ variable }} with values)"""
        result = template
        
        for key, value in context.items():
            placeholder = f"{{{{ {key} }}}}"
            result = result.replace(placeholder, str(value))
        
        # Handle conditional blocks {% if var %}...{% endif %}
        # Simple implementation for date and author
        if_pattern = r'\{%\s*if\s+(\w+)\s*%\}(.*?)\{%\s*endif\s*%\}'
        
        def replace_if(match):
            var_name = match.group(1)
            content = match.group(2)
            if var_name in context and context[var_name]:
                return content
            return ''
        
        result = re.sub(if_pattern, replace_if, result, flags=re.DOTALL)
        
        return result
    
    def _extract_date_from_filename(self, filename: str) -> Optional[str]:
        """Extract date from Jekyll post filename (YYYY-MM-DD-title.md)"""
        date_pattern = r'^(\d{4}-\d{2}-\d{2})-'
        match = re.match(date_pattern, filename)
        if match:
            date_str = match.group(1)
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                return date_obj.strftime('%B %d, %Y')
            except ValueError:
                pass
        return None
    
    def _get_output_filename(self, post_file: Path, front_matter: Dict) -> str:
        """Generate output filename for the rendered HTML"""
        # Remove date prefix and .md extension
        filename = post_file.stem
        date_pattern = r'^\d{4}-\d{2}-\d{2}-'
        filename = re.sub(date_pattern, '', filename)
        return f"{filename}.html"
    
    def render_post(self, post_file: Path) -> Optional[Dict]:
        """Render a single post file to HTML and return post metadata"""
        try:
            # Read the markdown file
            with open(post_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse front matter and content
            front_matter, markdown_content = self._parse_front_matter(content)
            
            # Convert markdown to HTML
            html_content = self.md.convert(markdown_content)
            
            # Reset markdown parser for next use
            self.md.reset()
            
            # Extract date from filename if not in front matter
            date = front_matter.get('date')
            if not date:
                date = self._extract_date_from_filename(post_file.name)
            
            # Prepare context for template
            context = {
                'title': front_matter.get('title', post_file.stem),
                'content': html_content,
                'date': date or '',
                'author': front_matter.get('author', ''),
                'site_title': self.config.get('title', 'Prajna'),
                'description': front_matter.get('description', ''),
            }
            
            # Load and render template
            layout = front_matter.get('layout', 'post')
            template = self._load_template(layout)
            rendered_html = self._render_template(template, context)
            
            # Create output directory if it doesn't exist
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Write output file
            output_filename = self._get_output_filename(post_file, front_matter)
            output_path = self.output_dir / output_filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(rendered_html)
            
            print(f"✓ Rendered: {post_file.name} -> {output_filename}")
            
            # Return metadata for index generation
            return {
                'title': context['title'],
                'date': context['date'],
                'author': context['author'],
                'description': context['description'],
                'filename': output_filename
            }
            
        except Exception as e:
            print(f"✗ Error rendering {post_file.name}: {e}")
            return None
    
    def render_all_posts(self) -> int:
        """Render all posts in the _posts directory"""
        if not self.posts_dir.exists():
            print(f"Posts directory not found: {self.posts_dir}")
            return 0
        
        # Find all markdown files
        post_files = sorted(self.posts_dir.glob('*.md'))
        post_files.extend(sorted(self.posts_dir.glob('*.markdown')))
        
        if not post_files:
            print(f"No markdown files found in {self.posts_dir}")
            return 0
        
        print(f"\nRendering {len(post_files)} post(s)...\n")
        
        posts_info = []
        success_count = 0
        for post_file in post_files:
            post_metadata = self.render_post(post_file)
            if post_metadata:
                success_count += 1
                posts_info.append(post_metadata)
        
        # Generate index page
        if posts_info:
            self._generate_index(posts_info)
            self._generate_sitemap(posts_info)
        
        print(f"\n{success_count}/{len(post_files)} posts rendered successfully")
        print(f"Output directory: {self.output_dir}")
        
        return success_count
    
    def _generate_index(self, posts_info: List[Dict]):
        """Generate an index page listing all posts"""
        try:
            # Build posts list HTML
            posts_html = []
            for post in posts_info:
                post_html = f'''            <li class="post-item">
                <a href="{post['filename']}" class="post-link">
                    <h2 class="post-title">{post['title']}</h2>
                    <div class="post-meta">'''
                
                if post['date']:
                    post_html += f"\n                        {post['date']}"
                if post['author']:
                    post_html += f" by {post['author']}"
                
                post_html += "\n                    </div>"
                
                if post['description']:
                    post_html += f'''
                    <p class="post-description">{post['description']}</p>'''
                
                post_html += '''
                </a>
            </li>'''
                posts_html.append(post_html)
            
            # Load index template
            template = self._load_template('index')
            
            # Prepare context
            context = {
                'site_title': self.config.get('title', 'Prajna'),
                'site_description': self.config.get('description', 'A book rendered from Jekyll-format markdown'),
                'posts_list': '\n'.join(posts_html)
            }
            
            # Render template
            rendered_html = self._render_template(template, context)
            
            # Write index file
            index_path = self.output_dir / 'index.html'
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(rendered_html)
            
            print(f"✓ Generated: index.html")
            
        except Exception as e:
            print(f"✗ Error generating index: {e}")
    
    def _generate_sitemap(self, posts_info: List[Dict]):
        """Generate sitemap.xml for all pages"""
        try:
            # Get base URL from config
            base_url = self.config.get('url', '').rstrip('/')
            baseurl = self.config.get('baseurl', '').rstrip('/')
            
            # If no URL is configured, use a placeholder
            if not base_url:
                base_url = 'https://example.com'
            
            full_base_url = base_url + baseurl
            
            # Create root element
            urlset = Element('urlset')
            urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
            
            # Add index page
            url = SubElement(urlset, 'url')
            loc = SubElement(url, 'loc')
            loc.text = f"{full_base_url}/"
            lastmod = SubElement(url, 'lastmod')
            lastmod.text = datetime.now().strftime('%Y-%m-%d')
            changefreq = SubElement(url, 'changefreq')
            changefreq.text = 'weekly'
            priority = SubElement(url, 'priority')
            priority.text = '1.0'
            
            # Add all post pages
            for post in posts_info:
                url = SubElement(urlset, 'url')
                loc = SubElement(url, 'loc')
                loc.text = f"{full_base_url}/{post['filename']}"
                lastmod = SubElement(url, 'lastmod')
                # Use post date if available, otherwise use current date
                if post.get('date'):
                    try:
                        # Try to parse the date string
                        date_obj = datetime.strptime(post['date'], '%B %d, %Y')
                        lastmod.text = date_obj.strftime('%Y-%m-%d')
                    except (ValueError, TypeError):
                        lastmod.text = datetime.now().strftime('%Y-%m-%d')
                else:
                    lastmod.text = datetime.now().strftime('%Y-%m-%d')
                changefreq = SubElement(url, 'changefreq')
                changefreq.text = 'monthly'
                priority = SubElement(url, 'priority')
                priority.text = '0.8'
            
            # Pretty print the XML
            xml_string = minidom.parseString(
                tostring(urlset, encoding='utf-8')
            ).toprettyxml(indent='  ', encoding='utf-8')
            
            # Write sitemap file
            sitemap_path = self.output_dir / 'sitemap.xml'
            with open(sitemap_path, 'wb') as f:
                f.write(xml_string)
            
            print(f"✓ Generated: sitemap.xml")
            
        except Exception as e:
            print(f"✗ Error generating sitemap: {e}")


def main():
    """Main entry point"""
    print("=" * 50)
    print("Prajna - Jekyll-format Markdown to HTML Renderer")
    print("=" * 50)
    
    renderer = PrajnaRenderer()
    renderer.render_all_posts()


if __name__ == '__main__':
    main()
