#!/usr/bin/env python3
"""
Analyze iOS Swift project structure for Android conversion planning.
Outputs a JSON report with project structure, dependencies, and architecture details.
"""

import os
import sys
import json
import re
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import datetime


@dataclass
class SwiftFile:
    path: str
    name: str
    type: str  # view, viewmodel, model, service, extension, test, etc.
    imports: list[str] = field(default_factory=list)
    classes: list[str] = field(default_factory=list)
    structs: list[str] = field(default_factory=list)
    enums: list[str] = field(default_factory=list)
    protocols: list[str] = field(default_factory=list)
    uses_swiftui: bool = False
    uses_uikit: bool = False
    uses_combine: bool = False
    uses_async_await: bool = False
    line_count: int = 0


@dataclass
class Dependency:
    name: str
    version: Optional[str]
    source: str  # cocoapods, spm, carthage


@dataclass
class ProjectAnalysis:
    project_name: str
    ios_path: str
    analyzed_at: str
    swift_version: Optional[str] = None
    min_ios_version: Optional[str] = None
    
    # Architecture
    architecture_pattern: str = "unknown"  # mvvm, mvc, viper, clean, etc.
    ui_framework: str = "unknown"  # swiftui, uikit, hybrid
    
    # File counts
    total_swift_files: int = 0
    total_lines: int = 0
    
    # File breakdown
    model_files: list[SwiftFile] = field(default_factory=list)
    view_files: list[SwiftFile] = field(default_factory=list)
    viewmodel_files: list[SwiftFile] = field(default_factory=list)
    service_files: list[SwiftFile] = field(default_factory=list)
    extension_files: list[SwiftFile] = field(default_factory=list)
    utility_files: list[SwiftFile] = field(default_factory=list)
    test_files: list[SwiftFile] = field(default_factory=list)
    other_files: list[SwiftFile] = field(default_factory=list)
    
    # Dependencies
    dependencies: list[Dependency] = field(default_factory=list)
    
    # Framework usage
    uses_combine: bool = False
    uses_async_await: bool = False
    uses_core_data: bool = False
    uses_realm: bool = False
    uses_alamofire: bool = False
    uses_kingfisher: bool = False
    uses_firebase: bool = False
    
    # Conversion complexity
    complexity_score: int = 0  # 1-10
    complexity_notes: list[str] = field(default_factory=list)


def analyze_swift_file(filepath: Path, project_root: Path) -> SwiftFile:
    """Analyze a single Swift file."""
    relative_path = str(filepath.relative_to(project_root))
    
    sf = SwiftFile(
        path=relative_path,
        name=filepath.stem,
        type="other"
    )
    
    try:
        content = filepath.read_text(encoding='utf-8', errors='ignore')
        sf.line_count = len(content.splitlines())
        
        # Detect imports
        import_pattern = r'^import\s+(\w+)'
        sf.imports = re.findall(import_pattern, content, re.MULTILINE)
        
        # Detect SwiftUI/UIKit usage
        sf.uses_swiftui = 'SwiftUI' in sf.imports or 'View' in content and 'body:' in content
        sf.uses_uikit = 'UIKit' in sf.imports or 'UIViewController' in content
        sf.uses_combine = 'Combine' in sf.imports or '@Published' in content
        sf.uses_async_await = 'async' in content and ('await' in content or 'throws' in content)
        
        # Detect type declarations
        sf.classes = re.findall(r'class\s+(\w+)', content)
        sf.structs = re.findall(r'struct\s+(\w+)', content)
        sf.enums = re.findall(r'enum\s+(\w+)', content)
        sf.protocols = re.findall(r'protocol\s+(\w+)', content)
        
        # Classify file type based on content and path
        path_lower = relative_path.lower()
        name_lower = sf.name.lower()
        
        if 'test' in path_lower or name_lower.endswith('tests') or name_lower.endswith('test'):
            sf.type = "test"
        elif 'viewmodel' in name_lower or 'vm' in name_lower:
            sf.type = "viewmodel"
        elif sf.uses_swiftui and ('View' in content or 'body:' in content):
            sf.type = "view"
        elif sf.uses_uikit and 'UIViewController' in content:
            sf.type = "view"
        elif 'model' in path_lower or ('struct' in content.lower() and 'Codable' in content):
            sf.type = "model"
        elif 'service' in path_lower or 'api' in path_lower or 'network' in path_lower:
            sf.type = "service"
        elif 'extension' in path_lower or name_lower.endswith('+'):
            sf.type = "extension"
        elif 'util' in path_lower or 'helper' in path_lower:
            sf.type = "utility"
            
    except Exception as e:
        print(f"Warning: Could not analyze {filepath}: {e}", file=sys.stderr)
    
    return sf


def parse_podfile(podfile_path: Path) -> list[Dependency]:
    """Parse CocoaPods Podfile for dependencies."""
    deps = []
    try:
        content = podfile_path.read_text()
        # Match pod 'Name', '~> 1.0' or pod 'Name'
        pattern = r"pod\s+['\"]([^'\"]+)['\"](?:\s*,\s*['\"]([^'\"]+)['\"])?"
        for match in re.finditer(pattern, content):
            deps.append(Dependency(
                name=match.group(1),
                version=match.group(2),
                source="cocoapods"
            ))
    except Exception:
        pass
    return deps


def parse_package_swift(package_path: Path) -> list[Dependency]:
    """Parse Swift Package Manager Package.swift for dependencies."""
    deps = []
    try:
        content = package_path.read_text()
        # Match .package(url: "...", from: "1.0.0") or .package(name: "...", ...)
        url_pattern = r'\.package\s*\(\s*url:\s*"([^"]+)"'
        for match in re.finditer(url_pattern, content):
            url = match.group(1)
            name = url.split('/')[-1].replace('.git', '')
            deps.append(Dependency(name=name, version=None, source="spm"))
    except Exception:
        pass
    return deps


def parse_cartfile(cartfile_path: Path) -> list[Dependency]:
    """Parse Carthage Cartfile for dependencies."""
    deps = []
    try:
        content = cartfile_path.read_text()
        # Match github "Owner/Repo" ~> 1.0
        pattern = r'(?:github|git)\s+"([^"]+)"'
        for match in re.finditer(pattern, content):
            repo = match.group(1)
            name = repo.split('/')[-1] if '/' in repo else repo
            deps.append(Dependency(name=name, version=None, source="carthage"))
    except Exception:
        pass
    return deps


def detect_architecture(analysis: ProjectAnalysis) -> str:
    """Detect the architecture pattern used in the project."""
    has_viewmodels = len(analysis.viewmodel_files) > 0
    has_views = len(analysis.view_files) > 0
    has_services = len(analysis.service_files) > 0
    
    # Check for VIPER indicators
    all_files = [f.name.lower() for f in 
                 analysis.view_files + analysis.viewmodel_files + 
                 analysis.service_files + analysis.other_files]
    
    has_presenter = any('presenter' in f for f in all_files)
    has_interactor = any('interactor' in f for f in all_files)
    has_router = any('router' in f or 'coordinator' in f for f in all_files)
    
    if has_presenter and has_interactor and has_router:
        return "viper"
    
    if has_router and has_viewmodels:
        return "mvvm-c"  # MVVM with Coordinators
    
    if has_viewmodels:
        return "mvvm"
    
    if has_views and not has_viewmodels:
        return "mvc"
    
    return "unknown"


def calculate_complexity(analysis: ProjectAnalysis) -> tuple[int, list[str]]:
    """Calculate conversion complexity score and notes."""
    score = 1
    notes = []
    
    # UI Framework complexity
    if analysis.ui_framework == "hybrid":
        score += 2
        notes.append("Mixed UIKit and SwiftUI requires handling both conversion paths")
    elif analysis.ui_framework == "uikit":
        score += 1
        notes.append("UIKit to Compose/XML conversion requires more manual work")
    
    # Architecture complexity
    if analysis.architecture_pattern == "viper":
        score += 2
        notes.append("VIPER architecture needs careful mapping to Android patterns")
    elif analysis.architecture_pattern == "mvvm-c":
        score += 1
        notes.append("Coordinators need conversion to Navigation Component")
    
    # Framework dependencies
    if analysis.uses_core_data:
        score += 2
        notes.append("CoreData to Room migration requires schema mapping")
    
    if analysis.uses_combine:
        score += 1
        notes.append("Combine publishers need conversion to Kotlin Flow")
    
    # Size complexity
    if analysis.total_lines > 50000:
        score += 2
        notes.append("Large codebase (>50k lines) requires phased conversion")
    elif analysis.total_lines > 20000:
        score += 1
        notes.append("Medium codebase (>20k lines)")
    
    # Third-party dependencies
    complex_deps = ['realm', 'rxswift', 'reactiveswift']
    for dep in analysis.dependencies:
        if dep.name.lower() in complex_deps:
            score += 1
            notes.append(f"Complex dependency: {dep.name}")
    
    return min(score, 10), notes


def analyze_project(ios_path: str) -> ProjectAnalysis:
    """Analyze an iOS project directory."""
    root = Path(ios_path).resolve()
    
    if not root.exists():
        raise FileNotFoundError(f"Project path does not exist: {ios_path}")
    
    # Find project name
    xcodeproj = list(root.glob("*.xcodeproj"))
    project_name = xcodeproj[0].stem if xcodeproj else root.name
    
    analysis = ProjectAnalysis(
        project_name=project_name,
        ios_path=str(root),
        analyzed_at=datetime.now().isoformat()
    )
    
    # Collect all Swift files
    swift_files = list(root.rglob("*.swift"))
    # Exclude Pods, Carthage, build directories
    swift_files = [f for f in swift_files if not any(
        x in str(f) for x in ['Pods/', 'Carthage/', 'build/', '.build/', 'DerivedData/']
    )]
    
    analysis.total_swift_files = len(swift_files)
    
    # Analyze each file
    for filepath in swift_files:
        sf = analyze_swift_file(filepath, root)
        analysis.total_lines += sf.line_count
        
        # Update framework usage
        if sf.uses_combine:
            analysis.uses_combine = True
        if sf.uses_async_await:
            analysis.uses_async_await = True
        
        # Sort into categories
        if sf.type == "model":
            analysis.model_files.append(sf)
        elif sf.type == "view":
            analysis.view_files.append(sf)
        elif sf.type == "viewmodel":
            analysis.viewmodel_files.append(sf)
        elif sf.type == "service":
            analysis.service_files.append(sf)
        elif sf.type == "extension":
            analysis.extension_files.append(sf)
        elif sf.type == "utility":
            analysis.utility_files.append(sf)
        elif sf.type == "test":
            analysis.test_files.append(sf)
        else:
            analysis.other_files.append(sf)
    
    # Determine UI framework
    swiftui_count = sum(1 for f in analysis.view_files if f.uses_swiftui)
    uikit_count = sum(1 for f in analysis.view_files if f.uses_uikit)
    
    if swiftui_count > 0 and uikit_count > 0:
        analysis.ui_framework = "hybrid"
    elif swiftui_count > 0:
        analysis.ui_framework = "swiftui"
    elif uikit_count > 0:
        analysis.ui_framework = "uikit"
    
    # Parse dependencies
    podfile = root / "Podfile"
    if podfile.exists():
        analysis.dependencies.extend(parse_podfile(podfile))
    
    package_swift = root / "Package.swift"
    if package_swift.exists():
        analysis.dependencies.extend(parse_package_swift(package_swift))
    
    cartfile = root / "Cartfile"
    if cartfile.exists():
        analysis.dependencies.extend(parse_cartfile(cartfile))
    
    # Check for common frameworks
    all_imports = set()
    for files in [analysis.model_files, analysis.view_files, analysis.viewmodel_files,
                  analysis.service_files, analysis.other_files]:
        for f in files:
            all_imports.update(f.imports)
    
    dep_names = {d.name.lower() for d in analysis.dependencies}
    
    analysis.uses_core_data = 'CoreData' in all_imports
    analysis.uses_realm = 'RealmSwift' in all_imports or 'realm' in dep_names
    analysis.uses_alamofire = 'Alamofire' in all_imports or 'alamofire' in dep_names
    analysis.uses_kingfisher = 'Kingfisher' in all_imports or 'kingfisher' in dep_names
    analysis.uses_firebase = any('Firebase' in imp for imp in all_imports) or 'firebase' in dep_names
    
    # Detect architecture
    analysis.architecture_pattern = detect_architecture(analysis)
    
    # Calculate complexity
    analysis.complexity_score, analysis.complexity_notes = calculate_complexity(analysis)
    
    return analysis


def main():
    if len(sys.argv) < 2:
        print("Usage: analyze_ios.py <ios-project-path> [--output <file.json>]")
        print("\nAnalyzes an iOS Swift project and outputs a JSON report.")
        sys.exit(1)
    
    ios_path = sys.argv[1]
    output_file = None
    
    if '--output' in sys.argv:
        idx = sys.argv.index('--output')
        if idx + 1 < len(sys.argv):
            output_file = sys.argv[idx + 1]
    
    try:
        analysis = analyze_project(ios_path)
        result = asdict(analysis)
        
        json_output = json.dumps(result, indent=2, default=str)
        
        if output_file:
            Path(output_file).write_text(json_output)
            print(f"Analysis saved to: {output_file}")
        else:
            print(json_output)
            
    except Exception as e:
        print(f"Error analyzing project: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
