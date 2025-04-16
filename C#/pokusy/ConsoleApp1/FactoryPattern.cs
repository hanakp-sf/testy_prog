using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Net.Mail;
using System.Text;
using System.Threading.Tasks;

namespace ConsoleApp
{
    interface IDelivery
    {
        public void send(string message);
    }

    class Email:IDelivery
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

            b.send("hello2");
            a.send("hello");
            c.send("hello3");
        }
    }


}
