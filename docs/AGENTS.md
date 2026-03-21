# Wind Nowcasting - Project Documentation for AI Agents

## Project Overview

This is a **Jekyll-based static website** for the **Wind Nowcasting** project - an AI-powered weather forecasting research initiative conducted by a team from the Australian National University (ANU) in collaboration with the Australian Bureau of Meteorology (BOM).

The website serves as the project's public documentation hub, featuring:
- Project overview and goals
- Interactive project roadmap with timeline
- Team member profiles
- Blog for research updates
- Modern dark-themed UI with WebGL2 animated backgrounds

## Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Static Site Generator | Jekyll | ~> 4.4.1 |
| Theme | Minima | ~> 2.5 |
| CSS Framework | Bulma | (bundled) |
| Icons | Font Awesome | 7.0.1 (CDN) |
| Animation | Anime.js | (CDN) |
| Graphics | WebGL2 + Custom Perlin Noise | - |
| Language | Ruby | (via Bundler) |

### External Dependencies (CDN)
- `https://cdnjs.cloudflare.com/ajax/libs/font-awesome/7.0.1/css/all.min.css`
- `https://cdn.jsdelivr.net/npm/animejs/dist/bundles/anime.umd.min.js`

## Project Structure

```
.
├── _config.yml              # Jekyll configuration
├── Gemfile                  # Ruby dependencies
├── Gemfile.lock             # Locked dependency versions
├── .gitignore               # Git ignore rules
│
├── _layouts/                # HTML page layouts
│   ├── base.html            # Base layout with header/footer
│   ├── plain.html           # Plain layout (same as base)
│   └── post.html            # Blog post layout
│
├── _includes/               # Reusable HTML components
│   ├── header.html          # Site navigation header
│   ├── footer.html          # Site footer with links
│   ├── hero.html            # Full-height hero section
│   ├── hero2.html           # Medium hero section
│   ├── section-header.html  # Section title component
│   ├── overview-card.html   # Project overview card
│   ├── member-card.html     # Team member card
│   ├── goal-card.html       # Project goal card
│   └── milestone-item.html  # Roadmap milestone item
│
├── _data/                   # YAML data files
│   ├── nav.yml              # Navigation menu items
│   ├── members.yml          # Team member information
│   ├── overview.yml         # Project overview cards data
│   └── roadmap.yml          # Project roadmap/timeline data
│
├── _posts/                  # Blog posts (Markdown)
│   └── (empty - add posts here)
│
├── assets/                  # Static assets
│   ├── css/
│   │   ├── bulma.css        # Bulma CSS framework
│   │   └── style.css        # Custom styles (~1900 lines)
│   └── js/
│       ├── perlin.js        # Perlin noise library
│       ├── background.js    # WebGL2 background animation
│       └── script.js        # (empty - reserved)
│
├── index.html               # Homepage
├── about.html               # About/Team page
├── blog.html                # Blog listing page
└── 404.html                 # 404 error page
```

## Build and Development Commands

### Prerequisites
- Ruby installed (2.5 or higher recommended)
- Bundler gem installed (`gem install bundler`)

### Setup
```bash
# Install dependencies
bundle install
```

### Development
```bash
# Start local development server
bundle exec jekyll serve

# Start with live reload (auto-refresh on changes)
bundle exec jekyll serve --livereload

# Server will be available at http://localhost:4000/BOM-Team/
```

### Production Build
```bash
# Build site for production
bundle exec jekyll build

# Output will be in _site/ directory
```

### Configuration Notes
- `baseurl` is set to `/BOM-Team` for GitHub Pages deployment
- URL structure: `http://localhost:4000/BOM-Team/`
- Changing `_config.yml` requires server restart

## Data Files Reference

### _data/nav.yml
Navigation menu structure. Each item has:
- `title`: Display name
- `url`: Relative URL path

### _data/members.yml
Team member profiles. Fields:
- `name`: Full name
- `role`: Role (Stakeholder/Student/Tutor)
- `id`: University ID or identifier
- `email`: Email address
- `github`: GitHub username
- `avatar`: Initial letter for avatar
- `color`: Avatar color class (primary/blue/purple/green/orange/pink/teal)

### _data/overview.yml
Project overview cards displayed on homepage. Fields:
- `icon_class`: CSS class for icon styling
- `icon`: Font Awesome icon class
- `title`: Card title
- `description`: Card description
- `stat_icon`: Icon for stat badge
- `stat_text`: Stat badge text

### _data/roadmap.yml
Project roadmap timeline. Fields:
- `badge`: Semester badge text (e.g., "S1")
- `title`: Semester title
- `subtitle`: Semester subtitle
- `badge_class`: Optional CSS class for styling
- `line_class`: Optional CSS class for timeline line
- `milestones`: Array of milestone objects

## Adding Blog Posts

Create new Markdown files in `_posts/` with the naming convention:
```
YYYY-MM-DD-title-here.md
```

Front matter template:
```yaml
---
layout: post
title: "Your Post Title"
date: YYYY-MM-DD HH:MM:SS +1100
categories: update
---

Your content here...
```

## Code Style Guidelines

### HTML/Liquid Templates
- Use 4-space indentation
- Use double quotes for attributes
- Use `{{ site.baseurl }}` for internal links
- Use `relative_url` filter for URLs

### CSS
- Custom properties (CSS variables) defined in `:root`
- BEM-like naming convention used
- Color scheme based on CSS variables:
  - `--primary-blue: #007bff`
  - `--secondary-purple: #4f3fff`
  - `--accent-purple: #9b59b6`
  - `--accent-green: #2ecc71`

### File Organization
- Layouts in `_layouts/`
- Reusable components in `_includes/`
- Data in `_data/`
- Static assets in `assets/`

## Key Layouts

### base.html / plain.html
- Includes header and footer
- Loads all required CSS and JS
- Sets up WebGL2 background canvas

### post.html
- Extends base layout
- Adds article styling
- Includes back-to-blog link

## Testing

### Local Testing
1. Run `bundle exec jekyll serve`
2. Visit `http://localhost:4000/BOM-Team/`
3. Test on different screen sizes (responsive design)

### Build Verification
```bash
# Verify build completes without errors
bundle exec jekyll build --strict_front_matter
```

## Deployment

### GitHub Pages
This site is configured for GitHub Pages deployment:
- Repository: `joeyllm/BOM-Team`
- `baseurl: "/BOM-Team"` is set in `_config.yml`

### Deployment Steps
1. Push changes to GitHub repository
2. GitHub Pages will automatically build and deploy
3. Site will be available at: `https://joeyllm.github.io/BOM-Team/`

## Security Considerations

- No sensitive data should be stored in this repository
- All external CDN links use HTTPS
- No forms or user input handling
- Static site - no server-side processing

## Troubleshooting

### Common Issues

**Jekyll serve fails:**
- Ensure Ruby and Bundler are installed
- Run `bundle install` to update dependencies

**Changes not reflecting:**
- Restart the server after modifying `_config.yml`
- Clear browser cache
- Check `_site/` directory is being updated

**CSS/JS not loading:**
- Verify `baseurl` is correctly set
- Check file paths include `{{ site.baseurl }}`

## External Resources

- **Jekyll Docs**: https://jekyllrb.com/docs/
- **Liquid Syntax**: https://shopify.github.io/liquid/
- **Bulma CSS**: https://bulma.io/documentation/
- **Font Awesome**: https://fontawesome.com/icons

---

*Last updated: Generated for AI agent reference*
