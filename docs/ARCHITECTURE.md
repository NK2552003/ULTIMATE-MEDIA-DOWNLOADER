# Architecture Documentation - Ultimate Media Downloader

**Version**: 2.0.0  
**Last Updated**: October 2, 2025  
**Author**: Nitish Kumar

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Patterns](#architecture-patterns)
3. [Component Architecture](#component-architecture)
4. [Data Flow](#data-flow)
5. [Module Descriptions](#module-descriptions)
6. [Design Decisions](#design-decisions)
7. [Scalability Considerations](#scalability-considerations)
8. [Security Architecture](#security-architecture)

---

## System Overview

The Ultimate Media Downloader is built using a modular, layered architecture that separates concerns and allows for easy extension and maintenance.

### Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│  (CLI Interface, Interactive Mode, Rich UI Components)       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Application Layer                          │
│  (Business Logic, Validation, Orchestration)                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Service Layer                              │
│  (Platform Handlers, Download Services, Auth Services)       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Integration Layer                          │
│  (yt-dlp, FFmpeg, Browser Automation, APIs)                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Infrastructure Layer                       │
│  (File System, Network, Cache, Logging)                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Architecture Patterns

### 1. Strategy Pattern (Platform Handlers)

Different platforms require different download strategies. The Strategy pattern allows dynamic selection of the appropriate handler.

```python
class PlatformHandler(ABC):
    @abstractmethod
    def can_handle(self, url: str) -> bool:
        pass
    
    @abstractmethod
    def download(self, url: str, options: dict) -> Result:
        pass

class YouTubeHandler(PlatformHandler):
    def can_handle(self, url: str) -> bool:
        return 'youtube.com' in url or 'youtu.be' in url
    
    def download(self, url: str, options: dict) -> Result:
        # YouTube-specific implementation
        pass

class SpotifyHandler(PlatformHandler):
    def can_handle(self, url: str) -> bool:
        return 'spotify.com' in url
    
    def download(self, url: str, options: dict) -> Result:
        # Spotify-specific implementation
        pass
```

### 2. Factory Pattern (Handler Creation)

The Factory pattern creates appropriate handlers based on URL analysis.

```python
class HandlerFactory:
    def __init__(self):
        self.handlers = [
            YouTubeHandler(),
            SpotifyHandler(),
            InstagramHandler(),
            GenericHandler()
        ]
    
    def get_handler(self, url: str) -> PlatformHandler:
        for handler in self.handlers:
            if handler.can_handle(url):
                return handler
        return GenericHandler()
```

### 3. Observer Pattern (Progress Tracking)

Progress updates are broadcast to multiple observers (UI, logs, stats).

```python
class DownloadProgressObserver(ABC):
    @abstractmethod
    def on_progress(self, downloaded: int, total: int):
        pass

class UIProgressObserver(DownloadProgressObserver):
    def on_progress(self, downloaded: int, total: int):
        # Update progress bar
        pass

class LogProgressObserver(DownloadProgressObserver):
    def on_progress(self, downloaded: int, total: int):
        # Log progress
        pass
```

### 4. Chain of Responsibility (Error Handling)

Errors are passed through a chain of handlers until one can handle it.

```python
class ErrorHandler(ABC):
    def __init__(self, next_handler=None):
        self.next_handler = next_handler
    
    def handle(self, error: Exception) -> bool:
        if self.can_handle(error):
            return self.process(error)
        elif self.next_handler:
            return self.next_handler.handle(error)
        return False

class NetworkErrorHandler(ErrorHandler):
    def can_handle(self, error: Exception) -> bool:
        return isinstance(error, NetworkError)
    
    def process(self, error: Exception) -> bool:
        # Retry with exponential backoff
        pass
```

### 5. Singleton Pattern (Configuration)

Configuration is loaded once and shared across the application.

```python
class Config:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.load_config()
        return cls._instance
```

---

## Component Architecture

### 1. Core Components

#### UltimateDownloader (Main Class)

**Responsibilities:**
- Application orchestration
- Command-line argument parsing
- Main execution flow

**Key Methods:**
```python
class UltimateDownloader:
    def __init__(self, config: Config)
    def parse_arguments(self) -> Args
    def run(self, url: str, options: dict) -> Result
    def download(self, url: str) -> Result
    def download_playlist(self, url: str) -> List[Result]
```

#### URLParser

**Responsibilities:**
- URL validation
- Domain extraction
- Platform identification

**Key Methods:**
```python
class URLParser:
    def parse(self, url: str) -> ParsedURL
    def validate(self, url: str) -> bool
    def extract_domain(self, url: str) -> str
    def identify_platform(self, url: str) -> Platform
```

#### DownloadManager

**Responsibilities:**
- Download queue management
- Worker thread pool
- Concurrency control

**Key Methods:**
```python
class DownloadManager:
    def add_to_queue(self, item: DownloadItem)
    def start_workers(self, num_workers: int)
    def process_queue(self)
    def wait_completion(self) -> List[Result]
```

### 2. Platform Handlers

Each platform handler implements the `PlatformHandler` interface:

```python
# YouTube Handler
class YouTubeHandler(PlatformHandler):
    - download_video()
    - download_playlist()
    - download_channel()
    - extract_metadata()
    - get_formats()

# Spotify Handler
class SpotifyHandler(PlatformHandler):
    - authenticate()
    - search_track()
    - download_track()
    - download_album()
    - download_playlist()

# Instagram Handler
class InstagramHandler(PlatformHandler):
    - download_post()
    - download_reel()
    - download_story()
    - handle_private()

# Generic Handler
class GenericSiteDownloader(PlatformHandler):
    - try_ytdlp()
    - try_requests()
    - try_selenium()
    - try_playwright()
    - extract_video_urls()
```

### 3. Download Engine Components

#### YTDLPEngine

**Responsibilities:**
- Wrapper around yt-dlp
- Format selection
- Progress callbacks

**Key Methods:**
```python
class YTDLPEngine:
    def extract_info(self, url: str) -> dict
    def download(self, url: str, options: dict)
    def get_formats(self, url: str) -> List[Format]
    def select_best_format(self, formats: List[Format]) -> Format
```

#### StreamDownloader

**Responsibilities:**
- Direct stream downloads
- HLS/DASH handling
- Resume support

**Key Methods:**
```python
class StreamDownloader:
    def download_stream(self, url: str, output: Path)
    def download_hls(self, m3u8_url: str, output: Path)
    def download_dash(self, mpd_url: str, output: Path)
    def resume_download(self, url: str, partial_file: Path)
```

#### BrowserAutomation

**Responsibilities:**
- Selenium/Playwright integration
- JavaScript rendering
- Anti-bot bypass

**Key Methods:**
```python
class BrowserAutomation:
    def initialize_driver(self) -> WebDriver
    def fetch_page(self, url: str) -> str
    def extract_video_url(self, page_source: str) -> str
    def handle_captcha(self) -> bool
    def close(self)
```

### 4. Post-Processing Components

#### FFmpegProcessor

**Responsibilities:**
- Video/audio conversion
- Format transformation
- Stream merging

**Key Methods:**
```python
class FFmpegProcessor:
    def convert_format(self, input: Path, output: Path, format: str)
    def merge_streams(self, video: Path, audio: Path, output: Path)
    def extract_audio(self, video: Path, output: Path)
    def normalize_audio(self, audio: Path)
```

#### MetadataEditor

**Responsibilities:**
- ID3 tag editing
- Thumbnail embedding
- Metadata extraction

**Key Methods:**
```python
class MetadataEditor:
    def set_metadata(self, file: Path, metadata: dict)
    def embed_thumbnail(self, file: Path, image: Path)
    def extract_metadata(self, file: Path) -> dict
    def set_cover_art(self, file: Path, image: Path)
```

#### FileOrganizer

**Responsibilities:**
- File naming
- Directory structure
- Archive management

**Key Methods:**
```python
class FileOrganizer:
    def generate_filename(self, metadata: dict) -> str
    def create_directory_structure(self, base: Path, metadata: dict)
    def move_file(self, src: Path, dst: Path)
    def update_archive(self, item: DownloadItem)
```

---

## Data Flow

### Download Process Data Flow

```
1. User Input (URL)
       ↓
2. URLParser.parse()
       ↓
3. HandlerFactory.get_handler()
       ↓
4. PlatformHandler.extract_info()
       ↓
5. DownloadManager.add_to_queue()
       ↓
6. Worker Thread Pool
       ↓
7. DownloadEngine.download()
       ↓
8. StreamDownloader.download_stream()
       ↓
9. ProgressObserver.on_progress()
       ↓
10. File saved to disk
       ↓
11. FFmpegProcessor.convert_format()
       ↓
12. MetadataEditor.set_metadata()
       ↓
13. FileOrganizer.organize()
       ↓
14. Result returned to user
```

### Authentication Data Flow

```
1. Platform requires auth
       ↓
2. AuthService.check_cached_credentials()
       ↓
3. If not cached:
   - AuthService.get_credentials()
   - AuthService.authenticate()
   - AuthService.cache_token()
       ↓
4. Request headers updated with auth token
       ↓
5. Authenticated requests sent
```

---

## Module Descriptions

### ultimate_downloader.py (Main Module)

**Lines of Code**: ~6,454  
**Primary Classes**:
- `UltimateDownloader` - Main application class
- `ModernUI` - UI components
- `Icons` - Icon management
- `Messages` - Message templates
- `QuietLogger` - Custom logger

**Key Features**:
- Command-line interface
- Interactive mode
- Multi-threaded downloads
- Progress tracking
- Rich UI integration

### generic_downloader.py (Generic Handler Module)

**Lines of Code**: ~1,219  
**Primary Class**:
- `GenericSiteDownloader` - Universal site handler

**Key Features**:
- Multiple fallback methods
- SSL/TLS bypass
- Cloudflare bypass
- Proxy support
- User agent rotation

---

## Design Decisions

### 1. Why Python?

**Pros:**
- Rich ecosystem of media libraries
- Easy integration with yt-dlp
- Rapid development
- Cross-platform compatibility

**Cons:**
- Performance overhead
- GIL limitations for true parallelism

### 2. Why yt-dlp as Core Engine?

**Pros:**
- Supports 1000+ sites out of the box
- Active development
- Extensive format support
- Regular updates for site changes

**Cons:**
- External dependency
- Some sites require custom handling

### 3. Why Virtual Environment?

**Pros:**
- Isolated dependencies
- Version control
- No system pollution
- Easy cleanup

**Cons:**
- Requires activation
- Slight overhead

### 4. Why Rich Library for UI?

**Pros:**
- Beautiful terminal output
- Progress bars and spinners
- Cross-platform colors
- Easy to use API

**Cons:**
- Dependency overhead
- Not suitable for GUI

### 5. Why Multiple Fallback Methods?

**Rational:**
- Sites change frequently
- Anti-bot measures vary
- No single method works for all
- Increases success rate

---

## Scalability Considerations

### Horizontal Scalability

**Current Implementation:**
- Multi-threaded worker pool
- Configurable concurrency

**Future Enhancements:**
- Distributed task queue (Celery)
- Multiple machine support
- Load balancing

### Vertical Scalability

**Current Implementation:**
- Efficient memory usage
- Streaming downloads
- Chunked processing

**Future Enhancements:**
- GPU acceleration for encoding
- Better caching strategies
- Memory-mapped files

### Performance Optimizations

1. **Connection Pooling**: Reuse HTTP connections
2. **Caching**: Cache metadata and authentication
3. **Lazy Loading**: Load modules only when needed
4. **Async I/O**: For network operations
5. **Compression**: Compress cached data

---

## Security Architecture

### 1. Authentication Security

**Measures:**
- Credentials never stored in plain text
- Token-based authentication
- Secure credential prompts
- Cookie encryption

### 2. Network Security

**Measures:**
- SSL/TLS for all connections
- Certificate verification (when possible)
- Proxy support for anonymity
- User agent randomization

### 3. File System Security

**Measures:**
- Proper file permissions
- Path traversal prevention
- Sanitized filenames
- Temp file cleanup

### 4. Input Validation

**Measures:**
- URL validation
- Type checking
- Length limits
- XSS prevention

### 5. Dependencies Security

**Measures:**
- Regular dependency updates
- Security audit of packages
- Minimal dependencies
- Trusted sources only

---

## Technology Stack

### Core Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Runtime | Python | 3.9+ | Core language |
| Download Engine | yt-dlp | Latest | Video/audio extraction |
| Media Processing | FFmpeg | 4.0+ | Format conversion |
| HTTP Client | Requests | 2.31+ | Web requests |
| Browser Automation | Selenium/Playwright | Latest | JavaScript sites |
| UI Framework | Rich | 13.7+ | Terminal UI |

### Dependencies

**Essential:**
- yt-dlp
- requests
- rich
- mutagen
- Pillow

**Optional:**
- spotipy (Spotify)
- selenium (Browser automation)
- playwright (Advanced automation)
- cloudscraper (Cloudflare bypass)

---

## Future Architecture Enhancements

### Short Term (v2.1)

1. **Plugin System**: Allow third-party handlers
2. **Configuration UI**: Web-based configuration
3. **REST API**: Remote control
4. **Database**: SQLite for metadata

### Medium Term (v2.5)

1. **Microservices**: Separate download workers
2. **Message Queue**: RabbitMQ/Redis integration
3. **Load Balancing**: Distribute across machines
4. **Monitoring**: Prometheus/Grafana integration

### Long Term (v3.0)

1. **Cloud Native**: Kubernetes deployment
2. **Serverless**: AWS Lambda functions
3. **Real-time Sync**: WebSocket support
4. **Mobile Apps**: iOS/Android clients

---

## Deployment Architecture

### Development Environment

```
Developer Machine
├── Python 3.9+
├── Virtual Environment
├── Development Dependencies
└── Local Testing
```

### Production Environment

```
Production Server
├── Python 3.9+ (system or venv)
├── FFmpeg
├── ChromeDriver
├── Supervisor (process manager)
├── Nginx (reverse proxy - future)
└── Log Rotation
```

---

## Monitoring & Observability

### Logging Strategy

**Levels:**
- DEBUG: Detailed diagnostic info
- INFO: General operational events
- WARNING: Warning messages
- ERROR: Error events
- CRITICAL: Critical failures

**Log Locations:**
- Console output (via Rich)
- File logs (downloads.log)
- Error logs (errors.log)

### Metrics to Track

- Download success/failure rate
- Average download speed
- Concurrent downloads
- Error frequency by type
- Platform-specific metrics

---

## Testing Strategy

### Unit Tests

- Individual function testing
- Mock external dependencies
- Edge case coverage

### Integration Tests

- End-to-end workflows
- Real platform testing
- Error scenario testing

### Performance Tests

- Large playlist handling
- Concurrent download limits
- Memory usage profiling

---

**Document Version**: 2.0.0  
**Last Review**: October 2, 2025  
**Next Review**: January 2026
