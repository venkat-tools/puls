/**
 * Venkat Windows Tool Kit - Application Logic Suite
 * Handles Tab navigation, Theme Toggling, Diagnostics Wizard state machine, 
 * Error Code Search matching, Test Page configuration, and localStorage Maintenance Logging.
 */

// Hardcoded Default Gemini API Key (Replace empty string with your key to avoid entering it every time)
const DEFAULT_GEMINI_API_KEY = "AQ.Ab8RN6LR7pTxNb8J3H4ffw4MS_wdIt3yL53of1EOauvrlylhrA";

// Global State
let currentTheme = 'dark';
let activeTab = 'dashboard';
let wizardState = {
  category: null,
  questionId: null,
  history: [] // for going back
};

// Local API Server Base URL (handles file:// and remote web hosting launches)
const API_BASE = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') ? '' : 'http://localhost:3000';
let isServerOnline = false;

// Error Code Database
const ERROR_DATABASE = [
  {
    code: '59.F0',
    brand: 'hp',
    name: 'Fuser Motor Rotation Error',
    description: 'The transfer alienation sensor or fuser motor has experienced a startup or rotational failure, common on HP LaserJet printers.',
    steps: [
      'Perform a cold reset: Turn the printer off, wait 30 seconds, and turn it back on.',
      'Check for physical obstructions near the fuser gear assemblies or toner drive gears.',
      'Perform a system diagnostics test of the alienation motor via the printer control panel.',
      'If the error persists, the fuser assembly motor or ITB (Intermediate Transfer Belt) alienation mechanism may require physical replacement.'
    ]
  },
  {
    code: '50.1',
    brand: 'hp',
    name: 'Fuser Low Temperature Error',
    description: 'The printer fuser assembly is failing to reach operating temperature within the allotted timeout period.',
    steps: [
      'Unplug the printer directly from any surge protectors and plug it directly into a high-amperage wall outlet.',
      'Allow the printer to cool down for 20 minutes before restarting.',
      'Check the fuser power connector pins on the back of the fuser unit.',
      'Replace the fuser assembly unit if the heater element is burned out.'
    ]
  },
  {
    code: '1401',
    brand: 'canon',
    name: 'Printhead Recognition Error (Code 1401/1403)',
    description: 'The printer cannot verify or read the EEPROM signature of the printhead, meaning it is either missing, misaligned, or faulty.',
    steps: [
      'Open the cover and remove all individual ink cartridges.',
      'Release the gray lock lever on the carriage and carefully lift out the printhead unit.',
      'Use a lint-free cloth lightly moistened with isopropyl alcohol to clean the gold contact pins on the back of the printhead.',
      'Clean the matching pin contacts inside the carriage slot.',
      'Reinsert the printhead, lock the lever, insert cartridges, and restart the unit.'
    ]
  },
  {
    code: 'B200',
    brand: 'canon',
    name: 'Critical Voltage / Temperature Fault',
    description: 'An over-voltage or thermal sensor spike has occurred on the printhead assembly, triggering a firmware safety lockout.',
    steps: [
      'Power off the printer, unplug the main power cord, and disconnect the USB or Ethernet connection.',
      'Leave the unit completely unpowered for at least 30 minutes to drain the capacitor banks.',
      'Open the door and inspect the carriage rail for dust buildup or gear jams.',
      'Power on the printer. If the error returns, the printhead nozzle heaters are permanently damaged and require a new printhead.'
    ]
  },
  {
    code: '0xEA',
    brand: 'epson',
    name: 'Carriage Jam Fatal Error',
    description: 'The print carriage sensor detected an unexpected physical obstruction blocking its path along the carriage guide rail.',
    steps: [
      'Unplug the printer immediately to prevent damage to the carriage belt motor.',
      'Open the scanner unit/printer cover and check for torn paper scraps, paperclips, or dust balls.',
      'Check the clear encoder strip (thin plastic strip running behind the carriage) for ink smudges. Clean gently with a dry cotton swab.',
      'Manually push the print carriage left and right to ensure smooth slide movement.'
    ]
  },
  {
    code: 'W-02',
    brand: 'epson',
    name: 'Paper Feed / Roll Gate Jam',
    description: 'Paper has failed to pass through the internal registration rollers or has triggered the exit sensor prematurely.',
    steps: [
      'Turn off the printer and look inside the paper feeder tray.',
      'Slowly pull any visible sheets straight out. Do not pull at an angle to avoid tearing.',
      'Verify that the paper guide tabs are snug against the paper stack, not clamping it too tight.',
      'Clean the rubber pickup rollers using a damp cloth to restore grip.'
    ]
  },
  {
    code: 'E2',
    brand: 'brother',
    name: 'Rear Cover Open or Paper Jam',
    description: 'The rear sensor switch detects that the duplex tray is out of alignment, or paper is jammed inside the back panel.',
    steps: [
      'Turn the printer around and pull out the rear paper clearance cover.',
      'Carefully extract any jammed paper or labels sticking to the rollers.',
      'Push the rear cover lock levers back into their locked position.',
      'Inspect the plastic sensor flag inside the cover tab for physical breaks.'
    ]
  },
  {
    code: 'E3',
    brand: 'brother',
    name: 'No Paper Fed / Roller Friction Loss',
    description: 'The feed rollers spun for 3 cycles but the registration sensor did not detect the lead edge of a sheet.',
    steps: [
      'Pull out the main paper drawer tray fully.',
      'Look inside the bottom cavity and locate the rubber separation roller pads.',
      'Use a cloth with warm water to clean paper dust and debris off the rollers.',
      'Fan the paper stack in the tray and ensure it is not loaded past the maximum mark.'
    ]
  },
  {
    code: '0x0000011b',
    brand: 'windows',
    name: 'Windows RPC Printer Sharing Protection Block',
    description: 'A security update (e.g., CVE-2021-34481) enforces RPC authentication privacy levels, preventing connections to shared network printers.',
    steps: [
      'On the printer host PC, open Registry Editor (regedit).',
      'Navigate to HKEY_LOCAL_MACHINE\\System\\CurrentControlSet\\Control\\Print.',
      'Create a new DWORD (32-bit) named RpcAuthnLevelPrivacyEnabled and set its value to 0.',
      'Restart the Print Spooler service on the host computer.',
      'Note: This registry setting bypasses privacy enforcement; ensure your LAN is trusted.'
    ]
  },
  {
    code: '0x00000709',
    brand: 'windows',
    name: 'Cannot Connect / Group Policy RPC Restriction',
    description: 'Windows blocks remote printer connections because the client RPC interface is restricted from connecting to local spoolers.',
    steps: [
      'Open the Group Policy Editor (gpedit.msc) on the client computer.',
      'Go to Computer Configuration > Administrative Templates > Printers.',
      'Double-click Configure RPC connection settings.',
      'Set it to Enabled and choose "RPC over Named Pipes and TCP" from the options.',
      'Run gpupdate /force in cmd and restart the print spooler.'
    ]
  },
  {
    code: '0x0000007a',
    brand: 'windows',
    name: 'Invalid Printer Port / LPR Configuration Error',
    description: 'The print system cannot establish an LPD connection because the local LPR port monitor service is disabled or blocked by the firewall.',
    steps: [
      'Open Windows Features (optionalfeatures.exe) and check "LPD Print Service" and "LPR Port Monitor".',
      'Open Control Panel > Devices and Printers > Add Printer.',
      'Add a local printer with a manual LPR Port, specifying the server IP and LPD queue name.',
      'Ensure TCP port 515 (LPD) is open in the firewall of the destination printer host.'
    ]
  },
  {
    code: 'SMB-Share',
    brand: 'windows',
    name: 'SMB Client/Server Connection Blocked',
    description: 'Windows 11 disables SMBv1 by default, which prevents legacy network-attached printers or old sharing servers from establishing connection.',
    steps: [
      'Open Windows Features and enable "SMB 1.0/CIFS File Sharing Support" if connecting to a legacy printer server.',
      'To enable SMBv2/v3 server sharing, run PowerShell as Administrator: Set-SmbServerConfiguration -EnableSMB2Protocol $true.',
      'Verify that Network Discovery is enabled in Network & Sharing Center.',
      'Ensure TCP port 445 (SMB) is open in your local network firewall.'
    ]
  }
];

// Wizard Logic Decision Tree
const WIZARD_STEPS = {
  connectivity: {
    start: {
      question: "How is your printer currently connected to your computer?",
      options: [
        { text: "Wi-Fi (Wireless Network)", next: "wifi_check" },
        { text: "USB Cable (Direct Connect)", next: "usb_check" },
        { text: "Ethernet / Network LAN Cable", next: "network_check" },
        { text: "Windows Printer Sharing (SMB / RPC / Group Policy)", next: "network_sharing_check" }
      ]
    },
    wifi_check: {
      question: "What is the behavior of the Wi-Fi light/indicator on the printer?",
      options: [
        { text: "It is flashing or blinking continuously", next: "wifi_blinking_solution" },
        { text: "It is solid/on, but my computer cannot see it", next: "wifi_ip_check" },
        { text: "The light is completely dark/off", next: "wifi_off_solution" }
      ]
    },
    wifi_ip_check: {
      question: "Are your computer and printer connected to the exact same Wi-Fi router (SSID name)?",
      options: [
        { text: "Yes, both are on the same SSID/band", next: "wifi_spooler_test" },
        { text: "No, or my router has separate 2.4G and 5G networks", next: "wifi_ssid_solution" },
        { text: "I am not sure how to verify this", next: "wifi_check_ip_solution" }
      ]
    },
    wifi_spooler_test: {
      question: "Can you access the printer's Web Console (IP Address) from your browser?",
      options: [
        { text: "Yes, the page loads but it will not print", next: "spooler_reset_solution" },
        { text: "No, the site says connection timed out", next: "wifi_ip_reassign_solution" }
      ]
    },
    usb_check: {
      question: "Does your computer make a connection sound or display a notification when you plug the USB cable in?",
      options: [
        { text: "Yes, but it says 'Device Not Recognized'", next: "usb_driver_solution" },
        { text: "No sound or reaction at all", next: "usb_hardware_solution" }
      ]
    },
    network_check: {
      question: "Is the green connection status link light glowing on the printer's Ethernet port?",
      options: [
        { text: "Yes, the link light is glowing/blinking", next: "network_dhcp_solution" },
        { text: "No, the port lights are completely dark", next: "network_cable_solution" }
      ]
    },
    network_sharing_check: {
      question: "What Windows network printer sharing issue are you seeing?",
      options: [
        { text: "Remote RPC connection error (e.g. 0x0000011b, 0x00000709)", next: "rpc_sharing_error_options" },
        { text: "SMB / Network discovery sharing problems", next: "smb_sharing_check" },
        { text: "LPD / LPR Port connection issues", next: "lpd_sharing_check" }
      ]
    },
    rpc_sharing_error_options: {
      question: "Which RPC printer sharing error is blocking your connection?",
      options: [
        { text: "Error 0x0000011b (Registry Auth Privacy Fault)", next: "rpc_11b_solution" },
        { text: "Error 0x00000709 (Default Printer / RPC Policy Restriction)", next: "rpc_709_solution" }
      ]
    },
    smb_sharing_check: {
      question: "What SMB / Local Policy adjustment do you want to configure?",
      options: [
        { text: "Enable/Disable SMB v1/v2 protocols", next: "smb_configure_solution" },
        { text: "Configure Windows Group Policy (gpedit) security bounds", next: "gpedit_sharing_solution" }
      ]
    },
    lpd_sharing_check: {
      question: "What LPD port setting requires verification?",
      options: [
        { text: "Configure LPD Print Port and Windows Features", next: "lpd_configure_solution" }
      ]
    }
  },
  quality: {
    start: {
      question: "What specific defect are you seeing on your printouts?",
      options: [
        { text: "White lines, streaks, or missing colors", next: "clogged_nozzles_solution" },
        { text: "Extremely light, faded, or washed-out prints", next: "toner_low_solution" },
        { text: "Smudges, ink smears, or dark dots repeating down the page", next: "roller_fuser_dirty_solution" },
        { text: "Double images, blurry text, or misaligned columns", next: "alignment_needed_solution" }
      ]
    }
  },
  paper: {
    start: {
      question: "Where is the paper jam or feeding error located?",
      options: [
        { text: "Paper is jammed inside the main rollers/duplex unit", next: "roller_jam_solution" },
        { text: "Printer says 'Out of Paper' but the tray is loaded", next: "roller_wear_solution" },
        { text: "Multiple sheets feed at once causing immediate jams", next: "sheet_friction_solution" }
      ]
    }
  },
  hardware: {
    start: {
      question: "What physical hardware issue are you experiencing?",
      options: [
        { text: "There is a specific numeric error code showing on the screen", next: "goto_error_database" },
        { text: "The printer is making a loud grinding or squealing noise", next: "gears_carriage_jam_solution" },
        { text: "Flashing red/orange light, but no text on screen", next: "cover_reset_solution" }
      ]
    }
  }
};

// Solution Detail Database
const SOLUTIONS = {
  // Connectivity
  wifi_blinking_solution: {
    title: "Reconnect Printer to Wi-Fi",
    steps: [
      "Press the WPS button on your Wi-Fi router, then press the Wi-Fi button on your printer within 2 minutes.",
      "If your printer has a screen, go to Network Settings -> Wireless Setup Wizard and select your SSID.",
      "Ensure you enter the Wi-Fi password carefully (passwords are case-sensitive).",
      "Power cycle both the router and printer if connection handshake fails."
    ],
    tip: "Printers typically connect only to 2.4 GHz bands. If your router has smart steering, temporarily split your Wi-Fi bands."
  },
  wifi_off_solution: {
    title: "Enable Wireless Radio",
    steps: [
      "Access the printer settings panel and verify that 'Wireless' or 'Wi-Fi' is turned ON.",
      "On older models, look for a physical Wi-Fi switch or button on the outer chassis and hold it for 3 seconds.",
      "Perform a Network Defaults Reset in the printer's Administration menu to restore the Wi-Fi card state."
    ],
    tip: "A green wireless light represents a connected state, while blinking indicates searching. No light means disabled."
  },
  wifi_ssid_solution: {
    title: "Align Network SSIDs",
    steps: [
      "Open your computer's Wi-Fi network settings and note the SSID name.",
      "Print a Network Configuration page from your printer (under Settings > Reports) to check its connected SSID.",
      "If your computer is on a 5 GHz band and the printer only supports 2.4 GHz, connect your computer to the 2.4 GHz SSID temporarily to send the print job."
    ],
    tip: "Many modern mesh routers use a single name for both bands; if so, verify client isolation is disabled in router admin."
  },
  wifi_check_ip_solution: {
    title: "Locate and Verify Printer IP",
    steps: [
      "Print the network configuration page from the printer control panel.",
      "Locate the IP Address line (it will look like 192.168.X.X or 10.0.X.X).",
      "Open a web browser on your computer and type the IP address directly into the URL bar.",
      "If the printer status page loads, the network link is functional, and the issue lies in your computer's driver settings."
    ],
    tip: "If the IP starts with 169.254, the printer has failed to retrieve an IP from the router and is using an auto-configuration IP."
  },
  spooler_reset_solution: {
    title: "Restart Windows Print Spooler",
    steps: [
      "On Windows, press Win + R, type 'services.msc' and press Enter.",
      "Scroll down to find the 'Print Spooler' service.",
      "Right-click 'Print Spooler' and select 'Restart'.",
      "If jobs are still stuck, go to 'C:\\Windows\\System32\\spool\\PRINTERS' and delete all files in this folder, then restart the spooler service."
    ],
    tip: "Stuck jobs in the queue will block all incoming print packets even if the network connection is perfectly fine."
  },
  wifi_ip_reassign_solution: {
    title: "Fix Router IP Lease Conflict",
    steps: [
      "Turn off the printer completely.",
      "Unplug your internet router/modem for 30 seconds, then plug it back in and wait for it to fully start.",
      "Turn on the printer. The router will assign a fresh, non-conflicting IP address.",
      "To prevent this in the future, log into the router admin dashboard and assign a 'Static IP Reservation' to the printer's MAC address."
    ],
    tip: "Printers left in standby mode for long periods can lose their DHCP lease, causing IP address drifting."
  },
  usb_driver_solution: {
    title: "Reinstall USB Driver Stack",
    steps: [
      "Unplug the USB cable from your computer.",
      "Go to Device Manager (Win + X > Device Manager) and expand 'Universal Serial Bus controllers'.",
      "Uninstall any items marked with a yellow warning triangle.",
      "Plug the printer back into a different USB port (preferably a USB 2.0 port on the back of a desktop computer).",
      "Windows will download and load the correct USB print support stack automatically."
    ],
    tip: "Avoid USB hubs or extensions. Connect the printer directly to the PC motherboard port."
  },
  usb_hardware_solution: {
    title: "Inspect Cable & Port Hardware",
    steps: [
      "Verify the USB cable is firmly inserted in the square USB-B port on the back of the printer, not the network port.",
      "Swap out the USB printer cable. Cable failure is common due to bends or kinks.",
      "Try connecting the printer to a different computer to verify if the printer's logic board port is functioning."
    ],
    tip: "USB cables longer than 15 feet can suffer from signal attenuation, leading to intermittent connection drops."
  },
  network_dhcp_solution: {
    title: "Fix LAN Ethernet Configuration",
    steps: [
      "Print a network report page to check the IP assignment mode. It should be set to 'DHCP' or 'Automatic'.",
      "If the printer shows a static IP that does not match your home network subnet, change the printer settings to DHCP and reboot.",
      "Ensure your router network switch has DHCP enabled."
    ],
    tip: "LAN printers must be in the same IP range as the computer. If the PC is 192.168.1.5, the printer must be 192.168.1.X."
  },
  network_cable_solution: {
    title: "Verify Ethernet Link Layer",
    steps: [
      "Check if the Ethernet cable is clicked firmly into the port.",
      "Verify the cable is plugged into a LAN port on the router, not the WAN/Internet port.",
      "Replace the Ethernet cable with a verified working Cat5e/Cat6 patch cable.",
      "Check if the port on the switch or router has a status light indicator."
    ],
    tip: "No lights on the physical port indicate a hardware disconnect. The Ethernet card, cable, or switch port is dead."
  },

  // Print Quality
  clogged_nozzles_solution: {
    title: "Clean Printhead Nozzles",
    steps: [
      "Through the printer settings panel, navigate to Tools/Maintenance and select 'Clean Printhead' or 'Nozzle Check'.",
      "Let the cycle complete and print the nozzle test pattern.",
      "If gaps remain, run a 'Deep Cleaning' or 'Power Ink Flushing' cycle (Note: this consumes a significant amount of ink).",
      "For stubborn blocks: Remove the printhead assembly, soak the bottom nozzles in a shallow tray of warm distilled water with a few drops of glass cleaner for 10 minutes, dry thoroughly, and re-insert."
    ],
    tip: "Inkjets left unused for weeks will have dried ink in the micro-nozzles. Print a test page at least once a month to prevent this."
  },
  toner_low_solution: {
    title: "Redistribute Toner / Disable Eco-Mode",
    steps: [
      "For Laser Printers: Remove the toner cartridge, hold it horizontally, and gently rock it side-to-side 5-6 times to redistribute the toner powder inside.",
      "For Inkjet: Check ink reservoirs. If ink is below the lower line, fill immediately to prevent air from entering the tubes.",
      "Disable 'Eco-Mode', 'Draft Mode', or 'Toner Saver' in the print driver preferences panel to increase print density."
    ],
    tip: "Rocking a laser toner can buy you another 50-100 pages when the print begins to fade."
  },
  roller_fuser_dirty_solution: {
    title: "Clean Internal Rollers and Fuser",
    steps: [
      "Turn off the printer and wait 15 minutes for the fuser (Laser) to cool down (caution: fusers get extremely hot!).",
      "Remove paper drawers and look for the rubber rollers inside. Wipe them with a lint-free cloth lightly dampened with water.",
      "On laser printers, check the fuser roller for stuck toner powder or labels. Clean gently with dry microfiber.",
      "Run a 'Cleaning Page' from the printer utility menu to clear loose toner dust from the paper path."
    ],
    tip: "Avoid using alcohol on rubber rollers as it can dry out and crack the rubber compound over time."
  },
  alignment_needed_solution: {
    title: "Run Printhead Alignment",
    steps: [
      "Load blank A4/Letter paper into the main feed tray.",
      "Access the printer utility menu and run 'Align Printhead' or 'Calibration'.",
      "The printer will output a page containing numbered grids and lines.",
      "Look closely at the patterns, identify the block with the straightest lines, and input the matching numbers into the printer console.",
      "Alternatively, on scanner-equipped models, place the printed calibration sheet face down on the scanner glass and press Scan to calibrate automatically."
    ],
    tip: "Mechanical jolts or cartridge swaps pull the printing nozzles out of micrometric alignment, causing double print shadows."
  },

  // Paper Handling
  roller_jam_solution: {
    title: "Safely Clear Rollers and Sensors",
    steps: [
      "Always turn off and unplug the printer before reaching inside the roller bays.",
      "Pull jammed paper out slowly in the normal direction of the paper path. Pulling backward can damage gear clutches.",
      "Inspect the pathway with a flashlight for tiny torn paper scraps or labels stuck to rollers.",
      "Locate the plastic sensor levers (flags) along the path and verify they spring back freely when pushed."
    ],
    tip: "A tiny shred of paper blocking a single photoelectric sensor will trigger a persistent 'Paper Jam' error."
  },
  roller_wear_solution: {
    title: "Clean and Condition Roller Rubber",
    steps: [
      "Pull out the paper tray and locate the D-shaped rubber pickup rollers on the underside.",
      "Clean off white paper dust build-up using a lint-free cloth moistened with water.",
      "If the rubber feels glossy and slick, rub it gently with fine-grit sandpaper to restore grip friction.",
      "Verify the spring tension on the paper tray lift plate is functioning properly."
    ],
    tip: "Paper dust functions like baby powder, removing all friction from rubber rollers and causing feeding failures."
  },
  sheet_friction_solution: {
    title: "Reset Paper Feed Separation Pad",
    steps: [
      "Remove the paper stack from the tray.",
      "Fan the sheets thoroughly to remove static electricity cling before reloading.",
      "Ensure the paper guide tabs inside the tray are clicked into the exact size slots (A4 or Letter). Do not pack too tightly.",
      "Clean or replace the rubber separator pad located at the front center of the paper tray."
    ],
    tip: "Humidity can cause paper sheets to bond together. Store paper in a dry place to prevent multi-sheet feeds."
  },

  // Hardware
  goto_error_database: {
    title: "Lookup Error Codes",
    steps: [
      "Switch to the 'Error Lookup' tab using the navigation menu at the top.",
      "Input your printer brand and the code into the search engine.",
      "The database will provide the exact fuser, logic board, or mechanical repair sheet."
    ],
    tip: "Standard error codes allow you to isolate hardware faults instantly."
  },
  gears_carriage_jam_solution: {
    title: "Clear Carriage Obstruction",
    steps: [
      "Unplug the printer and open the main cartridge door.",
      "Locate the metal guide rail that the cartridge carriage slides on.",
      "Check for obstacles such as packing tape, jammed paper, or detached tension springs.",
      "Gently slide the carriage manually from side to side. It should slide smoothly without resistance.",
      "Clean the guide rail with a dry cloth and apply a single drop of sewing machine oil or silicone lubricant to the rail."
    ],
    tip: "Grinding noises usually mean the drive belt is slipping over stuck carriage gears."
  },
  cover_reset_solution: {
    title: "Reset Cover Safety Sensors",
    steps: [
      "Open and firmly close all access doors: cartridge door, rear duplexer door, and paper trays.",
      "Check the plastic latch tabs on the doors for cracks or breaks.",
      "Locate the micro-switches inside the frame where the door tabs insert. Clean dust out with compressed air.",
      "If the light continues flashing, perform a hard power reset: unplug the power cord for 60 seconds, then plug back in."
    ],
    tip: "A broken safety switch tab will make the printer think a door is permanently open, preventing any operation."
  },
  rpc_11b_solution: {
    title: "Fix Windows Sharing Error 0x0000011b",
    steps: [
      "On the HOST PC (where the printer is physically connected), press Win + R, type 'regedit' and press Enter.",
      "Navigate to: HKEY_LOCAL_MACHINE\\System\\CurrentControlSet\\Control\\Print.",
      "Right-click in the empty space, select New > DWORD (32-bit) Value.",
      "Name it 'RpcAuthnLevelPrivacyEnabled' (exact spelling) and ensure the value is set to 0.",
      "Open the Windows Services console (services.msc), find 'Print Spooler', and click Restart."
    ],
    tip: "A Windows security update enforces RPC privacy, which causes non-auth connections from other PCs to fail with error 0x0000011b."
  },
  rpc_709_solution: {
    title: "Configure RPC Port & Group Policy for Connection",
    steps: [
      "On the client Windows 11 PC, press Win + R, type 'gpedit.msc' and press Enter.",
      "Navigate to Computer Configuration > Administrative Templates > Printers.",
      "Find and double-click 'Configure RPC connection settings'. Set it to Enabled.",
      "In the options dropdown, change it to 'RPC over Named Pipes and TCP' (or 'RPC over Named Pipes' depending on your build).",
      "Open Command Prompt as Admin, run 'gpupdate /force', and restart the computer or Print Spooler.",
      "Ensure registry HKEY_LOCAL_MACHINE\\Software\\Policies\\Microsoft\\Windows NT\\Printers\\RPC has 'RpcUseNamedPipeShare' set to 1 if named pipes fail."
    ],
    tip: "Error 0x00000709 occurs when Windows blocks connection over standard TCP RPC ports due to new hardening guidelines."
  },
  smb_configure_solution: {
    title: "Enable/Disable SMB Protocols & Discovery",
    steps: [
      "Open Windows Features by running 'optionalfeatures' in the Run dialog.",
      "Check or uncheck 'SMB 1.0/CIFS File Sharing Support' depending on the legacy hardware requirement.",
      "To check SMBv2/v3 status, open PowerShell as Administrator and run: 'Get-SmbServerConfiguration'.",
      "Enable SMBv2/v3 by running: 'Set-SmbServerConfiguration -EnableSMB2Protocol $true'.",
      "Go to Settings > Network & Internet > Advanced network settings > Advanced sharing settings, and ensure 'File and printer sharing' is checked."
    ],
    tip: "SMBv1 is insecure and disabled in modern Windows 11. Use it only as a temporary resort for legacy print servers."
  },
  gpedit_sharing_solution: {
    title: "Verify Print Spooler Sharing Group Policies",
    steps: [
      "Run 'gpedit.msc' on both sharing computers.",
      "Go to Computer Configuration > Administrative Templates > Printers.",
      "Verify 'Allow Print Spooler to accept client connections' is set to Enabled.",
      "Verify 'Point and Print Restrictions' is either Disabled or configured to not show warnings for trusted server paths to prevent driver download blocks."
    ],
    tip: "Security restrictions like Point and Print prevent non-admin clients from downloading shared printer drivers from host machines."
  },
  lpd_configure_solution: {
    title: "Enable and Configure LPD Print Service",
    steps: [
      "Open Windows Features ('optionalfeatures') and expand the 'Print and Document Services' folder.",
      "Check 'LPD Print Service' and 'LPR Port Monitor', then click OK to install.",
      "Go to Control Panel > Devices and Printers > Add Printer, select 'Add a local printer with manual settings'.",
      "Select 'Create a new port' and choose 'LPR Port' from the dropdown.",
      "Specify the printer IP and LPD queue name, select the driver, and complete installation."
    ],
    tip: "LPD (Line Printer Daemon) is an alternative to SMB printing that avoids complex Windows-to-Windows credential handshakes."
  }
};

// INITIALIZATION
document.addEventListener("DOMContentLoaded", () => {
  // Environment Detection (Local Host vs. GitHub Pages landing)
  const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' || window.location.protocol === 'file:';
  const publicLanding = document.getElementById("public-landing");
  const appContainer = document.getElementById("app-container");

  if (isLocal) {
    if (publicLanding) publicLanding.style.display = "none";
    if (appContainer) appContainer.style.display = "flex";
  } else {
    if (publicLanding) publicLanding.style.display = "flex";
    if (appContainer) appContainer.style.display = "none";
  }

  // Load saved theme
  const savedTheme = localStorage.getItem("theme") || "dark";
  document.body.className = `${savedTheme}-theme`;
  currentTheme = savedTheme;
  const themeSelect = document.getElementById("theme-select");
  if (themeSelect) {
    themeSelect.value = savedTheme;
  }

  // Initialize Lucide Icons
  lucide.createIcons();

  // Tab Navigation Listeners
  const tabButtons = document.querySelectorAll(".nav-tab");
  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const tabId = btn.getAttribute("data-tab");
      switchTab(tabId);
    });
  });

  // Theme Select Listener
  const themeSelectEl = document.getElementById("theme-select");
  if (themeSelectEl) {
    themeSelectEl.addEventListener("change", (e) => {
      applyTheme(e.target.value);
    });
  }

  // Error Search Input Listeners
  const searchInput = document.getElementById("error-search-input");
  const brandSelect = document.getElementById("brand-select");
  if (searchInput && brandSelect) {
    searchInput.addEventListener("input", runErrorSearch);
    brandSelect.addEventListener("change", runErrorSearch);
  }

  // Test Page Controls Listeners
  const testPageRadioBtns = document.querySelectorAll("input[name='test-type']");
  testPageRadioBtns.forEach(radio => {
    radio.addEventListener("change", updateTestPagePreview);
  });

  const testPageCheckboxes = [
    'check-color-c', 'check-color-m', 'check-color-y', 'check-color-k', 
    'include-text', 'include-grid'
  ];
  testPageCheckboxes.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener("change", updateTestPagePreview);
  });

  // Set default date in Maintenance Form
  const dateInput = document.getElementById("log-date");
  if (dateInput) {
    const today = new Date().toISOString().split('T')[0];
    dateInput.value = today;
  }

  // Load Initial logs
  loadMaintenanceLogs();
  updateTestPagePreview();
  runErrorSearch();
  checkServerStatus();
  setInterval(checkServerStatus, 5000);
  startTelemetryMonitor();
  
  // Live Clock & Geolocation startup
  startLiveClock();
  fetchGeoLocation();
});

// Live 12-Hour Clock
function startLiveClock() {
  const clockEl = document.getElementById('live-clock');
  if (!clockEl) return;
  
  const updateClock = () => {
    const now = new Date();
    let hours = now.getHours();
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    const ampm = hours >= 12 ? 'PM' : 'AM';
    
    hours = hours % 12;
    hours = hours ? hours : 12; // the hour '0' should be '12'
    const hoursStr = String(hours).padStart(2, '0');
    
    clockEl.textContent = `${hoursStr}:${minutes}:${seconds} ${ampm}`;
  };
  
  updateClock();
  setInterval(updateClock, 1000);
}

// Fetch Geolocation details
async function fetchGeoLocation() {
  const countryEl = document.getElementById('geo-country');
  const regionEl = document.getElementById('geo-region-city');
  const coordinatesEl = document.getElementById('geo-coordinates');
  
  if (!countryEl || !regionEl || !coordinatesEl) return;

  // Helper for IP-based geolocation fallback
  const runIpGeoFallback = async (onlyIp = false) => {
    const urls = [];
    if (window.location.protocol !== 'file:') {
      urls.push('/api/geoip');
    } else {
      urls.push(API_BASE + '/api/geoip');
    }
    urls.push('https://freeipapi.com/api/json');
    urls.push('https://ipwho.is/');
    urls.push('https://ipapi.co/json/');
    
    let success = false;
    for (const url of urls) {
      try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP error status: ${response.status}`);
        const data = await response.json();
        
        const ip = data.ipAddress || data.ip || 'Unknown IP';
        coordinatesEl.textContent = ip;
        
        if (!onlyIp) {
          let country = data.countryName || data.country || data.country_name || 'Unknown Country';
          const code = data.countryCode || data.country_code;
          if (code) country += ` (${code})`;
          
          const region = (data.regionName && data.cityName) ? `${data.regionName}, ${data.cityName}` : 
                         (data.region && data.city) ? `${data.region}, ${data.city}` : 
                         data.region || data.city || 'Unknown Region';
                         
          countryEl.textContent = country;
          regionEl.textContent = region;
        }
        
        success = true;
        break;
      } catch (error) {
        console.warn(`[GeoIP Fallback] Failed to fetch from ${url}:`, error.message);
      }
    }
    if (!success) {
      coordinatesEl.textContent = 'Offline / Unavailable';
      if (!onlyIp) {
        countryEl.textContent = 'Offline / Unavailable';
        regionEl.textContent = 'Offline / Unavailable';
      }
    }
  };

  // Check if user has overridden location in localStorage
  const savedCountry = localStorage.getItem('custom_country');
  const savedRegion = localStorage.getItem('custom_region');
  
  if (savedCountry || savedRegion) {
    if (savedCountry) countryEl.textContent = savedCountry;
    if (savedRegion) regionEl.textContent = savedRegion;
    
    // Resolve IP silently in the background if it is still empty or default
    const currentIP = coordinatesEl.textContent;
    if (currentIP === 'Fetching...' || currentIP === 'Offline / Unavailable' || currentIP === '--') {
      runIpGeoFallback(true);
    }
    return;
  }

  // Try HTML5 Browser Geolocation (highly accurate GPS/WiFi coordinates)
  if (navigator.geolocation) {
    console.log("[GeoIP] Requesting HTML5 geolocation coordinates...");
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        try {
          const lat = position.coords.latitude;
          const lon = position.coords.longitude;
          console.log(`[GeoIP] GPS Coordinates found: ${lat}, ${lon}. Requesting reverse geocode...`);
          
          const response = await fetch(`https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${lat}&longitude=${lon}&localityLanguage=en`);
          if (!response.ok) throw new Error("Reverse geocoding failed");
          const data = await response.json();
          
          const country = data.countryName ? `${data.countryName} (${data.countryCode})` : 'Unknown Country';
          const state = data.principalSubdivision || '';
          const city = data.city || data.locality || '';
          const region = (state && city) ? `${state}, ${city}` : (state || city || 'Unknown Region');
          
          countryEl.textContent = country;
          regionEl.textContent = region;
          
          // Silently resolve and populate the IP address field only
          runIpGeoFallback(true);
        } catch (e) {
          console.warn("[GeoIP] Geocoding API failed. Falling back to IP-based lookup.", e);
          runIpGeoFallback(false);
        }
      },
      (error) => {
        console.warn("[GeoIP] Geolocation denied or unavailable. Falling back to IP-based lookup. Error code:", error.code);
        runIpGeoFallback(false);
      },
      { timeout: 6000, enableHighAccuracy: false }
    );
  } else {
    console.log("[GeoIP] Geolocation not supported by browser. Falling back to IP-based lookup.");
    runIpGeoFallback(false);
  }
}

// Manually override/edit Geolocation details
function editGeoLocation() {
  const countryEl = document.getElementById('geo-country');
  const regionEl = document.getElementById('geo-region-city');
  if (!countryEl || !regionEl) return;

  const currentCountry = countryEl.textContent;
  const currentRegion = regionEl.textContent;

  const newCountry = prompt(
    "Enter your Country (e.g., India (IN)) or leave empty to auto-detect:",
    currentCountry === 'Offline / Unavailable' ? '' : currentCountry
  );
  if (newCountry === null) return; // user cancelled

  const newRegion = prompt(
    "Enter your Region / City (e.g., Andhra Pradesh, Guntur) or leave empty to auto-detect:",
    currentRegion === 'Offline / Unavailable' ? '' : currentRegion
  );
  if (newRegion === null) return; // user cancelled

  if (newCountry.trim() === '' && newRegion.trim() === '') {
    localStorage.removeItem('custom_country');
    localStorage.removeItem('custom_region');
    // Force re-fetch from APIs
    countryEl.textContent = 'Fetching...';
    regionEl.textContent = 'Fetching...';
    fetchGeoLocation();
  } else {
    localStorage.setItem('custom_country', newCountry.trim());
    localStorage.setItem('custom_region', newRegion.trim());
    
    countryEl.textContent = newCountry.trim();
    regionEl.textContent = newRegion.trim();
  }
}

// FUNCTIONS

// 1. Tab Router
function switchTab(tabId) {
  activeTab = tabId;

  // Update tabs buttons UI
  const tabButtons = document.querySelectorAll(".nav-tab");
  tabButtons.forEach(btn => {
    if (btn.getAttribute("data-tab") === tabId) {
      btn.classList.add("active");
    } else {
      btn.classList.remove("active");
    }
  });

  // Update panels UI
  const panels = document.querySelectorAll(".tab-panel");
  panels.forEach(panel => {
    if (panel.id === tabId) {
      panel.classList.add("active");
    } else {
      panel.classList.remove("active");
    }
  });

  // Special hooks on tab activation
  if (tabId === 'testpage') {
    // Set timestamp on calibration page
    const dateEl = document.getElementById("sheet-timestamp");
    if (dateEl) {
      dateEl.innerText = "Date: " + new Date().toLocaleDateString();
    }
  }

  // Re-render icons just in case
  lucide.createIcons();
  
  if (tabId === 'printers') {
    switchSubTab('printer-status');
  } else if (tabId === 'aiassistant') {
    loadApiKey();
    toggleAiMode();
  } else if (tabId === 'disksecurity') {
    loadWebDiskInfo();
  }
}

// 2. Theme Management
function applyTheme(themeName) {
  const body = document.body;
  const themes = ['dark', 'light', 'cyberpunk', 'emerald', 'crimson'];
  themes.forEach(t => {
    body.classList.remove(`${t}-theme`);
  });
  body.classList.add(`${themeName}-theme`);
  currentTheme = themeName;
  localStorage.setItem("theme", currentTheme);
  
  const themeSelect = document.getElementById("theme-select");
  if (themeSelect && themeSelect.value !== themeName) {
    themeSelect.value = themeName;
  }
}

// 2b. Folder Browser helper
async function browseFolder(inputId) {
  try {
    const response = await fetch(API_BASE + '/api/browse');
    if (!response.ok) {
      throw new Error('Failed to open folder browser dialog');
    }
    const data = await response.json();
    if (data.success && data.path) {
      document.getElementById(inputId).value = data.path;
    }
  } catch (error) {
    console.error('Error browsing folder:', error);
    alert('Failed to browse folder. Make sure the local server is running.');
  }
}

// 3. Diagnostics Wizard Actions
function startWizardWithIssue(issueName) {
  switchTab('printers');
  switchSubTab('diagnostics');
  wizardReset();

  if (issueName === 'offline') {
    wizardSelectCategory('connectivity');
  } else if (issueName === 'streaks') {
    wizardSelectCategory('quality');
  } else if (issueName === 'paperjam') {
    wizardSelectCategory('paper');
  } else if (issueName === 'spooler') {
    wizardSelectCategory('connectivity');
    // Fast jump to wifi_spooler_test or spooler_reset_solution
    wizardState.questionId = "wifi_spooler_test";
    renderWizardQuestion();
  }
}

function wizardReset() {
  wizardState.category = null;
  wizardState.questionId = null;
  wizardState.history = [];

  // Update Progress UI
  document.getElementById("step-dot-1").className = "progress-step active";
  document.getElementById("step-dot-2").className = "progress-step";
  document.getElementById("step-dot-3").className = "progress-step";

  // Display Panel 1
  document.getElementById("wizard-step-1").classList.add("active");
  document.getElementById("wizard-step-2").classList.remove("active");
  document.getElementById("wizard-step-3").classList.remove("active");
}

function wizardSelectCategory(cat) {
  wizardState.category = cat;
  wizardState.questionId = "start";
  wizardState.history = [];

  // Update dots
  document.getElementById("step-dot-1").className = "progress-step completed";
  document.getElementById("step-dot-2").className = "progress-step active";

  // Change view
  document.getElementById("wizard-step-1").classList.remove("active");
  document.getElementById("wizard-step-2").classList.add("active");

  renderWizardQuestion();
}

function renderWizardQuestion() {
  const catData = WIZARD_STEPS[wizardState.category];
  const qData = catData[wizardState.questionId];

  // Question Title
  document.getElementById("diagnostic-question-title").innerText = qData.question;

  // Clear options
  const optionsDiv = document.getElementById("diagnostic-options");
  optionsDiv.innerHTML = "";

  // Add buttons
  qData.options.forEach(opt => {
    const btn = document.createElement("button");
    btn.className = "option-btn";
    
    // Check if next is a direct solution or another question
    const isSolution = !catData[opt.next] && opt.next !== 'goto_error_database';
    const badgeText = isSolution ? "Recommendation" : "Diagnostic Check";
    
    btn.innerHTML = `
      <span>${opt.text}</span>
      <span class="option-badge-text">${badgeText} &rarr;</span>
    `;

    btn.onclick = () => {
      wizardSelectOption(opt.next);
    };

    optionsDiv.appendChild(btn);
  });
}

function wizardSelectOption(nextId) {
  // Push current to history for backtracking
  wizardState.history.push(wizardState.questionId);

  const catData = WIZARD_STEPS[wizardState.category];
  
  if (nextId === 'goto_error_database') {
    switchTab('printers');
    switchSubTab('errors');
    fillSearch('59.F0', 'hp');
    return;
  }

  // Check if the next step is another question
  if (catData[nextId]) {
    wizardState.questionId = nextId;
    renderWizardQuestion();
  } else {
    // It is a final Solution!
    renderWizardSolution(nextId);
  }
}

function wizardBack() {
  if (wizardState.history.length > 0) {
    wizardState.questionId = wizardState.history.pop();
    renderWizardQuestion();
  } else {
    wizardReset();
  }
}

function renderWizardSolution(solutionKey) {
  const solution = SOLUTIONS[solutionKey];
  if (!solution) return;

  // Update dots
  document.getElementById("step-dot-2").className = "progress-step completed";
  document.getElementById("step-dot-3").className = "progress-step active";

  // Change View
  document.getElementById("wizard-step-2").classList.remove("active");
  document.getElementById("wizard-step-3").classList.add("active");

  // Load solution text
  document.getElementById("solution-title").innerText = solution.title;
  document.getElementById("solution-tip-text").innerText = solution.tip || "Ensure the printer is fully powered off before clearing internal gears.";

  // Populate steps list
  const stepsList = document.getElementById("solution-steps-list");
  stepsList.innerHTML = "";

  solution.steps.forEach((stepText, idx) => {
    const item = document.createElement("div");
    item.className = "step-item";
    item.innerHTML = `
      <div class="step-number">${idx + 1}</div>
      <div class="step-details">
        <h5>Step Action</h5>
        <p>${stepText}</p>
      </div>
    `;
    stepsList.appendChild(item);
  });

  // Action log button handler
  const logBtn = document.getElementById("log-solution-btn");
  if (logBtn) {
    logBtn.onclick = () => {
      logMaintenanceAction(solution.title, "Resolved", `Applied wizard repair guide: ${solution.title}`);
      switchTab('auditlogs');
    };
  }
}

// 4. Error Code Lookup Directory
function runErrorSearch() {
  const searchInput = document.getElementById("error-search-input");
  const brandSelect = document.getElementById("brand-select");
  const grid = document.getElementById("error-results-grid");
  const countText = document.getElementById("results-count-text");

  if (!grid) return;

  const query = searchInput.value.toLowerCase().trim();
  const selectedBrand = brandSelect.value;

  // Filter items
  const filtered = ERROR_DATABASE.filter(item => {
    const matchesBrand = selectedBrand === 'all' || item.brand === selectedBrand;
    const matchesQuery = item.code.toLowerCase().includes(query) || 
                         item.name.toLowerCase().includes(query) ||
                         item.description.toLowerCase().includes(query);
    return matchesBrand && matchesQuery;
  });

  // Update count text
  countText.innerText = `Found ${filtered.length} matching code(s)`;

  // Clear grid
  grid.innerHTML = "";

  if (filtered.length === 0) {
    grid.innerHTML = `
      <div class="card error-code-card" style="grid-column: span 2; align-items: center; justify-content: center; padding: 40px;">
        <i data-lucide="search-slash" style="width: 36px; height: 36px; color: var(--text-muted); margin-bottom: 12px;"></i>
        <h4>No Error Guides Found</h4>
        <p class="subtitle" style="margin-bottom: 0;">Try adjusting your query or selecting "All Brands".</p>
      </div>
    `;
    lucide.createIcons();
    return;
  }

  // Populate cards
  filtered.forEach(item => {
    const card = document.createElement("div");
    card.className = "card error-code-card";

    // Build steps HTML
    let stepsHTML = "";
    item.steps.forEach(step => {
      stepsHTML += `<li>${step}</li>`;
    });

    card.innerHTML = `
      <div>
        <div class="error-code-header">
          <div class="code-title-wrap">
            <span class="brand-badge">${item.brand.toUpperCase()} Device Error</span>
            <span class="code-badge">${item.code}</span>
          </div>
          <span class="badge ${item.brand === 'hp' ? 'badge-danger' : 'badge-warning'}">${item.brand}</span>
        </div>
        <h4 style="font-size: 0.95rem; margin-bottom: 8px;">${item.name}</h4>
        <p class="description">${item.description}</p>
        
        <div class="repair-instructions-box">
          <h5>Troubleshooting Protocol</h5>
          <ul>
            ${stepsHTML}
          </ul>
        </div>
      </div>

      <div class="error-action-row">
        <button class="btn btn-secondary btn-small" onclick="logMaintenanceAction('Fixed Error ${item.code} (${item.brand.toUpperCase()})', 'Resolved', 'Error code lookup procedure: ' + '${item.name}')">
          <i data-lucide="clipboard-list" style="width: 12px; height: 12px;"></i> Log Repair
        </button>
      </div>
    `;

    grid.appendChild(card);
  });

  lucide.createIcons();
}

function fillSearch(code, brand) {
  const searchInput = document.getElementById("error-search-input");
  const brandSelect = document.getElementById("brand-select");
  
  if (searchInput && brandSelect) {
    searchInput.value = code;
    brandSelect.value = brand;
    runErrorSearch();
  }
}

// 5. Test Page Studio Configuration
function updateTestPagePreview() {
  const testType = document.querySelector("input[name='test-type']:checked").value;
  const includeText = document.getElementById("include-text").checked;
  const includeGrid = document.getElementById("include-grid").checked;

  const cyanCheck = document.getElementById("check-color-c").checked;
  const magentaCheck = document.getElementById("check-color-m").checked;
  const yellowCheck = document.getElementById("check-color-y").checked;
  const blackCheck = document.getElementById("check-color-k").checked;

  // Toggle Section blocks
  const textSection = document.getElementById("sheet-text-section");
  const colorSection = document.getElementById("sheet-color-section");
  const cmykSection = document.getElementById("sheet-cmyk-blocks");
  const gridSection = document.getElementById("sheet-grid-section");

  // Set default viewports
  textSection.style.display = includeText ? "block" : "none";
  gridSection.style.display = includeGrid ? "block" : "none";
  colorSection.style.display = "block";
  cmykSection.style.display = "none";

  // Specific template configurations
  if (testType === 'standard') {
    // Normal calibration page
    colorSection.style.display = "block";
    cmykSection.style.display = "none";
  } else if (testType === 'cmyk') {
    // Large solid ink blocks only
    colorSection.style.display = "none";
    cmykSection.style.display = "block";
    textSection.style.display = "none";
    gridSection.style.display = "none";
  } else if (testType === 'alignment') {
    // Grid alignment sheet only
    colorSection.style.display = "none";
    cmykSection.style.display = "none";
    textSection.style.display = "none";
    gridSection.style.display = "block";
  }

  // Toggle Individual color rows
  document.querySelector(".cyan-row").style.display = cyanCheck ? "flex" : "none";
  document.querySelector(".magenta-row").style.display = magentaCheck ? "flex" : "none";
  document.querySelector(".yellow-row").style.display = yellowCheck ? "flex" : "none";
  document.querySelector(".black-row").style.display = blackCheck ? "flex" : "none";

  // Solid block grid items toggle
  document.querySelector(".cyan-block").style.display = cyanCheck ? "block" : "none";
  document.querySelector(".magenta-block").style.display = magentaCheck ? "block" : "none";
  document.querySelector(".yellow-block").style.display = yellowCheck ? "block" : "none";
  document.querySelector(".black-block").style.display = blackCheck ? "block" : "none";
}

function triggerTestPagePrint() {
  window.print();
}

// 6. Maintenance Logs Local Storage Engine
function getLogs() {
  const raw = localStorage.getItem("printpulse_logs");
  if (!raw) {
    // Add default seeds so dashboard looks premium and populated
    const seeds = [
      {
        id: "seed-1",
        date: "2026-06-12",
        model: "Epson L3210 EcoTank",
        action: "Nozzle Cleaning Run",
        status: "Resolved",
        notes: "Cyan channel was skipping lines. Ran cleaning cycle twice, now printing clean color spectrum."
      },
      {
        id: "seed-2",
        date: "2026-06-20",
        model: "HP LaserJet M404dn",
        action: "Cleared Paper Jam",
        status: "Resolved",
        notes: "Paper jammed near output roller. Carefully removed and vacuumed toner/paper dust from pickup gate."
      }
    ];
    localStorage.setItem("printpulse_logs", JSON.stringify(seeds));
    return seeds;
  }
  return JSON.parse(raw);
}

function loadMaintenanceLogs() {
  const logs = getLogs();
  
  // Render History Table
  const tableBody = document.getElementById("logs-table-body");
  const emptyState = document.getElementById("history-empty");

  if (!tableBody) return;

  tableBody.innerHTML = "";

  if (logs.length === 0) {
    emptyState.style.display = "flex";
  } else {
    emptyState.style.display = "none";
    
    // Sort logs descending (recent dates first)
    logs.sort((a,b) => new Date(b.date) - new Date(a.date));

    logs.forEach(log => {
      const tr = document.createElement("tr");
      
      let badgeClass = "badge-success";
      if (log.status === "Improved") badgeClass = "badge-warning";
      if (log.status === "Unresolved" || log.status === "Failed") badgeClass = "badge-danger";

      tr.innerHTML = `
        <td style="font-weight:600;">${log.date}</td>
        <td>${log.model}</td>
        <td>${log.action}</td>
        <td><span class="badge ${badgeClass}">${log.status}</span></td>
        <td style="max-width:250px; text-overflow:ellipsis; overflow:hidden; white-space:nowrap; cursor:pointer; color:var(--primary-color); text-decoration:underline;" title="Click to view details" onclick="showLogDetails('${log.id}')">
          ${log.notes || '—'}
        </td>
        <td>
          <button class="btn-delete-row" onclick="deleteLogEntry('${log.id}')" title="Delete Entry">
            <i data-lucide="trash-2" style="width:14px; height:14px;"></i>
          </button>
        </td>
      `;

      tableBody.appendChild(tr);
    });
  }

  // Update dashboard timeline compact view
  updateDashboardTimeline(logs);
  lucide.createIcons();
}

function showLogDetails(logId) {
  const logs = getLogs();
  const log = logs.find(l => l.id === logId);
  if (!log) return;

  document.getElementById("log-detail-date").innerText = log.date;
  
  const statusEl = document.getElementById("log-detail-status");
  statusEl.innerText = log.status;
  if (log.status === "Resolved") {
    statusEl.style.color = "#34d399";
  } else if (log.status === "Improved") {
    statusEl.style.color = "#fbbf24";
  } else {
    statusEl.style.color = "#f87171";
  }
  
  document.getElementById("log-detail-model").innerText = log.model;
  document.getElementById("log-detail-action").innerText = log.action;
  document.getElementById("log-detail-notes").innerText = log.notes || "—";

  const modal = document.getElementById("log-details-modal");
  if (modal) modal.style.display = "flex";
}

function closeLogDetailsModal() {
  const modal = document.getElementById("log-details-modal");
  if (modal) modal.style.display = "none";
}

function updateDashboardTimeline(logs) {
  const timeline = document.getElementById("compact-timeline");
  if (!timeline) return;

  timeline.innerHTML = "";

  if (logs.length === 0) {
    timeline.innerHTML = '<p class="empty-state">No actions logged yet.</p>';
    return;
  }

  // Take top 3 recent logs
  const recent = [...logs]
    .sort((a,b) => new Date(b.date) - new Date(a.date))
    .slice(0, 3);

  recent.forEach(log => {
    const item = document.createElement("div");
    item.className = "timeline-item-compact";
    
    item.innerHTML = `
      <div class="timeline-date-compact">${log.date}</div>
      <div class="timeline-content-compact">
        <div class="timeline-title-compact">${log.action}</div>
        <div class="timeline-desc-compact">${log.model} &bull; ${log.status}</div>
      </div>
    `;

    timeline.appendChild(item);
  });
}

function logMaintenanceAction(actionName, status = "Resolved", notesText = "Triggered from system calibration utility", customModel = null) {
  let model = customModel;
  
  if (!model) {
    const actionLower = actionName.toLowerCase();
    if (actionLower.includes("driver")) {
      model = "Windows Device Driver";
    } else if (actionLower.includes("dns") || actionLower.includes("network") || actionLower.includes("subnet") || actionLower.includes("ip") || actionLower.includes("rdp") || actionLower.includes("adapter")) {
      model = "Network Adapter Interface";
    } else if (actionLower.includes("disk") || actionLower.includes("chkdsk") || actionLower.includes("trim") || actionLower.includes("defrag") || actionLower.includes("volume")) {
      model = "Local Disk Drive";
    } else if (actionLower.includes("office") || actionLower.includes("outlook") || actionLower.includes("word") || actionLower.includes("excel") || actionLower.includes("powerpoint") || actionLower.includes("pst")) {
      model = "Microsoft Office Suite";
    } else if (actionLower.includes("user") || actionLower.includes("account") || actionLower.includes("policy") || actionLower.includes("gpedit") || actionLower.includes("godmode")) {
      model = "System Policy Manager";
    } else if (actionLower.includes("robocopy") || actionLower.includes("backup") || actionLower.includes("migration") || actionLower.includes("appdata")) {
      model = "Data Migration Hub";
    } else if (actionLower.includes("winget") || actionLower.includes("install")) {
      model = "Software Package Manager";
    } else if (actionLower.includes("tally") || actionLower.includes("temp") || actionLower.includes("cache") || actionLower.includes("explorer") || actionLower.includes("icon")) {
      model = "System Service Manager";
    } else if (actionLower.includes("debloat") || actionLower.includes("tweak")) {
      model = "Windows Performance Tweaker";
    } else if (actionLower.includes("nirsoft")) {
      model = "NirSoft Diagnostic Suite";
    } else {
      // Try to read active printer model from wizard context if it exists
      const printerSelect = document.getElementById("log-printer-model");
      if (printerSelect && printerSelect.value && printerSelect.value.trim() !== "") {
        model = printerSelect.value;
      } else {
        model = "Generic Printer Device";
      }
    }
  }

  const date = new Date().toISOString().split('T')[0];
  const newLog = {
    id: "log-" + Date.now(),
    date,
    model,
    action: actionName,
    status,
    notes: notesText
  };

  const logs = getLogs();
  logs.push(newLog);
  localStorage.setItem("printpulse_logs", JSON.stringify(logs));
  
  loadMaintenanceLogs();
}

function handleLogSubmit(event) {
  event.preventDefault();
  
  const modelInput = document.getElementById("log-printer-model");
  const actionSelect = document.getElementById("log-action");
  const customActionInput = document.getElementById("log-action-custom");
  const dateInput = document.getElementById("log-date");
  const statusSelect = document.getElementById("log-status");
  const notesTextarea = document.getElementById("log-notes");

  let action = actionSelect.value;
  if (action === 'custom') {
    action = customActionInput.value || "Custom Repair Task";
  }

  const newLog = {
    id: "log-" + Date.now(),
    date: dateInput.value,
    model: modelInput.value,
    action: action,
    status: statusSelect.value,
    notes: notesTextarea.value
  };

  const logs = getLogs();
  logs.push(newLog);
  localStorage.setItem("printpulse_logs", JSON.stringify(logs));

  // Reset form but retain date & model for convenience
  customActionInput.value = "";
  customActionInput.style.display = "none";
  actionSelect.value = "Nozzle Cleaning Run";
  notesTextarea.value = "";

  loadMaintenanceLogs();
}

function deleteLogEntry(id) {
  let logs = getLogs();
  logs = logs.filter(log => log.id !== id);
  localStorage.setItem("printpulse_logs", JSON.stringify(logs));
  loadMaintenanceLogs();
}

function clearAllLogs() {
  if (confirm("Are you sure you want to clear the entire log history? This cannot be undone.")) {
    localStorage.setItem("printpulse_logs", JSON.stringify([]));
    loadMaintenanceLogs();
  }
}

function toggleCustomActionInput(selectEl) {
  const customInput = document.getElementById("log-action-custom");
  if (selectEl.value === 'custom') {
    customInput.style.display = "block";
    customInput.required = true;
  } else {
    customInput.style.display = "none";
    customInput.required = false;
  }
}

// 7. Admin System Toolbox Data Registry
const TOOLBOX_DATA = {
  quick_repair: {
    title: "Printer Quick Repair Protocol",
    description: "Performs a full restart on Windows Spooler resources, flushes stuck background operations, and forces a system configuration refresh.",
    codeType: "PowerShell (Run as Admin)",
    code: `# Stop the spooler service and clear out cache files\nStop-Service -Name Spooler -Force\nRemove-Item -Path "C:\\Windows\\System32\\spool\\PRINTERS\\*" -Force -Recurse\nStart-Service -Name Spooler\nGet-Service -Name Spooler`
  },
  clear_queue: {
    title: "Clear Stuck Print Queue",
    description: "Clears all print jobs currently queued up. Warning: This will delete all active jobs waiting to print.",
    codeType: "Command Prompt (Run as Admin)",
    code: `net stop spooler\ndel /Q /F /S "%systemroot%\\System32\\Spool\\Printers\\*.*"\nnet start spooler`
  },
  restart_spooler: {
    title: "Restart Windows Print Spooler Service",
    description: "A fast power-cycle of the Spooler print engine without deleting files. Fixes most temporary freezes.",
    codeType: "PowerShell (Run as Admin)",
    code: `Restart-Service -Name Spooler -Force`
  },
  devices_printers: {
    title: "Launch Classic Devices & Printers Control Panel",
    description: "Opens the classic layout where legacy properties and printer sharing ports can be configured directly.",
    codeType: "Windows Run Dialog (Win+R)",
    code: `control printers`
  },
  print_management: {
    title: "Launch Print Management Console",
    description: "Opens the Microsoft Management Console (MMC) snap-in for printer servers, port configurations, and driver management.",
    codeType: "Windows Run Dialog (Win+R)",
    code: `printmanagement.msc`
  },
  sharing_center: {
    title: "Launch Network & Sharing Center",
    description: "Opens Network properties to configure network interfaces, private profile boundaries, and client access control.",
    codeType: "Windows Run Dialog (Win+R)",
    code: `control.exe /name Microsoft.NetworkAndSharingCenter`
  },
  printers_settings: {
    title: "Launch Printers & Scanners Settings",
    description: "Opens the modern Windows 10/11 configuration interface. You can click the 'Launch Settings' button below to open it immediately.",
    codeType: "Windows Settings URL",
    code: `ms-settings:printers`,
    launchUri: "ms-settings:printers"
  },
  point_print_fix: {
    title: "Point and Print Restriction Bypass (KB5005652)",
    description: "Relaxes Windows Point & Print restrictions to allow non-administrator users to download and update printer drivers from local trusted print servers.",
    codeType: "Registry Script (.reg)",
    code: `Windows Registry Editor Version 5.00\n\n[HKEY_LOCAL_MACHINE\\SOFTWARE\\Policies\\Microsoft\\Windows NT\\Printers\\PointAndPrint]\n"RestrictDriverInstallationToAdministrators"=dword:00000000`,
    gpoPath: "Computer Configuration > Administrative Templates > System > Device Installation",
    gpoSetting: "Configure 'Allow non-administrators to install drivers for these device setup classes' -> Enabled. Add Printer Class GUID: {4d36e979-e325-11ce-bfc1-08002be10318}"
  },
  rpc_fixes: {
    title: "RPC Over Named Pipes & Authentication Privacy Fix",
    description: "Enforces printing connection RPC packets to run over Named Pipes instead of raw TCP sockets. Resolves errors `0x00000709` and `0x0000011b` on Windows 11.",
    codeType: "Registry Script (.reg)",
    code: `Windows Registry Editor Version 5.00\n\n# Force printer RPC queries over Named Pipes\n[HKEY_LOCAL_MACHINE\\SOFTWARE\\Policies\\Microsoft\\Windows NT\\Printers\\RPC]\n"RpcOverNamedPipes"=dword:00000001\n"RpcUseNamedPipeShare"=dword:00000001\n"RpcAuthnLevelPrivacyEnabled"=dword:00000000`,
    gpoPath: "Computer Configuration > Administrative Templates > Printers",
    gpoSetting: "Configure 'Configure RPC connection settings' -> Set to Enabled, and choose 'RPC over Named Pipes and TCP' (or 'RPC over Named Pipes')."
  },
  network_discovery: {
    title: "Enable Local Network Discovery",
    description: "Opens firewall ports for SSDP and WS-Discovery protocols so your computer can auto-detect shared network printers on the LAN.",
    codeType: "PowerShell (Run as Admin)",
    code: `netsh advfirewall firewall set rule group="Network Discovery" new enable=Yes`
  },
  enable_smb1: {
    title: "Enable SMBv1 Legacy Client Support",
    description: "Installs the SMBv1 sharing stack. Required if connecting to very old NAS printer ports or legacy host operating systems. Warning: SMBv1 has known security vulnerabilities.",
    codeType: "PowerShell (Run as Admin)",
    code: `Enable-WindowsOptionalFeature -Online -FeatureName "SMB1Protocol" -All`
  },
  disable_smb1: {
    title: "Disable SMBv1 Sharing Protocol (Security Hardening)",
    description: "Disables the legacy SMBv1 client features to secure your computer against Wannacry-style network exploits.",
    codeType: "PowerShell (Run as Admin)",
    code: `Disable-WindowsOptionalFeature -Online -FeatureName "SMB1Protocol" -Force`
  },
  
  // Windows Repairs
  sfc_scan: {
    title: "System File Checker (SFC) Scan",
    description: "Scans all protected Windows system files and replaces corrupted or incorrect versions with factory originals.",
    codeType: "CMD (Run as Admin)",
    code: "start cmd /k sfc /scannow"
  },
  dism_restore: {
    title: "DISM Image Health Repair",
    description: "Connects to Windows Update to download and restore clean component copies for system files.",
    codeType: "CMD (Run as Admin)",
    code: "start cmd /k dism /online /cleanup-image /restorehealth"
  },
  reset_wua: {
    title: "Reset Windows Update Components",
    description: "Stops background update services, deletes downloaded update caches, and recreates service nodes.",
    codeType: "PowerShell (Run as Admin)",
    code: "start powershell -NoExit -Command \"Stop-Service wuauserv,bits,cryptsvc; Remove-Item C:\\Windows\\SoftwareDistribution\\* -Recurse -Force; Start-Service wuauserv,bits,cryptsvc\""
  },
  flush_dns: {
    title: "Flush DNS Cache & DHCP Renewal",
    description: "Flushes the local DNS client resolver database and requests a new DHCP IP address from the network.",
    codeType: "CMD",
    code: "ipconfig /flushdns && ipconfig /release && ipconfig /renew"
  },
  reset_winsock: {
    title: "Reset Windows Sockets (Winsock)",
    description: "Resets the Winsock Catalog to clean defaults, recovering system network connectivity.",
    codeType: "CMD (Run as Admin)",
    code: "netsh winsock reset"
  },
  reset_firewall: {
    title: "Reset Windows Defender Firewall",
    description: "Clears all custom inbound and outbound security rules and restores default firewall policies.",
    codeType: "CMD (Run as Admin)",
    code: "netsh advfirewall reset"
  },
  stop_updates: {
    title: "Stop Windows Updates",
    description: "Fully disables and stops the Windows Update Service (wuauserv), Background Intelligent Transfer Service (bits), and Update Orchestrator (UsoSvc) to block automatic updates.",
    codeType: "PowerShell (Run as Admin)",
    code: "Stop-Service -Name wuauserv, bits, UsoSvc -Force\nSet-Service -Name wuauserv -StartupType Disabled\nSet-Service -Name bits -StartupType Disabled\nSet-Service -Name UsoSvc -StartupType Disabled\nreg add \"HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU\" /v NoAutoUpdate /t REG_DWORD /d 1 /f\nreg add \"HKLM\\SYSTEM\\CurrentControlSet\\Services\\WaaSMedicSvc\" /v Start /t REG_DWORD /d 4 /f"
  },
  resume_updates: {
    title: "Resume Windows Updates",
    description: "Enables and restarts all Windows Update core background services and clears policy registry flags to default states.",
    codeType: "PowerShell (Run as Admin)",
    code: "reg delete \"HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU\" /v NoAutoUpdate /f\nreg add \"HKLM\\SYSTEM\\CurrentControlSet\\Services\\WaaSMedicSvc\" /v Start /t REG_DWORD /d 3 /f\nSet-Service -Name wuauserv -StartupType Manual\nSet-Service -Name bits -StartupType Manual\nSet-Service -Name UsoSvc -StartupType Manual\nStart-Service -Name wuauserv, bits, UsoSvc"
  },
  security_only_updates: {
    title: "Enable Security Updates Only",
    description: "Configures Windows Updates to bypass driver offers, defer Feature Updates by 365 days, and Quality Updates by 4 days. Restricts updates to security and definition patches only.",
    codeType: "PowerShell (Run as Admin)",
    code: "reg add \"HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\" /v ExcludeWUDriversInQualityUpdate /t REG_DWORD /d 1 /f\nreg add \"HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\" /v DeferFeatureUpdates /t REG_DWORD /d 1 /f\nreg add \"HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\" /v DeferFeatureUpdatesPeriodInDays /t REG_DWORD /d 365 /f\nreg add \"HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\" /v DeferQualityUpdates /t REG_DWORD /d 1 /f\nreg add \"HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\" /v DeferQualityUpdatesPeriodInDays /t REG_DWORD /d 4 /f\nreg delete \"HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU\" /v NoAutoUpdate /f\nreg add \"HKLM\\SYSTEM\\CurrentControlSet\\Services\\WaaSMedicSvc\" /v Start /t REG_DWORD /d 3 /f\nSet-Service -Name wuauserv -StartupType Manual\nSet-Service -Name bits -StartupType Manual\nSet-Service -Name UsoSvc -StartupType Manual\nStart-Service -Name wuauserv, bits, UsoSvc"
  },

  // Windows Debloater
  create_restore_point: {
    title: "Create System Restore Point",
    description: "Registers a system state checkpoint description so you can roll back system settings if needed.",
    codeType: "PowerShell (Run as Admin)",
    code: "start powershell -NoExit -Command \"Enable-ComputerRestore -Drive C:; Checkpoint-Computer -Description 'VenkatPulseBeforeRepair' -RestorePointType MODIFY_SETTINGS\""
  },
  disable_telemetry: {
    title: "Disable Diagnostics Telemetry",
    description: "Stops tracking services and adds registry flags to prevent telemetry transmission to Microsoft.",
    codeType: "CMD / Registry (Run as Admin)",
    code: "reg add \"HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection\" /v AllowTelemetry /t REG_DWORD /d 0 /f"
  },
  disable_cortana: {
    title: "Disable Cortana Integration",
    description: "Disables Cortana voice search and stops background assistant indexing.",
    codeType: "CMD / Registry (Run as Admin)",
    code: "reg add \"HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Windows Search\" /v AllowCortana /t REG_DWORD /d 0 /f"
  },
  disable_onedrive: {
    title: "Disable OneDrive Integration",
    description: "Unlinks OneDrive file sync client and prevents it from loading on user login.",
    codeType: "CMD / Registry (Run as Admin)",
    code: "reg add \"HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\OneDrive\" /v DisableFileSyncNGSC /t REG_DWORD /d 1 /f"
  },
  disable_xbox: {
    title: "Disable Xbox Services",
    description: "Stops and disables Xbox game monitoring and live authentication services in the background.",
    codeType: "PowerShell (Run as Admin)",
    code: "Stop-Service XblAuthManager,XblGameSave,XboxNetApiSvc; Set-Service XblAuthManager -StartupType Disabled; Set-Service XblGameSave -StartupType Disabled; Set-Service XboxNetApiSvc -StartupType Disabled"
  },
  uninstall_bloatware: {
    title: "Uninstall Preinstalled Bloatware Apps",
    description: "Removes default consumer apps (XboxApp, ZuneMusic, BingNews, Solitaire Collection) using AppxPackage parameters.",
    codeType: "PowerShell (Run as Admin)",
    code: "start powershell -NoExit -Command \"Get-AppxPackage -AllUsers *XboxApp*,*ZuneMusic*,*BingNews*,*Office.OneNote*,*SolitaireCollection* | Remove-AppxPackage -ErrorAction SilentlyContinue\""
  },

  // User Tools (GUI consoles)
  lusrmgr: {
    title: "Local Users & Groups Manager",
    description: "Launches the Administrative Users and Groups MMC console (lusrmgr.msc).",
    codeType: "Windows Run Command",
    code: "lusrmgr.msc"
  },
  uac_settings: {
    title: "User Account Control Settings",
    description: "Opens UAC Control slider interface to adjust permissions warnings.",
    codeType: "Windows Run Command",
    code: "useraccountcontrolsettings.exe"
  },
  sys_properties: {
    title: "System Properties Dialog",
    description: "Opens Advanced System Properties for virtual memory swap settings (sysdm.cpl).",
    codeType: "Windows Run Command",
    code: "sysdm.cpl"
  },
  comp_mgmt: {
    title: "Computer Management Console",
    description: "Launches MMC for Disk Management, Event Viewer, and Services (compmgmt.msc).",
    codeType: "Windows Run Command",
    code: "compmgmt.msc"
  },
  gp_editor: {
    title: "Local Group Policy Editor",
    description: "Launches the policies console to customize system rules (gpedit.msc).",
    codeType: "Windows Run Command",
    code: "gpedit.msc"
  },
  reg_editor: {
    title: "Windows Registry Editor",
    description: "Launches the registry system browser (regedit.exe).",
    codeType: "Windows Run Command",
    code: "regedit.exe"
  },

  // Migration Tools
  backup_printers: {
    title: "Export Printer Drivers & Queues",
    description: "Runs PrintBrm printer migration to backup all printer settings to C:\\PulseBackup.",
    codeType: "CMD (Run as Admin)",
    code: "start cmd /k \"if not exist C:\\PulseBackup mkdir C:\\PulseBackup && C:\\Windows\\System32\\Spool\\Tools\\PrintBrm.exe -b -f C:\\PulseBackup\\PrinterBackup.printerExport\""
  },
  restore_printers: {
    title: "Import Printer Drivers & Queues",
    description: "Restores print configurations and drivers from C:\\PulseBackup using PrintBrm.",
    codeType: "CMD (Run as Admin)",
    code: "if not exist C:\\PulseBackup\\PrinterBackup.printerExport (echo Backup file C:\\PulseBackup\\PrinterBackup.printerExport not found!) else (C:\\Windows\\System32\\Spool\\Tools\\PrintBrm.exe -r -f C:\\PulseBackup\\PrinterBackup.printerExport)"
  },
  activate_windows: {
    title: "Windows HWID Activation",
    description: "Launches the official Microsoft Activation Scripts (MAS) to permanently activate Windows using hardware ID.",
    codeType: "PowerShell (Run as Admin)",
    code: "start powershell -NoExit -Command \"& ([ScriptBlock]::Create((irm https://get.activated.win))) /HWID\""
  },
  activate_office: {
    title: "Office Ohook Activation",
    description: "Launches the official Microsoft Activation Scripts (MAS) to activate Office applications using the Ohook method.",
    codeType: "PowerShell (Run as Admin)",
    code: "start powershell -NoExit -Command \"& ([ScriptBlock]::Create((irm https://get.activated.win))) /Ohook\""
  },
  activate_kms: {
    title: "Universal Online KMS Activation",
    description: "Launches the official Microsoft Activation Scripts (MAS) to activate Windows and Office via KMS.",
    codeType: "PowerShell (Run as Admin)",
    code: "start powershell -NoExit -Command \"& ([ScriptBlock]::Create((irm https://get.activated.win))) /K-WindowsOffice\""
  },
  activate_kms_uninstall: {
    title: "Uninstall Online KMS Setup",
    description: "Uninstalls Online KMS setup from the device, cleaning background tasks and registry flags.",
    codeType: "PowerShell (Run as Admin)",
    code: "start powershell -NoExit -Command \"& ([ScriptBlock]::Create((irm https://get.activated.win))) /K-Uninstall\""
  },
  download_nirsoft: {
    title: "Download & Extract NirLauncher Suite",
    description: "Downloads the NirSoft utilities bundle zip file and extracts it to C:\\NirLauncher automatically.",
    codeType: "Python / Command (Run as Admin)",
    code: "start cmd /k python install_nirsoft.py download"
  },
  launch_nirsoft: {
    title: "Launch NirLauncher Suite",
    description: "Launches the portable NirLauncher.exe main panel utility.",
    codeType: "Windows Command",
    code: "C:\\NirLauncher\\NirLauncher.exe"
  },
  download_mailpv: {
    title: "Download & Run MailPassView",
    description: "Downloads and extracts NirSoft MailPassView tool to recover mail credentials, then runs it.",
    codeType: "Python / Command (Run as Admin)",
    code: "start cmd /k python install_nirsoft.py mailpv"
  },
  launch_mailpv: {
    title: "Launch MailPassView",
    description: "Launches MailPassView to view stored mail password details.",
    codeType: "Windows Command",
    code: "C:\\NirLauncher\\mailpv\\mailpv.exe"
  },
  launch_info_specs: {
    title: "Launch msinfo32 System Specifications",
    description: "Opens Windows System Information panel detailing complete hardware resources and system components configurations.",
    codeType: "Windows Command",
    code: "msinfo32.exe"
  },
  generate_health_report: {
    title: "Generate System Performance Diagnostic Report",
    description: "Triggers Windows Reliability and Performance Monitor tool to collect telemetry data and construct a local health report.",
    codeType: "Windows Command",
    code: "perfmon.exe /report"
  },
  generate_battery_report: {
    title: "Generate Power Battery Health Report",
    description: "Generates HTML battery capacity report using Windows powercfg utilities and displays it automatically on Desktop.",
    codeType: "CMD (Run as Admin)",
    code: "powercfg /batteryreport /output %userprofile%\\Desktop\\battery-report.html && start %userprofile%\\Desktop\\battery-report.html"
  },
  run_quick_scan: {
    title: "Windows Defender Quick Scan",
    description: "Runs standard fast scan sweep targeting active RAM, registry objects, and startup folders.",
    codeType: "PowerShell (Run as Admin)",
    code: "powershell -NoExit -Command \"Start-MpScan -ScanType QuickScan\""
  },
  deep_full_scan: {
    title: "Windows Defender Deep Scan",
    description: "Runs exhaustive full system scan on all storage drives in the background.",
    codeType: "PowerShell (Run as Admin)",
    code: "powershell -NoExit -Command \"Start-MpScan -ScanType FullScan\""
  },
  update_defender_db: {
    title: "Update Windows Defender Signatures Database",
    description: "Force queries online update mirrors to pull the latest security definitions.",
    codeType: "PowerShell (Run as Admin)",
    code: "powershell -NoExit -Command \"Update-MpSignature\""
  },
  wifi_password_decoder: {
    title: "Recover Local WiFi Profiles Password Keys",
    description: "Queries netsh profiles database to decode security key content configuration of saved WLAN connections.",
    codeType: "PowerShell (Run as Admin)",
    code: "powershell -NoExit -Command \"netsh wlan show profiles | Select-String 'All User Profile' | ForEach-Object { $name = $_.Line.Split(':')[1].Trim(); $key = (netsh wlan show profile name=$name key=clear | Select-String 'Key Content' | ForEach-Object { $_.Line.Split(':')[1].Trim() }); [PSCustomObject]@{Profile=$name; Password=$key} } | Out-String\""
  },
  open_credential_manager: {
    title: "Open Windows Credential Manager Console",
    description: "Opens classic Control Panel UI keymgr.dll to manage Windows and Web vault credentials.",
    codeType: "Windows Command",
    code: "control.exe keymgr.dll"
  },
  export_appdata: {
    title: "Export User Roaming AppData Profile Backup",
    description: "Copies %APPDATA% directories to C:\\PulseBackup\\AppDataBackup using multi-threaded Robocopy.",
    codeType: "PowerShell (Run as Admin)",
    code: "powershell -NoExit -Command \"Robocopy $env:APPDATA C:\\PulseBackup\\AppDataBackup /E /MT:8\""
  },
  import_appdata: {
    title: "Import User Roaming AppData Profile Backup",
    description: "Restores user configurations from C:\\PulseBackup\\AppDataBackup folder back to roaming app data directories.",
    codeType: "PowerShell (Run as Admin)",
    code: "powershell -NoExit -Command \"Robocopy C:\\PulseBackup\\AppDataBackup $env:APPDATA /E /MT:8\""
  },
  office_quick_repair: {
    title: "Office Suite Quick Repair Protocol",
    description: "Launches MS ClickToRun engine to scan and verify installation files offline without modifying network properties.",
    codeType: "PowerShell (Run as Admin)",
    code: "powershell -ExecutionPolicy Bypass -NoExit -Command \"$p = 'C:\\Program Files\\Common Files\\microsoft shared\\ClickToRun\\OfficeClickToRun.exe'; if (!(Test-Path $p)) { $p = 'C:\\Program Files (x86)\\Common Files\\microsoft shared\\ClickToRun\\OfficeClickToRun.exe' }; if (Test-Path $p) { Start-Process $p -ArgumentList 'scenario=Repair platform=x64 culture=en-us ForceAppShutdown=True' -Wait } else { Write-Host 'Error: Office ClickToRun service not found.' -ForegroundColor Red }\""
  },
  office_online_repair: {
    title: "Office Suite Online Repair Sweep",
    description: "Performs full download-based reinstall sweep of Office deployment resources to fix deep system registry breaks.",
    codeType: "PowerShell (Run as Admin)",
    code: "powershell -ExecutionPolicy Bypass -NoExit -Command \"$p = 'C:\\Program Files\\Common Files\\microsoft shared\\ClickToRun\\OfficeClickToRun.exe'; if (!(Test-Path $p)) { $p = 'C:\\Program Files (x86)\\Common Files\\microsoft shared\\ClickToRun\\OfficeClickToRun.exe' }; if (Test-Path $p) { Start-Process $p -ArgumentList 'scenario=Repair platform=x64 culture=en-us RepairType=FullRepair ForceAppShutdown=True' -Wait } else { Write-Host 'Error: Office ClickToRun service not found.' -ForegroundColor Red }\""
  },
  outlook_safe_mode: {
    title: "Start Microsoft Outlook in Safe Mode",
    description: "Launches Outlook with all add-ins and custom toolbars disabled to check configuration conflicts.",
    codeType: "PowerShell",
    code: "powershell -ExecutionPolicy Bypass -NoExit -Command \"try { Start-Process outlook.exe -ArgumentList '/safe' } catch { Write-Host 'Error: Outlook is not installed or registered on this machine.' -ForegroundColor Red }\""
  },
  outlook_reset_nav: {
    title: "Reset Outlook Navigation Pane Layout",
    description: "Clears and regenerates the navigation pane layout configuration settings.",
    codeType: "PowerShell",
    code: "powershell -ExecutionPolicy Bypass -NoExit -Command \"try { Start-Process outlook.exe -ArgumentList '/resetnavpane' } catch { Write-Host 'Error: Outlook is not installed.' -ForegroundColor Red }\""
  },
  outlook_reset_folders: {
    title: "Restore Outlook Default Folder Directories",
    description: "Restores missing default folders in the data store for the active profile.",
    codeType: "PowerShell",
    code: "powershell -ExecutionPolicy Bypass -NoExit -Command \"try { Start-Process outlook.exe -ArgumentList '/resetfolders' } catch { Write-Host 'Error: Outlook is not installed.' -ForegroundColor Red }\""
  },
  outlook_reset_bar: {
    title: "Reset Outlook Shortcut Bar",
    description: "Clears custom shortcut entries from the Outlook bar layout configuration.",
    codeType: "PowerShell",
    code: "powershell -ExecutionPolicy Bypass -NoExit -Command \"try { Start-Process outlook.exe -ArgumentList '/resetoutlookbar' } catch { Write-Host 'Error: Outlook is not installed.' -ForegroundColor Red }\""
  },
  outlook_mail_setup: {
    title: "Outlook Mail Control Setup Console (mlcfg32)",
    description: "Launches the classic Office Mail Setup console to manage data files and active profiles directly.",
    codeType: "PowerShell",
    code: "powershell -ExecutionPolicy Bypass -NoExit -Command \"try { Start-Process control.exe -ArgumentList 'mlcfg32.cpl' } catch { Write-Host 'Error: Mail Setup control panel (mlcfg32.cpl) could not be opened.' -ForegroundColor Red }\""
  },
  outlook_scanpst_auto: {
    title: "Run ScanPST (Automated File Recovery)",
    description: "Locates scanpst.exe utility on drive C: and starts it in diagnostic mode to repair corrupted PST/OST files.",
    codeType: "PowerShell (Run as Admin)",
    code: "powershell -NoExit -Command \"$path = (Get-ChildItem -Path 'C:\\Program Files' -Filter 'scanpst.exe' -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1).FullName; if ($path) { Start-Process $path -ArgumentList '/force' } else { Write-Host 'ScanPST not found. Please browse manually.' }\""
  },
  outlook_scanpst_browse: {
    title: "Browse Outlook Installation Folder",
    description: "Opens Explorer window pointing to standard Office16 installation directories where ScanPST utility resides.",
    codeType: "PowerShell",
    code: "powershell -ExecutionPolicy Bypass -NoExit -Command \"if (Test-Path 'C:\\Program Files\\Microsoft Office\\root\\Office16') { Start-Process explorer.exe 'C:\\Program Files\\Microsoft Office\\root\\Office16' } else { Write-Host 'Office16 folder not found.' -ForegroundColor Red }\""
  },
  outlook_open_data: {
    title: "Open Outlook Local Data Files Directory",
    description: "Opens user's Outlook Files folder containing PST/OST database archives.",
    codeType: "PowerShell",
    code: "powershell -ExecutionPolicy Bypass -NoExit -Command \"if (Test-Path '$env:USERPROFILE\\Documents\\Outlook Files') { Start-Process explorer.exe '$env:USERPROFILE\\Documents\\Outlook Files' } else { Write-Host 'Outlook Files folder not found.' -ForegroundColor Red }\""
  },
  outlook_backup_pst: {
    title: "Backup Local Outlook Data Files",
    description: "Performs quick file replication copy of OST and PST database storage to C:\\PulseBackup\\OutlookBackup folder.",
    codeType: "PowerShell (Run as Admin)",
    code: "powershell -NoExit -Command \"if (!(Test-Path C:\\PulseBackup\\OutlookBackup)) { New-Item -ItemType Directory -Path C:\\PulseBackup\\OutlookBackup -Force }; Copy-Item -Path $env:LOCALAPPDATA\\Microsoft\\Outlook\\* -Destination C:\\PulseBackup\\OutlookBackup\\ -Force -ErrorAction SilentlyContinue\""
  },
  outlook_backup_folder: {
    title: "Backup AppData Outlook Configurations",
    description: "Copies Outlook profiles directories to C:\\PulseBackup\\OutlookDataBackup folder.",
    codeType: "PowerShell (Run as Admin)",
    code: "powershell -NoExit -Command \"if (!(Test-Path C:\\PulseBackup\\OutlookDataBackup)) { New-Item -ItemType Directory -Path C:\\PulseBackup\\OutlookDataBackup -Force }; Copy-Item -Path $env:APPDATA\\Microsoft\\Outlook\\* -Destination C:\\PulseBackup\\OutlookDataBackup\\ -Force -ErrorAction SilentlyContinue\""
  },
  outlook_new_profile: {
    title: "Create New Outlook Profile Configuration",
    description: "Opens mail setup control panel window to create a fresh profile database.",
    codeType: "PowerShell",
    code: "powershell -ExecutionPolicy Bypass -NoExit -Command \"try { Start-Process control.exe -ArgumentList 'mlcfg32.cpl' } catch { Write-Host 'Error: Mail Setup control panel could not be opened.' -ForegroundColor Red }\""
  },
  winword_safe_mode: {
    title: "Launch Microsoft Word in Safe Mode",
    description: "Launches MS Word bypassing startup templates and registry load hooks.",
    codeType: "PowerShell",
    code: "powershell -ExecutionPolicy Bypass -NoExit -Command \"try { Start-Process winword.exe -ArgumentList '/safe' } catch { Write-Host 'Error: Word is not installed.' -ForegroundColor Red }\""
  },
  excel_safe_mode: {
    title: "Launch Microsoft Excel in Safe Mode",
    description: "Launches MS Excel with plugins and macros loading disabled.",
    codeType: "PowerShell",
    code: "powershell -ExecutionPolicy Bypass -NoExit -Command \"try { Start-Process excel.exe -ArgumentList '/safe' } catch { Write-Host 'Error: Excel is not installed.' -ForegroundColor Red }\""
  },
  powerpnt_safe_mode: {
    title: "Launch Microsoft PowerPoint in Safe Mode",
    description: "Launches MS PowerPoint to recover presentation layouts from crashing addons.",
    codeType: "PowerShell",
    code: "powershell -ExecutionPolicy Bypass -NoExit -Command \"try { Start-Process powerpnt.exe -ArgumentList '/safe' } catch { Write-Host 'Error: PowerPoint is not installed.' -ForegroundColor Red }\""
  },
  driver_scan: {
    title: "Scan Local Hardware Devices (PnpUtil)",
    description: "Forces PNP stack updates scan on local hardware components buses.",
    codeType: "CMD (Run as Admin)",
    code: "pnputil /scan-devices"
  },
  driver_upgrade: {
    title: "Force Windows Update Driver Upgrades",
    description: "Uses PSWindowsUpdate modules to download and install missing vendor package updates.",
    codeType: "PowerShell (Run as Admin)",
    code: "powershell -ExecutionPolicy Bypass -NoExit -Command \"try { Write-Host 'Setting up PSWindowsUpdate module...' -ForegroundColor Cyan; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Set-PSRepository -Name PSGallery -InstallationPolicy Trusted -ErrorAction SilentlyContinue; Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force -ErrorAction SilentlyContinue; Install-Module -Name PSWindowsUpdate -Force -SkipPublisherCheck -ErrorAction SilentlyContinue; Import-Module PSWindowsUpdate -ErrorAction Stop; Write-Host 'Checking and installing driver updates...' -ForegroundColor Cyan; Get-WindowsUpdate -Category 'Drivers' -Install -AcceptAll -AutoReboot; } catch { Write-Host 'Error: ' $_.Exception.Message -ForegroundColor Red; Write-Host 'Failed to install or run PSWindowsUpdate. Make sure you are connected to the Internet.' -ForegroundColor Red; }\""
  },
  driver_backup: {
    title: "Backup Hardware Drivers to C:\\PulseBackup",
    description: "Exports all active third-party drivers to C:\\PulseBackup\\DriversBackup folder using DISM utility.",
    codeType: "CMD (Run as Admin)",
    code: "if not exist C:\\PulseBackup\\DriversBackup (mkdir C:\\PulseBackup\\DriversBackup) && dism /online /export-driver /destination:\"C:\\PulseBackup\\DriversBackup\""
  },
  driver_restore: {
    title: "Restore Hardware Drivers from C:\\PulseBackup",
    description: "Imports and installs third-party drivers from drivers backup directories in C:\\PulseBackup.",
    codeType: "CMD (Run as Admin)",
    code: "if not exist C:\\PulseBackup\\DriversBackup (echo Backup folder C:\\PulseBackup\\DriversBackup not found!) else (pnputil /add-driver \"C:\\PulseBackup\\DriversBackup\\*.inf\" /subdirs /install)"
  },
  user_netplwiz: {
    title: "Launch netplwiz Account Panel",
    description: "Launches Advanced User Accounts configuration panel to set system auto-logins and groups.",
    codeType: "Windows Command",
    code: "netplwiz.exe"
  },
  create_godmode: {
    title: "Create Windows 'God Mode' Dashboard Folder",
    description: "Creates folder on Desktop with the shell directory GUID to access all Windows Control Panel tools in a single place.",
    codeType: "PowerShell",
    code: "powershell -Command \"New-Item -ItemType Directory -Path '$home\\Desktop\\GodMode.{ED7BA470-8E54-465E-825C-99712043E01C}' -Force\""
  },
  net_scan_subnet: {
    title: "Scan Network Subnet Nodes (ARP Table)",
    description: "Queries Address Resolution Protocol cache table to display local hosts and IP addresses.",
    codeType: "CMD",
    code: "arp -a"
  },
  net_recycle_adapters: {
    title: "Force Recycle Network Adapters",
    description: "Restarts all active network interfaces to recover connection link sockets.",
    codeType: "PowerShell (Run as Admin)",
    code: "powershell -NoExit -Command \"Get-NetAdapter | Restart-NetAdapter\""
  },
  net_enable_rdp: {
    title: "Enable Inbound Remote Desktop (RDP)",
    description: "Enables Terminal Server registry properties and activates Remote Desktop inbound firewall rules.",
    codeType: "PowerShell (Run as Admin)",
    code: "powershell -NoExit -Command \"Set-ItemProperty -Path 'HKLM:\\System\\CurrentControlSet\\Control\\Terminal Server' -Name 'fDenyTSConnections' -Value 0; Enable-NetFirewallRule -DisplayGroup 'Remote Desktop'\""
  },
  disk_trim_ssd: {
    title: "Force SSD Block Re-Trim Optimization",
    description: "Initiates native Windows trim sweeps on drive C: to recover SSD storage block speed.",
    codeType: "Windows Command",
    code: "defrag C: /L"
  },
  disk_defrag: {
    title: "Run Disk Storage Fragment Optimizer",
    description: "Initiates standard space optimization defragmentation cycles on drive C:.",
    codeType: "Windows Command",
    code: "defrag C: /O"
  },
  disk_chkdsk: {
    title: "Check Disk Drive Integrity (Chkdsk)",
    description: "Runs the Check Disk utility on drive C: to find and fix file system errors and bad sectors.",
    codeType: "CMD (Run as Admin)",
    code: "chkdsk C: /f /r"
  },
  disk_heaviest_files: {
    title: "Map Top 10 Heaviest Files",
    description: "Scans drive C: to find and display the 10 largest files consuming storage space.",
    codeType: "PowerShell (Run as Admin)",
    code: "Get-ChildItem -Path C:\\ -File -Recurse -ErrorAction SilentlyContinue | Sort-Object Length -Descending | Select-Object -First 10 | Format-Table @{Label='File Name';Expression={$_.Name}}, @{Label='Size (MB)';Expression={[Math]::Round($_.Length/1MB, 2)}}, @{Label='Folder';Expression={$_.DirectoryName}}"
  },
  restart_tally: {
    title: "Restart Tally Gateway Server Service",
    description: "Restarts Tally ERP gateway services to recover server connections.",
    codeType: "CMD (Run as Admin)",
    code: "net stop 'Tally-Gateway-Server' && net start 'Tally-Gateway-Server'"
  },
  purge_temp_cache: {
    title: "Purge System Caches & Temp Directories",
    description: "Deletes all files in C:\\Windows\\Temp, Local AppData Temp, and Windows Prefetch indexes to clear junk storage.",
    codeType: "PowerShell (Run as Admin)",
    code: "powershell -NoExit -Command \"Remove-Item -Path 'C:\\Windows\\Temp\\*' -Recurse -Force; Remove-Item -Path 'C:\\Users\\*\\AppData\\Local\\Temp\\*' -Recurse -Force; Remove-Item -Path 'C:\\Windows\\Prefetch\\*' -Recurse -Force\""
  },
  explorer_restart: {
    title: "Restart Windows Explorer Shell",
    description: "Terminates active explorer.exe task instances and restarts the Windows graphical shell.",
    codeType: "CMD (Run as Admin)",
    code: "taskkill /f /im explorer.exe && start explorer.exe"
  },
  icon_cache_rebuild: {
    title: "Rebuild Windows System Icon Cache database",
    description: "Terminates Explorer shell, purges local IconCache.db file, and restarts system GUI to repair blank/broken desktop icons.",
    codeType: "CMD (Run as Admin)",
    code: "taskkill /f /im explorer.exe && del /a /q /f %localappdata%\\IconCache.db && start explorer.exe"
  },
  run_robocopy: {
    title: "Robocopy Mirror sync",
    description: "Runs multi-threaded Robocopy mirroring from source to target directory path.",
    codeType: "CMD (Run as Admin)",
    code: "robocopy \"[Source]\" \"[Target]\" /MIR /MT:8"
  }
};

// 8. Admin System Toolbox Modal Controllers
let activeToolKey = null;

function openToolModal(toolKey) {
  const tool = TOOLBOX_DATA[toolKey];
  if (!tool) return;

  activeToolKey = toolKey;

  document.getElementById("modal-tool-title").innerText = tool.title;
  document.getElementById("modal-tool-description").innerText = tool.description;
  document.getElementById("code-type-label").innerText = tool.codeType;
  document.getElementById("modal-tool-code").innerText = tool.code;

  // GPO settings display
  const gpoBox = document.getElementById("modal-gpo-note-box");
  if (tool.gpoPath && tool.gpoSetting) {
    gpoBox.style.display = "block";
    document.getElementById("modal-gpo-note-text").innerHTML = `
      <strong>Policy Path:</strong> <code>${tool.gpoPath}</code><br>
      <strong>Action:</strong> ${tool.gpoSetting}
    `;
  } else {
    gpoBox.style.display = "none";
  }

  // Reset execution status
  const statusEl = document.getElementById("modal-exec-status");
  statusEl.style.display = "none";
  statusEl.innerText = "";
  statusEl.className = "";

  // Apply button display
  const applyBtn = document.getElementById("modal-apply-btn");
  if (tool.launchUri) {
    applyBtn.style.display = "none";
  } else {
    applyBtn.style.display = "inline-flex";
    applyBtn.disabled = false;
  }

  // Launch button display
  const launchBtn = document.getElementById("modal-launch-btn");
  if (tool.launchUri) {
    launchBtn.style.display = "inline-flex";
  } else {
    launchBtn.style.display = "none";
  }

  // Show Modal
  document.getElementById("tool-modal").style.display = "flex";
  lucide.createIcons();
}

function closeToolModal() {
  document.getElementById("tool-modal").style.display = "none";
  activeToolKey = null;
}

function copyToolCommand() {
  const codeEl = document.getElementById("modal-tool-code");
  const copyBtn = document.querySelector(".btn-copy-code");

  if (!codeEl) return;

  navigator.clipboard.writeText(codeEl.innerText).then(() => {
    // Show temporary feedback
    const originalText = copyBtn.innerHTML;
    copyBtn.innerHTML = `<i data-lucide="check" style="width:14px; height:14px; vertical-align: middle;"></i> Copied!`;
    lucide.createIcons();

    setTimeout(() => {
      copyBtn.innerHTML = originalText;
      lucide.createIcons();
    }, 2000);
  }).catch(err => {
    console.error("Failed to copy code: ", err);
  });
}

function launchSettingsUri() {
  if (!activeToolKey) return;
  const tool = TOOLBOX_DATA[activeToolKey];
  if (tool && tool.launchUri) {
    // Attempt protocol launch
    window.location.href = tool.launchUri;
  }
}

// 9. API One-Click Executor
function executeLocalFix() {
  if (!activeToolKey) return;
  
  const statusEl = document.getElementById("modal-exec-status");
  const applyBtn = document.getElementById("modal-apply-btn");
  const tool = TOOLBOX_DATA[activeToolKey];
  
  statusEl.style.display = "inline-block";
  statusEl.className = "";
  statusEl.style.color = "var(--state-warning)";
  statusEl.innerText = "⌛ Applying fix to local system...";
  applyBtn.disabled = true;

  fetch(API_BASE + '/api/execute', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ toolKey: activeToolKey })
  })
  .then(res => {
    if (!res.ok) {
      return res.json().then(data => { throw new Error(data.error || 'Server error'); });
    }
    return res.json();
  })
  .then(data => {
    statusEl.style.color = "var(--state-success)";
    statusEl.innerText = "✓ Fix applied successfully!";
    applyBtn.disabled = false;
    
    // Log in database
    logMaintenanceAction(`Applied Fix: ${tool.title}`, "Resolved", `Executed one-click fix automatically.`);
  })
  .catch(err => {
    statusEl.style.color = "var(--state-danger)";
    statusEl.innerText = `✕ Error: ${err.message || 'Make sure the server runs as Admin.'}`;
    applyBtn.disabled = false;
    console.error("Execute local fix error:", err);
  });
}

function formatUptime(seconds) {
  const d = Math.floor(seconds / (3600*24));
  const h = Math.floor(seconds % (3600*24) / 3600);
  const m = Math.floor(seconds % 3600 / 60);
  
  const dDisplay = d > 0 ? d + "d " : "";
  const hDisplay = h > 0 ? h + "h " : "";
  const mDisplay = m > 0 ? m + "m" : "0m";
  return dDisplay + hDisplay + mDisplay;
}

// 10. Connection Status Checker
// 10. Connection Status Checker
function checkServerStatus() {
  const banner = document.getElementById("status-banner");
  const heroBadge = document.querySelector(".hero-card .badge"); // the "System Online" badge
  const toolboxBadge = document.querySelector(".toolbox-card .badge"); // the "Administrator Level" badge
  const selfDestructBtn = document.getElementById("self-destruct-btn");
  
  fetch(API_BASE + '/api/status')
    .then(res => {
      if (!res.ok) throw new Error("Offline");
      return res.json();
    })
    .then(data => {
      if (data.status === 'online') {
        if (!isServerOnline) {
          isServerOnline = true;
          fetchGeoLocation();
        }
        if (selfDestructBtn) selfDestructBtn.style.display = "inline-flex";
        
        // Update live host telemetry
        if (data.hostname) {
          const deviceNameEl = document.getElementById("sys-device-name");
          if (deviceNameEl) deviceNameEl.innerText = data.hostname;
        }
        if (data.osName) {
          const osVerEl = document.getElementById("sys-os-ver");
          if (osVerEl) osVerEl.innerText = data.osName;
        }
        if (data.uptime) {
          const uptimeEl = document.getElementById("sys-uptime");
          if (uptimeEl) uptimeEl.innerText = formatUptime(data.uptime);
        }

        if (data.isAdmin) {
          // Connected & Admin
          if (banner) banner.style.display = "none";
          if (heroBadge) {
            heroBadge.className = "badge badge-success";
            heroBadge.innerHTML = `<i data-lucide="check-circle" style="width:12px; height:12px; margin-right:4px; vertical-align: middle;"></i> Connected (Admin)`;
          }
          if (toolboxBadge) {
            toolboxBadge.className = "badge badge-success";
            toolboxBadge.innerHTML = `<i data-lucide="shield" style="width:12px; height:12px; margin-right:4px; vertical-align: middle;"></i> Admin Mode Active`;
          }
        } else {
          // Connected but non-admin
          if (banner) {
            banner.style.display = "flex";
            banner.className = "status-banner warning";
            const descEl = banner.querySelector(".banner-desc");
            if (descEl) {
              descEl.innerHTML = `Server is running but <strong>does NOT have Administrator rights</strong>. One-click repairs will fail. Please close this window, double-click <strong style="color: var(--accent-cyan);">main.exe</strong>, and click <strong>'Yes'</strong> to the UAC prompt (Image 2).`;
            }
          }
          if (heroBadge) {
            heroBadge.className = "badge badge-warning";
            heroBadge.innerHTML = `<i data-lucide="alert-triangle" style="width:12px; height:12px; margin-right:4px; vertical-align: middle;"></i> Connected (Non-Admin)`;
          }
          if (toolboxBadge) {
            toolboxBadge.className = "badge badge-warning";
            toolboxBadge.innerHTML = `<i data-lucide="shield-alert" style="width:12px; height:12px; margin-right:4px; vertical-align: middle;"></i> Elevation Required`;
          }
        }
        lucide.createIcons();
      }
    })
    .catch(err => {
      console.warn("Local API server is offline:", err);
      isServerOnline = false;
      if (selfDestructBtn) selfDestructBtn.style.display = "none";
      // Offline mode
      if (banner) {
        banner.style.display = "flex";
        banner.className = "status-banner danger";
        const descEl = banner.querySelector(".banner-desc");
        if (descEl) {
          descEl.innerHTML = `Local Repair Server is <strong>OFFLINE</strong>. One-click repairs are disabled. Please <a href="https://github.com/venkat-tools/puls/archive/refs/heads/main.zip" style="color: var(--accent-cyan); font-weight: bold; text-decoration: underline;">Download the Repair Client (ZIP)</a>, extract it, double-click <strong style="color: var(--accent-cyan);">main.exe</strong> and click <strong>'Yes'</strong> to UAC.`;
        }
      }
      if (heroBadge) {
        heroBadge.className = "badge badge-danger";
        heroBadge.innerHTML = `<i data-lucide="x-circle" style="width:12px; height:12px; margin-right:4px; vertical-align: middle;"></i> Server Offline`;
      }
      if (toolboxBadge) {
        toolboxBadge.className = "badge badge-danger";
        toolboxBadge.innerHTML = `<i data-lucide="shield-off" style="width:12px; height:12px; margin-right:4px; vertical-align: middle;"></i> Server Offline`;
      }
      lucide.createIcons();
    });
}

// 10b. Self-Destruct Trigger
function triggerSelfDestruct() {
  if (!confirm("Warning: This will stop the local repair server and completely delete all its files (main.exe, server.js, index.html, styles.css, app.js, logo.png, etc.) from the client's system. Are you sure?")) {
    return;
  }
  
  fetch(API_BASE + '/api/self-destruct', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  })
  .then(res => res.json())
  .then(data => {
    alert("Self-destruct command sent successfully. The local files are being removed.");
    window.location.reload();
  })
  .catch(err => {
    console.error("Self-destruct failed:", err);
    alert("Failed to communicate with local server. Please delete the files manually.");
  });
}

// 11. Sub-Tab Navigation Router for nested panels
function switchSubTab(subTabId) {
  // Update sub-tab buttons UI
  const buttons = document.querySelectorAll(".sub-nav-tab");
  buttons.forEach(btn => {
    // Find onclick content to match subTabId
    if (btn.outerHTML.includes(subTabId)) {
      btn.classList.add("active");
    } else {
      btn.classList.remove("active");
    }
  });

  // Update sub-tab panels UI
  const panels = document.querySelectorAll(".sub-tab-panel");
  panels.forEach(panel => {
    if (panel.id === subTabId) {
      panel.classList.add("active");
    } else {
      panel.classList.remove("active");
    }
  });
}

// 12. App Downloader installation controller (Winget wrapper)
function installApp(appId) {
  // Find card button
  const card = document.getElementById("app-" + appId.split('.')[1]?.toLowerCase());
  const btn = card ? card.querySelector(".app-install-btn") : null;
  
  if (!btn) return;
  
  const originalHtml = btn.innerHTML;
  btn.disabled = true;
  btn.style.background = "var(--state-warning)";
  btn.innerHTML = `<i class="lucide-spinner" style="animation: spin 1.5s linear infinite; width:14px; height:14px; margin-right:4px;"></i> Installing...`;
  
  // Inject spinner style dynamically if not present
  if (!document.getElementById("spinner-keyframe-style")) {
    const style = document.createElement("style");
    style.id = "spinner-keyframe-style";
    style.innerHTML = "@keyframes spin { 100% { transform: rotate(360deg); } }";
    document.head.appendChild(style);
  }

  fetch(API_BASE + '/api/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ toolKey: 'winget_install', appId: appId })
  })
  .then(res => {
    if (!res.ok) {
      return res.json().then(data => { throw new Error(data.error || 'Install failed'); });
    }
    return res.json();
  })
  .then(data => {
    btn.style.background = "var(--state-success)";
    btn.style.borderColor = "var(--state-success)";
    btn.innerHTML = `<i data-lucide="check" style="width:14px; height:14px; margin-right:4px; vertical-align: middle;"></i> Installed!`;
    lucide.createIcons();
    
    // Log action
    logMaintenanceAction("App Install: " + appId, "Resolved", "Installed via winget package manager.");
  })
  .catch(err => {
    btn.style.background = "var(--state-danger)";
    btn.innerHTML = `<i data-lucide="x" style="width:14px; height:14px; margin-right:4px; vertical-align: middle;"></i> Failed`;
    lucide.createIcons();
    alert("Winget Installation Failed: " + err.message);
    
    setTimeout(() => {
      btn.disabled = false;
      btn.style.background = "";
      btn.style.borderColor = "";
      btn.innerHTML = originalHtml;
      lucide.createIcons();
    }, 4000);
  });
}

// 12b. Office Setup installation controller
function installOffice(versionId) {
  // Find card button
  const card = document.getElementById("office-" + versionId);
  const btn = card ? card.querySelector(".app-install-btn") : null;
  
  if (!btn) return;
  
  if (versionId === '2007') {
    // 2007 is redirect only
    window.open("https://archive.org/details/microsoft-office-2007-standard", "_blank");
    logMaintenanceAction("Downloaded Office 2007 Info", "Resolved", "Opened Office 2007 legacy download archive link.");
    return;
  }
  
  const originalHtml = btn.innerHTML;
  btn.disabled = true;
  btn.style.background = "var(--state-warning)";
  btn.innerHTML = `<i class="lucide-spinner" style="animation: spin 1.5s linear infinite; width:14px; height:14px; margin-right:4px; vertical-align: middle; display: inline-block;"></i> Installing...`;
  
  // Inject spinner style dynamically if not present
  if (!document.getElementById("spinner-keyframe-style")) {
    const style = document.createElement("style");
    style.id = "spinner-keyframe-style";
    style.innerHTML = "@keyframes spin { 100% { transform: rotate(360deg); } }";
    document.head.appendChild(style);
  }

  fetch(API_BASE + '/api/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ toolKey: 'install_office_' + versionId })
  })
  .then(res => {
    if (!res.ok) {
      return res.json().then(data => { throw new Error(data.error || 'Install failed'); });
    }
    return res.json();
  })
  .then(data => {
    btn.style.background = "var(--state-success)";
    btn.style.borderColor = "var(--state-success)";
    btn.innerHTML = `<i data-lucide="check" style="width:14px; height:14px; margin-right:4px; vertical-align: middle;"></i> Installed!`;
    lucide.createIcons();
    
    // Log action
    logMaintenanceAction("Office Setup: " + versionId, "Resolved", "Office version " + versionId + " installation triggered successfully.");
  })
  .catch(err => {
    btn.style.background = "var(--state-danger)";
    btn.innerHTML = `<i data-lucide="x" style="width:14px; height:14px; margin-right:4px; vertical-align: middle;"></i> Failed`;
    lucide.createIcons();
    alert("Office Installation Failed: " + err.message);
    
    setTimeout(() => {
      btn.disabled = false;
      btn.style.background = "";
      btn.style.borderColor = "";
      btn.innerHTML = originalHtml;
      lucide.createIcons();
    }, 4000);
  });
}

// 12c. Windows/Office Activation controller
function executeActivation(type) {
  // Find card button
  const card = document.getElementById("activate-" + type);
  const btn = card ? card.querySelector(".app-install-btn") : null;
  
  if (!btn) return;
  
  const originalHtml = btn.innerHTML;
  btn.disabled = true;
  btn.style.background = "var(--state-warning)";
  btn.innerHTML = `<i class="lucide-spinner" style="animation: spin 1.5s linear infinite; width:14px; height:14px; margin-right:4px; vertical-align: middle; display: inline-block;"></i> Activating...`;
  
  // Inject spinner style dynamically if not present
  if (!document.getElementById("spinner-keyframe-style")) {
    const style = document.createElement("style");
    style.id = "spinner-keyframe-style";
    style.innerHTML = "@keyframes spin { 100% { transform: rotate(360deg); } }";
    document.head.appendChild(style);
  }

  fetch(API_BASE + '/api/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ toolKey: 'activate_' + type.replace('-', '_') })
  })
  .then(res => {
    if (!res.ok) {
      return res.json().then(data => { throw new Error(data.error || 'Activation failed'); });
    }
    return res.json();
  })
  .then(data => {
    btn.style.background = "var(--state-success)";
    btn.style.borderColor = "var(--state-success)";
    btn.innerHTML = `<i data-lucide="check" style="width:14px; height:14px; margin-right:4px; vertical-align: middle;"></i> Activated!`;
    lucide.createIcons();
    
    // Log action
    logMaintenanceAction("Activation: " + type, "Resolved", "Executed activation script for " + type + " successfully.");
  })
  .catch(err => {
    btn.style.background = "var(--state-danger)";
    btn.innerHTML = `<i data-lucide="x" style="width:14px; height:14px; margin-right:4px; vertical-align: middle;"></i> Failed`;
    lucide.createIcons();
    alert("Activation script failed: " + err.message);
    
    setTimeout(() => {
      btn.disabled = false;
      btn.style.background = "";
      btn.style.borderColor = "";
      btn.innerHTML = originalHtml;
      lucide.createIcons();
    }, 4000);
  });
}

// 12c-2. Windows Edition Changer controller
function onEditionSelectChange() {
  const select = document.getElementById("edition-select");
  const input = document.getElementById("edition-key-input");
  if (select.value === "custom") {
    input.value = "";
    input.placeholder = "Enter 25-character key...";
    input.focus();
  } else {
    input.value = select.value;
  }
}

function executeChangeEdition() {
  const keyInput = document.getElementById("edition-key-input");
  const key = keyInput ? keyInput.value.trim() : "";
  if (!key || key.length < 20) {
    alert("Please enter a valid 25-character Windows Product Key.");
    return;
  }
  
  if (confirm(`Are you sure you want to change your Windows edition? This will invoke the Windows upgrade wizard using the key: ${key}. Your PC might restart during the process.`)) {
    fetch(API_BASE + '/api/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        toolKey: 'change_windows_edition',
        productKey: key
      })
    })
    .then(res => {
      if (!res.ok) {
        return res.json().then(data => { throw new Error(data.error || 'Failed to trigger edition change'); });
      }
      return res.json();
    })
    .then(data => {
      alert("Edition change command initiated successfully. The Windows Upgrade wizard should open shortly.");
      logMaintenanceAction("Change Edition: " + key, "Resolved", "Executed edition change successfully.");
    })
    .catch(err => {
      alert("Edition change failed: " + err.message);
      logMaintenanceAction("Change Edition: " + key, "Failed", err.message);
    });
  }
}

// 12d. Ninite installer controller
function installNiniteBundle() {
  const card = document.getElementById("app-ninite");
  const btn = card ? card.querySelector(".app-install-btn") : null;
  if (!btn) return;
  
  const originalHtml = btn.innerHTML;
  btn.disabled = true;
  btn.style.background = "var(--state-warning)";
  btn.innerHTML = `<i class="lucide-spinner" style="animation: spin 1.5s linear infinite; width:14px; height:14px; margin-right:4px; vertical-align: middle; display: inline-block;"></i> Installing...`;

  if (!document.getElementById("spinner-keyframe-style")) {
    const style = document.createElement("style");
    style.id = "spinner-keyframe-style";
    style.innerHTML = "@keyframes spin { 100% { transform: rotate(360deg); } }";
    document.head.appendChild(style);
  }

  fetch(API_BASE + '/api/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ toolKey: 'install_ninite_bundle' })
  })
  .then(res => {
    if (!res.ok) {
      return res.json().then(data => { throw new Error(data.error || 'Bundle install failed'); });
    }
    return res.json();
  })
  .then(data => {
    btn.style.background = "var(--state-success)";
    btn.style.borderColor = "var(--state-success)";
    btn.innerHTML = `<i data-lucide="check" style="width:14px; height:14px; margin-right:4px; vertical-align: middle;"></i> Installed!`;
    lucide.createIcons();
    logMaintenanceAction("App Install: WinGet Bundle", "Resolved", "Installed Chrome, VLC, 7-Zip via automated winget bundle.");
  })
  .catch(err => {
    btn.style.background = "var(--state-danger)";
    btn.innerHTML = `<i data-lucide="x" style="width:14px; height:14px; margin-right:4px; vertical-align: middle;"></i> Failed`;
    lucide.createIcons();
    alert("Bundle Installation Failed: " + err.message);
    
    setTimeout(() => {
      btn.disabled = false;
      btn.style.background = "";
      btn.style.borderColor = "";
      btn.innerHTML = originalHtml;
      lucide.createIcons();
    }, 4000);
  });
}

// 12e. NirSoft Suite controller
function executeNirSoft(action) {
  const cardId = action === 'download' ? 'nirsoft-download-card' : 'nirsoft-launch-card';
  const card = document.getElementById(cardId);
  const btn = card ? card.querySelector(".app-install-btn") : null;
  if (!btn) return;

  const originalHtml = btn.innerHTML;
  btn.disabled = true;
  btn.style.background = "var(--state-warning)";
  btn.innerHTML = `<i class="lucide-spinner" style="animation: spin 1.5s linear infinite; width:14px; height:14px; margin-right:4px; vertical-align: middle; display: inline-block;"></i> Executing...`;

  if (!document.getElementById("spinner-keyframe-style")) {
    const style = document.createElement("style");
    style.id = "spinner-keyframe-style";
    style.innerHTML = "@keyframes spin { 100% { transform: rotate(360deg); } }";
    document.head.appendChild(style);
  }

  fetch(API_BASE + '/api/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ toolKey: action === 'download' ? 'download_nirsoft' : 'launch_nirsoft' })
  })
  .then(res => {
    if (!res.ok) {
      return res.json().then(data => { throw new Error(data.error || 'NirSoft operation failed'); });
    }
    return res.json();
  })
  .then(data => {
    btn.style.background = "var(--state-success)";
    btn.style.borderColor = "var(--state-success)";
    btn.innerHTML = `<i data-lucide="check" style="width:14px; height:14px; margin-right:4px; vertical-align: middle;"></i> Success!`;
    lucide.createIcons();
    logMaintenanceAction("NirSoft: " + (action === 'download' ? "Download" : "Launch"), "Resolved", "Executed NirSoft " + action + " task.");
    
    setTimeout(() => {
      btn.disabled = false;
      btn.style.background = "";
      btn.style.borderColor = "";
      btn.innerHTML = originalHtml;
      lucide.createIcons();
    }, 4000);
  })
  .catch(err => {
    btn.style.background = "var(--state-danger)";
    btn.innerHTML = `<i data-lucide="x" style="width:14px; height:14px; margin-right:4px; vertical-align: middle;"></i> Failed`;
    lucide.createIcons();
    logMaintenanceAction("NirSoft: " + (action === 'download' ? "Download" : "Launch"), "Failed", "NirSoft task execution failed: " + err.message);
    alert("NirSoft Suite command failed: " + err.message);
    
    setTimeout(() => {
      btn.disabled = false;
      btn.style.background = "";
      btn.style.borderColor = "";
      btn.innerHTML = originalHtml;
      lucide.createIcons();
    }, 4000);
  });
}

// 12f. Super Admin Tool launcher controller
function executeAdminTool(toolKey) {
  openToolModal(toolKey);
}

// 12g. Robocopy engine controller
function runRobocopyEngine() {
  const sourceEl = document.getElementById("robocopy-source");
  const targetEl = document.getElementById("robocopy-target");
  const btn = document.querySelector("#superadmin button[onclick='runRobocopyEngine()']");
  
  if (!sourceEl || !targetEl) return;
  
  const sourcePath = sourceEl.value.trim();
  const targetPath = targetEl.value.trim();
  
  if (!sourcePath || !targetPath) {
    alert("Please enter both source and target directory paths for Robocopy replication.");
    return;
  }
  
  const originalHtml = btn.innerHTML;
  btn.disabled = true;
  btn.style.background = "var(--state-warning)";
  btn.innerHTML = `<i class="lucide-spinner" style="animation: spin 1.5s linear infinite; width:14px; height:14px; margin-right:4px; vertical-align: middle; display: inline-block;"></i> Mirroring...`;
  
  fetch(API_BASE + '/api/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      toolKey: 'run_robocopy', 
      sourcePath: sourcePath, 
      targetPath: targetPath 
    })
  })
  .then(res => {
    if (!res.ok) {
      return res.json().then(data => { throw new Error(data.error || 'Robocopy failed'); });
    }
    return res.json();
  })
  .then(data => {
    btn.style.background = "var(--state-success)";
    btn.innerHTML = `<i data-lucide="check" style="width:14px; height:14px; margin-right:4px; vertical-align: middle;"></i> Replication Started!`;
    lucide.createIcons();
    logMaintenanceAction("Robocopy Sync", "Resolved", `Mirrored "${sourcePath}" to "${targetPath}".`);
    
    setTimeout(() => {
      btn.disabled = false;
      btn.style.background = "";
      btn.innerHTML = originalHtml;
      lucide.createIcons();
    }, 4000);
  })
  .catch(err => {
    btn.style.background = "var(--state-danger)";
    btn.innerHTML = `<i data-lucide="x" style="width:14px; height:14px; margin-right:4px; vertical-align: middle;"></i> Failed`;
    lucide.createIcons();
    alert("Robocopy execution failed: " + err.message);
    
    setTimeout(() => {
      btn.disabled = false;
      btn.style.background = "";
      btn.innerHTML = originalHtml;
      lucide.createIcons();
    }, 4000);
  });
}

// 12h. User Profile migration controller
function runProfileMigrationBackup() {
  const targetEl = document.getElementById("migration-target");
  const btn = document.querySelector("#superadmin button[onclick='runProfileMigrationBackup()']");
  
  if (!targetEl || !btn) return;
  const targetPath = targetEl.value.trim();
  
  if (!targetPath) {
    alert("Please select or enter a target directory path for the migration backup.");
    return;
  }
  
  const originalHtml = btn.innerHTML;
  btn.disabled = true;
  btn.style.background = "var(--state-warning)";
  btn.innerHTML = `<i class="lucide-spinner" style="animation: spin 1.5s linear infinite; width:14px; height:14px; margin-right:4px; vertical-align: middle; display: inline-block;"></i> Backing up...`;
  
  fetch(API_BASE + '/api/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      toolKey: 'run_migration_backup', 
      targetPath: targetPath 
    })
  })
  .then(res => {
    if (!res.ok) {
      return res.json().then(data => { throw new Error(data.error || 'Backup failed'); });
    }
    return res.json();
  })
  .then(data => {
    btn.style.background = "var(--state-success)";
    btn.innerHTML = `<i data-lucide="check" style="width:14px; height:14px; margin-right:4px; vertical-align: middle;"></i> Backup Started!`;
    lucide.createIcons();
    logMaintenanceAction("Profile Backup", "Resolved", `Backed up user profile folders to "${targetPath}".`);
    
    setTimeout(() => {
      btn.disabled = false;
      btn.style.background = "";
      btn.innerHTML = originalHtml;
      lucide.createIcons();
    }, 4000);
  })
  .catch(err => {
    alert("Error: " + err.message);
    btn.disabled = false;
    btn.style.background = "";
    btn.innerHTML = originalHtml;
    lucide.createIcons();
  });
}

// 12i. Winget apps list export controller
function runWingetExport() {
  const targetEl = document.getElementById("migration-target");
  const btn = document.querySelector("#superadmin button[onclick='runWingetExport()']");
  
  if (!btn) return;
  const targetPath = targetEl ? targetEl.value.trim() : "";
  
  const originalHtml = btn.innerHTML;
  btn.disabled = true;
  btn.style.background = "var(--state-warning)";
  btn.innerHTML = `<i class="lucide-spinner" style="animation: spin 1.5s linear infinite; width:14px; height:14px; margin-right:4px; vertical-align: middle; display: inline-block;"></i> Exporting...`;
  
  fetch(API_BASE + '/api/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      toolKey: 'winget_export', 
      targetPath: targetPath 
    })
  })
  .then(res => {
    if (!res.ok) {
      return res.json().then(data => { throw new Error(data.error || 'Export failed'); });
    }
    return res.json();
  })
  .then(data => {
    btn.style.background = "var(--state-success)";
    btn.innerHTML = `<i data-lucide="check" style="width:14px; height:14px; margin-right:4px; vertical-align: middle;"></i> Export Started!`;
    lucide.createIcons();
    logMaintenanceAction("Winget Export", "Resolved", `Exported installed applications list to JSON.`);
    
    setTimeout(() => {
      btn.disabled = false;
      btn.style.background = "";
      btn.innerHTML = originalHtml;
      lucide.createIcons();
    }, 4000);
  })
  .catch(err => {
    alert("Error: " + err.message);
    btn.disabled = false;
    btn.style.background = "";
    btn.innerHTML = originalHtml;
    lucide.createIcons();
  });
}

// 12j. Winget apps list import controller
async function runWingetImport() {
  const btn = document.querySelector("#superadmin button[onclick='runWingetImport()']");
  if (!btn) return;

  try {
    const response = await fetch(API_BASE + '/api/browse-file');
    if (!response.ok) {
      throw new Error('Failed to open file browser dialog');
    }
    const browseData = await response.json();
    if (!browseData.success || !browseData.path) {
      return;
    }
    const filePath = browseData.path;

    const originalHtml = btn.innerHTML;
    btn.disabled = true;
    btn.style.background = "var(--state-warning)";
    btn.innerHTML = `<i class="lucide-spinner" style="animation: spin 1.5s linear infinite; width:14px; height:14px; margin-right:4px; vertical-align: middle; display: inline-block;"></i> Importing...`;
    
    fetch(API_BASE + '/api/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        toolKey: 'winget_import', 
        filePath: filePath 
      })
    })
    .then(res => {
      if (!res.ok) {
        return res.json().then(data => { throw new Error(data.error || 'Import failed'); });
      }
      return res.json();
    })
    .then(data => {
      btn.style.background = "var(--state-success)";
      btn.innerHTML = `<i data-lucide="check" style="width:14px; height:14px; margin-right:4px; vertical-align: middle;"></i> Import Started!`;
      lucide.createIcons();
      logMaintenanceAction("Winget Import", "Resolved", `Imported installed applications list from "${filePath}".`);
      
      setTimeout(() => {
        btn.disabled = false;
        btn.style.background = "";
        btn.innerHTML = originalHtml;
        lucide.createIcons();
      }, 4000);
    })
    .catch(err => {
      alert("Error: " + err.message);
      btn.disabled = false;
      btn.style.background = "";
      btn.innerHTML = originalHtml;
      lucide.createIcons();
    });

  } catch (error) {
    console.error('Error importing winget apps:', error);
    alert('Failed to browse files or start import. Make sure the local server is running.');
  }
}

// 12h_2. User Profile migration controller (Tab version)
function runProfileMigrationBackupTab() {
  const targetEl = document.getElementById("migration-target-tab");
  const btn = document.getElementById("btn-backup-profile-tab");
  
  if (!targetEl || !btn) return;
  const targetPath = targetEl.value.trim();
  
  if (!targetPath) {
    alert("Please select or enter a target directory path for the migration backup.");
    return;
  }
  
  const originalHtml = btn.innerHTML;
  btn.disabled = true;
  btn.style.background = "var(--state-warning)";
  btn.innerHTML = `<i class="lucide-spinner" style="animation: spin 1.5s linear infinite; width:14px; height:14px; margin-right:4px; vertical-align: middle; display: inline-block;"></i> Backing up...`;
  
  fetch(API_BASE + '/api/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      toolKey: 'run_migration_backup', 
      targetPath: targetPath 
    })
  })
  .then(res => {
    if (!res.ok) {
      return res.json().then(data => { throw new Error(data.error || 'Backup failed'); });
    }
    return res.json();
  })
  .then(data => {
    btn.style.background = "var(--state-success)";
    btn.innerHTML = `<i data-lucide="check" style="width:14px; height:14px; margin-right:4px; vertical-align: middle;"></i> Backup Started!`;
    lucide.createIcons();
    logMaintenanceAction("Profile Backup", "Resolved", `Backed up user profile folders to "${targetPath}".`);
    
    setTimeout(() => {
      btn.disabled = false;
      btn.style.background = "";
      btn.innerHTML = originalHtml;
      lucide.createIcons();
    }, 4000);
  })
  .catch(err => {
    alert("Error: " + err.message);
    btn.disabled = false;
    btn.style.background = "";
    btn.innerHTML = originalHtml;
    lucide.createIcons();
  });
}

// 12i_2. Winget apps list export controller (Tab version)
function runWingetExportTab() {
  const targetEl = document.getElementById("migration-target-tab");
  const btn = document.querySelector("button[onclick='runWingetExportTab()']");
  
  if (!btn) return;
  const targetPath = targetEl ? targetEl.value.trim() : "";
  
  const originalHtml = btn.innerHTML;
  btn.disabled = true;
  btn.style.background = "var(--state-warning)";
  btn.innerHTML = `<i class="lucide-spinner" style="animation: spin 1.5s linear infinite; width:14px; height:14px; margin-right:4px; vertical-align: middle; display: inline-block;"></i> Exporting...`;
  
  fetch(API_BASE + '/api/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      toolKey: 'winget_export', 
      targetPath: targetPath 
    })
  })
  .then(res => {
    if (!res.ok) {
      return res.json().then(data => { throw new Error(data.error || 'Export failed'); });
    }
    return res.json();
  })
  .then(data => {
    btn.style.background = "var(--state-success)";
    btn.innerHTML = `<i data-lucide="check" style="width:14px; height:14px; margin-right:4px; vertical-align: middle;"></i> Export Started!`;
    lucide.createIcons();
    logMaintenanceAction("Winget Export", "Resolved", `Exported installed applications list to JSON.`);
    
    setTimeout(() => {
      btn.disabled = false;
      btn.style.background = "";
      btn.innerHTML = originalHtml;
      lucide.createIcons();
    }, 4000);
  })
  .catch(err => {
    alert("Error: " + err.message);
    btn.disabled = false;
    btn.style.background = "";
    btn.innerHTML = originalHtml;
    lucide.createIcons();
  });
}

// 12j_2. Winget apps list import controller (Tab version)
async function runWingetImportTab() {
  const btn = document.querySelector("button[onclick='runWingetImportTab()']");
  if (!btn) return;

  try {
    const response = await fetch(API_BASE + '/api/browse-file');
    if (!response.ok) {
      throw new Error('Failed to open file browser dialog');
    }
    const browseData = await response.json();
    if (!browseData.success || !browseData.path) {
      return;
    }
    const filePath = browseData.path;

    const originalHtml = btn.innerHTML;
    btn.disabled = true;
    btn.style.background = "var(--state-warning)";
    btn.innerHTML = `<i class="lucide-spinner" style="animation: spin 1.5s linear infinite; width:14px; height:14px; margin-right:4px; vertical-align: middle; display: inline-block;"></i> Importing...`;
    
    fetch(API_BASE + '/api/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        toolKey: 'winget_import', 
        filePath: filePath 
      })
    })
    .then(res => {
      if (!res.ok) {
        return res.json().then(data => { throw new Error(data.error || 'Import failed'); });
      }
      return res.json();
    })
    .then(data => {
      btn.style.background = "var(--state-success)";
      btn.innerHTML = `<i data-lucide="check" style="width:14px; height:14px; margin-right:4px; vertical-align: middle;"></i> Import Started!`;
      lucide.createIcons();
      logMaintenanceAction("Winget Import", "Resolved", `Imported installed applications list from "${filePath}".`);
      
      setTimeout(() => {
        btn.disabled = false;
        btn.style.background = "";
        btn.innerHTML = originalHtml;
        lucide.createIcons();
      }, 4000);
    })
    .catch(err => {
      alert("Error: " + err.message);
      btn.disabled = false;
      btn.style.background = "";
      btn.innerHTML = originalHtml;
      lucide.createIcons();
    });

  } catch (error) {
    console.error('Error importing winget apps:', error);
    alert('Failed to browse files or start import. Make sure the local server is running.');
  }
}

// 13. System Debloater loop controller
function executeDebloatAll() {
  const tweaks = [
    { id: "tweak-telemetry", key: "disable_telemetry", name: "Telemetry Tweaks" },
    { id: "tweak-cortana", key: "disable_cortana", name: "Cortana Tweaks" },
    { id: "tweak-onedrive", key: "disable_onedrive", name: "OneDrive Tweaks" },
    { id: "tweak-xbox", key: "disable_xbox", name: "Xbox Live Tweaks" },
    { id: "tweak-bloatware", key: "uninstall_bloatware", name: "Uninstall Bloatware" }
  ];

  const selectedTweaks = tweaks.filter(t => {
    const el = document.getElementById(t.id);
    return el && el.checked;
  });

  if (selectedTweaks.length === 0) {
    alert("Please check at least one debloat tweak to apply.");
    return;
  }

  if (!confirm("Are you sure you want to apply the " + selectedTweaks.length + " selected tweaks to your Windows system?")) {
    return;
  }

  // Execute sequentially in the background
  let successCount = 0;
  let failCount = 0;
  
  alert("Applying " + selectedTweaks.length + " tweaks in the background. Keep this browser page open. Status logs will populate in your Maintenance Log.");

  function runNext(index) {
    if (index >= selectedTweaks.length) {
      alert("System Debloater finished! Tweak success: " + successCount + ", failed: " + failCount);
      loadMaintenanceLogs();
      return;
    }

    const tweak = selectedTweaks[index];
    
    fetch(API_BASE + '/api/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ toolKey: tweak.key })
    })
    .then(res => {
      if (!res.ok) throw new Error("Tweak failed");
      successCount++;
      logMaintenanceAction("Debloat: " + tweak.name, "Resolved", "Tweak applied successfully.");
    })
    .catch(err => {
      failCount++;
      logMaintenanceAction("Debloat: " + tweak.name, "Failed", "Error applying system tweak registry settings.");
    })
    .finally(() => {
      runNext(index + 1);
    });
  }

  runNext(0);
}

// 14. Hybrid Multimodal AI Assistant Chat Engine (Online/Offline)
let aiModeOnline = false;
let attachedFileBase64 = null;
let attachedFileType = null;
let attachedFileName = null;

function toggleAiMode() {
  const toggle = document.getElementById("ai-mode-toggle");
  const keySection = document.getElementById("ai-key-section");
  const desc = document.getElementById("ai-status-desc");
  
  if (toggle && toggle.checked) {
    aiModeOnline = true;
    if (keySection) keySection.style.display = "flex";
    if (desc) desc.innerHTML = "<strong>Online AI Mode Active:</strong> Direct Google Gemini integration. Key is saved in localStorage. Vision image attachments are supported.";
  } else {
    aiModeOnline = false;
    if (keySection) keySection.style.display = "none";
    if (desc) desc.innerHTML = "<strong>Offline Mode Active:</strong> Type system issues or upload log files (.log, .txt) to perform local pattern-matching error scans.";
  }
}

function saveApiKey() {
  const el = document.getElementById("ai-api-key");
  if (el) {
    localStorage.setItem("winpulse_gemini_api_key", el.value);
  }
}

function loadApiKey() {
  const el = document.getElementById("ai-api-key");
  let savedKey = localStorage.getItem("winpulse_gemini_api_key");
  if (!savedKey && DEFAULT_GEMINI_API_KEY) {
    savedKey = DEFAULT_GEMINI_API_KEY;
    localStorage.setItem("winpulse_gemini_api_key", savedKey);
  }
  if (el && savedKey) {
    el.value = savedKey;
  }
}

function triggerFileInput() {
  const fileInput = document.getElementById("ai-file-input");
  if (fileInput) fileInput.click();
}

function handleFileSelect(event) {
  const file = event.target.files[0];
  if (!file) return;

  attachedFileName = file.name;
  const ext = file.name.split('.').pop().toLowerCase();
  
  const isImage = ['png', 'jpg', 'jpeg'].includes(ext);
  const isLog = ['txt', 'log'].includes(ext);
  
  if (!isImage && !isLog) {
    alert("Invalid file format. Please upload error screenshots (.png, .jpg, .jpeg) or text log files (.log, .txt).");
    return;
  }
  
  attachedFileType = isImage ? 'image' : 'text';
  
  const reader = new FileReader();
  reader.onload = function(e) {
    if (isImage) {
      // Store raw base64 data for Gemini vision API
      attachedFileBase64 = e.target.result.split(',')[1];
      showAttachmentPreview(e.target.result, file.name);
    } else {
      // Store log file text contents
      attachedFileBase64 = e.target.result;
      showAttachmentPreview(null, file.name);
    }
  };
  
  if (isImage) {
    reader.readAsDataURL(file);
  } else {
    reader.readAsText(file);
  }
}

function showAttachmentPreview(imgSrc, fileName) {
  const bar = document.getElementById("attachment-preview-bar");
  if (!bar) return;
  
  bar.style.display = "flex";
  
  let previewHtml = "";
  if (imgSrc) {
    previewHtml = `
      <div class="attachment-preview-card">
        <img src="${imgSrc}" alt="screenshot">
        <span>${fileName.substring(0, 15)}...</span>
        <button class="attachment-remove-btn" onclick="clearAttachment()"><i data-lucide="x"></i></button>
      </div>
    `;
  } else {
    previewHtml = `
      <div class="attachment-preview-card">
        <i data-lucide="file-text" style="width: 16px; height: 16px; color: var(--accent-cyan); vertical-align: middle;"></i>
        <span>${fileName.substring(0, 15)}...</span>
        <button class="attachment-remove-btn" onclick="clearAttachment()"><i data-lucide="x"></i></button>
      </div>
    `;
  }
  
  bar.innerHTML = previewHtml;
  lucide.createIcons();
}

function clearAttachment() {
  attachedFileBase64 = null;
  attachedFileType = null;
  attachedFileName = null;
  
  const fileInput = document.getElementById("ai-file-input");
  if (fileInput) fileInput.value = "";
  
  const bar = document.getElementById("attachment-preview-bar");
  if (bar) {
    bar.innerHTML = "";
    bar.style.display = "none";
  }
}

function handleChatKeyDown(event) {
  if (event.key === 'Enter' && event.ctrlKey) {
    event.preventDefault();
    sendChatMessage();
  }
}

function sendChatMessage() {
  const inputEl = document.getElementById("ai-chat-input");
  if (!inputEl) return;
  
  const userText = inputEl.value.trim();
  if (!userText && !attachedFileBase64) return;
  
  const chatMessages = document.getElementById("ai-chat-messages");
  if (!chatMessages) return;

  // Render User Bubble
  const userBubble = document.createElement("div");
  userBubble.className = "chat-bubble user";
  
  let attachmentMsg = "";
  if (attachedFileName) {
    attachmentMsg = `<div style="font-size:11px; margin-bottom:6px; opacity:0.8; display:flex; align-items:center; gap:5px;">
      <i data-lucide="${attachedFileType === 'image' ? 'image' : 'file-text'}" style="width:12px; height:12px;"></i>
      Attached: ${attachedFileName}
    </div>`;
  }

  userBubble.innerHTML = `
    ${attachmentMsg}
    ${userText || '<i>Sent attachment files</i>'}
    <span class="chat-bubble-meta">${new Date().toLocaleTimeString()}</span>
  `;
  
  chatMessages.appendChild(userBubble);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  
  // Clear textarea
  inputEl.value = "";
  lucide.createIcons();

  // Create loading placeholder bubble for AI
  const aiBubble = document.createElement("div");
  aiBubble.className = "chat-bubble ai";
  aiBubble.innerHTML = `
    <span class="typing-indicator" style="display:inline-flex; gap:3px;">
      <span style="animation: bounce 1.2s infinite; width:6px; height:6px; background:#fff; border-radius:50%;"></span>
      <span style="animation: bounce 1.2s infinite 0.2s; width:6px; height:6px; background:#fff; border-radius:50%;"></span>
      <span style="animation: bounce 1.2s infinite 0.4s; width:6px; height:6px; background:#fff; border-radius:50%;"></span>
    </span>
  `;
  
  // Inject typing indicator keyframe if not present
  if (!document.getElementById("typing-bounce-style")) {
    const style = document.createElement("style");
    style.id = "typing-bounce-style";
    style.innerHTML = "@keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-5px); } }";
    document.head.appendChild(style);
  }

  chatMessages.appendChild(aiBubble);
  chatMessages.scrollTop = chatMessages.scrollHeight;

  // Capture attachment configurations before clearing preview
  const fileData = attachedFileBase64;
  const fileType = attachedFileType;
  const fileName = attachedFileName;
  clearAttachment();

  if (aiModeOnline) {
    executeOnlineAi(userText, fileData, fileType, fileName, aiBubble, chatMessages);
  } else {
    executeOfflineAi(userText, fileData, fileType, fileName, aiBubble, chatMessages);
  }
}

function executeOnlineAi(promptText, fileData, fileType, fileName, aiBubble, chatViewport) {
  const apiKey = localStorage.getItem("winpulse_gemini_api_key") || DEFAULT_GEMINI_API_KEY || "";
  
  if (!apiKey) {
    aiBubble.innerHTML = `✕ <strong>Error:</strong> Please enter a Gemini API Key in the AI Configuration sidebar to run in Online Mode.`;
    return;
  }

  // Multi-model backup list to handle model-busy / rate-limits / server issues
  const models = ["gemini-2.5-flash", "gemini-1.5-flash"];
  
  const systemInstruction = "You are the Venkat Windows Tool Kit Diagnostic Assistant. Analyze the user's computer issue. Provide clear, concise, step-by-step recommendations. You can recommend that the user execute one-click fixes. If one of our tool keys matches the user's problem, you MUST include the token [EXECUTE: toolKey] on a new line. Supported tool keys: sfc_scan, dism_restore, reset_wua, flush_dns, reset_winsock, reset_firewall, create_restore_point, disable_telemetry, disable_cortana, disable_onedrive, disable_xbox, uninstall_bloatware, backup_printers, restore_printers, quick_repair, clear_queue, restart_spooler, devices_printers, print_management, sharing_center, activate_windows, activate_office, activate_kms, activate_kms_uninstall, run_migration_backup, winget_export, winget_import.";

  const contents = [];
  const parts = [];

  // Add text prompt
  parts.push({ text: promptText || "Analyze the uploaded file for computer errors." });

  // Add image if attached
  if (fileData && fileType === 'image') {
    parts.push({
      inlineData: {
        mimeType: "image/jpeg",
        data: fileData
      }
    });
  } else if (fileData && fileType === 'text') {
    // Inject log text file directly into text parts
    parts.push({ text: "\nAttached Log File Contents (" + fileName + "):\n" + fileData });
  }

  contents.push({ role: "user", parts: parts });

  const payload = {
    contents: contents,
    systemInstruction: {
      parts: [{ text: systemInstruction }]
    }
  };

  function tryRequest(modelIndex) {
    const activeModel = models[modelIndex];
    const url = `https://generativelanguage.googleapis.com/v1beta/models/${activeModel}:generateContent?key=${apiKey}`;

    fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    .then(res => {
      if (!res.ok) return res.json().then(data => { throw new Error(data.error?.message || 'API request failed'); });
      return res.json();
    })
    .then(data => {
      let responseText = data.candidates?.[0]?.content?.parts?.[0]?.text || "No response received.";
      const parsedHtml = formatAiResponse(responseText);
      
      aiBubble.innerHTML = `
        ${parsedHtml}
        <span class="chat-bubble-meta">${new Date().toLocaleTimeString()}</span>
      `;
      chatViewport.scrollTop = chatViewport.scrollHeight;
    })
    .catch(err => {
      console.warn(`[AI Assistant] Model ${activeModel} failed:`, err.message);
      
      if (modelIndex + 1 < models.length) {
        // Fall back to backup model (e.g. Gemini 1.5 Flash)
        aiBubble.innerHTML = `<span style="color: var(--state-warning);">⚠️ Primary AI (Gemini 2.5) was busy. Retrying with backup AI (Gemini 1.5)...</span>`;
        tryRequest(modelIndex + 1);
      } else {
        // Fall back to offline diagnostics database if all online endpoints fail
        aiBubble.innerHTML = `<span style="color: var(--state-warning);">⚠️ Online AI service is busy or offline. Switching to local diagnostics database...</span>`;
        setTimeout(() => {
          executeOfflineAi(promptText, fileData, fileType, fileName, aiBubble, chatViewport, true);
        }, 1200);
      }
    });
  }

  // Start with primary model (index 0)
  tryRequest(0);
}

function executeOfflineAi(promptText, fileData, fileType, fileName, aiBubble, chatViewport, isFallback = false) {
  setTimeout(() => {
    let responseText = "";
    
    if (fileData && fileType === 'text') {
      // Local Log parsing!
      const logText = fileData.toLowerCase();
      
      if (logText.includes("0x0000011b") || logText.includes("rpc_fixes") || logText.includes("rpc over named pipes")) {
        responseText = "I scanned the uploaded log file **" + fileName + "** and identified print spooler connectivity errors relating to RPC protocols.\n\n**Diagnostic Recommendation:** Enforce printing RPC packets to run over Named Pipes to resolve security credential mismatches.\n\n[EXECUTE: rpc_fixes]";
      } else if (logText.includes("spooler") || logText.includes("spooler service") || logText.includes("printers")) {
        responseText = "I scanned the uploaded log file **" + fileName + "** and found Spooler crashes and printer queue lockouts.\n\n**Diagnostic Recommendation:** Cycle the Print Spooler service and clear stuck job documents.\n\n[EXECUTE: quick_repair]";
      } else if (logText.includes("dns") || logText.includes("dhcp") || logText.includes("ipconfig") || logText.includes("network")) {
        responseText = "I scanned the uploaded log file **" + fileName + "** and identified networking resolver faults.\n\n**Diagnostic Recommendation:** Flush local DNS resolver cache and renew DHCP allocations.\n\n[EXECUTE: flush_dns]";
      } else {
        responseText = "I scanned the uploaded log file **" + fileName + "** but did not match any specific printer or system error codes.\n\n**Diagnostic Recommendation:** Try running a generic System File Checker (SFC) scan to repair components.\n\n[EXECUTE: sfc_scan]";
      }
    } else if (fileData && fileType === 'image') {
      responseText = "✕ **Offline Mode Warning:** Vision screenshot analysis requires an active internet connection. Please enable **Online AI Mode** and enter a Gemini API Key in the settings sidebar to diagnose error screenshots.";
    } else {
      // Keyword matching
      const query = (promptText || "").toLowerCase();
      
      if (query.includes("slow") || query.includes("performance") || query.includes("bloat") || query.includes("telemetry")) {
        responseText = "If your computer is running slowly or you want to improve privacy, I recommend running the Windows Debloater tool to disable telemetry and remove consumer bloatware.\n\n**Tweak Actions:**\n\n[EXECUTE: disable_telemetry]";
      } else if (query.includes("spooler") || query.includes("stuck") || query.includes("queue") || query.includes("printer")) {
        responseText = "For printing failures, service crashes, or documents stuck in the queue, run the Printer Quick Repair tool.\n\n[EXECUTE: quick_repair]";
      } else if (query.includes("internet") || query.includes("wifi") || query.includes("network") || query.includes("dns")) {
        responseText = "To troubleshoot networking glitches, IP conflicts, or domain name errors, flush your resolver cache.\n\n[EXECUTE: flush_dns]";
      } else if (query.includes("corrupt") || query.includes("dism") || query.includes("sfc") || query.includes("system file")) {
        responseText = "If you are encountering system crashes, missing DLLs, or corrupted files, run System File Checker (SFC) scan.\n\n[EXECUTE: sfc_scan]";
      } else {
        responseText = "I am running in **Offline Mode**. Describe your issue with keywords like 'spooler', 'slow', 'internet', or 'corrupt' so I can match them, or attach system log files to scan. Enable **Online AI Mode** to get full conversational support.";
      }
    }

    if (isFallback) {
      responseText = "⚠️ **Note:** The online Gemini service was busy or rate-limited. I generated this report using our local offline diagnostics database:\n\n" + responseText;
    }

    const parsedHtml = formatAiResponse(responseText);
    
    aiBubble.innerHTML = `
      ${parsedHtml}
      <span class="chat-bubble-meta">${new Date().toLocaleTimeString()}</span>
    `;
    chatViewport.scrollTop = chatViewport.scrollHeight;
  }, 1000);
}

function formatAiResponse(text) {
  // Convert newlines to breaks and simple markdown-like bolding **text** to <strong>
  let formatted = text
    .replace(/\n/g, "<br>")
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

  // Parse [EXECUTE: toolKey] tags
  const executeRegex = /\[EXECUTE:\s*([a-zA-Z0-9_-]+)\]/g;
  
  formatted = formatted.replace(executeRegex, (match, toolKey) => {
    const tool = TOOLBOX_DATA[toolKey];
    const toolTitle = tool ? tool.title : "System Tweak / Repair";
    const toolDesc = tool ? tool.description : "Execute the recommended repair command automatically.";
    
    return `
      <div class="ai-action-card">
        <span class="ai-action-card-title"><i data-lucide="zap" style="width:12px; height:12px; margin-right:4px; vertical-align: middle;"></i> Actionable Fix</span>
        <span class="ai-action-card-desc"><strong>${toolTitle}</strong>: ${toolDesc.substring(0, 100)}...</span>
        <button class="btn btn-primary btn-sm" style="margin-top:5px; display:inline-flex; align-items:center; gap:4px;" onclick="openToolModal('${toolKey}')">
          <i data-lucide="play" style="width:10px; height:10px;"></i> Apply Fix automatically
        </button>
      </div>
    `;
  });

  return formatted;
}

// 15. Telemetry monitor simulation
function startTelemetryMonitor() {
  setInterval(() => {
    const cpuVal = Math.floor(Math.random() * 20) + 15; // 15-35%
    const ramVal = Math.floor(Math.random() * 10) + 50; // 50-60%
    
    const cpuFill = document.querySelector(".cpu-fill");
    const ramFill = document.querySelector(".ram-fill");
    const cpuPct = document.getElementById("cpu-pct");
    const ramPct = document.getElementById("ram-pct");
    
    if (cpuFill) cpuFill.style.height = cpuVal + "%";
    if (ramFill) ramFill.style.height = ramVal + "%";
    if (cpuPct) cpuPct.innerText = cpuVal + "%";
    if (ramPct) ramPct.innerText = ramVal + "%";
  }, 3000);
}

// 16. Disk & Security Tools Integration
function loadWebDiskInfo() {
  fetch(API_BASE + '/api/diskinfo')
    .then(res => res.json())
    .then(data => {
      // 1. Populate Windows drives
      const winSelect = document.getElementById("ds-win-drive");
      if (winSelect) {
        winSelect.innerHTML = "";
        if (data.windowsDrives && data.windowsDrives.length > 0) {
          data.windowsDrives.forEach(drv => {
            winSelect.innerHTML += `<option value="${drv}">${drv}:\\</option>`;
          });
        } else {
          winSelect.innerHTML = `<option value="C">C:\\</option><option value="D">D:\\</option><option value="E">E:\\</option>`;
        }
      }

      // 2. Populate all drive letters
      const allSelects = ["ds-fat32-drive", "ds-bcd-win", "ds-bcd-boot", "ds-target-part"];
      allSelects.forEach(id => {
        const select = document.getElementById(id);
        if (select) {
          select.innerHTML = "";
          if (data.allDrives && data.allDrives.length > 0) {
            data.allDrives.forEach(drv => {
              select.innerHTML += `<option value="${drv}">${drv}:\\</option>`;
            });
          } else {
            select.innerHTML = `<option value="C">C:\\</option><option value="D">D:\\</option><option value="E">E:\\</option>`;
          }
        }
      });

      // 3. Populate disks
      const diskSelects = ["ds-disk-num", "ds-target-disk"];
      diskSelects.forEach(id => {
        const select = document.getElementById(id);
        if (select) {
          select.innerHTML = "";
          if (data.disks && data.disks.length > 0) {
            data.disks.forEach(d => {
              select.innerHTML += `<option value="${d.Number}">Disk ${d.Number}: ${d.Name} (${d.Style})</option>`;
            });
          } else {
            select.innerHTML = `<option value="0">Disk 0</option><option value="1">Disk 1</option>`;
          }
        }
      });
    })
    .catch(err => {
      console.warn("Failed to load disk info: ", err);
    });
}

function runDiskSecurityCommand(action) {
  let bodyData = { toolKey: action };
  
  if (action === 'apply_utilman_bypass' || action === 'restore_utilman') {
    bodyData.winDrive = document.getElementById("ds-win-drive").value;
  } else if (action === 'convert_fat32_to_ntfs') {
    bodyData.driveLetter = document.getElementById("ds-fat32-drive").value;
  } else if (action === 'convert_mbr_to_gpt') {
    bodyData.diskNum = document.getElementById("ds-disk-num").value;
  } else if (action === 'bcdboot_repair') {
    bodyData.winDrive = document.getElementById("ds-bcd-win").value;
    bodyData.bootDrive = document.getElementById("ds-bcd-boot").value;
  }

  fetch(API_BASE + '/api/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(bodyData)
  })
  .then(res => {
    if (!res.ok) {
      return res.json().then(data => { throw new Error(data.error || 'Execution failed'); });
    }
    return res.json();
  })
  .then(data => {
    alert("Command executed successfully!");
    logMaintenanceAction("Disk/Security Tool", "Success", `Action: ${action}`);
  })
  .catch(err => {
    alert("Error: " + err.message);
  });
}

const OS_INSTALL_ERRORS_WEB = {
  "Select an installation error to troubleshoot...": {
    "desc": "Select an error from the dropdown to see detailed causes, guides, and automated scripting solutions.",
    "fix_type": null
  },
  "wipe_gpt": {
    "desc": "Cause: You booted the Windows installer in UEFI mode, but your hard drive is partitioned in the older MBR style.\n\nSolution 1 (Lossless): Use our 'Convert MBR to GPT' tool on the left to convert the disk without losing any files.\n\nSolution 2 (Destructive): Wipe the disk and convert to GPT via Diskpart. This will delete all partitions and data on the selected disk.",
    "fix_type": "wipe_gpt"
  },
  "wipe_mbr": {
    "desc": "Cause: You booted the Windows installer in Legacy/CSM BIOS mode, but your hard drive is partitioned in the GPT style.\n\nSolution: Wipe the disk and convert to MBR via Diskpart. This will delete all partitions and data on the selected disk.",
    "fix_type": "wipe_mbr"
  },
  "wipe_basic": {
    "desc": "Cause: The target hard drive was converted to a dynamic disk, which Windows Setup cannot install to.\n\nSolution: Wipe the disk and convert it back to a basic partition style. WARNING: This deletes all data on the disk.",
    "fix_type": "wipe_basic"
  },
  "wipe_clean": {
    "desc": "Cause: This can happen if multiple hard drives are plugged in, causing drive number confusion, or if the partition layout is corrupt.\n\nSolution 1: Unplug all other internal/external hard drives except the target drive.\n\nSolution 2: Run a quick Diskpart clean on the target disk to reset its partition structure.",
    "fix_type": "wipe_clean"
  },
  "chkdsk": {
    "desc": "Cause: This error indicates file corruption, usually caused by bad sectors on the hard drive, corrupted USB installation files, or faulty RAM.\n\nSolution 1: Run a disk integrity check (chkdsk /f) on the target partition using the tool below to repair system sectors.\n\nSolution 2: Re-create your Windows bootable USB drive using a new USB stick or download.",
    "fix_type": "chkdsk"
  }
};

function onWebErrorSelect(val) {
  const descEl = document.getElementById("ds-error-desc");
  const info = OS_INSTALL_ERRORS_WEB[val] || OS_INSTALL_ERRORS_WEB["Select an installation error to troubleshoot..."];
  if (descEl) {
    descEl.innerText = info.desc;
  }
}

function runWebInstallFix() {
  const select = document.getElementById("ds-error-select");
  const val = select.value;
  const info = OS_INSTALL_ERRORS_WEB[val];
  if (!info || !info.fix_type) {
    alert("Please select a valid error to fix.");
    return;
  }

  const fix_type = info.fix_type;
  
  if (["wipe_gpt", "wipe_mbr", "wipe_basic", "wipe_clean"].includes(fix_type)) {
    const disk = document.getElementById("ds-target-disk").value;
    if (!confirm(`CRITICAL WARNING: This will completely WIPE Disk ${disk} via Diskpart.\nAll files and partitions will be permanently deleted.\n\nDo you want to proceed?`)) {
      return;
    }
    
    fetch(API_BASE + '/api/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ toolKey: "wipe_disk", fixType: fix_type, diskNum: disk })
    })
    .then(res => res.json())
    .then(data => {
      if (data.error) throw new Error(data.error);
      alert("Disk wiped and converted successfully!");
      logMaintenanceAction("Disk Fixer", "Success", `Wiped disk ${disk} and converted to ${fix_type}`);
    })
    .catch(err => alert("Error: " + err.message));
    
  } else if (fix_type === "chkdsk") {
    const part = document.getElementById("ds-target-part").value;
    fetch(API_BASE + '/api/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ toolKey: "chkdsk_repair", driveLetter: part })
    })
    .then(res => res.json())
    .then(data => {
      if (data.error) throw new Error(data.error);
      alert("chkdsk integrity scan launched!");
      logMaintenanceAction("Disk Fixer", "Success", `Run chkdsk on drive ${part}:`);
    })
    .catch(err => alert("Error: " + err.message));
  }
}
