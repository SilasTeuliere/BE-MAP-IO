[Setup]
AppName=ClearCCNData
AppVersion=1.0
DefaultDirName={pf}\ClearCCNData
OutputDir=.
OutputBaseFilename=setup_ClearCCNData

[Files]
Source: "dist\BE-MAP-IO.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\ClearCCNData"; Filename: "{app}\ClearCCNData.exe"