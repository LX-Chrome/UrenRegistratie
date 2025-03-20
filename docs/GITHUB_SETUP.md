# Setting Up a GitHub Repository for Time Registrator

This guide will walk you through the process of creating a GitHub repository for the Time Registrator application and pushing your code to it.

## Step 1: Create a New Repository on GitHub

1. Go to [GitHub](https://github.com/) and sign in to your account
2. Click the "+" button in the top right corner, then select "New repository"
3. Enter the following information:
   - Repository name: `time-registrator`
   - Description: `A comprehensive time tracking and project management application for logging and managing work hours`
   - Visibility: Choose either Public or Private
   - Do NOT initialize with a README, .gitignore, or license (since we already have our files)
4. Click "Create repository"

## Step 2: Push Your Local Repository to GitHub

After creating the repository, GitHub will show you commands to push an existing repository. You'll need to:

1. Copy the repository URL shown on the GitHub page (it should look like `https://github.com/YOUR-USERNAME/time-registrator.git`)

2. Open your command line/terminal in the root directory of your Time Registrator project

3. If you haven't already configured your Git user identity, run:
   ```
   git config --global user.email "your-email@example.com"
   git config --global user.name "Your Name"
   ```

4. Make sure all your files are added to Git:
   ```
   git add .
   ```

5. Commit your changes:
   ```
   git commit -m "Initial commit with comprehensive documentation"
   ```

6. Add the GitHub repository as a remote:
   ```
   git remote add origin https://github.com/YOUR-USERNAME/time-registrator.git
   ```

7. Push your code to GitHub:
   ```
   git push -u origin main
   ```
   (If your branch is named "master" instead of "main", use `git push -u origin master`)

## Step 3: Verify Your Repository

1. Refresh your GitHub repository page
2. You should see all your files and documentation

## Step 4: Create GitHub Pages (Optional)

If you want to make your documentation accessible as a website:

1. Go to your repository on GitHub
2. Click "Settings"
3. Scroll down to "GitHub Pages"
4. Under "Source", select "main" branch and "/docs" folder
5. Click "Save"
6. After a few minutes, your documentation will be available at `https://YOUR-USERNAME.github.io/time-registrator/`

## Troubleshooting

If you encounter authentication issues when pushing to GitHub:

1. You might need to create a personal access token:
   - Go to GitHub → Settings → Developer settings → Personal access tokens
   - Generate a new token with "repo" permissions
   - Use this token as your password when pushing

2. If you're using HTTPS URLs, you might be prompted for username and password:
   - Username: Your GitHub username
   - Password: Your personal access token (not your GitHub password)

3. If you have two-factor authentication enabled, you must use a personal access token instead of your password 