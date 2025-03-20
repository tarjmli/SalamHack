# i18n Automation Tool

This repository contains a set of Python tools that leverage generative AI to automate the internationalization (i18n) process for React and Next.js applications.

## Overview

The i18n Automation Tool includes two main components:

1. **I18nextProvider Integration** - Automatically integrates the I18nextProvider into your main application entry point
2. **Localization String Extraction** - Uses AI to extract text strings from your components and generates translations

Both tools utilize the Groq API and Llama 3.3 (70B) model to intelligently process your code, making the internationalization process significantly faster and less error-prone.

## Features

- 🔍 **Intelligent Text Detection** - Identifies user-facing text in components
- 🔄 **Automatic Code Transformation** - Replaces hardcoded text with `t()` function calls
- 🌐 **Multi-language Translation** - Generates translations for extracted strings
- 📁 **JSON Resource Creation** - Creates language resource files in the correct format
- ⚙️ **i18n Configuration Generation** - Sets up the necessary i18n configuration files
- 🛠️ **Main File Integration** - Adds I18nextProvider to your application's main entry point

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/i18n-automation-tool.git
cd i18n-automation-tool

# Install dependencies
pip install langchain-groq aiofiles
```

## Usage

### I18nextProvider Integration

This script finds your main application file and wraps your `<App />` component with the `I18nextProvider`:

```bash
python I18nextProvider.py
```

### Full i18n Automation

This script processes all component files in a directory, extracts strings, generates translations, and creates i18n configuration:

```bash
python local-i18n-automation.py
```

By default, it will:

1. Process `.jsx`, `.tsx`, `.js`, and `.ts` files in the "components" directory
2. Generate translations for English, German, and French
3. Create a complete i18n setup in the output directory

## How It Works

### AI-Powered Internationalization

This tool uses generative AI (Llama 3.3 70B via Groq) to:

1. **Analyze your code structure** to identify the main application entry point
2. **Extract user-facing strings** from your components
3. **Replace hardcoded text** with i18n function calls
4. **Generate accurate translations** based on context
5. **Fix any syntax issues** that might arise during the transformation

The AI models understand both the structure of React/Next.js components and the semantics of the content, resulting in high-quality translations that maintain the original meaning.

### Technical Implementation

- **Asynchronous Processing**: Uses `asyncio` and `aiofiles` for efficient file operations
- **Intelligent JSON Extraction**: Multiple fallback methods to ensure valid JSON parsing
- **Syntax Validation**: Validates and corrects syntax after code transformation
- **Error Handling**: Robust retry mechanisms and error handling

## Example Workflow

1. Original component with hardcoded text:

   ```jsx
   function Welcome() {
     return <h1>Welcome to our application!</h1>;
   }
   ```

2. Transformed component with i18n:

   ```jsx
   import { useTranslation } from "react-i18next";

   function Welcome() {
     const { t } = useTranslation();
     return <h1>{t("welcomeMessage")}</h1>;
   }
   ```

3. Generated language files:

   ```json
   // en.json
   {
     "welcomeMessage": "Welcome to our application!"
   }

   // fr.json
   {
     "welcomeMessage": "Bienvenue dans notre application !"
   }
   ```

## Requirements

- Python 3.7+
- Groq API key
- React or Next.js project

## License

MIT

## Acknowledgements

This tool uses the Groq API and Llama 3.3 70B model for AI-powered code transformation and translation.
