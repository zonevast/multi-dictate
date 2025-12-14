# 🧠 Multi-Dictate RAG System Flow

This diagram illustrates exactly how your voice, clipboard, and the AI's "Brain" (Vector DB) interact to produce intelligent results and learn over time.

```mermaid
sequenceDiagram
    autonumber
    
    box "Input Layer" #e1f5fe
        participant User
        participant Clipboard as Clipboard/Files
    end
    
    box "Processing Core" #fff3e0
        participant DictateApp as Main App
        participant RAG as RAG Processor
    end
    
    box "Memory Systems" #f3e5f5
        participant Context as Context Collector
        participant Chroma as Vector DB (Brain)
    end
    
    box "Intelligence" #e8f5e9
        participant Optimizer as Prompt Optimizer
        participant AI as Smart AI Router
    end

    Note over User, AI: 1. INPUT PHASE
    User->>DictateApp: Voice Command ("Fix this database error")
    DictateApp->>Clipboard: Read Content (e.g. "/app/db.py")
    DictateApp->>Context: Collect Environment (Window, Time)

    Note over User, AI: 2. RETRIEVAL PHASE (The "Thinking")
    DictateApp->>RAG: Enhance(Raw Text, Clipboard)
    
    rect rgb(240, 248, 255)
        RAG->>Context: Read File Content from "/app/db.py"
        Context-->>RAG: Return Source Code
        
        RAG->>Chroma: Query: "Fix database error"
        Chroma-->>RAG: Found: "Similar pattern from 2 weeks ago (Success: 95%)"
    end
    
    Note over User, AI: 3. AUGMENTATION PHASE
    RAG->>RAG: Fuse Data: [Voice] + [File Code] + [Past Experience]
    RAG-->>DictateApp: Return Enhanced Prompt Context

    Note over User, AI: 4. EXECUTION PHASE
    DictateApp->>Optimizer: Structure this request
    Optimizer-->>DictateApp: Structured Prompt ("Act as DB Expert...")
    
    DictateApp->>AI: Process Final Prompt
    AI-->>DictateApp: Optimized Solution Code

    Note over User, AI: 5. OUTPUT & LEARNING
    DictateApp->>User: Type/Paste Solution
    
    rect rgb(255, 240, 245)
        Note right of DictateApp: ACTIVE LEARNING LOOP
        DictateApp->>Chroma: Store Tuple: (Original Query + New Solution)
        Chroma->>Chroma: Update Weights (Success Rate ++)
    end
```

## 🔍 How to Read This Diagram

1.  **Input Layer**: Where you start. You provide the intent (voice) and the subject (clipboard file path).
2.  **Retrieval Phase (The "Magic")**: Before doing anything, the system checks its "Brain" (ChromaDB). It asks: *"Have I seen this problem before?"* and *"Let me read the file you mentioned."*
3.  **Augmentation**: It combines your simple command with the massive context it just found.
4.  **Learning Loop (Pink Area)**: This is crucial. Once the AI gives a solution, the system **automatically saves it**. Next time, it remembers this solution, making it smarter every single time you use it.
