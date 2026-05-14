PAGE_BG = "#f6f8fc"
SHELL_BG = "#111827"
SHELL_PANEL = "#1f2937"
PANEL_BG = "#ffffff"
TEXT_BG = "#ffffff"
INK = "#111827"
MUTED = "#4b5563"
REPORT_BLUE = "#2563eb"
BORDER = "#cbd5e1"
CARD_SHADOW = "#cbd5e1"
CARD_HOVER = "#f8fafc"
SUCCESS = "#10b981"

RESULT_TABS = (
    (
        "System Info",
        "System_Info",
        "system_info.csv",
        "Host identity, Windows version, install data, and computer name values.",
        "SYSTEM",
        "#2563eb",
    ),
    (
        "User Activity",
        "User_Activity",
        "recent_activity.csv",
        "Recent documents, typed paths, RunMRU, and open/save activity.",
        "ACTIVITY",
        "#059669",
    ),
    (
        "Execution History",
        "Execution_History",
        "execution_history.csv",
        "UserAssist and AppCompat traces that show program execution evidence.",
        "EXECUTION",
        "#7c3aed",
    ),
    (
        "Persistence",
        "Persistence",
        "run_keys.csv",
        "Run and RunOnce registry entries used for autorun persistence.",
        "AUTORUN",
        "#dc2626",
    ),
    (
        "USB History",
        "USB_History",
        "usb_devices.csv",
        "USB storage devices, instance IDs, friendly names, and timestamps.",
        "USB",
        "#d97706",
    ),
    (
        "Network Info",
        "Network_Info",
        "network_profiles.csv",
        "Known network profiles, creation dates, and last connection times.",
        "NETWORK",
        "#0891b2",
    ),
)

CATEGORY_ITEMS = {
    "System Info": ("Computer Name", "Windows Version", "Install Details", "Registered Owner"),
    "User Activity": ("Recent Documents", "Typed Paths", "Run Commands", "Opened/Saved Files"),
    "Execution History": ("UserAssist", "AppCompat Store", "Decoded Program Names", "Raw Values"),
    "Persistence": ("Run Keys", "RunOnce Keys", "User Autoruns", "System Autoruns"),
    "USB History": ("USB Devices", "Device Types", "Instance IDs", "Friendly Names"),
    "Network Info": ("Network Profiles", "Profile Names", "Created Time", "Last Connected"),
}
