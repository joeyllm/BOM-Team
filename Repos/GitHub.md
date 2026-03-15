# 🐙 GitHub: Our Central Source of Truth

While we communicate on Discord, **GitHub is where the actual work gets done.** This is our central hub for project tracking, version control, and collaborating on code.

---

## 🛑 The "Stay in the Repo" Rule

Throughout the semester, your university tutors, lecturers, or external advisors might suggest using various third-party tools for project management (like Trello, Jira, Asana, or Notion). 

**Please remember: those are only suggestions.** For the BOM Nowcasting project, **we strictly use GitHub for everything.** We do not fragment our workflow across multiple outside tools. Every piece of code, every task, and every project milestone stays right here in the repository. Keeping our tools consolidated makes us significantly faster and more organized.

---

## 🛠️ How We Work Together

We utilize GitHub's built-in features to manage the entire lifecycle of our pipelines and models:

### 1. Code Repositories (Version Control)
As mentioned in our data documentation, your pipeline code is your most valuable asset. All Python scripts, Jupyter Notebook exports, container configurations, and training loops must be committed here regularly. **If it is not committed to GitHub, it does not exist!**

### 2. Project Tracking (GitHub Projects & Issues)
Instead of external task trackers, we use **GitHub Issues** to report bugs or outline new features, and **GitHub Projects** (the built-in Kanban boards) to track our progress. 
* If you are picking up a task (like optimizing a specific data cleaning function), assign the Issue to yourself.
* Move your tasks across the project board (Todo ➡️ In Progress ➡️ Done) so the whole team knows what is actively being worked on.



### 3. Collaboration (Pull Requests)
When you finish a feature or pipeline, you will submit a **Pull Request (PR)**. This allows the rest of the team to review your code, suggest memory optimizations (especially for our L4 GPUs), and ensure it won't break the system before it gets merged into the main branch.

---

## ✅ Your First Steps
* Ensure you have access to the BOM Nowcasting organization and repositories.
* Check the current Issues tab or Project board to see what tasks are open.
* Get comfortable with standard Git commands (`git pull`, `git commit`, `git push`) and branch management, as you will be using them every single day.
