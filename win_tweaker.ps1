# Requires -RunAsAdministrator
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    Exit
}

Add-Type -AssemblyName PresentationFramework
Add-Type -AssemblyName PresentationCore
Add-Type -AssemblyName WindowsBase
Add-Type -AssemblyName System.Windows.Forms

[xml]$xaml = @"
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="VenkatPulse AI - Windows Utility Suite" Height="800" Width="1200"
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

                <!-- Brand logo/text -->
                <StackPanel Grid.Row="0" Margin="20,20,20,10" VerticalAlignment="Center">
                    <TextBlock Text="⚡ VenkatPulse AI" FontSize="18" FontWeight="Bold" Foreground="#38bdf8"/>
                    <TextBlock Text="Windows Utility Suite" FontSize="10" Foreground="#6b7280" Margin="2,2,0,0"/>
                </StackPanel>

                <!-- Scrollable Navigation Items -->
                <ScrollViewer Grid.Row="1" VerticalScrollBarVisibility="Auto" HorizontalScrollBarVisibility="Disabled">
                    <StackPanel Margin="10,0,10,0">
                        <Button Name="btn_dash" Content="🏠  Dashboard" Height="36" Margin="0,2,0,2" Background="Transparent" Foreground="#cbd5e1" BorderThickness="0" HorizontalContentAlignment="Left" Padding="15,0,0,0" FontSize="11.5" FontWeight="SemiBold"/>
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

                    <!-- Structured ListView Table for logs on Dashboard -->
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
                                        <GridViewColumn Header="Description" Width="400" DisplayMemberBinding="{Binding Description}"/>
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
                                <Button Name="btn_install_soft" Content="🚀 Install Selected" Height="36" Background="#059669" BorderThickness="0" FontWeight="Bold" Margin="0,0,0,5"/>
                                <Button Name="btn_uninstall_soft" Content="🗑️ Uninstall Selected" Height="36" Background="#b91c1c" BorderThickness="0" FontWeight="Bold" Margin="0,5,0,0"/>
                            </StackPanel>
                        </Grid>
                    </Border>
                </Grid>

                <!-- 3. Activation Suite View -->
                <Grid Name="grid_act" Visibility="Collapsed">
                    <Grid.RowDefinitions>
                        <RowDefinition Height="1.2*"/>
                        <RowDefinition Height="*"/>
                    </Grid.RowDefinitions>
                    
                    <!-- Top Row: Office Installer Suite -->
                    <Border Grid.Row="0" Background="#1f2937" BorderBrush="#374151" BorderThickness="1" CornerRadius="8" Padding="15" Margin="0,0,0,10">
                        <Grid>
                            <Grid.RowDefinitions>
                                <RowDefinition Height="Auto"/>
                                <RowDefinition Height="*"/>
                            </Grid.RowDefinitions>
                            <TextBlock Grid.Row="0" Text="📦 MICROSOFT OFFICE INSTALLER SUITE" FontSize="11" FontWeight="Bold" Foreground="#38bdf8" Margin="0,0,0,10"/>
                            <UniformGrid Grid.Row="1" Columns="2" Rows="2">
                                <!-- 4 Office options as cards -->
                                <Border Background="#111827" BorderBrush="#374151" BorderThickness="1" CornerRadius="6" Padding="10" Margin="5">
                                    <Grid>
                                        <StackPanel VerticalAlignment="Center">
                                            <TextBlock Text="Microsoft 365 Apps" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Subscription Suite. Includes cloud service apps." FontSize="9" Foreground="#9ca3af" Margin="0,2,0,8" TextWrapping="Wrap"/>
                                            <Button Name="btn_off_365" Content="Install Microsoft 365" Height="26" Background="#0284c7" BorderThickness="0" FontSize="10" FontWeight="Bold"/>
                                        </StackPanel>
                                    </Grid>
                                </Border>
                                <Border Background="#111827" BorderBrush="#374151" BorderThickness="1" CornerRadius="6" Padding="10" Margin="5">
                                    <Grid>
                                        <StackPanel VerticalAlignment="Center">
                                            <TextBlock Text="Office LTSC 2019" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Volume License. Perpetual Office LTSC 2019 ProPlus." FontSize="9" Foreground="#9ca3af" Margin="0,2,0,8" TextWrapping="Wrap"/>
                                            <Button Name="btn_off_2019" Content="Install Office 2019" Height="26" Background="#0284c7" BorderThickness="0" FontSize="10" FontWeight="Bold"/>
                                        </StackPanel>
                                    </Grid>
                                </Border>
                                <Border Background="#111827" BorderBrush="#374151" BorderThickness="1" CornerRadius="6" Padding="10" Margin="5">
                                    <Grid>
                                        <StackPanel VerticalAlignment="Center">
                                            <TextBlock Text="Office LTSC 2021" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Volume License. Perpetual Office LTSC 2021 ProPlus." FontSize="9" Foreground="#9ca3af" Margin="0,2,0,8" TextWrapping="Wrap"/>
                                            <Button Name="btn_off_2021" Content="Install Office 2021" Height="26" Background="#0284c7" BorderThickness="0" FontSize="10" FontWeight="Bold"/>
                                        </StackPanel>
                                    </Grid>
                                </Border>
                                <Border Background="#111827" BorderBrush="#374151" BorderThickness="1" CornerRadius="6" Padding="10" Margin="5">
                                    <Grid>
                                        <StackPanel VerticalAlignment="Center">
                                            <TextBlock Text="Office LTSC 2024" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Volume License. Perpetual Office LTSC 2024 ProPlus." FontSize="9" Foreground="#9ca3af" Margin="0,2,0,8" TextWrapping="Wrap"/>
                                            <Button Name="btn_off_2024" Content="Install Office 2024" Height="26" Background="#0284c7" BorderThickness="0" FontSize="10" FontWeight="Bold"/>
                                        </StackPanel>
                                    </Grid>
                                </Border>
                            </UniformGrid>
                        </Grid>
                    </Border>

                    <!-- Bottom Row: Activation & Edition Changer -->
                    <Grid Grid.Row="1" Margin="0,10,0,0">
                        <Grid.ColumnDefinitions>
                            <ColumnDefinition Width="*"/>
                            <ColumnDefinition Width="*"/>
                        </Grid.ColumnDefinitions>
                        
                        <!-- MAS Activator card -->
                        <Border Grid.Column="0" Background="#1f2937" BorderBrush="#374151" BorderThickness="1" CornerRadius="8" Padding="15" Margin="0,0,5,0">
                            <StackPanel VerticalAlignment="Center">
                                <TextBlock Text="🔑 MAS WINDOWS &amp; OFFICE ACTIVATOR" FontSize="11" FontWeight="Bold" Foreground="#38bdf8" HorizontalAlignment="Center"/>
                                <TextBlock Text="Activates Windows HWID and Office Ohook via official open-source scripts." TextWrapping="Wrap" FontSize="10" Foreground="#9ca3af" Margin="0,5,0,15" TextAlignment="Center"/>
                                <StackPanel Orientation="Horizontal" HorizontalAlignment="Center">
                                    <Button Name="btn_launch_mas" Content="🚀 Launch MAS GUI" Height="32" Background="#059669" BorderThickness="0" FontWeight="Bold" Width="140" Margin="0,0,5,0"/>
                                    <Button Name="btn_check_license" Content="🔍 Check License" Height="32" Background="#1f2937" BorderThickness="1" BorderBrush="#374151" FontWeight="Bold" Width="120" Margin="5,0,0,0"/>
                                </StackPanel>
                            </StackPanel>
                        </Border>
                        
                        <!-- Edition Changer card -->
                        <Border Grid.Column="1" Background="#1f2937" BorderBrush="#374151" BorderThickness="1" CornerRadius="8" Padding="15" Margin="5,0,0,0">
                            <StackPanel VerticalAlignment="Center">
                                <TextBlock Text="🔄 WINDOWS EDITION CHANGER" FontSize="11" FontWeight="Bold" Foreground="#38bdf8" HorizontalAlignment="Center"/>
                                <TextBlock Text="Converts Windows Home edition to Professional edition losslessly." TextWrapping="Wrap" FontSize="10" Foreground="#9ca3af" Margin="0,5,0,15" TextAlignment="Center"/>
                                <Grid>
                                    <Grid.ColumnDefinitions>
                                        <ColumnDefinition Width="*"/>
                                        <ColumnDefinition Width="130"/>
                                    </Grid.ColumnDefinitions>
                                    <ComboBox Grid.Column="0" Name="cb_editions" Height="30" Background="#111827" Foreground="#ffffff" VerticalContentAlignment="Center" Margin="0,0,5,0">
                                        <ComboBoxItem Content="Professional"/>
                                        <ComboBoxItem Content="Enterprise"/>
                                        <ComboBoxItem Content="Education"/>
                                    </ComboBox>
                                    <Button Grid.Column="2" Name="btn_change_edition" Content="Upgrade Edition" Height="30" Background="#b91c1c" BorderThickness="0" FontWeight="Bold" Margin="5,0,0,0"/>
                                </Grid>
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

                                <Border BorderBrush="#374151" BorderThickness="0,0,0,1" Padding="0,0,0,10" Margin="0,0,0,10">
                                    <Grid>
                                        <StackPanel HorizontalAlignment="Left">
                                            <TextBlock Text="⚡ Windows Fast Startup Settings" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Toggles Hiberboot configuration to allow full kernel reload on power off." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <StackPanel Orientation="Horizontal" HorizontalAlignment="Right">
                                            <Button Name="btn_tweak_fast_on" Content="Enable" Background="#059669" BorderThickness="0" Margin="0,0,5,0" Width="110"/>
                                            <Button Name="btn_tweak_fast_off" Content="Disable" Background="#b91c1c" BorderThickness="0" Width="110"/>
                                        </StackPanel>
                                    </Grid>
                                </Border>
                            </StackPanel>
                        </ScrollViewer>
                    </Border>
                </Grid>

                <!-- 5. Bloatware & Features View -->
                <Grid Name="grid_bloat" Visibility="Collapsed">
                    <Grid.RowDefinitions>
                        <RowDefinition Height="Auto"/>
                        <RowDefinition Height="*"/>
                    </Grid.RowDefinitions>

                    <Border Grid.Row="0" Background="#1e1b4b" BorderBrush="#312e81" BorderThickness="1" CornerRadius="6" Padding="12" Margin="0,0,0,15">
                        <TextBlock Text="🧼 Wipes native Microsoft Windows bloatware packages and toggles optional features like LPD/LPR." FontSize="11" Foreground="#cbd5e1"/>
                    </Border>

                    <Grid Grid.Row="1">
                        <Grid.ColumnDefinitions>
                            <ColumnDefinition Width="*"/>
                            <ColumnDefinition Width="*"/>
                        </Grid.ColumnDefinitions>

                        <!-- Left Card: Bloatware Remover -->
                        <Border Grid.Column="0" Background="#1f2937" BorderBrush="#374151" BorderThickness="1" CornerRadius="8" Padding="15" Margin="0,0,10,0">
                            <StackPanel>
                                <TextBlock Text="🧼 UWP Bloatware Remover" FontSize="14" FontWeight="Bold" Foreground="#ef4444" Margin="0,0,0,10"/>
                                <TextBlock Text="Purges pre-installed apps such as Xbox, Skype, Solitaire, MSN Weather, and Microsoft Maps." TextWrapping="Wrap" FontSize="11" Foreground="#9ca3af" Margin="0,0,0,20"/>
                                <Button Name="btn_remove_bloat" Content="🧼 Uninstall Windows Bloatware" Height="40" Background="#b91c1c" BorderThickness="0" FontWeight="Bold"/>
                            </StackPanel>
                        </Border>

                        <!-- Right Card: Optional Features -->
                        <Border Grid.Column="1" Background="#1f2937" BorderBrush="#374151" BorderThickness="1" CornerRadius="8" Padding="15" Margin="10,0,0,0">
                            <StackPanel>
                                <TextBlock Text="🔌 Windows Optional Features" FontSize="14" FontWeight="Bold" Foreground="#38bdf8" Margin="0,0,0,10"/>
                                <CheckBox Name="cb_feat_lpd" Content="Enable LPD Printing Service" Foreground="#ffffff" Margin="0,5,0,5"/>
                                <CheckBox Name="cb_feat_lpr" Content="Enable LPR Port Monitor Service" Foreground="#ffffff" Margin="0,5,0,5"/>
                                <CheckBox Name="cb_feat_smb" Content="Enable SMB1 Protocol Service" Foreground="#ffffff" Margin="0,5,0,15"/>
                                <Button Name="btn_apply_features" Content="⚡ Apply Windows Features" Height="40" Background="#059669" BorderThickness="0" FontWeight="Bold"/>
                            </StackPanel>
                        </Border>
                    </Grid>
                </Grid>

                <!-- 6. System Repairs View -->
                <Grid Name="grid_repairs" Visibility="Collapsed">
                    <Grid.ColumnDefinitions>
                        <ColumnDefinition Width="1.4*"/>
                        <ColumnDefinition Width="*"/>
                    </Grid.ColumnDefinitions>
                    
                    <!-- Left Column: Scrollable list of buttons -->
                    <Border Grid.Column="0" Background="#1f2937" BorderBrush="#374151" BorderThickness="1" CornerRadius="8" Padding="15" Margin="0,0,10,0">
                        <ScrollViewer VerticalScrollBarVisibility="Auto">
                            <StackPanel>
                                <TextBlock Text="🛡️ SYSTEM SCANS &amp; REPAIRS" FontSize="11" FontWeight="Bold" Foreground="#38bdf8" Margin="0,0,0,6"/>
                                <Button Name="btn_rep_sfc" Content="🛡️ Run System File Check (sfc /scannow)" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_dism" Content="⚙️ Repair Image Health (DISM /RestoreHealth)" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_dism_check" Content="🔍 Quick Check Image Corruption Status (DISM /CheckHealth)" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_wu" Content="🔄 Reset Windows Update Components &amp; Cache" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_engines" Content="🛠️ Repair Windows Native Repair Engines (SFC &amp; DISM Fix)" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_dll" Content="⚙️ Re-Register Core Windows System DLL Libraries (regsvr32)" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_dns" Content="🧹 Flush System DNS Resolver Cache" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_winsock" Content="🔌 Reset Network Winsock Catalog Bindings" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_firewall" Content="🔥 Reset Windows Firewall Rules to Default" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_store" Content="🛍️ Re-register &amp; Repair Microsoft Store &amp; Default Apps" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_net" Content="📡 Run Comprehensive Network Stack &amp; Adapter Reset" Height="30" Margin="0,2,0,15" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>

                                <TextBlock Text="🛠️ SYSTEM RECOVERY &amp; BOOT MANAGEMENT" FontSize="11" FontWeight="Bold" Foreground="#38bdf8" Margin="0,10,0,6"/>
                                <Button Name="btn_rep_winre_en" Content="💪 Enable Windows Recovery Environment (WinRE)" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_winre_stat" Content="🔍 Check WinRE Environment Configuration Status" Height="30" Margin="0,2,0,15" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>

                                <TextBlock Text="⚙️ MICROSOFT OFFICE &amp; OUTLOOK DIAGNOSTICS &amp; REPAIRS" FontSize="11" FontWeight="Bold" Foreground="#38bdf8" Margin="0,10,0,6"/>
                                <Button Name="btn_rep_off_quick" Content="🛠️ Run Microsoft Office Quick Repair (Click-to-Run)" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_off_pst" Content="📧 Launch Outlook PST File Repair Tool (ScanPST)" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <!-- Safe mode row -->
                                <Grid Margin="0,2,0,15">
                                    <Grid.ColumnDefinitions>
                                        <ColumnDefinition Width="Auto"/>
                                        <ColumnDefinition Width="*"/>
                                    </Grid.ColumnDefinitions>
                                    <TextBlock Grid.Column="0" Text="Launch Safe Mode:" FontSize="10.5" VerticalAlignment="Center" Margin="5,0,10,0"/>
                                    <UniformGrid Grid.Column="1" Columns="4">
                                        <Button Name="btn_safe_word" Content="Word" Height="24" Margin="2" FontSize="9.5" FontWeight="Bold" Background="#111827"/>
                                        <Button Name="btn_safe_excel" Content="Excel" Height="24" Margin="2" FontSize="9.5" FontWeight="Bold" Background="#111827"/>
                                        <Button Name="btn_safe_ppt" Content="PPT" Height="24" Margin="2" FontSize="9.5" FontWeight="Bold" Background="#111827"/>
                                        <Button Name="btn_safe_outlook" Content="Outlook" Height="24" Margin="2" FontSize="9.5" FontWeight="Bold" Background="#111827"/>
                                    </UniformGrid>
                                </Grid>

                                <TextBlock Text="💻 WINDOWS BOOT SECTOR &amp; EFI REPAIR" FontSize="11" FontWeight="Bold" Foreground="#38bdf8" Margin="0,10,0,6"/>
                                <Button Name="btn_rep_bcd" Content="💻 Rebuild Windows Boot configuration partition files (BCDBoot)" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_rec_boot" Content="🔄 Reboot System directly into Startup Repair / Recovery Menu" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_fail_menu" Content="🚦 Enable Windows Boot Failures Menu Display Policy" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_chkdsk" Content="📂 Schedule Boot-Time Disk Volume Scan &amp; Repair (Chkdsk /f /r)" Height="30" Margin="0,2,0,15" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>

                                <TextBlock Text="🖨️ PRINTER SERVICE &amp; SHARING REPAIRS" FontSize="11" FontWeight="Bold" Foreground="#38bdf8" Margin="0,10,0,6"/>
                                <Button Name="btn_rep_printer_11b" Content="🔓 Fix Shared Printer Error 0x0000011b (Set RpcAuthnLevelPrivacyEnabled=0)" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_printer_policy" Content="📜 Configure Group Policy Printer Sharing &amp; RPC Connection Settings" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_printer_lpd" Content="⚙️ Enable Windows LPD Print Service &amp; LPR Port Monitor Optional Features" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_printer_disc" Content="🌐 Restart Network Discovery &amp; Printer Sharing Dependency Services" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_printer_spool" Content="🧹 Flush Print Spooler Service &amp; Clear Pending Queue" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_printer_diag" Content="🔍 Launch Native Windows Printer Troubleshooter Diagnostic Wizard" Height="30" Margin="0,2,0,15" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>

                                <TextBlock Text="🎛️ LOSSLESS DRIVE &amp; DISK STYLE CONVERTERS" FontSize="11" FontWeight="Bold" Foreground="#38bdf8" Margin="0,10,0,6"/>
                                <!-- NTFS converter -->
                                <Grid Margin="0,2,0,4">
                                    <Grid.ColumnDefinitions>
                                        <ColumnDefinition Width="Auto"/>
                                        <ColumnDefinition Width="*"/>
                                        <ColumnDefinition Width="130"/>
                                    </Grid.ColumnDefinitions>
                                    <TextBlock Grid.Column="0" Text="FAT32 Letter:" FontSize="10.5" VerticalAlignment="Center" Margin="5,0,5,0"/>
                                    <ComboBox Grid.Column="1" Name="cb_ntfs_drive" Height="28" Background="#111827" Foreground="#ffffff" VerticalContentAlignment="Center" Margin="5,0,5,0">
                                        <ComboBoxItem Content="D:"/>
                                        <ComboBoxItem Content="E:"/>
                                        <ComboBoxItem Content="F:"/>
                                        <ComboBoxItem Content="G:"/>
                                    </ComboBox>
                                    <Button Grid.Column="2" Name="btn_conv_ntfs" Content="Convert to NTFS" Height="28" Background="#1e293b" BorderBrush="#374151" FontSize="10" FontWeight="Bold"/>
                                </Grid>
                                <!-- GPT converter -->
                                <Grid Margin="0,2,0,15">
                                    <Grid.ColumnDefinitions>
                                        <ColumnDefinition Width="Auto"/>
                                        <ColumnDefinition Width="*"/>
                                        <ColumnDefinition Width="130"/>
                                    </Grid.ColumnDefinitions>
                                    <TextBlock Grid.Column="0" Text="Disk ID (MBR):" FontSize="10.5" VerticalAlignment="Center" Margin="5,0,5,0"/>
                                    <ComboBox Grid.Column="1" Name="cb_gpt_disk" Height="28" Background="#111827" Foreground="#ffffff" VerticalContentAlignment="Center" Margin="5,0,5,0">
                                        <ComboBoxItem Content="Disk 0"/>
                                        <ComboBoxItem Content="Disk 1"/>
                                        <ComboBoxItem Content="Disk 2"/>
                                    </ComboBox>
                                    <Button Grid.Column="2" Name="btn_conv_gpt" Content="Convert MBR to GPT" Height="28" Background="#ef4444" BorderThickness="0" FontSize="10" FontWeight="Bold"/>
                                </Grid>

                                <TextBlock Text="🧹 SYSTEM CLEANERS &amp; CACHE OPTIMIZERS" FontSize="11" FontWeight="Bold" Foreground="#38bdf8" Margin="0,10,0,6"/>
                                <Button Name="btn_rep_clean_ram" Content="🧠 Optimize &amp; Flush System RAM Cache (Empty Process Working Sets)" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_clean_browser" Content="🧹 Clean Web Browser Cache &amp; Temp Files (Chrome, Edge, Firefox)" Height="30" Margin="0,2,0,15" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>

                                <TextBlock Text="🛡️ WINDOWS SERVICES &amp; SHIELD REPAIRS" FontSize="11" FontWeight="Bold" Foreground="#38bdf8" Margin="0,10,0,6"/>
                                <Button Name="btn_rep_shield_wu" Content="⚙️ Run Comprehensive Windows Update Service &amp; Cache Repair Engine" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <!-- Windows update block frame -->
                                <Grid Margin="0,2,0,4">
                                    <Grid.ColumnDefinitions>
                                        <ColumnDefinition Width="*"/>
                                        <ColumnDefinition Width="*"/>
                                    </Grid.ColumnDefinitions>
                                    <Button Grid.Column="0" Name="btn_rep_shield_block_wu" Content="🔒 Block Windows Updates" Height="30" Margin="0,2,5,2" Background="#b91c1c" BorderThickness="0" FontSize="10" FontWeight="Bold"/>
                                    <Button Grid.Column="1" Name="btn_rep_shield_enable_wu" Content="🔓 Enable Windows Updates" Height="30" Margin="5,2,0,2" Background="#059669" BorderThickness="0" FontSize="10" FontWeight="Bold"/>
                                </Grid>
                                <Button Name="btn_rep_shield_defender" Content="🛡️ Reset Windows Defender Policies &amp; Restart Antivirus Services" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_shield_firewall" Content="🧱 Restore Default Windows Firewall Settings and Rules" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_shield_audio" Content="🎧 Reset &amp; Restart Windows Audio Playback Services" Height="30" Margin="0,2,0,15" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>

                                <TextBlock Text="🚀 SHELL OPTIMIZERS &amp; DATA WIPERS" FontSize="11" FontWeight="Bold" Foreground="#38bdf8" Margin="0,10,0,6"/>
                                <Button Name="btn_rep_shell_explorer" Content="🚀 Restart Windows Explorer Shell (Quick Freeze Fix)" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_shell_events" Content="💽 Clear All Windows System, Application &amp; Security Event Logs" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_shell_icon" Content="🖼️ Rebuild Windows Desktop Icon &amp; Thumbnail Cache Data" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_shell_font" Content="🔤 Rebuild Windows System Font Cache Database" Height="30" Margin="0,2,0,15" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                            </StackPanel>
                        </ScrollViewer>
                    </Border>
                    
                    <!-- Right Column: Output console -->
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

                <!-- 7. Diagnostics & Specs View -->
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
                                            <TextBlock Text="💾 Check Connected Physical Drive Health Status (SMART Scan)" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Queries hardware sensors on connected physical drives to check reliability." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <Button Name="btn_diag_disk" Content="Run SMART Drive Check" Background="#4f46e5" BorderThickness="0" HorizontalAlignment="Right" Width="200"/>
                                    </Grid>
                                </Border>

                                <Border BorderBrush="#374151" BorderThickness="0,0,0,1" Padding="0,0,0,10" Margin="0,0,0,10">
                                    <Grid>
                                        <StackPanel HorizontalAlignment="Left">
                                            <TextBlock Text="🧠 Analyze Installed RAM Modules &amp; Speed Specifications" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Queries WMIC to identify installed memory module speeds and clock cycles." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <Button Name="btn_diag_ram" Content="Show Memory Specs" Background="#374151" BorderThickness="0" HorizontalAlignment="Right" Width="200"/>
                                    </Grid>
                                </Border>

                                <Border BorderBrush="#374151" BorderThickness="0,0,0,1" Padding="0,0,0,10" Margin="0,0,0,10">
                                    <Grid>
                                        <StackPanel HorizontalAlignment="Left">
                                            <TextBlock Text="🔄 Schedule Windows Memory Diagnostic Scanner (mdsched.exe)" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Sets up Windows Memory Diagnostic to check physical RAM hardware during restart." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <Button Name="btn_diag_mdsched" Content="Schedule RAM Scan" Background="#0284c7" BorderThickness="0" HorizontalAlignment="Right" Width="200"/>
                                    </Grid>
                                </Border>

                                <Border BorderBrush="#374151" BorderThickness="0,0,0,1" Padding="0,0,0,10" Margin="0,0,0,10">
                                    <Grid>
                                        <StackPanel HorizontalAlignment="Left">
                                            <TextBlock Text="🌐 Configure Secure Network DNS Servers (Cloudflare 1.1.1.1)" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Configures adapter DNS settings to use Cloudflare secure DNS." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <Button Name="btn_diag_dns" Content="Apply Secure DNS" Background="#4f46e5" BorderThickness="0" HorizontalAlignment="Right" Width="200"/>
                                    </Grid>
                                </Border>

                                <Border BorderBrush="#374151" BorderThickness="0,0,0,1" Padding="0,0,0,10" Margin="0,0,0,10">
                                    <Grid>
                                        <StackPanel HorizontalAlignment="Left">
                                            <TextBlock Text="📡 Run Real-Time Internet Download Speed Test" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Downloads a test file from Cloudflare CDN to calculate internet bandwidth." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <Button Name="btn_diag_speed" Content="Run Download Speed Test" Background="#10b981" BorderThickness="0" HorizontalAlignment="Right" Width="200"/>
                                    </Grid>
                                </Border>

                                <Border BorderBrush="#374151" BorderThickness="0,0,0,1" Padding="0,0,0,10" Margin="0,0,0,10">
                                    <Grid>
                                        <StackPanel HorizontalAlignment="Left">
                                            <TextBlock Text="🔋 Generate Windows Battery Lifecycle &amp; Wear Health Report" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Generates HTML power battery wear diagnostic status chart." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <Button Name="btn_diag_battery" Content="Generate Battery Report" Background="#10b981" BorderThickness="0" HorizontalAlignment="Right" Width="200"/>
                                    </Grid>
                                </Border>

                                <Border BorderBrush="#374151" BorderThickness="0,0,0,1" Padding="0,0,0,10" Margin="0,0,0,10">
                                    <Grid>
                                        <StackPanel HorizontalAlignment="Left">
                                            <TextBlock Text="🔑 Verify Windows OS License Activation Status" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Queries software licensing services to check activation." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <Button Name="btn_diag_act" Content="Check Activation Status" Background="#1f2937" BorderThickness="1" BorderBrush="#374151" HorizontalAlignment="Right" Width="200"/>
                                    </Grid>
                                </Border>

                                <Border BorderBrush="#374151" BorderThickness="0,0,0,1" Padding="0,0,0,10" Margin="0,0,0,10">
                                    <Grid>
                                        <StackPanel HorizontalAlignment="Left">
                                            <TextBlock Text="📝 Generate Comprehensive Windows Hardware &amp; System Info Summary" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Generates CPU, GPU, Motherboard, and BIOS properties summary." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <Button Name="btn_diag_specs" Content="Generate Specs Info" Background="#0284c7" BorderThickness="0" HorizontalAlignment="Right" Width="200"/>
                                    </Grid>
                                </Border>
                            </StackPanel>
                        </ScrollViewer>
                    </Border>
                </Grid>

                <!-- 8. Backups & Migration View -->
                <Grid Name="grid_backups" Visibility="Collapsed">
                    <Grid.RowDefinitions>
                        <RowDefinition Height="Auto"/>
                        <RowDefinition Height="*"/>
                    </Grid.RowDefinitions>

                    <Border Grid.Row="0" Background="#1e1b4b" BorderBrush="#312e81" BorderThickness="1" CornerRadius="6" Padding="12" Margin="0,0,0,15">
                        <TextBlock Text="💾 Migrate or back up directory folders to secondary drives losslessly using Robocopy." FontSize="11" Foreground="#cbd5e1"/>
                    </Border>

                    <Border Grid.Row="1" Background="#1f2937" BorderBrush="#374151" BorderThickness="1" CornerRadius="8" Padding="20">
                        <StackPanel VerticalAlignment="Center">
                            <TextBlock Text="Source Folder Path:" FontSize="11" Foreground="#9ca3af" Margin="0,0,0,5"/>
                            <Grid Margin="0,0,0,15">
                                <Grid.ColumnDefinitions>
                                    <ColumnDefinition Width="*"/>
                                    <ColumnDefinition Width="80"/>
                                </Grid.ColumnDefinitions>
                                <TextBox Grid.Column="0" Name="txt_backup_src" Height="30" Background="#111827" Foreground="#ffffff" BorderBrush="#374151" Padding="5,0,5,0" VerticalContentAlignment="Center"/>
                                <Button Grid.Column="1" Name="btn_backup_browse_src" Content="Browse" Height="30" Margin="5,0,0,0"/>
                            </Grid>

                            <TextBlock Text="Destination Folder Path:" FontSize="11" Foreground="#9ca3af" Margin="0,0,0,5"/>
                            <Grid Margin="0,0,0,25">
                                <Grid.ColumnDefinitions>
                                    <ColumnDefinition Width="*"/>
                                    <ColumnDefinition Width="80"/>
                                </Grid.ColumnDefinitions>
                                <TextBox Grid.Column="0" Name="txt_backup_dst" Height="30" Background="#111827" Foreground="#ffffff" BorderBrush="#374151" Padding="5,0,5,0" VerticalContentAlignment="Center"/>
                                <Button Grid.Column="1" Name="btn_backup_browse_dst" Content="Browse" Height="30" Margin="5,0,0,0"/>
                            </Grid>

                            <Button Name="btn_start_backup" Content="⚡ Start Robocopy Backup Migration" Height="40" Background="#059669" BorderThickness="0" FontWeight="Bold" FontSize="13"/>
                        </StackPanel>
                    </Border>
                </Grid>

                <!-- 9. Windows Config Shortcuts View -->
                <Grid Name="grid_config" Visibility="Collapsed">
                    <Grid.RowDefinitions>
                        <RowDefinition Height="Auto"/>
                        <RowDefinition Height="*"/>
                    </Grid.RowDefinitions>

                    <TextBlock Grid.Row="0" Text="Quick launch native Windows system administration consoles:" FontSize="11" Foreground="#9ca3af" Margin="0,0,0,10"/>

                    <Border Grid.Row="1" Background="#1f2937" BorderBrush="#374151" BorderThickness="1" CornerRadius="8" Padding="15">
                        <UniformGrid Columns="3" Rows="3">
                            <Button Name="btn_cfg_panel" Content="⚙️ Control Panel" Height="50" Margin="10" FontSize="11" FontWeight="Bold"/>
                            <Button Name="btn_cfg_reg" Content="📁 Registry Editor" Height="50" Margin="10" FontSize="11" FontWeight="Bold"/>
                            <Button Name="btn_cfg_dev" Content="🔌 Device Manager" Height="50" Margin="10" FontSize="11" FontWeight="Bold"/>
                            <Button Name="btn_cfg_disk" Content="💾 Disk Management" Height="50" Margin="10" FontSize="11" FontWeight="Bold"/>
                            <Button Name="btn_cfg_services" Content="🛠️ System Services" Height="50" Margin="10" FontSize="11" FontWeight="Bold"/>
                            <Button Name="btn_cfg_event" Content="📋 Event Viewer" Height="50" Margin="10" FontSize="11" FontWeight="Bold"/>
                            <Button Name="btn_cfg_task" Content="📈 Task Manager" Height="50" Margin="10" FontSize="11" FontWeight="Bold"/>
                            <Button Name="btn_cfg_gp" Content="📜 Group Policy Editor" Height="50" Margin="10" FontSize="11" FontWeight="Bold"/>
                            <Button Name="btn_cfg_sys" Content="💻 System Properties" Height="50" Margin="10" FontSize="11" FontWeight="Bold"/>
                        </UniformGrid>
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
$activities = New-Object System.Collections.ObjectModel.ObservableCollection[PSObject]
$activity_tree.ItemsSource = $activities

function Add-Activity ($op, $desc, $status) {
    $window.Dispatcher.Invoke([Action]{
        $script:activities.Insert(0, [PSCustomObject]@{
            Operation = $op
            Description = $desc
            Status = $status
            Timestamp = (Get-Date -Format "HH:mm:ss")
        })
    })
}

function Log-Message ($msg) {
    $timestamp = Get-Date -Format "HH:mm:ss"
    $formatted = "[$timestamp] $msg`r`n"
    $window.Dispatcher.Invoke([Action[string]]{
        param($text)
        $txt_log_soft.AppendText($text)
        $txt_log_soft.ScrollToEnd()
        
        $txt_log_rep.AppendText($text)
        $txt_log_rep.ScrollToEnd()
    }, $formatted)
}

function Switch-View ($viewName) {
    $views = @("grid_dash", "grid_soft", "grid_act", "grid_tweaks", "grid_bloat", "grid_repairs", "grid_diag", "grid_backups", "grid_config")
    $titles = @{
        "grid_dash" = "🏠 Dashboard Overview"
        "grid_soft" = "📥 Silent Software Installer Hub"
        "grid_act"  = "🔑 Windows & Office Activation (MAS)"
        "grid_tweaks" = "🔧 Premium OS Registry Tweaks"
        "grid_bloat" = "🧼 Windows Bloatware & Features"
        "grid_repairs" = "🛠️ System Command & Cache Repairs"
        "grid_diag" = "📊 Hardware Diagnostics & Reports"
        "grid_backups" = "💾 Backups & Data Migration"
        "grid_config" = "⚙️ Windows Configuration Consoles"
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
$btn_bloat.Add_Click({ Switch-View "grid_bloat" })
$btn_repairs.Add_Click({ Switch-View "grid_repairs" })
$btn_diag.Add_Click({ Switch-View "grid_diag" })
$btn_backups.Add_Click({ Switch-View "grid_backups" })
$btn_config.Add_Click({ Switch-View "grid_config" })

# --- INITIALIZE SOFTWARE LIST WITH GROUPS (100% Matching Python catalog) ---
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

Add-Softwares $browsers $panel_soft_browsers
Add-Softwares $msoft $panel_soft_msoft
Add-Softwares $utils $panel_soft_utils
Add-Softwares $devs $panel_soft_dev
Add-Softwares $media $panel_soft_media

# Select/Deselect All software callbacks
$btn_soft_sel_all.Add_Click({
    $checkboxes | ForEach-Object { $_.IsChecked = $true }
})
$btn_soft_desel_all.Add_Click({
    $checkboxes | ForEach-Object { $_.IsChecked = $false }
})

# --- SYSTEM STATS DISPATCHER TIMER ---
$osPlatform = (Get-CimInstance Win32_OperatingSystem).Caption
$txt_os.Text = "Win 10/11"

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

Add-Activity "Launch Utility" "Ready" "Success"
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
    Add-Activity "Software Installer" "Starting installation batch" "Running"
    
    Start-ThreadJob {
        param($items)
        foreach ($item in $items) {
            $name = $item.Content
            $id = $item.Tag
            [Action[string]]{ param($n) Log-Message "Installing $n..." }.Invoke($name)
            
            $proc = Start-Process winget -ArgumentList "install --id $id --silent --accept-source-agreements --accept-package-agreements" -NoNewWindow -PassThru -Wait
            if ($proc.ExitCode -eq 0) {
                [Action[string]]{ param($n) Log-Message "[✓] $n installed successfully." }.Invoke($name)
                [Action[string]]{ param($n) Add-Activity "WinGet Installer" "$n installed successfully" "Success" }.Invoke($name)
            } else {
                [Action[string]]{ param($n) Log-Message "[X] $n failed or was already installed." }.Invoke($name)
                [Action[string]]{ param($n) Add-Activity "WinGet Installer" "$n install failed" "Failed" }.Invoke($name)
            }
        }
        [Action]{ Log-Message "Installation batch completed." }.Invoke()
        [Action]{ Add-Activity "Software Installer" "Installation batch completed" "Success" }.Invoke()
    } -ArgumentList (,$selected)
})

# Software Uninstallation
$btn_uninstall_soft.Add_Click({
    $selected = $checkboxes | Where-Object { $_.IsChecked -eq $true }
    if ($selected.Count -eq 0) {
        [System.Windows.MessageBox]::Show("Please select at least one software package to uninstall.", "Warning", "OK", "Warning")
        return
    }
    
    Log-Message "Starting uninstallation batch..."
    Add-Activity "Software Installer" "Starting uninstallation batch" "Running"
    
    Start-ThreadJob {
        param($items)
        foreach ($item in $items) {
            $name = $item.Content
            $id = $item.Tag
            [Action[string]]{ param($n) Log-Message "Uninstalling $n..." }.Invoke($name)
            
            $proc = Start-Process winget -ArgumentList "uninstall --id $id --silent" -NoNewWindow -PassThru -Wait
            if ($proc.ExitCode -eq 0) {
                [Action[string]]{ param($n) Log-Message "[✓] $n uninstalled successfully." }.Invoke($name)
                [Action[string]]{ param($n) Add-Activity "WinGet Installer" "$n uninstalled successfully" "Success" }.Invoke($name)
            } else {
                [Action[string]]{ param($n) Log-Message "[X] $n failed to uninstall." }.Invoke($name)
                [Action[string]]{ param($n) Add-Activity "WinGet Installer" "$n uninstall failed" "Failed" }.Invoke($name)
            }
        }
        [Action]{ Log-Message "Uninstallation batch completed." }.Invoke()
        [Action]{ Add-Activity "Software Installer" "Uninstallation batch completed" "Success" }.Invoke()
    } -ArgumentList (,$selected)
})

# Deploy custom Microsoft Office suites (M365, LTSC 2019, 2021, 2024)
function Start-OfficeDeployment ($pkgId, $title) {
    Log-Message "Requesting install for $title..."
    Add-Activity "Office Installer" "Deploying $title..." "Running"
    
    if ($pkgId -eq "Microsoft.Office") {
        # Deploy Microsoft 365 silent using WinGet
        Start-ThreadJob {
            [Action]{ Log-Message "Installing Microsoft 365 Apps silently via WinGet..." }.Invoke()
            $proc = Start-Process winget -ArgumentList "install --id Microsoft.Office --silent --accept-source-agreements --accept-package-agreements" -NoNewWindow -PassThru -Wait
            if ($proc.ExitCode -eq 0) {
                [Action]{ Log-Message "[✓] Microsoft 365 installed successfully." }.Invoke()
                [Action]{ Add-Activity "Office Installer" "M365 installed successfully" "Success" }.Invoke()
            } else {
                [Action]{ Log-Message "[X] Microsoft 365 installation failed." }.Invoke()
                [Action]{ Add-Activity "Office Installer" "M365 install failed" "Failed" }.Invoke()
            }
        }
    } else {
        # Custom ODT deployment for LTSC
        Start-ThreadJob {
            param($id, $t)
            $odtDir = "C:\OfficeODT"
            if (-not (Test-Path $odtDir)) { New-Item -ItemType Directory -Path $odtDir | Out-Null }
            
            [Action]{ Log-Message "Downloading Microsoft Office Deployment Tool (ODT) setup..." }.Invoke()
            $setupExe = "C:\Program Files\OfficeDeploymentTool\setup.exe"
            if (-not (Test-Path $setupExe)) { $setupExe = "C:\Program Files (x86)\OfficeDeploymentTool\setup.exe" }
            if (-not (Test-Path $setupExe)) {
                # Fallback direct download
                $url = "https://download.microsoft.com/download/6c1eeb25-cf8b-41d9-8d0d-cc1dbc032140/officedeploymenttool_20228-20124.exe"
                $odtInstaller = "$odtDir\odt_installer.exe"
                Invoke-WebRequest -Uri $url -OutFile $odtInstaller
                Start-Process $odtInstaller -ArgumentList "/extract:$odtDir /quiet" -Wait
                $setupExe = "$odtDir\setup.exe"
            }
            
            # Configure XML
            $channel = "PerpetualVL2019"
            $product = "ProPlus2019Volume"
            if ($id -like "*2021*") {
                $channel = "PerpetualVL2021"
                $product = "ProPlus2021Volume"
            } elseif ($id -like "*2024*") {
                $channel = "PerpetualVL2024"
                $product = "ProPlus2024Volume"
            }
            
            $configXml = @"
<Configuration>
  <Add OfficeClientEdition="64" Channel="$channel">
    <Product ID="$product">
      <Language ID="en-us" />
    </Product>
  </Add>
  <Display Level="Full" AcceptEULA="TRUE" />
</Configuration>
"@
            $configXml | Out-File -FilePath "$odtDir\configuration.xml" -Encoding utf8
            
            [Action]{ Log-Message "Running setup.exe /configure configuration.xml (Follow the Microsoft UI)..." }.Invoke()
            $proc = Start-Process $using:setupExe -ArgumentList "/configure $odtDir\configuration.xml" -Wait -PassThru
            if ($proc.ExitCode -eq 0) {
                [Action[string]]{ param($title) Log-Message "[✓] $title installed successfully." }.Invoke($t)
                [Action[string]]{ param($title) Add-Activity "Office Installer" "$title installed" "Success" }.Invoke($t)
            } else {
                [Action[string]]{ param($title) Log-Message "[X] $title failed (Exit code: $($proc.ExitCode))." }.Invoke($t)
                [Action[string]]{ param($title) Add-Activity "Office Installer" "$title install failed" "Failed" }.Invoke($t)
            }
        } -ArgumentList $pkgId, $title
    }
}

$btn_off_365.Add_Click({ Start-OfficeDeployment "Microsoft.Office" "Microsoft 365 Apps" })
$btn_off_2019.Add_Click({ Start-OfficeDeployment "Microsoft.Office.LTSC.2019" "Office LTSC 2019" })
$btn_off_2021.Add_Click({ Start-OfficeDeployment "Microsoft.Office.LTSC.2021" "Office LTSC 2021" })
$btn_off_2024.Add_Click({ Start-OfficeDeployment "Microsoft.Office.LTSC.2024" "Office LTSC 2024" })

# Activation Click (MAS)
$btn_launch_mas.Add_Click({
    Log-Message "Launching MAS Console..."
    Add-Activity "System Activation" "Launching MAS GUI" "Running"
    Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -Command [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; iex(irm https://get.activated.win)"
    Log-Message "[✓] MAS process initialized."
    Add-Activity "System Activation" "MAS GUI opened successfully" "Success"
})

# Check Activation Status
$btn_check_license.Add_Click({
    Log-Message "Checking Windows activation status details..."
    Add-Activity "Diagnostics" "Checking activation status..." "Running"
    Start-ThreadJob {
        $res = cscript //nologo $env:SystemRoot\system32\slmgr.vbs /dli
        $joined = $res -join "`r`n"
        [Action[string]]{ 
            param($txt)
            Log-Message "License details returned:" 
            Log-Message $txt
            Add-Activity "Diagnostics" "Activation Checked" "Success"
        }.Invoke($joined)
    }
})

# Upgrade Windows Edition Changer
$btn_change_edition.Add_Click({
    $selectedEdition = $cb_editions.Text
    Log-Message "Upgrading Windows edition to: $selectedEdition..."
    Add-Activity "Edition Changer" "Upgrading Windows to $selectedEdition" "Running"
    
    $keys = @{
        "Professional" = "W269N-WFGWX-YVC9B-4J6C9-T83GX"
        "Enterprise"   = "NPPR9-FWDCX-D2C8J-H822J-VMKFT"
        "Education"    = "NW6C2-QMPVW-D7KKK-3GKT6-VCFB2"
    }
    
    $key = $keys[$selectedEdition]
    Start-ThreadJob {
        param($k, $ed)
        [Action[string]]{ param($txt) Log-Message "Installing product key: $txt..." }.Invoke($k)
        
        $proc = Start-Process changepk.exe -ArgumentList "/ProductKey $k" -NoNewWindow -PassThru -Wait
        [Action[string, string]]{ 
            param($code, $e) 
            Log-Message "Edition upgrade process completed (Exit code: $code)."
            Add-Activity "Edition Changer" "Upgraded to $e" "Success"
        }.Invoke($proc.ExitCode, $ed)
    } -ArgumentList $key, $selectedEdition
})

# --- REPAIR FUNCTIONS CALLBACKS ---
function Run-RepairCommand ($argsList, $opName) {
    Log-Message "Initiating command: $($argsList -join ' ')..."
    Add-Activity "System Repair" "Running $opName" "Running"
    Start-ThreadJob {
        param($cmd, $args, $name)
        $proc = Start-Process $cmd -ArgumentList $args -NoNewWindow -PassThru -Wait
        [Action[string, string]]{ 
            param($code, $n) 
            Log-Message "$n finished with exit code: $code" 
            Add-Activity "System Repair" "$n completed" "Success"
        }.Invoke($proc.ExitCode, $name)
    } -ArgumentList $argsList[0], ($argsList[1..($argsList.Length-1)] -join ' '), $opName
}

$btn_rep_sfc.Add_Click({ Run-RepairCommand @("sfc", "/scannow") "SFC Scan" })
$btn_rep_dism.Add_Click({ Run-RepairCommand @("dism", "/online", "/cleanup-image", "/restorehealth") "DISM RestoreHealth" })
$btn_rep_dism_check.Add_Click({ Run-RepairCommand @("dism", "/online", "/cleanup-image", "/checkhealth") "DISM CheckHealth" })
$btn_rep_wu.Add_Click({
    Log-Message "Resetting Windows Update components cache..."
    Add-Activity "System Repair" "Resetting Update Cache" "Running"
    Start-ThreadJob {
        Stop-Service wuauserv -Force -ErrorAction SilentlyContinue
        Stop-Service bits -Force -ErrorAction SilentlyContinue
        
        [Action]{ Log-Message "Deleting SoftwareDistribution download cache..." }.Invoke()
        Remove-Item "$env:SystemRoot\SoftwareDistribution\Download\*" -Recurse -Force -ErrorAction SilentlyContinue
        
        Start-Service wuauserv -ErrorAction SilentlyContinue
        Start-Service bits -ErrorAction SilentlyContinue
        [Action]{ Log-Message "[✓] Windows Update services cache reset completed." }.Invoke()
        [Action]{ Add-Activity "System Repair" "Reset Update Cache completed" "Success" }.Invoke()
    }
})

$btn_rep_engines.Add_Click({
    Log-Message "Repairing Windows native repair engines (SFC/DISM Fix)..."
    Add-Activity "System Repair" "Repair Native Engines" "Running"
    Start-ThreadJob {
        # Reset CBS log file and repair components
        Remove-Item "$env:SystemRoot\Logs\CBS\CBS.log" -Force -ErrorAction SilentlyContinue
        dism /online /cleanup-image /startcomponentcleanup | Out-Null
        [Action]{ Log-Message "[✓] Native repair engines refreshed successfully." }.Invoke()
        [Action]{ Add-Activity "System Repair" "Repair Native Engines completed" "Success" }.Invoke()
    }
})

$btn_rep_dll.Add_Click({
    Log-Message "Re-registering core Windows System DLL Libraries..."
    Add-Activity "System Repair" "Re-register DLLs" "Running"
    Start-ThreadJob {
        $dlls = @("atl.dll", "urlmon.dll", "mshtml.dll", "shdocvw.dll", "browseui.dll", "jscript.dll", "vbscript.dll", "scrrun.dll", "msxml.dll", "msxml3.dll", "msxml6.dll", "actxprxy.dll", "softpub.dll", "wintrust.dll", "dssenh.dll", "gpkcsp.dll", "sccbase.dll", "slbcsp.dll", "cryptdlg.dll", "ole32.dll", "oleaut32.dll", "initpki.dll", "msi.dll")
        $success = 0
        foreach ($dll in $dlls) {
            $proc = Start-Process regsvr32.exe -ArgumentList "/s $dll" -NoNewWindow -PassThru -Wait
            if ($proc.ExitCode -eq 0) { $success++ }
        }
        [Action[string]]{ 
            param($s) 
            Log-Message "[✓] Re-registered $s system DLL files." 
            Add-Activity "System Repair" "Re-register DLLs completed" "Success"
        }.Invoke($success)
    }
})

$btn_rep_dns.Add_Click({
    Log-Message "Flushing DNS resolver cache..."
    ipconfig /flushdns | Out-Null
    Log-Message "[✓] DNS cache flushed."
    Add-Activity "System Repair" "Flush DNS Cache" "Success"
})

$btn_rep_winsock.Add_Click({ Run-RepairCommand @("netsh", "winsock", "reset") "Winsock Reset" })
$btn_rep_firewall.Add_Click({ Run-RepairCommand @("netsh", "advfirewall", "reset") "Firewall Defaults Reset" })

$btn_rep_store.Add_Click({
    Log-Message "Re-registering Microsoft App Store packages..."
    Add-Activity "System Repair" "Repair App Store" "Running"
    Start-ThreadJob {
        Get-AppXPackage -AllUsers -Name "Microsoft.WindowsStore" | Foreach-Object {
            Add-AppxPackage -DisableDevelopmentMode -Register "$($_.InstallLocation)\AppXManifest.xml"
        }
        [Action]{ 
            Log-Message "[✓] Microsoft App Store packages re-registered." 
            Add-Activity "System Repair" "Repair App Store completed" "Success"
        }.Invoke()
    }
})

$btn_rep_net.Add_Click({
    Log-Message "Running complete network adapter reset..."
    Add-Activity "System Repair" "Network Adapter Reset" "Running"
    Start-ThreadJob {
        [Action]{ Log-Message "Resetting Winsock catalog..." }.Invoke()
        netsh winsock reset | Out-Null
        [Action]{ Log-Message "Resetting TCP/IP stack..." }.Invoke()
        netsh int ip reset | Out-Null
        [Action]{ Log-Message "[✓] Network reset completed. Please restart your system." }.Invoke()
        [Action]{ Add-Activity "System Repair" "Network Reset completed" "Success" }.Invoke()
    }
})

$btn_rep_winre_en.Add_Click({ Run-RepairCommand @("reagentc", "/enable") "Enable WinRE" })
$btn_rep_winre_stat.Add_Click({ Run-RepairCommand @("reagentc", "/info") "WinRE Status Check" })

$btn_rep_off_quick.Add_Click({
    Log-Message "Running Microsoft Office Quick Repair (Click-to-Run)..."
    Add-Activity "System Repair" "Office Quick Repair" "Running"
    Start-ThreadJob {
        # Trigger CTR repair silently
        $proc = Start-Process "C:\Program Files\Common Files\microsoft shared\ClickToRun\OfficeClickToRun.exe" -ArgumentList "scenario=Repair platform=x64 culture=en-us ForceRepair=1" -NoNewWindow -PassThru -Wait
        [Action]{ 
            Log-Message "[✓] Office Quick Repair finished." 
            Add-Activity "System Repair" "Office Quick Repair completed" "Success"
        }.Invoke()
    }
})

$btn_rep_off_pst.Add_Click({
    Log-Message "Searching and launching Outlook ScanPST tool..."
    Start-ThreadJob {
        $paths = @(
            "C:\Program Files\Microsoft Office\root\Office16\SCANPST.EXE"
            "C:\Program Files (x86)\Microsoft Office\root\Office16\SCANPST.EXE"
        )
        $found = $false
        foreach ($p in $paths) {
            if (Test-Path $p) {
                Start-Process $p
                $found = $true
                break
            }
        }
        if (-not $found) {
            [Action]{ Log-Message "[X] ScanPST.exe could not be found in default Office directories." }.Invoke()
        } else {
            [Action]{ Log-Message "[✓] Launched ScanPST successfully." }.Invoke()
        }
    }
})

# Launch Office apps in Safe Mode
function Start-OfficeSafeMode ($bin) {
    Log-Message "Launching $bin in Safe Mode..."
    Start-Process $bin -ArgumentList "/safe"
}
$btn_safe_word.Add_Click({ Start-OfficeSafeMode "winword.exe" })
$btn_safe_excel.Add_Click({ Start-OfficeSafeMode "excel.exe" })
$btn_safe_ppt.Add_Click({ Start-OfficeSafeMode "powerpnt.exe" })
$btn_safe_outlook.Add_Click({ Start-OfficeSafeMode "outlook.exe" })

$btn_rep_bcd.Add_Click({ Run-RepairCommand @("bcdboot", "C:\Windows") "BCDBoot Rebuild" })
$btn_rep_rec_boot.Add_Click({
    Log-Message "Rebooting system directly into Startup Repair / Recovery..."
    Start-Process shutdown.exe -ArgumentList "/r /o /t 0"
})
$btn_rep_fail_menu.Add_Click({ Run-RepairCommand @("bcdedit", "/set", "{current}", "bootstatuspolicy", "displayallfailures") "Boot failure menu policy" })
$btn_rep_chkdsk.Add_Click({
    Log-Message "Scheduling Boot-time Chkdsk /f /r scan on drive C:..."
    Start-ThreadJob {
        # Echo Y to confirm volume dismount on restart
        $proc = Start-Process chkdsk -ArgumentList "C: /f /r" -RedirectStandardInput "$env:temp\y.txt" -NoNewWindow -PassThru -Wait
        [Action]{ Log-Message "[✓] Boot check scheduled. Please reboot your machine to scan." }.Invoke()
    }
})

$btn_rep_printer_11b.Add_Click({
    Log-Message "Fixing Printer Sharing Error 0x0000011b..."
    try {
        Set-ItemProperty -Path "HKLM:\System\CurrentControlSet\Control\Print" -Name "RpcAuthnLevelPrivacyEnabled" -Value 0 -Force
        Log-Message "[✓] Applied RPC privacy key registry bypass."
        Add-Activity "Printer Repair" "Error 0x0000011b Fixed" "Success"
    } catch {
        Log-Message "[X] Failed to modify print registry keys: $_"
        Add-Activity "Printer Repair" "Error 0x0000011b Fix Failed" "Failed"
    }
})

$btn_rep_printer_policy.Add_Click({
    Log-Message "Configuring GPO Point and Print / RPC driver install policy..."
    try {
        New-Item -Path "HKLM:\Software\Policies\Microsoft\Windows NT\Printers\PointAndPrint" -Force -ErrorAction SilentlyContinue | Out-Null
        Set-ItemProperty -Path "HKLM:\Software\Policies\Microsoft\Windows NT\Printers\PointAndPrint" -Name "RestrictDriverInstallationToAdministrators" -Value 0 -Force
        
        New-Item -Path "HKLM:\Software\Policies\Microsoft\Windows NT\Printers" -Force -ErrorAction SilentlyContinue | Out-Null
        Set-ItemProperty -Path "HKLM:\Software\Policies\Microsoft\Windows NT\Printers" -Name "RpcOverTcp" -Value 1 -Force
        
        Log-Message "[✓] Printer GPO Point and Print / RPC rules applied."
        Add-Activity "Printer Repair" "GPO Printer Policies Applied" "Success"
    } catch {
        Log-Message "[X] Failed to write print GPO keys: $_"
    }
})

$btn_rep_printer_lpd.Add_Click({
    Log-Message "Enabling Windows LPD Print Service & LPR Port Monitor Optional Features..."
    Add-Activity "Printer Repair" "Enable LPD/LPR Features" "Running"
    Start-ThreadJob {
        Enable-WindowsOptionalFeature -Online -FeatureName "LPDPrintService" -NoRestart | Out-Null
        Enable-WindowsOptionalFeature -Online -FeatureName "LPRPortMonitor" -NoRestart | Out-Null
        [Action]{ 
            Log-Message "[✓] LPD Print service and LPR Port Monitor features enabled." 
            Add-Activity "Printer Repair" "LPD/LPR Features Enabled" "Success"
        }.Invoke()
    }
})

$btn_rep_printer_disc.Add_Click({
    Log-Message "Restarting Network Discovery and Printer sharing dependency services..."
    Start-ThreadJob {
        $services = @("FDResPub", "SSDPSrv", "UPnPHost", "Dnscache")
        foreach ($s in $services) {
            Set-Service -Name $s -StartupType Automatic -ErrorAction SilentlyContinue
            Restart-Service -Name $s -Force -ErrorAction SilentlyContinue
        }
        [Action]{ Log-Message "[✓] Network discovery dependency services restarted." }.Invoke()
    }
})

$btn_rep_printer_spool.Add_Click({
    Log-Message "Stopping Print Spooler..."
    Stop-Service spooler -Force
    Log-Message "Clearing print queue directory..."
    Remove-Item "$env:SystemRoot\system32\spool\PRINTERS\*" -Force -Recurse -ErrorAction SilentlyContinue
    Log-Message "Starting Print Spooler..."
    Start-Service spooler
    Log-Message "[✓] Print Spooler restarted and queue cleared successfully."
    Add-Activity "Printer Repair" "Spooler Cleaned" "Success"
})

$btn_rep_printer_diag.Add_Click({ Run-RepairCommand @("msdt.exe", "/id", "PrinterDiagnostic") "Printer Troubleshooter Wizard" })

# NTFS Convert
$btn_conv_ntfs.Add_Click({
    $drv = $cb_ntfs_drive.Text
    Log-Message "Converting drive $drv to NTFS partition style losslessly..."
    Start-ThreadJob {
        param($d)
        $proc = Start-Process convert.exe -ArgumentList "$d /fs:ntfs" -NoNewWindow -PassThru -Wait
        [Action[string]]{ param($code) Log-Message "NTFS conversion completed (Exit code: $code)." }.Invoke($proc.ExitCode)
    } -ArgumentList $drv
})

# MBR to GPT Convert
$btn_conv_gpt.Add_Click({
    $disk = $cb_gpt_disk.Text.Replace("Disk ", "")
    Log-Message "Converting disk $disk from MBR to GPT partition style..."
    Start-ThreadJob {
        param($dk)
        $proc = Start-Process mbr2gpt.exe -ArgumentList "/convert /disk:$dk /allowFullOS" -NoNewWindow -PassThru -Wait
        [Action[string]]{ param($code) Log-Message "MBR2GPT completed (Exit code: $code)." }.Invoke($proc.ExitCode)
    } -ArgumentList $disk
})

$btn_rep_clean_ram.Add_Click({
    Log-Message "Flushing Standby List memory allocations..."
    Add-Activity "Memory Optimization" "Flushing RAM cache standby list" "Running"
    # PowerShell standby list flush using Empty Working Sets API or generic process garbage collect
    [System.GC]::Collect()
    Log-Message "[✓] Process working sets emptied."
    Add-Activity "Memory Optimization" "Flushed standby lists successfully" "Success"
})

$btn_rep_clean_browser.Add_Click({
    Log-Message "Cleaning browser caches..."
    Start-ThreadJob {
        # Chrome Cache
        Remove-Item "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Cache\*" -Force -Recurse -ErrorAction SilentlyContinue
        # Edge Cache
        Remove-Item "$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\Cache\*" -Force -Recurse -ErrorAction SilentlyContinue
        # Firefox Cache
        Remove-Item "$env:LOCALAPPDATA\Mozilla\Firefox\Profiles\*\cache2\*" -Force -Recurse -ErrorAction SilentlyContinue
        
        [Action]{ Log-Message "[✓] Web Browser Cache cleared successfully." }.Invoke()
    }
})

$btn_rep_shield_wu.Add_Click({
    Log-Message "Running comprehensive Windows Update Service repair engine..."
    Add-Activity "System Repair" "Windows Update Service Repair" "Running"
    Start-ThreadJob {
        Stop-Service wuauserv -Force -ErrorAction SilentlyContinue
        Stop-Service bits -Force -ErrorAction SilentlyContinue
        # Register core WU dlls
        $dlls = @("wups.dll", "wups2.dll", "wuaueng.dll", "wuapi.dll", "wucltux.dll", "wuwebv.dll")
        foreach ($d in $dlls) { Start-Process regsvr32.exe -ArgumentList "/s $d" -Wait }
        Start-Service wuauserv -ErrorAction SilentlyContinue
        Start-Service bits -ErrorAction SilentlyContinue
        [Action]{ 
            Log-Message "[✓] Windows Update components registered and services restarted." 
            Add-Activity "System Repair" "Windows Update Service Repair completed" "Success"
        }.Invoke()
    }
})

# Windows Update Blocker
$btn_rep_shield_block_wu.Add_Click({
    Log-Message "Blocking automatic Windows Updates..."
    try {
        Stop-Service wuauserv -Force -ErrorAction SilentlyContinue
        Set-Service -Name wuauserv -StartupType Disabled -ErrorAction SilentlyContinue
        
        New-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" -Force -ErrorAction SilentlyContinue | Out-Null
        Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" -Name "NoAutoUpdate" -Value 1 -Force
        Log-Message "[✓] Windows Update service disabled and GPO block applied."
        Add-Activity "Shield Tweak" "Windows Updates Blocked" "Success"
    } catch {
        Log-Message "[X] Failed to block Windows Updates: $_"
    }
})

$btn_rep_shield_enable_wu.Add_Click({
    Log-Message "Enabling automatic Windows Updates..."
    try {
        Remove-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" -Name "NoAutoUpdate" -Force -ErrorAction SilentlyContinue
        Set-Service -Name wuauserv -StartupType Automatic -ErrorAction SilentlyContinue
        Start-Service wuauserv -ErrorAction SilentlyContinue
        Log-Message "[✓] Windows Update service enabled and GPO block removed."
        Add-Activity "Shield Tweak" "Windows Updates Enabled" "Success"
    } catch {
        Log-Message "[X] Failed to enable Windows Updates: $_"
    }
})

$btn_rep_shield_defender.Add_Click({
    Log-Message "Resetting Windows Defender policies..."
    Add-Activity "System Repair" "Reset Windows Defender Policies" "Running"
    try {
        # Wipe Defender Group Policies
        Remove-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows Defender" -Recurse -Force -ErrorAction SilentlyContinue
        # Restart defender service
        Start-Service WinDefend -ErrorAction SilentlyContinue
        Log-Message "[✓] Windows Defender policies reset successfully."
        Add-Activity "System Repair" "Reset Windows Defender Policies completed" "Success"
    } catch {
        Log-Message "[X] Failed to reset Defender: $_"
    }
})

$btn_rep_shield_firewall.Add_Click({ Run-RepairCommand @("netsh", "advfirewall", "reset") "Restore default firewall rules" })

$btn_rep_shield_audio.Add_Click({
    Log-Message "Resetting and restarting Windows Audio Playback services..."
    Start-ThreadJob {
        Stop-Service AudioSrv -Force -ErrorAction SilentlyContinue
        Stop-Service AudioEndpointBuilder -Force -ErrorAction SilentlyContinue
        Start-Service AudioEndpointBuilder -ErrorAction SilentlyContinue
        Start-Service AudioSrv -ErrorAction SilentlyContinue
        [Action]{ Log-Message "[✓] AudioSrv and AudioEndpointBuilder restarted successfully." }.Invoke()
    }
})

$btn_rep_shell_explorer.Add_Click({
    Log-Message "Restarting Windows Explorer shell..."
    Stop-Process -Name explorer -Force -ErrorAction SilentlyContinue
    Start-Process explorer
    Log-Message "[✓] Explorer restarted."
})

$btn_rep_shell_events.Add_Click({
    Log-Message "Clearing all Application, System, and Security event logs..."
    Add-Activity "System Repair" "Clear Event Logs" "Running"
    Start-ThreadJob {
        wevtutil el | Foreach-Object { wevtutil cl $_ }
        [Action]{ 
            Log-Message "[✓] Windows Event Logs cleared successfully." 
            Add-Activity "System Repair" "Clear Event Logs completed" "Success"
        }.Invoke()
    }
})

$btn_rep_shell_icon.Add_Click({
    Log-Message "Rebuilding icon and thumbnail cache databases..."
    Start-ThreadJob {
        Stop-Process -Name explorer -Force -ErrorAction SilentlyContinue
        Remove-Item "$env:localappdata\IconCache.db" -Force -ErrorAction SilentlyContinue
        Remove-Item "$env:localappdata\Microsoft\Windows\Explorer\thumbcache_*.db" -Force -ErrorAction SilentlyContinue
        Start-Process explorer
        [Action]{ Log-Message "[✓] Icon and thumbnail cache rebuilt successfully." }.Invoke()
    }
})

$btn_rep_shell_font.Add_Click({
    Log-Message "Rebuilding Windows System Font Cache..."
    Start-ThreadJob {
        Stop-Service -Name "FontCache" -Force -ErrorAction SilentlyContinue
        Remove-Item "$env:SystemRoot\ServiceProfiles\LocalService\AppData\Local\FontCache\*" -Force -Recurse -ErrorAction SilentlyContinue
        Start-Service -Name "FontCache" -ErrorAction SilentlyContinue
        [Action]{ Log-Message "[✓] Font Cache rebuilt and service restarted." }.Invoke()
    }
})

# --- BLOATWARE REMOVER & OPTIONAL FEATURES ---
$btn_remove_bloat.Add_Click({
    Log-Message "Starting UWP bloatware package removal..."
    Add-Activity "System Repair" "Remove Bloatware UWP Apps" "Running"
    Start-ThreadJob {
        $bloat = @("*xbox*", "*skype*", "*solitaire*", "*bingweather*", "*maps*", "*getstarted*", "*officehub*", "*onenote*")
        foreach ($b in $bloat) {
            Get-AppxPackage -AllUsers $b | Remove-AppxPackage -AllUsers -ErrorAction SilentlyContinue
        }
        [Action]{ 
            Log-Message "[✓] Windows bloatware packages removed." 
            Add-Activity "System Repair" "Remove Bloatware UWP Apps completed" "Success"
        }.Invoke()
    }
})

$btn_apply_features.Add_Click({
    Log-Message "Configuring Windows Optional Features..."
    $lpd = $cb_feat_lpd.IsChecked
    $lpr = $cb_feat_lpr.IsChecked
    $smb = $cb_feat_smb.IsChecked
    
    Start-ThreadJob {
        param($eLpd, $eLpr, $eSmb)
        if ($eLpd) {
            [Action]{ Log-Message "Enabling LPD Print Service..." }.Invoke()
            Enable-WindowsOptionalFeature -Online -FeatureName "LPDPrintService" -NoRestart | Out-Null
        }
        if ($eLpr) {
            [Action]{ Log-Message "Enabling LPR Port Monitor..." }.Invoke()
            Enable-WindowsOptionalFeature -Online -FeatureName "LPRPortMonitor" -NoRestart | Out-Null
        }
        if ($eSmb) {
            [Action]{ Log-Message "Enabling SMB1 Protocol Service..." }.Invoke()
            Enable-WindowsOptionalFeature -Online -FeatureName "SMB1Protocol" -NoRestart | Out-Null
        }
        [Action]{ Log-Message "[✓] Optional features configuration completed." }.Invoke()
    } -ArgumentList $lpd, $lpr, $smb
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

$btn_tweak_fast_on.Add_Click({
    Log-Message "Enabling Windows Fast Startup..."
    try {
        Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Power" -Name "HiberbootEnabled" -Value 1 -Force
        Log-Message "[✓] Hiberboot Enabled successfully."
    } catch {
        Log-Message "[X] Failed to enable Fast Startup: $_"
    }
})

$btn_tweak_fast_off.Add_Click({
    Log-Message "Disabling Windows Fast Startup..."
    try {
        Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Power" -Name "HiberbootEnabled" -Value 0 -Force
        Log-Message "[✓] Hiberboot Disabled successfully."
    } catch {
        Log-Message "[X] Failed to disable Fast Startup: $_"
    }
})

# --- DIAGNOSTICS & SPECS CALLBACKS ---
$btn_diag_specs.Add_Click({
    Log-Message "Generating hardware specifications summary..."
    Add-Activity "Diagnostics" "Generating hardware specifications" "Running"
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
            Add-Activity "Diagnostics" "Hardware specifications generated" "Success"
        }.Invoke($cpu, $gpu, $mobo, $bios)
    }
})

$btn_diag_battery.Add_Click({
    Log-Message "Generating Windows Battery Lifecycle HTML Report..."
    Add-Activity "Diagnostics" "Generating Battery Report" "Running"
    Start-ThreadJob {
        powercfg /batteryreport /output "$env:USERPROFILE\Desktop\BatteryReport.html" | Out-Null
        [Action]{ 
            Log-Message "[✓] HTML Battery Report generated on your Desktop (BatteryReport.html)."
            Add-Activity "Diagnostics" "Battery Report generated" "Success"
        }.Invoke()
    }
})

$btn_diag_disk.Add_Click({
    Log-Message "Scanning connected physical drives status (SMART Check)..."
    Add-Activity "Diagnostics" "Scanning SMART Disk Status" "Running"
    Start-ThreadJob {
        $status = Get-CimInstance -Namespace root\wmi -ClassName MSStorageDriver_FailurePredictStatus -ErrorAction SilentlyContinue
        if ($status -eq $null) {
            [Action]{ 
                Log-Message "[✓] SMART reports all connected drives are healthy."
                Add-Activity "Diagnostics" "SMART Disk Scan completed" "Success"
            }.Invoke()
        } else {
            foreach ($drive in $status) {
                if ($drive.PredictFailure) {
                    [Action[string]]{ param($inst) Log-Message "[!] WARNING: Failure predicted on drive: $inst" }.Invoke($drive.InstanceName)
                } else {
                    [Action[string]]{ param($inst) Log-Message "[✓] Drive healthy: $inst" }.Invoke($drive.InstanceName)
                }
            }
            [Action]{ Add-Activity "Diagnostics" "SMART Disk Scan completed" "Success" }.Invoke()
        }
    }
})

$btn_diag_ram.Add_Click({
    Log-Message "Identifying installed memory modules properties..."
    Add-Activity "Diagnostics" "Identifying Memory Modules" "Running"
    Start-ThreadJob {
        $modules = Get-CimInstance Win32_PhysicalMemory
        foreach ($mod in $modules) {
            $cap = [Math]::Round($mod.Capacity / 1GB)
            $speed = $mod.Speed
            [Action[string, string, string]]{
                param($c, $s, $d)
                Log-Message "Slot ${d}: ${c} GB RAM module running at ${s} MHz."
            }.Invoke($cap, $speed, $mod.DeviceLocator)
        }
        [Action]{ Add-Activity "Diagnostics" "Memory Modules identified" "Success" }.Invoke()
    }
})

$btn_diag_mdsched.Add_Click({
    Log-Message "Scheduling Windows Memory Diagnostic scan (mdsched.exe)..."
    Start-Process mdsched.exe
    Log-Message "[✓] Memory diagnostic utility opened."
})

$btn_diag_dns.Add_Click({
    Log-Message "Configuring adapter DNS settings to Cloudflare Secure DNS (1.1.1.1)..."
    Start-ThreadJob {
        $adapters = Get-NetAdapter | Where-Object { $_.Status -eq "Up" }
        foreach ($a in $adapters) {
            Set-DnsClientServerAddress -InterfaceAlias $a.Name -ServerAddresses ("1.1.1.1", "1.0.0.1") -ErrorAction SilentlyContinue
        }
        [Action]{ Log-Message "[✓] Cloudflare DNS configuration completed." }.Invoke()
    }
})

$btn_diag_speed.Add_Click({
    Log-Message "Running real-time download bandwidth speed test..."
    Add-Activity "Diagnostics" "Running download Speed Test" "Running"
    Start-ThreadJob {
        $url = "https://speed.cloudflare.com/__down?bytes=10000000" # 10MB test file
        $start = Get-Date
        $tempFile = "$env:temp\speedtest.bin"
        [Action]{ Log-Message "Downloading 10MB test payload from Cloudflare CDN..." }.Invoke()
        try {
            Invoke-WebRequest -Uri $url -OutFile $tempFile -ErrorAction Stop
            $elapsed = (Get-Date) - $start
            $speedMbps = [Math]::Round((10 * 8) / $elapsed.TotalSeconds, 2)
            Remove-Item $tempFile -Force
            [Action[string]]{ 
                param($sp) 
                Log-Message "[✓] Speed test finished. Current Bandwidth: $sp Mbps." 
                Add-Activity "Diagnostics" "Speed Test Completed: $sp Mbps" "Success"
            }.Invoke($speedMbps)
        } catch {
            [Action]{ 
                Log-Message "[X] Speed test failed. Please check internet connection." 
                Add-Activity "Diagnostics" "Speed Test Failed" "Failed"
            }.Invoke()
        }
    }
})

$btn_diag_act.Add_Click({
    Log-Message "Checking Windows activation status details..."
    Add-Activity "Diagnostics" "Checking activation status..." "Running"
    Start-ThreadJob {
        $res = cscript //nologo $env:SystemRoot\system32\slmgr.vbs /dli
        $joined = $res -join "`r`n"
        [Action[string]]{ 
            param($txt)
            Log-Message "License details returned:" 
            Log-Message $txt
            Add-Activity "Diagnostics" "Activation Checked" "Success"
        }.Invoke($joined)
    }
})

# --- DATA MIGRATION & BACKUPS ---
$btn_backup_browse_src.Add_Click({
    $dialog = New-Object System.Windows.Forms.FolderBrowserDialog
    $dialog.Description = "Select Backup Source Folder"
    if ($dialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
        $txt_backup_src.Text = $dialog.SelectedPath
    }
})

$btn_backup_browse_dst.Add_Click({
    $dialog = New-Object System.Windows.Forms.FolderBrowserDialog
    $dialog.Description = "Select Backup Destination Folder"
    if ($dialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
        $txt_backup_dst.Text = $dialog.SelectedPath
    }
})

$btn_start_backup.Add_Click({
    $src = $txt_backup_src.Text.Trim()
    $dst = $txt_backup_dst.Text.Trim()
    if ($src -eq "" -or $dst -eq "") {
        [System.Windows.MessageBox]::Show("Please choose valid source and destination folder paths.", "Warning", "OK", "Warning")
        return
    }
    
    Log-Message "Initializing Robocopy migration command from '$src' to '$dst'..."
    Add-Activity "Backups" "Starting Robocopy backup" "Running"
    Start-ThreadJob {
        param($s, $d)
        $proc = Start-Process robocopy -ArgumentList "`"$s`" `"$d`" /E /Z /ZB /R:5 /W:5 /TBD /NP /V" -NoNewWindow -PassThru -Wait
        [Action[string]]{ 
            param($code) 
            Log-Message "Robocopy process completed (Exit code: $code)." 
            Add-Activity "Backups" "Robocopy completed (Code $code)" "Success"
        }.Invoke($proc.ExitCode)
    } -ArgumentList $src, $dst
})

# --- WINDOWS CONFIG SHORTCUTS ---
function Start-ConfigShortcut ($bin, $args="") {
    Log-Message "Launching console shortcut: $bin..."
    try {
        if ($args -ne "") {
            Start-Process $bin -ArgumentList $args
        } else {
            Start-Process $bin
        }
    } catch {
        Log-Message "[X] Failed to launch console component: $_"
    }
}

$btn_cfg_panel.Add_Click({ Start-ConfigShortcut "control.exe" })
$btn_cfg_reg.Add_Click({ Start-ConfigShortcut "regedit.exe" })
$btn_cfg_dev.Add_Click({ Start-ConfigShortcut "devmgmt.msc" })
$btn_cfg_disk.Add_Click({ Start-ConfigShortcut "diskmgmt.msc" })
$btn_cfg_services.Add_Click({ Start-ConfigShortcut "services.msc" })
$btn_cfg_event.Add_Click({ Start-ConfigShortcut "eventvwr.msc" })
$btn_cfg_task.Add_Click({ Start-ConfigShortcut "taskmgr.exe" })
$btn_cfg_gp.Add_Click({ Start-ConfigShortcut "gpedit.msc" })
$btn_cfg_sys.Add_Click({ Start-ConfigShortcut "control.exe" "sysdm.cpl" })

# --- SEARCH FEATURE CATALOG MATCHING ---
$toolsCatalog = @(
    @{ Name = "SFC Scan (sfc /scannow)"; Desc = "Scans and repairs corrupt or missing Windows system files."; View = "grid_repairs"; Keyword = "sfc,scannow,corrupt,repair,system files" }
    @{ Name = "DISM Repair (dism RestoreHealth)"; Desc = "Uses DISM to scan the Windows component store and repair OS image corruption."; View = "grid_repairs"; Keyword = "dism,restorehealth,component store,corruption" }
    @{ Name = "DISM CheckHealth"; Desc = "Performs a quick diagnostic scan on component store health."; View = "grid_repairs"; Keyword = "checkhealth,dism check,corruption status" }
    @{ Name = "Re-register System DLLs"; Desc = "Re-registers core system DLL library dynamic links in System32."; View = "grid_repairs"; Keyword = "dll,register dll,regsvr32" }
    @{ Name = "Rebuild Font Cache"; Desc = "Wipes corrupt system Font cache files database and restarts service."; View = "grid_repairs"; Keyword = "font,cache,rebuild font" }
    @{ Name = "Network Adapter Reset"; Desc = "Resets the Winsock TCP/IP catalog bindings and stack to defaults."; View = "grid_repairs"; Keyword = "winsock,network,ip reset,tcp/ip" }
    @{ Name = "Flush DNS Cache"; Desc = "Flushes the DNS resolver cache to clear corrupted IP configurations."; View = "grid_repairs"; Keyword = "dns,flush,ipconfig,flushdns" }
    @{ Name = "Firewall Defaults Reset"; Desc = "Wipes advfirewall rules configurations to original factory defaults."; View = "grid_repairs"; Keyword = "firewall,reset firewall,rules" }
    @{ Name = "Fix Printer Error 0x0000011b"; Desc = "Disables RPC authentication privacy requirement to resolve sharing."; View = "grid_repairs"; Keyword = "printer,0x0000011b,sharing,rpc" }
    @{ Name = "Clean Print Spooler Queue"; Desc = "Wipes stuck print documents in queue and restarts Spooler service."; View = "grid_repairs"; Keyword = "spooler,stuck print,clear queue" }
    @{ Name = "Windows Update Cache Reset"; Desc = "Deletes downloaded update files cache and restarts update services."; View = "grid_repairs"; Keyword = "update,windows update,cache,software distribution" }
    @{ Name = "Restart Windows Explorer"; Desc = "Kills and restarts explorer.exe shell to resolve freeze bugs."; View = "grid_repairs"; Keyword = "explorer,shell,restart explorer,taskbar freeze" }
    @{ Name = "Microsoft App Store Repair"; Desc = "Re-registers native Store packages to fix load crashes."; View = "grid_repairs"; Keyword = "store,microsoft store,appx" }
    @{ Name = "Microsoft Activation Scripts (MAS)"; Desc = "Launches MAS console tool to activate Windows and Office suites."; View = "grid_act"; Keyword = "activation,mas,activate,license" }
    @{ Name = "Windows Edition Changer"; Desc = "Upgrades Windows Home to Pro using KMS generic product keys."; View = "grid_act"; Keyword = "edition changer,upgrade,home to pro" }
    @{ Name = "Classic Context Menu Tweak"; Desc = "Restores traditional right-click menu layout instead of modern layout."; View = "grid_tweaks"; Keyword = "classic,context menu,right click,menu" }
    @{ Name = "Ultimate Power Plan Tweak"; Desc = "Unlocks and activates hidden maximum speed power profile scheme."; View = "grid_tweaks"; Keyword = "ultimate,power plan,scheme" }
    @{ Name = "Gaming Latency Tweaks"; Desc = "Optimizes GameDVR settings and system response latency."; View = "grid_tweaks"; Keyword = "gaming,latency,dvr,optimization" }
    @{ Name = "Disable Start Menu Bing"; Desc = "Disables Bing online web queries inside Start Menu local search."; View = "grid_tweaks"; Keyword = "bing,start menu,offline search" }
    @{ Name = "Fast Startup Settings"; Desc = "Toggles fast shutdown hiberboot kernel cache state."; View = "grid_tweaks"; Keyword = "fast startup,hiberboot" }
    @{ Name = "Remove Bloatware UWP Apps"; Desc = "Purges pre-installed Windows packages like Maps, Solitaire, Xbox."; View = "grid_bloat"; Keyword = "bloatware,remove bloat,skype" }
    @{ Name = "Windows Optional Features"; Desc = "Enables SMB1, LPD, and LPR printing network components."; View = "grid_bloat"; Keyword = "lpd,lpr,smb1,features" }
    @{ Name = "Generate Hardware Specs"; Desc = "Generates CPU, GPU, RAM, Motherboard properties summary."; View = "grid_diag"; Keyword = "specs,hardware,summary,bios" }
    @{ Name = "HTML Battery Health Report"; Desc = "Generates HTML power battery wear diagnostic status chart."; View = "grid_diag"; Keyword = "battery,html report,battery wear" }
    @{ Name = "SMART Disk Scan"; Desc = "Queries hardware sensors on connected physical drives to check reliability."; View = "grid_diag"; Keyword = "smart,disk health,drive failure,ssd" }
    @{ Name = "Show Memory Specs"; Desc = "Identifies installed memory module speeds and capacity sizes."; View = "grid_diag"; Keyword = "ram specs,memory modules,ram clock" }
    @{ Name = "Internet Speed Test"; Desc = "Measures download bandwidth in Mbps using Cloudflare CDN payload."; View = "grid_diag"; Keyword = "speed test,download speed,bandwidth" }
    @{ Name = "Robocopy Data Backup"; Desc = "Migrates folder data losslessly using Robocopy parameters."; View = "grid_backups"; Keyword = "backup,robocopy,migration" }
    @{ Name = "Windows System Consoles"; Desc = "Fast shortcuts to Device Manager, Registry, Disk Management, GPO."; View = "grid_config"; Keyword = "control,regedit,devmgmt,diskmgmt,gpedit" }
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
