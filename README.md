# iOS to Android Conversion Skill

A Claude Code skill for converting iOS Swift codebases to Android Kotlin with intelligent architecture mapping and incremental sync capabilities.

## Features

- **Full Project Conversion**: Convert an entire iOS Swift project to a new Android Kotlin project
- **Incremental Sync**: Keep an existing Android project in sync with iOS changes
- **Project Analysis**: Analyze iOS projects to understand structure and conversion complexity
- **Architecture Mapping**: Intelligent mapping of iOS patterns to Android equivalents
- **Dependency Mapping**: Comprehensive library equivalents between platforms

## Installation

Copy this skill directory to your Claude Code skills folder:

```bash
cp -r ios-to-android ~/.claude/skills/
```

The skill will be automatically available in Claude Code sessions.

## Usage

This skill is triggered automatically when you ask Claude Code to perform iOS-to-Android conversions. Simply describe what you want to do in natural language.

### Trigger Phrases

The skill activates when you use phrases like:
- "Convert to Android"
- "Create Android version"
- "Sync Android with iOS"
- "Upgrade Android"
- "Swift to Kotlin"
- "Port to Android"

### Analyze an iOS Project

Ask Claude to analyze your iOS project before conversion:

```
Analyze my iOS project at ~/Projects/MyiOSApp for Android conversion
```

Claude will examine the project and report:
- File structure and module organization
- Dependencies (CocoaPods, SPM, Carthage)
- Architecture patterns detected (MVVM, MVC, VIPER, etc.)
- UI framework (UIKit, SwiftUI, or hybrid)
- Conversion complexity score (1-10)

### Convert an iOS Project

Ask Claude to convert your iOS project to Android:

```
Convert my iOS app at ~/Projects/MyiOSApp to Android at ~/Projects/MyAndroidApp
```

Claude will ask for necessary details like:
- Android package name (e.g., `com.mycompany.myapp`)
- Minimum SDK version (default: 24)
- UI framework preference (Jetpack Compose or XML layouts)
- Dependency injection framework (Hilt, Koin, or manual)

### Sync Projects

Keep your Android project in sync with iOS changes:

```
Sync my Android project at ~/Projects/MyAndroidApp with iOS changes from ~/Projects/MyiOSApp
```

You can also be more specific:

```
Show me what iOS changes need to be synced to Android (dry run)
```

```
Sync only the User model changes from iOS to Android
```

## Architecture Mapping

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
| NavigationStack | NavHost/NavController |
| CoreData | Room |
| UserDefaults | DataStore |
| Keychain | EncryptedSharedPreferences |

## File Organization Mapping

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

## Reference Documentation

The `references/` directory contains detailed mapping guides:

- **`swiftui-to-compose.md`**: Comprehensive SwiftUI to Jetpack Compose component mapping
- **`swift-kotlin-patterns.md`**: Swift to Kotlin language pattern translations
- **`dependency-mappings.md`**: iOS library to Android library equivalents

## Sync State

The sync tool maintains `.ios-android-sync.json` in the Android project root to track:

```json
{
  "lastSyncDate": "2025-01-11T10:30:00Z",
  "iosCommit": "abc123",
  "fileMapping": {
    "ios/Models/User.swift": "app/src/main/java/.../model/User.kt"
  },
  "checksums": { ... }
}
```

## Post-Conversion Checklist

After conversion or sync:

1. **Build verification** - Run `./gradlew build`
2. **Review TODOs** - Search for `// TODO: VERIFY` markers
3. **Test coverage** - Ensure tests are converted and passing
4. **UI review** - Visual comparison with iOS app
5. **Platform-specific** - Add Android-specific features (widgets, notifications, etc.)

## Supported Dependencies

Common iOS libraries are mapped to Android equivalents:

| Category | iOS | Android |
|----------|-----|---------|
| Networking | URLSession, Alamofire | Retrofit + OkHttp |
| Images | Kingfisher, SDWebImage | Coil, Glide |
| Database | CoreData, Realm | Room, Realm |
| Reactive | Combine, RxSwift | Kotlin Flow, RxKotlin |
| DI | Swinject, Resolver | Hilt, Koin |
| Analytics | Firebase Analytics | Firebase Analytics |

See `references/dependency-mappings.md` for the complete list.

## Limitations

- Complex custom animations may require manual adjustment
- Platform-specific APIs (Sign in with Apple, StoreKit) need platform alternatives
- Test files are skipped during sync (manual conversion recommended)
- Some Swift-specific patterns may need manual review

## Tips

- Start with models and business logic before UI
- Keep iOS and Android codebases in sync with regular syncs
- Use feature flags for platform-specific divergences
- Document any intentional differences in `PLATFORM_DIFFERENCES.md`

## License

MIT
