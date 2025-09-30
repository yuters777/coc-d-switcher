import json
from pathlib import Path

def load_config() -> dict:
    """Load configuration"""
    default_config = {
        "supplier_block": {
            "name": "Elbit Systems C4I and Cyber Ltd",
            "address": "2 Hamachshev, Netanya, Israel",
            "contact": "Ido Shilo",
            "email": "Ido.Shilo@elbitsystems.com"
        },
        "contract_mod_text": [
            "AMENDMENT 15-12-2020 VOSS additional order call off solution and deliveries 11-12-2020",
            "10-01-2022 Amendment to the Agreement TCP 187, TCP 192, TCP 193 DMO signed",
            "Approved TCP's list"
        ],
        "deviations_text": [
            "See remarks in Box 14.",
            "ELB_VOS_POR001",
            "ELB_VOS_CE0003",
            "ELB_VOS_SEC001",
            "ELB_VOS_CE0004"
        ],
        "gqar_defaults": {
            "name": "R. Kompier",
            "phone": "+31 620415178",
            "email": "R.Kompier@mindef.nl",
            "statement": ""
        },
        "signers": {
            "qa_manager": "Ronen Shamir, SmartVest QA Manager",
            "signature_mark": "QM.Elbit"
        },
        "delivery_id": "Del165",
        "output_filename_pattern": "COC_SV_{DeliveryID}_{DD.MM.YYYY}.docx"
    }

    config_path = Path("config.json")
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)

    return default_config
