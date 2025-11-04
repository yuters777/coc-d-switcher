# backend/app/templates.py
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import json
import shutil
import logging

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path("templates")
TEMPLATES_DIR.mkdir(exist_ok=True)

TEMPLATE_METADATA_FILE = TEMPLATES_DIR / "metadata.json"

def load_metadata() -> Dict:
    """Load template metadata from disk with error handling"""
    try:
        if TEMPLATE_METADATA_FILE.exists():
            content = TEMPLATE_METADATA_FILE.read_text()
            # Validate JSON before parsing
            if not content.strip():
                logger.warning("Metadata file is empty, returning default")
                return {"templates": []}

            try:
                metadata = json.loads(content)
                # Validate structure
                if not isinstance(metadata, dict):
                    logger.error("Metadata is not a dict, resetting to default")
                    return {"templates": []}
                if "templates" not in metadata:
                    logger.warning("Metadata missing 'templates' key, adding it")
                    metadata["templates"] = []
                return metadata
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in metadata file: {str(e)}")
                # Backup corrupted file
                backup_path = TEMPLATE_METADATA_FILE.with_suffix('.json.backup')
                shutil.copy(TEMPLATE_METADATA_FILE, backup_path)
                logger.info(f"Backed up corrupted metadata to {backup_path}")
                return {"templates": []}
        return {"templates": []}
    except Exception as e:
        logger.error(f"Error loading metadata: {str(e)}")
        return {"templates": []}

def save_metadata(metadata: Dict):
    """Save template metadata to disk with error handling"""
    try:
        # Validate metadata structure before saving
        if not isinstance(metadata, dict):
            raise ValueError("Metadata must be a dictionary")
        if "templates" not in metadata:
            raise ValueError("Metadata must contain 'templates' key")
        if not isinstance(metadata["templates"], list):
            raise ValueError("'templates' must be a list")

        # Write with proper error handling
        TEMPLATE_METADATA_FILE.write_text(json.dumps(metadata, indent=2))
        logger.info("Metadata saved successfully")
    except Exception as e:
        logger.error(f"Error saving metadata: {str(e)}")
        raise

def list_templates() -> List[Dict]:
    """List all available templates"""
    try:
        metadata = load_metadata()
        return metadata.get("templates", [])
    except Exception as e:
        logger.error(f"Error listing templates: {str(e)}")
        return []

def get_template(template_id: str) -> Optional[Dict]:
    """Get template by ID"""
    try:
        if not template_id:
            logger.warning("Empty template_id provided")
            return None
        templates = list_templates()
        return next((t for t in templates if t.get("id") == template_id), None)
    except Exception as e:
        logger.error(f"Error getting template {template_id}: {str(e)}")
        return None

def get_default_template() -> Optional[Dict]:
    """Get the default template"""
    try:
        templates = list_templates()
        if not templates:
            logger.warning("No templates available")
            return None
        default = next((t for t in templates if t.get("is_default")), None)
        if not default and templates:
            logger.info("No default template set, returning first template")
            return templates[0]  # Return first if no default set
        return default
    except Exception as e:
        logger.error(f"Error getting default template: {str(e)}")
        return None

def add_template(file_path: Path, name: str, version: str, set_as_default: bool = False) -> Dict:
    """Add a new template"""
    import uuid

    try:
        # Validate inputs
        if not file_path or not file_path.exists():
            raise FileNotFoundError(f"Template file not found: {file_path}")
        if not name or not isinstance(name, str):
            raise ValueError("Template name must be a non-empty string")
        if not version or not isinstance(version, str):
            raise ValueError("Template version must be a non-empty string")

        # Validate file extension
        if not file_path.name.endswith('.docx'):
            raise ValueError("Template file must be a .docx file")

        metadata = load_metadata()
        templates = metadata.get("templates", [])

        template_id = str(uuid.uuid4())
        # Sanitize filename to prevent path traversal
        safe_filename = Path(file_path.name).name  # Get just the filename
        filename = f"{template_id}_{safe_filename}"
        dest_path = TEMPLATES_DIR / filename

        # Ensure dest_path is within TEMPLATES_DIR (security check)
        if not str(dest_path.resolve()).startswith(str(TEMPLATES_DIR.resolve())):
            raise ValueError("Invalid template path - path traversal detected")

        # Copy template file
        shutil.copy(file_path, dest_path)
        logger.info(f"Copied template file to {dest_path}")

        # If setting as default, unset others
        if set_as_default:
            for t in templates:
                t["is_default"] = False

        # Add to metadata
        template_info = {
            "id": template_id,
            "name": name,
            "version": version,
            "filename": filename,
            "path": str(dest_path),
            "uploaded_at": datetime.utcnow().isoformat(),
            "is_default": set_as_default or len(templates) == 0  # First one is default
        }

        templates.append(template_info)
        metadata["templates"] = templates
        save_metadata(metadata)

        logger.info(f"Added template {name} (ID: {template_id})")
        return template_info
    except Exception as e:
        logger.error(f"Error adding template: {str(e)}")
        raise

def set_default_template(template_id: str) -> bool:
    """Set a template as default"""
    try:
        if not template_id:
            logger.warning("Empty template_id provided")
            return False

        metadata = load_metadata()
        templates = metadata.get("templates", [])

        found = False
        for t in templates:
            if t.get("id") == template_id:
                t["is_default"] = True
                found = True
            else:
                t["is_default"] = False

        if found:
            save_metadata(metadata)
            logger.info(f"Set template {template_id} as default")
        else:
            logger.warning(f"Template {template_id} not found")

        return found
    except Exception as e:
        logger.error(f"Error setting default template: {str(e)}")
        return False

def delete_template(template_id: str) -> bool:
    """Delete a template"""
    try:
        if not template_id:
            logger.warning("Empty template_id provided")
            return False

        metadata = load_metadata()
        templates = metadata.get("templates", [])

        template = next((t for t in templates if t.get("id") == template_id), None)
        if not template:
            logger.warning(f"Template {template_id} not found")
            return False

        # Don't delete if it's the only template
        if len(templates) <= 1:
            logger.warning("Cannot delete the only template")
            return False

        # Delete file with security check
        file_path = Path(template["path"])

        # Ensure file_path is within TEMPLATES_DIR (security check)
        if not str(file_path.resolve()).startswith(str(TEMPLATES_DIR.resolve())):
            logger.error(f"Security violation: Attempted to delete file outside templates dir: {file_path}")
            return False

        if file_path.exists():
            try:
                file_path.unlink()
                logger.info(f"Deleted template file: {file_path}")
            except OSError as e:
                logger.error(f"Failed to delete template file {file_path}: {str(e)}")
                # Continue to remove from metadata even if file deletion fails

        # Remove from metadata
        templates = [t for t in templates if t.get("id") != template_id]

        # If deleted template was default, set first as default
        if template.get("is_default") and templates:
            templates[0]["is_default"] = True
            logger.info(f"Set {templates[0].get('id')} as new default template")

        metadata["templates"] = templates
        save_metadata(metadata)
        logger.info(f"Deleted template {template_id}")
        return True
    except Exception as e:
        logger.error(f"Error deleting template: {str(e)}")
        return False