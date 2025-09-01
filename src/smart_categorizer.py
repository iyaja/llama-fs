import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import mimetypes

class SmartCategorizer:
    """
    Efficient file categorization system that uses file extensions and naming patterns
    to organize files into logical categories before using LLM for content analysis.
    """

    def __init__(self):
        # Define file extensions that should be locationally-exempt (stay where they are)
        self.locationally_exempt_extensions = {
            ".c", ".ts", ".js", ".tsx", ".jsx", ".dll", ".bat", ".ps1", ".h", ".bin",
            ".rst", ".py", ".log", ".jar", ".cab", ".ini", ".cfg", ".conf", ".config",
            ".lock", ".pid", ".tmp", ".temp", ".cache", ".db", ".sqlite", ".sqlite3",
            ".env", ".gitignore", ".gitattributes", ".dockerignore", ".editorconfig",
            ".eslintrc", ".prettierrc", ".babelrc", ".webpack", ".rollup", ".vite",
            ".yarnrc", ".npmrc", ".bowerrc", ".composer", ".gemfile", ".requirements",
            ".makefile", ".cmake", ".gradle", ".maven", ".ant", ".sbt", ".cabal",
            ".stack", ".cargo", ".go.mod", ".go.sum", ".package.json", ".yarn.lock",
            ".package-lock.json", ".pnpm-lock.yaml", ".bun.lockb", ".poetry.lock",
            ".pipfile", ".pipfile.lock", ".conda.yml", ".environment.yml", ".setup.py",
            ".setup.cfg", ".pyproject.toml", ".tox.ini", ".pytest.ini", ".coverage",
            ".coveragerc", ".flake8", ".mypy.ini", ".isort.cfg", ".black", ".pre-commit",
            ".github", ".gitlab-ci", ".travis.yml", ".appveyor.yml", ".circleci",
            ".jenkins", ".azure-pipelines", ".bitbucket-pipelines", ".drone",
            ".woodpecker", ".buildkite", ".semaphore", ".teamcity", ".bamboo",
            ".codeship", ".wercker", ".shippable", ".magnum", ".solano", ".strider",
            ".surf", ".taskcluster", ".tfs", ".vsts", ".xcode", ".xcodeproj", ".xcworkspace",
            ".sln", ".vcxproj", ".vcproj", ".dsp", ".dsw", ".ncb", ".opt", ".plg",
            ".aps", ".clw", ".bsc", ".sbr", ".pdb", ".ilk", ".exp", ".lib", ".obj",
            ".res", ".rc", ".def", ".map", ".tlog", ".lastbuildstate", ".unsuccessfulbuild",
            ".manifest", ".pch", ".idb", ".ipdb", ".iobj", ".ipch", ".sdf", ".opensdf",
            ".suo", ".user", ".userosscache", ".sln.docstates", ".vspscc", ".vssscc",
            ".builds", ".pidb", ".svclog", ".scc", ".vssscc", ".vssscc", ".vssscc"
        }

        # Define file type categories with extensions and naming patterns
        self.categories = {
            "documents": {
                "extensions": [".pdf", ".doc", ".docx", ".txt", ".md", ".rtf", ".odt"],
                "patterns": ["document", "report", "manual", "guide", "readme", "license"],
                "description": "Text documents, PDFs, and written content"
            },
            "spreadsheets": {
                "extensions": [".xls", ".xlsx", ".csv", ".ods"],
                "patterns": ["spreadsheet", "data", "table", "list", "inventory"],
                "description": "Spreadsheets and tabular data"
            },
            "presentations": {
                "extensions": [".ppt", ".pptx", ".odp"],
                "patterns": ["presentation", "slides", "deck", "pitch"],
                "description": "Presentation files and slides"
            },
            "images": {
                "extensions": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg", ".webp", ".ai"],
                "patterns": ["image", "photo", "picture", "screenshot", "screenshot"],
                "description": "Images and graphics"
            },
            "videos": {
                "extensions": [".mp4", ".avi", ".mov", ".wmv", ".flv", ".mkv", ".webm"],
                "patterns": ["video", "movie", "recording", "screen", "demo"],
                "description": "Video files and recordings"
            },
            "audio": {
                "extensions": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"],
                "patterns": ["audio", "music", "sound", "podcast", "recording"],
                "description": "Audio files and music"
            },
            "3d-printing": {
                "extensions": [".stl", ".gcode", ".obj", ".3mf", ".amf", ".ply"],
                "patterns": ["3d", "print", "model", "stl", "gcode", "slicer"],
                "description": "3D printing files and models"
            },
            "installers": {
                "extensions": [".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm", ""],
                "patterns": ["setup", "install", "installer", "setup", "uninstall"],
                "description": "Software installers and setup files"
            },
            "executables": {
                "extensions": [".exe", ".app", ".bat", ".sh", ".py", ".jar"],
                "patterns": ["program", "app", "tool", "utility", "script"],
                "description": "Executable programs and scripts"
            },
            "archives": {
                "extensions": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".iso"],
                "patterns": ["archive", "backup", "compressed", "packed"],
                "description": "Compressed archives and backups"
            },
            "code": {
                "extensions": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".php", ".rb", ".go", ".ts", ".tsx", ".jsx", ".java", ".cpp", ".c", ".php", ".rb", ".go"],
                "patterns": ["code", "script", "program", "source", "dev"],
                "description": "Source code and development files"
            },
            "data": {
                "extensions": [".json", ".xml", ".yaml", ".yml", ".sql", ".db", ".sqlite", ".csv", ".xls", ".xlsx", ".ods"],
                "patterns": ["data", "config", "settings", "database"],
                "description": "Data files and configurations"
            },
            "other": {
                "extensions": [],
                "patterns": [],
                "description": "Miscellaneous files"
            }
        }

        # Initialize mimetypes
        mimetypes.init()

    def _is_existing_folder(self, file_path: str, base_path: str) -> bool:
        """
        Check if a file is inside an already organized folder structure.
        Only considers folders as "organized" if they contain files that suggest
        they're already properly categorized (e.g., all STL files in a folder).
        """
        rel_path = os.path.relpath(file_path, base_path)
        path_parts = rel_path.split(os.sep)

        # If there are multiple path parts, it's in a subdirectory
        if len(path_parts) <= 1:
            return False

        # Get the parent folder name
        folder_name = path_parts[0].lower()

        # Check if this folder name suggests it's already organized
        organized_folder_indicators = [
            "3d", "3d-printing", "stl", "gcode", "models", "prints",
            "images", "photos", "pictures", "screenshots", "wallpapers",
            "documents", "docs", "pdfs", "files", "papers", "research",
            "installers", "setup", "software", "programs", "apps",
            "code", "scripts", "programming", "development", "src",
            "videos", "movies", "clips", "recordings",
            "audio", "music", "sounds", "podcasts",
            "archives", "backups", "old", "temp", "temporary"
        ]

        # If the folder name suggests it's already organized, don't move files from it
        if folder_name in organized_folder_indicators:
            return True

        # Additional check: if the folder contains mostly files of the same type,
        # it might already be organized
        try:
            folder_path = os.path.join(base_path, path_parts[0])
            if os.path.isdir(folder_path):
                files_in_folder = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
                if len(files_in_folder) >= 3:  # Only check folders with 3+ files
                    extensions = [Path(f).suffix.lower() for f in files_in_folder]
                    # If 80% of files have the same extension, consider it organized
                    if extensions:
                        most_common_ext = max(set(extensions), key=extensions.count)
                        if extensions.count(most_common_ext) / len(extensions) >= 0.8:
                            return True
        except (OSError, PermissionError):
            # If we can't read the folder, assume it's not organized
            pass

        return False

    def _get_folder_context(self, file_path: str, base_path: str) -> str:
        """
        Get the folder context for a file to help with categorization.
        """
        rel_path = os.path.relpath(file_path, base_path)
        path_parts = rel_path.split(os.sep)

        if len(path_parts) > 1:
            # Return the parent folder name for context
            return path_parts[0].lower()
        return ""

    def _is_locationally_exempt(self, file_path: str) -> bool:
        """
        Check if a file should be locationally exempt (stay where it is).
        """
        file_path_obj = Path(file_path)
        extension = file_path_obj.suffix.lower()

        # Check if extension is in the exempt list
        if extension in self.locationally_exempt_extensions:
            return True

        # Also check for files without extensions that might be exempt
        filename = file_path_obj.name.lower()
        exempt_filenames = {
            "makefile", "dockerfile", "docker-compose.yml", "docker-compose.yaml",
            "readme", "readme.md", "readme.txt", "readme.rst", "readme.rst",
            "changelog", "changelog.md", "changelog.txt", "changelog.rst",
            "license", "license.md", "license.txt", "license.rst",
            "contributing", "contributing.md", "contributing.txt", "contributing.rst",
            "authors", "authors.md", "authors.txt", "authors.rst",
            "news", "news.md", "news.txt", "news.rst",
            "todo", "todo.md", "todo.txt", "todo.rst",
            "version", "version.md", "version.txt", "version.rst"
        }

        if filename in exempt_filenames:
            return True

        return False

    def categorize_file(self, file_path: str, file_name: str, base_path: str = "") -> Tuple[str, str, str]:
        """
        Categorize a file based on extension and filename patterns.
        Returns: (category, subcategory, description)
        """
        file_path_obj = Path(file_path)
        extension = file_path_obj.suffix.lower()
        name_lower = file_name.lower()

        # First, check if file is locationally exempt (should stay where it is)
        if self._is_locationally_exempt(file_path):
            return "exempt", "locationally-exempt", "File is locationally exempt and should stay in place"

        # Check if file is in an existing folder structure
        if base_path and self._is_existing_folder(file_path, base_path):
            folder_context = self._get_folder_context(file_path, base_path)

            # Use folder context to influence categorization
            if folder_context in ["3d", "3d-printing", "stl", "gcode", "models"]:
                return "3d-printing", "existing-folder", "3D printing files in existing folder"
            elif folder_context in ["images", "photos", "pictures", "screenshots"]:
                return "images", "existing-folder", "Images in existing folder"
            elif folder_context in ["documents", "docs", "pdfs", "files"]:
                return "documents", "existing-folder", "Documents in existing folder"
            elif folder_context in ["installers", "setup", "software"]:
                return "installers", "existing-folder", "Installers in existing folder"
            elif folder_context in ["code", "scripts", "programming"]:
                return "code", "existing-folder", "Code files in existing folder"
            else:
                # Generic existing folder
                return "other", "existing-folder", f"Files in existing {folder_context} folder"

        # Original categorization logic for root-level files
        # First, try to match by extension
        for category, config in self.categories.items():
            if extension in config["extensions"]:
                # Check if filename matches specific patterns for subcategorization
                subcategory = self._get_subcategory(name_lower, category)
                return category, subcategory, config["description"]

        # If no extension match, try pattern matching
        for category, config in self.categories.items():
            for pattern in config["patterns"]:
                if pattern in name_lower:
                    subcategory = self._get_subcategory(name_lower, category)
                    return category, subcategory, config["description"]

        # Try to guess by mimetype
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            if mime_type.startswith('image/'):
                return "images", self._get_subcategory(name_lower, "images"), "Images and graphics"
            elif mime_type.startswith('video/'):
                return "videos", self._get_subcategory(name_lower, "videos"), "Video files and recordings"
            elif mime_type.startswith('audio/'):
                return "audio", self._get_subcategory(name_lower, "audio"), "Audio files and music"
            elif mime_type.startswith('text/'):
                return "documents", self._get_subcategory(name_lower, "documents"), "Text documents"

        # Default to "other"
        return "other", "misc", "Miscellaneous files"

    def _get_subcategory(self, filename: str, category: str) -> str:
        """
        Determine subcategory based on filename patterns and category.
        """
        if category == "documents":
            if any(word in filename for word in ["manual", "guide", "tutorial"]):
                return "manuals"
            elif any(word in filename for word in ["report", "analysis", "study"]):
                return "reports"
            elif any(word in filename for word in ["contract", "agreement", "legal"]):
                return "legal"
            else:
                return "general"

        elif category == "images":
            if any(word in filename for word in ["screenshot", "screen"]):
                return "screenshots"
            elif any(word in filename for word in ["photo", "picture", "image"]):
                return "photos"
            elif any(word in filename for word in ["logo", "icon", "brand"]):
                return "logos"
            else:
                return "general"

        elif category == "3d-printing":
            if "gcode" in filename:
                return "gcode"
            elif any(word in filename for word in ["stl", "model"]):
                return "models"
            else:
                return "general"

        elif category == "installers":
            if any(word in filename for word in ["setup", "install"]):
                return "installers"
            elif any(word in filename for word in ["uninstall", "remove"]):
                return "uninstallers"
            else:
                return "general"

        elif category == "code":
            if any(word in filename for word in ["script", "utility"]):
                return "scripts"
            elif any(word in filename for word in ["config", "settings"]):
                return "config"
            else:
                return "source"

        else:
            return "general"

    def create_organized_structure(self, files: List[Dict], base_path: str = "") -> Dict[str, List[Dict]]:
        """
        Create an organized structure based on file categorization.
        """
        organized = {}

        for file_info in files:
            category, subcategory, description = self.categorize_file(
                file_info["file_path"],
                file_info["file_name"],
                base_path
            )

            # Create category key
            if category not in organized:
                organized[category] = {}

            # Create subcategory key
            if subcategory not in organized[category]:
                organized[category][subcategory] = []

            # Add file to appropriate subcategory
            organized[category][subcategory].append({
                **file_info,
                "category": category,
                "subcategory": subcategory,
                "description": description
            })

        return organized

    def generate_move_plan(self, organized_files: Dict[str, List[Dict]], base_path: str) -> List[Dict]:
        """
        Generate a plan for moving files to their organized locations.
        """
        move_plan = []

        for category, subcategories in organized_files.items():
            for subcategory, files in subcategories.items():
                for file_info in files:
                    # Check if file is locationally exempt or already in an existing folder
                    if subcategory in ["locationally-exempt", "existing-folder"]:
                        # Don't move files that are exempt or already in organized folders
                        # Just keep them where they are
                        move_plan.append({
                            "src_path": file_info["file_path"],
                            "dst_path": file_info["file_path"],  # Keep same path
                            "category": category,
                            "subcategory": subcategory,
                            "description": file_info["description"],
                            "skip_move": True  # Flag to indicate no actual move needed
                        })
                    else:
                        # Create destination path for root-level files
                        if subcategory == "general":
                            dst_path = f"{category}/{file_info['file_name']}"
                        else:
                            dst_path = f"{category}/{subcategory}/{file_info['file_name']}"

                        move_plan.append({
                            "src_path": file_info["file_path"],
                            "dst_path": dst_path,
                            "category": category,
                            "subcategory": subcategory,
                            "description": file_info["description"],
                            "skip_move": False
                        })

        return move_plan

    def get_category_stats(self, organized_files: Dict[str, List[Dict]]) -> Dict[str, int]:
        """
        Get statistics about file distribution across categories.
        """
        stats = {}
        for category, subcategories in organized_files.items():
            total_files = sum(len(files) for files in subcategories.values())
            stats[category] = total_files
        return stats
