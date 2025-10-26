# GitHub Release Guide

## 🚀 How to Publish Your Desktop App

### Step 1: Create GitHub Repository

```bash
cd /Users/sammalik/Desktop/xyz/cursor_mover_app

# Initialize git
git init
git add .
git commit -m "Initial commit: Random Cursor Mover Desktop App"

# Create repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/cursor-mover.git
git branch -M main
git push -u origin main
```

### Step 2: Build All Platforms

**On macOS (build macOS + Linux):**
```bash
./build.sh
# This creates: dist/CursorMover.app
```

**On Windows (build Windows):**
```cmd
build.bat
# Creates: dist\CursorMover.exe
```

**Or use GitHub Actions** (recommended):
- Create `.github/workflows/build.yml` (see BUILD_INSTRUCTIONS.md)
- Push code, GitHub Actions builds all platforms automatically

### Step 3: Prepare Release Assets

**macOS:**
```bash
cd dist
zip -r ../CursorMover-macOS.zip CursorMover.app
cd ..
```

**Windows:**
```cmd
cd dist
zip CursorMover-Windows.zip CursorMover.exe
cd ..
```

**Linux:**
```bash
cd dist
tar -czf ../CursorMover-Linux.tar.gz CursorMover
cd ..
```

### Step 4: Create GitHub Release

1. Go to your GitHub repository
2. Click "Releases" → "Create a new release"
3. Tag: `v1.0.0`
4. Title: `v1.0.0 - Random Cursor Mover`
5. Description:

```markdown
# Random Cursor Mover v1.0.0

A cross-platform desktop app that automatically moves your cursor at specified intervals.

## Downloads

- **macOS**: [CursorMover-macOS.zip](link)
- **Windows**: [CursorMover-Windows.zip](link)
- **Linux**: [CursorMover-Linux.tar.gz](link)

## How to Use

1. Download for your platform
2. Extract the archive
3. Run the executable
4. Click "Start" to begin cursor movement

## Requirements

- macOS 10.14+, Windows 10+, or modern Linux
- No Python installation needed!

## Permissions (macOS)

You may need to grant Accessibility permissions:
1. System Settings → Privacy & Security → Accessibility
2. Add CursorMover
3. Enable the toggle

## Features

- ✅ Moves cursor to random positions
- ✅ Configurable interval (10 seconds - 1 hour)
- ✅ Simple GUI
- ✅ Cross-platform
- ✅ Lightweight
```

6. Upload your release assets (zip files)
7. Click "Publish release"

### Step 5: Add Release Badges

Add to README.md:

```markdown
# Random Cursor Mover

[![GitHub release](https://img.shields.io/github/release/YOUR_USERNAME/cursor-mover.svg)](https://GitHub.com/YOUR_USERNAME/cursor-mover/releases/)
[![Downloads](https://img.shields.io/github/downloads/YOUR_USERNAME/cursor-mover/total.svg)](https://github.com/YOUR_USERNAME/cursor-mover/releases/)
```

## 📝 Release Checklist

- [ ] Code is working and tested
- [ ] Built executables for all platforms
- [ ] Tested executables on each platform
- [ ] Created release notes
- [ ] Tagged the release
- [ ] Uploaded release assets
- [ ] Published the release
- [ ] Updated README with download links

## 🎯 Automated Releases

Use GitHub Actions to automate builds and releases:

```yaml
name: Build and Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [macos-latest, ubuntu-latest, windows-latest]

    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: pip install -r requirements.txt pyinstaller

    - name: Build executable
      run: ./build.sh  # or appropriate command

    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: CursorMover-${{ runner.os }}

  release:
    needs: build
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3
    - uses: softprops/action-gh-release@v1
      with:
        files: |
          dist/**/*
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## 🔄 Continuous Deployment

Every time you push a tag like `v1.0.1`:

1. GitHub Actions builds all platforms
2. Creates release automatically
3. Uploads executables
4. Publishes release

**Usage:**
```bash
git tag v1.0.1
git push origin v1.0.1
# Automatically creates release!
```

