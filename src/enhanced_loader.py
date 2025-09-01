import asyncio
import json
import os
import warnings
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import colorama
import ollama
import weave
from tqdm.asyncio import tqdm

# Suppress only harmless warnings, keep important error logging
warnings.filterwarnings("ignore", message=".*Palette images with Transparency.*")
warnings.filterwarnings("ignore", message=".*Ignoring wrong pointing object.*")
# Don't suppress all PIL warnings - some might be important
from llama_index.core import Document, SimpleDirectoryReader
from llama_index.core.schema import ImageDocument
from llama_index.core.node_parser import TokenTextSplitter
from termcolor import colored

from src.smart_categorizer import SmartCategorizer


class EnhancedFileLoader:
    """
    Enhanced file loader that uses smart categorization for efficient organization.
    """

    def __init__(self):
        self.categorizer = SmartCategorizer()

    async def get_organized_files(self, path: str, use_llm_for_content: bool = True):
        """
        Get files organized using smart categorization with optional LLM content analysis.
        """
        # Step 1: Load basic file information
        file_list = self._load_file_list(path)

        # Step 2: Apply smart categorization
        organized_files = self.categorizer.create_organized_structure(file_list, path)

        # Step 3: Generate move plan
        move_plan = self.categorizer.generate_move_plan(organized_files, path)

        # Step 4: Optionally enhance with LLM content analysis for specific categories
        if use_llm_for_content:
            enhanced_plan = await self._enhance_with_llm_analysis(move_plan, path)
        else:
            enhanced_plan = move_plan

        # Step 5: Get statistics
        stats = self.categorizer.get_category_stats(organized_files)

        return {
            "organized_structure": organized_files,
            "move_plan": enhanced_plan,
            "statistics": stats,
            "total_files": len(file_list)
        }

    def _load_file_list(self, path: str) -> List[Dict]:
        """
        Load basic file information without content analysis.
        """
        file_list = []

        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, path)

                file_info = {
                    "file_path": rel_path,
                    "file_name": file,
                    "full_path": file_path,
                    "size": os.path.getsize(file_path),
                    "extension": Path(file).suffix.lower(),
                    "category": None,
                    "subcategory": None
                }

                file_list.append(file_info)

        return file_list

    async def _enhance_with_llm_analysis(self, move_plan: List[Dict], base_path: str) -> List[Dict]:
        """
        Enhance the move plan with LLM content analysis for specific categories.
        """
        enhanced_plan = []

        # Only analyze files that might benefit from content-based organization
        content_categories = ["documents", "images", "videos", "audio", "other"]

        # Filter files that need analysis
        files_to_analyze = [f for f in move_plan if f["category"] in content_categories]

        if not files_to_analyze:
            print("No files require LLM content analysis.")
            return move_plan

        print(f"🔍 Analyzing {len(files_to_analyze)} files with LLM...")

        # Process files with progress bar
        async def analyze_file(file_info):
            full_path = os.path.join(base_path, file_info["src_path"])
            file_name = os.path.basename(file_info["src_path"])

            try:
                summary = await self._get_file_summary(full_path)
                file_info["content_summary"] = summary

                # Enhance destination path based on content
                enhanced_dst = self._enhance_destination_path(file_info)
                file_info["dst_path"] = enhanced_dst

                return file_info, None
            except Exception as e:
                error_msg = f"Could not analyze {file_name}: {str(e)}"
                print(f"❌ {error_msg}")
                file_info["content_summary"] = "Analysis failed"
                return file_info, error_msg

        # Use tqdm for progress tracking
        tasks = [analyze_file(file_info) for file_info in files_to_analyze]
        results = []

        for task in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Analyzing files"):
            result, error = await task
            results.append(result)
            if error:
                print(f"⚠️  {error}")

        # Reconstruct the full plan with enhanced results
        result_dict = {r["src_path"]: r for r in results}

        for file_info in move_plan:
            if file_info["src_path"] in result_dict:
                enhanced_plan.append(result_dict[file_info["src_path"]])
            else:
                # For non-content files, keep the original categorization
                file_info["content_summary"] = file_info["description"]
                enhanced_plan.append(file_info)

        return enhanced_plan

    async def _get_file_summary(self, file_path: str) -> str:
        """
        Get a brief summary of file content using LLM.
        """
        try:
            # Determine file type and use appropriate analysis
            extension = Path(file_path).suffix.lower()

            if extension in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg", ".webp"]:
                return await self._analyze_image(file_path)
            elif extension in [".pdf", ".doc", ".docx", ".txt", ".md"]:
                return await self._analyze_text_document(file_path)
            else:
                return "File content analysis not available for this type"

        except Exception as e:
            return f"Analysis error: {str(e)}"

    async def _analyze_image(self, file_path: str) -> str:
        """
        Analyze image content using moondream.
        """
        try:
            # Suppress PIL warnings for better user experience
            import warnings
            from PIL import Image

            # Convert palette images to RGBA to avoid warnings
            temp_path = None
            try:
                with Image.open(file_path) as img:
                    if img.mode == 'P' and 'transparency' in img.info:
                        img = img.convert('RGBA')
                        # Save the converted image temporarily
                        temp_path = file_path + '.temp_rgba.png'
                        img.save(temp_path)
                        file_path = temp_path
            except Exception as img_error:
                # If image conversion fails, continue with original file
                print(f"⚠️  Image conversion warning for {os.path.basename(file_path)}: {img_error}")

            client = ollama.AsyncClient()
            response = await client.chat(
                messages=[
                    {
                        "role": "user",
                        "content": "Briefly describe this image in 1-2 sentences for file organization purposes.",
                        "images": [file_path],
                    },
                ],
                model="moondream",
                options={"num_predict": 64},
            )

            # Clean up temporary file if created
            if temp_path:
                try:
                    import os
                    os.remove(temp_path)
                except:
                    pass

            return response["message"]["content"]
        except Exception as e:
            error_msg = f"Image analysis failed for {os.path.basename(file_path)}: {str(e)}"
            print(f"❌ {error_msg}")
            return f"Image analysis failed: {str(e)}"

    async def _analyze_text_document(self, file_path: str) -> str:
        """
        Analyze text document content using llama3.1.
        """
        try:
            # Load document content
            reader = SimpleDirectoryReader(input_files=[file_path]).iter_data()
            docs = next(reader)

            if not docs:
                return "Empty or unreadable document"

            # Get first chunk of text
            text = docs[0].text[:500]  # Limit to first 500 characters

            client = ollama.AsyncClient()
            response = await client.chat(
                messages=[
                    {
                        "role": "system",
                        "content": "Provide a brief 1-2 sentence summary of this document for file organization purposes."
                    },
                    {
                        "role": "user",
                        "content": f"Document content: {text}"
                    },
                ],
                model="llama3.1:8b",
                options={"num_predict": 64},
            )
            return response["message"]["content"]
        except Exception as e:
            error_msg = f"Text analysis failed for {os.path.basename(file_path)}: {str(e)}"
            print(f"❌ {error_msg}")
            return f"Text analysis failed: {str(e)}"

    def _enhance_destination_path(self, file_info: Dict) -> str:
        """
        Enhance the destination path based on content analysis.
        """
        original_dst = file_info["dst_path"]
        summary = file_info.get("content_summary", "").lower()

        # Add content-based subcategories
        if file_info["category"] == "documents":
            if any(word in summary for word in ["manual", "guide", "tutorial", "instructions"]):
                return original_dst.replace("/general/", "/manuals/")
            elif any(word in summary for word in ["report", "analysis", "study", "research"]):
                return original_dst.replace("/general/", "/reports/")
            elif any(word in summary for word in ["contract", "agreement", "legal", "terms"]):
                return original_dst.replace("/general/", "/legal/")

        elif file_info["category"] == "images":
            if any(word in summary for word in ["screenshot", "screen capture"]):
                return original_dst.replace("/general/", "/screenshots/")
            elif any(word in summary for word in ["photo", "picture", "photograph"]):
                return original_dst.replace("/general/", "/photos/")
            elif any(word in summary for word in ["logo", "icon", "brand"]):
                return original_dst.replace("/general/", "/logos/")

        # Return original path if no enhancement needed
        return original_dst

    def get_quick_stats(self, path: str) -> Dict:
        """
        Get quick statistics about files in a directory without LLM analysis.
        """
        file_list = self._load_file_list(path)
        organized_files = self.categorizer.create_organized_structure(file_list)
        stats = self.categorizer.get_category_stats(organized_files)

        return {
            "total_files": len(file_list),
            "categories": stats,
            "file_types": self._get_file_type_breakdown(file_list)
        }

    def _get_file_type_breakdown(self, file_list: List[Dict]) -> Dict[str, int]:
        """
        Get breakdown of files by extension.
        """
        extension_counts = defaultdict(int)
        for file_info in file_list:
            ext = file_info["extension"]
            extension_counts[ext] += 1

        return dict(extension_counts)
