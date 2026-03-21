# Wind Nowcasting - Project Documentation for AI Agents

## Project Overview

This is a **Jekyll-based static website** for the **Wind Nowcasting** project - an AI-powered weather forecasting research initiative conducted by a team from the Australian National University (ANU) in collaboration with the Australian Bureau of Meteorology (BOM).

The website serves as the project's public documentation hub, featuring:
- Project overview with data-driven cards
- Interactive project roadmap with semester-based timeline
- Team member profiles (stakeholder, students, tutor)
- Blog for research updates (currently no posts)
- Modern dark-themed UI with WebGL2 animated particle background

## Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Static Site Generator | Jekyll | ~> 4.4.1 |
| Theme | Minima | ~> 2.5 |
| CSS Framework | Bulma | (bundled, ~785KB) |
| Icons | Font Awesome | 7.0.1 (CDN) |
| Animation | Anime.js | (CDN) |
| Graphics | WebGL2 + Custom Perlin Noise | - |
| Language | Ruby | (via Bundler) |

### External Dependencies (CDN)
- `https://cdnjs.cloudflare.com/ajax/libs/font-awesome/7.0.1/css/all.min.css`
- `https://cdn.jsdelivr.net/npm/animejs/dist/bundles/anime.umd.min.js`

### Ruby Dependencies
- jekyll (~> 4.4.1)
- minima (~> 2.5)
- jekyll-feed (~> 0.12)
- tzinfo, tzinfo-data (Windows/JRuby)
- wdm (~> 0.1) (Windows file watching)

## Project Structure

```
.
├── _config.yml              # Jekyll configuration
├── Gemfile                  # Ruby dependencies
├── Gemfile.lock             # Locked dependency versions
├── .gitignore               # Git ignore rules (_site, .sass-cache, .jekyll-cache, vendor)
│
├── _layouts/                # HTML page layouts
│   ├── base.html            # Base layout with WebGL background, header, footer
│   └── post.html            # Blog post layout (extends base)
│
├── _includes/               # Reusable HTML components
│   ├── header.html          # Site navigation header with mobile menu toggle
│   ├── footer.html          # Site footer with links and social icons
│   ├── hero.html            # Hero section with title, subtitle, CTA buttons
│   ├── section-header.html  # Section title component
│   ├── overview-card.html   # Project overview card (icon, title, description, stat)
│   ├── member-card.html     # Team member card (avatar, name, role, GitHub)
│   └── goal-card.html       # Project goal card (icon, title, description)
│
├── _data/                   # YAML data files
│   ├── nav.yml              # Navigation menu items (Home, About, Blog)
│   ├── members.yml          # Team member information (7 members)
│   ├── overview.yml         # Project overview cards data (3 cards: Data, Model, Evaluation)
│   └── roadmap.yml          # Project roadmap/timeline data (2 semesters)
│
├── _posts/                  # Blog posts (Markdown) - currently empty
│
├── assets/
│   ├── css/
│   │   ├── bulma.css        # Bulma CSS framework
│   │   ├── bulma.css.map    # Source map
│   │   └── style.css        # Main stylesheet (imports all components)
│   │       └── components/
│   │           ├── variables.css       # CSS custom properties
│   │           ├── base.css            # Base styles & utilities
│   │           ├── section-header.css  # Section header component
│   │           ├── overview-cards.css  # Overview card grid
│   │           ├── timeline.css        # Roadmap timeline
│   │           ├── hero.css            # Hero section & CTA buttons
│   │           ├── about.css           # About page (goals, members, partners)
│   │           ├── header.css          # Site header & navigation
│   │           ├── footer.css          # Site footer
│   │           ├── blog.css            # Blog listing page
│   │           └── post-article.css    # Individual post pages
│   └── js/
│       ├── perlin.js        # Perlin noise library for background animation
│       ├── background.js    # WebGL2 background animation with curl noise
│       ├── two.min.js       # Two.js graphics library (unused)
│       └── script.js        # Reserved for future use
│
├── index.html               # Homepage with hero, overview cards, roadmap, goals
├── about.html               # About/Team page with member cards and partners
├── blog.html                # Blog listing page
└── 404.html                 # 404 error page (uses 'page' layout - may need fix)
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
- **Important**: Changing `_config.yml` requires server restart

## Code Style Guidelines

### HTML/Liquid Templates
- Use 4-space indentation
- Use double quotes for attributes
- Use `{{ site.baseurl }}` for internal links
- Use `relative_url` filter for URLs
- Layouts use YAML front matter with `layout: base` for extension

### CSS Architecture
- Modular component-based structure in `assets/css/components/`
- CSS custom properties defined in `variables.css`
- BEM-like naming convention used
- Mobile-first responsive design with breakpoints at 768px and 640px

### Color Scheme (CSS Variables)
- `--primary-blue: #007bff`
- `--secondary-purple: #4f3fff`
- `--accent-purple: #9b59b6`
- `--accent-green: #2ecc71`
- `--accent-teal: #1abc9c`
- `--accent-orange: #f39c12`
- `--accent-pink: #fd79a8`
- Background: `#111` (dark theme)

### JavaScript
- ES6+ syntax used in background.js
- WebGL2 with GLSL 3.0 shaders
- Component-based class architecture (ParticleSystem)
- Event listeners use passive mode where appropriate

## Data Files Reference

### _data/nav.yml
Navigation menu structure:
```yaml
- title: Home
  url: /
- title: About
  url: /about/
- title: Blog
  url: /blog/
```

### _data/members.yml
Team member profiles. Fields:
- `name`: Full name
- `role`: Role (Stakeholder/Student/Tutor)
- `id`: University ID or identifier
- `email`: Email address
- `github`: GitHub username
- `phone`: Phone number (stakeholder only)
- `avatar`: Initial letter for avatar
- `color`: Avatar color class (primary/blue/purple/green/orange/pink/teal)

### _data/overview.yml
Project overview cards displayed on homepage. Fields:
- `icon_class`: CSS class for icon styling (data-icon/model-icon/eval-icon)
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
- `badge_class`: Optional CSS class for styling (s2 for purple theme)
- `line_class`: Optional CSS class for timeline line (s2-line)
- `milestones`: Array of milestone objects with `icon`, `title`, `description`, `marker_class`

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

## Layouts

### base.html
- Base layout used by all pages
- Includes header and footer
- Loads all required CSS and JS
- Sets up WebGL2 background canvas with id `index-background`
- Sets `data-theme="dark"` on body

### post.html
- Extends base layout
- Adds article styling with post metadata
- Includes back-to-blog link
- Forces black background (`#111`)

## Key Features

### WebGL2 Animated Background
- File: `assets/js/background.js`
- Uses curl noise and fractional Brownian motion (fBM)
- Particle system with configurable size and spacing
- Three color types: blue (30%), gray (68%), light blue (2%)
- Gracefully degrades if WebGL2 is not supported

### Responsive Design
- Mobile-first approach
- Breakpoints: 640px, 768px
- Hamburger menu for mobile navigation
- Flexible grid layouts using Bulma's column system

## Testing

### Local Testing
1. Run `bundle exec jekyll serve`
2. Visit `http://localhost:4000/BOM-Team/`
3. Test on different screen sizes (responsive design)
4. Verify WebGL background renders (check console for warnings if not)

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

**WebGL background not showing:**
- Check browser console for WebGL2 support warnings
- Verify `perlin.js` is loaded before `background.js`

## External Resources

- **Jekyll Docs**: https://jekyllrb.com/docs/
- **Liquid Syntax**: https://shopify.github.io/liquid/
- **Bulma CSS**: https://bulma.io/documentation/
- **Font Awesome**: https://fontawesome.com/icons

---

*Last updated: Based on actual project exploration*
