from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Dict, Any
import os
from ..services.plugin_manager import PluginManager

# Remove prefix from APIRouter
router = APIRouter(tags=["plugins"])
plugin_manager = PluginManager()

@router.get("/")
def list_plugins():
    return {"plugins": plugin_manager.list_plugins()}

@router.get("/{name}/describe")
def describe_plugin(name: str):
    return {"description": plugin_manager.describe_plugin(name)}

@router.post("/{name}/run")
def run_plugin(name: str, data: Dict[str, Any]):
    return plugin_manager.run_plugin(name, data)

@router.get("/{name}/test")
def test_plugin(name: str):
    return {"result": plugin_manager.test_plugin(name)}

@router.post("/reload")
def reload_plugins():
    plugin_manager.reload_plugins()
    return {"status": "reloaded"}

@router.post("/upload")
def upload_plugin(file: UploadFile = File(...)):
    plugin_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../plugins'))
    file_path = os.path.join(plugin_dir, file.filename)
    with open(file_path, 'wb') as f:
        f.write(file.file.read())
    plugin_manager.reload_plugins()
    return {"status": "uploaded", "plugin": file.filename} 