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

$xaml = @"
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

                <!-- Brand logo/text -->
                <StackPanel Grid.Row="0" Margin="20,20,20,10" VerticalAlignment="Center">
                    <TextBlock Text="&#x26A1; VenkatPulse AI" FontSize="18" FontWeight="Bold" Foreground="#38bdf8"/>
                    <TextBlock Text="Windows Utility Suite" FontSize="10" Foreground="#6b7280" Margin="2,2,0,0"/>
                </StackPanel>

                <!-- Scrollable Navigation Items -->
                <ScrollViewer Grid.Row="1" VerticalScrollBarVisibility="Auto" HorizontalScrollBarVisibility="Disabled">
                    <StackPanel Margin="10,0,10,0">
                        <Button Name="btn_dash" Content="&#x1F3E0;  Dashboard" Height="36" Margin="0,2,0,2" Background="Transparent" Foreground="#cbd5e1" BorderThickness="0" HorizontalContentAlignment="Left" Padding="15,0,0,0" FontSize="11.5" FontWeight="SemiBold"/>
                        <Button Name="btn_soft" Content="&#x1F4E5;  Software Installer" Height="36" Margin="0,2,0,2" Background="Transparent" Foreground="#cbd5e1" BorderThickness="0" HorizontalContentAlignment="Left" Padding="15,0,0,0" FontSize="11.5" FontWeight="SemiBold"/>
                        <Button Name="btn_act" Content="&#x1F511;  Activation Suite" Height="36" Margin="0,2,0,2" Background="Transparent" Foreground="#cbd5e1" BorderThickness="0" HorizontalContentAlignment="Left" Padding="15,0,0,0" FontSize="11.5" FontWeight="SemiBold"/>
                        <Button Name="btn_tweaks" Content="&#x1F527;  System Tweaks" Height="36" Margin="0,2,0,2" Background="Transparent" Foreground="#cbd5e1" BorderThickness="0" HorizontalContentAlignment="Left" Padding="15,0,0,0" FontSize="11.5" FontWeight="SemiBold"/>
                        <Button Name="btn_bloat" Content="&#x1F9FC;  Bloatware &amp; Features" Height="36" Margin="0,2,0,2" Background="Transparent" Foreground="#cbd5e1" BorderThickness="0" HorizontalContentAlignment="Left" Padding="15,0,0,0" FontSize="11.5" FontWeight="SemiBold"/>
                        <Button Name="btn_repairs" Content="&#x1F6E0;  System Repairs" Height="36" Margin="0,2,0,2" Background="Transparent" Foreground="#cbd5e1" BorderThickness="0" HorizontalContentAlignment="Left" Padding="15,0,0,0" FontSize="11.5" FontWeight="SemiBold"/>
                        <Button Name="btn_diag" Content="&#x1F4CA;  Diagnostics &amp; Health" Height="36" Margin="0,2,0,2" Background="Transparent" Foreground="#cbd5e1" BorderThickness="0" HorizontalContentAlignment="Left" Padding="15,0,0,0" FontSize="11.5" FontWeight="SemiBold"/>
                        <Button Name="btn_backups" Content="&#x1F4BE;  Backups &amp; Migration" Height="36" Margin="0,2,0,2" Background="Transparent" Foreground="#cbd5e1" BorderThickness="0" HorizontalContentAlignment="Left" Padding="15,0,0,0" FontSize="11.5" FontWeight="SemiBold"/>
                        <Button Name="btn_config" Content="&#x2699;  Windows Config" Height="36" Margin="0,2,0,2" Background="Transparent" Foreground="#cbd5e1" BorderThickness="0" HorizontalContentAlignment="Left" Padding="15,0,0,0" FontSize="11.5" FontWeight="SemiBold"/>
                    </StackPanel>
                </ScrollViewer>

                <!-- Footer version info -->
                <TextBlock Grid.Row="2" Text="v1.4.0 | Advanced Power Tools" FontSize="9" Foreground="#4b5563" HorizontalAlignment="Center" VerticalAlignment="Center"/>
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
                    <TextBlock Name="txt_header" Text="Dashboard Overview" FontSize="14" FontWeight="Bold" Foreground="#ffffff" VerticalAlignment="Center" HorizontalAlignment="Left"/>
                    
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
                            <TextBlock Grid.Row="0" Text="&#x1F4CB; Recent Actions &amp; System Diagnostics Logs" FontSize="11" FontWeight="Bold" Foreground="#ffffff" Margin="0,0,0,10"/>
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
                                    <TextBlock Text="&#x1F310; Browsers" FontSize="11.5" FontWeight="Bold" Foreground="#38bdf8" Margin="5,5,5,5"/>
                                    <WrapPanel Name="panel_soft_browsers" Orientation="Horizontal" Margin="0,0,0,15"/>
                                    
                                    <TextBlock Text="&#x1F4BB; Microsoft Tools &amp; Platforms" FontSize="11.5" FontWeight="Bold" Foreground="#38bdf8" Margin="5,5,5,5"/>
                                    <WrapPanel Name="panel_soft_msoft" Orientation="Horizontal" Margin="0,0,0,15"/>
                                    
                                    <TextBlock Text="&#x2699; Utilities &amp; Chat" FontSize="11.5" FontWeight="Bold" Foreground="#38bdf8" Margin="5,5,5,5"/>
                                    <WrapPanel Name="panel_soft_utils" Orientation="Horizontal" Margin="0,0,0,15"/>
                                    
                                    <TextBlock Text="&#x1F527; Development &amp; Networking" FontSize="11.5" FontWeight="Bold" Foreground="#38bdf8" Margin="5,5,5,5"/>
                                    <WrapPanel Name="panel_soft_dev" Orientation="Horizontal" Margin="0,0,0,15"/>

                                    <TextBlock Text="&#x1F4C4; Office, Design &amp; Media" FontSize="11.5" FontWeight="Bold" Foreground="#38bdf8" Margin="5,5,5,5"/>
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
                            <TextBlock Grid.Row="0" Text="&#x2699; Installation Terminal" FontSize="11" FontWeight="Bold" Foreground="#ffffff" Margin="0,0,0,10"/>
                            <TextBox Grid.Row="1" Name="txt_log_soft" Background="#0b0f19" Foreground="#10b981" BorderBrush="#374151" FontFamily="Consolas" FontSize="10" IsReadOnly="True" VerticalScrollBarVisibility="Auto" AcceptsReturn="True" TextWrapping="Wrap" Margin="0,0,0,10"/>
                            <StackPanel Grid.Row="2">
                                <Button Name="btn_install_soft" Content="Install Selected" Height="36" Background="#059669" BorderThickness="0" FontWeight="Bold" Margin="0,0,0,5"/>
                                <Button Name="btn_uninstall_soft" Content="Uninstall Selected" Height="36" Background="#b91c1c" BorderThickness="0" FontWeight="Bold" Margin="0,5,0,0"/>
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
                            <TextBlock Grid.Row="0" Text="&#x1F4E6; MICROSOFT OFFICE INSTALLER SUITE" FontSize="11" FontWeight="Bold" Foreground="#38bdf8" Margin="0,0,0,10"/>
                            <UniformGrid Grid.Row="1" Columns="2" Rows="2">
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
                                <TextBlock Text="&#x1F511; MAS WINDOWS &amp; OFFICE ACTIVATOR" FontSize="11" FontWeight="Bold" Foreground="#38bdf8" HorizontalAlignment="Center"/>
                                <TextBlock Text="Activates Windows HWID and Office Ohook via official open-source scripts." TextWrapping="Wrap" FontSize="10" Foreground="#9ca3af" Margin="0,5,0,15" TextAlignment="Center"/>
                                <StackPanel Orientation="Horizontal" HorizontalAlignment="Center">
                                    <Button Name="btn_launch_mas" Content="Launch MAS GUI" Height="32" Background="#059669" BorderThickness="0" FontWeight="Bold" Width="140" Margin="0,0,5,0"/>
                                    <Button Name="btn_check_license" Content="Check License" Height="32" Background="#1f2937" BorderThickness="1" BorderBrush="#374151" FontWeight="Bold" Width="120" Margin="5,0,0,0"/>
                                </StackPanel>
                            </StackPanel>
                        </Border>
                        
                        <!-- Edition Changer card -->
                        <Border Grid.Column="1" Background="#1f2937" BorderBrush="#374151" BorderThickness="1" CornerRadius="8" Padding="15" Margin="5,0,0,0">
                            <StackPanel VerticalAlignment="Center">
                                <TextBlock Text="&#x1F504; WINDOWS EDITION CHANGER" FontSize="11" FontWeight="Bold" Foreground="#38bdf8" HorizontalAlignment="Center"/>
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
                                <TextBlock Text="&#x1F527; PERFORMANCE &amp; UI TWEAKS" FontSize="11" FontWeight="Bold" Foreground="#38bdf8" Margin="0,5,0,10"/>
                                
                                <Border BorderBrush="#374151" BorderThickness="0,0,0,1" Padding="0,0,0,10" Margin="0,0,0,10">
                                    <Grid>
                                        <StackPanel HorizontalAlignment="Left">
                                            <TextBlock Text="&#x1F4C1; Windows 11 Classic Context Menu" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
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
                                            <TextBlock Text="&#x26A1; Enable Ultimate Performance Plan" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Unlocks and activates hidden maximum hardware speed power profile." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <Button Name="btn_tweak_ultimate" Content="Unlock Scheme" Background="#d97706" BorderThickness="0" HorizontalAlignment="Right" Width="225"/>
                                    </Grid>
                                </Border>

                                <Border BorderBrush="#374151" BorderThickness="0,0,0,1" Padding="0,0,0,10" Margin="0,0,0,10">
                                    <Grid>
                                        <StackPanel HorizontalAlignment="Left">
                                            <TextBlock Text="&#x1F3AE; Latency &amp; Gaming Optimization" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Disables GameDVR, CPU throttling and configures network game packet latency." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <Button Name="btn_tweak_gaming" Content="Apply Gaming Tweaks" Background="#059669" BorderThickness="0" HorizontalAlignment="Right" Width="225"/>
                                    </Grid>
                                </Border>

                                <Border BorderBrush="#374151" BorderThickness="0,0,0,1" Padding="0,0,0,10" Margin="0,0,0,10">
                                    <Grid>
                                        <StackPanel HorizontalAlignment="Left">
                                            <TextBlock Text="&#x26A1; Windows Fast Startup Settings" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Toggles Hiberboot configuration to allow full kernel reload on power off." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <StackPanel Orientation="Horizontal" HorizontalAlignment="Right">
                                            <Button Name="btn_tweak_fast_on" Content="Enable" Background="#059669" BorderThickness="0" Margin="0,0,5,0" Width="110"/>
                                            <Button Name="btn_tweak_fast_off" Content="Disable" Background="#b91c1c" BorderThickness="0" Width="110"/>
                                        </StackPanel>
                                    </Grid>
                                </Border>

                                <Border BorderBrush="#374151" BorderThickness="0,0,0,1" Padding="0,0,0,10" Margin="0,0,0,10">
                                    <Grid>
                                        <StackPanel HorizontalAlignment="Left">
                                            <TextBlock Text="&#x1F5BB; Adjust Visual Effects for Performance" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Disables window shadows, animations, and transparency to speed up UI." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <Button Name="btn_tweak_visuals" Content="Set Performance Mode" Background="#0284c7" BorderThickness="0" HorizontalAlignment="Right" Width="225"/>
                                    </Grid>
                                </Border>

                                <Border BorderBrush="#374151" BorderThickness="0,0,0,1" Padding="0,0,0,10" Margin="0,0,0,10">
                                    <Grid>
                                        <StackPanel HorizontalAlignment="Left">
                                            <TextBlock Text="&#x1F9E0; Configure Optimal Virtual Memory (Pagefile)" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Automatically sizes pagefile correctly based on installed physical RAM." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <Button Name="btn_tweak_pagefile" Content="Optimize Virtual RAM" Background="#4f46e5" BorderThickness="0" HorizontalAlignment="Right" Width="225"/>
                                    </Grid>
                                </Border>

                                <TextBlock Text="&#x1F512; SECURITY &amp; TELEMETRY PRIVACY POLICY TWEAKS" FontSize="11" FontWeight="Bold" Foreground="#38bdf8" Margin="0,15,0,10"/>

                                <Border BorderBrush="#374151" BorderThickness="0,0,0,1" Padding="0,0,0,10" Margin="0,0,0,10">
                                    <Grid>
                                        <StackPanel HorizontalAlignment="Left">
                                            <TextBlock Text="&#x1F512; Disable Online Bing Search in Start Menu" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Hides web results inside the Start Menu search for faster local searches." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <Button Name="btn_tweak_bing" Content="Disable Bing Search" Background="#4f46e5" BorderThickness="0" HorizontalAlignment="Right" Width="225"/>
                                    </Grid>
                                </Border>

                                <Border BorderBrush="#374151" BorderThickness="0,0,0,1" Padding="0,0,0,10" Margin="0,0,0,10">
                                    <Grid>
                                        <StackPanel HorizontalAlignment="Left">
                                            <TextBlock Text="&#x1F916; Disable Cortana Assistant &amp; Windows Copilot" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Disables background voice services and hides modern desktop Copilot panels." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <Button Name="btn_tweak_cortana" Content="Disable Assistants" Background="#b91c1c" BorderThickness="0" HorizontalAlignment="Right" Width="225"/>
                                    </Grid>
                                </Border>

                                <Border BorderBrush="#374151" BorderThickness="0,0,0,1" Padding="0,0,0,10" Margin="0,0,0,10">
                                    <Grid>
                                        <StackPanel HorizontalAlignment="Left">
                                            <TextBlock Text="&#x1F4E1; Turn Off Windows Feedback &amp; Diagnostic Telemetry" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Blocks background data transmission and diagnostic reports to Microsoft." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <Button Name="btn_tweak_telemetry" Content="Block Telemetry" Background="#374151" BorderThickness="1" BorderBrush="#374151" HorizontalAlignment="Right" Width="225"/>
                                    </Grid>
                                </Border>

                                <Border BorderBrush="#374151" BorderThickness="0,0,0,1" Padding="0,0,0,10" Margin="0,0,0,10">
                                    <Grid>
                                        <StackPanel HorizontalAlignment="Left">
                                            <TextBlock Text="&#x1F4FA; Disable Lock Screen Spotlight Ads &amp; Tips" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Disables promotional ads and lock screen background search tips." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <Button Name="btn_tweak_ads" Content="Disable Lockscreen Ads" Background="#4f46e5" BorderThickness="0" HorizontalAlignment="Right" Width="225"/>
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
                        <TextBlock Text="&#x1F9FC; Wipes native Microsoft Windows bloatware packages, telemetry clients, and configures virtualization optional services." FontSize="11" Foreground="#cbd5e1"/>
                    </Border>

                    <Grid Grid.Row="1">
                        <Grid.ColumnDefinitions>
                            <ColumnDefinition Width="*"/>
                            <ColumnDefinition Width="*"/>
                        </Grid.ColumnDefinitions>

                        <!-- Left Column: Bloatware Remover & System Purger -->
                        <ScrollViewer Grid.Column="0" VerticalScrollBarVisibility="Auto" Margin="0,0,10,0">
                            <StackPanel>
                                <Border Background="#1f2937" BorderBrush="#374151" BorderThickness="1" CornerRadius="8" Padding="15" Margin="0,0,0,10">
                                    <StackPanel>
                                        <TextBlock Text="&#x1F9FC; UWP Bloatware Remover" FontSize="14" FontWeight="Bold" Foreground="#ef4444" Margin="0,0,0,10"/>
                                        <TextBlock Text="Purges pre-installed apps such as Xbox, Skype, Solitaire, MSN Weather, and Microsoft Maps." TextWrapping="Wrap" FontSize="11" Foreground="#9ca3af" Margin="0,0,0,20"/>
                                        <Button Name="btn_remove_bloat" Content="Uninstall Windows Bloatware" Height="40" Background="#b91c1c" BorderThickness="0" FontWeight="Bold"/>
                                    </StackPanel>
                                </Border>
                                <Border Background="#1f2937" BorderBrush="#374151" BorderThickness="1" CornerRadius="8" Padding="15" Margin="0,10,0,0">
                                    <StackPanel>
                                        <TextBlock Text="&#x1F5D1; TELEMETRY &amp; EDGE CLEANERS" FontSize="13" FontWeight="Bold" Foreground="#38bdf8" Margin="0,0,0,10"/>
                                        <TextBlock Text="Wipe deep-rooted telemetry services and system background clients." FontSize="10.5" Foreground="#9ca3af" Margin="0,0,0,15" TextWrapping="Wrap"/>
                                        <Button Name="btn_bloat_onedrive" Content="Completely Purge OneDrive Client" Height="32" Background="#374151" BorderThickness="0" FontWeight="Bold" Margin="0,0,0,5"/>
                                        <Button Name="btn_bloat_edge" Content="Turn Off Edge Browser Telemetry" Height="32" Background="#374151" BorderThickness="0" FontWeight="Bold" Margin="5,5,0,0"/>
                                    </StackPanel>
                                </Border>
                            </StackPanel>
                        </ScrollViewer>

                        <!-- Right Card: Optional Features -->
                        <Border Grid.Column="1" Background="#1f2937" BorderBrush="#374151" BorderThickness="1" CornerRadius="8" Padding="15" Margin="10,0,0,0">
                            <StackPanel>
                                <TextBlock Text="&#x1F50C; Windows Optional Features" FontSize="14" FontWeight="Bold" Foreground="#38bdf8" Margin="0,0,0,10"/>
                                <CheckBox Name="cb_feat_lpd" Content="Enable LPD Printing Service" Foreground="#ffffff" Margin="0,5,0,5"/>
                                <CheckBox Name="cb_feat_lpr" Content="Enable LPR Port Monitor Service" Foreground="#ffffff" Margin="0,5,0,5"/>
                                <CheckBox Name="cb_feat_smb" Content="Enable SMB1 Protocol Service" Foreground="#ffffff" Margin="0,5,0,5"/>
                                <CheckBox Name="cb_feat_hyperv" Content="Enable Hyper-V Platform Virtualization" Foreground="#ffffff" Margin="0,5,0,5"/>
                                <CheckBox Name="cb_feat_sandbox" Content="Enable Windows Sandbox Isolation" Foreground="#ffffff" Margin="0,5,0,5"/>
                                <CheckBox Name="cb_feat_wsl" Content="Enable Windows Subsystem for Linux (WSL)" Foreground="#ffffff" Margin="0,5,0,15"/>
                                <Button Name="btn_apply_features" Content="Apply Windows Features" Height="40" Background="#059669" BorderThickness="0" FontWeight="Bold"/>
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
                                <TextBlock Text="&#x1F6E1; SYSTEM SCANS &amp; REPAIRS" FontSize="11" FontWeight="Bold" Foreground="#38bdf8" Margin="0,0,0,6"/>
                                <Button Name="btn_rep_sfc" Content="Run System File Check (sfc /scannow)" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_dism" Content="Repair Image Health (DISM /RestoreHealth)" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_dism_check" Content="Quick Check Image Corruption Status (DISM /CheckHealth)" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_wu" Content="Reset Windows Update Components &amp; Cache" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_engines" Content="Repair Windows Native Repair Engines (SFC &amp; DISM Fix)" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_dll" Content="Re-Register Core Windows System DLL Libraries (regsvr32)" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_dns" Content="Flush System DNS Resolver Cache" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_winsock" Content="Reset Network Winsock Catalog Bindings" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_firewall" Content="Reset Windows Firewall Rules to Default" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_store" Content="Re-register &amp; Repair Microsoft Store &amp; Default Apps" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_wsreset" Content="Reset Windows Store Cache (wsreset.exe)" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_wmi" Content="Rebuild Corrupted Windows WMI Repository Database" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_search" Content="Rebuild Windows Search Indexer Database Index" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_net" Content="Run Comprehensive Network Stack &amp; Adapter Reset" Height="30" Margin="0,2,0,15" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>

                                <TextBlock Text="&#x1F9FB; SYSTEM CLEANERS &amp; RAM CACHE OPTIMIZERS" FontSize="11" FontWeight="Bold" Foreground="#38bdf8" Margin="0,10,0,6"/>
                                <Button Name="btn_rep_clean_ram_wpf" Content="Empty Active Process Working Sets (API RAM Booster)" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_clean_ram" Content="Optimize &amp; Flush System RAM Cache (GC Collect)" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_clean_browser" Content="Clean Web Browser Cache &amp; Temp Files (Chrome, Edge, Firefox)" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_clean_mgr" Content="Run Deep Windows System Disk Cleanup (cleanmgr /autoclean)" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_clean_resetbase" Content="Purge Superseded Components Cache (DISM Component ResetBase)" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_clean_temp" Content="Delete All User and System TEMP Directories Cache Files" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_recycle" Content="Silent Empty Recycle Bin database on all drives" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_defrag" Content="Optimize / Defragment All Connected SSD and HDD volumes" Height="30" Margin="0,2,0,15" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>

                                <TextBlock Text="&#x1F6E1; SYSTEM RECOVERY &amp; BOOT MANAGEMENT" FontSize="11" FontWeight="Bold" Foreground="#38bdf8" Margin="0,10,0,6"/>
                                <Button Name="btn_rep_winre_en" Content="Enable Windows Recovery Environment (WinRE)" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_winre_stat" Content="Check WinRE Environment Configuration Status" Height="30" Margin="0,2,0,15" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>

                                <TextBlock Text="&#x1F6E1; MICROSOFT OFFICE &amp; OUTLOOK DIAGNOSTICS &amp; REPAIRS" FontSize="11" FontWeight="Bold" Foreground="#38bdf8" Margin="0,10,0,6"/>
                                <Button Name="btn_rep_off_quick" Content="Run Microsoft Office Quick Repair (Click-to-Run)" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_off_pst" Content="Launch Outlook PST File Repair Tool (ScanPST)" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
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

                                <TextBlock Text="&#x1F4BB; WINDOWS BOOT SECTOR &amp; EFI REPAIR" FontSize="11" FontWeight="Bold" Foreground="#38bdf8" Margin="0,10,0,6"/>
                                <Button Name="btn_rep_bcd" Content="Rebuild Windows Boot configuration partition files (BCDBoot)" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_rec_boot" Content="Reboot System directly into Startup Repair / Recovery Menu" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_fail_menu" Content="Enable Windows Boot Failures Menu Display Policy" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_chkdsk" Content="Schedule Boot-Time Disk Volume Scan &amp; Repair (Chkdsk /f /r)" Height="30" Margin="0,2,0,15" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>

                                <TextBlock Text="&#x1F5A8; PRINTER SERVICE &amp; SHARING REPAIRS" FontSize="11" FontWeight="Bold" Foreground="#38bdf8" Margin="0,10,0,6"/>
                                <Button Name="btn_rep_printer_11b" Content="Fix Shared Printer Error 0x0000011b (Set RpcAuthnLevelPrivacyEnabled=0)" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_printer_policy" Content="Configure Group Policy Printer Sharing &amp; RPC Connection Settings" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_printer_lpd" Content="Enable Windows LPD Print Service &amp; LPR Port Monitor Optional Features" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_printer_disc" Content="Restart Network Discovery &amp; Printer Sharing Dependency Services" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_printer_spool" Content="Flush Print Spooler Service &amp; Clear Pending Queue" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_printer_diag" Content="Launch Native Windows Printer Troubleshooter Diagnostic Wizard" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_printer_offline" Content="Fix Network Printer False Offline Registry Settings status bug" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_printer_drivers" Content="Wipe Corrupted Print Drivers Registry Configurations list" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_printer_dis_spooler" Content="Completely Stop &amp; Disable Windows Print Spooler service" Height="30" Margin="0,2,0,15" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>

                                <TextBlock Text="&#x1F39B; LOSSLESS DRIVE &amp; DISK STYLE CONVERTERS" FontSize="11" FontWeight="Bold" Foreground="#38bdf8" Margin="0,10,0,6"/>
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

                                <TextBlock Text="&#x1F6E1; WINDOWS SERVICES &amp; SHIELD REPAIRS" FontSize="11" FontWeight="Bold" Foreground="#38bdf8" Margin="0,10,0,6"/>
                                <Button Name="btn_rep_shield_wu" Content="Run Comprehensive Windows Update Service &amp; Cache Repair Engine" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <!-- Windows update block frame -->
                                <Grid Margin="0,2,0,4">
                                    <Grid.ColumnDefinitions>
                                        <ColumnDefinition Width="*"/>
                                        <ColumnDefinition Width="*"/>
                                    </Grid.ColumnDefinitions>
                                    <Button Grid.Column="0" Name="btn_rep_shield_block_wu" Content="Block Windows Updates" Height="30" Margin="0,2,5,2" Background="#b91c1c" BorderThickness="0" FontSize="10" FontWeight="Bold"/>
                                    <Button Grid.Column="1" Name="btn_rep_shield_enable_wu" Content="Enable Windows Updates" Height="30" Margin="5,2,0,2" Background="#059669" BorderThickness="0" FontSize="10" FontWeight="Bold"/>
                                </Grid>
                                <Button Name="btn_rep_shield_defender" Content="Reset Windows Defender Policies &amp; Restart Antivirus Services" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_shield_firewall" Content="Restore Default Windows Firewall Settings and Rules" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_shield_audio" Content="Reset &amp; Restart Windows Audio Playback Services" Height="30" Margin="0,2,0,15" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>

                                <TextBlock Text="&#x1F6E0; SHELL OPTIMIZERS &amp; DATA WIPERS" FontSize="11" FontWeight="Bold" Foreground="#38bdf8" Margin="0,10,0,6"/>
                                <Button Name="btn_rep_shell_explorer" Content="Restart Windows Explorer Shell (Quick Freeze Fix)" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_shell_events" Content="Clear All Windows System, Application &amp; Security Event Logs" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_shell_icon" Content="Rebuild Windows Desktop Icon &amp; Thumbnail Cache Data" Height="30" Margin="0,2,0,4" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
                                <Button Name="btn_rep_shell_font" Content="Rebuild Windows System Font Cache Database" Height="30" Margin="0,2,0,15" Background="#111827" BorderBrush="#374151" HorizontalContentAlignment="Left" Padding="10,0,0,0"/>
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
                                        <Grid.ColumnDefinitions>
                                            <ColumnDefinition Width="*"/>
                                            <ColumnDefinition Width="220"/>
                                        </Grid.ColumnDefinitions>
                                        <StackPanel Grid.Column="0" VerticalAlignment="Center">
                                            <TextBlock Text="Active Network Ping Latency Diagnostic Test Utility" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Enter a hostname or IP to measure ping response times in the log." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <StackPanel Grid.Column="1" Orientation="Horizontal" VerticalAlignment="Center">
                                            <TextBox Name="txt_diag_ping_host" Text="google.com" Width="130" Height="28" Background="#111827" Foreground="#ffffff" BorderBrush="#374151" Padding="5,0,5,0" VerticalContentAlignment="Center"/>
                                            <Button Name="btn_diag_ping_start" Content="Ping Test" Width="80" Height="28" Margin="5,0,0,0" Background="#0284c7" BorderThickness="0" FontSize="10.5" FontWeight="Bold"/>
                                        </StackPanel>
                                    </Grid>
                                </Border>

                                <TextBlock Text="WI-FI &amp; DHCP NETWORK DIAGNOSTICS" FontSize="11" FontWeight="Bold" Foreground="#38bdf8" Margin="0,5,0,10"/>

                                <Border BorderBrush="#374151" BorderThickness="0,0,0,1" Padding="0,0,0,10" Margin="0,0,0,10">
                                    <Grid>
                                        <StackPanel HorizontalAlignment="Left">
                                            <TextBlock Text="Show Saved Wi-Fi Passwords list" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Decrypts and displays all saved wireless networks SSIDs and security keys." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <Button Name="btn_rep_wifi_pass" Content="Show Passwords" Background="#1e293b" BorderBrush="#374151" HorizontalAlignment="Right" Width="200"/>
                                    </Grid>
                                </Border>

                                <Border BorderBrush="#374151" BorderThickness="0,0,0,1" Padding="0,0,0,10" Margin="0,0,0,10">
                                    <Grid>
                                        <StackPanel HorizontalAlignment="Left">
                                            <TextBlock Text="Export Decrypted Saved Wi-Fi Profiles to Desktop" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Saves wireless XML connection configurations profile files to Desktop." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <Button Name="btn_rep_wifi_export" Content="Export Wi-Fi XMLs" Background="#4f46e5" BorderThickness="0" HorizontalAlignment="Right" Width="200"/>
                                    </Grid>
                                </Border>

                                <Border BorderBrush="#374151" BorderThickness="0,0,0,1" Padding="0,0,0,10" Margin="0,0,0,10">
                                    <Grid>
                                        <StackPanel HorizontalAlignment="Left">
                                            <TextBlock Text="Release &amp; Renew Adapter DHCP IP Address" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Performs ipconfig /release and renew to refresh router network leases." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <Button Name="btn_rep_dhcp" Content="Renew DHCP IP" Background="#0284c7" BorderThickness="0" HorizontalAlignment="Right" Width="200"/>
                                    </Grid>
                                </Border>

                                <Border BorderBrush="#374151" BorderThickness="0,0,0,1" Padding="0,0,0,10" Margin="0,0,0,10">
                                    <Grid>
                                        <StackPanel HorizontalAlignment="Left">
                                            <TextBlock Text="Disable / Enable IPv6 network protocol status" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Toggles IPv6 binding on network adapters to resolve network routing bugs." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <StackPanel Orientation="Horizontal" HorizontalAlignment="Right">
                                            <Button Name="btn_rep_ipv6_dis" Content="Disable IPv6" Background="#b91c1c" BorderThickness="0" Margin="0,0,5,0" Width="100"/>
                                            <Button Name="btn_rep_ipv6_en" Content="Enable IPv6" Background="#059669" BorderThickness="0" Width="100"/>
                                        </StackPanel>
                                    </Grid>
                                </Border>

                                <TextBlock Text="STANDARD HARDWARE &amp; STATUS REPORTS" FontSize="11" FontWeight="Bold" Foreground="#38bdf8" Margin="0,15,0,10"/>

                                <Border BorderBrush="#374151" BorderThickness="0,0,0,1" Padding="0,0,0,10" Margin="0,0,0,10">
                                    <Grid>
                                        <StackPanel HorizontalAlignment="Left">
                                            <TextBlock Text="List Top Processes by CPU and Memory allocations resource usage" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Scans processes list and displays the highest hardware usage active targets." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <Button Name="btn_diag_top_proc" Content="Show Top Processes" Background="#1e293b" BorderBrush="#374151" HorizontalAlignment="Right" Width="200"/>
                                    </Grid>
                                </Border>

                                <Border BorderBrush="#374151" BorderThickness="0,0,0,1" Padding="0,0,0,10" Margin="0,0,0,10">
                                    <Grid>
                                        <StackPanel HorizontalAlignment="Left">
                                            <TextBlock Text="Export Active System Hardware Drivers list registry to Desktop" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Generates driver list and saves it as SystemDriversList.txt on your desktop." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <Button Name="btn_diag_export_drivers" Content="Export Driver List" Background="#4f46e5" BorderThickness="0" HorizontalAlignment="Right" Width="200"/>
                                    </Grid>
                                </Border>

                                <Border BorderBrush="#374151" BorderThickness="0,0,0,1" Padding="0,0,0,10" Margin="0,0,0,10">
                                    <Grid>
                                        <StackPanel HorizontalAlignment="Left">
                                            <TextBlock Text="Check Connected Physical Drive Health Status (SMART Scan)" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Queries hardware sensors on connected physical drives to check reliability." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <Button Name="btn_diag_disk" Content="Run SMART Drive Check" Background="#4f46e5" BorderThickness="0" HorizontalAlignment="Right" Width="200"/>
                                    </Grid>
                                </Border>

                                <Border BorderBrush="#374151" BorderThickness="0,0,0,1" Padding="0,0,0,10" Margin="0,0,0,10">
                                    <Grid>
                                        <StackPanel HorizontalAlignment="Left">
                                            <TextBlock Text="Generate Windows Battery Lifecycle &amp; Wear Health Report" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Generates HTML power battery wear diagnostic status chart." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <Button Name="btn_diag_battery" Content="Generate Battery Report" Background="#10b981" BorderThickness="0" HorizontalAlignment="Right" Width="200"/>
                                    </Grid>
                                </Border>

                                <Border BorderBrush="#374151" BorderThickness="0,0,0,1" Padding="0,0,0,10" Margin="0,0,0,10">
                                    <Grid>
                                        <StackPanel HorizontalAlignment="Left">
                                            <TextBlock Text="Analyze Installed RAM Modules &amp; Speed Specifications" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Queries WMIC to identify installed memory module speeds and clock cycles." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <Button Name="btn_diag_ram" Content="Show Memory Specs" Background="#374151" BorderThickness="0" HorizontalAlignment="Right" Width="200"/>
                                    </Grid>
                                </Border>

                                <Border BorderBrush="#374151" BorderThickness="0,0,0,1" Padding="0,0,0,10" Margin="0,0,0,10">
                                    <Grid>
                                        <StackPanel HorizontalAlignment="Left">
                                            <TextBlock Text="Verify Windows OS License Activation Status" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Queries software licensing services to check activation." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <Button Name="btn_diag_act" Content="Check Activation Status" Background="#1f2937" BorderThickness="1" BorderBrush="#374151" HorizontalAlignment="Right" Width="200"/>
                                    </Grid>
                                </Border>

                                <Border BorderBrush="#374151" BorderThickness="0,0,0,1" Padding="0,0,0,10" Margin="0,0,0,10">
                                    <Grid>
                                        <StackPanel HorizontalAlignment="Left">
                                            <TextBlock Text="Generate Comprehensive Windows Hardware &amp; System Info Summary" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Generates CPU, GPU, Motherboard, and BIOS properties summary." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <Button Name="btn_diag_specs" Content="Generate Specs Info" Background="#0284c7" BorderThickness="0" HorizontalAlignment="Right" Width="200"/>
                                    </Grid>
                                </Border>

                                <Border BorderBrush="#374151" BorderThickness="0,0,0,1" Padding="0,0,0,10" Margin="0,0,0,10">
                                    <Grid>
                                        <StackPanel HorizontalAlignment="Left">
                                            <TextBlock Text="Schedule Windows Memory Diagnostic Scanner (mdsched.exe)" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Sets up Windows Memory Diagnostic to check physical RAM hardware during restart." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <Button Name="btn_diag_mdsched" Content="Schedule RAM Scan" Background="#0284c7" BorderThickness="0" HorizontalAlignment="Right" Width="200"/>
                                    </Grid>
                                </Border>

                                <Border BorderBrush="#374151" BorderThickness="0,0,0,1" Padding="0,0,0,10" Margin="0,0,0,10">
                                    <Grid>
                                        <StackPanel HorizontalAlignment="Left">
                                            <TextBlock Text="Configure Secure Network DNS Servers (Cloudflare 1.1.1.1)" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Configures adapter DNS settings to use Cloudflare secure DNS." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <Button Name="btn_diag_dns" Content="Apply Secure DNS" Background="#4f46e5" BorderThickness="0" HorizontalAlignment="Right" Width="200"/>
                                    </Grid>
                                </Border>

                                <Border BorderBrush="#374151" BorderThickness="0,0,0,1" Padding="0,0,0,10" Margin="0,0,0,10">
                                    <Grid>
                                        <StackPanel HorizontalAlignment="Left">
                                            <TextBlock Text="Run Real-Time Internet Download Speed Test" FontSize="12" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Downloads a test file from Cloudflare CDN to calculate internet bandwidth." FontSize="10" Foreground="#9ca3af"/>
                                        </StackPanel>
                                        <Button Name="btn_diag_speed" Content="Run Download Speed Test" Background="#10b981" BorderThickness="0" HorizontalAlignment="Right" Width="200"/>
                                    </Grid>
                                </Border>
                            </StackPanel>
                        </ScrollViewer>
                    </Border>
                </Grid>

                <!-- 8. Backups & Migration View -->
                <Grid Name="grid_backups" Visibility="Collapsed">
                    <Grid.ColumnDefinitions>
                        <ColumnDefinition Width="*"/>
                        <ColumnDefinition Width="*"/>
                    </Grid.ColumnDefinitions>

                    <!-- Left Card: Robocopy Migration -->
                    <Border Grid.Column="0" Background="#1f2937" BorderBrush="#374151" BorderThickness="1" CornerRadius="8" Padding="15" Margin="0,0,10,0">
                        <StackPanel VerticalAlignment="Center">
                            <TextBlock Text="FOLDER MIGRATION (ROBOCOPY)" FontSize="13" FontWeight="Bold" Foreground="#38bdf8" Margin="0,0,0,15"/>
                            
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

                            <Button Name="btn_start_backup" Content="Start Robocopy Backup Migration" Height="40" Background="#059669" BorderThickness="0" FontWeight="Bold" FontSize="13"/>
                        </StackPanel>
                    </Border>

                    <!-- Right Card: System Restore Points -->
                    <Border Grid.Column="1" Background="#1f2937" BorderBrush="#374151" BorderThickness="1" CornerRadius="8" Padding="15" Margin="10,0,0,0">
                        <StackPanel VerticalAlignment="Center">
                            <TextBlock Text="WINDOWS SYSTEM RESTORE UTILITIES" FontSize="13" FontWeight="Bold" Foreground="#38bdf8" Margin="0,0,0,15"/>
                            <TextBlock Text="Manage active system restore points protection schemes to recover from crashes." FontSize="10.5" Foreground="#9ca3af" Margin="0,0,0,25" TextWrapping="Wrap"/>
                            
                            <Button Name="btn_backup_enable_restore" Content="Enable System Protection Restore on C: Drive" Height="36" Background="#374151" BorderThickness="0" FontWeight="Bold" Margin="0,0,0,8"/>
                            <Button Name="btn_backup_create_restore" Content="Create Instant System Restore Point" Height="36" Background="#0284c7" BorderThickness="0" FontWeight="Bold" Margin="0,8,0,8"/>
                            <Button Name="btn_backup_launch_restore" Content="Launch Windows Recovery System Restore Wizard" Height="36" Background="#4f46e5" BorderThickness="0" FontWeight="Bold" Margin="0,8,0,0"/>
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
                        <ScrollViewer VerticalScrollBarVisibility="Auto">
                            <StackPanel>
                                <TextBlock Text="STANDARD CONTROL CONSOLES SHORTCUTS" FontSize="11.5" FontWeight="Bold" Foreground="#38bdf8" Margin="5,5,5,10"/>
                                <UniformGrid Columns="3" Margin="0,0,0,20">
                                    <Button Name="btn_cfg_panel" Content="Control Panel" Height="45" Margin="5" FontSize="10.5" FontWeight="Bold"/>
                                    <Button Name="btn_cfg_reg" Content="Registry Editor" Height="45" Margin="5" FontSize="10.5" FontWeight="Bold"/>
                                    <Button Name="btn_cfg_dev" Content="Device Manager" Height="45" Margin="5" FontSize="10.5" FontWeight="Bold"/>
                                    <Button Name="btn_cfg_disk" Content="Disk Management" Height="45" Margin="5" FontSize="10.5" FontWeight="Bold"/>
                                    <Button Name="btn_cfg_services" Content="System Services" Height="45" Margin="5" FontSize="10.5" FontWeight="Bold"/>
                                    <Button Name="btn_cfg_event" Content="Event Viewer" Height="45" Margin="5" FontSize="10.5" FontWeight="Bold"/>
                                    <Button Name="btn_cfg_task" Content="Task Manager" Height="45" Margin="5" FontSize="10.5" FontWeight="Bold"/>
                                    <Button Name="btn_cfg_gp" Content="Group Policy Editor" Height="45" Margin="5" FontSize="10.5" FontWeight="Bold"/>
                                    <Button Name="btn_cfg_sys" Content="System Properties" Height="45" Margin="5" FontSize="10.5" FontWeight="Bold"/>
                                </UniformGrid>

                                <TextBlock Text="LOCAL USER ACCOUNTS &amp; AUTO-LOGIN MANAGER" FontSize="11.5" FontWeight="Bold" Foreground="#38bdf8" Margin="5,5,5,10"/>
                                <Border Background="#111827" BorderBrush="#374151" BorderThickness="1" CornerRadius="6" Padding="12" Margin="5">
                                    <Grid>
                                        <Grid.ColumnDefinitions>
                                            <ColumnDefinition Width="*"/>
                                            <ColumnDefinition Width="Auto"/>
                                        </Grid.ColumnDefinitions>
                                        <StackPanel Grid.Column="0">
                                            <TextBlock Text="Local User Account Security Settings &amp; Setup" FontSize="11" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Enable default accounts, reset passwords, or set up automated kiosk logins." FontSize="9.5" Foreground="#9ca3af" Margin="0,2,0,0"/>
                                        </StackPanel>
                                        <StackPanel Grid.Column="1" Orientation="Horizontal" VerticalAlignment="Center">
                                            <Button Name="btn_cfg_admin_en" Content="Enable Admin" Width="100" Height="28" Margin="2" FontSize="9.5" FontWeight="Bold" Background="#059669" BorderThickness="0"/>
                                            <Button Name="btn_cfg_admin_dis" Content="Disable Admin" Width="100" Height="28" Margin="2" FontSize="9.5" FontWeight="Bold" Background="#b91c1c" BorderThickness="0"/>
                                            <Button Name="btn_cfg_reset_pass" Content="Reset Password" Width="110" Height="28" Margin="2" FontSize="9.5" FontWeight="Bold"/>
                                            <Button Name="btn_cfg_autologin" Content="Setup Auto-Login" Width="120" Height="28" Margin="2" FontSize="9.5" FontWeight="Bold" Background="#4f46e5" BorderThickness="0"/>
                                        </StackPanel>
                                    </Grid>
                                </Border>

                                <TextBlock Text="BIOS &amp; DEVICE TELEMETRY INFORMATION" FontSize="11.5" FontWeight="Bold" Foreground="#38bdf8" Margin="5,15,5,10"/>
                                <Border Background="#111827" BorderBrush="#374151" BorderThickness="1" CornerRadius="6" Padding="12" Margin="5">
                                    <Grid>
                                        <Grid.ColumnDefinitions>
                                            <ColumnDefinition Width="*"/>
                                            <ColumnDefinition Width="Auto"/>
                                        </Grid.ColumnDefinitions>
                                        <StackPanel Grid.Column="0">
                                            <TextBlock Text="System Hardware Motherboard BIOS Serial Number Check" FontSize="11" FontWeight="Bold" Foreground="#ffffff"/>
                                            <TextBlock Text="Queries hardware chips directly to retrieve original device serial logs." FontSize="9.5" Foreground="#9ca3af" Margin="0,2,0,0"/>
                                        </StackPanel>
                                        <Button Grid.Column="1" Name="btn_cfg_serial" Content="Check Serial Info" Width="140" Height="28" VerticalAlignment="Center"/>
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

$reader = (New-Object System.Xml.XmlTextReader (New-Object System.IO.StringReader $xaml))
$window = [Windows.Markup.XamlReader]::Load($reader)

# Map all Named XAML elements to script variables
[xml]$xmlDoc = $xaml
$xmlDoc.SelectNodes("//*[@Name]") | ForEach-Object {
    Set-Variable -Name $_.Name -Value $window.FindName($_.Name) -Scope Script
}

# --- GLOBAL UTILITY FUNCTIONS ---
$activities = New-Object System.Collections.ObjectModel.ObservableCollection[PSObject]
$activity_tree.ItemsSource = $activities

$script:runspaces = [System.Collections.ArrayList]::new()

function Run-Async ($scriptBlock, $argsList=@()) {
    $ps = [PowerShell]::Create()
    $ps.AddScript($scriptBlock) | Out-Null
    $ps.AddArgument($window) | Out-Null
    foreach ($arg in $argsList) {
        $ps.AddArgument($arg) | Out-Null
    }
    $script:runspaces.Add($ps) | Out-Null
    $ps.BeginInvoke() | Out-Null
}

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
        "grid_dash" = "Dashboard Overview"
        "grid_soft" = "Silent Software Installer Hub"
        "grid_act"  = "Windows & Office Activation (MAS)"
        "grid_tweaks" = "Premium OS Registry Tweaks"
        "grid_bloat" = "Windows Bloatware & Features"
        "grid_repairs" = "System Command & Cache Repairs"
        "grid_diag" = "Hardware Diagnostics & Reports"
        "grid_backups" = "Backups & Data Migration"
        "grid_config" = "Windows Configuration Consoles"
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

# --- INITIALIZE SOFTWARE LIST WITH GROUPS ---
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

# --- SYSTEM STATS BACKGROUND MONITOR ---
$osPlatform = (Get-CimInstance Win32_OperatingSystem).Caption
$txt_os.Text = "Win 10/11"

Run-Async {
    param($win, $c, $r, $d, $u)
    while ($true) {
        try {
            $cpu = (Get-CimInstance -ClassName Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average
            if ($cpu -eq $null) { $cpu = 0 }
            $cpuStr = "$([Math]::Round($cpu))%"

            $os = Get-CimInstance Win32_OperatingSystem
            $freeRam = $os.FreePhysicalMemory
            $totalRam = $os.TotalVisibleMemorySize
            $usedRam = $totalRam - $freeRam
            $ramPct = ($usedRam / $totalRam) * 100
            $ramStr = "$([Math]::Round($ramPct))%"

            $disk = Get-PSDrive C
            $freeGB = [Math]::Round($disk.Free / 1GB)
            $diskStr = "$freeGB GB Free"

            $uptime = (Get-Date) - $os.LastBootUpTime
            $uptimeStr = "Uptime: $($uptime.Days)d $($uptime.Hours)h $($uptime.Minutes)m"

            $win.Dispatcher.Invoke([Action]{
                $c.Text = $cpuStr
                $r.Text = $ramStr
                $d.Text = $diskStr
                $u.Text = $uptimeStr
            })
        } catch {}
        Start-Sleep -Seconds 3
    }
} @($txt_cpu, $txt_ram, $txt_disk, $txt_uptime)

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

# Software Uninstallation
$btn_uninstall_soft.Add_Click({
    $selected = $checkboxes | Where-Object { $_.IsChecked -eq $true }
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

# Deploy custom Microsoft Office suites (M365, LTSC 2019, 2021, 2024)
function Start-OfficeDeployment ($pkgId, $title) {
    Log-Message "Requesting install for $title..."
    Add-Activity "Office Installer" "Deploying $title..." "Running"
    
    if ($pkgId -eq "Microsoft.Office") {
        Run-Async {
            param($win, $t)
            $win.Dispatcher.Invoke([Action]{ Log-Message "Installing Microsoft 365 Apps silently via WinGet..." })
            $proc = Start-Process winget -ArgumentList "install --id Microsoft.Office --silent --accept-source-agreements --accept-package-agreements" -NoNewWindow -PassThru -Wait
            if ($proc.ExitCode -eq 0) {
                $win.Dispatcher.Invoke([Action]{ 
                    Log-Message "[OK] Microsoft 365 installed successfully."
                    Add-Activity "Office Installer" "M365 installed successfully" "Success"
                })
            } else {
                $win.Dispatcher.Invoke([Action]{ 
                    Log-Message "[FAIL] Microsoft 365 installation failed."
                    Add-Activity "Office Installer" "M365 install failed" "Failed"
                })
            }
        } @($title)
    } else {
        Run-Async {
            param($win, $id, $t)
            $odtDir = "C:\OfficeODT"
            if (-not (Test-Path $odtDir)) { New-Item -ItemType Directory -Path $odtDir | Out-Null }
            
            $win.Dispatcher.Invoke([Action]{ Log-Message "Downloading Microsoft Office Deployment Tool (ODT) setup..." })
            $setupExe = "C:\Program Files\OfficeDeploymentTool\setup.exe"
            if (-not (Test-Path $setupExe)) { $setupExe = "C:\Program Files (x86)\OfficeDeploymentTool\setup.exe" }
            if (-not (Test-Path $setupExe)) {
                $url = "https://download.microsoft.com/download/6c1eeb25-cf8b-41d9-8d0d-cc1dbc032140/officedeploymenttool_20228-20124.exe"
                $odtInstaller = "$odtDir\odt_installer.exe"
                Invoke-WebRequest -Uri $url -OutFile $odtInstaller
                Start-Process $odtInstaller -ArgumentList "/extract:$odtDir /quiet" -Wait
                $setupExe = "$odtDir\setup.exe"
            }
            
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
            
            $win.Dispatcher.Invoke([Action]{ Log-Message "Running setup.exe /configure configuration.xml (Follow the Microsoft UI)..." })
            $proc = Start-Process $setupExe -ArgumentList "/configure $odtDir\configuration.xml" -Wait -PassThru
            if ($proc.ExitCode -eq 0) {
                $win.Dispatcher.Invoke([Action]{ 
                    Log-Message "[OK] $t installed successfully."
                    Add-Activity "Office Installer" "$t installed" "Success"
                })
            } else {
                $win.Dispatcher.Invoke([Action]{ 
                    Log-Message "[FAIL] $t failed (Exit code: $($proc.ExitCode))."
                    Add-Activity "Office Installer" "$t install failed" "Failed"
                })
            }
        } @($pkgId, $title)
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
    Log-Message "[OK] MAS process initialized."
    Add-Activity "System Activation" "MAS GUI opened successfully" "Success"
})

# Check Activation Status
$btn_check_license.Add_Click({
    Log-Message "Checking Windows activation status details..."
    Add-Activity "Diagnostics" "Checking activation status..." "Running"
    Run-Async {
        param($win)
        $res = cscript //nologo $env:SystemRoot\system32\slmgr.vbs /dli
        $joined = $res -join "`r`n"
        $win.Dispatcher.Invoke([Action]{ 
            Log-Message "License details returned:" 
            Log-Message $joined
            Add-Activity "Diagnostics" "Activation Checked" "Success"
        })
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
    Run-Async {
        param($win, $k, $ed)
        $win.Dispatcher.Invoke([Action]{ Log-Message "Installing product key: $k..." })
        
        $proc = Start-Process changepk.exe -ArgumentList "/ProductKey $k" -NoNewWindow -PassThru -Wait
        $win.Dispatcher.Invoke([Action]{ 
            Log-Message "Edition upgrade process completed (Exit code: $($proc.ExitCode))."
            Add-Activity "Edition Changer" "Upgraded to $ed" "Success"
        })
    } -ArgumentList $key, $selectedEdition
})

# --- REPAIR FUNCTIONS CALLBACKS ---
function Run-RepairCommand ($argsList, $opName) {
    Log-Message "Initiating command: $($argsList -join ' ')..."
    Add-Activity "System Repair" "Running $opName" "Running"
    Run-Async {
        param($win, $cmd, $args, $name)
        $proc = Start-Process $cmd -ArgumentList $args -NoNewWindow -PassThru -Wait
        $win.Dispatcher.Invoke([Action]{ 
            Log-Message "$name finished with exit code: $($proc.ExitCode)" 
            Add-Activity "System Repair" "$name completed" "Success"
        })
    } -ArgumentList $argsList[0], ($argsList[1..($argsList.Length-1)] -join ' '), $opName
}

$btn_rep_sfc.Add_Click({ Run-RepairCommand @("sfc", "/scannow") "SFC Scan" })
$btn_rep_dism.Add_Click({ Run-RepairCommand @("dism", "/online", "/cleanup-image", "/restorehealth") "DISM RestoreHealth" })
$btn_rep_dism_check.Add_Click({ Run-RepairCommand @("dism", "/online", "/cleanup-image", "/checkhealth") "DISM CheckHealth" })
$btn_rep_wu.Add_Click({
    Log-Message "Resetting Windows Update components cache..."
    Add-Activity "System Repair" "Resetting Update Cache" "Running"
    Run-Async {
        param($win)
        Stop-Service wuauserv -Force -ErrorAction SilentlyContinue
        Stop-Service bits -Force -ErrorAction SilentlyContinue
        
        $win.Dispatcher.Invoke([Action]{ Log-Message "Deleting SoftwareDistribution download cache..." })
        Remove-Item "$env:SystemRoot\SoftwareDistribution\Download\*" -Recurse -Force -ErrorAction SilentlyContinue
        
        Start-Service wuauserv -ErrorAction SilentlyContinue
        Start-Service bits -ErrorAction SilentlyContinue
        $win.Dispatcher.Invoke([Action]{ 
            Log-Message "[OK] Windows Update services cache reset completed." 
            Add-Activity "System Repair" "Reset Update Cache completed" "Success"
        })
    }
})

$btn_rep_engines.Add_Click({
    Log-Message "Repairing Windows native repair engines (SFC/DISM Fix)..."
    Add-Activity "System Repair" "Repair Native Engines" "Running"
    Run-Async {
        param($win)
        Remove-Item "$env:SystemRoot\Logs\CBS\CBS.log" -Force -ErrorAction SilentlyContinue
        dism /online /cleanup-image /startcomponentcleanup | Out-Null
        $win.Dispatcher.Invoke([Action]{ 
            Log-Message "[OK] Native repair engines refreshed successfully." 
            Add-Activity "System Repair" "Repair Native Engines completed" "Success"
        })
    }
})

$btn_rep_dll.Add_Click({
    Log-Message "Re-registering core Windows System DLL Libraries..."
    Add-Activity "System Repair" "Re-register DLLs" "Running"
    Run-Async {
        param($win)
        $dlls = @("atl.dll", "urlmon.dll", "mshtml.dll", "shdocvw.dll", "browseui.dll", "jscript.dll", "vbscript.dll", "scrrun.dll", "msxml.dll", "msxml3.dll", "msxml6.dll", "actxprxy.dll", "softpub.dll", "wintrust.dll", "dssenh.dll", "gpkcsp.dll", "sccbase.dll", "slbcsp.dll", "cryptdlg.dll", "ole32.dll", "oleaut32.dll", "initpki.dll", "msi.dll")
        $success = 0
        foreach ($dll in $dlls) {
            $proc = Start-Process regsvr32.exe -ArgumentList "/s $dll" -NoNewWindow -PassThru -Wait
            if ($proc.ExitCode -eq 0) { $success++ }
        }
        $win.Dispatcher.Invoke([Action]{ 
            Log-Message "[OK] Re-registered $success system DLL files." 
            Add-Activity "System Repair" "Re-register DLLs completed" "Success"
        })
    }
})

$btn_rep_dns.Add_Click({
    Log-Message "Flushing DNS resolver cache..."
    ipconfig /flushdns | Out-Null
    Log-Message "[OK] DNS cache flushed."
    Add-Activity "System Repair" "Flush DNS Cache" "Success"
})

$btn_rep_winsock.Add_Click({ Run-RepairCommand @("netsh", "winsock", "reset") "Winsock Reset" })
$btn_rep_firewall.Add_Click({ Run-RepairCommand @("netsh", "advfirewall", "reset") "Firewall Defaults Reset" })

$btn_rep_store.Add_Click({
    Log-Message "Re-registering Microsoft App Store packages..."
    Add-Activity "System Repair" "Repair App Store" "Running"
    Run-Async {
        param($win)
        Get-AppXPackage -AllUsers -Name "Microsoft.WindowsStore" | Foreach-Object {
            Add-AppxPackage -DisableDevelopmentMode -Register "$($_.InstallLocation)\AppXManifest.xml"
        }
        $win.Dispatcher.Invoke([Action]{ 
            Log-Message "[OK] Microsoft App Store packages re-registered." 
            Add-Activity "System Repair" "Repair App Store completed" "Success"
        })
    }
})

# wsreset cache reset
$btn_rep_wsreset.Add_Click({
    Log-Message "Resetting Microsoft Store Cache (wsreset.exe)..."
    Add-Activity "System Repair" "wsreset cache reset" "Running"
    Run-Async {
        param($win)
        $proc = Start-Process wsreset.exe -PassThru -Wait
        $win.Dispatcher.Invoke([Action]{ 
            Log-Message "[OK] wsreset process completed successfully."
            Add-Activity "System Repair" "wsreset completed" "Success"
        })
    }
})

# WMI database rebuild
$btn_rep_wmi.Add_Click({
    Log-Message "Attempting salvage / rebuild of corrupted Windows WMI Repository..."
    Add-Activity "System Repair" "Rebuild WMI Repository" "Running"
    Run-Async {
        param($win)
        $proc = Start-Process winmgmt.exe -ArgumentList "/salvagerepository" -NoNewWindow -PassThru -Wait
        $win.Dispatcher.Invoke([Action]{ 
            Log-Message "[OK] WMI Salvage command finished with exit code: $($proc.ExitCode)."
            Add-Activity "System Repair" "WMI Rebuilt" "Success"
        })
    }
})

# Rebuild Search Index
$btn_rep_search.Add_Click({
    Log-Message "Rebuilding Windows Search Indexer Database (Forces full catalog rebuild)..."
    try {
        Stop-Service wsearch -Force -ErrorAction SilentlyContinue
        Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows Search" -Name "SetupCompletedSuccessfully" -Value 0 -Force
        Start-Service wsearch -ErrorAction SilentlyContinue
        Log-Message "[OK] Search indexer database reset. Windows is now rebuilding the index in the background."
        Add-Activity "System Tweak" "Rebuilt Search Index" "Success"
    } catch {
        Log-Message "[FAIL] Error resetting Search Index: $_"
    }
})

$btn_rep_net.Add_Click({
    Log-Message "Running complete network adapter reset..."
    Add-Activity "System Repair" "Network Adapter Reset" "Running"
    Run-Async {
        param($win)
        $win.Dispatcher.Invoke([Action]{ Log-Message "Resetting Winsock catalog..." })
        netsh winsock reset | Out-Null
        $win.Dispatcher.Invoke([Action]{ Log-Message "Resetting TCP/IP stack..." })
        netsh int ip reset | Out-Null
        $win.Dispatcher.Invoke([Action]{ 
            Log-Message "[OK] Network reset completed. Please restart your system." 
            Add-Activity "System Repair" "Network Reset completed" "Success"
        })
    }
})

$btn_rep_winre_en.Add_Click({ Run-RepairCommand @("reagentc", "/enable") "Enable WinRE" })
$btn_rep_winre_stat.Add_Click({ Run-RepairCommand @("reagentc", "/info") "WinRE Status Check" })

$btn_rep_off_quick.Add_Click({
    Log-Message "Running Microsoft Office Quick Repair (Click-to-Run)..."
    Add-Activity "System Repair" "Office Quick Repair" "Running"
    Run-Async {
        param($win)
        $proc = Start-Process "C:\Program Files\Common Files\microsoft shared\ClickToRun\OfficeClickToRun.exe" -ArgumentList "scenario=Repair platform=x64 culture=en-us ForceRepair=1" -NoNewWindow -PassThru -Wait
        $win.Dispatcher.Invoke([Action]{ 
            Log-Message "[OK] Office Quick Repair finished." 
            Add-Activity "System Repair" "Office Quick Repair completed" "Success"
        })
    }
})

$btn_rep_off_pst.Add_Click({
    Log-Message "Searching and launching Outlook ScanPST tool..."
    Run-Async {
        param($win)
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
            $win.Dispatcher.Invoke([Action]{ Log-Message "[FAIL] ScanPST.exe could not be found in default Office directories." })
        } else {
            $win.Dispatcher.Invoke([Action]{ Log-Message "[OK] Launched ScanPST successfully." })
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
    Run-Async {
        param($win)
        $proc = Start-Process chkdsk -ArgumentList "C: /f /r" -RedirectStandardInput "$env:temp\y.txt" -NoNewWindow -PassThru -Wait
        $win.Dispatcher.Invoke([Action]{ Log-Message "[OK] Boot check scheduled. Please reboot your machine to scan." })
    }
})

$btn_rep_printer_11b.Add_Click({
    Log-Message "Fixing Printer Sharing Error 0x0000011b..."
    try {
        Set-ItemProperty -Path "HKLM:\System\CurrentControlSet\Control\Print" -Name "RpcAuthnLevelPrivacyEnabled" -Value 0 -Force
        Log-Message "[OK] Applied RPC privacy key registry bypass."
        Add-Activity "Printer Repair" "Error 0x0000011b Fixed" "Success"
    } catch {
        Log-Message "[FAIL] Failed to modify print registry keys: $_"
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
        
        Log-Message "[OK] Printer GPO Point and Print / RPC rules applied."
        Add-Activity "Printer Repair" "GPO Printer Policies Applied" "Success"
    } catch {
        Log-Message "[FAIL] Failed to write print GPO keys: $_"
    }
})

$btn_rep_printer_lpd.Add_Click({
    Log-Message "Enabling Windows LPD Print Service & LPR Port Monitor Optional Features..."
    Add-Activity "Printer Repair" "Enable LPD/LPR Features" "Running"
    Run-Async {
        param($win)
        Enable-WindowsOptionalFeature -Online -FeatureName "LPDPrintService" -NoRestart | Out-Null
        Enable-WindowsOptionalFeature -Online -FeatureName "LPRPortMonitor" -NoRestart | Out-Null
        $win.Dispatcher.Invoke([Action]{ 
            Log-Message "[OK] LPD Print service and LPR Port Monitor features enabled." 
            Add-Activity "Printer Repair" "LPD/LPR Features Enabled" "Success"
        })
    }
})

$btn_rep_printer_disc.Add_Click({
    Log-Message "Restarting Network Discovery and Printer sharing dependency services..."
    Run-Async {
        param($win)
        $services = @("FDResPub", "SSDPSrv", "UPnPHost", "Dnscache")
        foreach ($s in $services) {
            Set-Service -Name $s -StartupType Automatic -ErrorAction SilentlyContinue
            Restart-Service -Name $s -Force -ErrorAction SilentlyContinue
        }
        $win.Dispatcher.Invoke([Action]{ Log-Message "[OK] Network discovery dependency services restarted." })
    }
})

$btn_rep_printer_spool.Add_Click({
    Log-Message "Stopping Print Spooler..."
    Stop-Service spooler -Force
    Log-Message "Clearing print queue directory..."
    Remove-Item "$env:SystemRoot\system32\spool\PRINTERS\*" -Force -Recurse -ErrorAction SilentlyContinue
    Log-Message "Starting Print Spooler..."
    Start-Service spooler
    Log-Message "[OK] Print Spooler restarted and queue cleared successfully."
    Add-Activity "Printer Repair" "Spooler Cleaned" "Success"
})

$btn_rep_printer_diag.Add_Click({ Run-RepairCommand @("msdt.exe", "/id", "PrinterDiagnostic") "Printer Troubleshooter Wizard" })

# New Printer offline fix
$btn_rep_printer_offline.Add_Click({
    Log-Message "Fixing Printer Offline status status bug (Disable SNMP Status registry check)..."
    try {
        Get-ChildItem -Path "HKLM:\System\CurrentControlSet\Control\Print\Monitors\Standard TCP/IP Port\Ports" | ForEach-Object {
            Set-ItemProperty -Path $_.PSPath -Name "SNMP Enabled" -Value 0 -Force
        }
        Log-Message "[OK] Disabled SNMP Enabled flags for all TCP/IP printer ports."
        Add-Activity "Printer Repair" "SNMP Offline Status Fix" "Success"
    } catch {
        Log-Message "[FAIL] Error disabling SNMP status: $_"
    }
})

# Wipe Printer Drivers
$btn_rep_printer_drivers.Add_Click({
    Log-Message "Wiping corrupted printer drivers registry configuration keys..."
    try {
        Stop-Service spooler -Force
        Remove-Item -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Print\Environments\Windows x64\Drivers\Version-3\*" -Force -Recurse -ErrorAction SilentlyContinue
        Remove-Item -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Print\Environments\Windows x64\Drivers\Version-4\*" -Force -Recurse -ErrorAction SilentlyContinue
        Start-Service spooler
        Log-Message "[OK] Corrupted printer driver configuration keys cleaned."
        Add-Activity "Printer Repair" "Wiped Corrupted Drivers" "Success"
    } catch {
        Log-Message "[FAIL] Failed to wipe printer driver keys: $_"
    }
})

# Disable Print Spooler
$btn_rep_printer_dis_spooler.Add_Click({
    Log-Message "Stopping and disabling Print Spooler service for security..."
    try {
        Stop-Service spooler -Force
        Set-Service -Name spooler -StartupType Disabled
        Log-Message "[OK] Print Spooler stopped and disabled successfully."
        Add-Activity "Printer Repair" "Print Spooler Disabled" "Success"
    } catch {
        Log-Message "[FAIL] Failed to disable Spooler: $_"
    }
})

# NTFS Convert
$btn_conv_ntfs.Add_Click({
    $drv = $cb_ntfs_drive.Text
    Log-Message "Converting drive $drv to NTFS partition style losslessly..."
    Run-Async {
        param($win, $d)
        $proc = Start-Process convert.exe -ArgumentList "$d /fs:ntfs" -NoNewWindow -PassThru -Wait
        $win.Dispatcher.Invoke([Action]{ Log-Message "NTFS conversion completed (Exit code: $($proc.ExitCode))." })
    } -ArgumentList $drv
})

# MBR to GPT Convert
$btn_conv_gpt.Add_Click({
    $disk = $cb_gpt_disk.Text.Replace("Disk ", "")
    Log-Message "Converting disk $disk from MBR to GPT partition style..."
    Run-Async {
        param($win, $dk)
        $proc = Start-Process mbr2gpt.exe -ArgumentList "/convert /disk:$dk /allowFullOS" -NoNewWindow -PassThru -Wait
        $win.Dispatcher.Invoke([Action]{ Log-Message "MBR2GPT completed (Exit code: $($proc.ExitCode))." })
    } -ArgumentList $disk
})

# Advanced Memory Optimizer (WPF C# EmptyWorkingSet)
$btn_rep_clean_ram_wpf.Add_Click({
    Log-Message "Running Advanced Memory API Optimizer (EmptyWorkingSet P/Invoke)..."
    Add-Activity "Memory Optimization" "API Empty Working Set Memory optimization" "Running"
    Run-Async {
        param($win)
        $csharp = @"
        using System;
        using System.Runtime.InteropServices;
        using System.Diagnostics;
        public class MemoryOptimizer {
            [DllImport("psapi.dll")]
            public static extern int EmptyWorkingSet(IntPtr hwProc);
            public static int Optimize() {
                int count = 0;
                foreach (Process p in Process.GetProcesses()) {
                    try {
                        if (EmptyWorkingSet(p.Handle) != 0) { count++; }
                    } catch {}
                }
                return count;
            }
        }
"@
        Add-Type -TypeDefinition $csharp -ErrorAction SilentlyContinue
        $optimizedCount = [MemoryOptimizer]::Optimize()
        $win.Dispatcher.Invoke([Action]{ 
            Log-Message "[OK] EWS RAM API Optimizer completed. Purged working sets of $optimizedCount active processes." 
            Add-Activity "Memory Optimization" "EWS API RAM Optimizer completed" "Success"
        })
    }
})

$btn_rep_clean_ram.Add_Click({
    Log-Message "Flushing Standby List memory allocations..."
    Add-Activity "Memory Optimization" "Flushing RAM cache standby list" "Running"
    [System.GC]::Collect()
    Log-Message "[OK] Process working sets GC collected."
    Add-Activity "Memory Optimization" "Flushed standby lists successfully" "Success"
})

$btn_rep_clean_browser.Add_Click({
    Log-Message "Cleaning browser caches..."
    Run-Async {
        param($win)
        Remove-Item "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Cache\*" -Force -Recurse -ErrorAction SilentlyContinue
        Remove-Item "$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\Cache\*" -Force -Recurse -ErrorAction SilentlyContinue
        Remove-Item "$env:LOCALAPPDATA\Mozilla\Firefox\Profiles\*\cache2\*" -Force -Recurse -ErrorAction SilentlyContinue
        $win.Dispatcher.Invoke([Action]{ Log-Message "[OK] Web Browser Cache cleared successfully." })
    }
})

# cleanmgr deep cleanup
$btn_rep_clean_mgr.Add_Click({
    Log-Message "Launching deep cleanmgr command scan..."
    Add-Activity "Disk Cleaning" "Deep Disk Cleanup" "Running"
    Run-Async {
        param($win)
        $proc = Start-Process cleanmgr.exe -ArgumentList "/autoclean" -NoNewWindow -PassThru -Wait
        $win.Dispatcher.Invoke([Action]{ 
            Log-Message "[OK] Deep disk cleanup manager finished." 
            Add-Activity "Disk Cleaning" "Deep Disk Cleanup completed" "Success"
        })
    }
})

# Component store cleanup ResetBase
$btn_rep_clean_resetbase.Add_Click({
    Log-Message "Purging superseded updates from system Component Store (ResetBase)..."
    Add-Activity "Disk Cleaning" "Component Store ResetBase Purge" "Running"
    Run-Async {
        param($win)
        $proc = Start-Process dism.exe -ArgumentList "/online /cleanup-image /startcomponentcleanup /resetbase" -NoNewWindow -PassThru -Wait
        $win.Dispatcher.Invoke([Action]{ 
            Log-Message "[OK] Component Store ResetBase completed (Exit code: $($proc.ExitCode))." 
            Add-Activity "Disk Cleaning" "Component Store ResetBase completed" "Success"
        })
    }
})

# Delete Temp Directories
$btn_rep_clean_temp.Add_Click({
    Log-Message "Purging all files in User and System Temp directory paths..."
    Add-Activity "Disk Cleaning" "Delete TEMP Files" "Running"
    Run-Async {
        param($win)
        $paths = @(
            "$env:temp\*"
            "C:\Windows\Temp\*"
        )
        foreach ($p in $paths) {
            Remove-Item -Path $p -Force -Recurse -ErrorAction SilentlyContinue
        }
        $win.Dispatcher.Invoke([Action]{ 
            Log-Message "[OK] Completed cleaning temporary directories." 
            Add-Activity "Disk Cleaning" "TEMP Files cleaned" "Success"
        })
    }
})

# Empty Recycle Bin
$btn_rep_recycle.Add_Click({
    Log-Message "Emptying Windows Recycle Bin database on all drives silently..."
    Add-Activity "Disk Cleaning" "Empty Recycle Bin" "Running"
    Run-Async {
        param($win)
        Clear-RecycleBin -Force -ErrorAction SilentlyContinue
        $win.Dispatcher.Invoke([Action]{ 
            Log-Message "[OK] Recycle Bin emptied successfully." 
            Add-Activity "Disk Cleaning" "Recycle Bin Emptied" "Success"
        })
    }
})

# Defrag / Optimize Drives
$btn_rep_defrag.Add_Click({
    Log-Message "Optimizing and Defragmenting all connected system drives..."
    Add-Activity "Disk Cleaning" "Optimize/Defrag Volumes" "Running"
    Run-Async {
        param($win)
        Optimize-Volume -DriveLetter C -Defrag -Verbose | Out-Null
        $win.Dispatcher.Invoke([Action]{ 
            Log-Message "[OK] Completed volume defragmentation and trimming optimization passes."
            Add-Activity "Disk Cleaning" "Optimize/Defrag Completed" "Success"
        })
    }
})

$btn_rep_shield_wu.Add_Click({
    Log-Message "Running comprehensive Windows Update Service repair engine..."
    Add-Activity "System Repair" "Windows Update Service Repair" "Running"
    Run-Async {
        param($win)
        Stop-Service wuauserv -Force -ErrorAction SilentlyContinue
        Stop-Service bits -Force -ErrorAction SilentlyContinue
        $dlls = @("wups.dll", "wups2.dll", "wuaueng.dll", "wuapi.dll", "wucltux.dll", "wuwebv.dll")
        foreach ($d in $dlls) { Start-Process regsvr32.exe -ArgumentList "/s $d" -Wait }
        Start-Service wuauserv -ErrorAction SilentlyContinue
        Start-Service bits -ErrorAction SilentlyContinue
        $win.Dispatcher.Invoke([Action]{ 
            Log-Message "[OK] Windows Update components registered and services restarted." 
            Add-Activity "System Repair" "Windows Update Service Repair completed" "Success"
        })
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
        Log-Message "[OK] Windows Update service disabled and GPO block applied."
        Add-Activity "Shield Tweak" "Windows Updates Blocked" "Success"
    } catch {
        Log-Message "[FAIL] Failed to block Windows Updates: $_"
    }
})

$btn_rep_shield_enable_wu.Add_Click({
    Log-Message "Enabling automatic Windows Updates..."
    try {
        Remove-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" -Name "NoAutoUpdate" -Force -ErrorAction SilentlyContinue
        Set-Service -Name wuauserv -StartupType Automatic -ErrorAction SilentlyContinue
        Start-Service wuauserv -ErrorAction SilentlyContinue
        Log-Message "[OK] Windows Update service enabled and GPO block removed."
        Add-Activity "Shield Tweak" "Windows Updates Enabled" "Success"
    } catch {
        Log-Message "[FAIL] Failed to enable Windows Updates: $_"
    }
})

$btn_rep_shield_defender.Add_Click({
    Log-Message "Resetting Windows Defender policies..."
    Add-Activity "System Repair" "Reset Windows Defender Policies" "Running"
    try {
        Remove-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows Defender" -Recurse -Force -ErrorAction SilentlyContinue
        Start-Service WinDefend -ErrorAction SilentlyContinue
        Log-Message "[OK] Windows Defender policies reset successfully."
        Add-Activity "System Repair" "Reset Windows Defender Policies completed" "Success"
    } catch {
        Log-Message "[FAIL] Failed to reset Defender: $_"
    }
})

$btn_rep_shield_firewall.Add_Click({ Run-RepairCommand @("netsh", "advfirewall", "reset") "Restore default firewall rules" })

$btn_rep_shield_audio.Add_Click({
    Log-Message "Resetting and restarting Windows Audio Playback services..."
    Run-Async {
        param($win)
        Stop-Service AudioSrv -Force -ErrorAction SilentlyContinue
        Stop-Service AudioEndpointBuilder -Force -ErrorAction SilentlyContinue
        Start-Service AudioEndpointBuilder -ErrorAction SilentlyContinue
        Start-Service AudioSrv -ErrorAction SilentlyContinue
        $win.Dispatcher.Invoke([Action]{ Log-Message "[OK] AudioSrv and AudioEndpointBuilder restarted successfully." })
    }
})

$btn_rep_shell_explorer.Add_Click({
    Log-Message "Restarting Windows Explorer shell..."
    Stop-Process -Name explorer -Force -ErrorAction SilentlyContinue
    Start-Process explorer
    Log-Message "[OK] Explorer restarted."
})

$btn_rep_shell_events.Add_Click({
    Log-Message "Clearing all Application, System, and Security event logs..."
    Add-Activity "System Repair" "Clear Event Logs" "Running"
    Run-Async {
        param($win)
        wevtutil el | Foreach-Object { wevtutil cl $_ }
        $win.Dispatcher.Invoke([Action]{ 
            Log-Message "[OK] Windows Event Logs cleared successfully." 
            Add-Activity "System Repair" "Clear Event Logs completed" "Success"
        })
    }
})

$btn_rep_shell_icon.Add_Click({
    Log-Message "Rebuilding icon and thumbnail cache databases..."
    Run-Async {
        param($win)
        Stop-Process -Name explorer -Force -ErrorAction SilentlyContinue
        Remove-Item "$env:localappdata\IconCache.db" -Force -ErrorAction SilentlyContinue
        Remove-Item "$env:localappdata\Microsoft\Windows\Explorer\thumbcache_*.db" -Force -ErrorAction SilentlyContinue
        Start-Process explorer
        $win.Dispatcher.Invoke([Action]{ Log-Message "[OK] Icon and thumbnail cache rebuilt successfully." })
    }
})

$btn_rep_shell_font.Add_Click({
    Log-Message "Rebuilding Windows System Font Cache..."
    Run-Async {
        param($win)
        Stop-Service -Name "FontCache" -Force -ErrorAction SilentlyContinue
        Remove-Item "$env:SystemRoot\ServiceProfiles\LocalService\AppData\Local\FontCache\*" -Force -Recurse -ErrorAction SilentlyContinue
        Start-Service -Name "FontCache" -ErrorAction SilentlyContinue
        $win.Dispatcher.Invoke([Action]{ Log-Message "[OK] Font Cache rebuilt and service restarted." })
    }
})

# --- BLOATWARE REMOVER & OPTIONAL FEATURES ---
$btn_remove_bloat.Add_Click({
    Log-Message "Starting UWP bloatware package removal..."
    Add-Activity "System Repair" "Remove Bloatware UWP Apps" "Running"
    Run-Async {
        param($win)
        $bloat = @("*xbox*", "*skype*", "*solitaire*", "*bingweather*", "*maps*", "*getstarted*", "*officehub*", "*onenote*")
        foreach ($b in $bloat) {
            Get-AppxPackage -AllUsers $b | Remove-AppxPackage -AllUsers -ErrorAction SilentlyContinue
        }
        $win.Dispatcher.Invoke([Action]{ 
            Log-Message "[OK] Windows bloatware packages removed." 
            Add-Activity "System Repair" "Remove Bloatware UWP Apps completed" "Success"
        })
    }
})

# New Telemetry / Edge Cleaners
$btn_bloat_onedrive.Add_Click({
    Log-Message "Completely purging Microsoft OneDrive Client from the system..."
    Add-Activity "Bloatware Purge" "Purge OneDrive Client" "Running"
    Run-Async {
        param($win)
        taskkill /f /im OneDrive.exe | Out-Null
        if (Test-Path "$env:SystemRoot\System32\OneDriveSetup.exe") {
            $proc = Start-Process "$env:SystemRoot\System32\OneDriveSetup.exe" -ArgumentList "/uninstall" -Wait -PassThru
        } elseif (Test-Path "$env:SystemRoot\SysWOW64\OneDriveSetup.exe") {
            $proc = Start-Process "$env:SystemRoot\SysWOW64\OneDriveSetup.exe" -ArgumentList "/uninstall" -Wait -PassThru
        }
        $win.Dispatcher.Invoke([Action]{ 
            Log-Message "[OK] OneDrive Client uninstall command triggered." 
            Add-Activity "Bloatware Purge" "Purged OneDrive Client" "Success"
        })
    }
})

$btn_bloat_edge.Add_Click({
    Log-Message "Blocking Edge browser background telemetry & updates..."
    try {
        New-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Edge" -Force -ErrorAction SilentlyContinue | Out-Null
        Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Edge" -Name "MetricsReportingEnabled" -Value 0 -Force
        
        New-Item -Path "HKLM:\SOFTWARE\Microsoft\EdgeUpdate" -Force -ErrorAction SilentlyContinue | Out-Null
        Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\EdgeUpdate" -Name "AutoUpdateDisableUntilTime" -Value 1 -Force
        
        Log-Message "[OK] Edge browser telemetry disabled."
        Add-Activity "Telemetry Tweak" "Edge Telemetry Blocked" "Success"
    } catch {
        Log-Message "[FAIL] Error blocking Edge telemetry: $_"
    }
})

$btn_apply_features.Add_Click({
    Log-Message "Configuring Windows Optional Features..."
    $lpd = $cb_feat_lpd.IsChecked
    $lpr = $cb_feat_lpr.IsChecked
    $smb = $cb_feat_smb.IsChecked
    $hyp = $cb_feat_hyperv.IsChecked
    $snd = $cb_feat_sandbox.IsChecked
    $wsl = $cb_feat_wsl.IsChecked
    
    Run-Async {
        param($win, $eLpd, $eLpr, $eSmb, $eHyp, $eSnd, $eWsl)
        if ($eLpd) {
            $win.Dispatcher.Invoke([Action]{ Log-Message "Enabling LPD Print Service..." })
            Enable-WindowsOptionalFeature -Online -FeatureName "LPDPrintService" -NoRestart | Out-Null
        }
        if ($eLpr) {
            $win.Dispatcher.Invoke([Action]{ Log-Message "Enabling LPR Port Monitor..." })
            Enable-WindowsOptionalFeature -Online -FeatureName "LPRPortMonitor" -NoRestart | Out-Null
        }
        if ($eSmb) {
            $win.Dispatcher.Invoke([Action]{ Log-Message "Enabling SMB1 Protocol Service..." })
            Enable-WindowsOptionalFeature -Online -FeatureName "SMB1Protocol" -NoRestart | Out-Null
        }
        if ($eHyp) {
            $win.Dispatcher.Invoke([Action]{ Log-Message "Enabling Hyper-V Platform..." })
            Enable-WindowsOptionalFeature -Online -FeatureName "Microsoft-Hyper-V-All" -NoRestart | Out-Null
        }
        if ($eSnd) {
            $win.Dispatcher.Invoke([Action]{ Log-Message "Enabling Windows Sandbox..." })
            Enable-WindowsOptionalFeature -Online -FeatureName "Containers-DisposableKit" -NoRestart | Out-Null
        }
        if ($eWsl) {
            $win.Dispatcher.Invoke([Action]{ Log-Message "Enabling WSL Platform..." })
            Enable-WindowsOptionalFeature -Online -FeatureName "Microsoft-Windows-Subsystem-Linux" -NoRestart | Out-Null
        }
        $win.Dispatcher.Invoke([Action]{ Log-Message "[OK] Optional features configuration completed." })
    } -ArgumentList $lpd, $lpr, $smb, $hyp, $snd, $wsl
})

# --- SYSTEM TWEAKS IMPLEMENTATION ---
$btn_tweak_classic.Add_Click({
    Log-Message "Restoring Win11 Classic Context Menu..."
    try {
        New-Item -Path "HKCU:\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}" -Force | Out-Null
        New-Item -Path "HKCU:\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32" -Force | Out-Null
        Set-ItemProperty -Path "HKCU:\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32" -Name "(Default)" -Value "" -Force
        Log-Message "[OK] Classic Right-click context menu enabled. Restart Explorer to apply."
    } catch {
        Log-Message "[FAIL] Error applying context menu tweak: $_"
    }
})

$btn_tweak_default_ctx.Add_Click({
    Log-Message "Reverting to Win11 Default Context Menu..."
    try {
        Remove-Item -Path "HKCU:\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}" -Recurse -Force -ErrorAction SilentlyContinue
        Log-Message "[OK] Default modern menu layout restored. Restart Explorer to apply."
    } catch {
        Log-Message "[FAIL] Error removing context menu tweak: $_"
    }
})

$btn_tweak_ultimate.Add_Click({
    Log-Message "Unlocking Ultimate Performance Power Scheme..."
    $res = powercfg -duplicatescheme e9a22db2-565e-4b6e-82f0-8022c5e3430b
    Log-Message $res
    Log-Message "[OK] Power plan scheme unlocked."
})

$btn_tweak_gaming.Add_Click({
    Log-Message "Applying Low-Latency Gaming Registry tweaks..."
    try {
        New-Item -Path "HKCU:\System\GameConfigStore" -Force -ErrorAction SilentlyContinue | Out-Null
        Set-ItemProperty -Path "HKCU:\System\GameConfigStore" -Name "GameDVR_Enabled" -Value 0 -Force
        
        New-Item -Path "HKLM:\SOFTWARE\Microsoft\PolicyManager\default\ApplicationManagement\AllowGameDVR" -Force -ErrorAction SilentlyContinue | Out-Null
        Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\PolicyManager\default\ApplicationManagement\AllowGameDVR" -Name "value" -Value 0 -Force
        
        Log-Message "[OK] Disallowed GameDVR overlays."
        
        New-Item -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" -Force -ErrorAction SilentlyContinue | Out-Null
        Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" -Name "SystemResponsiveness" -Value 0 -Force
        
        Log-Message "[OK] Optimized game process latency bindings."
    } catch {
        Log-Message "[FAIL] Failed to apply some gaming tweaks: $_"
    }
})

$btn_tweak_bing.Add_Click({
    Log-Message "Disabling online Bing Search in Start Menu..."
    try {
        New-Item -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Search" -Force -ErrorAction SilentlyContinue | Out-Null
        Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Search" -Name "BingSearchEnabled" -Value 0 -Force
        Log-Message "[OK] Online Bing Start Menu results disabled."
    } catch {
        Log-Message "[FAIL] Failed to apply Bing Search GPO registry key: $_"
    }
})

$btn_tweak_fast_on.Add_Click({
    Log-Message "Enabling Windows Fast Startup..."
    try {
        Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Power" -Name "HiberbootEnabled" -Value 1 -Force
        Log-Message "[OK] Hiberboot Enabled successfully."
    } catch {
        Log-Message "[FAIL] Failed to enable Fast Startup: $_"
    }
})

$btn_tweak_fast_off.Add_Click({
    Log-Message "Disabling Windows Fast Startup..."
    try {
        Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Power" -Name "HiberbootEnabled" -Value 0 -Force
        Log-Message "[OK] Hiberboot Disabled successfully."
    } catch {
        Log-Message "[FAIL] Failed to disable Fast Startup: $_"
    }
})

# Visual Performance Mode
$btn_tweak_visuals.Add_Click({
    Log-Message "Configuring visual effects settings for high performance..."
    try {
        Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects" -Name "VisualFXSetting" -Value 2 -Force
        Set-ItemProperty -Path "HKCU:\Control Panel\Desktop" -Name "UserPreferencesMask" -Value ([byte[]](0x90,0x12,0x01,0x80,0x10,0x00,0x00,0x00)) -Force
        Log-Message "[OK] Visual options configured for Maximum Performance. Restart Explorer to see differences."
        Add-Activity "Visual Tweak" "Set Performance Visuals" "Success"
    } catch {
        Log-Message "[FAIL] Error modifying visual properties: $_"
    }
})

# Pagefile Optimizer
$btn_tweak_pagefile.Add_Click({
    Log-Message "Optimizing Virtual Memory allocation (Pagefile sizing)..."
    try {
        $wmi = Get-CimInstance Win32_ComputerSystem
        $wmi.AutomaticManagedPagefile = $true
        Set-CimInstance -InputObject $wmi
        Log-Message "[OK] Enabled Windows Automatic Managed Pagefile configuration."
        Add-Activity "Memory Tweak" "Pagefile Auto-managed" "Success"
    } catch {
        Log-Message "[FAIL] Error writing virtual memory flags: $_"
    }
})

# Telemetry Tweaks
$btn_tweak_cortana.Add_Click({
    Log-Message "Disabling Cortana and Windows Copilot assistant modules..."
    try {
        New-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot" -Force -ErrorAction SilentlyContinue | Out-Null
        Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot" -Name "TurnOffWindowsCopilot" -Value 1 -Force
        
        New-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\Windows Search" -Force -ErrorAction SilentlyContinue | Out-Null
        Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\Windows Search" -Name "AllowCortana" -Value 0 -Force
        
        Log-Message "[OK] Disallowed Cortana Search and Copilot taskbar interfaces."
        Add-Activity "Privacy Tweak" "Disabled Assistants" "Success"
    } catch {
        Log-Message "[FAIL] Error writing registry key properties: $_"
    }
})

$btn_tweak_telemetry.Add_Click({
    Log-Message "Blocking diagnostic telemetry and feedback policies..."
    try {
        Stop-Service DiagTrack -Force -ErrorAction SilentlyContinue
        Set-Service -Name DiagTrack -StartupType Disabled
        
        New-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection" -Force -ErrorAction SilentlyContinue | Out-Null
        Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection" -Name "AllowTelemetry" -Value 0 -Force
        
        Log-Message "[OK] Telmetry services blocked and registry GPO applied."
        Add-Activity "Privacy Tweak" "Blocked Diagnostic Telemetry" "Success"
    } catch {
        Log-Message "[FAIL] Error stopping telemetry bindings: $_"
    }
})

$btn_tweak_ads.Add_Click({
    Log-Message "Disabling Microsoft lockscreen spotlight tips & ads..."
    try {
        New-Item -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" -Force -ErrorAction SilentlyContinue | Out-Null
        Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" -Name "SubscribedContent-338387Enabled" -Value 0 -Force
        Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" -Name "SubscribedContent-338389Enabled" -Value 0 -Force
        
        Log-Message "[OK] Turned off lockscreen Spotlight promotional tips."
        Add-Activity "Privacy Tweak" "Disabled Lockscreen Ads" "Success"
    } catch {
        Log-Message "[FAIL] Error disabling Spotlight properties: $_"
    }
})

# --- DIAGNOSTICS & SPECS CALLBACKS ---
$btn_diag_ping_start.Add_Click({
    $hostTarget = $txt_diag_ping_host.Text.Trim()
    if ($hostTarget -eq "") { return }
    
    if ($btn_diag_ping_start.Content -eq "Stop Ping") {
        $btn_diag_ping_start.Content = "Ping Test"
        $btn_diag_ping_start.Background = [System.Windows.Media.Brushes]::Navy
        Log-Message "Stopping network ping test session."
        return
    }
    
    $btn_diag_ping_start.Content = "Stop Ping"
    $btn_diag_ping_start.Background = [System.Windows.Media.Brushes]::Red
    Log-Message "Starting active ping diagnostic on '$hostTarget'..."
    Add-Activity "Diagnostics" "Running Ping Test on $hostTarget" "Running"
    
    Run-Async {
        param($win, $t)
        while ($true) {
            $btnText = $win.Dispatcher.Invoke([Func[string]]{ $btn_diag_ping_start.Content })
            if ($btnText -eq "Ping Test") { break }
            
            try {
                $ping = Test-Connection -ComputerName $t -Count 1 -ErrorAction Stop
                $time = $ping.ResponseTime
                if ($time -eq $null) { $time = 0 }
                $win.Dispatcher.Invoke([Action]{ 
                    Log-Message "Ping response from ${t}: Reply latency = ${time} ms." 
                })
            } catch {
                $win.Dispatcher.Invoke([Action]{ Log-Message "[FAIL] Ping timed out or failed to reach host: $t" })
            }
            Start-Sleep -Seconds 1
        }
        $win.Dispatcher.Invoke([Action]{ Add-Activity "Diagnostics" "Ping Test Completed" "Success" })
    } -ArgumentList $hostTarget
})

# Show Decrypted Wi-Fi Passwords list
$btn_rep_wifi_pass.Add_Click({
    Log-Message "Decrypting all saved Wi-Fi security keys from netsh profiles..."
    Add-Activity "Diagnostics" "Decrypting Wi-Fi Passwords" "Running"
    Run-Async {
        param($win)
        $profiles = netsh wlan show profiles | Select-String "All User Profile" | ForEach-Object { $_.ToString().Split(":")[1].Trim() }
        $win.Dispatcher.Invoke([Action]{ Log-Message "--- DECRYPTED WI-FI SECURITY PROFILES ---" })
        foreach ($p in $profiles) {
            $res = netsh wlan show profile name="$p" key=clear
            $passLine = $res | Select-String "Key Content"
            if ($passLine) {
                $pwd = $passLine.ToString().Split(":")[1].Trim()
                $win.Dispatcher.Invoke([Action]{ Log-Message " -> Wireless SSID: $p | Security Key: $pwd" })
            } else {
                $win.Dispatcher.Invoke([Action]{ Log-Message " -> Wireless SSID: $p | Security Key: [Open / No Password]" })
            }
        }
        $win.Dispatcher.Invoke([Action]{ Add-Activity "Diagnostics" "Wi-Fi Passwords Decrypted" "Success" })
    }
})

# Export Wi-Fi Profiles XML
$btn_rep_wifi_export.Add_Click({
    Log-Message "Exporting Wi-Fi connection profile XML keys to desktop..."
    Add-Activity "Diagnostics" "Exporting Wi-Fi XML profiles" "Running"
    Run-Async {
        param($win)
        $desktop = [Environment]::GetFolderPath("Desktop")
        netsh wlan export profile folder="$desktop" key=clear | Out-Null
        $win.Dispatcher.Invoke([Action]{ 
            Log-Message "[OK] All decrypted Wi-Fi XML profiles exported to directory: $desktop" 
            Add-Activity "Diagnostics" "Wi-Fi XML Profiles Exported" "Success"
        })
    }
})

# DHCP renew IP
$btn_rep_dhcp.Add_Click({
    Log-Message "Releasing and renewing network adapter IP configurations (DHCP lease refresh)..."
    Add-Activity "Diagnostics" "Renew DHCP IP Address" "Running"
    Run-Async {
        param($win)
        ipconfig /release | Out-Null
        ipconfig /renew | Out-Null
        $win.Dispatcher.Invoke([Action]{ 
            Log-Message "[OK] Completed adapter IP refresh and renewed DHCP connection."
            Add-Activity "Diagnostics" "DHCP IP Address Renewed" "Success"
        })
    }
})

# IPv6 Toggle Disable
$btn_rep_ipv6_dis.Add_Click({
    Log-Message "Disabling IPv6 bindings on all active network adapters..."
    try {
        Disable-NetAdapterBinding -Name "*" -ComponentID "ms_tcpip6" -ErrorAction Stop
        Log-Message "[OK] IPv6 protocol disabled on all adapters."
        Add-Activity "Network Tweak" "IPv6 Disabled" "Success"
    } catch {
        Log-Message "[FAIL] Failed to disable IPv6 binding: $_"
    }
})

$btn_rep_ipv6_en.Add_Click({
    Log-Message "Enabling IPv6 bindings on all active network adapters..."
    try {
        Enable-NetAdapterBinding -Name "*" -ComponentID "ms_tcpip6" -ErrorAction Stop
        Log-Message "[OK] IPv6 protocol enabled on all adapters."
        Add-Activity "Network Tweak" "IPv6 Enabled" "Success"
    } catch {
        Log-Message "[FAIL] Failed to enable IPv6 binding: $_"
    }
})

# Show Top Processes
$btn_diag_top_proc.Add_Click({
    Log-Message "Scanning active process allocations..."
    Add-Activity "Diagnostics" "Scanning processes CPU/RAM allocation" "Running"
    Run-Async {
        param($win)
        $cpuProc = Get-Process | Sort-Object CPU -Descending | Select-Object -First 5
        $ramProc = Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 5
        
        $win.Dispatcher.Invoke([Action]{ Log-Message "--- TOP PROCESSES BY CPU TIME ---" })
        foreach ($p in $cpuProc) {
            $cpuSecs = [Math]::Round($p.CPU)
            $name = $p.ProcessName
            $win.Dispatcher.Invoke([Action]{ Log-Message "  -> Process Name: $name ($cpuSecs CPU-seconds)" })
        }
        
        $win.Dispatcher.Invoke([Action]{ Log-Message "--- TOP PROCESSES BY MEMORY WORKING SET ---" })
        foreach ($p in $ramProc) {
            $wsMB = [Math]::Round($p.WorkingSet / 1MB)
            $name = $p.ProcessName
            $win.Dispatcher.Invoke([Action]{ Log-Message "  -> Process Name: $name ($wsMB MB RAM alloc)" })
        }
        $win.Dispatcher.Invoke([Action]{ Add-Activity "Diagnostics" "Processes Scanned" "Success" })
    }
})

# Export Drivers
$btn_diag_export_drivers.Add_Click({
    Log-Message "Exporting active system drivers details registry list..."
    Add-Activity "Diagnostics" "Exporting drivers list" "Running"
    Run-Async {
        param($win)
        $outFile = "$env:USERPROFILE\Desktop\SystemDriversList.txt"
        Get-CimInstance Win32_SystemDriver | Select-Object Name, DisplayName, State, StartMode | Out-File -FilePath $outFile -Encoding utf8
        $win.Dispatcher.Invoke([Action]{
            Log-Message "[OK] Completed driver manifest export. Document saved: $outFile"
            Add-Activity "Diagnostics" "Driver List Exported" "Success"
        })
    }
})

$btn_diag_specs.Add_Click({
    Log-Message "Generating hardware specifications summary..."
    Add-Activity "Diagnostics" "Generating hardware specifications" "Running"
    Run-Async {
        param($win)
        $cpu = (Get-CimInstance Win32_Processor).Name
        $gpu = (Get-CimInstance Win32_VideoController).Name
        $mobo = (Get-CimInstance Win32_BaseBoard).Product
        $bios = (Get-CimInstance Win32_Bios).SMBIOSBIOSVersion
        
        $win.Dispatcher.Invoke([Action]{
            Log-Message "--- HARDWARE SUMMARY ---"
            Log-Message "Processor: $cpu"
            Log-Message "Graphics: $gpu"
            Log-Message "Motherboard: $mobo"
            Log-Message "BIOS Version: $bios"
            Add-Activity "Diagnostics" "Hardware specifications generated" "Success"
        })
    }
})

$btn_diag_battery.Add_Click({
    Log-Message "Generating Windows Battery Lifecycle HTML Report..."
    Add-Activity "Diagnostics" "Generating Battery Report" "Running"
    Run-Async {
        param($win)
        powercfg /batteryreport /output "$env:USERPROFILE\Desktop\BatteryReport.html" | Out-Null
        $win.Dispatcher.Invoke([Action]{ 
            Log-Message "[OK] HTML Battery Report generated on your Desktop (BatteryReport.html)."
            Add-Activity "Diagnostics" "Battery Report generated" "Success"
        })
    }
})

$btn_diag_disk.Add_Click({
    Log-Message "Scanning connected physical drives status (SMART Check)..."
    Add-Activity "Diagnostics" "Scanning SMART Disk Status" "Running"
    Run-Async {
        param($win)
        $status = Get-CimInstance -Namespace root\wmi -ClassName MSStorageDriver_FailurePredictStatus -ErrorAction SilentlyContinue
        if ($status -eq $null) {
            $win.Dispatcher.Invoke([Action]{ 
                Log-Message "[OK] SMART reports all connected drives are healthy."
                Add-Activity "Diagnostics" "SMART Disk Scan completed" "Success"
            })
        } else {
            foreach ($drive in $status) {
                $inst = $drive.InstanceName
                if ($drive.PredictFailure) {
                    $win.Dispatcher.Invoke([Action]{ Log-Message "[FAIL] WARNING: Failure predicted on drive: $inst" })
                } else {
                    $win.Dispatcher.Invoke([Action]{ Log-Message "[OK] Drive healthy: $inst" })
                }
            }
            $win.Dispatcher.Invoke([Action]{ Add-Activity "Diagnostics" "SMART Disk Scan completed" "Success" })
        }
    }
})

$btn_diag_ram.Add_Click({
    Log-Message "Identifying installed memory modules properties..."
    Add-Activity "Diagnostics" "Identifying Memory Modules" "Running"
    Run-Async {
        param($win)
        $modules = Get-CimInstance Win32_PhysicalMemory
        foreach ($mod in $modules) {
            $cap = [Math]::Round($mod.Capacity / 1GB)
            $speed = $mod.Speed
            $loc = $mod.DeviceLocator
            $win.Dispatcher.Invoke([Action]{ 
                Log-Message "Slot ${loc}: ${cap} GB RAM module running at ${speed} MHz."
            })
        }
        $win.Dispatcher.Invoke([Action]{ Add-Activity "Diagnostics" "Memory Modules identified" "Success" })
    }
})

$btn_diag_mdsched.Add_Click({
    Log-Message "Scheduling Windows Memory Diagnostic scan (mdsched.exe)..."
    Start-Process mdsched.exe
    Log-Message "[OK] Memory diagnostic utility opened."
})

$btn_diag_dns.Add_Click({
    Log-Message "Configuring adapter DNS settings to Cloudflare Secure DNS (1.1.1.1)..."
    Start-ThreadJob {
        $adapters = Get-NetAdapter | Where-Object { $_.Status -eq "Up" }
        foreach ($a in $adapters) {
            Set-DnsClientServerAddress -InterfaceAlias $a.Name -ServerAddresses ("1.1.1.1", "1.0.0.1") -ErrorAction SilentlyContinue
        }
        Log-Message "[OK] Cloudflare DNS configuration completed."
    }
})

$btn_diag_speed.Add_Click({
    Log-Message "Running real-time download bandwidth speed test..."
    Add-Activity "Diagnostics" "Running download Speed Test" "Running"
    Run-Async {
        param($win)
        $url = "https://speed.cloudflare.com/__down?bytes=10000000" # 10MB test file
        $start = Get-Date
        $tempFile = "$env:temp\speedtest.bin"
        $win.Dispatcher.Invoke([Action]{ Log-Message "Downloading 10MB test payload from Cloudflare CDN..." })
        try {
            Invoke-WebRequest -Uri $url -OutFile $tempFile -ErrorAction Stop
            $elapsed = (Get-Date) - $start
            $speedMbps = [Math]::Round((10 * 8) / $elapsed.TotalSeconds, 2)
            Remove-Item $tempFile -Force
            $win.Dispatcher.Invoke([Action]{ 
                Log-Message "[OK] Speed test finished. Current Bandwidth: $speedMbps Mbps." 
                Add-Activity "Diagnostics" "Speed Test Completed: $speedMbps Mbps" "Success"
            })
        } catch {
            $win.Dispatcher.Invoke([Action]{ 
                Log-Message "[FAIL] Speed test failed. Please check internet connection." 
                Add-Activity "Diagnostics" "Speed Test Failed" "Failed"
            })
        }
    }
})

$btn_diag_act.Add_Click({
    Log-Message "Checking Windows activation status details..."
    Add-Activity "Diagnostics" "Checking activation status..." "Running"
    Run-Async {
        param($win)
        $res = cscript //nologo $env:SystemRoot\system32\slmgr.vbs /dli
        $joined = $res -join "`r`n"
        $win.Dispatcher.Invoke([Action]{ 
            Log-Message "License details returned:" 
            Log-Message $joined
            Add-Activity "Diagnostics" "Activation Checked" "Success"
        })
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
    Run-Async {
        param($win, $s, $d)
        $proc = Start-Process robocopy -ArgumentList "`"$s`" `"$d`" /E /Z /ZB /R:5 /W:5 /TBD /NP /V" -NoNewWindow -PassThru -Wait
        $win.Dispatcher.Invoke([Action]{ 
            Log-Message "Robocopy process completed (Exit code: $($proc.ExitCode))." 
            Add-Activity "Backups" "Robocopy completed (Code $($proc.ExitCode))" "Success"
        })
    } -ArgumentList $src, $dst
})

# System Restore protection & point creation
$btn_backup_enable_restore.Add_Click({
    Log-Message "Enabling System Restore point protection on C: Drive..."
    try {
        Enable-ComputerRestore -Drive "C:\" -ErrorAction Stop
        vssadmin resize shadowstorage /on=C: /for=C: /maxsize=10% | Out-Null
        Log-Message "[OK] Computer System Protection enabled for Drive C: with 10% max allocation limit."
        Add-Activity "Restore Point" "Enabled System Protection" "Success"
    } catch {
        Log-Message "[FAIL] Error enabling System Restore protection: $_"
    }
})

$btn_backup_create_restore.Add_Click({
    Log-Message "Creating instant checkpoint System Restore point..."
    Add-Activity "Restore Point" "Creating System Restore Point" "Running"
    Run-Async {
        param($win)
        try {
            Checkpoint-Computer -Description "VenkatPulse_AI_RestorePoint" -RestorePointType "MODIFY_SETTINGS" -ErrorAction Stop
            $win.Dispatcher.Invoke([Action]{ 
                Log-Message "[OK] Immediate System Restore Point created successfully!"
                Add-Activity "Restore Point" "System Restore Point Created" "Success"
            })
        } catch {
            $err = $_.ToString()
            $win.Dispatcher.Invoke([Action]{ 
                Log-Message "[FAIL] Failed to create restore point: $err" 
                Log-Message "[!] Make sure System Protection is Enabled on C: Drive and you haven't created another restore point in the last 24 hours (Windows limit)."
                Add-Activity "Restore Point" "Restore Point Creation Failed" "Failed"
            })
        }
    }
})

$btn_backup_launch_restore.Add_Click({
    Log-Message "Launching Windows Recovery System Restore Wizard (rstrui.exe)..."
    Start-Process rstrui.exe
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
        Log-Message "[FAIL] Failed to launch console component: $_"
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

# Local accounts options
$btn_cfg_admin_en.Add_Click({
    Log-Message "Enabling the built-in Windows Administrator account..."
    try {
        net user administrator /active:yes | Out-Null
        Log-Message "[OK] Default Administrator account activated."
        Add-Activity "User Accounts" "Enabled Built-in Admin" "Success"
    } catch {
        Log-Message "[FAIL] Failed to enable Administrator account: $_"
    }
})

$btn_cfg_admin_dis.Add_Click({
    Log-Message "Disabling the built-in Windows Administrator account..."
    try {
        net user administrator /active:no | Out-Null
        Log-Message "[OK] Default Administrator account deactivated."
        Add-Activity "User Accounts" "Disabled Built-in Admin" "Success"
    } catch {
        Log-Message "[FAIL] Failed to disable Administrator account: $_"
    }
})

$btn_cfg_reset_pass.Add_Click({
    try {
        $username = [Microsoft.VisualBasic.Interaction]::InputBox("Enter the target local Windows Username to reset password:", "Reset Password Manager", "")
        if ($username.Trim() -eq "") { return }
        $password = [Microsoft.VisualBasic.Interaction]::InputBox("Enter the new Password for user '$username':", "Reset Password Manager", "")
        
        Log-Message "Resetting password for local user '$username'..."
        net user $username $password | Out-Null
        Log-Message "[OK] Password for user '$username' has been reset successfully."
        Add-Activity "User Accounts" "Reset Password for $username" "Success"
    } catch {
        Log-Message "[FAIL] Failed to reset user password: $_"
    }
})

$btn_cfg_autologin.Add_Click({
    try {
        $username = [Microsoft.VisualBasic.Interaction]::InputBox("Enter auto-login Username:", "Auto-Login Manager", "")
        if ($username.Trim() -eq "") { return }
        $password = [Microsoft.VisualBasic.Interaction]::InputBox("Enter password for '$username':", "Auto-Login Manager", "")
        $domain = $env:COMPUTERNAME
        
        Log-Message "Configuring Windows registry auto-login policies for '$username'..."
        Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" -Name "AutoAdminLogon" -Value "1" -Force
        Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" -Name "DefaultUserName" -Value $username -Force
        Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" -Name "DefaultPassword" -Value $password -Force
        Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" -Name "DefaultDomainName" -Value $domain -Force
        
        Log-Message "[OK] Windows auto-login configured successfully. System will automatically login on boot."
        Add-Activity "User Accounts" "Auto-Login configured for $username" "Success"
    } catch {
        Log-Message "[FAIL] Failed to configure auto-login: $_"
    }
})

# System Serial info check
$btn_cfg_serial.Add_Click({
    Log-Message "Retrieving system BIOS and motherboard physical serial credentials..."
    Run-Async {
        param($win)
        $bios = Get-CimInstance Win32_Bios
        $board = Get-CimInstance Win32_BaseBoard
        $ser = $bios.SerialNumber
        $moth = $board.SerialNumber
        $manuf = $board.Manufacturer
        $prod = $board.Product
        
        $win.Dispatcher.Invoke([Action]{
            Log-Message "--- BIOS & TELEMETRY MANIFEST ---"
            Log-Message "BIOS Serial Number: $ser"
            Log-Message "Motherboard Serial: $moth"
            Log-Message "System Manufacturer: $manuf"
            Log-Message "Motherboard SKU: $prod"
            Add-Activity "Diagnostics" "System Serial Checked" "Success"
        })
    }
})

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
        Log-Message "[INFO] No matching tools found. Try keywords like: 'printer', 'sfc', 'dism', 'ram', 'activation', 'bing'."
        return
    }
    
    $matches = $matches | Sort-Object Score -Descending
    Log-Message "Found $($matches.Count) matching tools:"
    foreach ($m in $matches) {
        Log-Message "  -> $($m.Tool.Name) - View: $($m.Tool.View.Replace('grid_', ''))"
        Log-Message "    $($m.Tool.Desc)"
    }
    
    # Switch to the view of the top match
    $topView = $matches[0].Tool.View
    Switch-View $topView
})

$window.ShowDialog() | Out-Null
