#!/usr/bin/env python3
"""
Template XML Run Merger

Word often splits Jinja2 variables across multiple <w:t> tags:
  <w:t>{{ </w:t><w:t>variable</w:t><w:t> }}</w:t>

This script merges adjacent text runs to reassemble complete variables:
  <w:t>{{ variable }}</w:t>

This allows docxtpl to properly recognize and render the variables.
"""

import zipfile
import re
from pathlib import Path
import shutil
from xml.dom import minidom
import xml.etree.ElementTree as ET

# Define Word namespace
WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
W = WORD_NAMESPACE  # Shorthand


def merge_text_runs(xml_content):
    """
    Merge adjacent text runs that together form Jinja2 variables

    Strategy:
    1. Find all <w:r> (run) elements
    2. Extract text from <w:t> elements within runs
    3. Look for patterns where Jinja2 is split: "{{ " + "var" + " }}"
    4. Merge the <w:t> elements in those runs
    """

    try:
        # Parse XML
        root = ET.fromstring(xml_content.encode('utf-8'))

        # Register namespace to avoid ns0: prefixes
        ET.register_namespace('w', 'http://schemas.openxmlformats.org/wordprocessingml/2006/main')
        ET.register_namespace('r', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships')
        ET.register_namespace('wp', 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing')
        ET.register_namespace('a', 'http://schemas.openxmlformats.org/drawingml/2006/main')
        ET.register_namespace('pic', 'http://schemas.openxmlformats.org/drawingml/2006/picture')

        changes_made = 0

        # Find all runs
        for para in root.iter(f'{W}p'):  # Iterate paragraphs
            runs = list(para.findall(f'{W}r'))

            # For each run, check if it contains partial Jinja2 syntax
            for i, run in enumerate(runs):
                # Get all text elements in this run
                text_elements = run.findall(f'{W}t')

                if not text_elements:
                    continue

                # Collect text from this run
                run_text = ''.join(t.text or '' for t in text_elements)

                # Check if this run contains start of Jinja2 but not complete
                if '{{' in run_text or '{%' in run_text:
                    # Check if variable is incomplete (missing closing braces)
                    if ('{{' in run_text and '}}' not in run_text) or \
                       ('{%' in run_text and '%}' not in run_text):

                        # Try to merge with subsequent runs
                        j = i + 1
                        accumulated_text = run_text
                        runs_to_merge = [run]

                        while j < len(runs):
                            next_run = runs[j]
                            next_text_elements = next_run.findall(f'{W}t')
                            next_text = ''.join(t.text or '' for t in next_text_elements)

                            accumulated_text += next_text
                            runs_to_merge.append(next_run)

                            # Check if we now have a complete variable
                            if '}}' in accumulated_text or '%}' in accumulated_text:
                                # Merge successful!
                                # Remove old text elements from first run
                                for t in text_elements:
                                    run.remove(t)

                                # Create single merged text element
                                new_text = ET.SubElement(run, f'{W}t')
                                new_text.text = accumulated_text
                                # Preserve space attribute if needed
                                if accumulated_text.startswith(' ') or accumulated_text.endswith(' '):
                                    new_text.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')

                                # Remove the subsequent runs that were merged
                                for merged_run in runs_to_merge[1:]:
                                    para.remove(merged_run)

                                changes_made += 1
                                break

                            j += 1

                            # Safety: don't merge too many runs
                            if j - i > 10:
                                break

        # Convert back to string (without xml_declaration for compatibility)
        xml_bytes = ET.tostring(root, encoding='utf-8')
        xml_str = xml_bytes.decode('utf-8')

        return xml_str, changes_made

    except Exception as e:
        print(f"❌ Error merging runs: {e}")
        import traceback
        traceback.print_exc()
        return xml_content, 0


def fix_template(template_path, output_path=None):
    """Fix split Jinja2 variables in DOCX template"""

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
    print("TEMPLATE XML RUN MERGER")
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

                    # Only process main document XML
                    if item == 'word/document.xml':
                        try:
                            # Decode XML
                            xml_content = data.decode('utf-8')

                            # Merge split runs
                            fixed_content, changes = merge_text_runs(xml_content)

                            if changes > 0:
                                files_changed.append(item)
                                total_changes += changes

                                print(f"✅ Fixed {item}: {changes} variables merged")

                                # Write fixed content
                                zip_out.writestr(item, fixed_content.encode('utf-8'))
                            else:
                                # No changes, copy as-is
                                zip_out.writestr(item, data)

                        except Exception as e:
                            print(f"⚠️  Error processing {item}: {e}")
                            # Copy original on error
                            zip_out.writestr(item, data)
                    else:
                        # Other files, copy as-is
                        zip_out.writestr(item, data)

                print(f"\n{'='*80}")
                print("SUMMARY")
                print(f"{'='*80}\n")

                if total_changes > 0:
                    print(f"✅ Merged {total_changes} split variables in {len(files_changed)} file(s)")
                    print(f"\n✅ Fixed template saved: {output_path}")
                    print(f"\n⚠️  IMPORTANT: Test the fixed template in Word before using!")
                else:
                    print("ℹ️  No split variables found - template may already be clean")
                    print(f"   Output file created: {output_path}")

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
        return 1

    success = fix_template(template_path, output_path)

    if success:
        print(f"{'='*80}")
        print("\nNEXT STEPS:")
        print("1. Verify the fixed template opens correctly in Word")
        print("2. Update render.py to use the fixed template")
        print("3. Restart the backend server")
        print("4. Test rendering with actual data")
        print(f"{'='*80}\n")
        return 0
    else:
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
