# Upload Project to GitHub

## Step-by-Step Instructions

### Step 1: Navigate to Project Directory

Open PowerShell or Command Prompt and navigate to your project:

```powershell
cd "C:\Users\ROG\Desktop\人工智能导论\YA_MCPServer_Template"
```

### Step 2: Initialize Git Repository (if not already initialized)

```powershell
git init
```

### Step 3: Add Remote Repository

```powershell
git remote add origin https://github.com/wangzhiyao-sys/shaziwzy.git
```

If the remote already exists, update it:

```powershell
git remote set-url origin https://github.com/wangzhiyao-sys/shaziwzy.git
```

### Step 4: Check Current Status

```powershell
git status
```

### Step 5: Add All Files

```powershell
git add .
```

### Step 6: Commit Changes

```powershell
git commit -m "Initial commit: MCP-PolyGame-Agent - Role-aware multi-party game reasoning system"
```

Or use a more detailed commit message:

```powershell
git commit -m "Add MCP-PolyGame-Agent project

- Implemented Bayesian inference for identity reasoning
- Implemented knowledge graph for relationship analysis
- Implemented game tree search for action decision making
- Added 11 MCP tools for game management and analysis
- Added 7 resources and 5 prompts for enhanced usability
- Complete documentation and usage guides"
```

### Step 7: Push to GitHub

If this is the first push:

```powershell
git branch -M main
git push -u origin main
```

If the repository already has content and you want to force push (be careful!):

```powershell
git push -u origin main --force
```

## Alternative: Using GitHub CLI

If you have GitHub CLI installed:

```powershell
gh repo set-default wangzhiyao-sys/shaziwzy
git push -u origin main
```

## Troubleshooting

### If you get authentication error:

1. Use Personal Access Token instead of password
2. Or use SSH instead:

```powershell
git remote set-url origin git@github.com:wangzhiyao-sys/shaziwzy.git
```

### If you need to authenticate:

GitHub no longer accepts passwords. You need to:
1. Generate a Personal Access Token: https://github.com/settings/tokens
2. Use the token as password when prompted

### Check what will be uploaded:

```powershell
git status
git ls-files
```

This shows all files that will be committed.

## Files That Will NOT Be Uploaded

The following are ignored by .gitignore:
- `logs/` directory
- `data/` directory (database files)
- `__pycache__/` directories
- `.venv/` directories
- `*.db`, `*.sqlite` files
- `*.log` files
- `uv.lock` files

## After Uploading

1. Go to https://github.com/wangzhiyao-sys/shaziwzy
2. Verify all files are uploaded correctly
3. Update README.md on GitHub if needed
4. Add project description and topics on GitHub
