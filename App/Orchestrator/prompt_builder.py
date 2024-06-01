import os
import re

class PromptBuilder:
    def __init__(self):
        self.prompts = {}
        self._scan_directory()

    def _scan_directory(self):
        """Scan the 'prompts' directory for .md files and load them into the prompts dictionary."""
        current_dir = os.path.dirname(__file__)
        prompts_dir = os.path.join(current_dir, 'prompts')
        for filename in os.listdir(prompts_dir):
            if filename.endswith('.md'):
                filepath = os.path.join(prompts_dir, filename)
                # Remove the .md extension
                name_without_extension = os.path.splitext(filename)[0].lower()
                with open(filepath, 'r') as file:
                    self.prompts[name_without_extension] = file.read()

    def _substitute_template(self, text, template_values):
        """Recursively substitute templates in the given text."""
        # Create a pattern that matches any of the keys in uppercase format
        keys_pattern = re.compile(r'\b(' + '|'.join(re.escape(key.upper()) for key in template_values.keys()) + r'|' + '|'.join(re.escape(key.upper()) for key in self.prompts.keys()) + r')\b')

        while True:
            # Find all matches for the current keys pattern
            matches = keys_pattern.findall(text)
            if not matches:
                break

            for match in matches:
                key = match.lower()
                if key in template_values:
                    replacement_value = template_values[key]
                elif key in self.prompts:
                    replacement_value = self._substitute_template(self.prompts[key], template_values)
                else:
                    replacement_value = match  # No substitution found, keep original

                text = text.replace(match, replacement_value)

        return text

    def get(self, name, template_values):
        template_values = {key.lower(): value for key, value in template_values.items()}
        """Get the content of the specified prompt with template substitution."""
        lower_name = name.lower()
        if lower_name not in self.prompts:
            raise ValueError(f"Prompt '{name}' not found in prompts directory.")
        
        initial_content = self.prompts[lower_name]
        return self._substitute_template(initial_content, template_values)

if __name__ == "__main__":
    prompt = Prompt()
    output = prompt.get('x', {'USER_QUERY': 'my query is here', 'ANOTHER_TEMPLATE': 'another value'})
    print(output)
