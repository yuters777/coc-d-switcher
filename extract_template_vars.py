#!/usr/bin/env python3
"""
Template Variable Extraction Script
Extracts all Jinja2 variables from the DOCX template to understand what it expects
"""

import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

def extract_jinja_variables_from_docx(docx_path):
    """
    Extract all Jinja2 variables from a DOCX template

    DOCX files are ZIP archives containing XML files.
    Jinja2 variables like {{ variable_name }} are stored in the XML.
    """

    variables = set()
    loops = set()
    conditionals = set()

    print(f"\n📂 Analyzing template: {Path(docx_path).name}\n")

    try:
        # Open DOCX as ZIP
        with zipfile.ZipFile(docx_path, 'r') as docx_zip:
            # Search ALL XML files in the DOCX archive
            all_files = docx_zip.namelist()
            xml_files = [f for f in all_files if f.endswith('.xml')]

            print(f"📁 Searching {len(xml_files)} XML files in template:\n")
            for xml_file in xml_files[:10]:  # Show first 10
                print(f"  • {xml_file}")
            if len(xml_files) > 10:
                print(f"  ... and {len(xml_files) - 10} more")
            print()

            for xml_file in xml_files:
                try:
                    xml_content = docx_zip.read(xml_file).decode('utf-8')

                    # Find all {{ variable }} AND { variable } patterns (both syntaxes)
                    var_pattern_double = r'\{\{\s*([^}]+?)\s*\}\}'
                    var_pattern_single = r'\{\s*([^}]+?)\s*\}'

                    matches_double = re.findall(var_pattern_double, xml_content)
                    matches_single = re.findall(var_pattern_single, xml_content)

                    for match in matches_double + matches_single:
                        var_name = match.strip()
                        # Skip XML tags, Word internal tags, and common XML patterns
                        if (var_name.startswith('#') or var_name.startswith('w:') or
                            var_name.startswith('/') or '<' in var_name or '>' in var_name):
                            continue

                        # Extract base variable name (without filters)
                        if '|' in var_name:
                            base_var = var_name.split('|')[0].strip()
                            variables.add(base_var)
                        else:
                            variables.add(var_name)

                    # Find all {% for %} loops
                    loop_pattern = r'\{%\s*for\s+(\w+)\s+in\s+([^%]+?)\s*%\}'
                    loop_matches = re.findall(loop_pattern, xml_content, re.IGNORECASE)
                    for item_var, collection_var in loop_matches:
                        loops.add(f"{item_var} in {collection_var.strip()}")

                    # Find docxtpl table row loops: {%tr for item in items %}
                    tr_loop_pattern = r'\{%tr\s+for\s+(\w+)\s+in\s+([^%]+?)\s*%\}'
                    tr_matches = re.findall(tr_loop_pattern, xml_content, re.IGNORECASE)
                    for item_var, collection_var in tr_matches:
                        loops.add(f"TR_LOOP: {item_var} in {collection_var.strip()}")

                    # Find docxtpl table cell loops: {%tc for item in items %}
                    tc_loop_pattern = r'\{%tc\s+for\s+(\w+)\s+in\s+([^%]+?)\s*%\}'
                    tc_matches = re.findall(tc_loop_pattern, xml_content, re.IGNORECASE)
                    for item_var, collection_var in tc_matches:
                        loops.add(f"TC_LOOP: {item_var} in {collection_var.strip()}")

                    # Find all {% if %} conditionals
                    if_pattern = r'\{%\s*if\s+([^%]+?)\s*%\}'
                    if_matches = re.findall(if_pattern, xml_content, re.IGNORECASE)
                    for condition in if_matches:
                        conditionals.add(condition.strip())

                    # Report findings per file
                    total_findings = len(matches_double) + len(matches_single) + len(loop_matches) + len(tr_matches) + len(tc_matches) + len(if_matches)
                    if total_findings > 0:
                        print(f"✅ {xml_file}: {total_findings} Jinja2 patterns found")

                except KeyError:
                    pass
                except (UnicodeDecodeError, Exception) as e:
                    # Silently skip binary files or decode errors
                    pass

        return {
            "variables": sorted(variables),
            "loops": sorted(loops),
            "conditionals": sorted(conditionals)
        }

    except Exception as e:
        print(f"❌ Error processing template: {e}")
        return None


def analyze_variable_structure(variables):
    """Analyze the structure of variables (nested vs flat)"""

    flat_vars = []
    nested_vars = {}

    for var in variables:
        if '.' in var:
            # Nested variable like PI.ContractNumber
            parts = var.split('.')
            parent = parts[0]
            child = '.'.join(parts[1:])

            if parent not in nested_vars:
                nested_vars[parent] = []
            nested_vars[parent].append(child)
        else:
            flat_vars.append(var)

    return {
        "flat": flat_vars,
        "nested": nested_vars
    }


def print_template_analysis(result):
    """Pretty print the template analysis"""

    if not result:
        return

    variables = result["variables"]
    loops = result["loops"]
    conditionals = result["conditionals"]

    print("\n" + "="*80)
    print("TEMPLATE VARIABLE ANALYSIS")
    print("="*80)

    if variables:
        print(f"\n📝 VARIABLES FOUND ({len(variables)} total):")

        structure = analyze_variable_structure(variables)

        if structure["flat"]:
            print(f"\n  Flat Variables ({len(structure['flat'])}):")
            for var in structure["flat"]:
                print(f"    • {{ {var} }}")

        if structure["nested"]:
            print(f"\n  Nested Variables ({sum(len(v) for v in structure['nested'].values())} total):")
            for parent, children in structure["nested"].items():
                print(f"\n    {parent}:")
                for child in children:
                    print(f"      • {{ {parent}.{child} }}")
    else:
        print("\n⚠️  NO JINJA2 VARIABLES FOUND!")
        print("    This might mean:")
        print("    1. Variables are split across XML tags (common in DOCX)")
        print("    2. Template uses a different syntax")
        print("    3. Template has no dynamic variables")

    if loops:
        print(f"\n🔄 FOR LOOPS FOUND ({len(loops)} total):")
        for loop in loops:
            if loop.startswith("TR_LOOP:"):
                print(f"    • {{%tr for {loop.replace('TR_LOOP: ', '')} %}}  [Table Row Loop]")
            elif loop.startswith("TC_LOOP:"):
                print(f"    • {{%tc for {loop.replace('TC_LOOP: ', '')} %}}  [Table Cell Loop]")
            else:
                print(f"    • {{% for {loop} %}}")
    else:
        print(f"\n⚠️  NO LOOPS FOUND!")
        print("    If serial numbers should appear, check:")
        print("    1. Template might have static serial number fields (unlikely for 100+)")
        print("    2. Template might be corrupted or variables split by Word")
        print("    3. Serial numbers might be in a different structure")

    if conditionals:
        print(f"\n🔀 CONDITIONALS FOUND ({len(conditionals)} total):")
        for cond in conditionals:
            print(f"    • {{% if {cond} %}}")

    print("\n" + "="*80)


def compare_with_our_context():
    """Show what we're providing vs what template expects"""

    print("\n" + "*"*80)
    print("COMPARISON: Template Expects vs What We Provide")
    print("*"*80)

    print("\n📤 WHAT WE PROVIDE (from render.py):")
    print("\n  Flat variables:")
    our_vars = [
        "contract_number", "shipment_no", "product_description", "quantity",
        "supplier_serial_no", "manufacturing_date", "delivery_date", "invoice_no",
        "invoice_date", "final_delivery_number", "date", "delivery_address",
        "acquirer", "serials", "serial_count", "qa_signer",
        "partial_delivery_number", "undelivered_quantity", "sw_version", "remarks"
    ]
    for var in our_vars:
        print(f"    • {var}")

    print("\n  Nested structure (PI object):")
    pi_vars = [
        "ContractNumber", "ShipmentNo", "ProductDescription", "Quantity",
        "SupplierSerialNo", "DeliveryAddress", "Acquirer", "Date",
        "Serials", "SerialCount", "QASigner", "PartialDeliveryNumber",
        "UndeliveredQuantity", "SWVersion", "Remarks"
    ]
    for var in pi_vars:
        print(f"    • PI.{var}")


def main():
    """Main function"""

    # Template path - using actual template filename
    template_path = "backend/templates/d0d00cd7-54a4-4925-a5bd-6965624e82b8_temp_dutch_coc_template.docx"

    print("="*80)
    print("DOCX TEMPLATE VARIABLE EXTRACTOR")
    print("="*80)

    if not Path(template_path).exists():
        print(f"\n❌ Template not found: {template_path}")
        print("\nPlease ensure the template exists at the correct location.")
        return 1

    # Extract variables
    result = extract_jinja_variables_from_docx(template_path)

    if result:
        # Print analysis
        print_template_analysis(result)

        # Compare with what we provide
        compare_with_our_context()

        # Recommendations
        print("\n" + "="*80)
        print("RECOMMENDATIONS")
        print("="*80)

        if not result["variables"]:
            print("\n⚠️  CRITICAL ISSUE: No Jinja2 variables found!")
            print("\nThis likely means variables are SPLIT across XML tags.")
            print("Word does this when you edit the document.")
            print("\nSOLUTION: Use the template fix script to merge split tags:")
            print("  1. Check if merge_split_jinja_tags.py exists")
            print("  2. Run it on the template to fix split variables")
            print("  3. Re-run this analysis to verify")
        else:
            print("\n✅ Template has Jinja2 variables")
            print("\nNext steps:")
            print("  1. Compare template variables with what we provide")
            print("  2. Update render.py to match exact variable names")
            print("  3. Test rendering with actual data")

        # Save to file
        output_file = "template_variables.txt"
        with open(output_file, 'w') as f:
            f.write("TEMPLATE VARIABLES\n")
            f.write("="*80 + "\n\n")

            f.write("Variables:\n")
            for var in result["variables"]:
                f.write(f"  {{ {var} }}\n")

            f.write("\nLoops:\n")
            for loop in result["loops"]:
                f.write(f"  {{% for {loop} %}}\n")

            f.write("\nConditionals:\n")
            for cond in result["conditionals"]:
                f.write(f"  {{% if {cond} %}}\n")

        print(f"\n📄 Results also saved to: {output_file}")

    print("\n" + "="*80)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
