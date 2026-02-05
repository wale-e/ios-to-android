---
name: ios-to-android
description: >
  Automated iOS Swift to Android Kotlin conversion using analysis scripts and pattern mappings.
  Targets Swift 5.x to Kotlin 1.9 (API 24+). Supports full project conversion, incremental syncing,
  SwiftUI to Compose, UIKit to XML, and multiple architectures (MVVM, MVI, Clean).
  Triggers: convert to Android, create Android version, sync Android with iOS,
  upgrade Android, Swift to Kotlin, port to Android.
---

# iOS to Android Conversion

## Modes of Operation

- **Full Conversion**: `python3 scripts/convert_project.py <ios-path> <android-path>`
- **Incremental Sync**: `python3 scripts/sync_projects.py <ios-path> <android-path>`
- **Analyze Only**: `python3 scripts/analyze_ios.py <ios-project-path>`

All scripts use Python standard library only.

## Scripts Overview

### analyze_ios.py
Analyzes iOS project and outputs JSON report with:
- Framework detection (UIKit, SwiftUI, hybrid)
- Architecture patterns (MVC, MVVM, VIPER)
- Dependencies from Podfile/Package.swift/Cartfile
- Complexity score and conversion recommendations

### convert_project.py
Creates complete Android project with:
- Gradle configuration from templates
- Package structure based on target architecture
- Regex-based Swift→Kotlin conversion
- `// TODO: VERIFY` markers for uncertain translations

### sync_projects.py
Detects iOS changes since last sync:
- Checksum-based change detection
- File-by-file or selective syncing
- Dry-run and interactive modes
- Conflict markers for diverged files

## Step 1: Analyze the iOS Project

```bash
python3 scripts/analyze_ios.py <ios-project-path>
```

## Step 2: Plan the Conversion

Load reference files based on analysis output:

| If analysis shows... | Load this reference |
|---------------------|---------------------|
| Any project | `references/dependency-mappings.md` (has Gradle template) |
| `ui_framework: "swiftui"` or `"hybrid"` | `references/swiftui-to-compose.md` |
| `uses_combine: true` or complex logic | `references/swift-kotlin-patterns.md` |

**File Organization** (adapt based on target architecture):

| iOS | Android (MVVM) | Android (Clean) |
|-----|----------------|-----------------|
| Models/ | model/ | domain/model/ |
| Views/ | ui/ | presentation/ui/ |
| ViewModels/ | viewmodel/ | presentation/viewmodel/ |
| Services/ | data/repository/ | data/repository/ |
| Networking/ | data/remote/ | data/remote/ |
| Extensions/ | util/ | core/util/ |

## Step 3: Execute the Conversion

```bash
python3 scripts/convert_project.py <ios-path> <android-path> --package <com.example.app> [options]
```

Options:
- `--min-sdk <24>` — Minimum SDK (default: 24)
- `--compose` — Use Jetpack Compose (default for SwiftUI)
- `--xml-views` — Use XML layouts (default for UIKit)
- `--di <hilt|koin|manual>` — DI framework (default: hilt)

## Step 4: Sync Existing Android Project

```bash
python3 scripts/sync_projects.py <ios-path> <android-path> [options]
```

Options:
- `--since <date|commit>` — Only sync changes since date/commit
- `--files <path1,path2>` — Sync specific files only
- `--dry-run` — Show changes without applying
- `--interactive` — Prompt for each change

## Error Handling

Search for uncertain translations after conversion:
```bash
grep -r "TODO: VERIFY" <android-path>
```

**Common issues:**
- **Path errors**: Exclude Pods/, Carthage/, .build/ from iOS path
- **Parse errors**: Check for unsupported Swift features
- **Script failures**: Verify Python 3.7+ is installed

## Post-Conversion Checklist

1. Run `./gradlew build` to verify compilation
2. Address all `// TODO: VERIFY` markers
3. Ensure tests are converted and passing
4. Visual comparison with iOS app
5. Add Android-specific features (widgets, notifications)
