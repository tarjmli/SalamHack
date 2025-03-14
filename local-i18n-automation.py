import os
import json
import re
import argparse
from typing import Dict, Tuple, List, Any, Optional
import asyncio
import aiofiles

from langchain_groq import ChatGroq
from langchain.schema import HumanMessage

class I18nExtractor:
    def __init__(self, api_key: str, model_name: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key
        self.model_name = model_name
        self.chat = ChatGroq(
            groq_api_key=api_key,
            model_name=model_name
        )

    # Extract translatable strings and update code using LLM
    async def process_file(self, file_path: str, framework: str = "React") -> Tuple[str, Dict[str, str]]:
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                code = await f.read()
            
            print(f"Processing {file_path} ({len(code)} characters)")
            
            extraction_prompt = f"""
                        You are an internationalization assistant for a {framework} project.
                        Extract all user-facing text such as headers, titles, button text, paragraphs... from the following code and replace them with t('key') from {'react-i18next' if framework == 'React' else 'next-i18next'}, 
                        and return **only** the modified code along with the JSON mapping.

                        **Modify only:**  
                        - Plain text inside JSX elements (`<h1>`, `<p>`, `<button>`, `<span>`, etc.).
                        - `alt` attributes in `<img>` tags.
                        - `aria-label` attributes in accessible elements.

                        **Do NOT modify:**  
                        - Custom components or their props and arguments, for example: <PricingCard type={"Free"} price={0} />, **DO NOT EDIT ANY OF THOSE WHATSOEVER AND DO NOT ADD BRACKETS!**.
                        - Dynamic expressions (e.g., `{'`someVariable`'}`).
                        - JavaScript logic inside JSX such as if-else statements.
                        - CSS classes, IDs, or non-text properties.

                        Here is the code to process:
                        
                        {code}


                        Return your response in the following JSON format:

                        {{
                        "updated_code": "modified code here",
                        "i18n_json": {{
                            "key1": "value1",
                            "key2": "value2"
                        }}
                        }}
                        where key is the key we use in t() in the code and value is the text that we extracted from the code.
                        Do not include any explanations, just the JSON object.
                        """

            response = await self.invoke_model(extraction_prompt)
            json_data = self.extract_valid_json(response)

            if json_data and "updated_code" in json_data and "i18n_json" in json_data:
                updated_code, i18n_json = json_data["updated_code"], json_data["i18n_json"]

                # ✅ WRITE THE UPDATED CODE BACK TO THE FILE
                async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                    await f.write(updated_code)

                return updated_code, i18n_json
            else:
                print("Model response is not valid JSON. Returning original code.")
                return code, {"error": "Model response is not valid JSON"}

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            return code, {"error": str(e)}


    # Translate extracted strings to target language
    async def translate_strings(self, strings: Dict[str, str], language: str) -> Dict[str, str]:
        translation_prompt = f"""
        You are a translation assistant. Translate the following JSON key-value pairs into {language}.
        Return only the translated JSON in the exact same format as the input. Do not add any extra text or explanations.
        Ensure your response is valid JSON that can be parsed with JSON.parse() or equivalent.

        Input JSON:
        {json.dumps(strings, indent=2, ensure_ascii=False)}

        Translated JSON (valid JSON only):
        """
        
        print(f"Translating to {language}...")
        response = await self.invoke_model(translation_prompt)
        translated_json = self.extract_valid_json(response)
        
        if translated_json:
            return translated_json
        else:
            print(f"Could not extract valid JSON from {language} translation response.")
            return {"error": f"Failed to translate to {language}"}

    # Helper method to invoke the model
    async def invoke_model(self, prompt: str) -> str:
        try:
            response = self.chat.invoke([HumanMessage(content=prompt)])
            return response.content.strip()
        except Exception as e:
            print(f"Error invoking model: {e}")
            raise

    # Extract valid JSON from model response
    def extract_valid_json(self, response_content: str) -> Optional[Dict[str, Any]]:
        # First try to directly extract JSON
        try:
            json_match = re.search(r'({[\s\S]*})', response_content)
            if json_match:
                potential_json = json_match.group(1)
                return json.loads(potential_json)
            elif response_content.startswith("{") and response_content.endswith("}"):
                return json.loads(response_content)
        except json.JSONDecodeError:
            pass
        
        # If direct extraction fails, use a secondary model prompt
        try:
            json_extraction_prompt = f"""
            Extract only the valid JSON object from the following text. Return only the JSON object with no additional text.
            If there are multiple JSON objects, extract the one that appears to contain i18n translations (key-value pairs of strings).

            Input:
            {response_content}

            Output (valid JSON only):
            """
            
            json_extraction_response = self.chat.invoke([HumanMessage(content=json_extraction_prompt)])
            json_text = json_extraction_response.content.strip()
            
            json_match = re.search(r'({[\s\S]*})', json_text)
            if json_match:
                potential_json = json_match.group(1)
                return json.loads(potential_json)
            else:
                return json.loads(json_text)
        except Exception as e:
            print(f"Error extracting valid JSON: {e}")
            return None

    # Generate i18n configuration file
    def generate_i18n_config(self, languages: List[str], framework: str = "React") -> str:
        if framework == "Next":
            return self._generate_next_i18n_config(languages)
        else:
            return self._generate_react_i18n_config(languages)
    
    def _generate_react_i18n_config(self, languages: List[str]) -> str:
        imports = '\n'.join([
            f'import {lang}Translation from "./locales/{lang}.json";'
            for lang in languages
        ])
        
        resources = ',\n'.join([
            f'    {lang}: {{ translation: {lang}Translation }}'
            for lang in languages
        ])
        
        return f"""import i18n from "i18next";
import {{ initReactI18next }} from "react-i18next";
{imports}

i18n
  .use(initReactI18next)
  .init({{
    resources: {{
{resources}
    }},
    lng: "en", // Default language
    fallbackLng: "en",
    interpolation: {{
      escapeValue: false
    }}
  }});

export default i18n;"""

    def _generate_next_i18n_config(self, languages: List[str]) -> str:
        return f"""// next-i18next.config.js
module.exports = {{
  i18n: {{
    defaultLocale: 'en',
    locales: {json.dumps(languages)},
  }},
}};
"""

# Main function to process files and generate translations
async def process_components(
    api_key: str, 
    component_dir: str, 
    output_dir: str = None,
    framework: str = "React",
    languages: List[str] = ["en", "ar", "fr"],
    file_extensions: List[str] = [".jsx", ".tsx", ".js", ".ts"]
):
    if output_dir is None:
        output_dir = os.path.join(component_dir, "i18n_output")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    locales_dir = os.path.join(output_dir, "locales")
    os.makedirs(locales_dir, exist_ok=True)
    
    # Initialize extractor
    extractor = I18nExtractor(api_key=api_key)
    
    # Find all component files
    component_files = []
    for root, _, files in os.walk(component_dir):
        for file in files:
            if any(file.endswith(ext) for ext in file_extensions):
                component_files.append(os.path.join(root, file))
    
    if not component_files:
        print(f"No {', '.join(file_extensions)} files found in {component_dir}")
        return
    
    print(f"Found {len(component_files)} component files")
    
    # Process each file to extract strings
    all_strings = {}
    for file_path in component_files:
        print(f"\nProcessing {os.path.basename(file_path)}...")
        updated_code, extracted_strings = await extractor.process_file(file_path, framework)
        
        if "error" not in extracted_strings:
            # Save updated component
            rel_path = os.path.relpath(file_path, component_dir)
            output_file_path = os.path.join(output_dir, rel_path)
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
            
            async with aiofiles.open(output_file_path, 'w', encoding='utf-8') as f:
                await f.write(updated_code)
            print(f"Updated component saved to {output_file_path}")
            
            # Merge extracted strings
            all_strings.update(extracted_strings)
    
    if not all_strings:
        print("No translatable strings were extracted.")
        return
    
    print(f"\nExtracted {len(all_strings)} translatable strings")
    
    # Save English strings (source language)
    en_path = os.path.join(locales_dir, "en.json")
    async with aiofiles.open(en_path, 'w', encoding='utf-8') as f:
        await f.write(json.dumps(all_strings, indent=2, ensure_ascii=False))
    print(f"English strings saved to {en_path}")
    
    # Translate to other languages
    translations = {"en": all_strings}
    for lang in languages:
        if lang != "en":
            translated_strings = await extractor.translate_strings(all_strings, lang)
            if "error" not in translated_strings:
                translations[lang] = translated_strings
                
                # Save translated strings
                lang_path = os.path.join(locales_dir, f"{lang}.json")
                async with aiofiles.open(lang_path, 'w', encoding='utf-8') as f:
                    await f.write(json.dumps(translated_strings, indent=2, ensure_ascii=False))
                print(f"{lang.capitalize()} strings saved to {lang_path}")
    
    # Generate i18n configuration file
    config = extractor.generate_i18n_config(languages, framework)
    config_filename = "next-i18next.config.js" if framework == "Next" else "i18n.js"
    config_path = os.path.join(output_dir, config_filename)
    
    async with aiofiles.open(config_path, 'w', encoding='utf-8') as f:
        await f.write(config)
    print(f"\ni18n configuration saved to {config_path}")
    
    print("\nI18n processing complete!")
    print(f"All output files are in: {output_dir}")

# Command line interface
async def main():
    api_key ="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"
    component_dir = "components"
    output_dir = "path_to_output_directory"
    framework = "React" 
    languages = ["en", "ar", "fr"]
    extensions = [".jsx", ".tsx", ".js", ".ts"]
    
    await process_components(
        api_key=api_key,
        component_dir=component_dir,
        output_dir=output_dir,
        framework=framework,
        languages=languages,
        file_extensions=extensions
    )

if __name__ == "__main__":
    asyncio.run(main())