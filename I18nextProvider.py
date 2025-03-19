import os
import re
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage

i18n_imports = """import { I18nextProvider } from "react-i18next";
import i18n from "./i18n";"""

EXCLUDED_DIRS = {"node_modules", ".next", "dist", "build", "out"}  # Ignore these directories

class SyntaxFixer:
    API_KEY = "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"  

    def __init__(self, model_name="llama-3.3-70b-versatile"):
        self.chat = ChatGroq(
            groq_api_key=self.API_KEY,
            model_name=model_name
        )

    def fix_syntax(self, code: str) -> str:
        """Uses AI to check & fix syntax errors in JavaScript/TypeScript code."""
        prompt = f"""
        You are an expert JavaScript and TypeScript developer.
        The following code has been modified to include i18n support, but it may contain syntax errors.
        Your task is to:
        - Check for syntax errors.
        - If there are errors, correct them while preserving the intended functionality.
        - If there are no errors, return the code as is.
        
        important: Do NOT add any unnecessary text, comments, or language annotations like javascript;.
        ### Code:
        ```js
        {code}
        ```
        
        RESPONSE FORMAT:
        Return only the corrected code inside ```js ... ``` without extra explanations.
        """

        try:
            response = self.chat.invoke([HumanMessage(content=prompt)])
            return self.extract_code(response.content.strip())
        except Exception as e:
            print(f"AI Syntax Check Failed: {e}")
            return code  # Return original code if AI fails

    def extract_code(self, response: str) -> str:
        """Extracts the corrected JavaScript/TypeScript code from AI response."""
        return re.sub(r'```(?:js)?|```', '', response).strip()

def find_main_file(directory="."):
    """Recursively searches for a file containing <App /> to identify the main entry file."""
    candidates = []
    
    for root, _, files in os.walk(directory):
        if any(excluded in root for excluded in EXCLUDED_DIRS):
            continue  # Skip excluded directories

        for file in files:
            if file.endswith((".js", ".jsx", ".ts", ".tsx")):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if "<App />" in content:
                        candidates.append(file_path)
    
    # Prioritize known entry filenames
    for filename in ["index.js", "main.js", "index.tsx", "main.tsx"]:
        for candidate in candidates:
            if candidate.endswith(filename):
                return candidate
    
    return candidates[0] if candidates else None

def modify_main_file():
    """Finds and modifies the main entry file to include i18n imports and wrap <App /> correctly without extra spacing."""
    main_file = find_main_file()
    
    if not main_file:
        print("Error: No main entry file found!")
        return
    
    with open(main_file, "r", encoding="utf-8") as file:
        content = file.read()

    # Add imports if not present
    if 'i18next' not in content:
        content = i18n_imports + "\n\n" + content

    
    content = re.sub(
        r"(\s*)(<App\s*/>)", 
        r"\1<I18nextProvider i18n={i18n}>\n\1  \2\n\1</I18nextProvider>",
        content
    )

   
    content = re.sub(r'(<I18nextProvider[^>]*>\n)\s*\n', r'\1', content)
    content = re.sub(r'\n\s*(</I18nextProvider>)', r'\1', content)

    
    fixer = SyntaxFixer()
    corrected_code = fixer.fix_syntax(content)

    with open(main_file, "w", encoding="utf-8") as file:
        file.write(corrected_code + "\n")  
    
    print(f"Modified & Syntax-Checked: {main_file}")

if __name__ == "__main__":
    modify_main_file()
