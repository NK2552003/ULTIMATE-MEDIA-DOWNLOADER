# Process Flowcharts - Ultimate Media Downloader

This document contains all the process flowcharts for the Ultimate Media Downloader system, created using Mermaid syntax.

## Table of Contents
1. [Main Application Flow](#1-main-application-flow)
2. [Download Process Flow](#2-download-process-flow)
3. [Platform Detection Flow](#3-platform-detection-flow)
4. [Authentication Flow](#4-authentication-flow)
5. [Post-Processing Flow](#5-post-processing-flow)
6. [Error Handling Flow](#6-error-handling-flow)
7. [Playlist Processing Flow](#7-playlist-processing-flow)
8. [Configuration Flow](#8-configuration-flow)

---

## 1. Main Application Flow

```mermaid
flowchart TD
    Start([Start Application]) --> Init[Initialize System]
    Init --> LoadConfig[Load Configuration]
    LoadConfig --> ParseArgs[Parse Command Line Arguments]
    ParseArgs --> CheckMode{Check Mode}
    
    CheckMode -->|Interactive| Interactive[Launch Interactive Mode]
    CheckMode -->|CLI| ValidateURL[Validate URL]
    CheckMode -->|Search| SearchMode[Search Mode]
    
    Interactive --> GetUserInput[Get User Input]
    GetUserInput --> ValidateURL
    
    SearchMode --> PerformSearch[Perform Search]
    PerformSearch --> DisplayResults[Display Results]
    DisplayResults --> UserSelect[User Selects Item]
    UserSelect --> ValidateURL
    
    ValidateURL --> URLValid{URL Valid?}
    URLValid -->|No| ShowError[Show Error Message]
    ShowError --> CheckMode
    
    URLValid -->|Yes| DetectPlatform[Detect Platform]
    DetectPlatform --> SelectHandler[Select Platform Handler]
    SelectHandler --> InitDownload[Initialize Download]
    
    InitDownload --> DownloadProcess[Download Process]
    DownloadProcess --> PostProcess[Post-Processing]
    PostProcess --> Complete{Complete?}
    
    Complete -->|Yes| SaveMetadata[Save Metadata]
    SaveMetadata --> ShowSuccess[Show Success Message]
    ShowSuccess --> CheckMore{More Downloads?}
    
    Complete -->|No| HandleError[Handle Error]
    HandleError --> Retry{Retry?}
    Retry -->|Yes| InitDownload
    Retry -->|No| CheckMore
    
    CheckMore -->|Yes| CheckMode
    CheckMore -->|No| Cleanup[Cleanup & Exit]
    Cleanup --> End([End])
    
    style Start fill:#4CAF50
    style End fill:#F44336
    style DownloadProcess fill:#2196F3
    style PostProcess fill:#FF9800
```

---

## 2. Download Process Flow

```mermaid
flowchart TD
    Start([Start Download]) --> CheckCache{Check Cache}
    CheckCache -->|Found| UseCached[Use Cached Data]
    CheckCache -->|Not Found| ExtractInfo[Extract Media Info]
    
    ExtractInfo --> ParseMetadata[Parse Metadata]
    ParseMetadata --> CheckQuality{Quality Check}
    
    CheckQuality -->|Available| SelectFormat[Select Best Format]
    CheckQuality -->|Not Available| AdjustQuality[Adjust Quality Settings]
    AdjustQuality --> SelectFormat
    
    SelectFormat --> CheckAuth{Authentication Required?}
    CheckAuth -->|Yes| AuthProcess[Authentication Process]
    CheckAuth -->|No| InitStream[Initialize Stream]
    AuthProcess --> InitStream
    
    InitStream --> CheckType{Media Type}
    
    CheckType -->|Video| DownloadVideo[Download Video Stream]
    CheckType -->|Audio| DownloadAudio[Download Audio Stream]
    CheckType -->|Both| DownloadBoth[Download Video + Audio]
    
    DownloadVideo --> MergeCheck{Merge Required?}
    DownloadAudio --> ProcessAudio[Process Audio]
    DownloadBoth --> MergeStreams[Merge Streams]
    
    MergeCheck -->|Yes| MergeStreams
    MergeCheck -->|No| ProcessVideo[Process Video]
    
    MergeStreams --> ProcessVideo
    ProcessVideo --> CheckSuccess{Download Success?}
    ProcessAudio --> CheckSuccess
    
    CheckSuccess -->|Yes| VerifyFile[Verify File Integrity]
    CheckSuccess -->|No| RetryLogic{Retry Available?}
    
    RetryLogic -->|Yes| WaitRetry[Wait Before Retry]
    RetryLogic -->|No| FailDownload[Mark as Failed]
    WaitRetry --> InitStream
    
    VerifyFile --> Integrity{File OK?}
    Integrity -->|Yes| SaveToCache[Save to Cache]
    Integrity -->|No| RetryLogic
    
    SaveToCache --> Complete([Download Complete])
    FailDownload --> Error([Download Failed])
    UseCached --> Complete
    
    style Start fill:#4CAF50
    style Complete fill:#4CAF50
    style Error fill:#F44336
    style DownloadVideo fill:#2196F3
    style DownloadAudio fill:#9C27B0
```

---

## 3. Platform Detection Flow

```mermaid
flowchart TD
    Start([URL Input]) --> ParseURL[Parse URL]
    ParseURL --> ExtractDomain[Extract Domain]
    ExtractDomain --> CheckKnown{Known Platform?}
    
    CheckKnown -->|Yes| IdentifyPlatform{Identify Platform}
    CheckKnown -->|No| GenericHandler[Use Generic Handler]
    
    IdentifyPlatform -->|YouTube| YouTubeHandler[YouTube Handler]
    IdentifyPlatform -->|Spotify| SpotifyHandler[Spotify Handler]
    IdentifyPlatform -->|Instagram| InstagramHandler[Instagram Handler]
    IdentifyPlatform -->|TikTok| TikTokHandler[TikTok Handler]
    IdentifyPlatform -->|SoundCloud| SoundCloudHandler[SoundCloud Handler]
    IdentifyPlatform -->|Twitter| TwitterHandler[Twitter Handler]
    IdentifyPlatform -->|Facebook| FacebookHandler[Facebook Handler]
    IdentifyPlatform -->|Apple Music| AppleMusicHandler[Apple Music Handler]
    IdentifyPlatform -->|Vimeo| VimeoHandler[Vimeo Handler]
    IdentifyPlatform -->|Twitch| TwitchHandler[Twitch Handler]
    IdentifyPlatform -->|Generic| GenericHandler
    
    YouTubeHandler --> CheckType{Content Type}
    SpotifyHandler --> RequireAuth{Auth Required?}
    InstagramHandler --> CheckPrivate{Private?}
    TikTokHandler --> ExtractVideo[Extract Video]
    SoundCloudHandler --> ExtractTrack[Extract Track]
    TwitterHandler --> ExtractMedia[Extract Media]
    FacebookHandler --> ExtractVideo
    AppleMusicHandler --> RequireAuth
    VimeoHandler --> ExtractVideo
    TwitchHandler --> CheckStreamType{Stream Type?}
    
    CheckType -->|Video| ProcessYTVideo[Process Video]
    CheckType -->|Playlist| ProcessYTPlaylist[Process Playlist]
    CheckType -->|Channel| ProcessYTChannel[Process Channel]
    CheckType -->|Live| ProcessYTLive[Process Live Stream]
    
    CheckStreamType -->|VOD| ProcessVOD[Process VOD]
    CheckStreamType -->|Clip| ProcessClip[Process Clip]
    CheckStreamType -->|Live| ProcessLive[Process Live]
    
    RequireAuth -->|Yes| GetCredentials[Get Credentials]
    RequireAuth -->|No| ProcessContent[Process Content]
    GetCredentials --> Authenticate[Authenticate]
    Authenticate --> Success{Auth Success?}
    Success -->|Yes| ProcessContent
    Success -->|No| AuthError[Authentication Error]
    
    CheckPrivate -->|Yes| RequireLogin[Require Login]
    CheckPrivate -->|No| PublicDownload[Public Download]
    
    GenericHandler --> TryMethods[Try Multiple Methods]
    TryMethods --> Method1{Try yt-dlp}
    Method1 -->|Success| ProcessContent
    Method1 -->|Fail| Method2{Try Requests}
    Method2 -->|Success| ProcessContent
    Method2 -->|Fail| Method3{Try Selenium}
    Method3 -->|Success| ProcessContent
    Method3 -->|Fail| Method4{Try Playwright}
    Method4 -->|Success| ProcessContent
    Method4 -->|Fail| FailExtraction[Extraction Failed]
    
    ProcessYTVideo --> Complete([Handler Selected])
    ProcessYTPlaylist --> Complete
    ProcessYTChannel --> Complete
    ProcessYTLive --> Complete
    ProcessVOD --> Complete
    ProcessClip --> Complete
    ProcessLive --> Complete
    ProcessContent --> Complete
    PublicDownload --> Complete
    ExtractVideo --> Complete
    ExtractTrack --> Complete
    ExtractMedia --> Complete
    
    AuthError --> Error([Error])
    FailExtraction --> Error
    
    style Start fill:#4CAF50
    style Complete fill:#4CAF50
    style Error fill:#F44336
```

---

## 4. Authentication Flow

```mermaid
flowchart TD
    Start([Auth Required]) --> CheckCached{Cached Credentials?}
    CheckCached -->|Yes| ValidateCache[Validate Cache]
    CheckCached -->|No| GetCredentials[Get Credentials]
    
    ValidateCache --> CacheValid{Valid?}
    CacheValid -->|Yes| UseCache[Use Cached Auth]
    CacheValid -->|No| GetCredentials
    
    GetCredentials --> CheckMethod{Auth Method}
    
    CheckMethod -->|API Key| APIAuth[API Key Authentication]
    CheckMethod -->|OAuth| OAuthFlow[OAuth Flow]
    CheckMethod -->|Cookies| CookieAuth[Cookie Authentication]
    CheckMethod -->|Username/Password| LoginAuth[Login Authentication]
    
    APIAuth --> ValidateKey[Validate API Key]
    ValidateKey --> KeyValid{Valid?}
    KeyValid -->|Yes| StoreToken[Store Token]
    KeyValid -->|No| KeyError[Invalid Key Error]
    
    OAuthFlow --> OpenBrowser[Open Browser]
    OpenBrowser --> UserAuthorize[User Authorizes]
    UserAuthorize --> GetToken[Get OAuth Token]
    GetToken --> TokenValid{Valid?}
    TokenValid -->|Yes| StoreToken
    TokenValid -->|No| OAuthError[OAuth Error]
    
    CookieAuth --> LoadCookies[Load Cookie File]
    LoadCookies --> ValidateCookies[Validate Cookies]
    ValidateCookies --> CookiesValid{Valid?}
    CookiesValid -->|Yes| StoreSession[Store Session]
    CookiesValid -->|No| CookieError[Cookie Error]
    
    LoginAuth --> InputCreds[Input Credentials]
    InputCreds --> SendLogin[Send Login Request]
    SendLogin --> CheckResponse{Response?}
    CheckResponse -->|Success| GetSession[Get Session]
    CheckResponse -->|2FA Required| Handle2FA[Handle 2FA]
    CheckResponse -->|Captcha| SolveCaptcha[Solve Captcha]
    CheckResponse -->|Failed| LoginError[Login Failed]
    
    Handle2FA --> Get2FACode[Get 2FA Code]
    Get2FACode --> Verify2FA[Verify 2FA]
    Verify2FA --> TwoFAValid{Valid?}
    TwoFAValid -->|Yes| GetSession
    TwoFAValid -->|No| LoginError
    
    SolveCaptcha --> CaptchaSolved{Solved?}
    CaptchaSolved -->|Yes| SendLogin
    CaptchaSolved -->|No| LoginError
    
    GetSession --> StoreSession
    StoreSession --> StoreToken
    StoreToken --> CacheAuth[Cache Authentication]
    UseCache --> Success([Auth Success])
    CacheAuth --> Success
    
    KeyError --> Retry{Retry?}
    OAuthError --> Retry
    CookieError --> Retry
    LoginError --> Retry
    
    Retry -->|Yes| GetCredentials
    Retry -->|No| AuthFailed([Auth Failed])
    
    style Start fill:#FF9800
    style Success fill:#4CAF50
    style AuthFailed fill:#F44336
```

---

## 5. Post-Processing Flow

```mermaid
flowchart TD
    Start([File Downloaded]) --> CheckFormat{Format Conversion Needed?}
    
    CheckFormat -->|Yes| ConvertFormat[Convert Format]
    CheckFormat -->|No| CheckMetadata{Add Metadata?}
    
    ConvertFormat --> UseFFmpeg[Use FFmpeg]
    UseFFmpeg --> Conversion{Success?}
    Conversion -->|Yes| CheckMetadata
    Conversion -->|No| ConversionError[Conversion Error]
    
    CheckMetadata -->|Yes| ExtractMetadata[Extract Metadata]
    CheckMetadata -->|No| CheckThumbnail{Add Thumbnail?}
    
    ExtractMetadata --> ParseTags[Parse Tags]
    ParseTags --> GetArtwork[Get Artwork]
    GetArtwork --> ArtworkFound{Found?}
    ArtworkFound -->|Yes| DownloadArtwork[Download Artwork]
    ArtworkFound -->|No| UseDefault[Use Default]
    
    DownloadArtwork --> EmbedMetadata[Embed Metadata]
    UseDefault --> EmbedMetadata
    EmbedMetadata --> CheckThumbnail
    
    CheckThumbnail -->|Yes| GetThumbnail[Get Thumbnail]
    CheckThumbnail -->|No| CheckSubtitles{Add Subtitles?}
    
    GetThumbnail --> DownloadThumb[Download Thumbnail]
    DownloadThumb --> ProcessImage[Process Image]
    ProcessImage --> EmbedThumbnail[Embed Thumbnail]
    EmbedThumbnail --> CheckSubtitles
    
    CheckSubtitles -->|Yes| GetSubtitles[Get Subtitles]
    CheckSubtitles -->|No| CheckNormalize{Normalize Audio?}
    
    GetSubtitles --> DownloadSubs[Download Subtitles]
    DownloadSubs --> FormatSubs{Format Conversion?}
    FormatSubs -->|Yes| ConvertSubs[Convert Format]
    FormatSubs -->|No| EmbedSubs[Embed Subtitles]
    ConvertSubs --> EmbedSubs
    EmbedSubs --> CheckNormalize
    
    CheckNormalize -->|Yes| AnalyzeAudio[Analyze Audio]
    CheckNormalize -->|No| CheckQuality{Quality Check?}
    
    AnalyzeAudio --> NormalizeVolume[Normalize Volume]
    NormalizeVolume --> ApplyFilters[Apply Filters]
    ApplyFilters --> CheckQuality
    
    CheckQuality -->|Yes| VerifyQuality[Verify Quality]
    CheckQuality -->|No| FinalizeFile[Finalize File]
    
    VerifyQuality --> QualityOK{Quality OK?}
    QualityOK -->|Yes| FinalizeFile
    QualityOK -->|No| QualityWarning[Quality Warning]
    QualityWarning --> FinalizeFile
    
    FinalizeFile --> SetPermissions[Set Permissions]
    SetPermissions --> OrganizeFile[Organize File]
    OrganizeFile --> UpdateDatabase[Update Database]
    UpdateDatabase --> GenerateReport[Generate Report]
    GenerateReport --> Complete([Post-Processing Complete])
    
    ConversionError --> Error([Error])
    
    style Start fill:#2196F3
    style Complete fill:#4CAF50
    style Error fill:#F44336
```

---

## 6. Error Handling Flow

```mermaid
flowchart TD
    Start([Error Detected]) --> ClassifyError{Error Type}
    
    ClassifyError -->|Network| NetworkError[Network Error]
    ClassifyError -->|Auth| AuthError[Authentication Error]
    ClassifyError -->|Format| FormatError[Format Error]
    ClassifyError -->|Permission| PermError[Permission Error]
    ClassifyError -->|Disk Space| SpaceError[Disk Space Error]
    ClassifyError -->|Timeout| TimeoutError[Timeout Error]
    ClassifyError -->|Unknown| UnknownError[Unknown Error]
    
    NetworkError --> CheckConnection{Connection Available?}
    CheckConnection -->|Yes| RetryRequest[Retry Request]
    CheckConnection -->|No| WaitConnection[Wait for Connection]
    WaitConnection --> CheckConnection
    
    RetryRequest --> RetryCount{Retry Count < Max?}
    RetryCount -->|Yes| ExponentialBackoff[Exponential Backoff]
    RetryCount -->|No| NetworkFailed[Network Failed]
    ExponentialBackoff --> CheckConnection
    
    AuthError --> CheckCreds{Credentials Valid?}
    CheckCreds -->|Yes| RefreshAuth[Refresh Authentication]
    CheckCreds -->|No| RequestNewCreds[Request New Credentials]
    RefreshAuth --> AuthRetry{Success?}
    AuthRetry -->|Yes| Continue([Continue])
    AuthRetry -->|No| RequestNewCreds
    RequestNewCreds --> UserInput{User Provides?}
    UserInput -->|Yes| Continue
    UserInput -->|No| AuthFailed[Auth Failed]
    
    FormatError --> CheckFormat{Format Supported?}
    CheckFormat -->|Yes| TryAltMethod[Try Alternative Method]
    CheckFormat -->|No| SuggestFormat[Suggest Alternative]
    TryAltMethod --> MethodSuccess{Success?}
    MethodSuccess -->|Yes| Continue
    MethodSuccess -->|No| FormatFailed[Format Failed]
    SuggestFormat --> UserChoice{User Accepts?}
    UserChoice -->|Yes| ConvertFormat[Convert Format]
    UserChoice -->|No| FormatFailed
    ConvertFormat --> Continue
    
    PermError --> CheckPerms[Check Permissions]
    CheckPerms --> CanFix{Can Fix?}
    CanFix -->|Yes| FixPerms[Fix Permissions]
    CanFix -->|No| RequestSudo[Request Sudo]
    FixPerms --> PermSuccess{Success?}
    PermSuccess -->|Yes| Continue
    PermSuccess -->|No| RequestSudo
    RequestSudo --> SudoGranted{Granted?}
    SudoGranted -->|Yes| FixPerms
    SudoGranted -->|No| PermFailed[Permission Failed]
    
    SpaceError --> CheckSpace[Check Available Space]
    CheckSpace --> SpaceAvail{Enough Space?}
    SpaceAvail -->|Yes| Continue
    SpaceAvail -->|No| CleanTemp[Clean Temp Files]
    CleanTemp --> RecalcSpace[Recalculate Space]
    RecalcSpace --> StillLow{Still Low?}
    StillLow -->|Yes| AskUser[Ask User to Free Space]
    StillLow -->|No| Continue
    AskUser --> UserFreed{Space Freed?}
    UserFreed -->|Yes| Continue
    UserFreed -->|No| SpaceFailed[Insufficient Space]
    
    TimeoutError --> IncreaseTimeout[Increase Timeout]
    IncreaseTimeout --> RetryWithTimeout[Retry with New Timeout]
    RetryWithTimeout --> TimeoutRetry{Success?}
    TimeoutRetry -->|Yes| Continue
    TimeoutRetry -->|No| TimeoutFailed[Timeout Failed]
    
    UnknownError --> LogError[Log Detailed Error]
    LogError --> AnalyzeError[Analyze Error]
    AnalyzeError --> FindSolution{Solution Found?}
    FindSolution -->|Yes| ApplySolution[Apply Solution]
    FindSolution -->|No| ReportBug[Report Bug]
    ApplySolution --> SolutionWorks{Works?}
    SolutionWorks -->|Yes| Continue
    SolutionWorks -->|No| ReportBug
    ReportBug --> UnknownFailed[Unknown Failed]
    
    NetworkFailed --> LogFailure[Log Failure]
    AuthFailed --> LogFailure
    FormatFailed --> LogFailure
    PermFailed --> LogFailure
    SpaceFailed --> LogFailure
    TimeoutFailed --> LogFailure
    UnknownFailed --> LogFailure
    
    LogFailure --> NotifyUser[Notify User]
    NotifyUser --> CleanupError[Cleanup]
    CleanupError --> Failed([Operation Failed])
    
    Continue --> Success([Error Resolved])
    
    style Start fill:#FF9800
    style Success fill:#4CAF50
    style Failed fill:#F44336
```

---

## 7. Playlist Processing Flow

```mermaid
flowchart TD
    Start([Playlist URL]) --> ParsePlaylist[Parse Playlist URL]
    ParsePlaylist --> ExtractID[Extract Playlist ID]
    ExtractID --> FetchMetadata[Fetch Playlist Metadata]
    
    FetchMetadata --> GetInfo{Info Retrieved?}
    GetInfo -->|No| RetryFetch[Retry Fetch]
    GetInfo -->|Yes| ParseItems[Parse Playlist Items]
    RetryFetch --> FetchMetadata
    
    ParseItems --> CountItems[Count Items]
    CountItems --> CheckRange{User Range Specified?}
    
    CheckRange -->|Yes| ApplyRange[Apply Range Filter]
    CheckRange -->|No| UseAll[Use All Items]
    
    ApplyRange --> FilterItems[Filter Items]
    UseAll --> FilterItems
    FilterItems --> CheckReverse{Reverse Order?}
    
    CheckReverse -->|Yes| ReverseList[Reverse List]
    CheckReverse -->|No| InitQueue[Initialize Queue]
    ReverseList --> InitQueue
    
    InitQueue --> CheckArchive{Archive Mode?}
    CheckArchive -->|Yes| LoadArchive[Load Archive]
    CheckArchive -->|No| CreateBatches[Create Download Batches]
    
    LoadArchive --> FilterDownloaded[Filter Downloaded]
    FilterDownloaded --> CreateBatches
    
    CreateBatches --> SetConcurrency[Set Concurrency Level]
    SetConcurrency --> StartWorkers[Start Worker Threads]
    
    StartWorkers --> ProcessBatch[Process Next Batch]
    ProcessBatch --> GetNextItem{Next Item Available?}
    
    GetNextItem -->|Yes| AssignWorker[Assign to Worker]
    GetNextItem -->|No| AllDone{All Items Processed?}
    
    AssignWorker --> DownloadItem[Download Item]
    DownloadItem --> ItemSuccess{Success?}
    
    ItemSuccess -->|Yes| UpdateArchive[Update Archive]
    ItemSuccess -->|No| HandleItemError[Handle Error]
    
    UpdateArchive --> UpdateProgress[Update Progress]
    HandleItemError --> RetryItem{Retry Item?}
    
    RetryItem -->|Yes| RequeueItem[Requeue Item]
    RetryItem -->|No| MarkFailed[Mark as Failed]
    
    RequeueItem --> UpdateProgress
    MarkFailed --> UpdateProgress
    UpdateProgress --> ProcessBatch
    
    AllDone -->|Yes| WaitWorkers[Wait for Workers]
    AllDone -->|No| ProcessBatch
    
    WaitWorkers --> CollectResults[Collect Results]
    CollectResults --> GenerateStats[Generate Statistics]
    GenerateStats --> CheckFailed{Any Failed?}
    
    CheckFailed -->|Yes| ShowFailures[Show Failed Items]
    CheckFailed -->|No| AllSuccess[All Successful]
    
    ShowFailures --> SaveFailedList[Save Failed List]
    SaveFailedList --> Complete([Playlist Complete])
    AllSuccess --> Complete
    
    style Start fill:#4CAF50
    style Complete fill:#4CAF50
    style DownloadItem fill:#2196F3
```

---

## 8. Configuration Flow

```mermaid
flowchart TD
    Start([Application Start]) --> CheckConfig{Config Exists?}
    
    CheckConfig -->|Yes| LoadConfig[Load Configuration]
    CheckConfig -->|No| CreateDefault[Create Default Config]
    
    CreateDefault --> SetDefaults[Set Default Values]
    SetDefaults --> SaveConfig[Save Configuration]
    SaveConfig --> LoadConfig
    
    LoadConfig --> ParseJSON[Parse JSON]
    ParseJSON --> ValidConfig{Valid JSON?}
    
    ValidConfig -->|No| ConfigError[Configuration Error]
    ValidConfig -->|Yes| ValidateSettings[Validate Settings]
    
    ConfigError --> UseDefaults[Use Default Values]
    UseDefaults --> ValidateSettings
    
    ValidateSettings --> CheckSections{Check All Sections}
    
    CheckSections --> ValidateDownload[Validate Download Settings]
    ValidateDownload --> DownloadOK{Settings OK?}
    DownloadOK -->|No| FixDownload[Fix Download Settings]
    DownloadOK -->|Yes| ValidateAuth[Validate Auth Settings]
    
    FixDownload --> ValidateAuth
    ValidateAuth --> AuthOK{Settings OK?}
    AuthOK -->|No| FixAuth[Fix Auth Settings]
    AuthOK -->|Yes| ValidateProxy[Validate Proxy Settings]
    
    FixAuth --> ValidateProxy
    ValidateProxy --> ProxyOK{Settings OK?}
    ProxyOK -->|No| FixProxy[Fix Proxy Settings]
    ProxyOK -->|Yes| ValidatePaths[Validate Paths]
    
    FixProxy --> ValidatePaths
    ValidatePaths --> CheckPaths{Paths Exist?}
    CheckPaths -->|No| CreatePaths[Create Directories]
    CheckPaths -->|Yes| CheckPermissions{Permissions OK?}
    
    CreatePaths --> CheckPermissions
    CheckPermissions -->|No| FixPermissions[Fix Permissions]
    CheckPermissions -->|Yes| MergeCLI[Merge CLI Args]
    
    FixPermissions --> MergeCLI
    MergeCLI --> OverrideCLI[Override with CLI]
    OverrideCLI --> FinalValidation[Final Validation]
    
    FinalValidation --> AllValid{All Valid?}
    AllValid -->|Yes| ApplyConfig[Apply Configuration]
    AllValid -->|No| ShowWarnings[Show Warnings]
    
    ShowWarnings --> UseAvailable[Use Available Settings]
    UseAvailable --> ApplyConfig
    
    ApplyConfig --> CacheConfig[Cache in Memory]
    CacheConfig --> SetupLogger[Setup Logger]
    SetupLogger --> SetupProxy[Setup Proxy]
    SetupProxy --> InitHandlers[Initialize Handlers]
    InitHandlers --> Complete([Config Complete])
    
    style Start fill:#4CAF50
    style Complete fill:#4CAF50
    style ConfigError fill:#FF9800
```

---

## System Overview Diagram

```mermaid
graph TB
    subgraph "User Interface"
        CLI[Command Line Interface]
        Interactive[Interactive Mode]
        Search[Search Interface]
    end
    
    subgraph "Core Engine"
        Parser[URL Parser]
        Validator[Input Validator]
        Queue[Download Queue]
        Manager[Download Manager]
    end
    
    subgraph "Platform Handlers"
        YouTube[YouTube Handler]
        Spotify[Spotify Handler]
        Instagram[Instagram Handler]
        Generic[Generic Handler]
        Social[Social Media Handler]
    end
    
    subgraph "Download Engine"
        YTDLP[yt-dlp Engine]
        Requests[Requests Library]
        Browser[Browser Automation]
        Stream[Stream Handler]
    end
    
    subgraph "Post-Processing"
        FFmpeg[FFmpeg Processor]
        Metadata[Metadata Editor]
        Converter[Format Converter]
        Organizer[File Organizer]
    end
    
    subgraph "Storage"
        FileSystem[File System]
        Database[Metadata DB]
        Cache[Download Cache]
    end
    
    CLI --> Parser
    Interactive --> Parser
    Search --> Parser
    
    Parser --> Validator
    Validator --> Queue
    Queue --> Manager
    
    Manager --> YouTube
    Manager --> Spotify
    Manager --> Instagram
    Manager --> Generic
    Manager --> Social
    
    YouTube --> YTDLP
    Spotify --> Requests
    Instagram --> Browser
    Generic --> Stream
    Social --> Browser
    
    YTDLP --> FFmpeg
    Requests --> FFmpeg
    Browser --> FFmpeg
    Stream --> FFmpeg
    
    FFmpeg --> Metadata
    Metadata --> Converter
    Converter --> Organizer
    
    Organizer --> FileSystem
    Organizer --> Database
    Organizer --> Cache
    
    style CLI fill:#4CAF50
    style Manager fill:#2196F3
    style FFmpeg fill:#FF9800
    style FileSystem fill:#9C27B0
```

---

## Data Flow Diagram

```mermaid
flowchart LR
    User([User]) -->|Input URL| App[Application]
    App -->|Parse| URLParser[URL Parser]
    URLParser -->|Extract Info| Platform[Platform API]
    Platform -->|Metadata| Cache[(Cache)]
    Platform -->|Stream URL| Downloader[Downloader]
    Downloader -->|Raw File| Processor[Post-Processor]
    Processor -->|Processed File| Storage[(Storage)]
    Storage -->|Confirmation| User
    
    Cache -.->|Cached Data| Downloader
    Config[(Configuration)] -.->|Settings| App
    
    style User fill:#4CAF50
    style Storage fill:#2196F3
    style Cache fill:#FF9800
```

---

**Last Updated**: October 2, 2025  
**Version**: 2.0.0  
**Author**: Nitish Kumar
