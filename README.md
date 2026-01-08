# Prajna

A Jekyll-like static site generator that renders markdown posts as beautifully formatted book pages.

## Overview

Prajna takes markdown files in Jekyll format from the `_posts` folder and converts them into HTML pages with a book-like appearance. Perfect for writing books, documentation, or any long-form content.

## Features

- ✨ **Jekyll-compatible format** - Uses standard Jekyll front matter (YAML)
- 📚 **Book-like layout** - Clean, readable design optimized for long-form content
- 🎨 **Beautiful typography** - Serif fonts and proper spacing for comfortable reading
- 📝 **Full markdown support** - Headers, lists, code blocks, tables, and more
- 🔧 **Simple configuration** - Easy to customize via `_config.yml`
- 🚀 **Fast rendering** - Quickly generates HTML from all your posts
- 🗺️ **SEO-friendly** - Automatically generates sitemap.xml for search engines

## Installation

1. Clone the repository:
```bash
git clone https://github.com/rockerritesh/prajna.git
cd prajna
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Quick Start

1. Add markdown files to the `_posts` folder following Jekyll naming convention:
   ```
   _posts/YYYY-MM-DD-title.md
   ```

2. Run the renderer:
   ```bash
   python3 prajna.py
   ```

3. View the generated HTML files in the `docs` folder

The script will generate:
- Individual HTML pages for each post
- An `index.html` page listing all posts
- A `sitemap.xml` file for search engine optimization

### Writing Posts

Create markdown files in the `_posts` folder with Jekyll front matter:

```markdown
---
layout: post
title: "Your Post Title"
date: 2024-01-01
author: "Your Name"
description: "Optional description"
---

# Your Content Here

Write your content using standard markdown syntax...
```

#### Front Matter Fields

- `layout`: Template to use (default: `post`)
- `title`: Post title (required)
- `date`: Publication date (optional, can be extracted from filename)
- `author`: Author name (optional)
- `description`: Short description (optional)

### Markdown Support

Prajna supports all standard markdown features:

- Headers (H1-H6)
- **Bold** and *italic* text
- Lists (ordered and unordered)
- Links and images
- Code blocks with syntax highlighting
- Tables
- Blockquotes
- Horizontal rules

### Configuration

Edit `_config.yml` to customize settings:

```yaml
# Site settings
title: Prajna
description: A book rendered from Jekyll-format markdown
url: https://yourdomain.com  # Important for sitemap.xml generation
baseurl: ""                   # Optional base URL path

# Build settings
markdown: kramdown

# Book settings
book:
  output_dir: docs
  posts_dir: _posts
  template_dir: _layouts
```

**Note:** Set the `url` field in `_config.yml` for proper sitemap.xml generation. If not set, a placeholder URL will be used.

### Custom Templates

Create custom HTML templates in the `_layouts` folder. Templates use simple placeholder syntax:

- `{{ title }}` - Post title
- `{{ content }}` - Rendered markdown content
- `{{ date }}` - Publication date
- `{{ author }}` - Author name
- `{% if variable %}...{% endif %}` - Conditional blocks

## Project Structure

```
prajna/
├── _config.yml          # Configuration file
├── _posts/              # Your markdown posts
│   ├── 2024-01-01-chapter-1.md
│   └── 2024-01-02-chapter-2.md
├── _layouts/            # HTML templates
│   └── post.html
├── docs/                # Generated HTML files (output)
├── prajna.py            # Main renderer script
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Examples

The repository includes three sample posts demonstrating various features:

1. **Chapter 1: The Beginning** - Introduction to Prajna
2. **Chapter 2: Understanding Markdown** - Markdown syntax guide
3. **Chapter 3: The Future** - Use cases and best practices

Run `python3 prajna.py` to see them rendered!

## GitHub Actions

The repository includes a GitHub Actions workflow that automatically generates HTML from your markdown posts whenever you push to the main/master branch. The workflow:

1. Sets up Python environment
2. Installs dependencies from `requirements.txt`
3. Runs `prajna.py` to generate HTML files
4. Commits and pushes the generated files to the `docs` folder

The workflow is triggered on:
- Push to main/master branches
- Pull requests to main/master branches
- Manual workflow dispatch

## Requirements

- Python 3.7+
- markdown>=3.4.0
- PyYAML>=6.0

## License

See LICENSE file for details.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## Acknowledgments

Inspired by Jekyll, the popular static site generator.
