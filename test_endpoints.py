"""
Comprehensive Test Suite for LlamaFS API Endpoints

This test suite covers all API endpoints in the LlamaFS server, including both
new smart categorization endpoints and legacy LLM-based endpoints.

Test Coverage:
- Quick statistics endpoint
- Smart batch preview and execution
- Legacy batch preview and execution
- Watch mode functionality
- Individual file commit operations
- Error handling and edge cases

Requirements:
- FastAPI test client
- Sample test data in sample_data directory
- Ollama models (llama3.1:8b and moondream) running locally

Usage:
    python test_endpoints.py

Author: LlamaFS Team
"""

import asyncio
import json
import os
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Import the FastAPI app
from server import app

# Create test client
client = TestClient(app)


class TestLlamaFSEndpoints:
    """Test suite for LlamaFS API endpoints."""

    @classmethod
    def setup_class(cls):
        """Set up test environment with sample data."""
        # Create temporary test directory
        cls.test_dir = tempfile.mkdtemp(prefix="llamafs_test_")

        # Create sample files for testing
        cls._create_sample_files()

        print(f"Test directory created: {cls.test_dir}")

    @classmethod
    def teardown_class(cls):
        """Clean up test environment."""
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)
            print(f"Test directory cleaned up: {cls.test_dir}")

    @classmethod
    def _create_sample_files(cls):
        """Create sample files for testing."""
        # Create various file types
        sample_files = {
            "document.pdf": "Sample PDF content",
            "spreadsheet.xlsx": "Sample Excel content",
            "presentation.pptx": "Sample PowerPoint content",
            "image.jpg": "Sample image content",
            "video.mp4": "Sample video content",
            "audio.mp3": "Sample audio content",
            "3d_model.stl": "Sample 3D model content",
            "installer.exe": "Sample installer content",
            "archive.zip": "Sample archive content",
            "script.py": "Sample Python script",
            "config.json": "Sample configuration",
            "readme.txt": "Sample readme file",
            "setup.exe": "Sample setup file",
            "uninstall.exe": "Sample uninstall file",
            "screenshot.png": "Sample screenshot",
            "photo.jpg": "Sample photo",
            "logo.svg": "Sample logo",
            "gcode.gcode": "Sample G-code file",
            "model.obj": "Sample 3D model",
            "data.csv": "Sample CSV data",
        }

        # Create files in test directory
        for filename, content in sample_files.items():
            file_path = os.path.join(cls.test_dir, filename)
            with open(file_path, "w") as f:
                f.write(content)

        # Create some subdirectories with files
        subdirs = {
            "documents": ["manual.pdf", "report.docx"],
            "images": ["photo1.jpg", "photo2.png"],
            "code": ["script.js", "style.css"],
        }

        for subdir, files in subdirs.items():
            subdir_path = os.path.join(cls.test_dir, subdir)
            os.makedirs(subdir_path, exist_ok=True)
            for file in files:
                file_path = os.path.join(subdir_path, file)
                with open(file_path, "w") as f:
                    f.write(f"Sample {file} content")

    def test_root_endpoint(self):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Hello World"}

    def test_quick_stats_endpoint(self):
        """Test the quick statistics endpoint."""
        response = client.post(
            "/quick-stats",
            json={
                "path": self.test_dir,
                "instruction": "Test instruction",
                "incognito": False,
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "message" in data
        assert "statistics" in data
        assert "total_files" in data["statistics"]
        assert "categories" in data["statistics"]
        assert "file_types" in data["statistics"]

        # Verify we have files in the test directory
        assert data["statistics"]["total_files"] > 0

    def test_quick_stats_invalid_path(self):
        """Test quick stats with invalid path."""
        response = client.post(
            "/quick-stats",
            json={
                "path": "/nonexistent/path",
                "instruction": "Test instruction",
                "incognito": False,
            },
        )

        assert response.status_code == 400
        assert "Path does not exist" in response.json()["detail"]

    @patch("src.enhanced_loader.EnhancedFileLoader.get_organized_files")
    def test_smart_batch_endpoint(self, mock_get_organized_files):
        """Test the smart batch preview endpoint."""
        # Mock the enhanced loader response
        mock_response = {
            "organized_structure": {
                "documents": {
                    "general": [
                        {"file_name": "document.pdf", "file_path": "document.pdf"}
                    ]
                }
            },
            "move_plan": [
                {
                    "src_path": "document.pdf",
                    "dst_path": "documents/general/document.pdf",
                    "category": "documents",
                    "subcategory": "general",
                }
            ],
            "statistics": {"documents": 1},
            "total_files": 1,
        }
        mock_get_organized_files.return_value = mock_response

        response = client.post(
            "/smart-batch",
            json={
                "path": self.test_dir,
                "instruction": "Test instruction",
                "incognito": False,
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "organized_structure" in data
        assert "move_plan" in data
        assert "statistics" in data
        assert "tree" in data
        assert "total_files" in data

    def test_smart_batch_invalid_path(self):
        """Test smart batch with invalid path."""
        response = client.post(
            "/smart-batch",
            json={
                "path": "/nonexistent/path",
                "instruction": "Test instruction",
                "incognito": False,
            },
        )

        assert response.status_code == 400
        assert "Path does not exist" in response.json()["detail"]

    @patch("src.enhanced_loader.EnhancedFileLoader.get_organized_files")
    def test_smart_batch_execute_endpoint(self, mock_get_organized_files):
        """Test the smart batch execute endpoint."""
        # Mock the enhanced loader response
        mock_response = {
            "move_plan": [
                {
                    "src_path": "document.pdf",
                    "dst_path": "documents/general/document.pdf",
                    "category": "documents",
                    "subcategory": "general",
                    "skip_move": False,
                }
            ],
            "statistics": {"documents": 1},
            "total_files": 1,
        }
        mock_get_organized_files.return_value = mock_response

        response = client.post(
            "/smart-batch-execute",
            json={
                "path": self.test_dir,
                "instruction": "Test instruction",
                "incognito": False,
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "message" in data
        assert "results" in data
        assert "errors" in data
        assert "statistics" in data
        assert "total_files" in data

    def test_smart_batch_execute_invalid_path(self):
        """Test smart batch execute with invalid path."""
        response = client.post(
            "/smart-batch-execute",
            json={
                "path": "/nonexistent/path",
                "instruction": "Test instruction",
                "incognito": False,
            },
        )

        assert response.status_code == 400
        assert "Path does not exist" in response.json()["detail"]

    @patch("src.loader.get_dir_summaries")
    @patch("src.tree_generator.create_file_tree")
    def test_batch_endpoint(self, mock_create_file_tree, mock_get_dir_summaries):
        """Test the legacy batch preview endpoint."""
        # Mock the loader response
        mock_summaries = [{"file_path": "document.pdf", "summary": "Test document"}]
        mock_get_dir_summaries.return_value = mock_summaries

        # Mock the tree generator response
        mock_files = [
            {"src_path": "document.pdf", "dst_path": "documents/document.pdf"}
        ]
        mock_create_file_tree.return_value = mock_files

        response = client.post(
            "/batch",
            json={
                "path": self.test_dir,
                "instruction": "Test instruction",
                "incognito": False,
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "files" in data
        assert "tree" in data

    def test_batch_invalid_path(self):
        """Test legacy batch with invalid path."""
        response = client.post(
            "/batch",
            json={
                "path": "/nonexistent/path",
                "instruction": "Test instruction",
                "incognito": False,
            },
        )

        assert response.status_code == 400
        assert "Path does not exist" in response.json()["detail"]

    @patch("src.loader.get_dir_summaries")
    @patch("src.tree_generator.create_file_tree")
    def test_batch_execute_endpoint(
        self, mock_create_file_tree, mock_get_dir_summaries
    ):
        """Test the legacy batch execute endpoint."""
        # Mock the loader response
        mock_summaries = [{"file_path": "document.pdf", "summary": "Test document"}]
        mock_get_dir_summaries.return_value = mock_summaries

        # Mock the tree generator response
        mock_files = [
            {"src_path": "document.pdf", "dst_path": "documents/document.pdf"}
        ]
        mock_create_file_tree.return_value = mock_files

        response = client.post(
            "/batch-execute",
            json={
                "path": self.test_dir,
                "instruction": "Test instruction",
                "incognito": False,
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "message" in data
        assert "results" in data
        assert "errors" in data
        assert "total_files" in data

    def test_batch_execute_invalid_path(self):
        """Test legacy batch execute with invalid path."""
        response = client.post(
            "/batch-execute",
            json={
                "path": "/nonexistent/path",
                "instruction": "Test instruction",
                "incognito": False,
            },
        )

        assert response.status_code == 400
        assert "Path does not exist" in response.json()["detail"]

    def test_commit_endpoint(self):
        """Test the individual file commit endpoint."""
        # Create a test file to move
        test_file = os.path.join(self.test_dir, "test_file.txt")
        with open(test_file, "w") as f:
            f.write("Test content")

        response = client.post(
            "/commit",
            json={
                "base_path": self.test_dir,
                "src_path": "test_file.txt",
                "dst_path": "moved/test_file.txt",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Commit successful"

        # Verify file was moved
        moved_file = os.path.join(self.test_dir, "moved", "test_file.txt")
        assert os.path.exists(moved_file)
        assert not os.path.exists(test_file)

    def test_commit_invalid_source(self):
        """Test commit with invalid source path."""
        response = client.post(
            "/commit",
            json={
                "base_path": self.test_dir,
                "src_path": "nonexistent.txt",
                "dst_path": "moved/nonexistent.txt",
            },
        )

        assert response.status_code == 400
        assert "Source path does not exist" in response.json()["detail"]

    def test_commit_move_to_directory(self):
        """Test commit moving file to directory."""
        # Create a test file and destination directory
        test_file = os.path.join(self.test_dir, "test_file2.txt")
        dest_dir = os.path.join(self.test_dir, "dest_dir")
        os.makedirs(dest_dir, exist_ok=True)

        with open(test_file, "w") as f:
            f.write("Test content")

        response = client.post(
            "/commit",
            json={
                "base_path": self.test_dir,
                "src_path": "test_file2.txt",
                "dst_path": "dest_dir",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Commit successful"

        # Verify file was moved to directory
        moved_file = os.path.join(dest_dir, "test_file2.txt")
        assert os.path.exists(moved_file)
        assert not os.path.exists(test_file)

    def test_watch_endpoint_invalid_path(self):
        """Test watch endpoint with invalid path."""
        response = client.post(
            "/watch",
            json={
                "path": "/nonexistent/path",
                "instruction": "Test instruction",
                "incognito": False,
            },
        )

        assert response.status_code == 400
        assert "Path does not exist" in response.json()["detail"]

    def test_request_validation(self):
        """Test request validation for all endpoints."""
        # Test missing path (None path should return 400)
        response = client.post(
            "/quick-stats", json={"instruction": "Test instruction", "incognito": False}
        )
        assert response.status_code == 400  # Should return 400 for None path

        # Test invalid JSON
        response = client.post(
            "/quick-stats",
            data="invalid json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422  # Validation error

    def test_commit_request_validation(self):
        """Test commit request validation."""
        # Test missing required fields
        response = client.post(
            "/commit",
            json={
                "base_path": self.test_dir
                # Missing src_path and dst_path
            },
        )
        assert response.status_code == 422  # Validation error

        # Test with all required fields
        response = client.post(
            "/commit",
            json={
                "base_path": self.test_dir,
                "src_path": "test.txt",
                "dst_path": "moved/test.txt",
            },
        )
        # Should return 400 for non-existent source, not 422 for validation
        assert response.status_code == 400


def run_tests():
    """Run all tests."""
    print("Running LlamaFS API endpoint tests...")

    # Create test instance
    test_instance = TestLlamaFSEndpoints()
    test_instance.setup_class()

    try:
        # Run tests
        test_methods = [
            method for method in dir(test_instance) if method.startswith("test_")
        ]

        passed = 0
        failed = 0

        for test_method in test_methods:
            try:
                print(f"Running {test_method}...")
                getattr(test_instance, test_method)()
                print(f"✅ {test_method} passed")
                passed += 1
            except Exception as e:
                print(f"❌ {test_method} failed: {str(e)}")
                failed += 1

        print(f"\nTest Results: {passed} passed, {failed} failed")

        if failed == 0:
            print("🎉 All tests passed!")
        else:
            print("⚠️  Some tests failed. Check the output above.")

    finally:
        test_instance.teardown_class()


if __name__ == "__main__":
    run_tests()
