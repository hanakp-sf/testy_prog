using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Net.Mail;
using System.Text;
using System.Threading.Tasks;

namespace ConsoleApp
{
    public interface IDelivery
    {
        public void send(string message);
    }

    public class Email:IDelivery
    {
        public void send(string message)
        {
            Console.WriteLine($"{message} sent via email");
        }
    }
    class Post : IDelivery
    {
        public void send(string message)
        {
            Console.WriteLine($"{message} sent via post");
        }
    }
    class SMS : IDelivery
    {
        public void send(string message)
        {
            Console.WriteLine($"{message} sent via SMS");
        }
    }
    interface Physical : IDelivery
    {
        public void send(string message)
        {
            Console.WriteLine($"{message} sent physically");
        }
    }

    class ByAirplane : Physical
    {
        public void send(string message)
        {
            Console.WriteLine($"{message} sent by airplane");
        }
    }
    class ByCar : Physical
    {
        public void send(string message)
        {
            Console.WriteLine($"{message} sent by car");
        }
    }

    class NoChannel : IDelivery
    {
        public void send(string message)
        {
            Console.WriteLine($"No channel available");
        }
    }
    class DeliveryFactory()
    {
        static public IDelivery createChannel(string name)
        {
            switch (name)
            {
                case "EMAIL":
                    return new Email();
                case "SMS":
                    return new SMS();
                case "POST":
                    return new Post();
                case "AIRPLANE":
                    return new ByAirplane();
                case "CAR":
                    return new ByCar();
            }
            return new NoChannel();
        }
    }

    class MainClass()
    {
        static public void Main()
        {
            IDelivery a = DeliveryFactory.createChannel("SMS");
            IDelivery b = DeliveryFactory.createChannel("EMAIL");
            IDelivery c = DeliveryFactory.createChannel("CAR");
            IDelivery d = DeliveryFactory.createChannel("AIRPLANE");
            IDelivery e = DeliveryFactory.createChannel("AIR");

            b.send("hello2");
            a.send("hello");
            c.send("hello3");
            d.send("hello4");
            e.send("hello5");
        }
    }


}
