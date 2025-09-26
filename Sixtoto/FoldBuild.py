#!/usr/bin/env python3
"""
Professional Folder / Folder Tree Creator 
Sixtoto v2.1 - COMPLETE
A feature-rich, cross-platform Python application for creating folder structures.

Features:
- Interactive Folder building with real time visual updates
- Copy paste mode for making tree structures  
- Folder scanning mode 
- Auto detection of files vs folders
- Cross platform compatibility (Windows/Linux/macOS)
- Professional command interface 

Author: .vixnz

"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional, Dict


class TreeCreator:
    """Main class for creating folder tree structures."""
    
    def __init__(self):
        self.structure = []  # List of (name, depth, is_file)
        self.current_depth = 0
        self.version = "2.1"
    
    def clear_screen(self):
        """Clear terminal screen for better UX."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Print application header."""
        print("🌳 Professional Folder Tree Creator v" + self.version)
        print("=" * 60)
        print("Create, scan, and replicate folder structures easily")
        print("=" * 60)
    
    def print_commands_summary(self):
        """Print quick command reference."""
        print("\n💡 Quick Commands:")
        print("  add <name>     indent/outdent     show     remove <#>")
        print("  help          paste-mode         done     clear")
        print(f"📍 Current depth: {self.current_depth} │ Items: {len(self.structure)}")
    
    def add_item(self, name: str, depth: int, is_file: bool = None):
        """Add an item to the structure with auto-detection."""
        # Clean the name
        name = name.strip()
        if not name:
            return False
        
        # Auto-detect file vs folder if not specified
        if is_file is None:
            # Files have extensions, folders don't (with exceptions)
            basename = os.path.basename(name)
            is_file = ('.' in basename and 
                      not basename.startswith('.') and 
                      not name.endswith('/'))
        
        self.structure.append((name, depth, is_file))
        return True
    
    def remove_item(self, index: int):
        """Remove an item from the structure."""
        if 0 <= index < len(self.structure):
            removed = self.structure.pop(index)
            return removed[0]
        return None
    
    def display_tree_with_updates(self, highlight_index: int = -1):
        """Display the tree with real-time updates and optional highlighting."""
        self.clear_screen()
        self.print_header()
        
        if not self.structure:
            print("\n📋 Tree Structure: (empty)")
            print("   Start by typing: add <folder_or_file_name>")
        else:
            print(f"\n📋 Tree Structure: ({len(self.structure)} items)")
            print("─" * 50)
            
            for i, (name, depth, is_file) in enumerate(self.structure):
                # Generate tree prefix
                prefix = self.get_tree_prefix(i, depth)
                
                # Choose icon
                icon = "📄" if is_file else "📁"
                
                # Highlight if this is the item we just added/modified
                highlight = "→ " if i == highlight_index else "  "
                
                print(f"{highlight}{i:2d}: {prefix}{icon} {name}")
            
            print("─" * 50)
        
        self.print_commands_summary()
    
    def get_tree_prefix(self, index: int, depth: int):
        """Generate professional tree prefix symbols."""
        if depth == 0:
            return ""
        
        prefix = ""
        
        # Build prefix level by level
        for level in range(depth):
            if level == depth - 1:
                # Current level - check if last child
                is_last = self.is_last_child_at_depth(index, depth)
                prefix += "└── " if is_last else "├── "
            else:
                # Parent level - check if more siblings exist
                has_siblings = self.has_more_siblings_at_level(index, level + 1)
                prefix += "    " if not has_siblings else "│   "
        
        return prefix
    
    def is_last_child_at_depth(self, index: int, depth: int):
        """Check if item is the last child at its depth."""
        current_depth = self.structure[index][1]
        parent_depth = current_depth - 1
        
        # Look ahead for more items at same depth
        for i in range(index + 1, len(self.structure)):
            item_depth = self.structure[i][1]
            
            if item_depth <= parent_depth:
                break
                
            if item_depth == current_depth:
                return False
        
        return True
    
    def has_more_siblings_at_level(self, index: int, level: int):
        """Check if more siblings exist at a specific level."""
        for i in range(index + 1, len(self.structure)):
            item_depth = self.structure[i][1]
            
            if item_depth <= level:
                if item_depth == level:
                    return True
                else:
                    break
        
        return False
    
    def scan_directory(self, directory_path: str, max_depth: int = None, show_hidden: bool = False):
        """Scan an existing directory and populate structure."""
        path = Path(directory_path).resolve()
        
        if not path.exists():
            return False, f"Directory '{directory_path}' does not exist"
        
        if not path.is_dir():
            return False, f"'{directory_path}' is not a directory"
        
        self.structure.clear()
        
        try:
            # Recursively scan directory - FIXED VERSION
            self._scan_recursive(path, 0, max_depth, show_hidden)
            
            return True, f"Successfully scanned {len(self.structure)} items"
            
        except PermissionError:
            return False, f"Permission denied accessing '{directory_path}'"
        except Exception as e:
            return False, f"Error scanning directory: {str(e)}"
    
    def _scan_recursive(self, current_path: Path, depth: int, max_depth: Optional[int], show_hidden: bool):
        """Recursively scan directory contents - FIXED to maintain proper structure."""
        if max_depth is not None and depth > max_depth:
            return
        
        try:
            # Get all items in current directory
            entries = list(current_path.iterdir())
            
            # Filter hidden files if not requested
            if not show_hidden:
                entries = [e for e in entries if not e.name.startswith('.')]
            
            # Sort entries (directories first, then files, alphabetically within each group)
            entries.sort(key=lambda x: (x.is_file(), x.name.lower()))
            
            for entry in entries:
                relative_name = entry.name
                is_file = entry.is_file()
                
                # Add this item to the structure at current depth
                self.structure.append((relative_name, depth, is_file))
                
                # If it's a directory and we haven't reached max depth, recurse into it
                if entry.is_dir() and (max_depth is None or depth < max_depth):
                    self._scan_recursive(entry, depth + 1, max_depth, show_hidden)
                    
        except PermissionError:
            # Add a note about permission denied directories
            self.structure.append(("[Permission Denied]", depth, False))
    
    def display_scanned_tree(self, base_path: str, stats: Dict = None):
        """Display scanned tree with additional information."""
        self.clear_screen()
        self.print_header()
        
        print(f"\n🔍 SCANNED DIRECTORY: {base_path}")
        print("=" * 60)
        
        if stats:
            print(f"📊 Stats: {stats.get('dirs', 0)} directories, {stats.get('files', 0)} files, {stats.get('total', 0)} total")
            if stats.get('max_depth'):
                print(f"📏 Max depth: {stats['max_depth']} levels")
            print("─" * 50)
        
        if not self.structure:
            print("   (empty directory)")
        else:
            # Display tree structure
            for i, (name, depth, is_file) in enumerate(self.structure):
                prefix = self.get_tree_prefix(i, depth)
                icon = "📄" if is_file else "📁"
                print(f"  {i:3d}: {prefix}{icon} {name}")
        
        print("─" * 50)
        print("\n💡 Commands: copy, save, export, back, help")
    
    def scan_mode(self):
        """Handle directory scanning mode."""
        self.clear_screen()
        self.print_header()
        
        print("\n🔍 DIRECTORY SCANNING MODE")
        print("=" * 50)
        print("Analyze existing folder structures and optionally recreate them.")
        print("\nOptions:")
        print("  • Scan any directory on your system")
        print("  • Control scan depth and hidden file visibility")
        print("  • Copy structure to create elsewhere")
        print("  • Export structure to text file")
        
        while True:
            print("\n📂 Enter directory to scan:")
            print("   Examples: . (current), ~ (home), /path/to/folder, C:\\Users")
            
            dir_path = input("Directory path (or 'back' to return): ").strip()
            
            if dir_path.lower() == 'back':
                return "interactive"
            
            if not dir_path:
                print("⚠️  Please enter a directory path.")
                continue
            
            # Handle special paths
            if dir_path == '.':
                dir_path = os.getcwd()
            elif dir_path == '~':
                dir_path = str(Path.home())
            else:
                dir_path = os.path.expanduser(dir_path)
            
            # Get scanning options
            print(f"\n⚙️  SCAN OPTIONS for: {dir_path}")
            
            # Max depth
            max_depth = None
            depth_input = input("Max depth (Enter for unlimited, or number): ").strip()
            if depth_input.isdigit():
                max_depth = int(depth_input)
            
            # Hidden files
            show_hidden = input("Include hidden files? (y/n, default=n): ").strip().lower() in ['y', 'yes']
            
            print("\n🔄 Scanning directory...")
            
            # Perform scan
            success, message = self.scan_directory(dir_path, max_depth, show_hidden)
            
            if not success:
                print(f"❌ {message}")
                retry = input("\nTry different directory? (y/n): ").strip().lower()
                if retry not in ['y', 'yes']:
                    return "interactive"
                continue
            
            # Calculate statistics
            stats = self._calculate_scan_stats()
            
            # Display results
            self.display_scanned_tree(dir_path, stats)
            print(f"✅ {message}")
            
            # Post-scan options
            return self._handle_scan_results(dir_path)
    
    def _calculate_scan_stats(self):
        """Calculate statistics for scanned structure."""
        if not self.structure:
            return {}
        
        dirs = sum(1 for _, _, is_file in self.structure if not is_file)
        files = sum(1 for _, _, is_file in self.structure if is_file)
        max_depth = max(depth for _, depth, _ in self.structure) if self.structure else 0
        
        return {
            'dirs': dirs,
            'files': files,
            'total': len(self.structure),
            'max_depth': max_depth
        }
    
    def _handle_scan_results(self, scanned_path: str):
        """Handle options after successful directory scan."""
        while True:
            print(f"\n🎯 SCAN COMPLETE - What would you like to do?")
            print("  1. Copy structure to new location")
            print("  2. Save structure to text file")
            print("  3. Edit structure in interactive mode")
            print("  4. Scan different directory")
            print("  5. Export as copy-paste format")
            print("  6. Return to main menu")
            
            choice = input("\nSelect option (1-6): ").strip()
            
            if choice == '1':
                return "create"
            elif choice == '2':
                self._export_structure_to_file(scanned_path)
            elif choice == '3':
                print("🔄 Switching to interactive mode with scanned structure...")
                input("Press Enter to continue...")
                return "interactive"
            elif choice == '4':
                return "scan_mode"
            elif choice == '5':
                self._export_structure_display()
            elif choice == '6':
                return "interactive"
            else:
                print("❌ Invalid choice. Please select 1-6.")
    
    def _export_structure_to_file(self, source_path: str):
        """Export scanned structure to a text file."""
        if not self.structure:
            print("⚠️  No structure to export!")
            return
        
        # Generate filename
        source_name = Path(source_path).name or "root"
        default_filename = f"{source_name}_structure.txt"
        
        filename = input(f"Export filename (default: {default_filename}): ").strip() 
        if not filename:
            filename = default_filename
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Directory Structure: {source_path}\n")
                f.write(f"Generated by Sixtoto v{self.version}\n")
                f.write("=" * 60 + "\n\n")
                
                # Write tree structure
                for i, (name, depth, is_file) in enumerate(self.structure):
                    prefix = self.get_tree_prefix(i, depth)
                    icon = "📄" if is_file else "📁"
                    f.write(f"{prefix}{icon} {name}\n")
                
                # Write statistics
                stats = self._calculate_scan_stats()
                f.write(f"\n" + "=" * 60 + "\n")
                f.write(f"Statistics:\n")
                f.write(f"  Directories: {stats.get('dirs', 0)}\n")
                f.write(f"  Files: {stats.get('files', 0)}\n")
                f.write(f"  Total items: {stats.get('total', 0)}\n")
                f.write(f"  Max depth: {stats.get('max_depth', 0)}\n")
            
            print(f"✅ Structure exported to: {filename}")
            
        except Exception as e:
            print(f"❌ Error exporting to file: {e}")
    
    def _export_structure_display(self):
        """Display structure in copy-paste format."""
        if not self.structure:
            print("⚠️  No structure to display!")
            return
        
        print("\n📋 COPY-PASTE FORMAT:")
        print("=" * 50)
        
        for i, (name, depth, is_file) in enumerate(self.structure):
            prefix = self.get_tree_prefix(i, depth)
            icon = "📄" if is_file else "📁"
            print(f"{prefix}{icon} {name}")
        
        print("=" * 50)
        print("Copy the above structure and paste it elsewhere!")
        input("\nPress Enter to continue...")
    
    def interactive_mode(self):
        """Interactive tree building with real-time updates."""
        print("🚀 Starting Interactive Mode...")
        print("Type 'help' for full command list")
        
        # Show initial state
        self.display_tree_with_updates()
        
        while True:
            try:
                command = input(f"\n[depth {self.current_depth}] > ").strip()
                
                if not command:
                    continue
                
                parts = command.split()
                cmd = parts[0].lower()
                
                # Handle commands
                if cmd in ["add", "a"] and len(parts) >= 2:
                    name = " ".join(parts[1:])  # Support names with spaces
                    is_file = None
                    
                    # Check for flags
                    if name.endswith(" -f"):
                        name = name[:-3].strip()
                        is_file = True
                    elif name.endswith(" -d"):
                        name = name[:-3].strip()
                        is_file = False
                    
                    if self.add_item(name, self.current_depth, is_file):
                        # Show update with highlighting
                        self.display_tree_with_updates(len(self.structure) - 1)
                        print(f"✅ Added: {name} at depth {self.current_depth}")
                    else:
                        print("❌ Invalid name!")
                
                elif cmd in ["indent", "in", ">"]:
                    self.current_depth += 1
                    self.display_tree_with_updates()
                    print(f"📍 Depth increased to {self.current_depth}")
                
                elif cmd in ["outdent", "out", "<"]:
                    if self.current_depth > 0:
                        self.current_depth -= 1
                        self.display_tree_with_updates()
                        print(f"📍 Depth decreased to {self.current_depth}")
                    else:
                        print("⚠️  Already at root level!")
                
                elif cmd in ["depth", "d"] and len(parts) == 2:
                    try:
                        new_depth = int(parts[1])
                        if new_depth >= 0:
                            self.current_depth = new_depth
                            self.display_tree_with_updates()
                            print(f"📍 Depth set to {self.current_depth}")
                        else:
                            print("❌ Depth must be 0 or positive!")
                    except ValueError:
                        print("❌ Invalid depth number!")
                
                elif cmd in ["remove", "rm", "delete"] and len(parts) == 2:
                    try:
                        index = int(parts[1])
                        removed = self.remove_item(index)
                        if removed:
                            self.display_tree_with_updates()
                            print(f"🗑️  Removed: {removed}")
                        else:
                            print("❌ Invalid index!")
                    except ValueError:
                        print("❌ Invalid index number!")
                
                elif cmd in ["show", "display", "tree"]:
                    self.display_tree_with_updates()
                
                elif cmd in ["clear", "reset"]:
                    confirm = input("🔄 Clear entire tree? (y/n): ").strip().lower()
                    if confirm in ['y', 'yes']:
                        self.structure.clear()
                        self.current_depth = 0
                        self.display_tree_with_updates()
                        print("🗑️  Tree cleared!")
                
                elif cmd in ["scan-mode", "scan", "analyze"]:
                    return "scan_mode"
                
                elif cmd in ["paste-mode", "paste", "copy-paste"]:
                    return "paste_mode"
                
                elif cmd in ["done", "finish", "create"]:
                    if self.structure:
                        return "create"
                    else:
                        print("⚠️  Tree is empty! Add items first or use scan-mode.")
                
                elif cmd in ["help", "h", "?"]:
                    self.show_help()
                
                elif cmd in ["exit", "quit", "q"]:
                    confirm = input("🚪 Exit without creating? (y/n): ").strip().lower()
                    if confirm in ['y', 'yes']:
                        return "exit"
                
                else:
                    print(f"❌ Unknown command: '{cmd}'. Type 'help' for available commands.")
                
            except KeyboardInterrupt:
                print("\n\n⚠️  Use 'exit' to quit or 'done' to create structure.")
            except EOFError:
                return "exit"
    
    def show_help(self):
        """Display comprehensive help information."""
        help_text = """
🆘 COMPREHENSIVE COMMAND REFERENCE
═══════════════════════════════════════════════════════════════

📝 ADDING ITEMS:
  add <name>              Add item (auto-detects file vs folder)
  add <name> -f           Force add as file
  add <name> -d           Force add as folder
  a <name>                Short form of 'add'

📐 NAVIGATION:
  indent / in / >         Increase depth (go deeper into tree)
  outdent / out / <       Decrease depth (go back up)
  depth <n> / d <n>       Jump to specific depth level (0,1,2...)

🔧 EDITING:
  remove <index> / rm <#> Remove item by its index number
  clear / reset           Clear entire tree structure
  show / display / tree   Refresh and display current tree

🔍 SCANNING:
  scan-mode / scan        Switch to directory scanning mode
  analyze                 Alias for scan mode

🔀 MODES:
  paste-mode / paste      Switch to copy-paste mode for existing trees
  help / h / ?            Show this help menu

🎯 COMPLETION:
  done / finish / create  Finish building and create the structure
  exit / quit / q         Exit without creating

💡 TIPS:
  • Items with extensions (file.txt) are auto-detected as files
  • Items without extensions are treated as folders
  • Use -f or -d flags to override auto-detection
  • Index numbers are shown on the left (0, 1, 2...)
  • Tree updates in real-time as you build it
  • Scan mode can analyze any directory and recreate it

📋 EXAMPLE WORKFLOWS:

  INTERACTIVE BUILD:
  > add MyProject
  > indent
  > add src
  > add config.py -f
  > done

  DIRECTORY SCANNING:
  > scan-mode
  > /path/to/existing/project
  > copy to new location

Press Enter to continue..."""
        
        print(help_text)
        input()
        self.display_tree_with_updates()
    
    def paste_mode(self):
        """Handle copy-paste mode for existing tree structures."""
        self.clear_screen()
        self.print_header()
        
        print("\n📋 COPY-PASTE MODE")
        print("=" * 50)
        print("Paste your existing folder tree structure below.")
        print("\nSupported formats:")
        print("  • Standard tree format (├──, └──, │)")
        print("  • Simple indented format")
        print("  • Mixed formats")
        print("\n📝 Input Methods:")
        print("  • Paste multi-line content")
        print("  • Type 'DONE' on new line when finished")
        print("  • Press Enter twice for empty line completion")
        print("  • Use 'back' to return to interactive mode")
        
        print("\n" + "─" * 40)
        print("Example formats:")
        print("/project")
        print("├── src/")
        print("│   ├── main.py")
        print("│   └── utils.py")
        print("└── README.md")
        print("─" * 40)
        
        print("\nPaste your tree structure:")
        
        lines = []
        empty_count = 0
        
        while True:
            try:
                line = input()
                
                if line.strip().upper() == 'DONE':
                    break
                elif line.strip().lower() == 'back':
                    return "interactive"
                
                if line.strip() == '':
                    empty_count += 1
                    if empty_count >= 2:
                        break
                else:
                    empty_count = 0
                
                lines.append(line)
                
            except (EOFError, KeyboardInterrupt):
                break
        
        # Remove trailing empty lines
        while lines and not lines[-1].strip():
            lines.pop()
        
        if not lines:
            print("⚠️  No content provided. Returning to interactive mode.")
            return "interactive"
        
        # Parse the pasted content
        tree_text = '\n'.join(lines)
        parsed_structure = self.parse_tree_text(tree_text)
        
        if not parsed_structure:
            print("❌ Could not parse the tree structure.")
            input("Press Enter to return to interactive mode...")
            return "interactive"
        
        # Update our structure
        self.structure = parsed_structure
        
        # Show parsed result
        self.display_tree_with_updates()
        print(f"✅ Successfully parsed {len(self.structure)} items!")
        
        return "create"
    
    def parse_tree_text(self, text: str) -> List[Tuple[str, int, bool]]:
        """Parse pasted tree text into structure format."""
        lines = text.strip().split('\n')
        structure = []
        
        for line in lines:
            if not line.strip():
                continue
            
            # Extract name and depth
            name, depth = self.parse_tree_line(line)
            if name:
                # Auto-detect file vs folder
                is_file = ('.' in os.path.basename(name) and 
                          not name.startswith('.') and 
                          not name.endswith('/'))
                
                # Clean up name
                if name.startswith('/'):
                    name = name[1:]
                name = name.rstrip('/')
                
                structure.append((name, depth, is_file))
        
        return structure
    
    def parse_tree_line(self, line: str) -> Tuple[Optional[str], int]:
        """Parse a single line to extract name and depth."""
        original_line = line
        
        # Count depth based on indentation and tree characters
        depth = 0
        
        # Remove tree drawing characters and count depth
        if any(char in line for char in ['├', '└', '│', '─']):
            # Count tree structure depth
            depth = line.count('│')
            if '├──' in line or '└──' in line:
                depth = line.count('│')
        else:
            # Simple indentation - count leading spaces/tabs
            stripped = line.lstrip()
            depth = (len(line) - len(stripped)) // 4  # Assume 4 spaces per level
        
        # Extract name by removing all tree characters
        name = line
        for char in ['├──', '└──', '│', '─', '├', '└']:
            name = name.replace(char, '')
        
        name = name.strip()
        
        if not name:
            return None, 0
        
        return name, depth
    
    def convert_to_file_paths(self) -> List[Tuple[str, bool]]:
        """Convert tree structure to file system paths."""
        if not self.structure:
            return []
        
        paths = []
        path_stack = []
        
        for name, depth, is_file in self.structure:
            # Adjust path stack to current depth
            path_stack = path_stack[:depth]
            
            # Build full path
            if path_stack:
                full_path = os.path.join(*path_stack, name)
            else:
                full_path = name
            
            paths.append((full_path, is_file))
            
            # Add directories to path stack
            if not is_file:
                path_stack.append(name)
        
        return paths
    
    def create_file_structure(self, base_path: str, paths: List[Tuple[str, bool]]):
        """Create the actual folder structure on the file system."""
        base = Path(base_path)
        stats = {"dirs": 0, "files": 0, "errors": 0}
        
        print(f"\n🚀 Creating structure in: {base}")
        print("=" * 60)
        
        for item_path, is_file in paths:
            full_path = base / item_path
            
            try:
                if is_file:
                    # Ensure parent directories exist
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    # Create empty file
                    full_path.touch()
                    stats["files"] += 1
                    print(f"📄 {item_path}")
                else:
                    # Create directory
                    full_path.mkdir(parents=True, exist_ok=True)
                    stats["dirs"] += 1
                    print(f"📁 {item_path}/")
                    
            except Exception as e:
                stats["errors"] += 1
                print(f"❌ ERROR: {item_path} - {e}")
        
        # Print summary
        print("=" * 60)
        print(f"✅ COMPLETED: {stats['dirs']} directories, {stats['files']} files")
        if stats["errors"]:
            print(f"⚠️  {stats['errors']} errors occurred")
        print(f"📂 Location: {base}")


def get_base_directory() -> Optional[str]:
    """Get and validate base directory from user."""
    print("\n📂 BASE DIRECTORY SETUP")
    print("=" * 40)
    
    while True:
        base_dir = input("Enter base directory path: ").strip()
        
        if not base_dir:
            print("⚠️  Please enter a directory path.")
            continue
        
        # Handle special paths
        if base_dir == '.':
            base_dir = os.getcwd()
        elif base_dir == '~':
            base_dir = str(Path.home())
        else:
            base_dir = os.path.expanduser(base_dir)
        
        path = Path(base_dir)
        
        try:
            # Check if path exists
            if not path.exists():
                print(f"📁 Directory '{base_dir}' doesn't exist.")
                create = input("Create it? (y/n): ").strip().lower()
                if create in ['y', 'yes']:
                    path.mkdir(parents=True, exist_ok=True)
                    print(f"✅ Created: {base_dir}")
                else:
                    continue
            
            # Check write permissions
            if not os.access(path, os.W_OK):
                print(f"❌ No write permission for '{base_dir}'")
                continue
            
            return str(path.resolve())
            
        except Exception as e:
            print(f"❌ Error with path '{base_dir}': {e}")


def show_welcome_help():
    """Show welcome screen with basic instructions."""
    help_text = """
🎯 WELCOME TO TREE CREATOR!
═══════════════════════════════════════════════

📖 QUICK START GUIDE:

🔨 INTERACTIVE MODE:
  • Build your folder structure step by step
  • Real-time visual updates as you work
  • Commands: add, indent, outdent, remove, help

📋 COPY-PASTE MODE:
  • Paste existing tree structures from anywhere
  • Supports standard tree formats (├──, └──, │)
  • Perfect for recreating documentation examples

🔍 SCAN MODE:
  • Analyze any existing directory on your system
  • Control scan depth and hidden file visibility
  • Export, copy, or recreate scanned structures

💡 FEATURES:
  • Auto-detects files vs folders by extensions
  • Cross-platform (Windows/Linux/macOS)
  • Professional tree visualization
  • Comprehensive error handling

📝 EXAMPLE WORKFLOW:
  1. Choose mode (Interactive/Copy-Paste/Scan)
  2. Build or import your structure
  3. Choose destination directory
  4. Create the folder structure instantly!

Press Enter to continue..."""
    
    print(help_text)
    input()


def main():
    """Main application entry point with professional interface."""
    try:
        creator = TreeCreator()
        
        # Main application loop
        while True:
            # Initial setup
            creator.clear_screen()
            creator.print_header()
            
            print("\n🎯 CHOOSE YOUR MODE:")
            print("  1. Interactive Mode - Build tree step by step")
            print("  2. Copy-Paste Mode  - Paste existing tree structure")
            print("  3. Scan Mode        - Analyze existing directories")
            print("  4. Help & Guide     - Learn how to use the tool")
            print("  5. Exit")
            
            choice = input("\nSelect mode (1-5): ").strip()
            
            # Handle mode selection
            if choice == '1':
                mode_result = creator.interactive_mode()
            elif choice == '2':
                mode_result = creator.paste_mode()
            elif choice == '3':
                mode_result = creator.scan_mode()
            elif choice == '4':
                show_welcome_help()
                continue
            elif choice == '5':
                print("\n👋 Thank you for using Sixtoto!")
                print("🌟 Star us on GitHub if you found this helpful!")
                sys.exit(0)
            else:
                print("❌ Invalid choice. Please select 1-5.")
                input("Press Enter to continue...")
                continue
            
            # Handle mode results
            if mode_result == "exit":
                print("\n👋 Thanks for using Sixtoto!")
                sys.exit(0)
            elif mode_result == "interactive":
                continue  # Return to mode selection
            elif mode_result == "scan_mode":
                # Direct transition to scan mode
                mode_result = creator.scan_mode()
                if mode_result == "exit":
                    print("\n👋 Thanks for using Sixtoto!")
                    sys.exit(0)
                elif mode_result != "create":
                    continue
            elif mode_result == "paste_mode":
                # Direct transition to paste mode
                mode_result = creator.paste_mode()
                if mode_result == "exit":
                    print("\n👋 Thanks for using Sixtoto!")
                    sys.exit(0)
                elif mode_result != "create":
                    continue
            
            # If we reach here, mode_result should be "create"
            if mode_result == "create":
                # Proceed with creation
                if not creator.structure:
                    print("⚠️  No structure to create!")
                    input("Press Enter to return to main menu...")
                    continue
                
                # Show final structure
                creator.display_tree_with_updates()
                print(f"\n🎯 Ready to create structure with {len(creator.structure)} items")
                
                # Confirm creation
                confirm = input("Proceed with creation? (y/n): ").strip().lower()
                if confirm not in ['y', 'yes']:
                    print("🔄 Returning to main menu...")
                    input("Press Enter to continue...")
                    continue
                
                # Get base directory
                base_directory = get_base_directory()
                if not base_directory:
                    print("❌ Invalid base directory. Returning to main menu.")
                    input("Press Enter to continue...")
                    continue
                
                # Convert structure to paths
                paths = creator.convert_to_file_paths()
                
                if not paths:
                    print("⚠️  No valid paths to create!")
                    input("Press Enter to continue...")
                    continue
                
                # Final confirmation with details
                print(f"\n🚀 CREATION SUMMARY:")
                print(f"📂 Base directory: {base_directory}")
                print(f"📊 Items to create: {len(paths)}")
                
                dirs = sum(1 for _, is_file in paths if not is_file)
                files = sum(1 for _, is_file in paths if is_file)
                print(f"   → {dirs} directories")
                print(f"   → {files} files")
                
                final_confirm = input(f"\n✅ Create structure in '{base_directory}'? (y/n): ").strip().lower()
                if final_confirm not in ['y', 'yes']:
                    print("🔄 Creation cancelled. Returning to main menu...")
                    input("Press Enter to continue...")
                    continue
                
                # Create the structure
                try:
                    creator.create_file_structure(base_directory, paths)
                    
                    print(f"\n🎉 SUCCESS! Structure created successfully!")
                    print(f"📂 Location: {base_directory}")
                    
                    # Ask what to do next
                    print(f"\n🎯 What would you like to do next?")
                    print("  1. Create another structure")
                    print("  2. Open created directory (if supported)")
                    print("  3. Exit")
                    
                    next_choice = input("Select option (1-3): ").strip()
                    
                    if next_choice == '1':
                        # Reset and continue
                        creator.structure.clear()
                        creator.current_depth = 0
                        continue
                    elif next_choice == '2':
                        # Try to open directory
                        try:
                            if os.name == 'nt':  # Windows
                                os.startfile(base_directory)
                            elif sys.platform == 'darwin':  # macOS
                                os.system(f'open "{base_directory}"')
                            else:  # Linux and others
                                os.system(f'xdg-open "{base_directory}"')
                            print(f"📂 Opened: {base_directory}")
                        except Exception as e:
                            print(f"⚠️  Could not open directory: {e}")
                            print(f"📂 Manual path: {base_directory}")
                        
                        print("\n👋 Thanks for using Sixtoto!")
                        sys.exit(0)
                    else:
                        print("\n👋 Thanks for using Sixtoto!")
                        sys.exit(0)
                        
                except Exception as e:
                    print(f"\n❌ ERROR during creation: {e}")
                    print("🔄 Returning to main menu...")
                    input("Press Enter to continue...")
                    continue
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        print("👋 Thanks for using Sixtoto!")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 UNEXPECTED ERROR: {e}")
        print("Please report this issue if it persists.")
        print("👋 Thanks for using Sixtoto!")
        sys.exit(1)


if __name__ == "__main__":
    # Entry point with version check
    if sys.version_info < (3, 6):
        print("❌ Python 3.6+ required. Current version:", sys.version)
        sys.exit(1)
    
    # Check for required modules
    try:
        from pathlib import Path
    except ImportError:
        print("❌ Required module 'pathlib' not available.")
        print("Please upgrade to Python 3.6+ or install pathlib2")
        sys.exit(1)
    
    # Run the application
    print("🌳 Professional Folder Tree Creator v2.1")
    print("🚀 Loading...")
    
    try:
        main()
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {e}")
        print("Application will now exit.")
        sys.exit(1)

"""
Professional Folder Tree Creator v2.1
Copyright (c) 2025 vixnz
All rights reserved. Unauthorized copying or claiming as your own is prohibited.
"""

