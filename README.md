# AI Auto-Committer

<div align="center">

![AI Auto-Committer](icon.ico)

**AI-powered Git commit message generator with a modern GUI**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

## 📖 Overview

AI Auto-Committer is a powerful desktop application that streamlines your Git workflow by automatically generating meaningful commit messages using AI. It features a modern, user-friendly interface built with CustomTkinter and supports multiple AI providers including Gemini, OpenAI, and Ollama.

### ✨ Key Features

- 🤖 **AI-Powered Commit Messages** - Generate contextual commit messages from your code changes
- 🎨 **Modern GUI** - Beautiful, responsive interface with light/dark theme support
- 📁 **Selective File Staging** - Choose which files to include in your commit
- 🔄 **Git Operations** - Push, pull, and view current branch directly from the app
- 🌐 **Multiple AI Providers** - Support for Gemini, OpenAI, and Ollama
- ⚙️ **Customizable** - Configure API keys, models, and system prompts
- 📊 **Diff Viewer** - Tabbed interface to review changes before committing

## 🚀 Quick Start

### Option 1: Download Executable (Windows)

**[📥 Download AI_Auto_Committer.exe]([https://github.com/eliau2005/AI_Auto_Committer/raw/main/dist/AI_Auto_Committer.exe](https://github.com/eliau2005/AI_Auto_Committer/raw/refs/heads/master/dist/AI_Auto_Committer.exe))**

1. Download the executable from the link above
2. Run `AI_Auto_Committer.exe`
3. Configure your API key and AI provider in Settings (⚙️)
4. Start committing!

### Option 2: Run from Source

#### Prerequisites

- Python 3.8 or higher
- Git installed and configured
- API key for your chosen AI provider (Gemini, OpenAI, or Ollama)

#### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/eliau2005/AI_Auto_Committer.git
   cd AI_Auto_Committer
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

4. **Configure settings**
   - Click the Settings button (⚙️) in the top-right corner
   - Enter your API key
   - Select your AI provider and model
   - (Optional) Customize the system prompt
   - Choose your preferred theme (Light/Dark)

## 📦 Dependencies

The application requires the following Python packages:

- **customtkinter** - Modern UI framework
- **Pillow** - Image processing for icons
- **google-generativeai** - Gemini AI integration
- **openai** - OpenAI API integration
- **requests** - HTTP requests for Ollama

All dependencies are listed in `requirements.txt` and will be installed automatically.

## 🛠️ Building from Source

To build your own executable:

```bash
python build_exe.py
```

The executable will be created in the `dist/` folder.

## 📋 Usage

1. **Select Repository**
   - Use the dropdown menu to select a recent repository
   - Or click "Browse..." to select a new repository

2. **Review Changes**
   - View changed files in the sidebar
   - Select/deselect files to include in the commit
   - Review diffs in the tabbed viewer

3. **Generate Commit Message**
   - Click "✨ Generate AI Message"
   - The AI will analyze your changes and create a commit message
   - Edit the title and description as needed

4. **Commit**
   - Click "Commit to [branch]" to commit your changes
   - Use Push/Pull buttons to sync with remote

## ⚙️ Configuration

### AI Providers

- **Gemini** - Google's Gemini AI (requires API key)
- **OpenAI** - ChatGPT and GPT models (requires API key)
- **Ollama** - Local AI models (no API key needed)

### Settings Location

User settings are stored in `settings.json` (not tracked in Git for privacy).

## 🎨 Features in Detail

### Selective File Staging
Choose exactly which files to include in your commit with checkboxes in the sidebar.

### Diff Viewer
View up to 8 file diffs simultaneously in a tabbed interface with syntax highlighting for additions and deletions.

### Theme Support
Switch between Light and Dark themes to match your preference.

### Branch Management
See your current branch at a glance and perform push/pull operations without leaving the app.

## 🤝 Contributing

Contributions are welcome! Feel free to:

- Report bugs
- Suggest new features
- Submit pull requests

## 📄 License

This project is licensed under the MIT License.

## 👤 Author

**Eliau Elkouby** - [@eliau2005](https://github.com/eliau2005)

---

<div align="center">
Made with ❤️ and AI
</div>
