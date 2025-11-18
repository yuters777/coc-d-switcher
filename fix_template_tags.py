#!/usr/bin/env python3
"""
Template Tag Fixer

Merges split Jinja2 tags in DOCX templates.
Word often breaks tags like { variable } into { { variable } when editing.
This script fixes those splits so docxtpl can recognize the variables.
"""

import zipfile
import re
from pathlib import Path
import shutil
from xml.dom import minidom

def fix_split_jinja_tags(xml_content):
    """
    Fix split Jinja2 tags in XML content

    Patterns to fix:
    - { { variable } } -> { variable }
    - {{ {{ variable }} }} -> {{ variable }}
    - {% {% for ... %} %} -> {% for ... %}
    """

    original_content = xml_content

    # Fix single brace variables split by extra spaces/tags
    # Pattern: { { anything } } -> { anything }
    xml_content = re.sub(r'\{\s+\{', '{', xml_content)
    xml_content = re.sub(r'\}\s+\}', '}', xml_content)

    # Fix double brace variables
    # Pattern: {{ {{ anything }} }} -> {{ anything }}
    xml_content = re.sub(r'\{\{\s+\{\{', '{{', xml_content)
    xml_content = re.sub(r'\}\}\s+\}\}', '}}', xml_content)

    # Fix Jinja2 control structures
    # Pattern: {% {% for ... %} %} -> {% for ... %}
    xml_content = re.sub(r'\{%\s+\{%', '{%', xml_content)
    xml_content = re.sub(r'%\}\s+%\}', '%}', xml_content)

    # Count changes
    changes = sum(1 for a, b in zip(original_content, xml_content) if a != b)

    return xml_content, changes > 0


def fix_template(template_path, output_path=None):
    """
    Fix split Jinja2 tags in a DOCX template

    Args:
        template_path: Path to the template file
        output_path: Path for the fixed template (default: adds '_fixed' suffix)
    """

    template_path = Path(template_path)

    if not template_path.exists():
        print(f"❌ Template not found: {template_path}")
        return False

    # Default output path
    if output_path is None:
        output_path = template_path.parent / f"{template_path.stem}_fixed{template_path.suffix}"
    else:
        output_path = Path(output_path)

    print(f"\n{'='*80}")
    print("TEMPLATE TAG FIXER")
    print(f"{'='*80}\n")
    print(f"Input:  {template_path}")
    print(f"Output: {output_path}\n")

    # Create backup
    backup_path = template_path.parent / f"{template_path.stem}_backup{template_path.suffix}"
    if not backup_path.exists():
        shutil.copy2(template_path, backup_path)
        print(f"✅ Backup created: {backup_path}\n")

    try:
        # Read the DOCX as a ZIP
        with zipfile.ZipFile(template_path, 'r') as zip_in:
            # Create output ZIP
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_out:

                total_changes = 0
                files_changed = []

                # Process each file in the ZIP
                for item in zip_in.namelist():
                    data = zip_in.read(item)

                    # Only process XML files
                    if item.endswith('.xml'):
                        try:
                            # Decode XML
                            xml_content = data.decode('utf-8')

                            # Fix split tags
                            fixed_content, changed = fix_split_jinja_tags(xml_content)

                            if changed:
                                files_changed.append(item)
                                # Count how many tags were fixed
                                original_vars = len(re.findall(r'\{\s+\{|\}\s+\}', xml_content))
                                total_changes += original_vars

                                print(f"✅ Fixed {item}: {original_vars} split tags merged")

                                # Write fixed content
                                zip_out.writestr(item, fixed_content.encode('utf-8'))
                            else:
                                # No changes, copy as-is
                                zip_out.writestr(item, data)

                        except UnicodeDecodeError:
                            # Binary XML, copy as-is
                            zip_out.writestr(item, data)
                    else:
                        # Non-XML files, copy as-is
                        zip_out.writestr(item, data)

                print(f"\n{'='*80}")
                print("SUMMARY")
                print(f"{'='*80}\n")

                if files_changed:
                    print(f"✅ Fixed {total_changes} split tags in {len(files_changed)} files:")
                    for f in files_changed:
                        print(f"   • {f}")
                    print(f"\n✅ Fixed template saved: {output_path}")
                    print(f"\n⚠️  IMPORTANT: Test the fixed template before using in production!")
                else:
                    print("ℹ️  No split tags found - template is already clean")
                    print(f"   Output file created anyway: {output_path}")

                print()
                return True

    except Exception as e:
        print(f"\n❌ Error processing template: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function"""

    # Template path
    template_path = "backend/templates/d0d00cd7-54a4-4925-a5bd-6965624e82b8_temp_dutch_coc_template.docx"
    output_path = "backend/templates/d0d00cd7-54a4-4925-a5bd-6965624e82b8_temp_dutch_coc_template_fixed.docx"

    if not Path(template_path).exists():
        print(f"\n❌ Template not found: {template_path}")
        print("\nPlease ensure the template exists at the correct location.")
        print("You can also pass the template path as a command-line argument:")
        print(f"  python {Path(__file__).name} <template_path> [output_path]")
        return 1

    success = fix_template(template_path, output_path)

    if success:
        print(f"{'='*80}")
        print("\nNEXT STEPS:")
        print("1. Update render.py to use the fixed template")
        print("2. Restart the backend server")
        print("3. Test rendering with actual data")
        print(f"{'='*80}\n")
        return 0
    else:
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
