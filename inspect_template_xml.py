#!/usr/bin/env python3
"""
Template XML Inspector

Shows the RAW XML content where Jinja2 variables are found.
This helps understand exactly how Word has encoded the template tags.
"""

import zipfile
import re
from pathlib import Path

def inspect_template_xml(template_path):
    """Inspect raw XML to see actual Jinja2 variable patterns"""

    template_path = Path(template_path)

    if not template_path.exists():
        print(f"❌ Template not found: {template_path}")
        return

    print(f"\n{'='*80}")
    print("TEMPLATE XML INSPECTOR")
    print(f"{'='*80}\n")
    print(f"Template: {template_path.name}\n")

    with zipfile.ZipFile(template_path, 'r') as zip_file:
        # Focus on main document
        xml_file = 'word/document.xml'

        print(f"📄 Inspecting: {xml_file}\n")

        try:
            xml_content = zip_file.read(xml_file).decode('utf-8')

            # Find all text segments that contain curly braces
            brace_pattern = r'<w:t[^>]*>([^<]*\{[^<]*)</w:t>'
            matches = re.findall(brace_pattern, xml_content)

            if matches:
                print(f"Found {len(matches)} text segments containing '{{' character:\n")

                # Group similar patterns
                from collections import Counter
                pattern_counts = Counter(matches)

                for i, (text, count) in enumerate(pattern_counts.most_common(20), 1):
                    print(f"{i:2}. [{count:2}x] {repr(text)}")

                if len(pattern_counts) > 20:
                    print(f"    ... and {len(pattern_counts) - 20} more unique patterns")

            print(f"\n{'='*80}")
            print("RAW XML CONTEXT (first few occurrences)")
            print(f"{'='*80}\n")

            # Show raw XML context around variables
            # Find patterns like {anything}
            context_pattern = r'(<w:r>.*?</w:r>)'
            runs = re.findall(context_pattern, xml_content, re.DOTALL)

            relevant_runs = [r for r in runs if '{' in r]

            for i, run in enumerate(relevant_runs[:5], 1):
                # Clean up for display
                display = run.replace('><', '>\n<')
                print(f"Run #{i}:")
                print(display)
                print('-' * 80)

            if len(relevant_runs) > 5:
                print(f"\n... and {len(relevant_runs) - 5} more runs with '{{' character")

            # Check for the specific pattern the user saw
            print(f"\n{'='*80}")
            print("CHECKING FOR SPECIFIC PATTERNS")
            print(f"{'='*80}\n")

            # Pattern 1: Simple single brace variables
            single_brace_vars = re.findall(r'\{\s*(\w+)\s*\}', xml_content)
            if single_brace_vars:
                unique_vars = set(single_brace_vars)
                print(f"✅ Found {len(single_brace_vars)} single-brace variables ({{ var }}):")
                for var in sorted(unique_vars)[:10]:
                    print(f"   • {var}")
                if len(unique_vars) > 10:
                    print(f"   ... and {len(unique_vars) - 10} more")
            else:
                print("❌ No single-brace variables found")

            # Pattern 2: Double brace variables
            double_brace_vars = re.findall(r'\{\{\s*(\w+)\s*\}\}', xml_content)
            if double_brace_vars:
                unique_vars = set(double_brace_vars)
                print(f"\n✅ Found {len(double_brace_vars)} double-brace variables ({{{{ var }}}}):")
                for var in sorted(unique_vars)[:10]:
                    print(f"   • {var}")
                if len(unique_vars) > 10:
                    print(f"   ... and {len(unique_vars) - 10} more")
            else:
                print("\n❌ No double-brace variables found")

            # Pattern 3: Malformed - extra space between braces
            split_pattern1 = r'\{\s\{([^}]+)\}\s\}'
            split_vars1 = re.findall(split_pattern1, xml_content)
            if split_vars1:
                print(f"\n⚠️  Found SPLIT PATTERN: '{{ {{ var }} }}' (extra spaces):")
                for var in split_vars1[:10]:
                    print(f"   • {var}")

            # Pattern 4: Missing opening brace
            split_pattern2 = r'(?<!\{)\{\s*\{\s*(\w+)\s*\}\s*\}(?!\})'
            split_vars2 = re.findall(split_pattern2, xml_content)
            if split_vars2:
                print(f"\n⚠️  Found MALFORMED: '{{ {{ var }}' (double open, double close):")
                for var in split_vars2[:10]:
                    print(f"   • {var}")

        except Exception as e:
            print(f"❌ Error reading XML: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'='*80}\n")


def main():
    template_path = "backend/templates/d0d00cd7-54a4-4925-a5bd-6965624e82b8_temp_dutch_coc_template.docx"

    if not Path(template_path).exists():
        print(f"❌ Template not found: {template_path}")
        return 1

    inspect_template_xml(template_path)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
