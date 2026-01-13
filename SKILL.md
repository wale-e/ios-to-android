---
name: ios-to-android
description: >
  Convert iOS Swift codebases to Android Kotlin and keep them in sync.
  Use when converting an entire iOS Swift project to Android Kotlin,
  syncing or upgrading an existing Android Kotlin version to match new iOS Swift features,
  translating specific Swift files or components to Kotlin equivalents,
  or analyzing iOS projects for Android conversion planning.
  Triggers include phrases like convert to Android, create Android version,
  sync Android with iOS, upgrade Android, Swift to Kotlin, port to Android.
---

# iOS to Android Conversion Skill

Convert iOS Swift codebases to Android Kotlin with intelligent architecture mapping and incremental sync capabilities.

## Workflow Overview

1. **Analyze iOS project** → Understand structure, dependencies, architecture
2. **Plan conversion** → Map iOS patterns to Android equivalents
3. **Execute conversion** → Generate Kotlin code with proper Android architecture
4. **Sync/upgrade** → Update existing Android project with new iOS features

## Modes of Operation

**Full Conversion**: `convert ios-path android-path`
- Creates new Android project from iOS codebase

**Incremental Sync**: `sync ios-path android-path`
- Updates existing Android project to match iOS changes

**Analyze Only**: `analyze ios-path`
- Reports structure and conversion complexity without generating code

## Step 1: Analyze iOS Project

Run the analyzer to understand the iOS project structure:

```bash
python3 scripts/analyze_ios.py <ios-project-path>
```

This produces a JSON report with:
- File structure and module organization
- Dependencies (CocoaPods, SPM, Carthage)
- Architecture patterns detected (MVVM, MVC, VIPER, etc.)
- UI framework (UIKit, SwiftUI, or hybrid)
- Networking layer details
- Data persistence approach
- Third-party SDK integrations

## Step 2: Plan Conversion

Review the analysis and apply these mappings:

### Architecture Mapping

| iOS Pattern | Android Equivalent |
|-------------|-------------------|
| SwiftUI View | Jetpack Compose Composable |
| UIKit ViewController | Fragment or Activity |
| @Observable / ObservableObject | ViewModel with StateFlow |
| @Published | MutableStateFlow |
| Combine Publisher | Kotlin Flow |
| async/await | Kotlin Coroutines |
| @State | remember { mutableStateOf() } |
| @Binding | Callback or State hoisting |
| @Environment | CompositionLocal |
| NavigationStack | NavHost/NavController |

### Dependency Mapping

See `references/dependency-mappings.md` for comprehensive library equivalents.

### File Organization

```
iOS Structure              →  Android Structure
───────────────────────────────────────────────
MyApp/                        app/src/main/
├── Models/                   ├── java/.../model/
├── Views/                    ├── java/.../ui/
├── ViewModels/              ├── java/.../viewmodel/
├── Services/                ├── java/.../data/
├── Networking/              │   ├── repository/
│                            │   ├── remote/
│                            │   └── local/
├── Extensions/              ├── java/.../util/
└── Resources/               └── res/
```

## Step 3: Execute Conversion

### For Full Conversion

```bash
python3 scripts/convert_project.py <ios-path> <android-path> [options]
```

Options:
- `--package <com.example.app>` - Android package name (required)
- `--min-sdk <24>` - Minimum SDK version (default: 24)
- `--compose` - Use Jetpack Compose (default for SwiftUI projects)
- `--xml-views` - Use XML layouts (default for UIKit projects)
- `--di <hilt|koin|manual>` - Dependency injection framework (default: hilt)

### Conversion Process

1. **Generate project structure**
   - Create Gradle configuration
   - Set up module hierarchy
   - Configure dependencies

2. **Convert models**
   - Swift structs → Kotlin data classes
   - Swift classes → Kotlin classes
   - Codable → @Serializable or Gson annotations
   - Property wrappers → Kotlin delegated properties

3. **Convert business logic**
   - Combine → Flow
   - async/await → suspend functions
   - Result types → Result<T, E> or sealed classes
   - Extensions → Extension functions

4. **Convert UI layer**
   - SwiftUI → Jetpack Compose (see `references/swiftui-to-compose.md`)
   - UIKit → XML layouts + ViewBinding or Compose
   - Navigation → Navigation Component or Compose Navigation

5. **Convert data layer**
   - CoreData → Room
   - UserDefaults → DataStore
   - Keychain → EncryptedSharedPreferences
   - URLSession → Retrofit + OkHttp

## Step 4: Sync/Upgrade Existing Android Project

For incremental updates when iOS features are added:

```bash
python3 scripts/sync_projects.py <ios-path> <android-path> [options]
```

Options:
- `--since <date|commit>` - Only sync changes since date/commit
- `--files <path1,path2>` - Sync specific files only
- `--dry-run` - Show changes without applying
- `--interactive` - Prompt for each change

### Sync Process

1. **Detect changes** - Compare iOS project against last sync state
2. **Classify changes** - New files, modified files, deleted files
3. **Generate diff report** - What needs to be added/updated in Android
4. **Apply changes** - Create/update Kotlin files with conflict markers if needed

### Tracking Sync State

The sync tool maintains `.ios-android-sync.json` in the Android project root:

```json
{
  "lastSyncDate": "2025-01-11T10:30:00Z",
  "iosCommit": "abc123",
  "fileMapping": {
    "ios/Models/User.swift": "app/src/main/java/.../model/User.kt",
    ...
  },
  "checksums": { ... }
}
```

## Code Translation Patterns

### Swift to Kotlin Quick Reference

```swift
// Swift                          // Kotlin
struct User: Codable {            data class User(
    let id: String                    val id: String,
    var name: String                  var name: String,
    let email: String?                val email: String?
}                                 )

// Optionals
user?.name ?? "Unknown"           user?.name ?: "Unknown"
guard let user = user else {      val user = user ?: return
    return
}

// Collections
array.map { $0.name }             array.map { it.name }
array.filter { $0.isActive }      array.filter { it.isActive }
array.compactMap { $0.email }     array.mapNotNull { it.email }

// Async
func fetch() async throws ->      suspend fun fetch(): User
    User

Task {                            viewModelScope.launch {
    await fetch()                     fetch()
}                                 }

// Combine → Flow
@Published var items: [Item]      private val _items = MutableStateFlow<List<Item>>(emptyList())
                                  val items: StateFlow<List<Item>> = _items.asStateFlow()
```

See `references/swift-kotlin-patterns.md` for comprehensive examples.

## Error Handling

The conversion tools mark uncertain translations with `// TODO: VERIFY` comments:

```kotlin
// TODO: VERIFY - iOS uses custom animation, may need adjustment
AnimatedVisibility(visible = isShowing) { ... }
```

Search for these after conversion: `grep -r "TODO: VERIFY" <android-path>`

## Post-Conversion Checklist

After conversion or sync:

1. **Build verification** - Run `./gradlew build`
2. **Review TODOs** - Address all `// TODO: VERIFY` markers
3. **Test coverage** - Ensure tests are converted and passing
4. **UI review** - Visual comparison with iOS app
5. **Platform-specific** - Add Android-specific features (widgets, notifications, etc.)

## Tips

- Start with models and business logic before UI
- Keep iOS and Android codebases in sync with regular syncs
- Use feature flags for platform-specific divergences
- Document any intentional differences in `PLATFORM_DIFFERENCES.md`
