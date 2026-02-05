# SwiftUI to Jetpack Compose Mapping

## Table of Contents

- [Views / Composables](#views--composables)
- [Layout Containers](#layout-containers)
- [Modifiers](#modifiers)
- [State Management](#state-management)
- [Navigation](#navigation)
- [Animations](#animations)
- [Gestures](#gestures)
- [Environment & Theming](#environment--theming)
- [Common Patterns](#common-patterns)

## Views / Composables

### Basic Components

```swift
// SwiftUI                        // Jetpack Compose
Text("Hello")                     Text("Hello")
Text("Bold").bold()               Text("Bold", fontWeight = FontWeight.Bold)
Text("Large").font(.title)        Text("Large", style = MaterialTheme.typography.headlineMedium)

Image("photo")                    Image(painter = painterResource(R.drawable.photo), contentDescription = null)
Image(systemName: "star")         Icon(Icons.Default.Star, contentDescription = null)
AsyncImage(url: url)              AsyncImage(model = url, contentDescription = null) // Coil

Button("Tap") { action() }        Button(onClick = { action() }) { Text("Tap") }
Button(action: {}) {              TextButton(onClick = {}) { Text("Link") }
    Text("Link")
}.buttonStyle(.plain)

TextField("Placeholder",          OutlinedTextField(
    text: $text)                      value = text,
                                      onValueChange = { text = it },
                                      label = { Text("Placeholder") }
                                  )

SecureField("Password",           OutlinedTextField(
    text: $password)                  value = password,
                                      onValueChange = { password = it },
                                      visualTransformation = PasswordVisualTransformation()
                                  )

Toggle(isOn: $isOn) {             Switch(checked = isOn, onCheckedChange = { isOn = it })
    Text("Label")
}

Slider(value: $value)             Slider(value = value, onValueChange = { value = it })

ProgressView()                    CircularProgressIndicator()
ProgressView(value: 0.5)          LinearProgressIndicator(progress = 0.5f)
```

## Layout Containers

```swift
// SwiftUI                        // Jetpack Compose
VStack {                          Column {
    Text("A")                         Text("A")
    Text("B")                         Text("B")
}                                 }

VStack(alignment: .leading,       Column(
    spacing: 16) {                    modifier = Modifier.fillMaxWidth(),
    ...                               verticalArrangement = Arrangement.spacedBy(16.dp),
}                                     horizontalAlignment = Alignment.Start
                                  ) { ... }

HStack {                          Row {
    Text("A")                         Text("A")
    Text("B")                         Text("B")
}                                 }

ZStack {                          Box {
    Background()                      Background()
    Foreground()                      Foreground()
}                                 }

ScrollView {                      Column(modifier = Modifier.verticalScroll(rememberScrollState())) {
    ...                               ...
}                                 }

ScrollView(.horizontal) {         Row(modifier = Modifier.horizontalScroll(rememberScrollState())) {
    ...                               ...
}                                 }

LazyVStack {                      LazyColumn {
    ForEach(items) { item in          items(items) { item ->
        ItemView(item)                    ItemView(item)
    }                                 }
}                                 }

LazyHStack {                      LazyRow {
    ...                               ...
}                                 }

LazyVGrid(columns:                LazyVerticalGrid(
    [GridItem(.flexible())]) {        columns = GridCells.Adaptive(100.dp)
    ...                           ) { ... }
}

List(items) { item in             LazyColumn {
    ItemRow(item)                     items(items) { item ->
}                                         ItemRow(item)
                                      }
                                  }

Spacer()                          Spacer(modifier = Modifier.weight(1f))
Divider()                         Divider()
```

## Modifiers

```swift
// SwiftUI                        // Jetpack Compose
.frame(width: 100, height: 50)    Modifier.size(100.dp, 50.dp)
.frame(maxWidth: .infinity)       Modifier.fillMaxWidth()
.frame(maxHeight: .infinity)      Modifier.fillMaxHeight()

.padding()                        Modifier.padding(16.dp)
.padding(.horizontal, 16)         Modifier.padding(horizontal = 16.dp)
.padding(.top, 8)                 Modifier.padding(top = 8.dp)

.background(.red)                 Modifier.background(Color.Red)
.background {                     Modifier.background(
    RoundedRectangle(cornerRadius: 8)     color = Color.Red,
        .fill(.red)                       shape = RoundedCornerShape(8.dp)
}                                 )

.foregroundColor(.blue)           // Use color parameter on Text/Icon directly
.tint(.blue)                      // Use LocalContentColor or explicit colors

.cornerRadius(8)                  Modifier.clip(RoundedCornerShape(8.dp))

.shadow(radius: 4)                Modifier.shadow(elevation = 4.dp)

.opacity(0.5)                     Modifier.alpha(0.5f)

.rotationEffect(.degrees(45))     Modifier.rotate(45f)
.scaleEffect(1.5)                 Modifier.scale(1.5f)
.offset(x: 10, y: 20)             Modifier.offset(x = 10.dp, y = 20.dp)

.onTapGesture { }                 Modifier.clickable { }
.onLongPressGesture { }           Modifier.combinedClickable(onLongClick = { })

.disabled(true)                   // enabled = false on component, or Modifier.alpha(0.5f)
.hidden()                         // Conditionally don't include in composition

.edgesIgnoringSafeArea(.all)      Modifier.fillMaxSize() // with WindowInsets handling
.safeAreaInset(edge: .bottom)     // Use WindowInsets.navigationBars, etc.
```

## State Management

```swift
// SwiftUI                        // Jetpack Compose
@State var count = 0              var count by remember { mutableStateOf(0) }

@Binding var value: String        // Pass value + onValueChange callback
                                  // Or use State hoisting pattern

@StateObject var vm = VM()        val vm: VM = viewModel()
@ObservedObject var vm: VM        val vm: VM = viewModel()
@EnvironmentObject var vm: VM     val vm: VM = viewModel() // or CompositionLocal

@Observable class VM {            class VM : ViewModel() {
    var items: [Item] = []            private val _items = MutableStateFlow<List<Item>>(emptyList())
}                                     val items: StateFlow<List<Item>> = _items.asStateFlow()
                                  }

// Usage in view                  // Usage in composable
vm.items.count                    val items by vm.items.collectAsStateWithLifecycle()
                                  items.size

@Published var data: Data         private val _data = MutableStateFlow<Data?>(null)
                                  val data: StateFlow<Data?> = _data.asStateFlow()

@AppStorage("key") var val        // Use DataStore
                                  val preferences by dataStore.data.collectAsStateWithLifecycle()
```

## Navigation

```swift
// SwiftUI                        // Jetpack Compose
NavigationStack {                 NavHost(navController, startDestination = "home") {
    HomeView()                        composable("home") { HomeScreen() }
        .navigationDestination(       composable("detail/{id}") { backStackEntry ->
            for: Item.self) {             DetailScreen(backStackEntry.arguments?.getString("id"))
            DetailView(item: $0)      }
        }                         }
}

NavigationLink(value: item) {     navController.navigate("detail/${item.id}")
    Text(item.name)
}

.navigationTitle("Home")          TopAppBar(title = { Text("Home") })

.toolbar {                        TopAppBar(
    ToolbarItem(placement:            actions = {
        .topBarTrailing) {                IconButton(onClick = {}) {
        Button("Edit") { }                    Icon(Icons.Default.Edit, null)
    }                                     }
}                                     }
                                  )

.sheet(isPresented: $show) {      if (show) {
    SheetContent()                    ModalBottomSheet(onDismissRequest = { show = false }) {
}                                         SheetContent()
                                      }
                                  }

.alert("Title",                   if (showAlert) {
    isPresented: $show) {             AlertDialog(
    Button("OK") { }                      onDismissRequest = { showAlert = false },
}                                         title = { Text("Title") },
                                          confirmButton = {
                                              TextButton(onClick = { showAlert = false }) {
                                                  Text("OK")
                                              }
                                          }
                                      )
                                  }
```

## Animations

```swift
// SwiftUI                        // Jetpack Compose
withAnimation {                   // Compose auto-animates state changes in many cases
    show.toggle()                 // For explicit: use animate*AsState
}

withAnimation(.spring()) {        val size by animateDpAsState(
    size = expanded ? 200 : 100       targetValue = if (expanded) 200.dp else 100.dp,
}                                     animationSpec = spring()
                                  )

.animation(.default, value: x)    // Compose: use animate*AsState or Animatable

.transition(.slide)               AnimatedVisibility(
                                      visible = show,
                                      enter = slideInHorizontally(),
                                      exit = slideOutHorizontally()
                                  ) { Content() }

.transition(.opacity)             AnimatedVisibility(
                                      visible = show,
                                      enter = fadeIn(),
                                      exit = fadeOut()
                                  ) { Content() }

if condition {                    AnimatedContent(targetState = condition) { state ->
    ViewA()                           if (state) ViewA() else ViewB()
} else {                          }
    ViewB()
}
```

## Gestures

```swift
// SwiftUI                        // Jetpack Compose
.gesture(                         Modifier.pointerInput(Unit) {
    DragGesture()                     detectDragGestures { change, dragAmount ->
        .onChanged { }                    // Handle drag
        .onEnded { }                  }
)                                 }

.gesture(                         Modifier.pointerInput(Unit) {
    MagnificationGesture()            detectTransformGestures { _, pan, zoom, rotation ->
        .onChanged { scale in             // Handle pinch/zoom
        }                             }
)                                 }

.simultaneousGesture(...)         // Compose gestures are composable by default

.highPriorityGesture(...)         // Use Modifier ordering for priority
```

## Environment & Theming

```swift
// SwiftUI                        // Jetpack Compose
@Environment(\.colorScheme)       isSystemInDarkTheme()
var colorScheme

Color.primary                     MaterialTheme.colorScheme.onSurface
Color.secondary                   MaterialTheme.colorScheme.onSurfaceVariant
Color.accentColor                 MaterialTheme.colorScheme.primary

.preferredColorScheme(.dark)      // Set in theme at app level

Font.title                        MaterialTheme.typography.headlineMedium
Font.body                         MaterialTheme.typography.bodyLarge
Font.caption                      MaterialTheme.typography.bodySmall

// Custom environment value       // CompositionLocal
@Environment(\.myValue)           val myValue = LocalMyValue.current
var myValue
```

## Common Patterns

```swift
// Pull to refresh - SwiftUI      // Pull to refresh - Compose
List {                            val pullRefreshState = rememberPullRefreshState(
    ...                               refreshing = isRefreshing,
}                                     onRefresh = { refresh() }
.refreshable {                    )
    await refresh()               Box(Modifier.pullRefresh(pullRefreshState)) {
}                                     LazyColumn { ... }
                                      PullRefreshIndicator(
                                          refreshing = isRefreshing,
                                          state = pullRefreshState,
                                          modifier = Modifier.align(Alignment.TopCenter)
                                      )
                                  }

// Search - SwiftUI               // Search - Compose
.searchable(text: $query)         var query by remember { mutableStateOf("") }
                                  SearchBar(
                                      query = query,
                                      onQueryChange = { query = it },
                                      onSearch = { performSearch(it) },
                                      active = searchActive,
                                      onActiveChange = { searchActive = it }
                                  ) { /* suggestions */ }

// TabView - SwiftUI              // TabRow - Compose
TabView {                         var selectedTab by remember { mutableStateOf(0) }
    HomeView()                    Scaffold(
        .tabItem {                    bottomBar = {
            Label("Home",                 NavigationBar {
                systemImage: "house")         NavigationBarItem(
        }                                         selected = selectedTab == 0,
    SettingsView()                                onClick = { selectedTab = 0 },
        .tabItem { ... }                          icon = { Icon(Icons.Default.Home, null) },
}                                                 label = { Text("Home") }
                                              )
                                              // More items...
                                          }
                                      }
                                  ) { padding ->
                                      when (selectedTab) {
                                          0 -> HomeScreen(Modifier.padding(padding))
                                          1 -> SettingsScreen(Modifier.padding(padding))
                                      }
                                  }
```
