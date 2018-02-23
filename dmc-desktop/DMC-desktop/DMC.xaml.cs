using System.Windows;
using System.Diagnostics;
using System.Net;
using System.Text;
using System.IO;
using System.Management;
using Newtonsoft.Json;
using System.Collections.Generic;
using System;
using System.Collections;
using System.Windows.Forms;
using System.Reflection;

namespace dmc_desktop
{
    /// <summary>
    /// Interaction logic for DMC.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        const string DMC_SERVER_API_URL = "http://127.0.0.1:5000/api/v1/devices";

        private Process agentProc, serverProc;


        public MainWindow()
        {
            Process[] processes = System.Diagnostics.Process.GetProcessesByName(System.Windows.Forms.Application.ProductName);
            if (processes.Length > 1)
            {
                System.Environment.Exit(1);
            }
            else
            {
                InitializeComponent();
            }
        }

        private void Window_Closing(object sender, System.ComponentModel.CancelEventArgs e) {
            stopAgent();
            stopServer();
        }

        private void AgentButton_Click(object sender, RoutedEventArgs e)
        {
            if (AgentButton.Content.ToString() == "Start Agent") startAgent();
            else stopAgent();
        }

        private void ServerButton_Click(object sender, RoutedEventArgs e)
        {
            if (ServerButton.Content.ToString() == "Start Server") startServer();
            else stopServer();
            
        }

        private void GetDeviceList_Click(object sender, RoutedEventArgs e) {

            if (serverProc != null && !serverProc.HasExited)
            {
                WebRequest request = WebRequest.Create(DMC_SERVER_API_URL);
                // Get the response.
                HttpWebResponse response = (HttpWebResponse)request.GetResponse();
                // Get the stream containing content returned by the server.
                Stream dataStream = response.GetResponseStream();
                // Open the stream using a StreamReader for easy access.
                var reader = new StreamReader(dataStream);
                // Read the content.
                string responseFromServer = reader.ReadToEnd();

                DeviceList devicelist = JsonConvert.DeserializeObject<DeviceList>(responseFromServer);

                //update deivce to listbox
                lbDeviceList.ItemsSource = devicelist.GetList();
                // Cleanup the streams and the response.
                reader.Close();
                dataStream.Close();
                response.Close();
            }
            else {
                lbDeviceList.ItemsSource = null;
            }

        }

        private void startAgent() {
            agentProc = new Process();
            agentProc.StartInfo.FileName = "dmc-agent.exe";
            agentProc.StartInfo.UseShellExecute = false;
            agentProc.StartInfo.CreateNoWindow = true;
            agentProc.Start();
            AgentButton.Content = "Stop Agent";
        }

        private void stopAgent() {
            if (agentProc != null && !agentProc.HasExited)
            {
                KillProcessAndChildren(agentProc.Id);
                agentProc.WaitForExit();
                agentProc = null;
            }
            AgentButton.Content = "Start Agent";
        }

        private void startServer() {
            serverProc = new Process();
            serverProc.StartInfo.FileName = "dmc-server.exe";
            serverProc.StartInfo.UseShellExecute = false;
            serverProc.StartInfo.CreateNoWindow = true;
            serverProc.Start();
            ServerButton.Content = "Stop Server";
        }

        private void stopServer() {
            if (serverProc != null && !serverProc.HasExited)
            {
                KillProcessAndChildren(serverProc.Id);
                serverProc.WaitForExit();
                serverProc = null;

            }
            ServerButton.Content = "Start Server";
        }

        /// <summary>
        /// Kill a process, and all of its children, grandchildren, etc.
        /// </summary>
        /// <param name="pid">Process ID.</param>
        private static void KillProcessAndChildren(int pid)
        {
            ManagementObjectSearcher searcher = new ManagementObjectSearcher
              ("Select * From Win32_Process Where ParentProcessID=" + pid);
            ManagementObjectCollection moc = searcher.Get();
            foreach (ManagementObject mo in moc)
            {
                KillProcessAndChildren(Convert.ToInt32(mo["ProcessID"]));
            }
            try
            {
                Process proc = Process.GetProcessById(pid);
                proc.Kill();
            }
            catch (ArgumentException)
            {
                // Process already exited.
            }
        }

        private void Grid_CellFormatting(object sender, DataGridViewCellFormattingEventArgs e)
        {

            DataGridView grid = (DataGridView)sender;
            DataGridViewRow row = grid.Rows[e.RowIndex];
            DataGridViewColumn col = grid.Columns[e.ColumnIndex];
            if (row.DataBoundItem != null && col.DataPropertyName.Contains("."))
            {
                string[] props = col.DataPropertyName.Split('.');
                PropertyInfo propInfo = row.DataBoundItem.GetType().GetProperty(props[0]);
                object val = propInfo.GetValue(row.DataBoundItem, null);
                for (int i = 1; i < props.Length; i++)
                {
                    propInfo = val.GetType().GetProperty(props[i]);
                    val = propInfo.GetValue(val, null);
                }
                e.Value = val;
            }
        }
    }

    public class DeviceList
    {
        public List<Device> devices { get; set; }

        public List<Device> GetList() {
            return this.devices;
        }

        public override string ToString()
        {
            string str = "";
            foreach (Device d in this.devices)
            {
                str += d.ToString();
            }
            return str;
        }
    }

    public class Device
    {
        public string name { get; set; }
        public string id { get; set; }
        public string udid { get; set; }
        public string uri { get; set; }
        public string version { get; set; }
        public string create_time { get; set; }
        public bool is_auth { get; set; }
        public bool is_active { get; set; }
        public bool is_removed { get; set; }
        public int type { get; set; }
        public Node node { get; set; }
        public Model model { get; set; }
        public status status { get; set; }

        public override string ToString()
        {
            return this.id + ": " + this.name + "at time: "+this.create_time +"\n";
        }
    }

    public class Node {
        public NodeStatus node { get; set; }
        public string cast { get; set; }
        public string host { get; set; }
        public string uri { get; set; }
        public string admin { get; set; }
        public string password { get; set; }
        public string id { get; set; }
        public string detail { get; set; }
    }

    public class NodeStatus {
        public int value { get; set; }
        public string label { get; set; }
    }

    public class Model {
        public int platform { get; set; }
        public string brand { get; set; }
        public string name { get; set; }
        public string size { get; set; }
        public override string ToString()
        {
            return "brand:" + this.brand + "\nsize: "+this.size+"\n";
        }
    }

    public class port {
        public int appium_port { get; set; }
        public int appium_bp_port { get; set; }
        public int vstream_port { get; set; }
        public int wda_port { get; set; }
    }

    public class status {
        public int value { get; set; }
        public string label { get; set; }
    }
}
