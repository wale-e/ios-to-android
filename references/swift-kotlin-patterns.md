# Swift to Kotlin Patterns

## Table of Contents

- [Basic Syntax](#basic-syntax)
- [Closures / Lambdas](#closures--lambdas)
- [Classes and Structs](#classes-and-structs)
- [Enums](#enums)
- [Protocols / Interfaces](#protocols--interfaces)
- [Extensions](#extensions)
- [Generics](#generics)
- [Error Handling](#error-handling)
- [Collections](#collections)
- [Higher-Order Functions](#higher-order-functions)
- [Async/Await & Concurrency](#asyncawait--concurrency)
- [Combine → Flow](#combine--flow)
- [Property Wrappers → Delegated Properties](#property-wrappers--delegated-properties)

## Basic Syntax

### Variables and Constants

```swift
// Swift                          // Kotlin
let constant = "value"            val constant = "value"
var variable = "value"            var variable = "value"

let name: String = "John"         val name: String = "John"
var age: Int = 25                 var age: Int = 25

// Type inference works similarly in both languages
```

### Optionals

```swift
// Swift                          // Kotlin
var name: String? = nil           var name: String? = null
var name: String? = "John"        var name: String? = "John"

// Unwrapping
if let name = name {              name?.let { name ->
    print(name)                       println(name)
}                                 }

// Or simpler
name?.let { print($0) }           name?.let { println(it) }

// Guard
guard let name = name else {      val name = name ?: return
    return
}

// Force unwrap (avoid!)
name!                             name!!

// Nil coalescing
name ?? "Unknown"                 name ?: "Unknown"

// Optional chaining
user?.address?.street             user?.address?.street

// Safe call with default
user?.name ?? "N/A"               user?.name ?: "N/A"
```

### Functions

```swift
// Swift                          // Kotlin
func greet(name: String) {        fun greet(name: String) {
    print("Hello, \(name)")           println("Hello, $name")
}                                 }

func add(_ a: Int, _ b: Int)      fun add(a: Int, b: Int): Int {
    -> Int {                          return a + b
    return a + b                  }
}
                                  // Or single expression
                                  fun add(a: Int, b: Int): Int = a + b

// Default parameters
func greet(name: String = "World")    fun greet(name: String = "World")

// Variadic
func sum(_ numbers: Int...) -> Int    fun sum(vararg numbers: Int): Int =
    { numbers.reduce(0, +) }              numbers.sum()

// Trailing closure
func execute(action: () -> Void)  fun execute(action: () -> Unit)
execute { print("Done") }         execute { println("Done") }

// Throws
func fetch() throws -> Data       @Throws(Exception::class)
                                  fun fetch(): Data

// Async
func fetch() async throws -> Data suspend fun fetch(): Data
```

## Closures / Lambdas

```swift
// Swift                          // Kotlin
let add: (Int, Int) -> Int =      val add: (Int, Int) -> Int = { a, b ->
    { a, b in a + b }                 a + b
                                  }

// Shorthand
{ $0 + $1 }                       { a, b -> a + b }

// Single param
names.map { $0.uppercased() }     names.map { it.uppercase() }

// Trailing closure
fetch { result in                 fetch { result ->
    print(result)                     println(result)
}                                 }

// @escaping
func store(_ action:              fun store(action: () -> Unit) {
    @escaping () -> Void) {           // Kotlin closures are always "escaping"
    self.action = action              this.action = action
}                                 }

// Capture list
{ [weak self] in                  { // No direct equivalent, use WeakReference if needed
    self?.doSomething()               weakSelf?.get()?.doSomething()
}                                 }
```

## Classes and Structs

```swift
// Swift Struct → Kotlin Data Class
struct User {                     data class User(
    let id: String                    val id: String,
    var name: String                  var name: String,
    let email: String?                val email: String?
}                                 )

// Swift Class → Kotlin Class
class UserManager {               class UserManager {
    private var users: [User] = []    private var users: MutableList<User> = mutableListOf()

    func add(_ user: User) {          fun add(user: User) {
        users.append(user)                users.add(user)
    }                                 }
}                                 }

// Computed properties
var fullName: String {            val fullName: String
    "\(firstName) \(lastName)"        get() = "$firstName $lastName"
}

var count: Int {                  var count: Int
    get { _count }                    get() = _count
    set { _count = newValue }         set(value) { _count = value }
}

// Lazy
lazy var expensive = compute()    val expensive by lazy { compute() }

// Static
static let shared = Manager()     companion object {
                                      val shared = Manager()
                                  }
```

## Enums

```swift
// Swift                          // Kotlin
enum Status {                     enum class Status {
    case pending                      PENDING,
    case approved                     APPROVED,
    case rejected                     REJECTED
}                                 }

// With raw values
enum Status: String {             enum class Status(val value: String) {
    case pending = "pending"          PENDING("pending"),
    case approved = "approved"        APPROVED("approved"),
    case rejected = "rejected"        REJECTED("rejected")
}                                 }

// Associated values → Sealed class
enum Result {                     sealed class Result {
    case success(Data)                data class Success(val data: Data) : Result()
    case failure(Error)               data class Failure(val error: Throwable) : Result()
}                                 }

// Usage
switch result {                   when (result) {
case .success(let data):              is Result.Success -> println(result.data)
    print(data)                       is Result.Failure -> println(result.error)
case .failure(let error):         }
    print(error)
}
```

## Protocols / Interfaces

```swift
// Swift Protocol                 // Kotlin Interface
protocol Identifiable {           interface Identifiable {
    var id: String { get }            val id: String
}                                 }

protocol DataSource {             interface DataSource {
    func numberOfItems() -> Int       fun numberOfItems(): Int
    func item(at index: Int)          fun item(index: Int): Item
        -> Item
}                                 }

// Default implementation
extension Identifiable {          interface Identifiable {
    var displayId: String {           val id: String
        "ID: \(id)"                   val displayId: String
    }                                     get() = "ID: $id"
}                                 }

// Protocol conformance
struct User: Identifiable {       data class User(
    let id: String                    override val id: String
}                                 ) : Identifiable
```

## Extensions

```swift
// Swift                          // Kotlin
extension String {                fun String.isValidEmail(): Boolean {
    var isValidEmail: Bool {          return contains("@") && contains(".")
        contains("@") &&          }
        contains(".")
    }                             // Property extension
}                                 val String.isValidEmail: Boolean
                                      get() = contains("@") && contains(".")

extension Array where             fun <T : Comparable<T>> List<T>.isSorted(): Boolean {
    Element: Comparable {             return this == this.sorted()
    func isSorted() -> Bool {     }
        self == self.sorted()
    }
}
```

## Generics

```swift
// Swift                          // Kotlin
func swap<T>(_ a: inout T,        fun <T> swap(a: T, b: T): Pair<T, T> {
    _ b: inout T) {                   return Pair(b, a)
    let temp = a                  }
    a = b
    b = temp
}

struct Stack<Element> {           class Stack<T> {
    private var items: [Element]      private val items = mutableListOf<T>()
        = []
    mutating func push(_ item:        fun push(item: T) {
        Element) {                        items.add(item)
        items.append(item)            }
    }
}                                 }

// Constraints
func process<T: Codable>(_ item: T)   fun <T : Serializable> process(item: T)

// Multiple constraints
func compare<T: Comparable &      fun <T> compare(a: T, b: T) where T : Comparable<T>, T : Identifiable
    Identifiable>(_ a: T, _ b: T)
```

## Error Handling

```swift
// Swift                          // Kotlin
enum NetworkError: Error {        sealed class NetworkError : Exception() {
    case notFound                     object NotFound : NetworkError()
    case unauthorized                 object Unauthorized : NetworkError()
    case serverError(code: Int)       data class ServerError(val code: Int) : NetworkError()
}                                 }

func fetch() throws -> Data {     @Throws(NetworkError::class)
    throw NetworkError.notFound   fun fetch(): Data {
}                                     throw NetworkError.NotFound
                                  }

do {                              try {
    let data = try fetch()            val data = fetch()
} catch NetworkError.notFound {   } catch (e: NetworkError.NotFound) {
    print("Not found")                println("Not found")
} catch {                         } catch (e: Exception) {
    print("Error: \(error)")          println("Error: $e")
}                                 }

// Try?                           // Kotlin: use runCatching
let data = try? fetch()           val data = runCatching { fetch() }.getOrNull()

// Try!                           // Force (avoid!)
let data = try! fetch()           val data = fetch() // if it throws, crashes
```

## Collections

```swift
// Swift                          // Kotlin
// Arrays
var array = [1, 2, 3]             val array = listOf(1, 2, 3)        // Immutable
var mutableArray = [1, 2, 3]      val mutableArray = mutableListOf(1, 2, 3)

array.append(4)                   mutableArray.add(4)
array.remove(at: 0)               mutableArray.removeAt(0)
array.count                       array.size
array.isEmpty                     array.isEmpty()
array.first                       array.firstOrNull()
array.last                        array.lastOrNull()

// Dictionaries
var dict = ["a": 1, "b": 2]       val map = mapOf("a" to 1, "b" to 2)
var mutableDict: [String: Int]    val mutableMap = mutableMapOf("a" to 1)

dict["c"] = 3                     mutableMap["c"] = 3
dict.removeValue(forKey: "a")     mutableMap.remove("a")
dict.keys                         map.keys
dict.values                       map.values

// Sets
var set: Set<Int> = [1, 2, 3]     val set = setOf(1, 2, 3)
var mutableSet = Set<Int>()       val mutableSet = mutableSetOf<Int>()

set.insert(4)                     mutableSet.add(4)
set.remove(1)                     mutableSet.remove(1)
set.contains(2)                   set.contains(2)
```

## Higher-Order Functions

```swift
// Swift                          // Kotlin
array.map { $0 * 2 }              array.map { it * 2 }
array.filter { $0 > 5 }           array.filter { it > 5 }
array.reduce(0, +)                array.reduce(0) { acc, i -> acc + i }
                                  // or array.sum()

array.compactMap { $0 }           array.mapNotNull { it }
array.flatMap { $0.items }        array.flatMap { it.items }
array.sorted()                    array.sorted()
array.sorted(by: >)               array.sortedDescending()
array.sorted { $0.name < $1.name }    array.sortedBy { it.name }

array.first { $0 > 5 }            array.firstOrNull { it > 5 }
array.contains { $0 > 5 }         array.any { it > 5 }
array.allSatisfy { $0 > 0 }       array.all { it > 0 }

array.forEach { print($0) }       array.forEach { println(it) }
array.enumerated().forEach {      array.forEachIndexed { index, item ->
    print("\($0): \($1)")             println("$index: $item")
}                                 }

// Chaining
array                             array
    .filter { $0 > 0 }                .filter { it > 0 }
    .map { $0 * 2 }                   .map { it * 2 }
    .sorted()                         .sorted()
```

## Async/Await & Concurrency

```swift
// Swift                          // Kotlin
func fetch() async throws -> Data {   suspend fun fetch(): Data {
    let data = try await api.get()        val data = api.get()
    return data                           return data
}                                     }

Task {                            viewModelScope.launch {
    let result = await fetch()        val result = fetch()
}                                 }

Task.detached {                   GlobalScope.launch {
    await heavyWork()                 heavyWork()
}                                 }

// Parallel
async let a = fetchA()            val a = async { fetchA() }
async let b = fetchB()            val b = async { fetchB() }
let results = await (a, b)        val results = listOf(a.await(), b.await())

// Actor (Swift) → Mutex/synchronized (Kotlin)
actor Counter {                   class Counter {
    private var count = 0             private val mutex = Mutex()
    func increment() {                private var count = 0
        count += 1                    suspend fun increment() {
    }                                     mutex.withLock { count += 1 }
}                                     }
                                  }

// MainActor                      // Main dispatcher
@MainActor                        withContext(Dispatchers.Main) {
func updateUI() { }                   updateUI()
                                  }
```

## Combine → Flow

```swift
// Swift Combine                  // Kotlin Flow
@Published var items: [Item] = [] private val _items = MutableStateFlow<List<Item>>(emptyList())
                                  val items: StateFlow<List<Item>> = _items.asStateFlow()

// Update
items = newItems                  _items.value = newItems

// Subscribe
$items                            items
    .sink { items in                  .collect { items ->
        print(items.count)                println(items.size)
    }                                 }
    .store(in: &cancellables)

// Map
$items                            items
    .map { $0.count }                 .map { it.size }
    .sink { }                         .collect { }

// Filter
$items                            items
    .filter { !$0.isEmpty }           .filter { it.isNotEmpty() }

// Combine latest
Publishers.CombineLatest(a, b)    combine(a, b) { aVal, bVal ->
    .map { a, b in a + b }            aVal + bVal
                                  }

// Debounce
$searchText                       searchText
    .debounce(for: .seconds(0.3),     .debounce(300)
        scheduler: RunLoop.main)       .collect { }
    .sink { }

// Just (single value)
Just("Hello")                     flowOf("Hello")

// PassthroughSubject
let subject =                     val channel = Channel<String>()
    PassthroughSubject<String,    // Or use MutableSharedFlow
        Never>()                  val sharedFlow = MutableSharedFlow<String>()
subject.send("Hello")             sharedFlow.emit("Hello")
```

## Property Wrappers → Delegated Properties

```swift
// Swift                          // Kotlin
@Published var name: String       var name by mutableStateOf("")

@AppStorage("key") var value      // Use DataStore
                                  val value = dataStore.data.map { it[KEY] }

@State var count = 0              var count by remember { mutableStateOf(0) }

@Binding var text: String         // Pattern: pass value + onChange callback
                                  fun MyComponent(
                                      text: String,
                                      onTextChange: (String) -> Unit
                                  )

// Custom property wrapper        // Custom delegate
@propertyWrapper                  class Logged<T>(initialValue: T) : ReadWriteProperty<Any?, T> {
struct Logged<Value> {                private var value = initialValue
    private var value: Value          override fun getValue(thisRef: Any?, property: KProperty<*>): T {
    var wrappedValue: Value {             println("Getting ${property.name}")
        get { value }                     return value
        set {                         }
            print("Setting to          override fun setValue(thisRef: Any?, property: KProperty<*>, value: T) {
                \(newValue)")              println("Setting ${property.name} to $value")
            value = newValue              this.value = value
        }                             }
    }                             }
}
                                  var name: String by Logged("initial")
@Logged var name = "initial"
```
