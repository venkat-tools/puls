# Requires -RunAsAdministrator
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    Exit
}

Add-Type -AssemblyName PresentationFramework
Add-Type -AssemblyName PresentationCore
Add-Type -AssemblyName WindowsBase
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName Microsoft.VisualBasic

$xamlRaw = @"
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="VenkatPulse AI - Windows Utility Suite" Height="840" Width="1240"
        Background="#0b0f19" Foreground="#ffffff" WindowStartupLocation="CenterScreen" ResizeMode="CanResize">
    <Window.Resources>
        <Style TargetType="Button">
            <Setter Property="Background" Value="#1e293b"/>
            <Setter Property="Foreground" Value="#ffffff"/>
            <Setter Property="BorderThickness" Value="1"/>
            <Setter Property="BorderBrush" Value="#334155"/>
            <Setter Property="Padding" Value="10,5,10,5"/>
            <Setter Property="Cursor" Value="Hand"/>
            <Style.Resources>
                <Style TargetType="Border">
                    <Setter Property="CornerRadius" Value="4"/>
                </Style>
            </Style.Resources>
        </Style>
    </Window.Resources>
    
    <Grid>
        <Grid.ColumnDefinitions>
            <ColumnDefinition Width="240"/>
            <ColumnDefinition Width="*"/>
        </Grid.ColumnDefinitions>

        <!-- Sidebar Navigation -->
        <Border Grid.Column="0" Background="#111827" BorderBrush="#1f2937" BorderThickness="0,0,1,0">
            <Grid>
                <Grid.RowDefinitions>
                    <RowDefinition Height="90"/>
                    <RowDefinition Height="*"/>
                    <RowDefinition Height="45"/>
                </Grid.RowDefinitions>

                <StackPanel Grid.Row="0" Margin="20,20,20,10" VerticalAlignment="Center">
                    <TextBlock Text="⚡ VenkatPulse AI" FontSize="18" FontWeight="Bold" Foreground="#38bdf8"/>
                    <TextBlock Text="Windows Utility Suite" FontSize="10" Foreground="#6b7280" Margin="2,2,0,0"/>
                </StackPanel>

                <ScrollViewer Grid.Row="1" VerticalScrollBarVisibility="Auto" HorizontalScrollBarVisibility="Disabled">
                    <StackPanel Margin="10,0,10,0">
                        <Button Name="btn_dash" Content="🏠  Dashboard" Height="36" Margin="0,2,0,2" Background="#1e293b" Foreground="#ffffff" BorderThickness="0" HorizontalContentAlignment="Left" Padding="15,0,0,0" FontSize="11.5" FontWeight="SemiBold"/>
                        <Button Name="btn_soft" Content="📥  Software Installer" Height="36" Margin="0,2,0,2" Background="Transparent" Foreground="#cbd5e1" BorderThickness="0" HorizontalContentAlignment="Left" Padding="15,0,0,0" FontSize="11.5" FontWeight="SemiBold"/>
                        <Button Name="btn_act" Content="🔑  Activation Suite" Height="36" Margin="0,2,0,2" Background="Transparent" Foreground="#cbd5e1" BorderThickness="0" HorizontalContentAlignment="Left" Padding="15,0,0,0" FontSize="11.5" FontWeight="SemiBold"/>
                        <Button Name="btn_tweaks" Content="🔧  System Tweaks" Height="36" Margin="0,2,0,2" Background="Transparent" Foreground="#cbd5e1" BorderThickness="0" HorizontalContentAlignment="Left" Padding="15,0,0,0" FontSize="11.5" FontWeight="SemiBold"/>
                        <Button Name="btn_bloat" Content="🧼  Bloatware &amp; Features" Height="36" Margin="0,2,0,2" Background="Transparent" Foreground="#cbd5e1" BorderThickness="0" HorizontalContentAlignment="Left" Padding="15,0,0,0" FontSize="11.5" FontWeight="SemiBold"/>
                        <Button Name="btn_repairs" Content="🛠️  System Repairs" Height="36" Margin="0,2,0,2" Background="Transparent" Foreground="#cbd5e1" BorderThickness="0" HorizontalContentAlignment="Left" Padding="15,0,0,0" FontSize="11.5" FontWeight="SemiBold"/>
                        <Button Name="btn_diag" Content="📊  Diagnostics &amp; Health" Height="36" Margin="0,2,0,2" Background="Transparent" Foreground="#cbd5e1" BorderThickness="0" HorizontalContentAlignment="Left" Padding="15,0,0,0" FontSize="11.5" FontWeight="SemiBold"/>
                        <Button Name="btn_backups" Content="💾  Backups &amp; Migration" Height="36" Margin="0,2,0,2" Background="Transparent" Foreground="#cbd5e1" BorderThickness="0" HorizontalContentAlignment="Left" Padding="15,0,0,0" FontSize="11.5" FontWeight="SemiBold"/>
                        <Button Name="btn_config" Content="⚙️  Windows Config" Height="36" Margin="0,2,0,2" Background="Transparent" Foreground="#cbd5e1" BorderThickness="0" HorizontalContentAlignment="Left" Padding="15,0,0,0" FontSize="11.5" FontWeight="SemiBold"/>
                    </StackPanel>
                </ScrollViewer>

                <TextBlock Grid.Row="2" Text="v1.4.0 | Advanced Power Tools" FontSize="9" Foreground="#4b5563" HorizontalAlignment="Center" VerticalAlignment="Center"/>
            </Grid>
        </Border>

        <!-- Right Content Area -->
        <Grid Grid.Column="1">
            <Grid.RowDefinitions>
                <RowDefinition Height="65"/>
                <RowDefinition Height="*"/>
            </Grid.RowDefinitions>

            <!-- Header -->
            <Border Grid.Row="0" Background="#111827" BorderBrush="#1f2937" BorderThickness="0,0,0,1">
                <Grid Margin="20,0,20,0">
                    <TextBlock Name="txt_header" Text="Dashboard Overview" FontSize="14" FontWeight="Bold" Foreground="#ffffff" VerticalAlignment="Center" HorizontalAlignment="Left"/>
                </Grid>
            </Border>

            <!-- Main Content Views Container -->
            <Grid Grid.Row="1" Margin="20">
                <!-- 1. Dashboard View -->
                <Grid Name="grid_dash" Visibility="Visible">
                    <Grid.RowDefinitions>
                        <RowDefinition Height="Auto"/>
                        <RowDefinition Height="*"/>
                    </Grid.RowDefinitions>

                    <!-- Metric Cards -->
                    <Grid Grid.Row="0">
                        <Grid.ColumnDefinitions>
                            <ColumnDefinition Width="*"/>
                            <ColumnDefinition Width="*"/>
                            <ColumnDefinition Width="*"/>
                            <ColumnDefinition Width="*"/>
                        </Grid.ColumnDefinitions>

                        <!-- OS card -->
                        <Border Grid.Column="0" Background="#1f2937" BorderBrush="#374151" BorderThickness="1" CornerRadius="8" Padding="15" Margin="5">
                            <StackPanel>
                                <TextBlock Text="OS Platform" FontSize="9" Foreground="#9ca3af"/>
                                <TextBlock Name="txt_os" Text="Windows 10/11" FontSize="14" FontWeight="Bold" Foreground="#ffffff" Margin="0,5,0,0"/>
                                <TextBlock Text="64-bit Edition" FontSize="8" Foreground="#38bdf8" Margin="0,2,0,0"/>
                            </StackPanel>
                        </Border>

                        <!-- CPU card -->
                        <Border Grid.Column="1" Background="#1f2937" BorderBrush="#374151" BorderThickness="1" CornerRadius="8" Padding="15" Margin="5">
                            <StackPanel>
                                <TextBlock Text="CPU Load" FontSize="9" Foreground="#9ca3af"/>
                                <TextBlock Name="txt_cpu" Text="0%" FontSize="16" FontWeight="Bold" Foreground="#ffffff" Margin="0,5,0,0"/>
                                <TextBlock Text="Real-time monitor" FontSize="8" Foreground="#10b981" Margin="0,2,0,0"/>
                            </StackPanel>
                        </Border>

                        <!-- RAM card -->
                        <Border Grid.Column="2" Background="#1f2937" BorderBrush="#374151" BorderThickness="1" CornerRadius="8" Padding="15" Margin="5">
                            <StackPanel>
                                <TextBlock Text="Memory Usage" FontSize="9" Foreground="#9ca3af"/>
                                <TextBlock Name="txt_ram" Text="0%" FontSize="16" FontWeight="Bold" Foreground="#ffffff" Margin="0,5,0,0"/>
                                <TextBlock Text="RAM allocation" FontSize="8" Foreground="#38bdf8" Margin="0,2,0,0"/>
                            </StackPanel>
                        </Border>

                        <!-- Storage card -->
                        <Border Grid.Column="3" Background="#1f2937" BorderBrush="#374151" BorderThickness="1" CornerRadius="8" Padding="15" Margin="5">
                            <StackPanel>
                                <TextBlock Text="Disk Free (C:)" FontSize="9" Foreground="#9ca3af"/>
                                <TextBlock Name="txt_disk" Text="Calculating..." FontSize="14" FontWeight="Bold" Foreground="#ffffff" Margin="0,5,0,0"/>
                                <TextBlock Name="txt_uptime" Text="Uptime: Loading..." FontSize="8" Foreground="#cbd5e1" Margin="0,2,0,0"/>
                            </StackPanel>
                        </Border>
                    </Grid>

                    <!-- Activity Log Grid -->
                    <Border Grid.Row="1" Background="#1f2937" BorderBrush="#374151" BorderThickness="1" CornerRadius="8" Margin="5,15,5,5" Padding="15">
                        <Grid>
                            <Grid.RowDefinitions>
                                <RowDefinition Height="Auto"/>
                                <RowDefinition Height="*"/>
                            </Grid.RowDefinitions>
                            <TextBlock Grid.Row="0" Text="📋 Recent Actions &amp; System Diagnostics Logs" FontSize="11" FontWeight="Bold" Foreground="#ffffff" Margin="0,0,0,10"/>
                            <ListView Grid.Row="1" Name="activity_tree" Background="#0b0f19" Foreground="#ffffff" BorderBrush="#374151" FontSize="11">
                                <ListView.View>
                                    <GridView>
                                        <GridViewColumn Header="Operation" Width="150" DisplayMemberBinding="{Binding Operation}"/>
                                        <GridViewColumn Header="Description" Width="440" DisplayMemberBinding="{Binding Description}"/>
                                        <GridViewColumn Header="Status" Width="90" DisplayMemberBinding="{Binding Status}"/>
                                        <GridViewColumn Header="Timestamp" Width="120" DisplayMemberBinding="{Binding Timestamp}"/>
                                    </GridView>
                                </ListView.View>
                            </ListView>
                        </Grid>
                    </Border>
                </Grid>

                <!-- 2. Software Installer View -->
                <Grid Name="grid_soft" Visibility="Collapsed">
                    <Grid.ColumnDefinitions>
                        <ColumnDefinition Width="1.3*"/>
                        <ColumnDefinition Width="*"/>
                    </Grid.ColumnDefinitions>
                    
                    <!-- Left Column: Software Categories Scroll -->
                    <Border Grid.Column="0" Background="#1f2937" BorderBrush="#374151" BorderThickness="1" CornerRadius="8" Padding="15" Margin="0,0,10,0">
                        <Grid>
                            <Grid.RowDefinitions>
                                <RowDefinition Height="Auto"/>
                                <RowDefinition Height="*"/>
                            </Grid.RowDefinitions>
                            <StackPanel Grid.Row="0" Orientation="Horizontal" Margin="0,0,0,10">
                                <Button Name="btn_soft_sel_all" Content="Select All" Width="95" Height="28" Margin="0,0,5,0" Background="#111827"/>
                                <Button Name="btn_soft_desel_all" Content="Deselect All" Width="95" Height="28" Margin="5,0,0,0" Background="#111827"/>
                            </StackPanel>
                            <ScrollViewer Grid.Row="1" VerticalScrollBarVisibility="Auto">
                                <StackPanel>
                                    <TextBlock Text="🌐 Browsers" FontSize="11.5" FontWeight="Bold" Foreground="#38bdf8" Margin="5,5,5,5"/>
                                    <WrapPanel Name="panel_soft_browsers" Orientation="Horizontal" Margin="0,0,0,15"/>
                                    
                                    <TextBlock Text="💻 Microsoft Tools &amp; Platforms" FontSize="11.5" FontWeight="Bold" Foreground="#38bdf8" Margin="5,5,5,5"/>
                                    <WrapPanel Name="panel_soft_msoft" Orientation="Horizontal" Margin="0,0,0,15"/>
                                    
                                    <TextBlock Text="⚙️ Utilities &amp; Chat" FontSize="11.5" FontWeight="Bold" Foreground="#38bdf8" Margin="5,5,5,5"/>
                                    <WrapPanel Name="panel_soft_utils" Orientation="Horizontal" Margin="0,0,0,15"/>
                                    
                                    <TextBlock Text="🔧 Development &amp; Networking" FontSize="11.5" FontWeight="Bold" Foreground="#38bdf8" Margin="5,5,5,5"/>
                                    <WrapPanel Name="panel_soft_dev" Orientation="Horizontal" Margin="0,0,0,15"/>

                                    <TextBlock Text="📄 Office, Design &amp; Media" FontSize="11.5" FontWeight="Bold" Foreground="#38bdf8" Margin="5,5,5,5"/>
                                    <WrapPanel Name="panel_soft_media" Orientation="Horizontal" Margin="0,0,0,15"/>
                                </StackPanel>
                            </ScrollViewer>
                        </Grid>
                    </Border>
                    
                    <!-- Right Column: Operations Terminal -->
                    <Border Grid.Column="1" Background="#1f2937" BorderBrush="#374151" BorderThickness="1" CornerRadius="8" Padding="15" Margin="10,0,0,0">
                        <Grid>
                            <Grid.RowDefinitions>
                                <RowDefinition Height="Auto"/>
                                <RowDefinition Height="*"/>
                                <RowDefinition Height="Auto"/>
                            </Grid.RowDefinitions>
                            <TextBlock Grid.Row="0" Text="⚙️ Installation Terminal" FontSize="11" FontWeight="Bold" Foreground="#ffffff" Margin="0,0,0,10"/>
                            <TextBox Grid.Row="1" Name="txt_log_soft" Background="#0b0f19" Foreground="#10b981" BorderBrush="#374151" FontFamily="Consolas" FontSize="10" IsReadOnly="True" VerticalScrollBarVisibility="Auto" AcceptsReturn="True" TextWrapping="Wrap" Margin="0,0,0,10"/>
                            <StackPanel Grid.Row="2">
                                <Button Name="btn_install_soft" Content="Install Selected" Height="36" Background="#059669" BorderThickness="0" FontWeight="Bold" Margin="0,0,0,5"/>
                                <Button Name="btn_uninstall_soft" Content="Uninstall Selected" Height="36" Background="#b91c1c" BorderThickness="0" FontWeight="Bold" Margin="0,5,0,0"/>
                            </StackPanel>
                        </Grid>
                    </Border>
                </Grid>

                <!-- Other grids under construction -->
                <Grid Name="grid_act" Visibility="Collapsed">
                    <Border Background="#1f2937" BorderBrush="#374151" BorderThickness="1" CornerRadius="8" Padding="30">
                        <TextBlock Text="🔑 Activation Suite is under construction in Phase 3." FontSize="14" Foreground="#9ca3af" HorizontalAlignment="Center" VerticalAlignment="Center"/>
                    </Border>
                </Grid>
                <Grid Name="grid_tweaks" Visibility="Collapsed">
                    <Border Background="#1f2937" BorderBrush="#374151" BorderThickness="1" CornerRadius="8" Padding="30">
                        <TextBlock Text="🔧 System Tweaks is under construction in Phase 4." FontSize="14" Foreground="#9ca3af" HorizontalAlignment="Center" VerticalAlignment="Center"/>
                    </Border>
                </Grid>
                <Grid Name="grid_bloat" Visibility="Collapsed">
                    <Border Background="#1f2937" BorderBrush="#374151" BorderThickness="1" CornerRadius="8" Padding="30">
                        <TextBlock Text="🧼 Bloatware &amp; Features is under construction in Phase 5." FontSize="14" Foreground="#9ca3af" HorizontalAlignment="Center" VerticalAlignment="Center"/>
                    </Border>
                </Grid>
                <Grid Name="grid_repairs" Visibility="Collapsed">
                    <Border Background="#1f2937" BorderBrush="#374151" BorderThickness="1" CornerRadius="8" Padding="30">
                        <TextBlock Text="🛠️ System Repairs is under construction in Phase 6." FontSize="14" Foreground="#9ca3af" HorizontalAlignment="Center" VerticalAlignment="Center"/>
                    </Border>
                </Grid>
                <Grid Name="grid_diag" Visibility="Collapsed">
                    <Border Background="#1f2937" BorderBrush="#374151" BorderThickness="1" CornerRadius="8" Padding="30">
                        <TextBlock Text="📊 Diagnostics &amp; Health is under construction in Phase 7." FontSize="14" Foreground="#9ca3af" HorizontalAlignment="Center" VerticalAlignment="Center"/>
                    </Border>
                </Grid>
                <Grid Name="grid_backups" Visibility="Collapsed">
                    <Border Background="#1f2937" BorderBrush="#374151" BorderThickness="1" CornerRadius="8" Padding="30">
                        <TextBlock Text="💾 Backups &amp; Migration is under construction in Phase 8." FontSize="14" Foreground="#9ca3af" HorizontalAlignment="Center" VerticalAlignment="Center"/>
                    </Border>
                </Grid>
                <Grid Name="grid_config" Visibility="Collapsed">
                    <Border Background="#1f2937" BorderBrush="#374151" BorderThickness="1" CornerRadius="8" Padding="30">
                        <TextBlock Text="⚙️ Windows Config is under construction in Phase 9." FontSize="14" Foreground="#9ca3af" HorizontalAlignment="Center" VerticalAlignment="Center"/>
                    </Border>
                </Grid>
            </Grid>
        </Grid>
    </Grid>
</Window>
"@

$xamlString = $xamlRaw.Trim().Trim([char]0xFEFF)
$reader = (New-Object System.Xml.XmlTextReader (New-Object System.IO.StringReader $xamlString))
$window = [Windows.Markup.XamlReader]::Load($reader)

# Map all Named XAML elements to script variables
[xml]$xmlDoc = $xamlString
$xmlDoc.SelectNodes("//*[@Name]") | ForEach-Object {
    Set-Variable -Name $_.Name -Value $window.FindName($_.Name) -Scope Script
}

# --- GLOBAL UTILITY FUNCTIONS ---
$activities = New-Object System.Collections.ObjectModel.ObservableCollection[PSObject]
$activity_tree.ItemsSource = $activities
[System.Windows.Data.BindingOperations]::EnableCollectionSynchronization($activities, (New-Object System.Object))

$script:runspaces = [System.Collections.ArrayList]::new()
$script:sharedData = [hashtable]::Synchronized(@{
    isTaskRunning = $false
})

# Initialize global RunspacePool at startup
$script:rsp = [runspacefactory]::CreateRunspacePool(1, 10)
$script:rsp.Open()

function Run-Async ($scriptBlock, $ArgumentList=@(), $isLockingTask=$true) {
    if ($isLockingTask -and $script:sharedData.isTaskRunning) {
        return
    }
    if ($isLockingTask) {
        $script:sharedData.isTaskRunning = $true
    }

    $ps = [PowerShell]::Create()
    $ps.RunspacePool = $script:rsp
    
    $helpersDef = @'
        function Log-Message ($msg) {
            $timestamp = Get-Date -Format "HH:mm:ss"
            $formatted = "[$timestamp] $msg`r`n"
            $action = {
                param($text)
                $global:txt_log_soft.AppendText($text)
                $global:txt_log_soft.ScrollToEnd()
                $global:txt_log_rep.AppendText($text)
                $global:txt_log_rep.ScrollToEnd()
            }
            if ($global:win.Dispatcher.CheckAccess()) {
                & $action $formatted
            } else {
                $global:win.Dispatcher.Invoke([Action[string]]$action, $formatted)
            }
        }
        function Add-Activity ($op, $desc, $status) {
            $action = {
                $existing = $null
                foreach ($act in $global:activities) {
                    if ($act.Operation -eq $op -and $act.Status -eq "Running") {
                        $existing = $act
                        break
                    }
                }
                if ($existing -ne $null) {
                    $index = $global:activities.IndexOf($existing)
                    if ($index -ge 0) {
                        $global:activities[$index] = [PSCustomObject]@{
                            Operation = $op
                            Description = $desc
                            Status = $status
                            Timestamp = (Get-Date -Format "HH:mm:ss")
                        }
                    }
                } else {
                    $global:activities.Insert(0, [PSCustomObject]@{
                        Operation = $op
                        Description = $desc
                        Status = $status
                        Timestamp = (Get-Date -Format "HH:mm:ss")
                    })
                }
            }
            if ($global:win.Dispatcher.CheckAccess()) {
                & $action
            } else {
                $global:win.Dispatcher.Invoke([Action]$action)
            }
        }
'@

    $lockVal = if ($isLockingTask) { '$true' } else { '$false' }
    $combinedScript = @"
        param(`$win, `$txt_log_soft, `$txt_log_rep, `$activities, `$sharedData, `$arg1, `$arg2, `$arg3, `$arg4, `$arg5)
        
        `$global:win = `$win
        `$global:txt_log_soft = `$txt_log_soft
        `$global:txt_log_rep = `$txt_log_rep
        `$global:activities = `$activities

        $helpersDef
        
        try {
            & { $scriptBlock } `$win `$arg1 `$arg2 `$arg3 `$arg4 `$arg5
        } finally {
            if ($lockVal) {
                `$sharedData.isTaskRunning = `$false
            }
        }
"@

    $ps.AddScript($combinedScript) | Out-Null
    $ps.AddArgument($window) | Out-Null
    $ps.AddArgument($txt_log_soft) | Out-Null
    $ps.AddArgument($txt_log_rep) | Out-Null
    $ps.AddArgument($activities) | Out-Null
    $ps.AddArgument($script:sharedData) | Out-Null
    foreach ($arg in $ArgumentList) {
        $ps.AddArgument($arg) | Out-Null
    }
    
    $script:runspaces.Add(@{ PS = $ps }) | Out-Null
    $ps.BeginInvoke() | Out-Null
}

function Log-Message ($msg) {
    $timestamp = Get-Date -Format "HH:mm:ss"
    $formatted = "[$timestamp] $msg`r`n"
    $action = {
        param($text)
        $txt_log_soft.AppendText($text)
        $txt_log_soft.ScrollToEnd()
        $txt_log_rep.AppendText($text)
        $txt_log_rep.ScrollToEnd()
    }
    if ($window.Dispatcher.CheckAccess()) {
        & $action $formatted
    } else {
        $window.Dispatcher.Invoke([Action[string]]$action, $formatted)
    }
}

function Add-Activity ($op, $desc, $status) {
    $action = {
        $existing = $null
        foreach ($act in $script:activities) {
            if ($act.Operation -eq $op -and $act.Status -eq "Running") {
                $existing = $act
                break
            }
        }
        if ($existing -ne $null) {
            $index = $script:activities.IndexOf($existing)
            if ($index -ge 0) {
                $script:activities[$index] = [PSCustomObject]@{
                    Operation = $op
                    Description = $desc
                    Status = $status
                    Timestamp = (Get-Date -Format "HH:mm:ss")
                }
            }
        } else {
            $script:activities.Insert(0, [PSCustomObject]@{
                Operation = $op
                Description = $desc
                Status = $status
                Timestamp = (Get-Date -Format "HH:mm:ss")
            })
        }
    }
    if ($window.Dispatcher.CheckAccess()) {
        & $action
    } else {
        $window.Dispatcher.Invoke([Action]$action)
    }
}

function Switch-View ($viewName) {
    $views = @("grid_dash", "grid_soft", "grid_act", "grid_tweaks", "grid_bloat", "grid_repairs", "grid_diag", "grid_backups", "grid_config")
    $titles = @{
        "grid_dash" = "Dashboard Overview"
        "grid_soft" = "Silent Software Installer Hub"
        "grid_act"  = "Windows & Office Activation (MAS)"
        "grid_tweaks" = "Premium OS Registry Tweaks"
        "grid_bloat" = "Windows Bloatware & Features"
        "grid_repairs" = "System Command & Cache Repairs"
        "grid_diag" = "Hardware Diagnostics & Reports"
        "grid_backups" = "Backups & Data Migration"
        "grid_config" = "Windows Optimization Config"
    }
    
    foreach ($v in $views) {
        $element = $window.FindName($v)
        if ($element) {
            if ($v -eq $viewName) {
                $element.Visibility = "Visible"
            } else {
                $element.Visibility = "Collapsed"
            }
        }
    }
    
    $txt_header.Text = $titles[$viewName]
    
    # Reset sidebar button active highlights
    $btnNames = @("btn_dash", "btn_soft", "btn_act", "btn_tweaks", "btn_bloat", "btn_repairs", "btn_diag", "btn_backups", "btn_config")
    foreach ($b in $btnNames) {
        $btn = $window.FindName($b)
        if ($btn) {
            if ($b -eq "btn_" + $viewName.Substring(5)) {
                $btn.Background = [System.Windows.Media.BrushConverter]::new().ConvertFromString("#1e293b")
            } else {
                $btn.Background = [System.Windows.Media.Brushes]::Transparent
            }
        }
    }
}

# Bind Navigation Clicks
$btn_dash.Add_Click({ Switch-View "grid_dash" })
$btn_soft.Add_Click({ Switch-View "grid_soft" })
$btn_act.Add_Click({ Switch-View "grid_act" })
$btn_tweaks.Add_Click({ Switch-View "grid_tweaks" })
$btn_bloat.Add_Click({ Switch-View "grid_bloat" })
$btn_repairs.Add_Click({ Switch-View "grid_repairs" })
$btn_diag.Add_Click({ Switch-View "grid_diag" })
$btn_backups.Add_Click({ Switch-View "grid_backups" })
$btn_config.Add_Click({ Switch-View "grid_config" })

# Retrieve OS Name cleanly from registry
try {
    $txt_os.Text = (Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion" -ErrorAction Stop).ProductName
} catch {
    $txt_os.Text = [Environment]::OSVersion.VersionString
}

# Add startup log entry
Add-Activity "Dashboard" "System Utility Toolkit initialized" "Success"

# Start Async metrics poller
Run-Async {
    param($win)
    
    Add-Type -AssemblyName Microsoft.VisualBasic -ErrorAction SilentlyContinue
    $computerInfo = New-Object Microsoft.VisualBasic.Devices.ComputerInfo
    $drive = New-Object System.IO.DriveInfo("C")
    
    while ($true) {
        # CPU
        $cpu = (Get-CimInstance Win32_PerfFormattedData_PerfOS_Processor | Where-Object { $_.Name -eq '_Total' }).PercentProcessorTime
        if ($cpu -eq $null) { $cpu = 0 }
        $cpuStr = "{0:N0}%" -f $cpu
        
        # RAM
        $totalRam = $computerInfo.TotalPhysicalMemory
        $freeRam = $computerInfo.AvailablePhysicalMemory
        $ramPct = [Math]::Round((($totalRam - $freeRam) / $totalRam) * 100)
        $ramStr = "${ramPct}%"
        
        # Disk Free
        $diskFreeGB = [Math]::Round($drive.AvailableFreeSpace / 1GB)
        $diskStr = "${diskFreeGB} GB Free"
        
        # Uptime
        $uptimeMS = [Environment]::TickCount
        if ($uptimeMS -lt 0) { $uptimeMS = $uptimeMS + [Double]::MaxValue } # Handle wrap
        $uptime = [TimeSpan]::FromMilliseconds($uptimeMS)
        $uptimeStr = "{0}d {1}h {2}m" -f $uptime.Days, $uptime.Hours, $uptime.Minutes
        
        $win.Dispatcher.Invoke([Action]{
            ($win.FindName("txt_cpu")).Text = $cpuStr
            ($win.FindName("txt_ram")).Text = $ramStr
            ($win.FindName("txt_disk")).Text = $diskStr
            ($win.FindName("txt_uptime")).Text = "Uptime: $uptimeStr"
        })
        
        Start-Sleep -Seconds 2
    }
} -isLockingTask $false

# --- Phase 2: SOFTWARE LISTS & INSTALLATION LOGIC ---

$browsers = @(
    @{ Name = "Google Chrome"; Id = "Google.Chrome" }
    @{ Name = "Mozilla Firefox"; Id = "Mozilla.Firefox" }
    @{ Name = "Brave Browser"; Id = "Brave.Brave" }
    @{ Name = "Opera Browser"; Id = "Opera.Opera" }
    @{ Name = "Vivaldi Browser"; Id = "VivaldiTechnologies.Vivaldi" }
    @{ Name = "Arc Browser"; Id = "TheBrowserCompany.Arc" }
    @{ Name = "Microsoft Edge"; Id = "Microsoft.Edge" }
)

$msoft = @(
    @{ Name = "Microsoft Teams"; Id = "Microsoft.Teams" }
    @{ Name = "Windows Terminal"; Id = "Microsoft.WindowsTerminal" }
    @{ Name = "Sysinternals Suite"; Id = "Microsoft.SysinternalsSuite" }
    @{ Name = "PowerShell 7 Core"; Id = "Microsoft.PowerShell" }
    @{ Name = "VS 2022 Community"; Id = "Microsoft.VisualStudio.2022.Community" }
    @{ Name = "Microsoft Office 365"; Id = "Microsoft.Office" }
    @{ Name = "PowerBI Desktop"; Id = "Microsoft.PowerBIDesktop" }
    @{ Name = "OneDrive Client"; Id = "Microsoft.OneDrive" }
    @{ Name = "Remote Desktop"; Id = "Microsoft.RemoteDesktop" }
    @{ Name = "SQL Studio (SSMS)"; Id = "Microsoft.SQLServerManagementStudio" }
)

$utils = @(
    @{ Name = "7-Zip (Archiver)"; Id = "7zip.7zip" }
    @{ Name = "Notepad++ (Editor)"; Id = "Notepad++.Notepad++" }
    @{ Name = "VLC Media Player"; Id = "VideoLAN.VLC" }
    @{ Name = "Discord Client"; Id = "Discord.Discord" }
    @{ Name = "Telegram Desktop"; Id = "Telegram.TelegramDesktop" }
    @{ Name = "WhatsApp Desktop"; Id = "WhatsApp.WhatsApp" }
    @{ Name = "Steam Client"; Id = "Valve.Steam" }
    @{ Name = "Microsoft PowerToys"; Id = "Microsoft.PowerToys" }
    @{ Name = "Rufus USB Boot"; Id = "Akeo.Rufus" }
    @{ Name = "WinRAR Archiver"; Id = "RARLab.WinRAR" }
    @{ Name = "Everything Search"; Id = "Voidtools.Everything" }
    @{ Name = "BleachBit Cleaner"; Id = "BleachBit.BleachBit" }
    @{ Name = "AnyDesk Utility"; Id = "AnyDeskSoftwareGmbH.AnyDesk" }
    @{ Name = "TeamViewer Client"; Id = "TeamViewer.TeamViewer" }
    @{ Name = "LDPlayer 9 Android"; Id = "XuanZhi.LDPlayer9" }
)

$devs = @(
    @{ Name = "VS Code Editor"; Id = "Microsoft.VisualStudioCode" }
    @{ Name = "Git SCM Tool"; Id = "Git.Git" }
    @{ Name = "Python 3.12"; Id = "Python.Python.3.12" }
    @{ Name = "Node.js LTS Runtime"; Id = "OpenJS.NodeJS.LTS" }
    @{ Name = "DBeaver Community"; Id = "dbeaver.dbeaver" }
    @{ Name = "IntelliJ IDEA Comm"; Id = "JetBrains.IntelliJIDEA.Community" }
    @{ Name = "Docker Desktop"; Id = "Docker.DockerDesktop" }
    @{ Name = "WSL Ubuntu Distro"; Id = "Canonical.Ubuntu" }
    @{ Name = "Cisco Packet Tracer"; Id = "Cisco.PacketTracer" }
    @{ Name = "WinSCP SFTP client"; Id = "WinSCP.WinSCP" }
    @{ Name = "FileZilla FTP client"; Id = "TimKosse.FileZilla.Client" }
    @{ Name = "Oracle VirtualBox"; Id = "Oracle.VirtualBox" }
    @{ Name = "Wireshark Analyzer"; Id = "Wireshark.Wireshark" }
    @{ Name = "Nmap Port Scanner"; Id = "Insecure.Nmap" }
    @{ Name = "PuTTY SSH Client"; Id = "SimonTatham.PuTTY" }
)

$media = @(
    @{ Name = "LibreOffice Suite"; Id = "LibreOffice.LibreOffice" }
    @{ Name = "GIMP Image Editor"; Id = "GIMP.GIMP" }
    @{ Name = "Blender 3D Suite"; Id = "BlenderFoundation.Blender" }
    @{ Name = "Adobe Reader DC"; Id = "Adobe.AdobeReaderext.Language.English" }
    @{ Name = "Zoom Conferences"; Id = "Zoom.Zoom" }
    @{ Name = "OBS Studio Recorder"; Id = "Obsproject.OBSStudio" }
    @{ Name = "Spotify Music"; Id = "Spotify.Spotify" }
)

$checkboxes = @()

function Add-Softwares($list, $panel) {
    foreach ($app in $list) {
        $cb = New-Object System.Windows.Controls.CheckBox
        $cb.Content = $app.Name
        $cb.Tag = $app.Id
        $cb.Foreground = [System.Windows.Media.Brushes]::White
        $cb.Margin = "8"
        $cb.Width = 185
        $cb.FontSize = 11
        $cb.FontWeight = [System.Windows.FontWeights]::SemiBold
        $panel.Children.Add($cb) | Out-Null
        $script:checkboxes += $cb
    }
}

# Dynamically populate software category WrapPanels
Add-Softwares $browsers $panel_soft_browsers
Add-Softwares $msoft $panel_soft_msoft
Add-Softwares $utils $panel_soft_utils
Add-Softwares $devs $panel_soft_dev
Add-Softwares $media $panel_soft_media

# Select / Deselect Callbacks
$btn_soft_sel_all.Add_Click({
    $script:checkboxes | ForEach-Object { $_.IsChecked = $true }
})
$btn_soft_desel_all.Add_Click({
    $script:checkboxes | ForEach-Object { $_.IsChecked = $false }
})

# Install Selected
$btn_install_soft.Add_Click({
    $selected = $script:checkboxes | Where-Object { $_.IsChecked -eq $true }
    if ($selected.Count -eq 0) {
        [System.Windows.MessageBox]::Show("Please select at least one software package to install.", "Warning", "OK", "Warning")
        return
    }
    
    Log-Message "Starting installation batch..."
    Add-Activity "Software Installer" "Starting installation batch" "Running"
    
    $itemsArray = @()
    foreach ($item in $selected) {
        $itemsArray += @{ Name = $item.Content; Id = $item.Tag }
    }

    Run-Async {
        param($win, $items)
        foreach ($item in $items) {
            $name = $item.Name
            $id = $item.Id
            $win.Dispatcher.Invoke([Action]{ Log-Message "Installing $name..." })
            
            $proc = Start-Process winget -ArgumentList "install --id $id --silent --accept-source-agreements --accept-package-agreements" -NoNewWindow -PassThru -Wait
            if ($proc.ExitCode -eq 0) {
                $win.Dispatcher.Invoke([Action]{ 
                    Log-Message "[OK] $name installed successfully."
                    Add-Activity "WinGet Installer" "$name installed successfully" "Success"
                })
            } else {
                $win.Dispatcher.Invoke([Action]{ 
                    Log-Message "[FAIL] $name failed or was already installed."
                    Add-Activity "WinGet Installer" "$name install failed" "Failed"
                })
            }
        }
        $win.Dispatcher.Invoke([Action]{ 
            Log-Message "Installation batch completed." 
            Add-Activity "Software Installer" "Installation batch completed" "Success"
        })
    } @(,$itemsArray)
})

# Uninstall Selected
$btn_uninstall_soft.Add_Click({
    $selected = $script:checkboxes | Where-Object { $_.IsChecked -eq $true }
    if ($selected.Count -eq 0) {
        [System.Windows.MessageBox]::Show("Please select at least one software package to uninstall.", "Warning", "OK", "Warning")
        return
    }
    
    Log-Message "Starting uninstallation batch..."
    Add-Activity "Software Installer" "Starting uninstallation batch" "Running"
    
    $itemsArray = @()
    foreach ($item in $selected) {
        $itemsArray += @{ Name = $item.Content; Id = $item.Tag }
    }

    Run-Async {
        param($win, $items)
        foreach ($item in $items) {
            $name = $item.Name
            $id = $item.Id
            $win.Dispatcher.Invoke([Action]{ Log-Message "Uninstalling $name..." })
            
            $proc = Start-Process winget -ArgumentList "uninstall --id $id --silent" -NoNewWindow -PassThru -Wait
            if ($proc.ExitCode -eq 0) {
                $win.Dispatcher.Invoke([Action]{ 
                    Log-Message "[OK] $name uninstalled successfully."
                    Add-Activity "WinGet Installer" "$name uninstalled successfully" "Success"
                })
            } else {
                $win.Dispatcher.Invoke([Action]{ 
                    Log-Message "[FAIL] $name failed to uninstall."
                    Add-Activity "WinGet Installer" "$name uninstall failed" "Failed"
                })
            }
        }
        $win.Dispatcher.Invoke([Action]{ 
            Log-Message "Uninstallation batch completed." 
            Add-Activity "Software Installer" "Uninstallation batch completed" "Success"
        })
    } @(,$itemsArray)
})

# Launch GUI
$window.ShowDialog() | Out-Null

# Cleanup Runspaces on close
$script:rsp.Close()
$script:runspaces | ForEach-Object { $_.PS.Dispose() }
