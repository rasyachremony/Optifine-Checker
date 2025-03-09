# Publishing to GitHub Guide

This guide will walk you through the process of publishing your OptiFine Cape Checker to GitHub.

## Prerequisites

1. Create a [GitHub account](https://github.com/join) if you don't already have one
2. Install [Git](https://git-scm.com/downloads) on your computer
3. Configure Git with your username and email:
   ```
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

## Step 1: Create a New Repository on GitHub

1. Log in to your GitHub account
2. Click the "+" icon in the top-right corner and select "New repository"
3. Name your repository (e.g., "optifine-cape-checker")
4. Add a description (optional)
5. Choose "Public" or "Private" visibility
6. Do NOT initialize the repository with a README, .gitignore, or license
7. Click "Create repository"

## Step 2: Initialize Your Local Repository

1. Open a terminal/command prompt
2. Navigate to your project folder:
   ```
   cd /path/to/optifine-cape-checker
   ```
3. Initialize a Git repository:
   ```
   git init
   ```

## Step 3: Add Your Files to the Repository

1. Add all your files to the staging area:
   ```
   git add .
   ```
2. Commit your files:
   ```
   git commit -m "Initial commit"
   ```

## Step 4: Connect and Push to GitHub

1. Connect your local repository to the GitHub repository:
   ```
   git remote add origin https://github.com/yourusername/optifine-cape-checker.git
   ```
   (Replace "yourusername" with your actual GitHub username)

2. Push your code to GitHub:
   ```
   git push -u origin main
   ```
   (If you're using an older version of Git, you might need to use `master` instead of `main`)

## Step 5: Verify Your Repository

1. Go to your GitHub repository page
2. Refresh the page if necessary
3. You should see all your files uploaded to GitHub

## Making Changes

After your initial push, whenever you make changes:

1. Add the changed files:
   ```
   git add .
   ```
2. Commit the changes:
   ```
   git commit -m "Description of changes"
   ```
3. Push to GitHub:
   ```
   git push
   ```

## Important Notes

1. Remember to update the copyright in the LICENSE file with your name
2. Update the README.md with your GitHub username in the clone URL
3. Never commit sensitive information like real account credentials
4. The .gitignore file is set up to exclude most sensitive files, but always double-check before committing

## Troubleshooting

- **Authentication Issues**: GitHub now requires a personal access token instead of a password for HTTPS authentication. [Learn how to create one](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- **Push Rejected**: If your push is rejected, try pulling first with `git pull --rebase origin main`
- **File Too Large**: GitHub has a file size limit. If you encounter this issue, add the large file to .gitignore 