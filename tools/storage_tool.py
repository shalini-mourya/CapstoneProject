# tools/storage_tool.py
import os
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class StorageTool:
    name: str = "store_pdf"

    def run(self, pdf_bytes: bytes, filename: str, dest: str = "local") -> Dict[str, Any]:
        """
        Save PDF bytes to a file. Extend later for cloud storage.
        """
        os.makedirs("outputs", exist_ok=True)
        path = os.path.join("outputs", filename)
        with open(path, "wb") as f:
            f.write(pdf_bytes)

        return {
            "type": "file",
            "path": path,
            "meta": {"dest": dest}
        }