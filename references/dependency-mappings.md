# iOS to Android Dependency Mappings

## Networking

| iOS | Android | Notes |
|-----|---------|-------|
| URLSession | Retrofit + OkHttp | Use Retrofit for REST APIs |
| Alamofire | Retrofit + OkHttp | Direct equivalent |
| Moya | Retrofit | Similar abstraction layer |
| Socket.IO-Client-Swift | Socket.IO-Android | Same API |
| Starscream (WebSocket) | OkHttp WebSocket | Built into OkHttp |
| gRPC-Swift | grpc-kotlin | Official implementations |

## JSON/Serialization

| iOS | Android | Notes |
|-----|---------|-------|
| Codable (native) | kotlinx.serialization | Prefer this for Kotlin-first |
| Codable (native) | Gson | Google's solution, mature |
| Codable (native) | Moshi | Square's solution, Kotlin-friendly |
| SwiftyJSON | Gson/Moshi | Use typed parsing instead |

## Image Loading

| iOS | Android | Notes |
|-----|---------|-------|
| Kingfisher | Coil | Kotlin-first, Compose support |
| SDWebImage | Glide | Most popular, by Google |
| Nuke | Coil | Similar API philosophy |
| AlamofireImage | Coil/Glide | Part of larger ecosystem |

## Database/Persistence

| iOS | Android | Notes |
|-----|---------|-------|
| CoreData | Room | Official Android persistence |
| Realm | Realm | Same library, both platforms |
| SQLite.swift | Room or SQLDelight | Room preferred for Android |
| UserDefaults | DataStore | Prefer DataStore over SharedPreferences |
| Keychain | EncryptedSharedPreferences | Android security library |
| MMKV | MMKV | Same library, both platforms |

## Reactive/Async

| iOS | Android | Notes |
|-----|---------|-------|
| Combine | Kotlin Flow | Native Kotlin solution |
| RxSwift | RxKotlin/RxJava | Same ReactiveX ecosystem |
| async/await | Kotlin Coroutines | Language-level support |
| PromiseKit | Kotlin Coroutines | Use suspend functions |

## Dependency Injection

| iOS | Android | Notes |
|-----|---------|-------|
| Swinject | Hilt | Official Android DI |
| Resolver | Koin | Lightweight alternative |
| Factory | Hilt/Koin | Choose based on project size |
| Manual DI | Manual/Hilt | Hilt recommended for scale |

## UI Components

| iOS | Android | Notes |
|-----|---------|-------|
| SwiftUI | Jetpack Compose | Modern declarative UI |
| UIKit | XML + ViewBinding | Traditional Android UI |
| SnapKit | ConstraintLayout | XML layout constraints |
| Lottie-iOS | Lottie-Android | Same animations both platforms |
| Charts (DGCharts) | MPAndroidChart | Similar API |
| Kingfisher | Coil Compose | For Compose image loading |

## Authentication

| iOS | Android | Notes |
|-----|---------|-------|
| Sign in with Apple | Google Sign-In | Platform-specific |
| Firebase Auth | Firebase Auth | Same SDK |
| Auth0 | Auth0 | Same SDK |
| AppAuth | AppAuth-Android | OAuth library |
| BiometricAuthentication | BiometricPrompt | Platform APIs |

## Analytics/Crash Reporting

| iOS | Android | Notes |
|-----|---------|-------|
| Firebase Analytics | Firebase Analytics | Same SDK |
| Crashlytics | Crashlytics | Same SDK |
| Mixpanel | Mixpanel | Same SDK |
| Amplitude | Amplitude | Same SDK |
| Sentry | Sentry | Same SDK |

## Push Notifications

| iOS | Android | Notes |
|-----|---------|-------|
| APNs (native) | FCM | Firebase Cloud Messaging |
| Firebase Cloud Messaging | Firebase Cloud Messaging | Same SDK |
| OneSignal | OneSignal | Same SDK |

## Maps/Location

| iOS | Android | Notes |
|-----|---------|-------|
| MapKit | Google Maps SDK | Different APIs |
| CoreLocation | FusedLocationProvider | Google Play Services |
| Mapbox | Mapbox | Same SDK |

## Payment

| iOS | Android | Notes |
|-----|---------|-------|
| StoreKit | Google Play Billing | Different APIs entirely |
| RevenueCat | RevenueCat | Abstracts both platforms |
| Stripe | Stripe | Same SDK concept |

## Logging

| iOS | Android | Notes |
|-----|---------|-------|
| OSLog | Timber | Popular logging library |
| CocoaLumberjack | Timber | Similar features |
| SwiftyBeaver | Timber | Feature parity |

## Testing

| iOS | Android | Notes |
|-----|---------|-------|
| XCTest | JUnit + Truth | Unit testing |
| Quick/Nimble | Kotest | BDD-style testing |
| XCUITest | Espresso | UI testing |
| Snapshot Testing | Paparazzi | Screenshot testing |
| Mockingbird | MockK | Mocking framework |

## Build Tools

| iOS | Android | Notes |
|-----|---------|-------|
| CocoaPods | Gradle (Maven) | Dependency management |
| SPM | Gradle (Maven) | Dependency management |
| Carthage | Gradle (Maven) | Dependency management |
| Fastlane | Fastlane | Same tool, both platforms |
| SwiftLint | ktlint/detekt | Code linting |
| SwiftFormat | ktfmt | Code formatting |

## Crypto/Security

| iOS | Android | Notes |
|-----|---------|-------|
| CryptoKit | Tink | Google's crypto library |
| CommonCrypto | BouncyCastle | Low-level crypto |
| Keychain | Android Keystore | Secure storage |

## Date/Time

| iOS | Android | Notes |
|-----|---------|-------|
| Foundation Date | java.time / kotlinx-datetime | Use kotlinx-datetime |
| DateFormatter | DateTimeFormatter | Java time API |

## Architecture Components

| iOS | Android | Notes |
|-----|---------|-------|
| Observation (@Observable) | ViewModel + StateFlow | Lifecycle-aware |
| @Published | MutableStateFlow | State management |
| @AppStorage | DataStore | Persistent preferences |
| @SceneStorage | SavedStateHandle | Process death survival |

## Gradle Dependencies Template

```kotlin
// build.gradle.kts (app level)
dependencies {
    // Networking
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")
    
    // Serialization
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.0")
    
    // Image Loading
    implementation("io.coil-kt:coil-compose:2.5.0")
    
    // Database
    implementation("androidx.room:room-runtime:2.6.1")
    implementation("androidx.room:room-ktx:2.6.1")
    ksp("androidx.room:room-compiler:2.6.1")
    
    // DataStore
    implementation("androidx.datastore:datastore-preferences:1.0.0")
    
    // DI
    implementation("com.google.dagger:hilt-android:2.48.1")
    kapt("com.google.dagger:hilt-compiler:2.48.1")
    
    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
    
    // Lifecycle
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.7.0")
    implementation("androidx.lifecycle:lifecycle-runtime-compose:2.7.0")
    
    // Navigation
    implementation("androidx.navigation:navigation-compose:2.7.6")
    
    // Compose BOM
    implementation(platform("androidx.compose:compose-bom:2024.01.00"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.ui:ui-tooling-preview")
}
```
