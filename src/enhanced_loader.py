"""
Enhanced File Loader for LlamaFS

This module provides an enhanced file loading and organization system that combines
smart categorization with optional LLM content analysis. It's designed to be fast
and efficient while providing intelligent file organization.

Key Features:
- Smart categorization using file extensions and patterns
- Optional LLM content analysis for enhanced organization
- Concurrent processing with configurable limits
- Safety limits to prevent system overload
- Progress tracking and error handling
- Support for both text and image analysis

The system first applies fast rule-based categorization, then optionally enhances
specific file types (documents, images) with LLM content analysis for better
organization.

"""

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

    This class combines the speed of rule-based categorization with the intelligence
    of LLM content analysis. It processes files in batches with concurrency limits
    to prevent system overload while providing comprehensive file organization.
    """

    def __init__(self, max_concurrent_tasks: int = 5):
        self.categorizer = SmartCategorizer()
        self.max_concurrent_tasks = max_concurrent_tasks
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)

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
            "total_files": len(file_list),
            "files_processed": len(file_list),
            "files_skipped": getattr(self, "_files_skipped", 0),
        }

    def _load_file_list(self, path: str) -> List[Dict]:
        """
        Load basic file information without content analysis.
        Only counts files that will actually be processed (not exempt or in existing folders).
        """
        file_list = []
        max_files = 5000  # Safety limit to prevent system overload
        files_processed = 0
        files_skipped = 0

        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, path)

                # Check if this file would be processed (not exempt or in existing folder)
                if self._should_process_file(file_path, path):
                    if files_processed >= max_files:
                        print(
                            f"⚠️  Reached processable file limit ({max_files}). Stopping file discovery."
                        )
                        break

                    file_info = {
                        "file_path": rel_path,
                        "file_name": file,
                        "full_path": file_path,
                        "size": os.path.getsize(file_path),
                        "extension": Path(file).suffix.lower(),
                        "category": None,
                        "subcategory": None,
                    }

                    file_list.append(file_info)
                    files_processed += 1
                else:
                    files_skipped += 1

            if files_processed >= max_files:
                break

        if files_processed >= max_files:
            print(
                f"⚠️  Limited to {max_files} processable files to prevent system overload."
            )

        if files_skipped > 0:
            print(f"ℹ️  Skipped {files_skipped} files (exempt or in existing folders).")

        # Store skipped count for statistics
        self._files_skipped = files_skipped

        return file_list

    def _should_process_file(self, file_path: str, base_path: str) -> bool:
        """
        Check if a file should be processed (not exempt or in existing folder).
        """
        # Check if file is locationally exempt
        if self.categorizer._is_locationally_exempt(file_path):
            return False

        # Check if file is in an existing organized folder
        if self.categorizer._is_existing_folder(file_path, base_path):
            return False

        return True

    async def _enhance_with_llm_analysis(
        self, move_plan: List[Dict], base_path: str
    ) -> List[Dict]:
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

        # Safety check: limit the number of files to analyze to prevent system overload
        max_files_to_analyze = 1000  # Reasonable limit
        if len(files_to_analyze) > max_files_to_analyze:
            print(
                f"⚠️  Too many files to analyze ({len(files_to_analyze)}). Limiting to {max_files_to_analyze} files."
            )
            files_to_analyze = files_to_analyze[:max_files_to_analyze]

        print(f"🔍 Analyzing {len(files_to_analyze)} files with LLM...")

        # Process files with progress bar and concurrency limits
        async def analyze_file(file_info):
            async with self.semaphore:  # Limit concurrent operations
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

        # Process files in batches to avoid overwhelming the system
        batch_size = min(50, len(files_to_analyze))  # Process max 50 files at a time
        results = []

        for i in range(0, len(files_to_analyze), batch_size):
            batch = files_to_analyze[i : i + batch_size]
            print(
                f"📦 Processing batch {i//batch_size + 1}/{(len(files_to_analyze) + batch_size - 1)//batch_size} ({len(batch)} files)"
            )

            # Create tasks for this batch
            tasks = [analyze_file(file_info) for file_info in batch]

            # Process batch with progress tracking
            batch_results = []
            for task in tqdm(
                asyncio.as_completed(tasks),
                total=len(tasks),
                desc=f"Batch {i//batch_size + 1}",
            ):
                result, error = await task
                batch_results.append(result)
                if error:
                    print(f"⚠️  {error}")

            results.extend(batch_results)

            # Small delay between batches to prevent overwhelming the system
            if i + batch_size < len(files_to_analyze):
                await asyncio.sleep(0.1)

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

            if extension in [
                ".jpg",
                ".jpeg",
                ".png",
                ".gif",
                ".bmp",
                ".tiff",
                ".svg",
                ".webp",
            ]:
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
                    if img.mode == "P" and "transparency" in img.info:
                        img = img.convert("RGBA")
                        # Save the converted image temporarily
                        temp_path = file_path + ".temp_rgba.png"
                        img.save(temp_path)
                        file_path = temp_path
            except Exception as img_error:
                # If image conversion fails, continue with original file
                print(
                    f"⚠️  Image conversion warning for {os.path.basename(file_path)}: {img_error}"
                )

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
            error_msg = (
                f"Image analysis failed for {os.path.basename(file_path)}: {str(e)}"
            )
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
                        "content": "Provide a brief 1-2 sentence summary of this document for file organization purposes.",
                    },
                    {"role": "user", "content": f"Document content: {text}"},
                ],
                model="llama3.1:8b",
                options={"num_predict": 64},
            )
            return response["message"]["content"]
        except Exception as e:
            error_msg = (
                f"Text analysis failed for {os.path.basename(file_path)}: {str(e)}"
            )
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
            if any(
                word in summary
                for word in ["manual", "guide", "tutorial", "instructions"]
            ):
                return original_dst.replace("/general/", "/manuals/")
            elif any(
                word in summary for word in ["report", "analysis", "study", "research"]
            ):
                return original_dst.replace("/general/", "/reports/")
            elif any(
                word in summary for word in ["contract", "agreement", "legal", "terms"]
            ):
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
            "file_types": self._get_file_type_breakdown(file_list),
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
