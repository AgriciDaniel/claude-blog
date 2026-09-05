#!/usr/bin/env python3
"""
Notebook Library Management for NotebookLM
Manages a library of NotebookLM notebooks with metadata
Based on the MCP server implementation
"""

import json
import argparse
import uuid
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from config import DATA_DIR, LIBRARY_FILE, validate_notebook_url


class NotebookLibrary:
    """Manages a collection of NotebookLM notebooks with metadata"""

    def __init__(self):
        """Initialize the notebook library"""
        # Store data within the skill directory
        self.data_dir = DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)
        try:
            self.data_dir.chmod(0o700)
        except OSError:
            pass

        self.library_file = LIBRARY_FILE
        self.notebooks: Dict[str, Dict[str, Any]] = {}
        self.active_notebook_id: Optional[str] = None

        # Load existing library
        self._load_library()

    def _load_library(self):
        """Load library from disk"""
        if self.library_file.exists():
            try:
                with open(self.library_file, 'r') as f:
                    data = json.load(f)
                    self.notebooks = data.get('notebooks', {})
                    self.active_notebook_id = data.get('active_notebook_id')
                    print(f"📚 Loaded library with {len(self.notebooks)} notebooks")
            except Exception as e:
                print(f"⚠️ Error loading library: {e}")
                self.notebooks = {}
                self.active_notebook_id = None
        else:
            self._save_library()

    def _save_library(self):
        """Save library to disk"""
        try:
            data = {
                'notebooks': self.notebooks,
                'active_notebook_id': self.active_notebook_id,
                'updated_at': datetime.now().isoformat()
            }
            with open(self.library_file, 'w') as f:
                json.dump(data, f, indent=2)
            try:
                self.library_file.chmod(0o600)
            except OSError:
                pass
        except Exception as e:
            print(f"❌ Error saving library: {e}")

    def _slugify(self, value: str) -> str:
        """Create a bounded notebook ID safe for JSON keys and logs."""
        slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
        return slug[:80] or f"notebook-{uuid.uuid4().hex[:8]}"

    def add_notebook(
        self,
        url: str,
        name: str,
        description: str,
        topics: List[str],
        content_types: Optional[List[str]] = None,
        use_cases: Optional[List[str]] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Add a new notebook to the library

        Args:
            url: NotebookLM notebook URL
            name: Display name for the notebook
            description: What's in this notebook
            topics: Topics covered
            content_types: Types of content (optional)
            use_cases: When to use this notebook (optional)
            tags: Additional tags for organization (optional)

        Returns:
            The created notebook object
        """
        url = validate_notebook_url(url)

        # Generate ID from name
        notebook_id = self._slugify(name)

        # Check for duplicates
        if notebook_id in self.notebooks:
            raise ValueError(f"Notebook with ID '{notebook_id}' already exists")

        # Create notebook object
        notebook = {
            'id': notebook_id,
            'url': url,
            'name': name,
            'description': description,
            'topics': topics,
            'content_types': content_types or [],
            'use_cases': use_cases or [],
            'tags': tags or [],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'use_count': 0,
            'last_used': None
        }

        # Add to library
        self.notebooks[notebook_id] = notebook

        # Set as active if it's the first notebook
        if len(self.notebooks) == 1:
            self.active_notebook_id = notebook_id

        self._save_library()

        print(f"✅ Added notebook: {name} ({notebook_id})")
        return notebook

    def remove_notebook(self, notebook_id: str) -> bool:
        """
        Remove a notebook from the library

        Args:
            notebook_id: ID of notebook to remove

        Returns:
            True if removed, False if not found
        """
        if notebook_id in self.notebooks:
            del self.notebooks[notebook_id]

            # Clear active if it was removed
            if self.active_notebook_id == notebook_id:
                self.active_notebook_id = None
                # Set new active if there are other notebooks
                if self.notebooks:
                    self.active_notebook_id = list(self.notebooks.keys())[0]

            self._save_library()
            print(f"✅ Removed notebook: {notebook_id}")
            return True

        print(f"⚠️ Notebook not found: {notebook_id}")
        return False

    def update_notebook(
        self,
        notebook_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        topics: Optional[List[str]] = None,
        content_types: Optional[List[str]] = None,
        use_cases: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update notebook metadata

        Args:
            notebook_id: ID of notebook to update
            Other args: Fields to update (None = keep existing)

        Returns:
            Updated notebook object
        """
        if notebook_id not in self.notebooks:
            raise ValueError(f"Notebook not found: {notebook_id}")

        notebook = self.notebooks[notebook_id]

        # Update fields if provided
        if name is not None:
            notebook['name'] = name
        if description is not None:
            notebook['description'] = description
        if topics is not None:
            notebook['topics'] = topics
        if content_types is not None:
            notebook['content_types'] = content_types
        if use_cases is not None:
            notebook['use_cases'] = use_cases
        if tags is not None:
            notebook['tags'] = tags
        if url is not None:
            notebook['url'] = validate_notebook_url(url)

        notebook['updated_at'] = datetime.now().isoformat()

        self._save_library()
        print(f"✅ Updated notebook: {notebook['name']}")
        return notebook

    def get_notebook(self, notebook_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific notebook by ID"""
        return self.notebooks.get(notebook_id)

    def list_notebooks(self) -> List[Dict[str, Any]]:
        """List all notebooks in the library"""
        return list(self.notebooks.values())

    def search_notebooks(self, query: str) -> List[Dict[str, Any]]:
        """
        Search notebooks by query

        Args:
            query: Search query (searches name, description, topics, tags)

        Returns:
            List of matching notebooks
        """
        query_lower = query.lower()
        results = []

        for notebook in self.notebooks.values():
            # Search in various fields
            searchable = [
                notebook['name'].lower(),
                notebook['description'].lower(),
                ' '.join(notebook['topics']).lower(),
                ' '.join(notebook['tags']).lower(),
                ' '.join(notebook.get('use_cases', [])).lower()
            ]

            if any(query_lower in field for field in searchable):
                results.append(notebook)

        return results

    def select_notebook(self, notebook_id: str) -> Dict[str, Any]:
        """
        Set a notebook as active

        Args:
            notebook_id: ID of notebook to activate

        Returns:
            The activated notebook
        """
        if notebook_id not in self.notebooks:
            raise ValueError(f"Notebook not found: {notebook_id}")

        self.active_notebook_id = notebook_id
        self._save_library()

        notebook = self.notebooks[notebook_id]
        print(f"✅ Activated notebook: {notebook['name']}")
        return notebook

    def get_active_notebook(self) -> Optional[Dict[str, Any]]:
        """Get the currently active notebook"""
        if self.active_notebook_id:
            return self.notebooks.get(self.active_notebook_id)
        return None

    def increment_use_count(self, notebook_id: str) -> Dict[str, Any]:
        """
        Increment usage counter for a notebook

        Args:
            notebook_id: ID of notebook that was used

        Returns:
            Updated notebook
        """
        if notebook_id not in self.notebooks:
            raise ValueError(f"Notebook not found: {notebook_id}")

        notebook = self.notebooks[notebook_id]
        notebook['use_count'] += 1
        notebook['last_used'] = datetime.now().isoformat()

        self._save_library()
        return notebook

    def get_stats(self) -> Dict[str, Any]:
        """Get library statistics"""
        total_notebooks = len(self.notebooks)
        total_topics = set()
        total_use_count = 0

        for notebook in self.notebooks.values():
            total_topics.update(notebook['topics'])
            total_use_count += notebook['use_count']

        # Find most used
        most_used = None
        if self.notebooks:
            most_used = max(
                self.notebooks.values(),
                key=lambda n: n['use_count']
            )

        return {
            'total_notebooks': total_notebooks,
            'total_topics': len(total_topics),
            'total_use_count': total_use_count,
            'active_notebook': self.get_active_notebook(),
            'most_used_notebook': most_used,
            'library_path': str(self.library_file)
        }


def main():
    """Command-line interface for notebook management"""
    parser = argparse.ArgumentParser(description='Manage NotebookLM library')
    parser.add_argument('--json', action='store_true', help='Output structured JSON')

    subparsers = parser.add_subparsers(dest='command', help='Commands')
    json_parent = argparse.ArgumentParser(add_help=False)
    json_parent.add_argument('--json', action='store_true', help='Output structured JSON')

    # Closes audit VULN-037: input length caps on CLI string args.
    # `add_notebook` derives notebook_id = name.lower().replace(' ', '-')
    # with no length limit, so an unbounded --name becomes a giant filesystem
    # key in library.json.
    def _bounded(max_len: int):
        def _check(s: str) -> str:
            if len(s) > max_len:
                raise argparse.ArgumentTypeError(
                    f"value too long ({len(s)} chars, max {max_len})"
                )
            return s
        return _check

    # Add command
    add_parser = subparsers.add_parser('add', parents=[json_parent], help='Add a notebook')
    add_parser.add_argument('--url', required=True, type=_bounded(2000),
                            help='NotebookLM URL (max 2000 chars)')
    add_parser.add_argument('--name', required=True, type=_bounded(200),
                            help='Display name (max 200 chars)')
    add_parser.add_argument('--description', required=True, type=_bounded(2000),
                            help='Description (max 2000 chars)')
    add_parser.add_argument('--topics', required=True, type=_bounded(1000),
                            help='Comma-separated topics (max 1000 chars)')
    add_parser.add_argument('--use-cases', type=_bounded(1000),
                            help='Comma-separated use cases (max 1000 chars)')
    add_parser.add_argument('--tags', type=_bounded(500),
                            help='Comma-separated tags (max 500 chars)')

    # List command
    subparsers.add_parser('list', parents=[json_parent], help='List all notebooks')

    # Search command
    search_parser = subparsers.add_parser('search', parents=[json_parent], help='Search notebooks')
    search_parser.add_argument('--query', required=True, help='Search query')

    # Activate command
    activate_parser = subparsers.add_parser('activate', parents=[json_parent], help='Set active notebook')
    activate_parser.add_argument('--id', required=True, help='Notebook ID')

    # Remove command
    remove_parser = subparsers.add_parser('remove', parents=[json_parent], help='Remove a notebook')
    remove_parser.add_argument('--id', required=True, help='Notebook ID')

    # Stats command
    subparsers.add_parser('stats', parents=[json_parent], help='Show library statistics')

    args = parser.parse_args()

    # Initialize library
    library = NotebookLibrary()

    # Execute command
    if args.command == 'add':
        topics = [t.strip() for t in args.topics.split(',')]
        use_cases = [u.strip() for u in args.use_cases.split(',')] if args.use_cases else None
        tags = [t.strip() for t in args.tags.split(',')] if args.tags else None

        notebook = library.add_notebook(
            url=args.url,
            name=args.name,
            description=args.description,
            topics=topics,
            use_cases=use_cases,
            tags=tags
        )
        print(json.dumps(notebook, indent=2))

    elif args.command == 'list':
        notebooks = library.list_notebooks()
        if args.json:
            print(json.dumps({
                "status": "success",
                "notebooks": notebooks,
                "active_notebook_id": library.active_notebook_id,
            }, indent=2))
            return
        if notebooks:
            print("\n📚 Notebook Library:")
            for notebook in notebooks:
                active = " [ACTIVE]" if notebook['id'] == library.active_notebook_id else ""
                print(f"\n  📓 {notebook['name']}{active}")
                print(f"     ID: {notebook['id']}")
                print(f"     Topics: {', '.join(notebook['topics'])}")
                print(f"     Uses: {notebook['use_count']}")
        else:
            print("📚 Library is empty. Add notebooks with: notebook_manager.py add")

    elif args.command == 'search':
        results = library.search_notebooks(args.query)
        if args.json:
            print(json.dumps({"status": "success", "results": results}, indent=2))
            return
        if results:
            print(f"\n🔍 Found {len(results)} notebooks:")
            for notebook in results:
                print(f"\n  📓 {notebook['name']} ({notebook['id']})")
                print(f"     {notebook['description']}")
        else:
            print(f"🔍 No notebooks found for: {args.query}")

    elif args.command == 'activate':
        notebook = library.select_notebook(args.id)
        if args.json:
            print(json.dumps({"status": "success", "active_notebook": notebook}, indent=2))
            return
        print(f"Now using: {notebook['name']}")

    elif args.command == 'remove':
        removed = library.remove_notebook(args.id)
        if args.json:
            print(json.dumps({"status": "success" if removed else "error", "removed": removed, "id": args.id}, indent=2))
            return
        if removed:
            print("Notebook removed from library")

    elif args.command == 'stats':
        stats = library.get_stats()
        if args.json:
            print(json.dumps({"status": "success", "stats": stats}, indent=2))
            return
        print("\n📊 Library Statistics:")
        print(f"  Total notebooks: {stats['total_notebooks']}")
        print(f"  Total topics: {stats['total_topics']}")
        print(f"  Total uses: {stats['total_use_count']}")
        if stats['active_notebook']:
            print(f"  Active: {stats['active_notebook']['name']}")
        if stats['most_used_notebook']:
            print(f"  Most used: {stats['most_used_notebook']['name']} ({stats['most_used_notebook']['use_count']} uses)")
        print(f"  Library path: {stats['library_path']}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
