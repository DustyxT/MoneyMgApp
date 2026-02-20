[Setup]
AppName=ManageUrWealth
AppVersion=1.0.0
DefaultDirName={autopf}\ManageUrWealth
DefaultGroupName=ManageUrWealth
UninstallDisplayIcon={app}\ManageUrWealth.exe
Compression=lzma2
SolidCompression=yes
OutputDir=setup_build
OutputBaseFilename=ManageUrWealth_Setup
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=lowest
; Allow installation without admin rights if user chooses a local folder, but defaults to Program Files

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\ManageUrWealth.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\ManageUrWealth"; Filename: "{app}\ManageUrWealth.exe"
Name: "{autodesktop}\ManageUrWealth"; Filename: "{app}\ManageUrWealth.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\ManageUrWealth.exe"; Description: "{cm:LaunchProgram,ManageUrWealth}"; Flags: nowait postinstall skipifsilent
