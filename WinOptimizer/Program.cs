using System;
using System.Windows.Forms;
using System.Drawing;
using WinOptimizer.Services;
using Newtonsoft.Json;
using System.IO;
using System.Security.Principal;

namespace WinOptimizer
{
    public class Program : Form
    {
        private NotifyIcon? _trayIcon;
        private StandbyMemoryCleaner? _memoryCleaner;
        private ProcessPriorityManager? _priorityManager;
        private SystemServiceController? _serviceController;
        private CPUPowerManager? _cpuPowerManager;
        private CPUStressTest? _stressTest;
        private OptimizerConfig? _config;

        private Label? _statusLabel;
        private Label? _memoryLabel;
        private Label? _cpuLabel;
        private Button? _cleanNowButton;
        private Button? _configButton;
        private TextBox? _logTextBox;
        private Timer? _updateTimer;

        [STAThread]
        static void Main()
        {
            // Verifica privilégios de administrador
            if (!IsAdministrator())
            {
                MessageBox.Show(
                    "Este aplicativo requer privilégios de Administrador.\n\n" +
                    "Por favor, execute como administrador.",
                    "Privilégios Insuficientes",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Warning
                );
                return;
            }

            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new Program());
        }

        public Program()
        {
            InitializeUI();
            LoadConfiguration();
            InitializeServices();
            StartServices();
        }

        private void InitializeUI()
        {
            // Configurações da janela
            Text = "Windows NVMe RAM Optimizer";
            Size = new Size(700, 550);
            StartPosition = FormStartPosition.CenterScreen;
            FormBorderStyle = FormBorderStyle.FixedSingle;
            MaximizeBox = false;

            // Status label
            _statusLabel = new Label
            {
                Text = "🟢 Otimizador Ativo",
                Font = new Font("Segoe UI", 12, FontStyle.Bold),
                Location = new Point(20, 20),
                AutoSize = true
            };
            Controls.Add(_statusLabel);

            // Memory label
            _memoryLabel = new Label
            {
                Text = "RAM Livre: Carregando...",
                Font = new Font("Segoe UI", 10),
                Location = new Point(20, 60),
                AutoSize = true
            };
            Controls.Add(_memoryLabel);

            // CPU label
            _cpuLabel = new Label
            {
                Text = "CPU: Carregando...",
                Font = new Font("Segoe UI", 10),
                Location = new Point(20, 85),
                AutoSize = true
            };
            Controls.Add(_cpuLabel);

            // Clean Now Button
            _cleanNowButton = new Button
            {
                Text = "Limpar Memória Agora",
                Location = new Point(20, 120),
                Size = new Size(200, 35),
                Font = new Font("Segoe UI", 10)
            };
            _cleanNowButton.Click += CleanNowButton_Click;
            Controls.Add(_cleanNowButton);

            // Config Button
            _configButton = new Button
            {
                Text = "⚙️ Configurações",
                Location = new Point(240, 120),
                Size = new Size(150, 35),
                Font = new Font("Segoe UI", 10)
            };
            _configButton.Click += ConfigButton_Click;
            Controls.Add(_configButton);

            // Log TextBox
            var logLabel = new Label
            {
                Text = "Log de Atividades:",
                Font = new Font("Segoe UI", 10, FontStyle.Bold),
                Location = new Point(20, 170),
                AutoSize = true
            };
            Controls.Add(logLabel);

            _logTextBox = new TextBox
            {
                Location = new Point(20, 200),
                Size = new Size(640, 280),
                Multiline = true,
                ScrollBars = ScrollBars.Vertical,
                ReadOnly = true,
                Font = new Font("Consolas", 9),
                BackColor = Color.Black,
                ForeColor = Color.LightGreen
            };
            Controls.Add(_logTextBox);

            // Tray Icon
            _trayIcon = new NotifyIcon
            {
                Icon = SystemIcons.Application,
                Visible = true,
                Text = "Windows Optimizer"
            };
            _trayIcon.DoubleClick += TrayIcon_DoubleClick;

            var trayMenu = new ContextMenuStrip();
            trayMenu.Items.Add("Mostrar", null, (s, e) => ShowWindow());
            trayMenu.Items.Add("Limpar RAM", null, (s, e) => CleanMemoryNow());
            trayMenu.Items.Add("-");
            trayMenu.Items.Add("Sair", null, (s, e) => ExitApplication());
            _trayIcon.ContextMenuStrip = trayMenu;

            // Timer para atualizar UI
            _updateTimer = new Timer { Interval = 2000 };
            _updateTimer.Tick += UpdateTimer_Tick;
            _updateTimer.Start();

            // Minimiza para tray ao fechar
            FormClosing += (s, e) =>
            {
                if (e!.CloseReason == CloseReason.UserClosing)
                {
                    e.Cancel = true;
                    Hide();
                    _trayIcon!.ShowBalloonTip(2000, "Windows Optimizer", 
                        "O otimizador continua rodando em segundo plano", 
                        ToolTipIcon.Info);
                }
            };

            // Logger output
            Logger.LogReceived += (s, e) =>
            {
                if (_logTextBox != null && !_logTextBox.IsDisposed)
                {
                    _logTextBox.Invoke((MethodInvoker)delegate
                    {
                        _logTextBox.AppendText(e!.Message + Environment.NewLine);
                        _logTextBox.SelectionStart = _logTextBox.Text.Length;
                        _logTextBox.ScrollToCaret();
                    });
                }
            };
        }

        private void LoadConfiguration()
        {
            try
            {
                string configPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "Config", "OptimizerConfig.json");
                if (File.Exists(configPath))
                {
                    string json = File.ReadAllText(configPath);
                    _config = JsonConvert.DeserializeObject<OptimizerConfig>(json);
                    Logger.Log("Configuração carregada", "INFO");
                }
                else
                {
                    _config = new OptimizerConfig();
                    Logger.Log("Usando configuração padrão", "INFO");
                }
            }
            catch (Exception ex)
            {
                Logger.Log($"Erro ao carregar config: {ex.Message}", "ERROR");
                _config = new OptimizerConfig();
            }
        }

        private void InitializeServices()
        {
            _memoryCleaner = new StandbyMemoryCleaner(
                _config?.StandbyThresholdMB ?? 1024,
                _config?.StandbyCheckIntervalSeconds ?? 5
            );

            _priorityManager = new ProcessPriorityManager();
            _serviceController = new SystemServiceController();
            _cpuPowerManager = new CPUPowerManager();
            _stressTest = new CPUStressTest();

            Logger.Log("Serviços inicializados", "INFO");
        }

        private void StartServices()
        {
            // Inicia limpador de memória
            if (_config?.StandbyCleanerEnabled ?? false)
            {
                _memoryCleaner?.Start();
            }

            // Inicia gerenciador de prioridades
            _priorityManager?.Start();

            // Aplica regras de processos
            if (_config?.ProcessRules != null)
            {
                foreach (var rule in _config.ProcessRules)
                {
                    if (rule.Enabled)
                    {
                        _priorityManager?.AddRule(new ProcessPriorityManager.ProcessRule
                        {
                            ProcessName = rule.ProcessName,
                            CPUPriority = ProcessPriorityManager.ParsePriority(rule.CPUPriority),
                            IOPriority = ProcessPriorityManager.ParseIOPriority(rule.IOPriority),
                            Enabled = true
                        });
                    }
                }
            }

            // Controla SysMain
            if (_config?.SysMainDisabled ?? false)
            {
                _serviceController?.DisableSysMain();
            }

            Logger.Log("✓ Todos os serviços iniciados", "SUCCESS");
        }

        private void UpdateTimer_Tick(object? sender, EventArgs e)
        {
            try
            {
                // Atualiza info de memória
                var memInfo = _memoryCleaner?.GetMemoryInfo();
                if (memInfo != null && _memoryLabel != null)
                {
                    _memoryLabel.Text = $"RAM Livre: {memInfo.AvailableMB} MB / {memInfo.TotalMB} MB ({100 - memInfo.UsedPercentage}% livre)";
                }

                // Atualiza info de CPU
                if (_cpuPowerManager != null && _cpuLabel != null)
                {
                    float cpuUsage = _cpuPowerManager.GetCPUUsage();
                    double? temp = _cpuPowerManager.GetCPUTemperature();
                    
                    string tempStr = temp.HasValue ? $" | {temp.Value:F1}°C" : "";
                    _cpuLabel.Text = $"CPU: {cpuUsage:F1}%{tempStr}";
                }
            }
            catch { }
        }

        private void CleanNowButton_Click(object? sender, EventArgs e)
        {
            CleanMemoryNow();
        }

        private void CleanMemoryNow()
        {
            long freed = _memoryCleaner?.CleanStandbyMemory() ?? 0;
            MessageBox.Show(
                $"Memória limpa!\n\n{freed / 1024 / 1024} MB liberados",
                "Limpeza Concluída",
                MessageBoxButtons.OK,
                MessageBoxIcon.Information
            );
        }

        private void ConfigButton_Click(object? sender, EventArgs e)
        {
            var configForm = new ConfigurationForm(_config, _cpuPowerManager, _stressTest);
            configForm.ShowDialog();
        }

        private void TrayIcon_DoubleClick(object? sender, EventArgs e)
        {
            ShowWindow();
        }

        private void ShowWindow()
        {
            Show();
            WindowState = FormWindowState.Normal;
            Activate();
        }

        private void ExitApplication()
        {
            _memoryCleaner?.Stop();
            _priorityManager?.Stop();
            _stressTest?.Stop();
            _trayIcon?.Dispose();
            Application.Exit();
        }

        private static bool IsAdministrator()
        {
            var identity = WindowsIdentity.GetCurrent();
            var principal = new WindowsPrincipal(identity);
            return principal.IsInRole(WindowsBuiltInRole.Administrator);
        }
    }

    public class OptimizerConfig
    {
        public bool StandbyCleanerEnabled { get; set; } = true;
        public int StandbyThresholdMB { get; set; } = 1024;
        public int StandbyCheckIntervalSeconds { get; set; } = 5;
        public bool SysMainDisabled { get; set; } = false;
        public ProcessRuleConfig[] ProcessRules { get; set; } = Array.Empty<ProcessRuleConfig>();
    }

    public class ProcessRuleConfig
    {
        public string ProcessName { get; set; } = "";
        public string CPUPriority { get; set; } = "Normal";
        public string IOPriority { get; set; } = "Normal";
        public bool Enabled { get; set; } = false;
    }
}
