#!/usr/bin/env python3
# codebase_analyzer.py - Universal codebase analysis tool // [Herramienta universal de análisis de código]
# v1.0.0

import os
import sys
import time
import datetime
import subprocess
import re
import json
from pathlib import Path
from collections import defaultdict

class CodebaseAnalyzer:
    def __init__(self):
        self.output_dir = "00_docs"
        self.ignore_dirs = [".git", "node_modules", "__pycache__", "venv", ".venv", "env", 
                           ".env", "dist", "build", ".idea", ".vscode"]
        self.ignore_files = [".gitignore", ".DS_Store", "Thumbs.db"]
        self.text_extensions = [".py", ".js", ".jsx", ".ts", ".tsx", ".html", ".css", ".scss", 
                              ".md", ".txt", ".json", ".yaml", ".yml", ".xml", ".csv", ".sql", 
                              ".c", ".cpp", ".h", ".java", ".rb", ".php", ".go", ".rs", ".swift",
                              ".kt", ".scala", ".sh", ".ps1", ".bat", ".cmd"]
        self.total_files = 0
        self.total_text_files = 0
        self.project_root = os.getcwd()
        self.has_git = self._check_git()
        
        # Language detection patterns // [Patrones de detección de lenguajes]
        self.language_patterns = {
            "Python": [".py"],
            "JavaScript": [".js", ".jsx"],
            "TypeScript": [".ts", ".tsx"],
            "HTML": [".html", ".htm"],
            "CSS": [".css", ".scss", ".sass", ".less"],
            "Java": [".java"],
            "C#": [".cs"],
            "C/C++": [".c", ".cpp", ".h", ".hpp"],
            "Go": [".go"],
            "Rust": [".rs"],
            "PHP": [".php"],
            "Ruby": [".rb"],
            "Swift": [".swift"],
            "Kotlin": [".kt"],
            "Shell": [".sh", ".bash"],
            "PowerShell": [".ps1"],
            "Markdown": [".md"],
            "JSON": [".json"],
            "YAML": [".yml", ".yaml"],
            "SQL": [".sql"],
        }
        
    def _check_git(self):
        """Check if git is available and if the directory is a git repository. // [Verificar si git está disponible y si el directorio es un repositorio git.]"""
        try:
            subprocess.run(["git", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], 
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def _print_status(self, message):
        """Print a status message with color if supported. // [Imprimir un mensaje de estado con color si es compatible.]"""
        if sys.stdout.isatty():
            print(f"\033[1;36m{message}\033[0m")
        else:
            print(message)
    
    def _print_progress(self, current, total, prefix='', suffix=''):
        """Print a progress bar if in terminal. // [Imprimir una barra de progreso si está en terminal.]"""
        if sys.stdout.isatty():
            bar_length = 30
            filled_length = int(round(bar_length * current / float(total)))
            percents = round(100.0 * current / float(total), 1)
            bar = '█' * filled_length + '-' * (bar_length - filled_length)
            sys.stdout.write(f'\r{prefix} |{bar}| {percents}% {suffix}')
            sys.stdout.flush()
            if current == total:
                print()
        else:
            if current == total:
                print(f"{prefix} {current}/{total} complete")
    
    def _should_ignore(self, path):
        """Check if path should be ignored. // [Verificar si la ruta debe ser ignorada.]"""
        # Skip hidden paths, starting with . // [Omitir rutas ocultas que comienzan con .]
        if os.path.basename(path).startswith('.') and os.path.basename(path) not in ['.', '..']:
            return True
            
        # Skip ignored directories // [Omitir directorios ignorados]
        for ignored in self.ignore_dirs:
            if f"/{ignored}/" in f"{path}/" or path.endswith(f"/{ignored}"):
                return True
        
        # Skip ignored files // [Omitir archivos ignorados]
        if os.path.isfile(path) and os.path.basename(path) in self.ignore_files:
            return True
            
        return False
        
    def _count_lines(self, file_path):
        """Count lines in a text file. // [Contar líneas en un archivo de texto.]"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except Exception:
            return 0
    
    def _is_text_file(self, file_path):
        """Check if a file is text based on extension. // [Verificar si un archivo es texto basado en su extensión.]"""
        _, ext = os.path.splitext(file_path.lower())
        return ext in self.text_extensions
    
    def _get_file_info(self, file_path):
        """Get file information. // [Obtener información del archivo.]"""
        stat = os.stat(file_path)
        size = stat.st_size
        mtime = stat.st_mtime
        is_text = self._is_text_file(file_path)
        lines = self._count_lines(file_path) if is_text else 0
        
        return {
            'path': os.path.relpath(file_path, self.project_root),
            'size': size,
            'mtime': mtime,
            'is_text': is_text,
            'lines': lines
        }
    
    def _detect_file_language(self, file_path):
        """Detect programming language based on file extension. // [Detectar el lenguaje de programación basado en la extensión del archivo.]"""
        _, ext = os.path.splitext(file_path.lower())
        for lang, extensions in self.language_patterns.items():
            if ext in extensions:
                return lang
        return "Unknown"
    
    def create_output_dir(self):
        """Create the output directory if it doesn't exist. // [Crear el directorio de salida si no existe.]"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"Created output directory: {self.output_dir}")

    def scan_codebase(self):
        """Scan the codebase and gather information. // [Escanear el código base y recopilar información.]"""
        self._print_status("Starting codebase analysis...")
        self.create_output_dir()
        
        all_files = []
        language_stats = defaultdict(int)
        dir_stats = defaultdict(lambda: {'files': 0, 'text_files': 0, 'lines': 0})
        
        # Walk through the codebase // [Recorrer la base de código]
        for root, dirs, files in os.walk('.'):
            # Skip ignored directories // [Omitir directorios ignorados]
            dirs[:] = [d for d in dirs if not self._should_ignore(os.path.join(root, d))]
            
            for file in files:
                file_path = os.path.join(root, file)
                if self._should_ignore(file_path):
                    continue
                
                self.total_files += 1
                
                # Get file info // [Obtener información del archivo]
                file_info = self._get_file_info(file_path)
                all_files.append(file_info)
                
                if file_info['is_text']:
                    self.total_text_files += 1
                    language = self._detect_file_language(file_path)
                    language_stats[language] += 1
                
                # Update directory stats // [Actualizar estadísticas del directorio]
                rel_dir = os.path.dirname(file_info['path']) or '.'
                dir_stats[rel_dir]['files'] += 1
                if file_info['is_text']:
                    dir_stats[rel_dir]['text_files'] += 1
                    dir_stats[rel_dir]['lines'] += file_info['lines']
                
                # Show progress occasionally // [Mostrar progreso ocasionalmente]
                if self.total_files % 100 == 0:
                    self._print_progress(self.total_files, self.total_files, 
                                       'Scanning files', f"({self.total_text_files} text files)")
        
        # Final progress update // [Actualización final de progreso]
        self._print_progress(self.total_files, self.total_files, 
                           'Scanning files', f"({self.total_text_files} text files)")
        
        # Generate the analysis files // [Generar los archivos de análisis]
        self._generate_files(all_files, language_stats, dir_stats)
        
    def _get_git_info(self):
        """Get git repository information if available. // [Obtener información del repositorio git si está disponible.]"""
        if not self.has_git:
            return {"available": False}
        
        try:
            # Get current branch // [Obtener rama actual]
            branch = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"], 
                stderr=subprocess.PIPE, text=True
            ).strip()
            
            # Get last commit // [Obtener último commit]
            last_commit = subprocess.check_output(
                ["git", "log", "-1", "--pretty=format:%h - %s (%cr)"], 
                stderr=subprocess.PIPE, text=True
            ).strip()
            
            # Count commits // [Contar commits]
            commit_count = subprocess.check_output(
                ["git", "rev-list", "--count", "HEAD"], 
                stderr=subprocess.PIPE, text=True
            ).strip()
            
            # Get remote URL // [Obtener URL remota]
            try:
                remote_url = subprocess.check_output(
                    ["git", "config", "--get", "remote.origin.url"], 
                    stderr=subprocess.PIPE, text=True
                ).strip()
            except subprocess.CalledProcessError:
                remote_url = "No remote URL configured"
            
            return {
                "available": True,
                "branch": branch,
                "last_commit": last_commit,
                "commit_count": commit_count,
                "remote_url": remote_url
            }
        except subprocess.SubprocessError:
            return {"available": False}
            
    def _generate_files(self, all_files, language_stats, dir_stats):
        """Generate all analysis files. // [Generar todos los archivos de análisis.]"""
        self._print_status("Generating analysis files...")
        
        # 1. Generate summary report // [Generar informe de resumen]
        self._generate_summary(all_files, language_stats, dir_stats)
        
        # 2. Generate codebase structure // [Generar estructura del código base]
        self._generate_structure(all_files)
        
        # 3. Generate largest files list // [Generar lista de archivos más grandes]
        self._generate_largest_files(all_files)
        
        # 4. Generate recent files list // [Generar lista de archivos recientes]
        self._generate_recent_files(all_files)
        
        # 5. Generate folder summary // [Generar resumen de carpetas]
        self._generate_folder_summary(dir_stats)
        
        self._print_status(f"Codebase analysis complete! Files saved to {self.output_dir}/ directory")
        
    def _generate_summary(self, all_files, language_stats, dir_stats):
        """Generate a summary markdown file with project overview. // [Generar un archivo markdown de resumen con la visión general del proyecto.]"""
        self._print_status("Generating project summary...")
        
        git_info = self._get_git_info()
        
        with open(os.path.join(self.output_dir, 'project_summary.md'), 'w', encoding='utf-8') as f:
            # Header // [Encabezado]
            f.write(f"# Project Summary\n\n")
            f.write(f"Analysis generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Git information // [Información de Git]
            f.write("## Repository Information\n\n")
            if git_info["available"]:
                f.write(f"- **Branch:** {git_info['branch']}\n")
                f.write(f"- **Latest Commit:** {git_info['last_commit']}\n")
                f.write(f"- **Commit Count:** {git_info['commit_count']}\n")
                f.write(f"- **Remote URL:** {git_info['remote_url']}\n")
            else:
                f.write("- Git information not available\n")
            f.write("\n")
            
            # Overall statistics // [Estadísticas generales]
            f.write("## Codebase Statistics\n\n")
            f.write(f"- **Total Files:** {self.total_files:,}\n")
            f.write(f"- **Text Files:** {self.total_text_files:,}\n")
            
            # Calculate total lines // [Calcular líneas totales]
            total_lines = sum(file_info['lines'] for file_info in all_files if file_info['is_text'])
            f.write(f"- **Total Lines of Code:** {total_lines:,}\n")
            
            # Calculate total size // [Calcular tamaño total]
            total_size = sum(file_info['size'] for file_info in all_files)
            f.write(f"- **Total Size:** {self._format_size(total_size)}\n\n")
            
            # Language statistics // [Estadísticas de lenguajes]
            f.write("## Language Distribution\n\n")
            f.write("| Language | Files | % of Codebase |\n")
            f.write("|----------|-------|---------------|\n")
            
            sorted_languages = sorted(language_stats.items(), key=lambda x: x[1], reverse=True)
            for language, count in sorted_languages:
                percentage = (count / self.total_text_files) * 100 if self.total_text_files > 0 else 0
                f.write(f"| {language} | {count:,} | {percentage:.1f}% |\n")
            
            f.write("\n")
            
            # Directory statistics // [Estadísticas de directorios]
            f.write("## Top Directories\n\n")
            f.write("| Directory | Files | Text Files | Lines of Code |\n")
            f.write("|-----------|-------|------------|---------------|\n")
            
            # Get the top 10 directories by file count // [Obtener los 10 directorios principales por cantidad de archivos]
            sorted_dirs = sorted(dir_stats.items(), key=lambda x: x[1]['files'], reverse=True)[:10]
            for dir_name, stats in sorted_dirs:
                f.write(f"| {dir_name} | {stats['files']:,} | {stats['text_files']:,} | {stats['lines']:,} |\n")
                
            f.write("\n")
            
            # Generated files // [Archivos generados]
            f.write("## Generated Analysis Files\n\n")
            f.write("The following files have been generated in the `00_docs` directory:\n\n")
            f.write("- **project_summary.md**: This summary file\n")
            f.write("- **codebase_structure.txt**: Complete listing of project files\n")
            f.write("- **largest_files.txt**: Top 20 files by line count\n")
            f.write("- **recent_files.txt**: 20 most recently modified files\n")
            f.write("- **folder_summary.txt**: Detailed folder statistics\n")

    def _format_size(self, size_bytes):
        """Format file size in a human-readable format. // [Formatear tamaño de archivo en un formato legible para humanos.]"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024 or unit == 'GB':
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
    
    def _generate_structure(self, all_files):
        """Generate file listing structure. // [Generar estructura de listado de archivos.]"""
        self._print_status("Generating codebase structure...")
        
        with open(os.path.join(self.output_dir, 'codebase_structure.txt'), 'w', encoding='utf-8') as f:
            f.write(f"# Codebase Structure ({self.total_files:,} files)\n")
            f.write(f"# Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for file_info in sorted(all_files, key=lambda x: x['path']):
                f.write(f"{file_info['path']}\n")
    
    def _generate_largest_files(self, all_files):
        """Generate list of largest files by line count. // [Generar lista de archivos más grandes por cantidad de líneas.]"""
        self._print_status("Generating largest files listing...")
        
        # Filter text files and sort by line count // [Filtrar archivos de texto y ordenar por cantidad de líneas]
        text_files = [f for f in all_files if f['is_text']]
        largest_files = sorted(text_files, key=lambda x: x['lines'], reverse=True)[:20]
        
        with open(os.path.join(self.output_dir, 'largest_files.txt'), 'w', encoding='utf-8') as f:
            f.write("# 20 Largest Files by Line Count\n")
            f.write(f"# Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("Lines    | Size       | Language   | File Path\n")
            f.write("---------|------------|------------|----------\n")
            
            for file_info in largest_files:
                language = self._detect_file_language(file_info['path'])
                f.write(f"{file_info['lines']:8,} | {self._format_size(file_info['size']):10} | {language:10} | {file_info['path']}\n")
    
    def _generate_recent_files(self, all_files):
        """Generate list of recently modified files. // [Generar lista de archivos modificados recientemente.]"""
        self._print_status("Generating recently modified files listing...")
        
        recent_files = sorted(all_files, key=lambda x: x['mtime'], reverse=True)[:20]
        
        with open(os.path.join(self.output_dir, 'recent_files.txt'), 'w', encoding='utf-8') as f:
            f.write("# 20 Most Recently Modified Files\n")
            f.write(f"# Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("Last Modified        | Language   | File Path\n")
            f.write("--------------------|------------|----------\n")
            
            for file_info in recent_files:
                modified = datetime.datetime.fromtimestamp(file_info['mtime']).strftime('%Y-%m-%d %H:%M:%S')
                language = self._detect_file_language(file_info['path'])
                f.write(f"{modified} | {language:10} | {file_info['path']}\n")
    
    def _generate_folder_summary(self, dir_stats):
        """Generate folder summary statistics. // [Generar estadísticas resumidas de carpetas.]"""
        self._print_status("Generating folder summary...")
        
        # Sort directories by file count // [Ordenar directorios por cantidad de archivos]
        sorted_dirs = sorted(dir_stats.items(), key=lambda x: x[1]['files'], reverse=True)
        
        with open(os.path.join(self.output_dir, 'folder_summary.txt'), 'w', encoding='utf-8') as f:
            f.write("# Folder Summary\n")
            f.write(f"# Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("Directory                      | Files  | Text Files | Lines of Code\n")
            f.write("-------------------------------|--------|------------|-------------\n")
            
            for dir_name, stats in sorted_dirs:
                # Truncate long directory names // [Truncar nombres de directorios largos]
                display_name = dir_name
                if len(display_name) > 30:
                    display_name = display_name[:27] + "..."
                    
                f.write(f"{display_name:30} | {stats['files']:6,} | {stats['text_files']:10,} | {stats['lines']:13,}\n")

def main():
    analyzer = CodebaseAnalyzer()
    analyzer.scan_codebase()

if __name__ == "__main__":
    main()
