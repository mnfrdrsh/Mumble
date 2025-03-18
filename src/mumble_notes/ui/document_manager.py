"""
Document manager component for Mumble Notes
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import json
import logging
from typing import Dict, List, Optional

class DocumentManager(ttk.Frame):
    """Document manager with tree view for organizing notes"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.logger = logging.getLogger('mumble.notes.docmanager')
        
        # Configure grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create search bar
        self.create_search_bar()
        
        # Create tree view
        self.create_tree_view()
        
        # Initialize document storage
        self.documents: Dict[str, dict] = {}
        self.current_document: Optional[str] = None
        
        # Load documents
        self.load_documents()
        
    def create_search_bar(self):
        """Create the search bar"""
        search_frame = ttk.Frame(self)
        search_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # Search entry
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_documents)
        
        search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=25
        )
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Clear button
        ttk.Button(
            search_frame,
            text="×",
            width=3,
            command=self.clear_search
        ).pack(side=tk.RIGHT)
        
    def create_tree_view(self):
        """Create the tree view for documents"""
        # Create frame for tree and scrollbar
        tree_frame = ttk.Frame(self)
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Configure frame grid
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Create tree view
        self.tree = ttk.Treeview(
            tree_frame,
            selectmode='browse',
            show='tree'
        )
        
        # Create scrollbar
        scrollbar = ttk.Scrollbar(
            tree_frame,
            orient=tk.VERTICAL,
            command=self.tree.yview
        )
        
        # Configure tree view scrolling
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid tree and scrollbar
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Bind events
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        self.tree.bind('<Double-1>', self.on_double_click)
        
    def load_documents(self):
        """Load documents from storage"""
        # This is a placeholder - will be implemented with actual storage
        self.logger.info("Loading documents (not implemented)")
        
        # Add some dummy documents for testing
        self.add_document("Welcome", "Welcome to Mumble Notes!")
        self.add_document("Getting Started", "Learn how to use Mumble Notes...")
        
    def add_document(self, title: str, content: str = ""):
        """Add a new document"""
        try:
            doc_id = f"doc_{len(self.documents)}"
            self.documents[doc_id] = {
                'title': title,
                'content': content,
                'created': None,  # Will add timestamp
                'modified': None  # Will add timestamp
            }
            
            # Add to tree view
            self.tree.insert('', 'end', doc_id, text=title)
            self.logger.info(f"Added document: {title}")
            
        except Exception as e:
            self.logger.error(f"Error adding document: {e}")
            messagebox.showerror("Error", "Could not add document")
            
    def open_document(self):
        """Open the selected document"""
        selection = self.tree.selection()
        if selection:
            doc_id = selection[0]
            doc = self.documents.get(doc_id)
            if doc:
                # This is a placeholder - will implement actual document opening
                messagebox.showinfo("Open", f"Opening {doc['title']}...")
                self.logger.info(f"Opening document: {doc['title']}")
                
    def filter_documents(self, *args):
        """Filter documents based on search text"""
        search_text = self.search_var.get().lower()
        
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Add matching documents
        for doc_id, doc in self.documents.items():
            if search_text in doc['title'].lower():
                self.tree.insert('', 'end', doc_id, text=doc['title'])
                
    def clear_search(self):
        """Clear the search field"""
        self.search_var.set("")
        
    def on_select(self, event):
        """Handle tree item selection"""
        selection = self.tree.selection()
        if selection:
            self.current_document = selection[0]
            
    def on_double_click(self, event):
        """Handle double click on tree item"""
        self.open_document() 