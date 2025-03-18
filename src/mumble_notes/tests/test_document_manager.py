"""
Tests for the document manager component
"""

import pytest
import tkinter as tk
from tkinter import ttk
from unittest.mock import MagicMock, patch
import logging

from ..ui.document_manager import DocumentManager

@pytest.fixture
def root():
    """Create root window"""
    root = tk.Tk()
    yield root
    root.destroy()

@pytest.fixture
def manager(root):
    """Create DocumentManager instance"""
    manager = DocumentManager(root)
    return manager

def test_initialization(manager):
    """Test document manager initialization"""
    # Test frame configuration
    assert manager.grid_info()['row'] == 0
    assert manager.grid_info()['column'] == 0
    
    # Test search bar setup
    search_frame = None
    for child in manager.winfo_children():
        if isinstance(child, ttk.Frame):
            if child.winfo_children()[0].winfo_class() == 'TEntry':
                search_frame = child
                break
    assert search_frame is not None
    
    # Test tree view setup
    tree_frame = None
    for child in manager.winfo_children():
        if isinstance(child, ttk.Frame):
            if child.winfo_children()[0].winfo_class() == 'Treeview':
                tree_frame = child
                break
    assert tree_frame is not None
    
    # Test initial state
    assert isinstance(manager.documents, dict)
    assert manager.current_document is None

def test_search_bar(manager):
    """Test search bar functionality"""
    # Add some test documents
    manager.add_document("Test Doc 1", "Content 1")
    manager.add_document("Test Doc 2", "Content 2")
    manager.add_document("Other Doc", "Content 3")
    
    # Test search filtering
    manager.search_var.set("Test")
    
    # Get visible items
    visible_items = manager.tree.get_children()
    assert len(visible_items) == 2
    assert all("Test" in manager.tree.item(item)['text'] for item in visible_items)
    
    # Test search clear
    manager.clear_search()
    assert manager.search_var.get() == ""
    assert len(manager.tree.get_children()) == 3

def test_document_operations(manager):
    """Test document operations"""
    # Test adding document
    manager.add_document("Test Doc", "Test content")
    assert len(manager.documents) == 1
    assert len(manager.tree.get_children()) == 1
    
    doc_id = list(manager.documents.keys())[0]
    doc = manager.documents[doc_id]
    assert doc['title'] == "Test Doc"
    assert doc['content'] == "Test content"
    
    # Test selecting document
    manager.tree.selection_set(doc_id)
    manager.on_select(None)
    assert manager.current_document == doc_id
    
    # Test opening document
    with patch('tkinter.messagebox.showinfo') as mock_info:
        manager.open_document()
        mock_info.assert_called_once()

def test_error_handling(manager):
    """Test error handling"""
    # Test adding document with error
    with patch('tkinter.messagebox.showerror') as mock_error:
        manager.tree.insert = MagicMock(side_effect=Exception("Insert error"))
        manager.add_document("Test Doc", "Content")
        mock_error.assert_called_once()

def test_document_filtering(manager):
    """Test document filtering"""
    # Add test documents
    docs = [
        ("Test 1", "Content 1"),
        ("Test 2", "Content 2"),
        ("Other 1", "Content 3"),
        ("Other 2", "Content 4"),
        ("Mixed Test", "Content 5")
    ]
    for title, content in docs:
        manager.add_document(title, content)
    
    # Test various search terms
    test_cases = [
        ("Test", 3),  # Should find 3 documents with "Test"
        ("Other", 2),  # Should find 2 documents with "Other"
        ("Mixed", 1),  # Should find 1 document with "Mixed"
        ("Nonexistent", 0),  # Should find no documents
        ("", 5)  # Should show all documents
    ]
    
    for search_term, expected_count in test_cases:
        manager.search_var.set(search_term)
        visible_items = manager.tree.get_children()
        assert len(visible_items) == expected_count

def test_tree_view_interaction(manager):
    """Test tree view interactions"""
    # Add test document
    manager.add_document("Test Doc", "Content")
    doc_id = manager.tree.get_children()[0]
    
    # Test selection
    manager.tree.selection_set(doc_id)
    manager.on_select(None)
    assert manager.current_document == doc_id
    
    # Test double click
    with patch('tkinter.messagebox.showinfo') as mock_info:
        manager.on_double_click(None)
        mock_info.assert_called_once()

def test_document_persistence(manager):
    """Test document persistence"""
    # Add test documents
    docs = [
        ("Doc 1", "Content 1"),
        ("Doc 2", "Content 2"),
        ("Doc 3", "Content 3")
    ]
    for title, content in docs:
        manager.add_document(title, content)
    
    # Verify documents are stored
    assert len(manager.documents) == 3
    assert all(doc['title'] in [d[0] for d in docs] 
              for doc in manager.documents.values())
    
    # Test document loading (currently uses dummy data)
    manager.documents.clear()
    manager.tree.delete(*manager.tree.get_children())
    manager.load_documents()
    assert len(manager.documents) > 0

def test_search_performance(manager):
    """Test search performance with many documents"""
    # Add many documents
    for i in range(100):
        manager.add_document(f"Test Doc {i}", f"Content {i}")
    
    # Measure search time
    start_time = manager.tree.tk.call('clock', 'milliseconds')
    manager.search_var.set("Test")
    end_time = manager.tree.tk.call('clock', 'milliseconds')
    
    # Verify search is reasonably fast
    assert end_time - start_time < 100  # Should take less than 100ms

def test_memory_management(manager):
    """Test memory management"""
    initial_items = len(manager.tree.get_children())
    
    # Add and remove documents multiple times
    for i in range(100):
        manager.add_document(f"Test {i}", f"Content {i}")
    
    for item in manager.tree.get_children():
        manager.tree.delete(item)
    
    # Verify cleanup
    assert len(manager.tree.get_children()) == initial_items

def test_large_document_handling(manager):
    """Test handling of large documents"""
    # Create a large document
    large_content = "Test content\n" * 1000
    manager.add_document("Large Doc", large_content)
    
    # Test search performance with large content
    start_time = manager.tree.tk.call('clock', 'milliseconds')
    manager.search_var.set("Large")
    end_time = manager.tree.tk.call('clock', 'milliseconds')
    
    # Verify search remains responsive
    assert end_time - start_time < 100  # Should take less than 100ms

def test_concurrent_operations(manager):
    """Test concurrent operations"""
    # Simulate rapid document additions and searches
    for i in range(10):
        manager.add_document(f"Doc {i}", f"Content {i}")
        manager.search_var.set(str(i))
        manager.tree.selection_set(manager.tree.get_children()[-1])
        manager.on_select(None)
    
    # Verify final state is consistent
    assert len(manager.documents) == 10
    assert len(manager.tree.get_children()) > 0
    assert manager.current_document is not None 