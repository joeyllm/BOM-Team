# BOM Nowcasting - Project Documentation for AI Agents

## Project Overview

**BOM Nowcasting** is a weather forecasting research project conducted by a team from the Australian National University (ANU) in collaboration with the Australian Bureau of Meteorology (BOM). The project focuses on building practical short-term (nowcasting) weather forecasting workflows end to end.

This repository serves as the **central documentation and project management hub** for the team. It contains **no source code** - only documentation, planning materials, and knowledge base resources.

### Project Goals

By the end of the project the team will have:
- Built workflows for **ingesting and cleaning forecasting data**
- Created **baseline nowcasting models**
- Developed **evaluation and validation pipelines**
- Produced **forecast outputs and performance reports**

The project provides hands-on experience with real-world data, modelling, and infrastructure workflows used in operational forecasting.

---

## Repository Structure

```
.
├── README.md                  # Main project overview and entry point
├── .gitignore                 # Git ignore rules (Python-focused)
├── AGENTS.md                  # This file - documentation for AI agents
│
├── docs/                      # Jekyll-based static website (GitHub Pages)
│   ├── _config.yml            # Jekyll configuration
│   ├── Gemfile                # Ruby dependencies
│   ├── _data/                 # YAML data files (members, roadmap, nav)
│   ├── _layouts/              # HTML page layouts
│   ├── _includes/             # Reusable HTML components
│   ├── assets/                # CSS, JavaScript, images
│   └── *.html                 # Static pages (index, about, blog, 404)
│
├── knowledge-base/            # Shared reference material and documentation
│   ├── compute-infrastructure/# VPN, GPU, and system access docs
│   ├── data/                  # Data sources, rules, and best practices
│   ├── models/                # Model architecture notes
│   ├── learning-resources/    # Shared notes and study material
│   ├── papers/                # Paper reading notes
│   ├── q-and-a/               # Questions and answers
│   ├── repos/                 # Platform and tooling documentation
│   └── AGILE methods/         # Project management methodologies
│
├── management/                # Team progress tracking and coordination
│   ├── weekly-reports/        # Combined meeting notes and progress reports
│   └── weekly-todos/          # Weekly task lists
│
├── roadmap/                   # Project planning and semester overviews
│   ├── ProjectGoal.md         # High-level project goals
│   ├── Semester1DataInfrastructure.md  # S1 focus: data & infrastructure
│   ├── Semester2ModelTraining.md       # S2 focus: forecast modelling
│   └── GithubProjectBoard.md  # Task tracking guidelines
│
└── team-members/              # Team member profiles and notebook tracking
    ├── README.md              # Team roster with contact information
    └── [member-name]/         # Individual member folders
        ├── README.md          # Member profile
        └── week-XX.ipynb      # Weekly Jupyter notebooks (work in progress)
```

---

## Technology Stack

### Main Repository (Documentation)

| Component | Technology |
|-----------|------------|
| Documentation Format | Markdown (.md) |
| Version Control | Git |
| Hosting Platform | GitHub |
| Project Management | GitHub Projects (Kanban board) |

### Documentation Website (`docs/` folder)

| Component | Technology | Version |
|-----------|------------|---------|
| Static Site Generator | Jekyll | ~> 4.4.1 |
| Theme | Minima | ~> 2.5 |
| CSS Framework | Bulma | bundled (~785KB) |
| Icons | Font Awesome | 7.0.1 (CDN) |
| Animation | Anime.js | CDN |
| Graphics | WebGL2 + Custom Perlin Noise | - |
| Language | Ruby | via Bundler |

### External Dependencies (CDN)

- Font Awesome: `https://cdnjs.cloudflare.com/ajax/libs/font-awesome/7.0.1/css/all.min.css`
- Anime.js: `https://cdn.jsdelivr.net/npm/animejs/dist/bundles/anime.umd.min.js`

### Ruby Dependencies

- jekyll (~> 4.4.1)
- minima (~> 2.5)
- jekyll-feed (~> 0.12)
- tzinfo, tzinfo-data (Windows/JRuby)
- wdm (~> 0.1) (Windows file watching)

---

## Build and Development Commands

### Documentation Website (`docs/` folder)

#### Prerequisites
- Ruby installed (2.5 or higher recommended)
- Bundler gem installed (`gem install bundler`)

#### Setup
```bash
cd docs
bundle install
```

#### Development
```bash
# Start local development server
bundle exec jekyll serve

# Start with live reload (auto-refresh on changes)
bundle exec jekyll serve --livereload

# Server will be available at http://localhost:4000/BOM-Team/
```

#### Production Build
```bash
# Build site for production
bundle exec jekyll build

# Output will be in _site/ directory
```

#### Configuration Notes
- `baseurl` is set to `/BOM-Team` for GitHub Pages deployment
- URL structure: `http://localhost:4000/BOM-Team/`
- **Important**: Changing `_config.yml` requires server restart

---

## Code Style Guidelines

### Markdown Documentation

- Use standard Markdown (.md) files
- Write documents so they are clear and highly scannable
- Use headers, bullet points, and lists to break up walls of text
- Keep files structured and logically organized within their folders
- Try not to let documentation pages grow too massive
- Keep documents short, punchy, and concise
- If a document becomes too long, split it into a new, separate file
- Each document should ideally focus on **one main topic**

### HTML/Liquid Templates (docs/)

- Use 4-space indentation
- Use double quotes for attributes
- Use `{{ site.baseurl }}` for internal links
- Use `relative_url` filter for URLs
- Layouts use YAML front matter with `layout: base` for extension

### CSS Architecture (docs/)

- Modular component-based structure in `assets/css/components/`
- CSS custom properties defined in `variables.css`
- BEM-like naming convention used
- Mobile-first responsive design with breakpoints at 768px and 640px

### Color Scheme (CSS Variables in docs/)

- `--primary-blue: #007bff`
- `--secondary-purple: #4f3fff`
- `--accent-purple: #9b59b6`
- `--accent-green: #2ecc71`
- `--accent-teal: #1abc9c`
- `--accent-orange: #f39c12`
- `--accent-pink: #fd79a8`
- Background: `#111` (dark theme)

### JavaScript (docs/)

- ES6+ syntax used in background.js
- WebGL2 with GLSL 3.0 shaders
- Component-based class architecture (ParticleSystem)
- Event listeners use passive mode where appropriate

---

## Testing Instructions

### Documentation Website Testing

1. Run `bundle exec jekyll serve`
2. Visit `http://localhost:4000/BOM-Team/`
3. Test on different screen sizes (responsive design)
4. Verify WebGL background renders (check console for warnings if not)

### Build Verification

```bash
# Verify build completes without errors
bundle exec jekyll build --strict_front_matter
```

---

## Deployment

### GitHub Pages (docs/ website)

The site is configured for GitHub Pages deployment:
- `baseurl: "/BOM-Team"` is set in `_config.yml`
- Push changes to GitHub repository
- GitHub Pages will automatically build and deploy
- Site will be available at: `https://[username].github.io/BOM-Team/`

---

## Team Structure

| Name | Role | Contact |
|------|------|---------|
| Matthew Altenburg | 📌 Stakeholder | matthew.altenburg@anu.edu.au |
| Adam Ahammed Basheer | 🎓 Student | u7628910@anu.edu.au |
| Dylan Han | 🎓 Student | Zhaokun.Han@anu.edu.au |
| Junling Yu | 🎓 Student | Junling.Yu@anu.edu.au |
| Kecheng Zhang | 🎓 Student | Kecheng.Zhang@anu.edu.au |
| Olivia Maftukhaturrizqoh | 🎓 Student | Olivia.Maftukhaturrizqoh@anu.edu.au |
| Lifan Zhao | 🏫 Tutor | Lifan.Zhao@anu.edu.au |

---

## Project Roadmap

### Semester 1 – Data and Infrastructure

Focus: **Understanding the infrastructure and preparing forecasting datasets**

Key Activities:
- Exploring the dataset
- Validating source quality
- Cleaning and normalising records
- Preparing data suitable for machine learning
- Building baseline analytical and predictive models

Goal: Produce **high-quality validated datasets** for forecast modelling.

### Semester 2 – Forecast Modelling

Focus: **Building and refining nowcasting models**

Key Activities:
- Regional forecasting models
- Rainfall or severe-weather nowcasting workflows
- Domain-specific forecast evaluation pipelines

Goal: Understand how datasets shape forecast behaviour and build reliable nowcasting systems.

---

## Compute Infrastructure

### System Architecture

```
Student Laptop
      │
      ▼
WireGuard VPN
      │
      ▼
Compute Server
      │
      ├── 🧠 CPU Notebooks (Default)
      └── 🚀 GPU Notebooks (NVIDIA L4)
```

### Access Steps

1. **Connect to the Network** - Use WireGuard VPN (see `knowledge-base/compute-infrastructure/Wireguard.md`)
2. **Verify GitHub Access** - Ensure you have an active GitHub account and have been added to the project's GitHub team
3. **Launch Your Notebook** - Navigate to `http://10.55.0.245` and sign in with GitHub credentials

### Compute Profiles

| Profile | 🧠 CPU Environment | 🚀 GPU Environment |
| :--- | :--- | :--- |
| **Specs** | Standard compute | NVIDIA L4 GPU (24 GB VRAM)* |
| **Best For** | Data exploration, cleaning, analysis | ML training, GPU-accelerated processing |
| **Availability**| Plentiful | **Limited (6 total GPUs)** |
| **Usage Rule** | **Use this most of the time** | **Use only when needed** |

\* Note: The NVIDIA L4 is roughly comparable to (and slightly better than) an NVIDIA A10 commonly used on AWS.

### Best Practices

- **Default to CPU:** Do exploratory work and code testing on the CPU environment
- **Free Up Resources:** Always shut down GPU sessions as soon as workloads are finished
- **Save Your Work:** Commit code to GitHub regularly to prevent data loss

---

## Data Environment

### Storage Limits & Quotas

- Each student is allocated a strict **50 GB personal storage quota**
- This space is for code, small test files, environment configurations, and limited output data
- The project works with a **60 TB corpus** of weather data

### Critical Rules

1. **Never copy shared datasets to your personal directory** - This will exhaust your 50 GB quota and break your environment
2. **Always read data directly from shared, read-only folders into memory**
3. **Commit your code to GitHub regularly** - There is no guarantee that saved data will persist from week to week

### Key Data Documentation

| File | Description |
| :--- | :--- |
| `knowledge-base/data/Fineweb.md` | Details on the 60 TB Fineweb corpus |
| `knowledge-base/data/LoadingData.md` | Code examples for loading data (CPU/GPU) |
| `knowledge-base/data/BestPractices.md` | Memory management and "Subset First" rule |
| `knowledge-base/data/Publishing.md` | Hugging Face, Kaggle & Data Cards |

---

## Development Conventions

### The "Stay in GitHub" Rule

**Keep all project work inside GitHub.** GitHub provides everything needed for documentation, planning, and task tracking.

> **Important:** You may receive suggestions to use different third-party tools (Notion, Jira, Trello). **Those are only suggestions.** For this project, keep *everything* inside this repository and the GitHub platform.

### GitHub Project Board

The team uses a GitHub Project Kanban board called **BOM Nowcasting Team** to manage tasks and track progress.

**Workflow:**
1. Create or update a GitHub issue for the work item
2. Add the issue to the `BOM Nowcasting Team` project board
3. Move the item across columns as work progresses
4. Reference the issue or card in weekly updates

### Weekly Reporting

- Weekly reports are prepared on **Mondays**
- Reports are stored in `management/weekly-reports/`
- Use the template in `management/weekly-reports/WeeklyReportTemplate.md`
- Naming convention: `WeekXXReport.md` (e.g., `Week01Report.md`)

### Notebook Uploads

- Place weekly Jupyter notebook files in each member's folder under `team-members/[name]/`
- Suggested naming: `week-01.ipynb`, `week-02.ipynb`, etc.
- Upload weekly working notebooks, not just final polished versions

---

## Security Considerations

### General

- No sensitive credentials should be stored in this repository
- All external CDN links use HTTPS
- Static site - no server-side processing
- No forms or user input handling in the documentation site

### VPN Access

- WireGuard VPN is required to access compute infrastructure
- Each user must generate a public/private key pair
- Never share your Private Key with anyone
- Disconnect VPN when not actively working on the project

### Data Security

- The 60 TB dataset is stored on secure internal servers
- Access is controlled via VPN and GitHub authentication
- Personal storage (50 GB) is isolated per user

---

## Troubleshooting

### Jekyll serve fails
- Ensure Ruby and Bundler are installed
- Run `bundle install` to update dependencies

### Changes not reflecting
- Restart the server after modifying `_config.yml`
- Clear browser cache
- Check `_site/` directory is being updated

### CSS/JS not loading
- Verify `baseurl` is correctly set
- Check file paths include `{{ site.baseurl }}`

### WebGL background not showing
- Check browser console for WebGL2 support warnings
- Verify `perlin.js` is loaded before `background.js`

### VPN Connection Issues
- Double-check that WireGuard says "Active"
- Try deactivating and reactivating the tunnel
- Contact Matthew Altenburg for support

---

## External Resources

- **Jekyll Docs**: https://jekyllrb.com/docs/
- **Liquid Syntax**: https://shopify.github.io/liquid/
- **Bulma CSS**: https://bulma.io/documentation/
- **Font Awesome**: https://fontawesome.com/icons
- **WireGuard**: https://www.wireguard.com/install/

---

## Quick Links for New Team Members

1. `roadmap/ProjectGoal.md` - Understand the project goals
2. `knowledge-base/compute-infrastructure/Wireguard.md` - Set up VPN access
3. `team-members/README.md` - Meet the team
4. `management/weekly-reports/README.md` - Understand reporting process
5. `management/weekly-todos/README.md` - Task tracking

---

*Last updated: 2026-03-23*
