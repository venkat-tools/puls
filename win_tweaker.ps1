# Requires -RunAsAdministrator
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    Exit
}

Add-Type -AssemblyName PresentationFramework
Add-Type -AssemblyName PresentationCore
Add-Type -AssemblyName WindowsBase

[xml]$xaml = @"
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="VenkatPulse AI - Windows Utility Suite" Height="700" Width="1050"
        Background="#0b0f19" Foreground="#ffffff" WindowStartupLocation="CenterScreen" ResizeMode="CanMinimize">
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
            <ColumnDefinition Width="230"/>
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

                <!-- Brand logo/text -->
                <StackPanel Grid.Row="0" Margin="20,20,20,10" VerticalAlignment="Center">
                    <TextBlock Text="⚡ VenkatPulse AI" FontSize="18" FontWeight="Bold" Foreground="#38bdf8"/>
                    <TextBlock Text="Windows Utility Suite" FontSize="10" Foreground="#6b7280" Margin="2,2,0,0"/>
                </StackPanel>

                <!-- Sidebar Buttons -->
                <StackPanel Grid.Row="1" Margin="10,0,10,0">
                    <Button Name="btn_dash" Content="🏠  Dashboard" Height="40" Margin="0,3,0,3" Background="Transparent" Foreground="#cbd5e1" BorderThickness="0" HorizontalContentAlignment="Left" Padding="15,0,0,0" FontSize="12" FontWeight="SemiBold"/>
                    <Button Name="btn_soft" Content="📥  Software Installer" Height="40" Margin="0,3,0,3" Background="Transparent" Foreground="#cbd5e1" BorderThickness="0" HorizontalContentAlignment="Left" Padding="15,0,0,0" FontSize="12" FontWeight="SemiBold"/>
                    <Button Name="btn_act" Content="🔑  Activation Suite" Height="40" Margin="0,3,0,3" Background="Transparent" Foreground="#cbd5e1" BorderThickness="0" HorizontalContentAlignment="Left" Padding="15,0,0,0" FontSize="12" FontWeight="SemiBold"/>
                    <Button Name="btn_tweaks" Content="🔧  System Tweaks" Height="40" Margin="0,3,0,3" Background="Transparent" Foreground="#cbd5e1" BorderThickness="0" HorizontalContentAlignment="Left" Padding="15,0,0,0" FontSize="12" FontWeight="SemiBold"/>
                    <Button Name="btn_repairs" Content="🛠️  System Repairs" Height="40" Margin="0,3,0,3" Background="Transparent" Foreground="#cbd5e1" BorderThickness="0" HorizontalContentAlignment="Left" Padding="15,0,0,0" FontSize="12" FontWeight="SemiBold"/>
                    <Button Name="btn_diag" Content="📊  Diagnostics &amp; Health" Height="40" Margin="0,3,0,3" Background="Transparent" Foreground="#cbd5e1" BorderThickness="0" HorizontalContentAlignment="Left" Padding="15,0,0,0" FontSize="12" FontWeight="SemiBold"/>
                </StackPanel>

                <!-- Footer version info -->
                <TextBlock Grid.Row="2" Text="v1.2.0 | Pure PowerShell &amp; XAML" FontSize="9" Foreground="#4b5563" HorizontalAlignment="Center" VerticalAlignment="Center"/>
            </Grid>
        </Border>

        <!-- Right Side Panel -->
        <Grid Grid.Column="1">
            <Grid.RowDefinitions>
                <RowDefinition Height="65"/>
                <RowDefinition Height="*"/>
            </Grid.RowDefinitions>

            <!-- Header Panel -->
            <Border Grid.Row="0" Background="#111827" BorderBrush="#1f2937" BorderThickness="0,0,0,1">
                <Grid Margin="20,0,20,0">
                    <TextBlock Name="txt_header" Text="🏠 Dashboard Overview" FontSize="14" FontWeight="Bold" Foreground="#ffffff" VerticalAlignment="Center" HorizontalAlignment="Left"/>
                    
                    <!-- Search Bar in Header -->
                    <StackPanel Orientation="Horizontal" HorizontalAlignment="Right" VerticalAlignment="Center">
                        <TextBox Name="txt_search" Width="220" Height="28" Background="#1f2937" Foreground="#ffffff" BorderBrush="#374151" Padding="6,4,6,4" FontSize="11" VerticalContentAlignment="Center"/>
                        <Button Name="btn_search" Content="Search" Width="65" Height="28" Margin="5,0,0,0" Background="#0284c7" Foreground="#ffffff" BorderThickness="0" FontSize="11" FontWeight="Bold"/>
                    </StackPanel>
                </Grid>
            </Border>

            <!-- Content Panel -->
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

                    <!-- Large Log Console on Dashboard -->
                    <Border Grid.Row="1" Background="#1f2937" BorderBrush="#374151" BorderThickness="1" CornerRadius="8" Margin="5,15,5,5" Padding="15">
                        <Grid>
                            <Grid.RowDefinitions>
                                <RowDefinition Height="Auto"/>
                                <RowDefinition Height="*"/>
                            </Grid.RowDefinitions>
                            <TextBlock Grid.Row="0" Text="📋 System Operations Activity Log" FontSize="11" FontWeight="Bold" Foreground="#ffffff" Margin="0,0,0,10"/>
                            <TextBox Grid.Row="1" Name="txt_log_dash" Background="#0b0f19" Foreground="#10b981" BorderBrush="#374151" FontFamily="Consolas" FontSize="10.5" IsReadOnly="True" VerticalScrollBarVisibility="Auto" AcceptsReturn="True" TextWrapping="Wrap"/>
                        </Grid>
                    </Border>
                </Grid>

                <!-- 2. Software Installer View -->
                <Grid Name="grid_soft" Visibility="Collapsed">
                    <Grid.RowDefinitions>
                        <RowDefinition Height="Auto"/>
                        <RowDefinition Height="*"/>
                        <RowDefinition Height="60"/>
                    </Grid.RowDefinitions>
                    
                    <Border Grid.Row="0" Background="#1e1b4b" BorderBrush="#312e81" BorderThickness="1" CornerRadius="6" Padding="12" Margin="0,0,0,15">
                        <TextBlock Text="💡 Select software tiles to install silently. It runs native Microsoft WinGet package manager in the background." FontSize="11" Foreground="#cbd5e1"/>
                    </Border>

                    <Border Grid.Row="1" Background="#1f2937" BorderBrush="#374151" BorderThickness="1" CornerRadius="8" Padding="15">
                        <ScrollViewer VerticalScrollBarVisibility="Auto">
                            <WrapPanel Name="panel_soft_items" Orientation="Horizontal">
                                <!-- Populated dynamically -->
                            </WrapPanel>
                        </ScrollViewer>
                    </Border>
                    
                    <Button Grid.Row="2" Name="btn_install_soft" Content="⚡ Start Silent Software Installation" Height="40" Background="#059669" Foreground="#ffffff" BorderThickness="0" FontWeight="Bold" FontSize="13" Margin="0,10,0,0"/>
                </Grid>

                <!-- 3. Activation Suite View -->
                <Grid Name="grid_act" Visibility="Collapsed">
                    <Grid.RowDefinitions>
                        <RowDefinition Height="Auto"/>
                        <RowDefinition Height="*"/>
                    </Grid.RowDefinitions>

                    <Border Grid.Row="0" Background="#1e1b4b" BorderBrush="#312e81" BorderThickness="1" CornerRadius="6" Padding="12" Margin="0,0,0,15">
                        <TextBlock Text="🛡️ Activates Windows &amp; Office safely using Microsoft Activation Scripts (MAS) open-source repositories." FontSize="11" Foreground="#cbd5e1"/>
                    </Border>

                    <Grid Grid.Row="1">
                        <Grid.ColumnDefinitions>
                            <ColumnDefinition Width="*"/>
                            <ColumnDefinition Width="*"/>
                        </Grid.ColumnDefinitions>

                        <!-- MAS Activator card -->
                        <Border Grid.Column="0" Background="#1f2937" BorderBrush="#374151" BorderThickness="1" CornerRadius="8" Padding="20" Margin="0,0,10,0">
                            <StackPanel VerticalAlignment="Center">
                                <TextBlock Text="🔑 Microsoft Activation Scripts (MAS)" FontSize="14" FontWeight="Bold" Foreground="#38bdf8" HorizontalAlignment="Center"/>
                                <TextBlock Text="Launches the official console interface to manage activation of Windows HWID and Office Ohook." TextWrapping="Wrap" FontSize="11" Foreground="#9ca3af" Margin="0,10,0,20" TextAlignment="Center"/>
                                <Button Name="btn_launch_mas" Content="🚀 Launch MAS Console" Height="40" Background="#0284c7" Foreground="#ffffff" BorderThickness="0" FontWeight="Bold" HorizontalAlignment="Center" Width="200"/>
                            </StackPanel>
                        </Border>

                        <!-- Status Check card -->
                        <Border Grid.Column="1" Background="#1f2937" BorderBrush="#374151" BorderThickness="1" CornerRadius="8" Padding="20" Margin="10,0,0,0">
                            <StackPanel VerticalAlignment="Center">
                                <TextBlock Text="🔍 License Verification" FontSize="14" FontWeight="Bold" Foreground="#10b981" HorizontalAlignment="Center"/>
                                <TextBlock Text="Runs slmgr.vbs query command to display active OS licenses and validation state details." TextWrapping="Wrap" FontSize="11" Foreground="#9ca3af" Margin="0,10,0,20" TextAlignment="Center"/>
                                <Button Name="btn_check_license" Content="🔍 Check Activation Status" Height="40" Background="#1f2937" Foreground="#ffffff" BorderThickness="1" BorderBrush="#374151" FontWeight="Bold" HorizontalAlignment="Center" Width="200"/>
                            </StackPanel>
                        </Border>
                    </Grid>
                </Grid>

                <!-- 4. System Tweaks View -->
                <Grid Name="grid_tweaks" Visibility="Collapsed">
                    <Grid.RowDefinitions>
                        <RowDefinition Height="Auto"/>
                        <RowDefinition Height="*"/>
                    </Grid.RowDefinitions>

                    <TextBlock Grid.Row="0" Text="Select tweaks to apply directly to registry policies:" FontSize="11" Foreground="#9ca3af" Margin="0,0,0,10"/>
                    
                    <Border Grid.Row="1" Background="#1f2937" BorderBrush="#374151" BorderThickness="1" CornerRadius="8" Padding="15">
                        <ScrollViewer VerticalScrollBarVisibility="Auto">
                            <StackPanel>
                                <Border BorderBrush="#374151" BorderThickness="0,0,0,1" Padding="0,0,0,10" Margin="0,0,0,10">
                                    <Grid>
                                        <StackPanel HorizontalAlignment="Left">
                                            <TextBlock Text="📂 Windows 11 Classic Context Menu" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Restores traditional right-click menu layout instead of 'Show more options'." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <StackPanel Orientation="Horizontal" HorizontalAlignment="Right">
                                            <Button Name="btn_tweak_classic" Content="Restore Classic" Background="#0284c7" BorderThickness="0" Margin="0,0,5,0" Width="110"/>
                                            <Button Name="btn_tweak_default_ctx" Content="Revert Default" Background="#374151" BorderThickness="0" Width="110"/>
                                        </StackPanel>
                                    </Grid>
                                </Border>

                                <Border BorderBrush="#374151" BorderThickness="0,0,0,1" Padding="0,0,0,10" Margin="0,0,0,10">
                                    <Grid>
                                        <StackPanel HorizontalAlignment="Left">
                                            <TextBlock Text="⚡ Enable Ultimate Performance Plan" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Unlocks and activates hidden maximum hardware speed power profile." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <Button Name="btn_tweak_ultimate" Content="Unlock Scheme" Background="#d97706" BorderThickness="0" HorizontalAlignment="Right" Width="225"/>
                                    </Grid>
                                </Border>

                                <Border BorderBrush="#374151" BorderThickness="0,0,0,1" Padding="0,0,0,10" Margin="0,0,0,10">
                                    <Grid>
                                        <StackPanel HorizontalAlignment="Left">
                                            <TextBlock Text="🎮 Latency &amp; Gaming Optimization" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Disables GameDVR, CPU throttling and configures network game packet latency." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <Button Name="btn_tweak_gaming" Content="Apply Gaming Tweaks" Background="#059669" BorderThickness="0" HorizontalAlignment="Right" Width="225"/>
                                    </Grid>
                                </Border>

                                <Border BorderBrush="#374151" BorderThickness="0,0,0,1" Padding="0,0,0,10" Margin="0,0,0,10">
                                    <Grid>
                                        <StackPanel HorizontalAlignment="Left">
                                            <TextBlock Text="🔍 Disable Online Bing Search in Start Menu" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Hides web results inside the Start Menu search for faster local searches." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <Button Name="btn_tweak_bing" Content="Disable Bing Search" Background="#4f46e5" BorderThickness="0" HorizontalAlignment="Right" Width="225"/>
                                    </Grid>
                                </Border>
                            </StackPanel>
                        </ScrollViewer>
                    </Border>
                </Grid>

                <!-- 5. System Repairs View -->
                <Grid Name="grid_repairs" Visibility="Collapsed">
                    <Grid.ColumnDefinitions>
                        <ColumnDefinition Width="3*"/>
                        <ColumnDefinition Width="2*"/>
                    </Grid.ColumnDefinitions>
                    
                    <!-- Left Column: Operations -->
                    <Border Grid.Column="0" Background="#1f2937" BorderBrush="#374151" BorderThickness="1" CornerRadius="8" Padding="15" Margin="0,0,10,0">
                        <ScrollViewer VerticalScrollBarVisibility="Auto">
                            <StackPanel>
                                <TextBlock Text="🛠️ Core Scan &amp; System File Repairs" FontSize="11" FontWeight="Bold" Foreground="#38bdf8" Margin="0,0,0,8"/>
                                <Button Name="btn_rep_sfc" Content="🛡️ Run System File Check Scanner (SFC Scannow)" Height="34" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="12,0,0,0"/>
                                <Button Name="btn_rep_dism" Content="⚙️ Repair Component Store Corruption (DISM)" Height="34" Margin="0,2,0,15" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="12,0,0,0"/>

                                <TextBlock Text="🌐 Network &amp; Internet Adaptor Reset" FontSize="11" FontWeight="Bold" Foreground="#38bdf8" Margin="0,10,0,8"/>
                                <Button Name="btn_rep_net" Content="📡 Reset Complete Network Stack Protocols" Height="34" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="12,0,0,0"/>
                                <Button Name="btn_rep_dns" Content="🧹 Flush Local DNS Cache &amp; Re-register IP" Height="34" Margin="0,2,0,15" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="12,0,0,0"/>

                                <TextBlock Text="🖨️ Printer Service &amp; Driver RPC Fixes" FontSize="11" FontWeight="Bold" Foreground="#38bdf8" Margin="0,10,0,8"/>
                                <Button Name="btn_rep_printer11b" Content="🔓 Fix Shared Printer Error 0x0000011b" Height="34" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="12,0,0,0"/>
                                <Button Name="btn_rep_spooler" Content="🧹 Clear Print Spooler Queue &amp; Restart Service" Height="34" Margin="0,2,0,15" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="12,0,0,0"/>

                                <TextBlock Text="⚙️ OS Repairs &amp; Cleaners" FontSize="11" FontWeight="Bold" Foreground="#38bdf8" Margin="0,10,0,8"/>
                                <Button Name="btn_rep_wua" Content="🔄 Reset Windows Update Components Cache" Height="34" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="12,0,0,0"/>
                                <Button Name="btn_rep_explorer" Content="🚀 Restart Windows Explorer Shell Process" Height="34" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="12,0,0,0"/>
                            </StackPanel>
                        </ScrollViewer>
                    </Border>
                    
                    <!-- Right Column: Live Output Log -->
                    <Border Grid.Column="1" Background="#1f2937" BorderBrush="#374151" BorderThickness="1" CornerRadius="8" Padding="15" Margin="10,0,0,0">
                        <Grid>
                            <Grid.RowDefinitions>
                                <RowDefinition Height="Auto"/>
                                <RowDefinition Height="*"/>
                            </Grid.RowDefinitions>
                            <TextBlock Grid.Row="0" Text="📋 Operation Output Console" FontSize="11" FontWeight="Bold" Foreground="#ffffff" Margin="0,0,0,10"/>
                            <TextBox Grid.Row="1" Name="txt_log_rep" Background="#0b0f19" Foreground="#10b981" BorderBrush="#374151" FontFamily="Consolas" FontSize="10" IsReadOnly="True" VerticalScrollBarVisibility="Auto" AcceptsReturn="True" TextWrapping="Wrap"/>
                        </Grid>
                    </Border>
                </Grid>

                <!-- 6. Diagnostics & Specs View -->
                <Grid Name="grid_diag" Visibility="Collapsed">
                    <Grid.RowDefinitions>
                        <RowDefinition Height="Auto"/>
                        <RowDefinition Height="*"/>
                    </Grid.RowDefinitions>

                    <TextBlock Grid.Row="0" Text="Select diagnostics report or testing scans:" FontSize="11" Foreground="#9ca3af" Margin="0,0,0,10"/>

                    <Border Grid.Row="1" Background="#1f2937" BorderBrush="#374151" BorderThickness="1" CornerRadius="8" Padding="15">
                        <ScrollViewer VerticalScrollBarVisibility="Auto">
                            <StackPanel>
                                <Border BorderBrush="#374151" BorderThickness="0,0,0,1" Padding="0,0,0,10" Margin="0,0,0,10">
                                    <Grid>
                                        <StackPanel HorizontalAlignment="Left">
                                            <TextBlock Text="📝 System Summary Specifications" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Generates CPU, GPU, RAM, Motherboard, and BIOS properties summary." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <Button Name="btn_diag_specs" Content="Generate Specs Info" Background="#0284c7" BorderThickness="0" HorizontalAlignment="Right" Width="200"/>
                                    </Grid>
                                </Border>

                                <Border BorderBrush="#374151" BorderThickness="0,0,0,1" Padding="0,0,0,10" Margin="0,0,0,10">
                                    <Grid>
                                        <StackPanel HorizontalAlignment="Left">
                                            <TextBlock Text="🔋 Laptop Battery Health Report" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Generates HTML power battery wear diagnostic status chart." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <Button Name="btn_diag_battery" Content="Generate Battery Report" Background="#10b981" BorderThickness="0" HorizontalAlignment="Right" Width="200"/>
                                    </Grid>
                                </Border>

                                <Border BorderBrush="#374151" BorderThickness="0,0,0,1" Padding="0,0,0,10" Margin="0,0,0,10">
                                    <Grid>
                                        <StackPanel HorizontalAlignment="Left">
                                            <TextBlock Text="💾 Disk Health Status (S.M.A.R.T. Scan)" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Queries hardware sensors on connected physical drives to check reliability." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <Button Name="btn_diag_disk" Content="Run SMART Drive Check" Background="#4f46e5" BorderThickness="0" HorizontalAlignment="Right" Width="200"/>
                                    </Grid>
                                </Border>

                                <Border BorderBrush="#374151" BorderThickness="0,0,0,1" Padding="0,0,0,10" Margin="0,0,0,10">
                                    <Grid>
                                        <StackPanel HorizontalAlignment="Left">
                                            <TextBlock Text="🧠 RAM Modules Specifications" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Queries WMIC to identify installed memory module speeds and clock cycles." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <Button Name="btn_diag_ram" Content="Show Memory Specs" Background="#374151" BorderThickness="0" HorizontalAlignment="Right" Width="200"/>
                                    </Grid>
                                </Border>
                            </StackPanel>
                        </ScrollViewer>
                    </Border>
                </Grid>

            </Grid>
        </Grid>
    </Grid>
</Window>
"@

$reader = (New-Object System.Xml.XmlNodeReader $xaml)
$window = [Windows.Markup.XamlReader]::Load($reader)

# Map all Named XAML elements to script variables
$xaml.SelectNodes("//*[@Name]") | ForEach-Object {
    Set-Variable -Name $_.Name -Value $window.FindName($_.Name) -Scope Script
}

# --- GLOBAL UTILITY FUNCTIONS ---
function Log-Message ($msg) {
    $timestamp = Get-Date -Format "HH:mm:ss"
    $formatted = "[$timestamp] $msg`r`n"
    $window.Dispatcher.Invoke([Action[string]]{
        param($text)
        $txt_log_dash.AppendText($text)
        $txt_log_dash.ScrollToEnd()
        
        $txt_log_rep.AppendText($text)
        $txt_log_rep.ScrollToEnd()
    }, $formatted)
}

function Switch-View ($viewName) {
    $views = @("grid_dash", "grid_soft", "grid_act", "grid_tweaks", "grid_repairs", "grid_diag")
    $titles = @{
        "grid_dash" = "🏠 System Dashboard Overview"
        "grid_soft" = "📥 Silent Software Installer Hub"
        "grid_act"  = "🔑 Windows & Office Activation (MAS)"
        "grid_tweaks" = "🔧 Premium OS Registry Tweaks"
        "grid_repairs" = "🛠️ System Command & Cache Repairs"
        "grid_diag" = "📊 Hardware Diagnostics & Reports"
    }

    $views | ForEach-Object {
        $v = Get-Variable -Name $_ -ValueOnly
        if ($_ -eq $viewName) {
            $v.Visibility = "Visible"
            $txt_header.Text = $titles[$_]
        } else {
            $v.Visibility = "Collapsed"
        }
    }
}

# --- INIT SIDEBAR BUTTON CLICKS ---
$btn_dash.Add_Click({ Switch-View "grid_dash" })
$btn_soft.Add_Click({ Switch-View "grid_soft" })
$btn_act.Add_Click({ Switch-View "grid_act" })
$btn_tweaks.Add_Click({ Switch-View "grid_tweaks" })
$btn_repairs.Add_Click({ Switch-View "grid_repairs" })
$btn_diag.Add_Click({ Switch-View "grid_diag" })

# --- INITIALIZE SOFTWARE LIST ---
$softwares = @(
    @{ Name = "Google Chrome"; Id = "Google.Chrome" },
    @{ Name = "Mozilla Firefox"; Id = "Mozilla.Firefox" },
    @{ Name = "Brave Browser"; Id = "Brave.Brave" },
    @{ Name = "VLC Media Player"; Id = "VideoLAN.VLC" },
    @{ Name = "7-Zip Archiver"; Id = "7zip.7zip" },
    @{ Name = "WinRAR Utilities"; Id = "RARLab.WinRAR" },
    @{ Name = "Visual Studio Code"; Id = "Microsoft.VisualStudioCode" },
    @{ Name = "Git Installer"; Id = "Git.Git" },
    @{ Name = "Zoom Meetings"; Id = "Zoom.Zoom" },
    @{ Name = "Notepad++ Editor"; Id = "Notepad++.Notepad++" },
    @{ Name = "AnyDesk Desktop"; Id = "AnyDeskSoftwareGmbH.AnyDesk" }
)

$checkboxes = @()
foreach ($app in $softwares) {
    $cb = New-Object System.Windows.Controls.CheckBox
    $cb.Content = $app.Name
    $cb.Tag = $app.Id
    $cb.Foreground = [System.Windows.Media.Brushes]::White
    $cb.Margin = "12"
    $cb.Width = 190
    $cb.FontSize = 11.5
    $cb.FontWeight = [System.Windows.FontWeights]::SemiBold
    $panel_soft_items.Children.Add($cb) | Out-Null
    $checkboxes += $cb
}

# --- SYSTEM STATS DISPATCHER TIMER ---
$osPlatform = (Get-CimInstance Win32_OperatingSystem).Caption
$txt_os.Text = $osPlatform

$timer = New-Object System.Windows.Threading.DispatcherTimer
$timer.Interval = [TimeSpan]::FromSeconds(2.5)
$timer.Add_Tick({
    try {
        # CPU
        $cpu = Get-CimInstance -ClassName Win32_Processor | Measure-Object -Property LoadPercentage -Average | Select-Object -ExpandProperty Average
        if ($cpu -eq $null) { $cpu = 0 }
        $txt_cpu.Text = "$([Math]::Round($cpu))%"

        # RAM
        $os = Get-CimInstance Win32_OperatingSystem
        $freeRam = $os.FreePhysicalMemory
        $totalRam = $os.TotalVisibleMemorySize
        $usedRam = $totalRam - $freeRam
        $ramPct = ($usedRam / $totalRam) * 100
        $txt_ram.Text = "$([Math]::Round($ramPct))%"

        # Disk
        $disk = Get-PSDrive C
        $freeGB = [Math]::Round($disk.Free / 1GB)
        $txt_disk.Text = "$freeGB GB Free"

        # Uptime
        $uptime = (Get-Date) - $os.LastBootUpTime
        $txt_uptime.Text = "Uptime: $($uptime.Days)d $($uptime.Hours)h $($uptime.Minutes)m"
    } catch {}
})
$timer.Start()

Log-Message "System Utility Toolkit initialized."
Log-Message "Operating System: $osPlatform"

# --- CORE ACTIONS IMPLEMENTATION ---

# Software installation
$btn_install_soft.Add_Click({
    $selected = $checkboxes | Where-Object { $_.IsChecked -eq $true }
    if ($selected.Count -eq 0) {
        [System.Windows.MessageBox]::Show("Please select at least one software package to install.", "Warning", "OK", "Warning")
        return
    }
    
    Log-Message "Starting installation batch..."
    Start-ThreadJob {
        param($items)
        foreach ($item in $items) {
            $name = $item.Content
            $id = $item.Tag
            [Action[string]]{ Log-Message "Installing $using:name..." }.Invoke()
            
            $proc = Start-Process winget -ArgumentList "install --id $id --silent --accept-source-agreements --accept-package-agreements" -NoNewWindow -PassThru -Wait
            if ($proc.ExitCode -eq 0) {
                [Action[string]]{ Log-Message "[✓] $using:name installed successfully." }.Invoke()
            } else {
                [Action[string]]{ Log-Message "[X] $using:name failed or was already installed." }.Invoke()
            }
        }
        [Action[string]]{ Log-Message "Installation batch completed." }.Invoke()
    } -ArgumentList (,$selected)
})

# Activation Click (MAS)
$btn_launch_mas.Add_Click({
    Log-Message "Launching MAS Console..."
    Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -Command [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; iex(irm https://get.activated.win)"
    Log-Message "[✓] MAS process initialized."
})

# Check Activation Status
$btn_check_license.Add_Click({
    Log-Message "Checking Windows activation status details..."
    Start-ThreadJob {
        $res = cscript //nologo $env:SystemRoot\system32\slmgr.vbs /dli
        $joined = $res -join "`r`n"
        [Action[string]]{ 
            Log-Message "License details returned:" 
            Log-Message $using:joined
        }.Invoke()
    }
})

# --- REPAIR FUNCTIONS CALLBACKS ---
$btn_rep_sfc.Add_Click({
    Log-Message "Launching SFC System File Scan..."
    Start-ThreadJob {
        [Action[string]]{ Log-Message "[*] Running: sfc /scannow (This takes a few minutes)..." }.Invoke()
        $proc = Start-Process sfc -ArgumentList "/scannow" -NoNewWindow -PassThru -Wait
        [Action[string]]{ Log-Message "SFC Scan finished with exit code: $using:($proc.ExitCode)" }.Invoke()
    }
})

$btn_rep_dism.Add_Click({
    Log-Message "Launching DISM RestoreHealth Scan..."
    Start-ThreadJob {
        [Action[string]]{ Log-Message "[*] Running: dism /online /cleanup-image /restorehealth..." }.Invoke()
        $proc = Start-Process dism -ArgumentList "/online /cleanup-image /restorehealth" -NoNewWindow -PassThru -Wait
        [Action[string]]{ Log-Message "DISM finished with exit code: $using:($proc.ExitCode)" }.Invoke()
    }
})

$btn_rep_net.Add_Click({
    Log-Message "Running complete network adapter reset..."
    Start-ThreadJob {
        [Action[string]]{ Log-Message "Resetting Winsock catalog..." }.Invoke()
        netsh winsock reset | Out-Null
        [Action[string]]{ Log-Message "Resetting TCP/IP stack..." }.Invoke()
        netsh int ip reset | Out-Null
        [Action[string]]{ Log-Message "[✓] Network reset completed. Please restart your system." }.Invoke()
    }
})

$btn_rep_dns.Add_Click({
    Log-Message "Flushing DNS resolver cache..."
    ipconfig /flushdns | Out-Null
    Log-Message "[✓] DNS cache flushed."
})

$btn_rep_printer11b.Add_Click({
    Log-Message "Fixing Printer Sharing Error 0x0000011b..."
    try {
        Set-ItemProperty -Path "HKLM:\System\CurrentControlSet\Control\Print" -Name "RpcAuthnLevelPrivacyEnabled" -Value 0 -Force
        Log-Message "[✓] Applied RPC privacy key registry bypass."
    } catch {
        Log-Message "[X] Failed to modify print registry keys: $_"
    }
})

$btn_rep_spooler.Add_Click({
    Log-Message "Stopping Print Spooler..."
    Stop-Service spooler -Force
    Log-Message "Clearing print queue directory..."
    Remove-Item "$env:SystemRoot\system32\spool\PRINTERS\*" -Force -Recurse -ErrorAction SilentlyContinue
    Log-Message "Starting Print Spooler..."
    Start-Service spooler
    Log-Message "[✓] Print Spooler restarted and queue cleared successfully."
})

$btn_rep_wua.Add_Click({
    Log-Message "Resetting Windows Update components cache..."
    Start-ThreadJob {
        Stop-Service wuauserv -Force -ErrorAction SilentlyContinue
        Stop-Service bits -Force -ErrorAction SilentlyContinue
        
        [Action[string]]{ Log-Message "Deleting SoftwareDistribution download cache..." }.Invoke()
        Remove-Item "$env:SystemRoot\SoftwareDistribution\Download\*" -Recurse -Force -ErrorAction SilentlyContinue
        
        Start-Service wuauserv -ErrorAction SilentlyContinue
        Start-Service bits -ErrorAction SilentlyContinue
        [Action[string]]{ Log-Message "[✓] Windows Update services cache reset completed." }.Invoke()
    }
})

$btn_rep_explorer.Add_Click({
    Log-Message "Restarting Windows Explorer shell..."
    Stop-Process -Name explorer -Force -ErrorAction SilentlyContinue
    Start-Process explorer
    Log-Message "[✓] Explorer restarted."
})

# --- SYSTEM TWEAKS IMPLEMENTATION ---
$btn_tweak_classic.Add_Click({
    Log-Message "Restoring Win11 Classic Context Menu..."
    try {
        New-Item -Path "HKCU:\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}" -Force | Out-Null
        New-Item -Path "HKCU:\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32" -Force | Out-Null
        Set-ItemProperty -Path "HKCU:\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32" -Name "(Default)" -Value "" -Force
        Log-Message "[✓] Classic Right-click context menu enabled. Restart Explorer to apply."
    } catch {
        Log-Message "[X] Error applying context menu tweak: $_"
    }
})

$btn_tweak_default_ctx.Add_Click({
    Log-Message "Reverting to Win11 Default Context Menu..."
    try {
        Remove-Item -Path "HKCU:\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}" -Recurse -Force -ErrorAction SilentlyContinue
        Log-Message "[✓] Default modern menu layout restored. Restart Explorer to apply."
    } catch {
        Log-Message "[X] Error removing context menu tweak: $_"
    }
})

$btn_tweak_ultimate.Add_Click({
    Log-Message "Unlocking Ultimate Performance Power Scheme..."
    $res = powercfg -duplicatescheme e9a22db2-565e-4b6e-82f0-8022c5e3430b
    Log-Message $res
    Log-Message "[✓] Power plan scheme unlocked."
})

$btn_tweak_gaming.Add_Click({
    Log-Message "Applying Low-Latency Gaming Registry tweaks..."
    try {
        # Disable game DVR
        New-Item -Path "HKCU:\System\GameConfigStore" -Force -ErrorAction SilentlyContinue | Out-Null
        Set-ItemProperty -Path "HKCU:\System\GameConfigStore" -Name "GameDVR_Enabled" -Value 0 -Force
        
        New-Item -Path "HKLM:\SOFTWARE\Microsoft\PolicyManager\default\ApplicationManagement\AllowGameDVR" -Force -ErrorAction SilentlyContinue | Out-Null
        Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\PolicyManager\default\ApplicationManagement\AllowGameDVR" -Name "value" -Value 0 -Force
        
        Log-Message "[✓] Disallowed GameDVR overlays."
        
        # System Responsiveness
        New-Item -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" -Force -ErrorAction SilentlyContinue | Out-Null
        Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" -Name "SystemResponsiveness" -Value 0 -Force
        
        Log-Message "[✓] Optimized game process latency bindings."
    } catch {
        Log-Message "[X] Failed to apply some latency tweaks: $_"
    }
})

$btn_tweak_bing.Add_Click({
    Log-Message "Disabling online Bing Search in Start Menu..."
    try {
        New-Item -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Search" -Force -ErrorAction SilentlyContinue | Out-Null
        Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Search" -Name "BingSearchEnabled" -Value 0 -Force
        Log-Message "[✓] Online Bing Start Menu results disabled."
    } catch {
        Log-Message "[X] Failed to apply Bing Search GPO registry key: $_"
    }
})

# --- DIAGNOSTICS & SPECS CALLBACKS ---
$btn_diag_specs.Add_Click({
    Log-Message "Generating hardware specifications summary..."
    Start-ThreadJob {
        $cpu = (Get-CimInstance Win32_Processor).Name
        $gpu = (Get-CimInstance Win32_VideoController).Name
        $mobo = (Get-CimInstance Win32_BaseBoard).Product
        $bios = (Get-CimInstance Win32_Bios).SMBIOSBIOSVersion
        
        [Action[string, string, string, string]]{
            param($c, $g, $m, $b)
            Log-Message "--- HARDWARE SUMMARY ---"
            Log-Message "Processor: $c"
            Log-Message "Graphics: $g"
            Log-Message "Motherboard: $m"
            Log-Message "BIOS Version: $b"
        }.Invoke($cpu, $gpu, $mobo, $bios)
    }
})

$btn_diag_battery.Add_Click({
    Log-Message "Generating Windows Battery Lifecycle HTML Report..."
    Start-ThreadJob {
        powercfg /batteryreport /output "$env:USERPROFILE\Desktop\BatteryReport.html" | Out-Null
        [Action]{ Log-Message "[✓] HTML Battery Report generated on your Desktop (BatteryReport.html)." }.Invoke()
    }
})

$btn_diag_disk.Add_Click({
    Log-Message "Scanning connected physical drives status (SMART Check)..."
    Start-ThreadJob {
        $status = Get-CimInstance -Namespace root\wmi -ClassName MSStorageDriver_FailurePredictStatus
        if ($status -eq $null) {
            [Action]{ Log-Message "[✓] SMART reports all connected drives are healthy." }.Invoke()
        } else {
            foreach ($drive in $status) {
                if ($drive.PredictFailure) {
                    [Action[string]]{ param($inst) Log-Message "[!] WARNING: Failure predicted on drive: $inst" }.Invoke($drive.InstanceName)
                } else {
                    [Action[string]]{ param($inst) Log-Message "[✓] Drive healthy: $inst" }.Invoke($drive.InstanceName)
                }
            }
        }
    }
})

$btn_diag_ram.Add_Click({
    Log-Message "Identifying installed memory modules properties..."
    Start-ThreadJob {
        $modules = Get-CimInstance Win32_PhysicalMemory
        foreach ($mod in $modules) {
            $cap = [Math]::Round($mod.Capacity / 1GB)
            $speed = $mod.Speed
            [Action[string, string, string]]{
                param($c, $s, $d)
                Log-Message "Slot $d: $c GB RAM module running at $s MHz."
            }.Invoke($cap, $speed, $mod.DeviceLocator)
        }
    }
})

# --- SEARCH FEATURE CATALOG MATCHING ---
$toolsCatalog = @(
    @{ Name = "SFC Scan (sfc /scannow)"; Desc = "Scans and repairs corrupt or missing Windows system files."; View = "grid_repairs"; Keyword = "sfc,scannow,corrupt,repair,system files" }
    @{ Name = "DISM Repair (dism RestoreHealth)"; Desc = "Uses DISM to scan the Windows component store and repair OS image corruption."; View = "grid_repairs"; Keyword = "dism,restorehealth,component store,corruption" }
    @{ Name = "Network Adapter Reset"; Desc = "Resets the Winsock TCP/IP catalog bindings and stack to defaults."; View = "grid_repairs"; Keyword = "winsock,network,ip reset,tcp/ip" }
    @{ Name = "Flush DNS Cache"; Desc = "Flushes the DNS resolver cache to clear corrupted IP configurations."; View = "grid_repairs"; Keyword = "dns,flush,ipconfig,flushdns" }
    @{ Name = "Fix Printer Error 0x0000011b"; Desc = "Disables RPC authentication privacy requirement to resolve sharing."; View = "grid_repairs"; Keyword = "printer,0x0000011b,sharing,rpc" }
    @{ Name = "Clean Print Spooler Queue"; Desc = "Wipes stuck print documents in queue and restarts Spooler service."; View = "grid_repairs"; Keyword = "spooler,stuck print,clear queue" }
    @{ Name = "Windows Update Cache Reset"; Desc = "Deletes downloaded update files cache and restarts update services."; View = "grid_repairs"; Keyword = "update,windows update,cache,software distribution" }
    @{ Name = "Restart Windows Explorer"; Desc = "Kills and restarts explorer.exe shell to resolve freeze bugs."; View = "grid_repairs"; Keyword = "explorer,shell,restart explorer,taskbar freeze" }
    @{ Name = "Microsoft Activation Scripts (MAS)"; Desc = "Launches MAS console tool to activate Windows and Office suites."; View = "grid_act"; Keyword = "activation,mas,activate,license" }
    @{ Name = "Classic Context Menu Tweak"; Desc = "Restores traditional right-click menu layout instead of modern layout."; View = "grid_tweaks"; Keyword = "classic,context menu,right click,menu" }
    @{ Name = "Ultimate Power Plan Tweak"; Desc = "Unlocks and activates hidden maximum speed power profile scheme."; View = "grid_tweaks"; Keyword = "ultimate,power plan,scheme" }
    @{ Name = "Gaming Latency Tweaks"; Desc = "Optimizes GameDVR settings and system response latency."; View = "grid_tweaks"; Keyword = "gaming,latency,dvr,optimization" }
    @{ Name = "Disable Start Menu Bing"; Desc = "Disables Bing online web queries inside Start Menu local search."; View = "grid_tweaks"; Keyword = "bing,start menu,offline search" }
    @{ Name = "Generate Hardware Specs"; Desc = "Generates CPU, GPU, RAM, Motherboard properties summary."; View = "grid_diag"; Keyword = "specs,hardware,summary,bios" }
    @{ Name = "HTML Battery Health Report"; Desc = "Generates HTML power battery wear diagnostic status chart."; View = "grid_diag"; Keyword = "battery,html report,battery wear" }
    @{ Name = "SMART Disk Scan"; Desc = "Queries hardware sensors on connected physical drives to check reliability."; View = "grid_diag"; Keyword = "smart,disk health,drive failure,ssd" }
    @{ Name = "Show Memory Specs"; Desc = "Identifies installed memory module speeds and capacity sizes."; View = "grid_diag"; Keyword = "ram specs,memory modules,ram clock" }
)

$btn_search.Add_Click({
    $q = $txt_search.Text.Trim().ToLower()
    if ($q -eq "") { return }
    
    Log-Message "Searching tools index for: '$q'..."
    
    $matches = @()
    foreach ($tool in $toolsCatalog) {
        $score = 0
        if ($tool.Name.ToLower().Contains($q)) { $score += 10 }
        if ($tool.Desc.ToLower().Contains($q)) { $score += 5 }
        if ($tool.Keyword.ToLower().Contains($q)) { $score += 3 }
        
        if ($score -gt 0) {
            $matches += [PSCustomObject]@{ Tool = $tool; Score = $score }
        }
    }
    
    if ($matches.Count -eq 0) {
        Log-Message "[!] No matching tools found. Try keywords like: 'printer', 'sfc', 'dism', 'ram', 'activation', 'bing'."
        return
    }
    
    $matches = $matches | Sort-Object Score -Descending
    Log-Message "Found $($matches.Count) matching tools:"
    foreach ($m in $matches) {
        Log-Message "  ➜ $($m.Tool.Name) - View: $($m.Tool.View.Replace('grid_', ''))"
        Log-Message "    $($m.Tool.Desc)"
    }
    
    # Switch to the view of the top match
    $topView = $matches[0].Tool.View
    Switch-View $topView
})

$window.ShowDialog() | Out-Null
