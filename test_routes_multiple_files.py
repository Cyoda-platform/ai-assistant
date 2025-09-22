#!/usr/bin/env python3
"""
Test script to verify that the chat routes support multiple files.
This is a simple verification script, not a comprehensive test suite.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock
from routes.chat_utils import get_form_data, get_mixed_data
from quart import Quart, request
import io


async def test_get_form_data_multiple_files():
    """Test that get_form_data can handle multiple files."""
    print("Testing get_form_data with multiple files...")
    
    app = Quart(__name__)
    
    with app.test_request_context(
        method='POST',
        data={
            'answer': 'Test answer',
            'name': 'Test chat'
        },
        files={
            'files': [
                (io.BytesIO(b'file1 content'), 'file1.txt'),
                (io.BytesIO(b'file2 content'), 'file2.txt')
            ]
        }
    ):
        (answer, name), single_file, multiple_files = await get_form_data(
            'answer', 'name',
            file_key='file',
            files_key='files'
        )
        
        print(f"Answer: {answer}")
        print(f"Name: {name}")
        print(f"Single file: {single_file}")
        print(f"Multiple files: {len(multiple_files) if multiple_files else 0}")
        
        assert answer == 'Test answer'
        assert name == 'Test chat'
        assert single_file is None  # No single file provided
        assert multiple_files is not None
        assert len(multiple_files) == 2
        
    print("✅ get_form_data test passed!")


async def test_get_mixed_data_json():
    """Test that get_mixed_data handles JSON requests."""
    print("Testing get_mixed_data with JSON...")
    
    app = Quart(__name__)
    
    with app.test_request_context(
        method='POST',
        json={'name': 'Test chat', 'description': 'Test description'},
        headers={'Content-Type': 'application/json'}
    ):
        (name, description), single_file, multiple_files = await get_mixed_data(
            'name', 'description',
            file_key='file',
            files_key='files'
        )
        
        print(f"Name: {name}")
        print(f"Description: {description}")
        print(f"Single file: {single_file}")
        print(f"Multiple files: {multiple_files}")
        
        assert name == 'Test chat'
        assert description == 'Test description'
        assert single_file is None
        assert multiple_files is None
        
    print("✅ get_mixed_data JSON test passed!")


async def test_get_mixed_data_form():
    """Test that get_mixed_data handles form data with files."""
    print("Testing get_mixed_data with form data...")
    
    app = Quart(__name__)
    
    with app.test_request_context(
        method='POST',
        data={
            'name': 'Test chat',
            'description': 'Test description'
        },
        files={
            'files': [
                (io.BytesIO(b'file1 content'), 'file1.txt'),
                (io.BytesIO(b'file2 content'), 'file2.txt')
            ]
        },
        headers={'Content-Type': 'multipart/form-data'}
    ):
        (name, description), single_file, multiple_files = await get_mixed_data(
            'name', 'description',
            file_key='file',
            files_key='files'
        )
        
        print(f"Name: {name}")
        print(f"Description: {description}")
        print(f"Single file: {single_file}")
        print(f"Multiple files: {len(multiple_files) if multiple_files else 0}")
        
        assert name == 'Test chat'
        assert description == 'Test description'
        assert single_file is None  # No single file provided
        assert multiple_files is not None
        assert len(multiple_files) == 2
        
    print("✅ get_mixed_data form test passed!")


async def main():
    """Run all tests."""
    print("🧪 Testing chat routes multiple file support...\n")
    
    try:
        await test_get_form_data_multiple_files()
        print()
        await test_get_mixed_data_json()
        print()
        await test_get_mixed_data_form()
        print()
        print("🎉 All tests passed! Chat routes now support multiple files.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
