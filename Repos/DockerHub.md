# 🐳 DockerHub & Container Registries

Containerization is a massive part of our workflow, especially as we package our environments to move from our local L4 GPUs up to the supercomputing clusters. 

First and foremost: **DockerHub is one of our amazing project sponsors** (alongside GitHub), and we are incredibly grateful for their support of the BOM Nowcasting team!

---

## 🔄 The Term 1 Experiment: GitHub Actions

While DockerHub has traditionally been our go-to registry for hosting our container images, we are running an experiment this term. 

As you read in our GitHub documentation, we are trying to aggressively consolidate our tools. To see if it speeds up our workflow, **we are shifting our automated builds to GitHub Actions and hosting our images directly in the GitHub Container Registry.**



We want to test if keeping our code, our issue tracking, our CI/CD pipelines, and our container images all under one single roof reduces friction for the team.

---

## 🙋 Can I still use DockerHub?

Absolutely! 

Because they are a project sponsor, we still have full access to their platform. If you have a specific use case where DockerHub makes more sense, or if you simply want to learn how to use it for your own professional development, **just ask.**

Reach out to Matthew, and we can easily get you set up with access to push your pipeline and testing containers to our BOM Nowcasting DockerHub organization. 

Otherwise, default to using GitHub Actions for your container builds this term while we test out this new workflow!
