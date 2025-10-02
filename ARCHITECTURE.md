# Project Architecture

## Overview

This document provides a comprehensive overview of the Ultimate Media Downloader architecture, including workflow diagrams, class relationships, and design patterns used.

## System Architecture

### High-Level Architecture

```mermaid
graph TB
    subgraph "Presentation Layer"
        CLI[Command Line Interface]
        Interactive[Interactive Mode]
        UI[Rich UI Components]
    end
    
    subgraph "Application Layer"
        Main[Main Controller]
        Downloader[Media Downloader]
        PlatformMgr[Platform Manager]
    end
    
    subgraph "Business Logic Layer"
        YouTube[YouTube Handler]
        Spotify[Spotify Handler]
        Apple[Apple Music Handler]
        Sound[SoundCloud Handler]
        Generic[Generic Handler]
    end
    
    subgraph "Integration Layer"
        YTDLP[yt-dlp Engine]
        SpotifyAPI[Spotify API]
        WebScraper[Web Scraper]
        Search[YouTube Search]
    end
    
    subgraph "Infrastructure Layer"
        FFmpeg[FFmpeg Processor]
        FileSystem[File System]
        Metadata[Metadata Handler]
        Cache[Cache Manager]
    end
    
    CLI --> Main
    Interactive --> UI
    UI --> Main
    Main --> Downloader
    Downloader --> PlatformMgr
    
    PlatformMgr --> YouTube
    PlatformMgr --> Spotify
    PlatformMgr --> Apple
    PlatformMgr --> Sound
    PlatformMgr --> Generic
    
    YouTube --> YTDLP
    Spotify --> SpotifyAPI
    Spotify --> Search
    Apple --> WebScraper
    Apple --> Search
    Sound --> YTDLP
    Generic --> YTDLP
    
    YTDLP --> FFmpeg
    YTDLP --> FileSystem
    Downloader --> Metadata
    Downloader --> Cache
    Metadata --> FileSystem
```

## Component Breakdown

### 1. Presentation Layer

#### CLI Interface
```python
class CommandLineInterface:
    """Handles command-line argument parsing and validation."""
    
    def parse_arguments(self) -> argparse.Namespace:
        """Parse and validate command-line arguments."""
        pass
    
    def validate_inputs(self, args: argparse.Namespace) -> bool:
        """Validate user inputs."""
        pass
```

#### Interactive Mode
```python
class InteractiveMode:
    """Manages interactive user sessions."""
    
    def start_session(self):
        """Start interactive mode loop."""
        pass
    
    def handle_command(self, command: str):
        """Process user commands."""
        pass
```

### 2. Application Layer

#### Main Controller
```mermaid
flowchart TD
    Start([Start Application]) --> ParseArgs[Parse Arguments]
    ParseArgs --> CheckMode{Mode?}
    
    CheckMode -->|Interactive| ShowBanner[Show Welcome Banner]
    CheckMode -->|CLI| ValidateURL[Validate URL]
    
    ShowBanner --> MainLoop[Interactive Loop]
    MainLoop --> GetInput[Get User Input]
    GetInput --> ProcessCmd{Command Type?}
    
    ProcessCmd -->|URL| InitDownload[Initialize Download]
    ProcessCmd -->|help| ShowHelp[Show Help]
    ProcessCmd -->|platforms| ListPlatforms[List Platforms]
    ProcessCmd -->|quit| Exit([Exit])
    
    ValidateURL --> InitDownload
    InitDownload --> DetectPlatform[Detect Platform]
    DetectPlatform --> ChooseHandler[Select Handler]
    ChooseHandler --> Download[Execute Download]
    Download --> PostProcess[Post-Process]
    PostProcess --> Complete[Complete]
    
    ShowHelp --> MainLoop
    ListPlatforms --> MainLoop
    Complete --> MainLoop
```

### 3. Platform Detection System

```mermaid
flowchart LR
    URL[Input URL] --> Detect{Detect Platform}
    
    Detect -->|youtube.com| YT[YouTube Handler]
    Detect -->|spotify.com| SP[Spotify Handler]
    Detect -->|music.apple.com| AM[Apple Music Handler]
    Detect -->|soundcloud.com| SC[SoundCloud Handler]
    Detect -->|instagram.com| IG[Instagram Handler]
    Detect -->|tiktok.com| TT[TikTok Handler]
    Detect -->|twitter.com| TW[Twitter Handler]
    Detect -->|Other| GN[Generic Handler]
    
    YT --> DirectDL[Direct Download]
    SC --> DirectDL
    IG --> DirectDL
    TT --> DirectDL
    TW --> DirectDL
    GN --> DirectDL
    
    SP --> Extract[Extract Metadata]
    AM --> Extract
    Extract --> Search[YouTube Search]
    Search --> DirectDL
    
    DirectDL --> Process[Process Media]
```

## Data Flow Diagrams

### Download Workflow

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant Downloader
    participant Platform
    participant YTDLP
    participant FFmpeg
    participant FileSystem
    
    User->>CLI: Provide URL + Options
    CLI->>Downloader: Initialize download request
    
    Downloader->>Platform: Detect platform
    Platform-->>Downloader: Platform type
    
    alt YouTube/Direct Platform
        Downloader->>YTDLP: Download with format
        YTDLP->>FileSystem: Fetch media
        FileSystem-->>YTDLP: Media data
    else Spotify/Apple Music
        Downloader->>Platform: Extract metadata
        Platform-->>Downloader: Track info
        Downloader->>YTDLP: Search YouTube
        YTDLP-->>Downloader: YouTube URL
        Downloader->>YTDLP: Download from YouTube
        YTDLP->>FileSystem: Fetch media
        FileSystem-->>YTDLP: Media data
    end
    
    YTDLP->>FFmpeg: Convert format
    FFmpeg-->>YTDLP: Converted file
    
    YTDLP-->>Downloader: File path
    
    opt Embed Metadata
        Downloader->>Platform: Fetch album art
        Platform-->>Downloader: Album art
        Downloader->>FileSystem: Embed metadata
    end
    
    Downloader-->>CLI: Success status
    CLI-->>User: Download complete
```

### Playlist Processing

```mermaid
flowchart TD
    Start([Playlist URL]) --> Extract[Extract Playlist Info]
    Extract --> GetItems[Get All Items]
    GetItems --> Count{Item Count?}
    
    Count -->|Single| DownloadDirect[Direct Download]
    Count -->|Multiple| ShowList[Display Items]
    
    ShowList --> UserChoice{User Selection}
    UserChoice -->|All| SelectAll[Select All Items]
    UserChoice -->|Range| SelectRange[Select Range]
    UserChoice -->|Specific| SelectSpecific[Select Specific]
    
    SelectAll --> Queue[Create Download Queue]
    SelectRange --> Queue
    SelectSpecific --> Queue
    DownloadDirect --> Queue
    
    Queue --> Process[Process Queue]
    Process --> NextItem{More Items?}
    
    NextItem -->|Yes| Download[Download Item]
    Download --> Success{Success?}
    Success -->|Yes| IncrSuccess[Increment Success]
    Success -->|No| IncrFail[Increment Failed]
    
    IncrSuccess --> NextItem
    IncrFail --> NextItem
    NextItem -->|No| Summary[Show Summary]
    
    Summary --> End([Complete])
```

### Metadata Embedding Flow

```mermaid
flowchart TD
    Start([Audio File]) --> CheckFormat{Format Type?}
    
    CheckFormat -->|MP3| LoadMP3[Load with Mutagen ID3]
    CheckFormat -->|FLAC| LoadFLAC[Load with Mutagen FLAC]
    CheckFormat -->|M4A| LoadM4A[Load with Mutagen MP4]
    CheckFormat -->|Other| Skip[Skip Metadata]
    
    LoadMP3 --> FetchArt[Fetch Album Art]
    LoadFLAC --> FetchArt
    LoadM4A --> FetchArt
    
    FetchArt --> Source{Art Source?}
    Source -->|Spotify| SpotifyArt[Get from Spotify API]
    Source -->|Apple Music| AppleArt[Get from Apple Music]
    Source -->|Thumbnail| ThumbArt[Use Video Thumbnail]
    
    SpotifyArt --> ProcessImg[Process Image]
    AppleArt --> ProcessImg
    ThumbArt --> ProcessImg
    
    ProcessImg --> Resize{Resize Needed?}
    Resize -->|Yes| ResizeImg[Resize to 1000x1000]
    Resize -->|No| EmbedData[Embed Metadata]
    
    ResizeImg --> EmbedData
    EmbedData --> AddTags[Add Tags]
    
    AddTags --> SetTitle[Set Title]
    SetTitle --> SetArtist[Set Artist]
    SetArtist --> SetAlbum[Set Album]
    SetAlbum --> SetYear[Set Year]
    SetYear --> EmbedArt[Embed Album Art]
    
    EmbedArt --> Save[Save File]
    Skip --> End([Complete])
    Save --> End
```

## Class Diagram

```mermaid
classDiagram
    class UltimateMediaDownloader {
        -output_dir: Path
        -console: Console
        -spotify_client: Spotipy
        -default_ydl_opts: dict
        +detect_platform(url: str): str
        +download_media(url, quality, audio_only): bool
        +download_playlist(url, quality): bool
        +search_youtube(query): str
        -_progress_hook(d: dict): void
        -_embed_album_art(file, art_data): void
    }
    
    class ModernUI {
        -console: Console
        +show_welcome_banner(): void
        +show_interactive_banner(): void
        +create_download_progress(): Progress
        +success_message(msg: str): void
        +error_message(msg: str): void
        +info_message(msg: str): void
        +prompt_input(prompt: str): str
    }
    
    class QuietLogger {
        +debug(msg: str): void
        +info(msg: str): void
        +warning(msg: str): void
        +error(msg: str): void
    }
    
    class Icons {
        +get(name: str): str
    }
    
    class Messages {
        +success(text: str): str
        +error(text: str): str
        +warning(text: str): str
        +info(text: str): str
    }
    
    class PlatformHandler {
        <<interface>>
        +detect(url: str): bool
        +download(url: str, options: dict): bool
        +extract_metadata(url: str): dict
    }
    
    class YouTubeHandler {
        +detect(url: str): bool
        +download(url: str, options: dict): bool
    }
    
    class SpotifyHandler {
        -client: Spotipy
        +detect(url: str): bool
        +extract_metadata(url: str): dict
        +search_youtube(query: str): str
    }
    
    class AppleMusicHandler {
        +detect(url: str): bool
        +extract_metadata(url: str): dict
        +scrape_info(url: str): dict
    }
    
    UltimateMediaDownloader --> ModernUI
    UltimateMediaDownloader --> QuietLogger
    UltimateMediaDownloader --> Icons
    UltimateMediaDownloader --> Messages
    UltimateMediaDownloader --> PlatformHandler
    
    PlatformHandler <|-- YouTubeHandler
    PlatformHandler <|-- SpotifyHandler
    PlatformHandler <|-- AppleMusicHandler
    
    ModernUI --> Icons
    ModernUI --> Messages
```

## Design Patterns Used

### 1. Strategy Pattern
Used for platform-specific download handlers.

```python
class PlatformStrategy:
    """Strategy interface for platform handlers."""
    def download(self, url: str, options: dict) -> bool:
        raise NotImplementedError

class YouTubeStrategy(PlatformStrategy):
    def download(self, url: str, options: dict) -> bool:
        # YouTube-specific implementation
        pass

class SpotifyStrategy(PlatformStrategy):
    def download(self, url: str, options: dict) -> bool:
        # Spotify-specific implementation
        pass
```

### 2. Factory Pattern
Used for creating platform handlers.

```python
class PlatformHandlerFactory:
    @staticmethod
    def create_handler(platform: str) -> PlatformStrategy:
        handlers = {
            'youtube': YouTubeStrategy,
            'spotify': SpotifyStrategy,
            'apple_music': AppleMusicStrategy,
        }
        return handlers.get(platform, GenericStrategy)()
```

### 3. Observer Pattern
Used for progress tracking.

```python
class DownloadObserver:
    def update(self, progress_data: dict):
        raise NotImplementedError

class ProgressBarObserver(DownloadObserver):
    def update(self, progress_data: dict):
        # Update progress bar
        pass

class LoggerObserver(DownloadObserver):
    def update(self, progress_data: dict):
        # Log progress
        pass
```

### 4. Singleton Pattern
Used for configuration management.

```python
class Config:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

## State Management

```mermaid
stateDiagram-v2
    [*] --> Idle
    
    Idle --> Initializing: Start Download
    Initializing --> DetectingPlatform: URL Validated
    DetectingPlatform --> ExtractingMetadata: Platform Detected
    
    ExtractingMetadata --> Searching: Spotify/Apple Music
    ExtractingMetadata --> Downloading: Direct Platform
    
    Searching --> Downloading: YouTube URL Found
    Searching --> Failed: Search Failed
    
    Downloading --> Converting: Download Complete
    Converting --> EmbeddingMetadata: Conversion Complete
    EmbeddingMetadata --> Complete: Metadata Added
    
    Converting --> Complete: No Metadata
    
    Failed --> Idle: Retry
    Complete --> Idle: Ready for Next
    Complete --> [*]: Exit
```

## Performance Optimization

### Concurrent Downloads

```mermaid
gantt
    title Parallel Download Timeline
    dateFormat X
    axisFormat %L
    
    section Thread 1
    URL 1 Download: 0, 1000
    URL 1 Convert: 1000, 1500
    
    section Thread 2
    URL 2 Download: 0, 800
    URL 2 Convert: 800, 1200
    
    section Thread 3
    URL 3 Download: 0, 1200
    URL 3 Convert: 1200, 1800
    
    section Main Thread
    Queue Management: 0, 1800
    Final Processing: 1800, 2000
```

### Caching Strategy

```mermaid
flowchart TD
    Request[Download Request] --> CheckCache{In Cache?}
    
    CheckCache -->|Yes| ValidCache{Valid?}
    CheckCache -->|No| FetchData[Fetch from Source]
    
    ValidCache -->|Yes| ReturnCache[Return Cached Data]
    ValidCache -->|No| FetchData
    
    FetchData --> StoreCache[Store in Cache]
    StoreCache --> ReturnData[Return Data]
    
    ReturnCache --> End([Complete])
    ReturnData --> End
```

## Error Handling

```mermaid
flowchart TD
    Start([Operation Start]) --> Try[Try Operation]
    Try --> Success{Success?}
    
    Success -->|Yes| Return[Return Result]
    Success -->|No| ErrorType{Error Type?}
    
    ErrorType -->|Network| Retry{Retry Count < Max?}
    ErrorType -->|Validation| LogError[Log Error]
    ErrorType -->|Platform| Fallback[Try Fallback]
    ErrorType -->|Unknown| LogError
    
    Retry -->|Yes| Wait[Wait & Backoff]
    Retry -->|No| LogError
    
    Wait --> Try
    Fallback --> AlternativeMethod[Use Alternative]
    AlternativeMethod --> Success
    
    LogError --> Notify[Notify User]
    Notify --> ReturnError[Return Error]
    
    Return --> End([Complete])
    ReturnError --> End
```

## Security Considerations

### URL Validation

```mermaid
flowchart TD
    URL[Input URL] --> Parse[Parse URL]
    Parse --> CheckScheme{Valid Scheme?}
    
    CheckScheme -->|No| Reject[Reject URL]
    CheckScheme -->|Yes| CheckDomain{Trusted Domain?}
    
    CheckDomain -->|No| Warn[Show Warning]
    CheckDomain -->|Yes| Sanitize[Sanitize Parameters]
    
    Warn --> UserConfirm{User Confirms?}
    UserConfirm -->|No| Reject
    UserConfirm -->|Yes| Sanitize
    
    Sanitize --> Validate[Final Validation]
    Validate --> Accept[Accept URL]
    
    Reject --> End([Rejected])
    Accept --> End([Accepted])
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "User Machine"
        CLI[Command Line]
        Files[Downloaded Files]
    end
    
    subgraph "Application"
        App[Ultimate Downloader]
        Cache[Local Cache]
    end
    
    subgraph "External Services"
        YouTube[YouTube]
        Spotify[Spotify API]
        AppleMusic[Apple Music]
        CDN[Content CDN]
    end
    
    CLI --> App
    App --> Cache
    App --> YouTube
    App --> Spotify
    App --> AppleMusic
    App --> CDN
    
    YouTube --> Files
    CDN --> Files
    Cache --> Files
```

---

*This architecture document is maintained alongside the codebase and updated with major changes.*
