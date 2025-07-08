%% graph TB
%%     subgraph "Client Side"
%%         WE[Web Extension for<br/>Interaction Capture<br/>• Real-time recording<br/>• DOM context capture<br/>• Metadata collection]
%%         BR[Browser<br/>Chrome/Firefox]
%%         WA[Web Application<br/>Under Test]
        
%%         BR --> WE
%%         WE --> WA
%%     end
    
%%     subgraph "Backend Server - Flask API Layer"
%%         API[Flask Backend API<br/>• Coordinates subsystems<br/>• Handles requests<br/>• Manages workflows]
        
%%         subgraph "Code Generation"
%%             LLM[LLM-Based Code Generation Engine<br/>• Dynamic prompt library<br/>• Language/framework selection<br/>• Post-generation validation]
%%             XPATH[XPath Suggestion and<br/>Ranking Endpoint<br/>• LLM-powered analysis<br/>• Historical success patterns<br/>• Confidence scoring]
%%         end
        
%%         subgraph "Self-Healing Engine"
%%             NEURAL[Neural Element Matching<br/>• Weighted attribute embeddings<br/>• Similarity scoring<br/>• Top-1 match identification]
%%             DOM[DOM Comparison<br/>• Baseline vs current<br/>• Change detection<br/>• Element mapping]
%%         end
        
%%         subgraph "Test Execution"
%%             CDP[Chrome DevTools Protocol Driver<br/>• Drop-in replacement<br/>• Legacy integration<br/>• Event capture]
%%             EXEC[Test Execution Engine<br/>• Screenshot capture<br/>• Log collection<br/>• Failure detection]
%%         end
        
%%         API --> LLM
%%         API --> XPATH
%%         API --> NEURAL
%%         API --> DOM
%%         API --> CDP
%%         API --> EXEC
%%     end
    
%%     subgraph "External Storage & Integration"
%%         CLOUD[Cloud Object Storage<br/>• Screenshot management<br/>• Visual artifacts<br/>• Metadata linking]
        
%%         subgraph "Version Control"
%%             GIT[Git Repository<br/>• Code patches<br/>• Branch management<br/>• Pull requests]
%%             PR[Pull Request System<br/>• Code review<br/>• Approval workflow<br/>• Merge management]
%%         end
        
%%         subgraph "External Configurations"
%%             PROP[Property Files<br/>• External locators<br/>• Configuration data<br/>• Framework settings]
%%             LEGACY[Legacy Test Suites<br/>• Existing automation<br/>• Retrofit integration<br/>• Minimal modifications]
%%         end
%%     end
    
%%     subgraph "User Interface & Database"
%%         UI[Custom User Interface<br/>• Code generation UI<br/>• Healing visualization<br/>• XPath suggestion tools<br/>• Visual diff inspection]
        
%%         DB[Backend Database<br/>• DOM snapshots<br/>• User preferences<br/>• Test history<br/>• Prompt statistics<br/>• Healing metadata]
        
%%         UI --> DB
%%     end
    
%%     subgraph "Data Flow"
%%         JSON[Interaction Logs<br/>JSON Format]
%%         SNAP[DOM Snapshots<br/>Baseline & Current]
%%         CODE[Generated Test Code<br/>Multiple Languages]
%%         PATCH[Code Patches<br/>Selective updates]
%%     end
    
%%     %% Client to Backend Flow
%%     WE -->|Upload Logs| API
%%     WE -->|Interaction Data| JSON
    
%%     %% Code Generation Flow
%%     JSON --> LLM
%%     LLM --> CODE
%%     XPATH --> CODE
    
%%     %% Self-Healing Flow
%%     CDP -->|DOM Data| SNAP
%%     SNAP --> DOM
%%     DOM --> NEURAL
%%     NEURAL --> PATCH
    
%%     %% Storage Connections
%%     EXEC --> CLOUD
%%     API --> CLOUD
%%     PATCH --> GIT
%%     GIT --> PR
    
%%     %% External Integration
%%     NEURAL --> PROP
%%     CDP --> LEGACY
    
%%     %% UI Connections
%%     API --> UI
%%     CODE --> UI
%%     PATCH --> UI
%%     CLOUD --> UI
    
%%     %% Database Connections
%%     SNAP --> DB
%%     CODE --> DB
%%     PATCH --> DB

graph TD
    A[User Interacts with Web App] --> B[Web Extension Captures Actions]
    B --> C[Upload to Backend API]
    
    C --> D{Request Type}
    D -->|Generate Code| E[LLM Code Generation]
    D -->|Execute Tests| F[CDP Test Driver]
    D -->|Get XPath| G[XPath Ranking Engine]
    
    E --> H[Generated Test Code]
    F --> I{Test Result}
    G --> J[Ranked XPath List]
    
    I -->|Success| K[Store DOM Baseline]
    I -->|Failure| L[Self-Healing Engine]
    
    L --> M[Neural Element Matching]
    M --> N{Match Found?}
    N -->|Yes| O[Generate Code Patch]
    N -->|No| P[Remove Element References]
    
    O --> Q[Create Pull Request]
    P --> Q
    Q --> R[Visual Review Interface]
    R --> S[User Reviews & Merges]
    
    H --> T[User Interface]
    J --> T
    K --> T
    S --> T