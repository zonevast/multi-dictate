# Multi-Dictate Keyboard Control Flow & Process Stages

> 🎹 **Complete Step-by-Step Keyboard Functionality and Processing Pipeline**

---

## 📋 Table of Contents

1. [Keyboard Control Overview](#-keyboard-control-overview)
2. [Default Key Bindings](#-default-key-bindings)
3. [Super+F9 - Main Dictation Toggle](#-superf9---main-dictation-toggle)
4. [Super+F10 - Quick Commands](#-superf10---quick-commands)
5. [Super+F11 - Settings & Configuration](#-superf11---settings--configuration)
6. [Super+F12 - Advanced Features](#-superf12---advanced-features)
7. [Ctrl+Shift+S - System Status](#-ctrlshifts---system-status)
8. [Custom Key Bindings](#-custom-key-bindings)
9. [Step-by-Step Processing Flow](#-step-by-step-processing-flow)
10. [Integration with Other Applications](#-integration-with-other-applications)

---

## ⌨️ Keyboard Control Overview

### System Architecture for Keyboard Input Processing

```mermaid
flowchart TD
    subgraph "🎹 KEYBOARD INPUT LAYER"
        KB1[Physical Key Press<br/>Hardware Detection<br/>Scan Code Generation]
        KB2[System Event<br/>X11/Wayland Event<br/>Key Code Mapping]
        KB3[GNOME Integration<br/>gsettings/dconf<br/>Custom Keybindings]
    end

    subgraph "🔍 INPUT PROCESSING"
        PROC1[Key Capture<br/>pyautogui Detection<br/>Event Filtering]
        PROC2[Key Identification<br/>Binding Lookup<br/>Context Analysis]
        PROC3[Permission Check<br/>Security Validation<br/>Access Control]
    end

    subgraph "⚙️ COMMAND ROUTING"
        ROUTE1[Command Parser<br/>Syntax Validation<br/>Parameter Extraction]
        ROUTE2[Action Dispatcher<br/>Service Selection<br/>Priority Assignment]
        ROUTE3[Queue Manager<br/>Task Scheduling<br/>Load Balancing]
    end

    subgraph "🚀 EXECUTION LAYER"
        EXEC1[Service Manager<br/>Process Control<br/>Resource Allocation]
        EXEC2[Task Executor<br/>Function Call<br/>State Management]
        EXEC3[Result Handler<br/>Response Generation<br/>Status Update]
    end

    subgraph "📤 FEEDBACK SYSTEM"
        FEED1[Visual Feedback<br/>Status Indicator<br/>Progress Display]
        FEED2[Audio Feedback<br/>Confirmation Sounds<br/>Voice Prompts]
        FEED3[System Logging<br/>Event Recording<br/>Debug Information]
    end

    %% Processing Flow
    KB1 --> KB2 --> KB3
    KB3 --> PROC1 --> PROC2 --> PROC3
    PROC3 --> ROUTE1 --> ROUTE2 --> ROUTE3
    ROUTE3 --> EXEC1 --> EXEC2 --> EXEC3
    EXEC3 --> FEED1 --> FEED2 --> FEED3

    %% Feedback Loop
    FEED3 -.-> KB1

    %% Styling
    classDef inputLayer fill:#e3f2fd,stroke:#1976d2
    classDef processLayer fill:#f3e5f5,stroke:#7b1fa2
    classDef routeLayer fill:#e8f5e8,stroke:#388e3c
    classDef execLayer fill:#fff3e0,stroke:#f57c00
    classDef feedbackLayer fill:#fce4ec,stroke:#c2185b

    class KB1,KB2,KB3 inputLayer
    class PROC1,PROC2,PROC3 processLayer
    class ROUTE1,ROUTE2,ROUTE3 routeLayer
    class EXEC1,EXEC2,EXEC3 execLayer
    class FEED1,FEED2,FEED3 feedbackLayer
```

**📝 Description:** The keyboard control system processes physical key presses through multiple layers: hardware detection, system integration, input processing, command routing, execution, and feedback. Each layer ensures reliable key capture and appropriate system response.

---

## 🎯 Default Key Bindings

### Primary Keyboard Shortcuts Configuration

```mermaid
graph LR
    subgraph "🔧 CORE BINDINGS"
        CORE1[Super+F9<br/>🎤 Main Dictation<br/>Start/Stop Recording]
        CORE2[Super+F10<br/>⚡ Quick Commands<br/>Instant Actions]
        CORE3[Super+F11<br/>⚙️ Settings Panel<br/>Configuration Access]
        CORE4[Super+F12<br/>🚀 Advanced Menu<br/>Expert Features]
    end

    subgraph "🔍 SYSTEM BINDINGS"
        SYS1[Ctrl+Shift+S<br/>📊 System Status<br/>Health Check Display]
        SYS2[Ctrl+Shift+D<br/>🔍 Debug Mode<br/>Developer Options]
        SYS3[Ctrl+Shift+R<br/>🔄 Restart Service<br/>Service Reset]
        SYS4[Ctrl+Shift+Q<br/>🚪 Quick Exit<br/>Emergency Shutdown]
    end

    subgraph "🎙️ DICTATION BINDINGS"
        DICT1[Ctrl+Space<br/>⏯️ Pause/Resume<br/>Recording Control]
        DICT2[Ctrl+Enter<br/>✅ Complete<br/>Finalize Input]
        DICT3[Ctrl+Backspace<br/>↩️ Undo Last<br/>Correction Mode]
        DICT4[Ctrl+Shift+C<br/>📋 Copy Result<br/>Clipboard Action]
    end

    subgraph "🎨 CUSTOM BINDINGS"
        CUSTOM1[Super+1...9<br/>🔢 Custom Macros<br/>User-Defined Actions]
        CUSTOM2[Alt+Function Keys<br/>🎭 Context Switching<br/>App-Specific Modes]
        CUSTOM3[Shift+Function Keys<br/>📝 Alternative Actions<br/>Secondary Functions]
        CUSTOM4[Ctrl+Alt+Keys<br/>🔒 Security Actions<br/>Admin Functions]
    end

    %% Styling
    classDef coreBindings fill:#ff6b35,stroke:#d84315,color:#ffffff
    classDef sysBindings fill:#42a5f5,stroke:#1565c0,color:#ffffff
    classDef dictBindings fill:#66bb6a,stroke:#2e7d32,color:#ffffff
    classDef customBindings fill:#ab47bc,stroke:#6a1b9a,color:#ffffff

    class CORE1,CORE2,CORE3,CORE4 coreBindings
    class SYS1,SYS2,SYS3,SYS4 sysBindings
    class DICT1,DICT2,DICT3,DICT4 dictBindings
    class CUSTOM1,CUSTOM2,CUSTOM3,CUSTOM4 customBindings
```

---

## 🎤 Super+F9 - Main Dictation Toggle

### Step-by-Step Processing Flow

```mermaid
sequenceDiagram
    participant User as 👤 User
    participant Keyboard as ⌨️ Keyboard
    participant System as 🔧 System
    participant Audio as 🎤 Audio
    participant AI as 🤖 AI
    participant Output as 📤 Output

    Note over User, Output: Super+F9 Pressed (First Time - START)

    User->>Keyboard: Press Super+F9
    Keyboard->>System: Key Event (Super+F9)

    System->>System: 1. Key Validation
    Note right of System: • Check key binding<br/>• Verify permissions<br/>• Validate context

    System->>System: 2. State Check
    Note right of System: • Current state: IDLE<br/>• Available resources: OK<br/>• Audio devices: Ready

    System->>Audio: 3. Initialize Audio
    Note right of Audio: • Open PulseAudio<br/>• Configure 48kHz/16-bit<br/>• Start VAD<br/>• Allocate buffers

    Audio->>System: 4. Audio Ready Confirmation
    System->>System: 5. Start Speech Recognition
    Note right of System: • Activate Google Speech API<br/>• Set language detection<br/>• Initialize context

    System->>User: 6. Visual Feedback
    Note right of User: • Show "Recording..." status<br/>• Display red indicator<br/>• Activate sound level meter

    loop Continuous Recording
        User->>Audio: Speak into microphone
        Audio->>Audio: Capture audio stream
        Audio->>AI: Process audio segments
        AI->>AI: Speech-to-text conversion
        AI->>Output: Real-time text display
        Output->>User: Show transcribed text
    end

    Note over User, Output: Super+F9 Pressed (Second Time - STOP)

    User->>Keyboard: Press Super+F9 again
    Keyboard->>System: Key Event (Super+F9)
    System->>System: 7. Stop Recording
    Note right of System: • Signal recording stop<br/>• Process final segment<br/>• Complete transcription

    System->>AI: 8. Final Processing
    Note right of AI: • Optimize final text<br/>• Apply context<br/>• Quality check

    AI->>Output: 9. Generate Final Output
    Note right of Output: • Format text<br/>• Apply corrections<br/>• Prepare for delivery

    Output->>User: 10. Deliver Result
    Note right of User: • Type final text<br/>• Copy to clipboard<br/>• Audio confirmation

    System->>System: 11. Cleanup
    Note right of System: • Close audio streams<br/>• Release resources<br/>• Update status
```

### Super+F9 Processing Stages

```mermaid
flowchart TD
    START([Super+F9 Pressed]) --> VALIDATE{Key Validation}

    VALIDATE -->|Valid Key| STATE{Current State?}
    VALIDATE -->|Invalid Key| IGNORE[Ignore Event]

    STATE -->|IDLE| START_RECORDING[Start Recording]
    STATE -->|RECORDING| STOP_RECORDING[Stop Recording]
    STATE -->|ERROR| ERROR_HANDLER[Handle Error State]

    START_RECORDING --> AUDIO_INIT[Initialize Audio System]
    AUDIO_INIT --> VAD_SETUP[Setup Voice Activity Detection]
    VAD_SETUP --> SPEECH_INIT[Initialize Speech Recognition]
    SPEECH_INIT --> VISUAL_ON[Turn ON Recording Indicator]
    VISUAL_ON --> RECORDING_LOOP[Recording Loop]

    RECORDING_LOOP --> AUDIO_CAPTURE{Audio Input?}
    AUDIO_CAPTURE -->|Speech Detected| SPEECH_PROCESS[Process Speech]
    AUDIO_CAPTURE -->|Silence Detected| CONTINUE_LOOP[Continue Monitoring]
    AUDIO_CAPTURE -->|Stop Command| STOP_RECORDING

    SPEECH_PROCESS --> REAL_TIME_DISPLAY[Display Real-time Text]
    REAL_TIME_DISPLAY --> CONTINUE_LOOP
    CONTINUE_LOOP --> AUDIO_CAPTURE

    STOP_RECORDING --> FINALIZE_AUDIO[Finalize Audio Processing]
    FINALIZE_AUDIO --> AI_PROCESS[Send to AI Pipeline]
    AI_PROCESS --> QUALITY_CHECK[Quality Validation]
    QUALITY_CHECK --> OUTPUT_GENERATE[Generate Final Output]
    OUTPUT_GENERATE --> OUTPUT_DELIVER[Deliver to User]
    OUTPUT_DELIVER --> CLEANUP[Cleanup Resources]
    CLEANUP --> VISUAL_OFF[Turn OFF Recording Indicator]
    VISUAL_OFF --> END([Process Complete])

    ERROR_HANDLER --> ERROR_LOG[Log Error]
    ERROR_LOG --> NOTIFY_USER[Notify User of Error]
    NOTIFY_USER --> END

    %% Styling
    classDef startEnd fill:#ff6b35,stroke:#d84315,color:#ffffff
    classDef process fill:#42a5f5,stroke:#1565c0,color:#ffffff
    classDef decision fill:#66bb6a,stroke:#2e7d32,color:#ffffff
    classDef error fill:#ef5350,stroke:#c62828,color:#ffffff

    class START,END startEnd
    class VALIDATE,STATE,AUDIO_INIT,VAD_SETUP,SPEECH_INIT,VISUAL_ON,RECORDING_LOOP,SPEECH_PROCESS,REAL_TIME_DISPLAY,CONTINUE_LOOP,STOP_RECORDING,FINALIZE_AUDIO,AI_PROCESS,QUALITY_CHECK,OUTPUT_GENERATE,OUTPUT_DELIVER,CLEANUP,VISUAL_OFF process
    class AUDIO_CAPTURE decision
    class ERROR_HANDLER,ERROR_LOG,NOTIFY_USER error
    class IGNORE fill:#9e9e9e,stroke:#616161,color:#ffffff
```

---

## ⚡ Super+F10 - Quick Commands

### Quick Command Processing Flow

```mermaid
flowchart TD
    F10_START([Super+F10 Pressed]) --> COMMAND_MENU[Display Quick Command Menu]

    COMMAND_MENU --> WAIT_INPUT[Wait for User Input]
    WAIT_INPUT --> INPUT_RECEIVED{Key Input Received}

    INPUT_RECEIVED -->|Digit 1-3| QUICK_ACTION[Execute Quick Action]
    INPUT_RECEIVED -->|Digit 4-6| SETTINGS_ACTION[Execute Settings Action]
    INPUT_RECEIVED -->|Digit 7-9| ADVANCED_ACTION[Execute Advanced Action]
    INPUT_RECEIVED -->|Escape/Timeout| MENU_CANCEL[Cancel Menu]

    QUICK_ACTION --> ACTION_1{Action 1: Clear Clipboard}
    ACTION_1 -->|Execute| CLEAR_CLIPBOARD[Clear System Clipboard]
    ACTION_1 -->|Confirm| CONFIRM_1[Show Confirmation]

    QUICK_ACTION --> ACTION_2{Action 2: Repeat Last}
    ACTION_2 -->|Execute| REPEAT_LAST[Repeat Last Dictation]
    ACTION_2 -->|Confirm| CONFIRM_2[Show "Repeated" Message]

    QUICK_ACTION --> ACTION_3{Action 3: Save Session}
    ACTION_3 -->|Execute| SAVE_SESSION[Save Current Session]
    ACTION_3 -->|Confirm| CONFIRM_3[Show "Saved" Message]

    SETTINGS_ACTION --> ACTION_4{Action 4: Toggle Language}
    ACTION_4 -->|Execute| TOGGLE_LANG[Switch Recognition Language]
    ACTION_4 -->|Confirm| CONFIRM_4[Show New Language]

    SETTINGS_ACTION --> ACTION_5{Action 5: Volume Control}
    ACTION_5 -->|Execute| VOLUME_ADJUST[Adjust Audio Volume]
    ACTION_5 -->|Confirm| CONFIRM_5[Show Volume Level]

    SETTINGS_ACTION --> ACTION_6{Action 6: Speed Control}
    ACTION_6 -->|Execute| SPEED_ADJUST[Adjust Typing Speed]
    ACTION_6 -->|Confirm| CONFIRM_6[Show Speed Setting]

    ADVANCED_ACTION --> ACTION_7{Action 7: Export Session}
    ACTION_7 -->|Execute| EXPORT_SESSION[Export Session Data]
    ACTION_7 -->|Confirm| CONFIRM_7[Show Export Path]

    ADVANCED_ACTION --> ACTION_8{Action 8: Import Settings}
    ACTION_8 -->|Execute| IMPORT_SETTINGS[Import Configuration]
    ACTION_8 -->|Confirm| CONFIRM_8[Show Import Status]

    ADVANCED_ACTION --> ACTION_9{Action 9: System Reset}
    ACTION_9 -->|Execute| SYSTEM_RESET[Reset to Defaults]
    ACTION_9 -->|Confirm| CONFIRM_9[Show Reset Complete]

    %% Completion paths
    CLEAR_CLIPBOARD --> CONFIRM_1 --> MENU_CLOSE[Close Menu]
    REPEAT_LAST --> CONFIRM_2 --> MENU_CLOSE
    SAVE_SESSION --> CONFIRM_3 --> MENU_CLOSE
    TOGGLE_LANG --> CONFIRM_4 --> MENU_CLOSE
    VOLUME_ADJUST --> CONFIRM_5 --> MENU_CLOSE
    SPEED_ADJUST --> CONFIRM_6 --> MENU_CLOSE
    EXPORT_SESSION --> CONFIRM_7 --> MENU_CLOSE
    IMPORT_SETTINGS --> CONFIRM_8 --> MENU_CLOSE
    SYSTEM_RESET --> CONFIRM_9 --> MENU_CLOSE
    MENU_CANCEL --> MENU_CLOSE

    MENU_CLOSE --> END([Process Complete])

    %% Styling
    classDef startEnd fill:#ff6b35,stroke:#d84315,color:#ffffff
    classDef menu fill:#42a5f5,stroke:#1565c0,color:#ffffff
    classDef quick fill:#66bb6a,stroke:#2e7d32,color:#ffffff
    classDef settings fill:#ffa726,stroke:#ef6c00,color:#ffffff
    classDef advanced fill:#ab47bc,stroke:#6a1b9a,color:#ffffff
    classDef confirm fill:#4caf50,stroke:#2e7d32,color:#ffffff

    class F10_START,END startEnd
    class COMMAND_MENU,WAIT_INPUT,INPUT_RECEIVED,MENU_CANCEL,MENU_CLOSE menu
    class QUICK_ACTION,ACTION_1,ACTION_2,ACTION_3,CLEAR_CLIPBOARD,REPEAT_LAST,SAVE_SESSION quick
    class SETTINGS_ACTION,ACTION_4,ACTION_5,ACTION_6,TOGGLE_LANG,VOLUME_ADJUST,SPEED_ADJUST settings
    class ADVANCED_ACTION,ACTION_7,ACTION_8,ACTION_9,EXPORT_SESSION,IMPORT_SETTINGS,SYSTEM_RESET advanced
    class CONFIRM_1,CONFIRM_2,CONFIRM_3,CONFIRM_4,CONFIRM_5,CONFIRM_6,CONFIRM_7,CONFIRM_8,CONFIRM_9 confirm
```

### Quick Command Menu Interface

```mermaid
graph TB
    subgraph "🎯 QUICK COMMAND MENU INTERFACE"
        MENU[Super+F10 Menu<br/>Appears on Screen]

        subgraph "📝 QUICK ACTIONS (Keys 1-3)"
            QA1[1️⃣ Clear Clipboard<br/>🗑️ Clear system clipboard<br/>🔒 Privacy protection]
            QA2[2️⃣ Repeat Last<br/>🔄 Repeat last dictation<br/>📝 Quick correction]
            QA3[3️⃣ Save Session<br/>💾 Save current session<br/>📂 Auto-backup]
        end

        subgraph "⚙️ SETTINGS ACTIONS (Keys 4-6)"
            SA1[4️⃣ Toggle Language<br/>🌍 Switch recognition lang<br/>🎯 Auto-detect available]
            SA2[5️⃣ Volume Control<br/>🔊 Adjust audio volume<br/>📊 Real-time feedback]
            SA3[6️⃣ Speed Control<br/>⚡ Adjust typing speed<br/>🎯 WPM adjustment]
        end

        subgraph "🚀 ADVANCED ACTIONS (Keys 7-9)"
            AA1[7️⃣ Export Session<br/>📤 Export session data<br/>📋 Format options]
            AA2[8️⃣ Import Settings<br/>📥 Import configuration<br/>🔐 Validation check]
            AA3[9️⃣ System Reset<br/>🔄 Reset to defaults<br/>⚠️ Confirmation required]
        end
    end

    MENU --> QA1
    MENU --> QA2
    MENU --> QA3
    MENU --> SA1
    MENU --> SA2
    MENU --> SA3
    MENU --> AA1
    MENU --> AA2
    MENU --> AA3

    %% Styling
    classDef menu fill:#ff6b35,stroke:#d84315,color:#ffffff
    classDef quick fill:#66bb6a,stroke:#2e7d32,color:#ffffff
    classDef settings fill:#ffa726,stroke:#ef6c00,color:#ffffff
    classDef advanced fill:#ab47bc,stroke:#6a1b9a,color:#ffffff

    class MENU menu
    class QA1,QA2,QA3 quick
    class SA1,SA2,SA3 settings
    class AA1,AA2,AA3 advanced
```

---

## ⚙️ Super+F11 - Settings & Configuration

### Settings Panel Processing Flow

```mermaid
flowchart TD
    F11_START([Super+F11 Pressed]) --> LAUNCH_SETTINGS[Launch Settings Panel]

    LAUNCH_SETTINGS --> LOAD_CONFIG[Load Current Configuration]
    LOAD_CONFIG --> DISPLAY_SETTINGS[Display Settings Interface]

    DISPLAY_SETTINGS --> WAIT_SETTING_INPUT[Wait for Setting Selection]
    WAIT_SETTING_INPUT --> SETTING_SELECTED{Setting Category Selected}

    SETTING_SELECTED -->|Audio| AUDIO_SETTINGS[Audio Settings]
    SETTING_SELECTED -->|AI Models| AI_SETTINGS[AI Model Settings]
    SETTING_SELECTED -->|Keyboard| KBD_SETTINGS[Keyboard Settings]
    SETTING_SELECTED -->|Output| OUTPUT_SETTINGS[Output Settings]
    SETTING_SELECTED -->|Advanced| ADV_SETTINGS[Advanced Settings]

    AUDIO_SETTINGS --> AUDIO_CONFIG{Audio Configuration}
    AUDIO_CONFIG -->|Input Device| INPUT_DEVICE[Select Microphone]
    AUDIO_CONFIG -->|Sample Rate| SAMPLE_RATE[Set Sample Rate]
    AUDIO_CONFIG -->|Channels| CHANNELS[Configure Channels]
    AUDIO_CONFIG -->|VAD Sensitivity| VAD_SENS[Adjust VAD]

    AI_SETTINGS --> AI_CONFIG{AI Configuration}
    AI_CONFIG -->|Primary Model| PRIMARY_MODEL[Select Primary AI]
    AI_CONFIG -->|Fallback Model| FALLBACK_MODEL[Set Fallback AI]
    AI_CONFIG -->|Quality Threshold| QUALITY_THR[Set Quality Score]
    AI_CONFIG -->|Context Window| CONTEXT_WIN[Configure Context]

    KBD_SETTINGS --> KBD_CONFIG{Keyboard Configuration}
    KBD_CONFIG -->|Layout Detection| LAYOUT_DETECT[Toggle Layout Detect]
    KBD_CONFIG -->|Key Repeat| KEY_REPEAT[Configure Key Repeat]
    KBD_CONFIG -->|Custom Bindings| CUSTOM_BIND[Manage Custom Keys]
    KBD_CONFIG -->|Typing Speed| TYPE_SPEED[Set Typing Speed]

    OUTPUT_SETTINGS --> OUTPUT_CONFIG{Output Configuration}
    OUTPUT_CONFIG -->|Typing Mode| TYPE_MODE[Select Typing Mode]
    OUTPUT_CONFIG -->|Voice Feedback| VOICE_FB[Configure Voice Feedback]
    OUTPUT_CONFIG -->|Visual Indicators| VISUAL_IND[Setup Indicators]
    OUTPUT_CONFIG -->|Clipboard| CLIPBOARD[Configure Clipboard]

    ADV_SETTINGS --> ADV_CONFIG{Advanced Configuration}
    ADV_CONFIG -->|Performance| PERF_OPT[Performance Options]
    ADV_CONFIG -->|Logging| LOG_CONFIG[Logging Configuration]
    ADV_CONFIG -->|Debug| DEBUG_MODE[Debug Settings]
    ADV_CONFIG -->|Security| SECURITY_OPT[Security Options]

    %% Individual setting processing
    INPUT_DEVICE --> VALIDATE_INPUT[Validate Input Device]
    SAMPLE_RATE --> VALIDATE_RATE[Validate Sample Rate]
    CHANNELS --> VALIDATE_CHANNELS[Validate Channels]
    VAD_SENS --> VALIDATE_VAD[Validate VAD Setting]

    PRIMARY_MODEL --> VALIDATE_MODEL[Validate AI Model]
    FALLBACK_MODEL --> VALIDATE_FALLBACK[Validate Fallback]
    QUALITY_THR --> VALIDATE_QUALITY[Validate Quality]
    CONTEXT_WIN --> VALIDATE_CONTEXT[Validate Context]

    LAYOUT_DETECT --> VALIDATE_LAYOUT[Validate Layout]
    KEY_REPEAT --> VALIDATE_REPEAT[Validate Repeat]
    CUSTOM_BIND --> VALIDATE_CUSTOM[Validate Custom]
    TYPE_SPEED --> VALIDATE_TYPE[Validate Speed]

    TYPE_MODE --> VALIDATE_TYPEMODE[Validate Mode]
    VOICE_FB --> VALIDATE_VOICE[Validate Voice]
    VISUAL_IND --> VALIDATE_VISUAL[Validate Visual]
    CLIPBOARD --> VALIDATE_CLIP[Validate Clipboard]

    PERF_OPT --> VALIDATE_PERF[Validate Performance]
    LOG_CONFIG --> VALIDATE_LOG[Validate Logging]
    DEBUG_MODE --> VALIDATE_DEBUG[Validate Debug]
    SECURITY_OPT --> VALIDATE_SEC[Validate Security]

    %% Validation results
    VALIDATE_INPUT --> APPLY_AUDIO[Apply Audio Setting]
    VALIDATE_RATE --> APPLY_AUDIO
    VALIDATE_CHANNELS --> APPLY_AUDIO
    VALIDATE_VAD --> APPLY_AUDIO

    VALIDATE_MODEL --> APPLY_AI[Apply AI Setting]
    VALIDATE_FALLBACK --> APPLY_AI
    VALIDATE_QUALITY --> APPLY_AI
    VALIDATE_CONTEXT --> APPLY_AI

    VALIDATE_LAYOUT --> APPLY_KBD[Apply Keyboard Setting]
    VALIDATE_REPEAT --> APPLY_KBD
    VALIDATE_CUSTOM --> APPLY_KBD
    VALIDATE_TYPE --> APPLY_KBD

    VALIDATE_TYPEMODE --> APPLY_OUTPUT[Apply Output Setting]
    VALIDATE_VOICE --> APPLY_OUTPUT
    VALIDATE_VISUAL --> APPLY_OUTPUT
    VALIDATE_CLIP --> APPLY_OUTPUT

    VALIDATE_PERF --> APPLY_ADV[Apply Advanced Setting]
    VALIDATE_LOG --> APPLY_ADV
    VALIDATE_DEBUG --> APPLY_ADV
    VALIDATE_SEC --> APPLY_ADV

    %% Apply and save
    APPLY_AUDIO --> SAVE_CONFIG[Save Configuration]
    APPLY_AI --> SAVE_CONFIG
    APPLY_KBD --> SAVE_CONFIG
    APPLY_OUTPUT --> SAVE_CONFIG
    APPLY_ADV --> SAVE_CONFIG

    SAVE_CONFIG --> RESTART_SERVICES[Restart Affected Services]
    RESTART_SERVICES --> CONFIRM_SETTINGS[Show Confirmation]
    CONFIRM_SETTINGS --> CLOSE_SETTINGS[Close Settings Panel]
    CLOSE_SETTINGS --> END([Settings Complete])

    %% Error handling
    VALIDATE_INPUT -->|Error| SHOW_AUDIO_ERROR[Show Audio Error]
    VALIDATE_MODEL -->|Error| SHOW_AI_ERROR[Show AI Error]
    VALIDATE_LAYOUT -->|Error| SHOW_KBD_ERROR[Show Keyboard Error]
    VALIDATE_TYPEMODE -->|Error| SHOW_OUTPUT_ERROR[Show Output Error]
    VALIDATE_PERF -->|Error| SHOW_ADV_ERROR[Show Advanced Error]

    SHOW_AUDIO_ERROR --> WAIT_SETTING_INPUT
    SHOW_AI_ERROR --> WAIT_SETTING_INPUT
    SHOW_KBD_ERROR --> WAIT_SETTING_INPUT
    SHOW_OUTPUT_ERROR --> WAIT_SETTING_INPUT
    SHOW_ADV_ERROR --> WAIT_SETTING_INPUT

    %% Styling
    classDef startEnd fill:#ff6b35,stroke:#d84315,color:#ffffff
    classDef settings fill:#42a5f5,stroke:#1565c0,color:#ffffff
    classDef category fill:#66bb6a,stroke:#2e7d32,color:#ffffff
    classDef validate fill:#ffa726,stroke:#ef6c00,color:#ffffff
    classDef apply fill:#ab47bc,stroke:#6a1b9a,color:#ffffff
    classDef error fill:#ef5350,stroke:#c62828,color:#ffffff

    class F11_START,END startEnd
    class LAUNCH_SETTINGS,LOAD_CONFIG,DISPLAY_SETTINGS,WAIT_SETTING_INPUT,SETTING_SELECTED,SAVE_CONFIG,RESTART_SERVICES,CONFIRM_SETTINGS,CLOSE_SETTINGS settings
    class AUDIO_SETTINGS,AI_SETTINGS,KBD_SETTINGS,OUTPUT_SETTINGS,ADV_SETTINGS,AUDIO_CONFIG,AI_CONFIG,KBD_CONFIG,OUTPUT_CONFIG,ADV_CONFIG category
    class VALIDATE_INPUT,VALIDATE_RATE,VALIDATE_CHANNELS,VALIDATE_VAD,VALIDATE_MODEL,VALIDATE_FALLBACK,VALIDATE_QUALITY,VALIDATE_CONTEXT,VALIDATE_LAYOUT,VALIDATE_REPEAT,VALIDATE_CUSTOM,VALIDATE_TYPE,VALIDATE_TYPEMODE,VALIDATE_VOICE,VALIDATE_VISUAL,VALIDATE_CLIP,VALIDATE_PERF,VALIDATE_LOG,VALIDATE_DEBUG,VALIDATE_SEC validate
    class APPLY_AUDIO,APPLY_AI,APPLY_KBD,APPLY_OUTPUT,APPLY_ADV apply
    class SHOW_AUDIO_ERROR,SHOW_AI_ERROR,SHOW_KBD_ERROR,SHOW_OUTPUT_ERROR,SHOW_ADV_ERROR error
```

---

## 🚀 Super+F12 - Advanced Features

### Advanced Features Menu Processing

```mermaid
flowchart TD
    F12_START([Super+F12 Pressed]) --> AUTH_CHECK[Authentication Check]

    AUTH_CHECK --> AUTH_SUCCESS{Authenticated?}
    AUTH_SUCCESS -->|Yes| SHOW_ADVANCED[Display Advanced Menu]
    AUTH_SUCCESS -->|No| SHOW_AUTH_ERROR[Authentication Error]

    SHOW_AUTH_ERROR --> END_AUTH([Authentication Failed])

    SHOW_ADVANCED --> WAIT_ADV_INPUT[Wait for Advanced Selection]
    WAIT_ADV_INPUT --> ADV_SELECTED{Advanced Option Selected}

    ADV_SELECTED -->|Performance| PERF_MENU[Performance Menu]
    ADV_SELECTED -->|Diagnostics| DIAG_MENU[Diagnostics Menu]
    ADV_SELECTED -->|Developer| DEV_MENU[Developer Menu]
    ADV_SELECTED -->|Security| SEC_MENU[Security Menu]
    ADV_SELECTED -->|Export/Import| EXP_MENU[Export/Import Menu]

    %% Performance Menu
    PERF_MENU --> PERF_OPTIONS{Performance Options}
    PERF_OPTIONS -->|Benchmark| RUN_BENCHMARK[Run Performance Benchmark]
    PERF_OPTIONS -->|Optimize| AUTO_OPTIMIZE[Auto-Optimize System]
    PERF_OPTIONS -->|Profiling| ENABLE_PROFILING[Enable Profiling]
    PERF_OPTIONS -->|Cache Management| CACHE_MGMT[Manage Caches]

    %% Diagnostics Menu
    DIAG_MENU --> DIAG_OPTIONS{Diagnostics Options}
    DIAG_OPTIONS -->|System Check| SYSTEM_CHECK[Full System Check]
    DIAG_OPTIONS -->|Component Test| COMPONENT_TEST[Test Components]
    DIAG_OPTIONS -->|Network Test| NETWORK_TEST[Test Network]
    DIAG_OPTIONS -->|Audio Test| AUDIO_TEST[Test Audio System]

    %% Developer Menu
    DEV_MENU --> DEV_OPTIONS{Developer Options}
    DEV_OPTIONS -->|Debug Mode| TOGGLE_DEBUG[Toggle Debug Mode]
    DEV_OPTIONS -->|Log Level| SET_LOG_LEVEL[Set Log Level]
    DEV_OPTIONS -->|Test Mode| ENABLE_TEST_MODE[Enable Test Mode]
    DEV_OPTIONS -->|API Access| ENABLE_API[Enable API Access]

    %% Security Menu
    SEC_MENU --> SEC_OPTIONS{Security Options}
    SEC_OPTIONS -->|Security Audit| SECURITY_AUDIT[Run Security Audit]
    SEC_OPTIONS -->|Permission Check| CHECK_PERMISSIONS[Check Permissions]
    SEC_OPTIONS -->|Key Management| KEY_MGMT[Manage Security Keys]
    SEC_OPTIONS -->|Privacy Mode| PRIVACY_MODE[Toggle Privacy Mode]

    %% Export/Import Menu
    EXP_MENU --> EXP_OPTIONS{Export/Import Options}
    EXP_OPTIONS -->|Export Data| EXPORT_DATA[Export All Data]
    EXP_OPTIONS -->|Import Data| IMPORT_DATA[Import Data]
    EXP_OPTIONS -->|Backup Config| BACKUP_CONFIG[Backup Configuration]
    EXP_OPTIONS -->|Restore Config| RESTORE_CONFIG[Restore Configuration]

    %% Process each option
    RUN_BENCHMARK --> EXEC_BENCHMARK[Execute Benchmark Suite]
    AUTO_OPTIMIZE --> START_OPTIMIZE[Start Optimization Process]
    ENABLE_PROFILING --> ACTIVATE_PROFILING[Activate Profiling Tools]
    CACHE_MGMT --> OPEN_CACHE_MGMT[Open Cache Management]

    SYSTEM_CHECK --> RUN_SYSTEM_CHECK[Run System Diagnostics]
    COMPONENT_TEST --> TEST_COMPONENTS[Test All Components]
    NETWORK_TEST --> TEST_NETWORK[Test Network Connectivity]
    AUDIO_TEST --> TEST_AUDIO[Test Audio Subsystem]

    TOGGLE_DEBUG --> SWITCH_DEBUG[Switch Debug Mode]
    SET_LOG_LEVEL --> CHANGE_LOG_LEVEL[Change Logging Level]
    ENABLE_TEST_MODE --> ACTIVATE_TEST_MODE[Activate Test Mode]
    ENABLE_API --> START_API_SERVER[Start API Server]

    SECURITY_AUDIT --> RUN_AUDIT[Run Security Audit]
    CHECK_PERMISSIONS --> VERIFY_PERMISSIONS[Verify All Permissions]
    KEY_MGMT --> OPEN_KEY_MGMT[Open Key Management]
    PRIVACY_MODE --> TOGGLE_PRIVACY[Toggle Privacy Mode]

    EXPORT_DATA --> START_EXPORT[Start Data Export]
    IMPORT_DATA --> START_IMPORT[Start Data Import]
    BACKUP_CONFIG --> CREATE_BACKUP[Create Configuration Backup]
    RESTORE_CONFIG --> RESTORE_FROM_BACKUP[Restore from Backup]

    %% Results processing
    EXEC_BENCHMARK --> SHOW_BENCHMARK_RESULTS[Display Benchmark Results]
    START_OPTIMIZE --> SHOW_OPTIMIZE_RESULTS[Show Optimization Results]
    ACTIVATE_PROFILING --> SHOW_PROFILING_STATUS[Show Profiling Status]
    OPEN_CACHE_MGMT --> CACHE_MGMT_INTERFACE[Open Cache Management UI]

    RUN_SYSTEM_CHECK --> SHOW_HEALTH_REPORT[Display Health Report]
    TEST_COMPONENTS --> SHOW_COMPONENT_RESULTS[Show Component Test Results]
    TEST_NETWORK --> SHOW_NETWORK_STATUS[Display Network Status]
    TEST_AUDIO --> SHOW_AUDIO_RESULTS[Show Audio Test Results]

    SWITCH_DEBUG --> CONFIRM_DEBUG[Confirm Debug Mode Change]
    CHANGE_LOG_LEVEL --> CONFIRM_LOG_LEVEL[Confirm Log Level Change]
    ACTIVATE_TEST_MODE --> CONFIRM_TEST_MODE[Confirm Test Mode]
    START_API_SERVER --> SHOW_API_STATUS[Show API Server Status]

    RUN_AUDIT --> SHOW_AUDIT_REPORT[Display Audit Report]
    VERIFY_PERMISSIONS --> SHOW_PERMISSIONS[Show Permission Status]
    OPEN_KEY_MGMT --> KEY_MGMT_UI[Open Key Management UI]
    TOGGLE_PRIVACY --> CONFIRM_PRIVACY[Confirm Privacy Mode]

    START_EXPORT --> SHOW_EXPORT_PROGRESS[Show Export Progress]
    START_IMPORT --> SHOW_IMPORT_PROGRESS[Show Import Progress]
    CREATE_BACKUP --> CONFIRM_BACKUP[Confirm Backup Created]
    RESTORE_FROM_BACKUP --> CONFIRM_RESTORE[Confirm Restore Complete]

    %% Completion paths
    SHOW_BENCHMARK_RESULTS --> CLOSE_ADVANCED[Close Advanced Menu]
    SHOW_OPTIMIZE_RESULTS --> CLOSE_ADVANCED
    SHOW_PROFILING_STATUS --> CLOSE_ADVANCED
    CACHE_MGMT_INTERFACE --> WAIT_ADV_INPUT

    SHOW_HEALTH_REPORT --> CLOSE_ADVANCED
    SHOW_COMPONENT_RESULTS --> CLOSE_ADVANCED
    SHOW_NETWORK_STATUS --> CLOSE_ADVANCED
    SHOW_AUDIO_RESULTS --> CLOSE_ADVANCED

    CONFIRM_DEBUG --> CLOSE_ADVANCED
    CONFIRM_LOG_LEVEL --> CLOSE_ADVANCED
    CONFIRM_TEST_MODE --> CLOSE_ADVANCED
    SHOW_API_STATUS --> CLOSE_ADVANCED

    SHOW_AUDIT_REPORT --> CLOSE_ADVANCED
    SHOW_PERMISSIONS --> CLOSE_ADVANCED
    KEY_MGMT_UI --> WAIT_ADV_INPUT
    CONFIRM_PRIVACY --> CLOSE_ADVANCED

    SHOW_EXPORT_PROGRESS --> CLOSE_ADVANCED
    SHOW_IMPORT_PROGRESS --> CLOSE_ADVANCED
    CONFIRM_BACKUP --> CLOSE_ADVANCED
    CONFIRM_RESTORE --> CLOSE_ADVANCED

    CLOSE_ADVANCED --> END_COMPLETE([Advanced Features Complete])
    END_AUTH --> END_COMPLETE

    %% Styling
    classDef startEnd fill:#ff6b35,stroke:#d84315,color:#ffffff
    classDef auth fill:#ef5350,stroke:#c62828,color:#ffffff
    classDef menu fill:#42a5f5,stroke:#1565c0,color:#ffffff
    classDef options fill:#66bb6a,stroke:#2e7d32,color:#ffffff
    classDef execution fill:#ffa726,stroke:#ef6c00,color:#ffffff
    classDef results fill:#ab47bc,stroke:#6a1b9a,color:#ffffff

    class F12_START,END_COMPLETE,END_AUTH startEnd
    class AUTH_CHECK,AUTH_SUCCESS,SHOW_AUTH_ERROR auth
    class SHOW_ADVANCED,WAIT_ADV_INPUT,ADV_SELECTED,PERF_MENU,DIAG_MENU,DEV_MENU,SEC_MENU,EXP_MENU,CLOSE_ADVANCED menu
    class PERF_OPTIONS,DIAG_OPTIONS,DEV_OPTIONS,SEC_OPTIONS,EXP_OPTIONS options
    class executionClass fill:#ffa726,stroke:#ef6c00,color:#ffffff
    class resultsClass fill:#ab47bc,stroke:#6a1b9a,color:#ffffff

    %% Apply execution and results styles
    class RUN_BENCHMARK,AUTO_OPTIMIZE,ENABLE_PROFILING,CACHE_MGMT,SYSTEM_CHECK,COMPONENT_TEST,NETWORK_TEST,AUDIO_TEST,TOGGLE_DEBUG,SET_LOG_LEVEL,ENABLE_TEST_MODE,ENABLE_API,SECURITY_AUDIT,CHECK_PERMISSIONS,KEY_MGMT,PRIVACY_MODE,EXPORT_DATA,IMPORT_DATA,BACKUP_CONFIG,RESTORE_CONFIG executionClass
    class SHOW_BENCHMARK_RESULTS,SHOW_OPTIMIZE_RESULTS,SHOW_PROFILING_STATUS,SHOW_HEALTH_REPORT,SHOW_COMPONENT_RESULTS,SHOW_NETWORK_STATUS,SHOW_AUDIO_RESULTS,CONFIRM_DEBUG,CONFIRM_LOG_LEVEL,CONFIRM_TEST_MODE,SHOW_API_STATUS,SHOW_AUDIT_REPORT,SHOW_PERMISSIONS,CONFIRM_PRIVACY,SHOW_EXPORT_PROGRESS,SHOW_IMPORT_PROGRESS,CONFIRM_BACKUP,CONFIRM_RESTORE resultsClass
```

---

## 📊 Ctrl+Shift+S - System Status

### System Status Display Processing

```mermaid
sequenceDiagram
    participant User as 👤 User
    participant Keyboard as ⌨️ Keyboard
    participant System as 🔧 System Manager
    participant Monitor as 📊 Status Monitor
    participant Display as 🖥️ Display Manager

    Note over User, Display: Ctrl+Shift+S Pressed

    User->>Keyboard: Press Ctrl+Shift+S
    Keyboard->>System: Key Event (Ctrl+Shift+S)

    System->>System: 1. Validate Key Binding
    Note right of System: • Check key combination<br/>• Verify permissions<br/>• Confirm context

    System->>Monitor: 2. Request System Status
    Note right of Monitor: • Collect metrics<br/>• Check services<br/>• Validate resources

    par Parallel Status Collection
        Monitor->>Monitor: Audio Status Check
        Note right of Monitor: • Microphone: Active<br/>• Sample Rate: 48kHz<br/>• VAD: Operational
    and
        Monitor->>Monitor: AI Services Check
        Note right of Monitor: • Qwen: Available<br/>• OpenAI: Connected<br/>• Gemini: Ready
    and
        Monitor->>Monitor: System Resources Check
        Note right of Monitor: • CPU: 25%<br/>• Memory: 2GB<br/>• Disk: 15GB free
    and
        Monitor->>Monitor: Performance Metrics
        Note right of Monitor: • Response Time: 85ms<br/>• Success Rate: 98%<br/>• Quality Score: 92/100
    end

    Monitor->>System: 3. Compile Status Report
    System->>Display: 4. Request Status Display
    Display->>Display: 5. Create Status Window

    Note over Display: Status Window Created

    Display->>User: 6. Show System Status
    Note right of User: ┌─ System Status ─┐<br/>│ ✅ Overall: Healthy │<br/>│ 🎤 Audio: Active │<br/>│ 🤖 AI: Online │<br/>│ 📊 Performance: Good │<br/>│ 💾 Resources: OK │<br/>│ ⏱️ Uptime: 2h 34m │<br/>└─────────────────┘

    User->>User: 7. View Status Information

    Note over User, Display: Auto-dismiss after 10 seconds or on any key press

    User->>Keyboard: Press any key
    Keyboard->>Display: 8. Dismiss Request
    Display->>Display: 9. Close Status Window
    Display->>System: 10. Display Complete

    System->>System: 11. Log Status Check
    Note right of System: • Record status view<br/>• Update metrics<br/>• Maintain history

```

### System Status Components

```mermaid
graph TB
    subgraph "📊 SYSTEM STATUS DASHBOARD"
        STATUS[Ctrl+Shift+S Status Window]

        subgraph "🎤 AUDIO STATUS"
            AUDIO1[Microphone: ✅ Active<br/>Device: USB Audio<br/>Sample Rate: 48kHz]
            AUDIO2[Voice Detection: ✅ Working<br/>Sensitivity: Medium<br/>Response Time: 50ms]
            AUDIO3[Audio Quality: ✅ Good<br/>Signal: 85%<br/>Noise: Low]
        end

        subgraph "🤖 AI SERVICES STATUS"
            AI1[Qwen Local: ✅ Available<br/>Model: qwen-turbo<br/>Load: Normal]
            AI2[OpenAI GPT: ✅ Connected<br/>API: gpt-4<br/>Credits: Sufficient]
            AI3[Gemini AI: ✅ Ready<br/>Service: gemini-pro<br/>Rate: Normal]
        end

        subgraph "💻 SYSTEM RESOURCES"
            SYS1[CPU Usage: ✅ Normal<br/>Load: 25%<br/>Cores: 8/8 Active]
            SYS2[Memory Usage: ✅ OK<br/>Used: 2GB/8GB<br/>Available: 6GB]
            SYS3[Disk Space: ✅ Good<br/>Used: 85GB/100GB<br/>Free: 15GB]
        end

        subgraph "📈 PERFORMANCE METRICS"
            PERF1[Response Time: ✅ Fast<br/>Average: 85ms<br/>Peak: 150ms]
            PERF2[Success Rate: ✅ High<br/>Today: 98%<br/>Last Hour: 99%]
            PERF3[Quality Score: ✅ Excellent<br/>Current: 92/100<br/>Average: 89/100]
        end

        subgraph "⏱️ ACTIVITY METRICS"
            ACT1[Uptime: ✅ Stable<br/>Current: 2h 34m<br/>Sessions Today: 5]
            ACT2[Today's Usage: ✅ Active<br/>Dictations: 47<br/>Words: 5,234]
            ACT3[Error Rate: ✅ Low<br/>Errors: 2<br/>Recovery: 100%]
        end
    end

    STATUS --> AUDIO1
    STATUS --> AUDIO2
    STATUS --> AUDIO3
    STATUS --> AI1
    STATUS --> AI2
    STATUS --> AI3
    STATUS --> SYS1
    STATUS --> SYS2
    STATUS --> SYS3
    STATUS --> PERF1
    STATUS --> PERF2
    STATUS --> PERF3
    STATUS --> ACT1
    STATUS --> ACT2
    STATUS --> ACT3

    %% Styling
    classDef mainStatus fill:#ff6b35,stroke:#d84315,color:#ffffff
    classDef audioStatus fill:#42a5f5,stroke:#1565c0,color:#ffffff
    classDef aiStatus fill:#66bb6a,stroke:#2e7d32,color:#ffffff
    classDef sysStatus fill:#ffa726,stroke:#ef6c00,color:#ffffff
    classDef perfStatus fill:#ab47bc,stroke:#6a1b9a,color:#ffffff
    classDef actStatus fill:#8d6e63,stroke:#5d4037,color:#ffffff

    class STATUS mainStatus
    class AUDIO1,AUDIO2,AUDIO3 audioStatus
    class AI1,AI2,AI3 aiStatus
    class SYS1,SYS2,SYS3 sysStatus
    class PERF1,PERF2,PERF3 perfStatus
    class ACT1,ACT2,ACT3 actStatus
```

---

## 🔧 Custom Key Bindings

### Custom Key Configuration Process

```mermaid
flowchart TD
    CUSTOM_START([Custom Key Setup]) --> CREATE_BINDING[Create New Binding]

    CREATE_BINDING --> KEY_SELECT[Select Key Combination]
    KEY_SELECT --> VALIDATE_KEY{Key Combination Valid?}

    VALIDATE_KEY -->|No| KEY_ERROR[Show Key Conflict Error]
    VALIDATE_KEY -->|Yes| ACTION_DEFINE[Define Action]

    KEY_ERROR --> KEY_SELECT

    ACTION_DEFINE --> ACTION_TYPE{Action Type}

    ACTION_TYPE -->|Simple Command| SIMPLE_CMD[Define Simple Command]
    ACTION_TYPE -->|Complex Script| COMPLEX_SCRIPT[Define Complex Script]
    ACTION_TYPE -->|Application Control| APP_CTRL[Define App Control]
    ACTION_TYPE -->|System Function| SYS_FUNC[Define System Function]

    SIMPLE_CMD --> CMD_PARAMS[Set Command Parameters]
    COMPLEX_SCRIPT --> SCRIPT_PARAMS[Set Script Parameters]
    APP_CTRL --> APP_PARAMS[Set App Parameters]
    SYS_FUNC --> SYS_PARAMS[Set System Parameters]

    CMD_PARAMS --> TEST_BINDING[Test Key Binding]
    SCRIPT_PARAMS --> TEST_BINDING
    APP_PARAMS --> TEST_BINDING
    SYS_PARAMS --> TEST_BINDING

    TEST_BINDING --> BINDING_WORKS{Binding Works?}

    BINDING_WORKS -->|No| DEBUG_BINDING[Debug Binding Issues]
    BINDING_WORKS -->|Yes| SAVE_BINDING[Save Binding]

    DEBUG_BINDING --> ACTION_DEFINE

    SAVE_BINDING --> ACTIVATE_BINDING[Activate Binding]
    ACTIVATE_BINDING --> CONFIG_UPDATE[Update Configuration]
    CONFIG_UPDATE --> RESTART_SERVICES[Restart Affected Services]
    RESTART_SERVICES --> CONFIRM_ACTIVE[Confirm Activation]
    CONFIRM_ACTIVE --> END_SUCCESS([Binding Active])

    subgraph "🎯 Example Custom Bindings"
        EXAMPLE1[Super+Ctrl+V<br/>📋 Paste with AI Enhancement<br/>Format and improve pasted text]
        EXAMPLE2[Alt+Shift+D<br/>🎤 Dictation Mode Toggle<br/>Quick start/stop without menu]
        EXAMPLE3[Ctrl+Alt+T<br/>🔍 Translate Last Text<br/>Translate to preferred language]
        EXAMPLE4[Super+Shift+S<br/>📊 Save Session Snapshot<br/>Quick save current state]
        EXAMPLE5[Ctrl+Shift+F<br/>🔍 Find & Replace AI<br/>AI-powered text correction]
    end

    %% Styling
    classDef startEnd fill:#ff6b35,stroke:#d84315,color:#ffffff
    classDef process fill:#42a5f5,stroke:#1565c0,color:#ffffff
    classDef action fill:#66bb6a,stroke:#2e7d32,color:#ffffff
    classDef test fill:#ffa726,stroke:#ef6c00,color:#ffffff
    classDef success fill:#4caf50,stroke:#2e7d32,color:#ffffff
    classDef error fill:#ef5350,stroke:#c62828,color:#ffffff
    classDef example fill:#ab47bc,stroke:#6a1b9a,color:#ffffff

    class CUSTOM_START,END_SUCCESS startEnd
    class CREATE_BINDING,KEY_SELECT,VALIDATE_KEY,ACTION_DEFINE,ACTION_TYPE,CMD_PARAMS,SCRIPT_PARAMS,APP_PARAMS,SYS_PARAMS,CONFIG_UPDATE,RESTART_SERVICES,CONFIRM_ACTIVE process
    class SIMPLE_CMD,COMPLEX_SCRIPT,APP_CTRL,SYS_FUNC action
    class TEST_BINDING,BINDING_WORKS test
    class SAVE_BINDING,ACTIVATE_BINDING success
    class KEY_ERROR,DEBUG_BINDING error
    class EXAMPLE1,EXAMPLE2,EXAMPLE3,EXAMPLE4,EXAMPLE5 example
```

---

## 🔄 Step-by-Step Processing Flow

### Complete Keyboard Input Processing Sequence

```mermaid
sequenceDiagram
    participant User as 👤 User
    participant HW as 🔧 Hardware
    participant OS as 💻 OS Layer
    participant App as 🎹 Multi-Dictate
    participant Router as 🚀 Router
    participant Service as ⚙️ Service
    participant Feedback as 📤 Feedback

    Note over User, Feedback: Complete Keyboard Processing Flow

    User->>HW: 1. Physical Key Press
    Note right of HW: Key matrix scan<br/>Generate scan code<br/>Hardware debouncing

    HW->>OS: 2. Scan Code to OS
    Note right of OS: Keyboard driver<br/>Scan code translation<br/>Event generation

    OS->>OS: 3. Event Processing
    Note right of OS: Key mapping<br/>Modifier detection<br/>Event queuing

    OS->>App: 4. Key Event to Application
    Note right of App: Event listener<br/>Key combination detection<br/>Permission check

    App->>App: 5. Key Validation
    Note right of App: • Verify key binding<br/>• Check active context<br/>• Validate permissions

    alt Valid Key Binding
        App->>Router: 6. Route to Handler
        Note right of Router: Command identification<br/>Handler selection<br/>Priority assignment

        Router->>Service: 7. Execute Service
        Note right of Service: • Parse parameters<br/>• Execute action<br/>• Handle errors

        Service->>Service: 8. Process Action
        Note right of Service: State management<br/>Resource allocation<br/>Side effect handling

        Service->>Feedback: 9. Generate Feedback
        Note right of Feedback: • Visual indicators<br/>• Audio confirmation<br/>• Status updates

        Feedback->>User: 10. User Feedback
        Note right of User: • Status display<br/>• Confirmation sounds<br/>• Result display

    else Invalid Key Binding
        App->>OS: 6B. Pass to OS
        Note right of OS: Default key handling<br/>System functions<br/>Other applications

        OS->>User: 7B. System Response
        Note right of User: Default behavior<br/>System functions<br/>Application switching
    end

    Note over User, Feedback: Logging and Monitoring

    App->>App: 11. Log Event
    Note right of App: • Key press logged<br/>• Action recorded<br/>• Performance metrics

    App->>App: 12. Update State
    Note right of App: • Internal state update<br/>• Configuration save<br/>• History tracking

```

### Keyboard Input Decision Tree

```mermaid
flowchart TD
    KEY_PRESSED([Key Pressed]) --> VALID_INPUT{Valid Input?}

    VALID_INPUT -->|No| IGNORE_KEY[Ignore Key]
    VALID_INPUT -->|Yes| CHECK_BINDING{Key Binding Exists?}

    CHECK_BINDING -->|No| PASS_TO_OS[Pass to OS]
    CHECK_BINDING -->|Yes| GET_BINDING[Get Binding Action]

    GET_BINDING --> ACTION_TYPE{Action Type}

    ACTION_TYPE -->|Dictation| DICTATION_ACTION[Handle Dictation]
    ACTION_TYPE -->|Quick Command| QUICK_ACTION[Handle Quick Command]
    ACTION_TYPE -->|Settings| SETTINGS_ACTION[Handle Settings]
    ACTION_TYPE -->|Advanced| ADVANCED_ACTION[Handle Advanced]
    ACTION_TYPE -->|Status| STATUS_ACTION[Handle Status]
    ACTION_TYPE -->|Custom| CUSTOM_ACTION[Handle Custom Action]

    DICTATION_ACTION --> DICTATION_STATE{Current Dictation State?}
    DICTATION_STATE -->|Idle| START_DICTATION[Start Recording]
    DICTATION_STATE -->|Recording| STOP_DICTATION[Stop Recording]
    DICTATION_STATE -->|Paused| RESUME_DICTATION[Resume Recording]
    DICTATION_STATE -->|Error| ERROR_DICTATION[Handle Error]

    QUICK_ACTION --> QUICK_TYPE{Quick Command Type?}
    QUICK_TYPE -->|Clear| CLEAR_CLIPBOARD[Clear Clipboard]
    QUICK_TYPE -->|Repeat| REPEAT_LAST[Repeat Last]
    QUICK_TYPE -->|Save| SAVE_SESSION[Save Session]
    QUICK_TYPE -->|Export| EXPORT_DATA[Export Data]

    SETTINGS_ACTION --> SETTINGS_TYPE{Settings Type?}
    SETTINGS_TYPE -->|Audio| AUDIO_SETTINGS[Audio Settings]
    SETTINGS_TYPE -->|AI| AI_SETTINGS[AI Settings]
    SETTINGS_TYPE -->|Keyboard| KBD_SETTINGS[Keyboard Settings]
    SETTINGS_TYPE -->|Output| OUTPUT_SETTINGS[Output Settings]

    ADVANCED_ACTION --> AUTH_REQUIRED{Authentication Required?}
    AUTH_REQUIRED -->|No| ADVANCED_MENU[Show Advanced Menu]
    AUTH_REQUIRED -->|Yes| AUTH_USER[Authenticate User]
    AUTH_USER --> AUTH_SUCCESS{Authentication Success?}
    AUTH_SUCCESS -->|Yes| ADVANCED_MENU
    AUTH_SUCCESS -->|No| AUTH_FAILED[Authentication Failed]

    STATUS_ACTION --> SHOW_STATUS[Display System Status]

    CUSTOM_ACTION --> EXECUTE_CUSTOM[Execute Custom Command]

    %% Processing completion paths
    START_DICTATION --> LOG_ACTION[Log Action]
    STOP_DICTATION --> LOG_ACTION
    RESUME_DICTATION --> LOG_ACTION
    ERROR_DICTATION --> LOG_ERROR[Log Error]

    CLEAR_CLIPBOARD --> LOG_ACTION
    REPEAT_LAST --> LOG_ACTION
    SAVE_SESSION --> LOG_ACTION
    EXPORT_DATA --> LOG_ACTION

    AUDIO_SETTINGS --> LOG_ACTION
    AI_SETTINGS --> LOG_ACTION
    KBD_SETTINGS --> LOG_ACTION
    OUTPUT_SETTINGS --> LOG_ACTION

    ADVANCED_MENU --> LOG_ACTION
    AUTH_FAILED --> LOG_ERROR

    SHOW_STATUS --> LOG_ACTION
    EXECUTE_CUSTOM --> LOG_ACTION

    LOG_ACTION --> PROVIDE_FEEDBACK[Provide User Feedback]
    LOG_ERROR --> ERROR_FEEDBACK[Provide Error Feedback]

    PROVIDE_FEEDBACK --> END_SUCCESS([Action Complete])
    ERROR_FEEDBACK --> END_ERROR([Action Failed])

    IGNORE_KEY --> END_IGNORED([Key Ignored])
    PASS_TO_OS --> END_PASSED([Passed to OS])
    AUTH_FAILED --> END_AUTH([Authentication Failed])

    %% Styling
    classDef startEnd fill:#ff6b35,stroke:#d84315,color:#ffffff
    classDef decision fill:#66bb6a,stroke:#2e7d32,color:#ffffff
    classDef process fill:#42a5f5,stroke:#1565c0,color:#ffffff
    classDef success fill:#4caf50,stroke:#2e7d32,color:#ffffff
    classDef error fill:#ef5350,stroke:#c62828,color:#ffffff
    classDef ignore fill:#9e9e9e,stroke:#616161,color:#ffffff

    class KEY_PRESSED,END_SUCCESS,END_ERROR,END_IGNORED,END_PASSED,END_AUTH startEnd
    class VALID_INPUT,CHECK_BINDING,ACTION_TYPE,DICTATION_STATE,QUICK_TYPE,SETTINGS_TYPE,AUTH_REQUIRED,AUTH_SUCCESS decision
    class GET_BINDING,DICTATION_ACTION,QUICK_ACTION,SETTINGS_ACTION,ADVANCED_ACTION,STATUS_ACTION,CUSTOM_ACTION,START_DICTATION,STOP_DICTATION,RESUME_DICTATION,CLEAR_CLIPBOARD,REPEAT_LAST,SAVE_SESSION,EXPORT_DATA,AUDIO_SETTINGS,AI_SETTINGS,KBD_SETTINGS,OUTPUT_SETTINGS,ADVANCED_MENU,SHOW_STATUS,EXECUTE_CUSTOM,AUTH_USER,LOG_ACTION,PROVIDE_FEEDBACK process
    class SUCCESS_CLASS fill:#4caf50,stroke:#2e7d32,color:#ffffff
    class ERROR_DICTATION,LOG_ERROR,ERROR_FEEDBACK,AUTH_FAILED error
    class IGNORE_KEY,PASS_TO_OS ignore
```

---

## 🌐 Integration with Other Applications

### Application-Specific Key Bindings

```mermaid
graph TB
    subgraph "🎯 APPLICATION INTEGRATION"
        MULTI_DICTATE[Multi-Dictate Core]

        subgraph "📝 TEXT EDITORS"
            TEXT1[VS Code<br/>Super+F9: Dictate Code<br/>Super+F10: Command Palette<br/>Ctrl+Shift+S: Status]
            TEXT2[Sublime Text<br/>Super+F9: Insert Text<br/>Super+F11: Settings<br/>Ctrl+Shift+C: Format]
            TEXT3[Vim/Neovim<br/>Ctrl+Space: Dictation Mode<br/>Leader+D: Dictate<br/>Leader+S: Status]
        end

        subgraph "🌐 WEB BROWSERS"
            WEB1[Firefox<br/>Super+F9: Dictate Form<br/>Super+F10: Quick Commands<br/>Ctrl+Shift+S: Browser Status]
            WEB2[Chrome/Chromium<br/>Super+F9: Dictate Search<br/>Super+F11: Browser Settings<br/>Ctrl+Shift+F: Find with AI]
            WEB3[Safari<br/>Cmd+F9: Dictate Text<br/>Cmd+F10: Quick Actions<br/>Cmd+Shift+S: Safari Status]
        end

        subgraph "💼 OFFICE APPLICATIONS"
            OFFICE1[Microsoft Word<br/>Alt+F9: Dictate Document<br/>Alt+F10: Formatting<br/>Ctrl+Shift+D: Dictate Dialog]
            OFFICE2[LibreOffice Writer<br/>Ctrl+Super+F9: Dictate<br/>Ctrl+Super+F10: Quick Format<br/>Ctrl+Shift+S: Document Status]
            OFFICE3[Google Docs<br/>Ctrl+F9: Dictate Text<br/>Ctrl+F10: Voice Commands<br/>Ctrl+Shift+S: Doc Status]
        end

        subgraph "💬 COMMUNICATION"
            COMM1[Slack/Discord<br/>Super+F9: Dictate Message<br/>Super+F10: Quick Replies<br/>Ctrl+Shift+M: Dictate DM]
            COMM2[Email Clients<br/>Alt+F9: Dictate Email<br/>Alt+F10: Quick Templates<br/>Ctrl+Shift+E: Email Status]
            COMM3[Zoom/Teams<br/>Ctrl+Space: Dictate Chat<br/>Ctrl+Shift+C: Caption Mode<br/>Ctrl+Shift+S: Meeting Status]
        end

        subgraph "🔧 DEVELOPMENT TOOLS"
            DEV1[Terminal/Konsole<br/>Ctrl+Super+F9: Dictate Commands<br/>Ctrl+Super+F10: Execute<br/>Ctrl+Shift+T: Terminal Status]
            DEV2[IDE (PyCharm/IntelliJ)<br/>Alt+F9: Dictate Code<br/>Alt+F10: Refactor with AI<br/>Ctrl+Shift+I: IDE Status]
            DEV3[Git Clients<br/>Super+G: Dictate Commit<br/>Super+F10: Quick Commands<br/>Ctrl+Shift+G: Git Status]
        end
    end

    MULTI_DICTATE --> TEXT1
    MULTI_DICTATE --> TEXT2
    MULTI_DICTATE --> TEXT3

    MULTI_DICTATE --> WEB1
    MULTI_DICTATE --> WEB2
    MULTI_DICTATE --> WEB3

    MULTI_DICTATE --> OFFICE1
    MULTI_DICTATE --> OFFICE2
    MULTI_DICTATE --> OFFICE3

    MULTI_DICTATE --> COMM1
    MULTI_DICTATE --> COMM2
    MULTI_DICTATE --> COMM3

    MULTI_DICTATE --> DEV1
    MULTI_DICTATE --> DEV2
    MULTI_DICTATE --> DEV3

    %% Styling
    classDef core fill:#ff6b35,stroke:#d84315,color:#ffffff
    classDef textEdit fill:#42a5f5,stroke:#1565c0,color:#ffffff
    classDef browser fill:#66bb6a,stroke:#2e7d32,color:#ffffff
    classDef office fill:#ffa726,stroke:#ef6c00,color:#ffffff
    classDef communication fill:#ab47bc,stroke:#6a1b9a,color:#ffffff
    classDef development fill:#8d6e63,stroke:#5d4037,color:#ffffff

    class MULTI_DICTATE core
    class TEXT1,TEXT2,TEXT3 textEdit
    class WEB1,WEB2,WEB3 browser
    class OFFICE1,OFFICE2,OFFICE3 office
    class COMM1,COMM2,COMM3 communication
    class DEV1,DEV2,DEV3 development
```

### Context-Aware Key Processing

```mermaid
flowchart TD
    KEY_INPUT([Key Press Received]) --> DETECT_CONTEXT[Detect Active Application]

    DETECT_CONTEXT --> APP_TYPE{Application Type?}

    APP_TYPE -->|Text Editor| TEXT_MODE[Text Editor Mode]
    APP_TYPE -->|Web Browser| WEB_MODE[Web Browser Mode]
    APP_TYPE -->|Office App| OFFICE_MODE[Office Application Mode]
    APP_TYPE -->|IDE/Dev| DEV_MODE[Development Mode]
    APP_TYPE -->|Communication| COMM_MODE[Communication Mode]
    APP_TYPE -->|System| SYSTEM_MODE[System Mode]
    APP_TYPE -->|Unknown| DEFAULT_MODE[Default Mode]

    TEXT_MODE --> TEXT_BINDINGS[Load Text Editor Bindings]
    WEB_MODE --> WEB_BINDINGS[Load Browser Bindings]
    OFFICE_MODE --> OFFICE_BINDINGS[Load Office Bindings]
    DEV_MODE --> DEV_BINDINGS[Load Development Bindings]
    COMM_MODE --> COMM_BINDINGS[Load Communication Bindings]
    SYSTEM_MODE --> SYS_BINDINGS[Load System Bindings]
    DEFAULT_MODE --> DEFAULT_BINDINGS[Load Default Bindings]

    TEXT_BINDINGS --> CONTEXT_FEATURES{Context Features}
    WEB_BINDINGS --> CONTEXT_FEATURES
    OFFICE_BINDINGS --> CONTEXT_FEATURES
    DEV_BINDINGS --> CONTEXT_FEATURES
    COMM_BINDINGS --> CONTEXT_FEATURES
    SYS_BINDINGS --> CONTEXT_FEATURES
    DEFAULT_BINDINGS --> CONTEXT_FEATURES

    CONTEXT_FEATURES --> AUTO_FORMAT[Auto-formatting]
    CONTEXT_FEATURES --> APP_COMMANDS[Application Commands]
    CONTEXT_FEATURES --> CONTEXT_SHORTCUTS[Context Shortcuts]
    CONTEXT_FEATURES --> SMART_COMPLETION[Smart Completion]

    AUTO_FORMAT --> EXECUTE_BINDING[Execute Contextual Binding]
    APP_COMMANDS --> EXECUTE_BINDING
    CONTEXT_SHORTCUTS --> EXECUTE_BINDING
    SMART_COMPLETION --> EXECUTE_BINDING

    EXECUTE_BINDING --> PROVIDE_CONTEXT[Provide Contextual Feedback]
    PROVIDE_CONTEXT --> END_CONTEXT([Context Processing Complete])

    %% Styling
    classDef startEnd fill:#ff6b35,stroke:#d84315,color:#ffffff
    classDef detection fill:#66bb6a,stroke:#2e7d32,color:#ffffff
    classDef mode fill:#42a5f5,stroke:#1565c0,color:#ffffff
    classDef features fill:#ffa726,stroke:#ef6c00,color:#ffffff
    classDef execution fill:#ab47bc,stroke:#6a1b9a,color:#ffffff

    class KEY_INPUT,END_CONTEXT startEnd
    class DETECT_CONTEXT,APP_TYPE detection
    class TEXT_MODE,WEB_MODE,OFFICE_MODE,DEV_MODE,COMM_MODE,SYSTEM_MODE,DEFAULT_MODE mode
    class TEXT_BINDINGS,WEB_BINDINGS,OFFICE_BINDINGS,DEV_BINDINGS,COMM_BINDINGS,SYS_BINDINGS,DEFAULT_BINDINGS mode
    class CONTEXT_FEATURES,AUTO_FORMAT,APP_COMMANDS,CONTEXT_SHORTCUTS,SMART_COMPLETION features
    class EXECUTE_BINDING,PROVIDE_CONTEXT execution
```

---

## 📖 Quick Reference Command Summary

### Essential Keyboard Commands by Function

```bash
# ============================================
# 🎤 DICTATION CONTROL
# ============================================

# Main dictation toggle
Super+F9                        # Start/Stop dictation
Ctrl+Space                      # Pause/Resume recording
Ctrl+Enter                      # Complete current dictation
Ctrl+Backspace                  # Undo last dictation segment
Ctrl+Shift+C                    # Copy result to clipboard

# ============================================
# ⚡ QUICK COMMANDS (Super+F10 Menu)
# ============================================

Super+F10, then press:
1                               # Clear system clipboard
2                               # Repeat last dictation
3                               # Save current session
4                               # Toggle recognition language
5                               # Adjust audio volume
6                               # Adjust typing speed
7                               # Export session data
8                               # Import settings
9                               # Reset to defaults

# ============================================
# ⚙️ SETTINGS CONTROL (Super+F11)
# ============================================

Super+F11                        # Open settings panel
Settings Categories:
- Audio                          # Input device, sample rate, VAD
- AI Models                      # Primary/fallback models
- Keyboard                       # Layout detection, custom keys
- Output                         # Typing mode, voice feedback
- Advanced                       # Performance, logging, security

# ============================================
# 🚀 ADVANCED FEATURES (Super+F12)
# ============================================

Super+F12                        # Advanced menu (auth required)
Advanced Options:
- Performance                    # Benchmark, optimize, profiling
- Diagnostics                   # System check, component test
- Developer                     # Debug mode, API access
- Security                      # Audit, permissions, privacy
- Export/Import                 # Data backup, configuration

# ============================================
# 📊 SYSTEM STATUS
# ============================================

Ctrl+Shift+S                    # Show system status
Auto-dismiss after 10 seconds or any key press

# ============================================
# 🔧 CUSTOM KEY BINDINGS
# ============================================

# Create custom bindings through settings:
# Super+F11 → Keyboard → Custom Bindings

# Examples:
Super+Ctrl+V                    # Paste with AI enhancement
Alt+Shift+D                     # Quick dictation toggle
Ctrl+Alt+T                      # Translate last text
Super+Shift+S                   # Save session snapshot
Ctrl+Shift+F                    # AI-powered find & replace

# ============================================
# 🌐 APPLICATION-SPECIFIC
# ============================================

# Text Editors (VS Code, Sublime, Vim)
Alt+F9                          # Dictate code
Alt+F10                         # AI formatting
Ctrl+Shift+I                    # IDE status

# Web Browsers (Firefox, Chrome)
Super+F9                        # Dictate form fields
Super+F10                       # Browser commands
Ctrl+Shift+F                    # AI-enhanced search

# Office Applications
Alt+F9                          # Dictate document
Alt+F10                         # Quick formatting
Ctrl+Shift+E                    # Email mode

# Development Tools
Ctrl+Super+F9                   # Dictate terminal commands
Alt+F9                          # Dictate code in IDE
Super+G                         # Dictate git commit message

# ============================================
# 🎮 EMERGENCY COMMANDS
# ============================================

Ctrl+Shift+Q                    # Quick exit
Ctrl+Shift+R                    # Restart service
Ctrl+Shift+D                    # Debug mode
Escape                          # Cancel current operation
```

---

## 📝 Summary

This comprehensive keyboard flow documentation provides complete step-by-step processing details for every key binding in the Multi-Dictate system. The documentation covers:

**🎯 Key Features:**
- **Complete Key Mapping**: Every default and customizable key binding
- **Step-by-Step Processing**: Detailed execution flows for each key
- **Application Integration**: Context-aware key handling
- **Visual Flow Diagrams**: Clear mermaid diagrams for each process
- **Real-world Examples**: Practical usage scenarios
- **Error Handling**: Comprehensive error management flows

**🔧 Technical Coverage:**
- Hardware-level key detection and processing
- System integration with GNOME/gsettings
- Context-aware application integration
- Security and authentication for advanced features
- Real-time feedback and status reporting
- Custom binding creation and management

The system provides enterprise-grade keyboard control with intelligent routing, context awareness, and extensive customization capabilities for optimal user productivity.