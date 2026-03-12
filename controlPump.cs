using System;
using System.IO.Ports;

class Program
{
    static void Main()
    {
        SerialPort port = new SerialPort("/dev/ttyUSB0", 9600);

        port.Open();

        port.Write("/1ZR\r");   // example initialize command
        string response = port.ReadLine();

        Console.WriteLine(response);

        port.Close();
    }
}