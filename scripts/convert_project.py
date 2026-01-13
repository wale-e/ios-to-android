#!/usr/bin/env python3
"""
Convert iOS Swift project to Android Kotlin.
Generates project structure, Gradle configuration, and converted source files.
"""

import os
import sys
import json
import re
import shutil
import argparse
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class ConversionConfig:
    ios_path: Path
    android_path: Path
    package_name: str
    min_sdk: int = 24
    target_sdk: int = 34
    use_compose: bool = True
    di_framework: str = "hilt"  # hilt, koin, manual


# Gradle templates
BUILD_GRADLE_PROJECT = '''// Top-level build file
plugins {{
    id("com.android.application") version "8.2.0" apply false
    id("org.jetbrains.kotlin.android") version "1.9.21" apply false
    id("org.jetbrains.kotlin.plugin.serialization") version "1.9.21" apply false
    {hilt_plugin}
}}
'''

BUILD_GRADLE_APP = '''plugins {{
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.serialization")
    {hilt_plugin}
}}

android {{
    namespace = "{package_name}"
    compileSdk = {target_sdk}

    defaultConfig {{
        applicationId = "{package_name}"
        minSdk = {min_sdk}
        targetSdk = {target_sdk}
        versionCode = 1
        versionName = "1.0"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        vectorDrawables {{ useSupportLibrary = true }}
    }}

    buildTypes {{
        release {{
            isMinifyEnabled = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }}
    }}
    compileOptions {{
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }}
    kotlinOptions {{ jvmTarget = "17" }}
    {compose_config}
    packaging {{ resources {{ excludes += "/META-INF/{{AL2.0,LGPL2.1}}" }} }}
}}

dependencies {{
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.7.0")
    implementation("androidx.activity:activity-compose:1.8.2")
    {compose_dependencies}
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:converter-gson:2.9.0")
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.2")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
    implementation("io.coil-kt:coil-compose:2.5.0")
    implementation("androidx.datastore:datastore-preferences:1.0.0")
    {di_dependencies}
    implementation("androidx.room:room-runtime:2.6.1")
    implementation("androidx.room:room-ktx:2.6.1")
    ksp("androidx.room:room-compiler:2.6.1")
    implementation("androidx.navigation:navigation-compose:2.7.6")
    testImplementation("junit:junit:4.13.2")
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.5.1")
    {compose_test_dependencies}
}}
'''

COMPOSE_CONFIG = '''buildFeatures { compose = true }
    composeOptions { kotlinCompilerExtensionVersion = "1.5.6" }'''

COMPOSE_DEPENDENCIES = '''implementation(platform("androidx.compose:compose-bom:2024.01.00"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-graphics")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.7.0")
    implementation("androidx.lifecycle:lifecycle-runtime-compose:2.7.0")
    debugImplementation("androidx.compose.ui:ui-tooling")
    debugImplementation("androidx.compose.ui:ui-test-manifest")'''

COMPOSE_TEST_DEPS = '''androidTestImplementation(platform("androidx.compose:compose-bom:2024.01.00"))
    androidTestImplementation("androidx.compose.ui:ui-test-junit4")'''

HILT_PLUGIN_PROJECT = 'id("com.google.dagger.hilt.android") version "2.48.1" apply false'
HILT_PLUGIN_APP = 'id("com.google.dagger.hilt.android")\n    id("com.google.devtools.ksp") version "1.9.21-1.0.15"'
HILT_DEPS = '''implementation("com.google.dagger:hilt-android:2.48.1")
    ksp("com.google.dagger:hilt-compiler:2.48.1")
    implementation("androidx.hilt:hilt-navigation-compose:1.1.0")'''

KOIN_DEPS = '''implementation("io.insert-koin:koin-android:3.5.3")
    implementation("io.insert-koin:koin-androidx-compose:3.5.3")'''

SETTINGS_GRADLE = '''pluginManagement {{
    repositories {{ google(); mavenCentral(); gradlePluginPortal() }}
}}
dependencyResolutionManagement {{
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {{ google(); mavenCentral() }}
}}
rootProject.name = "{project_name}"
include(":app")
'''


def create_directory_structure(config: ConversionConfig) -> None:
    """Create the Android project directory structure."""
    android = config.android_path
    pkg_path = config.package_name.replace('.', '/')
    
    directories = [
        android / "app" / "src" / "main" / "java" / pkg_path / "model",
        android / "app" / "src" / "main" / "java" / pkg_path / "ui" / "theme",
        android / "app" / "src" / "main" / "java" / pkg_path / "ui" / "screens",
        android / "app" / "src" / "main" / "java" / pkg_path / "ui" / "components",
        android / "app" / "src" / "main" / "java" / pkg_path / "viewmodel",
        android / "app" / "src" / "main" / "java" / pkg_path / "data" / "repository",
        android / "app" / "src" / "main" / "java" / pkg_path / "data" / "remote",
        android / "app" / "src" / "main" / "java" / pkg_path / "data" / "local",
        android / "app" / "src" / "main" / "java" / pkg_path / "di",
        android / "app" / "src" / "main" / "java" / pkg_path / "util",
        android / "app" / "src" / "main" / "res" / "values",
        android / "app" / "src" / "main" / "res" / "mipmap-hdpi",
        android / "app" / "src" / "test" / "java" / pkg_path,
        android / "app" / "src" / "androidTest" / "java" / pkg_path,
        android / "gradle" / "wrapper",
    ]
    
    for d in directories:
        d.mkdir(parents=True, exist_ok=True)


def create_gradle_files(config: ConversionConfig, project_name: str) -> None:
    """Create Gradle build files."""
    android = config.android_path
    
    hilt_plugin_project = HILT_PLUGIN_PROJECT if config.di_framework == "hilt" else ""
    hilt_plugin_app = HILT_PLUGIN_APP if config.di_framework == "hilt" else 'id("com.google.devtools.ksp") version "1.9.21-1.0.15"'
    
    if config.di_framework == "hilt":
        di_deps = HILT_DEPS
    elif config.di_framework == "koin":
        di_deps = KOIN_DEPS
    else:
        di_deps = "// Manual dependency injection"
    
    compose_config = COMPOSE_CONFIG if config.use_compose else ""
    compose_deps = COMPOSE_DEPENDENCIES if config.use_compose else ""
    compose_test = COMPOSE_TEST_DEPS if config.use_compose else ""
    
    project_gradle = BUILD_GRADLE_PROJECT.format(hilt_plugin=hilt_plugin_project)
    (android / "build.gradle.kts").write_text(project_gradle)
    
    app_gradle = BUILD_GRADLE_APP.format(
        package_name=config.package_name,
        min_sdk=config.min_sdk,
        target_sdk=config.target_sdk,
        hilt_plugin=hilt_plugin_app,
        compose_config=compose_config,
        compose_dependencies=compose_deps,
        di_dependencies=di_deps,
        compose_test_dependencies=compose_test
    )
    (android / "app" / "build.gradle.kts").write_text(app_gradle)
    
    settings = SETTINGS_GRADLE.format(project_name=project_name)
    (android / "settings.gradle.kts").write_text(settings)
    
    (android / "gradle.properties").write_text('''org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
kotlin.code.style=official
android.nonTransitiveRClass=true
''')
    
    (android / "app" / "proguard-rules.pro").write_text(f'''# Keep data classes
-keep class {config.package_name}.model.** {{ *; }}
-keepattributes Signature, InnerClasses, EnclosingMethod
''')
    
    (android / "gradle" / "wrapper" / "gradle-wrapper.properties").write_text('''distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\\://services.gradle.org/distributions/gradle-8.2-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
''')


def create_android_files(config: ConversionConfig, app_name: str) -> None:
    """Create Android manifest and core files."""
    pkg_path = config.package_name.replace('.', '/')
    use_hilt = config.di_framework == "hilt"
    
    # AndroidManifest.xml
    hilt_app = f'android:name=".{app_name}Application"' if use_hilt else ""
    manifest = f'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.INTERNET" />
    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.{app_name}"
        {hilt_app}>
        <activity android:name=".MainActivity" android:exported="true" android:theme="@style/Theme.{app_name}">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
'''
    (config.android_path / "app" / "src" / "main" / "AndroidManifest.xml").write_text(manifest)
    
    # Application class
    hilt_import = "import dagger.hilt.android.HiltAndroidApp" if use_hilt else ""
    hilt_annotation = "@HiltAndroidApp" if use_hilt else ""
    app_class = f'''package {config.package_name}

import android.app.Application
{hilt_import}

{hilt_annotation}
class {app_name}Application : Application() {{
    override fun onCreate() {{
        super.onCreate()
    }}
}}
'''
    (config.android_path / "app" / "src" / "main" / "java" / pkg_path / f"{app_name}Application.kt").write_text(app_class)
    
    # MainActivity
    hilt_import = "import dagger.hilt.android.AndroidEntryPoint" if use_hilt else ""
    hilt_annotation = "@AndroidEntryPoint" if use_hilt else ""
    activity = f'''package {config.package_name}

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import {config.package_name}.ui.theme.{app_name}Theme
{hilt_import}

{hilt_annotation}
class MainActivity : ComponentActivity() {{
    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)
        setContent {{
            {app_name}Theme {{
                Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {{
                    MainScreen()
                }}
            }}
        }}
    }}
}}
'''
    (config.android_path / "app" / "src" / "main" / "java" / pkg_path / "MainActivity.kt").write_text(activity)
    
    # MainScreen
    main_screen = f'''package {config.package_name}

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun MainScreen() {{
    Column(
        modifier = Modifier.fillMaxSize().padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {{
        Text(text = "Welcome to {app_name}", style = MaterialTheme.typography.headlineMedium)
        Spacer(modifier = Modifier.height(16.dp))
        Text(text = "Converted from iOS", style = MaterialTheme.typography.bodyLarge)
    }}
}}
'''
    (config.android_path / "app" / "src" / "main" / "java" / pkg_path / "MainScreen.kt").write_text(main_screen)


def create_theme_files(config: ConversionConfig, app_name: str) -> None:
    """Create Compose theme files."""
    pkg_path = config.package_name.replace('.', '/')
    theme_path = config.android_path / "app" / "src" / "main" / "java" / pkg_path / "ui" / "theme"
    
    (theme_path / "Color.kt").write_text(f'''package {config.package_name}.ui.theme

import androidx.compose.ui.graphics.Color

val Purple80 = Color(0xFFD0BCFF)
val PurpleGrey80 = Color(0xFFCCC2DC)
val Pink80 = Color(0xFFEFB8C8)
val Purple40 = Color(0xFF6650a4)
val PurpleGrey40 = Color(0xFF625b71)
val Pink40 = Color(0xFF7D5260)
''')
    
    (theme_path / "Type.kt").write_text(f'''package {config.package_name}.ui.theme

import androidx.compose.material3.Typography
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

val Typography = Typography(
    bodyLarge = TextStyle(fontFamily = FontFamily.Default, fontWeight = FontWeight.Normal, fontSize = 16.sp, lineHeight = 24.sp, letterSpacing = 0.5.sp)
)
''')
    
    (theme_path / "Theme.kt").write_text(f'''package {config.package_name}.ui.theme

import android.app.Activity
import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

private val DarkColorScheme = darkColorScheme(primary = Purple80, secondary = PurpleGrey80, tertiary = Pink80)
private val LightColorScheme = lightColorScheme(primary = Purple40, secondary = PurpleGrey40, tertiary = Pink40)

@Composable
fun {app_name}Theme(darkTheme: Boolean = isSystemInDarkTheme(), dynamicColor: Boolean = true, content: @Composable () -> Unit) {{
    val colorScheme = when {{
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {{
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }}
        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }}
    val view = LocalView.current
    if (!view.isInEditMode) {{
        SideEffect {{
            val window = (view.context as Activity).window
            window.statusBarColor = colorScheme.primary.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = darkTheme
        }}
    }}
    MaterialTheme(colorScheme = colorScheme, typography = Typography, content = content)
}}
''')


def create_resource_files(config: ConversionConfig, app_name: str) -> None:
    """Create resource files."""
    res_path = config.android_path / "app" / "src" / "main" / "res"
    
    (res_path / "values" / "strings.xml").write_text(f'''<resources>
    <string name="app_name">{app_name}</string>
</resources>
''')
    
    (res_path / "values" / "themes.xml").write_text(f'''<resources xmlns:tools="http://schemas.android.com/tools">
    <style name="Theme.{app_name}" parent="android:Theme.Material.Light.NoActionBar" />
</resources>
''')


def convert_swift_to_kotlin(swift_content: str, filename: str) -> str:
    """Convert Swift code to Kotlin (basic conversion)."""
    kotlin = swift_content
    
    replacements = [
        (r'\blet\b', 'val'), (r'\bvar\b', 'var'), (r'\bfunc\b', 'fun'),
        (r'\bnil\b', 'null'), (r'\bself\b', 'this'), (r'\bstruct\b', 'data class'),
        (r'\benum\b', 'enum class'), (r'\bprotocol\b', 'interface'),
        (r'\bBool\b', 'Boolean'), (r'\[(\w+)\]', r'List<\1>'),
        (r'\?\?', '?:'), (r'-> Void', ': Unit'), (r'-> (\w+)', r': \1'),
        (r'\\\(([^)]+)\)', r'${\1}'), (r'\.count\b', '.size'),
        (r'\.isEmpty\b', '.isEmpty()'), (r'\.append\(', '.add('),
        (r'\.first\b', '.firstOrNull()'), (r'print\(', 'println('),
        (r'import Foundation', '// import Foundation'),
        (r'import UIKit', '// import UIKit'),
        (r'import SwiftUI', '// import SwiftUI - use Compose'),
        (r'import Combine', '// import Combine - use Flow'),
    ]
    
    for pattern, replacement in replacements:
        kotlin = re.sub(pattern, replacement, kotlin)
    
    # Add TODO markers
    markers = [
        (r'@Published\b', '// TODO: VERIFY - Convert to MutableStateFlow'),
        (r'@State\b', '// TODO: VERIFY - Convert to remember { mutableStateOf() }'),
        (r'@ObservedObject\b', '// TODO: VERIFY - Convert to viewModel()'),
    ]
    
    for pattern, marker in markers:
        if re.search(pattern, kotlin):
            kotlin = marker + '\n' + kotlin
            break
    
    return kotlin


def run_analysis(ios_path: Path) -> dict:
    """Run the iOS analyzer."""
    import subprocess
    script_dir = Path(__file__).parent
    analyze_script = script_dir / "analyze_ios.py"
    
    result = subprocess.run(["python3", str(analyze_script), str(ios_path)], capture_output=True, text=True)
    if result.returncode != 0:
        return {}
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {}


def convert_source_files(config: ConversionConfig, analysis: dict) -> dict:
    """Convert source files from Swift to Kotlin."""
    file_mapping = {}
    pkg_path = config.package_name.replace('.', '/')
    
    for category, subdir in [('model_files', 'model'), ('viewmodel_files', 'viewmodel')]:
        target_dir = config.android_path / "app" / "src" / "main" / "java" / pkg_path / subdir
        
        for file_info in analysis.get(category, []):
            swift_path = config.ios_path / file_info['path']
            if not swift_path.exists():
                continue
            
            swift_content = swift_path.read_text(errors='ignore')
            kotlin_content = convert_swift_to_kotlin(swift_content, file_info['name'])
            kotlin_content = f"package {config.package_name}.{subdir}\n\n" + kotlin_content
            
            kotlin_path = target_dir / (file_info['name'] + ".kt")
            kotlin_path.write_text(kotlin_content)
            file_mapping[file_info['path']] = str(kotlin_path.relative_to(config.android_path))
    
    return file_mapping


def create_sync_state(config: ConversionConfig, file_mapping: dict) -> None:
    """Create sync state file."""
    sync_state = {
        "lastSyncDate": datetime.now().isoformat(),
        "iosCommit": None,
        "iosPath": str(config.ios_path),
        "androidPath": str(config.android_path),
        "packageName": config.package_name,
        "fileMapping": file_mapping,
        "checksums": {}
    }
    (config.android_path / ".ios-android-sync.json").write_text(json.dumps(sync_state, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Convert iOS Swift project to Android Kotlin")
    parser.add_argument("ios_path", help="Path to iOS project")
    parser.add_argument("android_path", help="Path for Android project output")
    parser.add_argument("--package", required=True, help="Android package name")
    parser.add_argument("--min-sdk", type=int, default=24, help="Minimum SDK version")
    parser.add_argument("--compose", action="store_true", default=True)
    parser.add_argument("--xml-views", action="store_true")
    parser.add_argument("--di", choices=["hilt", "koin", "manual"], default="hilt")
    
    args = parser.parse_args()
    
    ios_path = Path(args.ios_path).resolve()
    android_path = Path(args.android_path).resolve()
    
    if not ios_path.exists():
        print(f"Error: iOS project not found: {ios_path}", file=sys.stderr)
        sys.exit(1)
    
    config = ConversionConfig(
        ios_path=ios_path, android_path=android_path, package_name=args.package,
        min_sdk=args.min_sdk, use_compose=not args.xml_views, di_framework=args.di
    )
    
    app_name = args.package.split('.')[-1].title().replace('_', '').replace('-', '')
    
    print(f"Converting: {ios_path} -> {android_path}")
    print(f"Package: {args.package}, App: {app_name}\n")
    
    print("Analyzing iOS project...")
    analysis = run_analysis(ios_path)
    if analysis:
        print(f"  Files: {analysis.get('total_swift_files', 0)}, Arch: {analysis.get('architecture_pattern', '?')}\n")
    
    print("Creating Android project...")
    create_directory_structure(config)
    create_gradle_files(config, app_name)
    create_android_files(config, app_name)
    create_theme_files(config, app_name)
    create_resource_files(config, app_name)
    
    print("Converting source files...")
    file_mapping = convert_source_files(config, analysis) if analysis else {}
    create_sync_state(config, file_mapping)
    
    print(f"\n{'='*50}")
    print("Conversion complete!")
    print(f"{'='*50}")
    print(f"\nProject: {android_path}")
    print("\nNext steps:")
    print("1. Open in Android Studio")
    print("2. Run: grep -r 'TODO: VERIFY' app/src/")
    print("3. Build and test")


if __name__ == "__main__":
    main()
