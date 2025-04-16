using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;

namespace ConsoleApp
{
    public class Pokusy
    {
        public static void Select()
        {
            List<Reading> lst =
            [ new Reading() { ID = 1,Name = "aa",Value = "1.23"},
            new Reading() { ID = 2,Name = "bb",Value = "3.23"},
            ];

            var slr = lst.Select(d => d.Name).ToList();

            foreach (string? obj in slr)
            {
                Console.WriteLine($"{obj}");
            }
        }
        public static void Where()
        {
            List<Reading> lst =
            [ new Reading() { ID = 1,Name = "aa",Value = "1.23"},
            new Reading() { ID = 2,Name = "bb",Value = "3.23"},
            ];

            var wh = lst.Where(d => d.ID > 1).ToList();

            foreach (Reading? obj in wh)
            {
                Console.WriteLine($"{obj.ID}");
            }
        }

        public static void FirstDefault()
        {
            List<Reading> lst =
            [ new Reading() { ID = 1,Name = "aa",Value = "1.23"},
            new Reading() { ID = 2,Name = "bb",Value = "3.23"},
            new Reading() { ID = 3,Name = "bd",Value = "10.23"},
            ];

            var foundReading = lst.OrderByDescending(d => d.Name).FirstOrDefault(d => d.ID < 3,
                new() { ID = -1, Name = "def", Value = "0.00" });

            Console.WriteLine($"{foundReading.ID}, {foundReading.Name}, {foundReading.Value}");

        }

        public static void GroupBy()
        {
            List<Reading> lst =
            [ new Reading() { ID = 1, Name = "aa", Value = "1.23"},
            new Reading() { ID = 2, Name = "bb", Value = "3.23"},
            new Reading() { ID = 3, Name = "bd", Value = "10.23"},
            new Reading() { ID = 4, Name = "aa", Value = "-1.23"},
            new Reading() { ID = 5, Name = "bd", Value = "3.23"},
            ];

            // Variable groupByLastNamesQuery is an IEnumerable<IGrouping<string,
            // DataClass.Reading>>.
            var groupByNameQuery = lst
                .GroupBy(student => student.Name)
                .OrderBy(newGroup => newGroup.Key);

            foreach (Reading? obj in lst)
            {
                Console.WriteLine($"{obj.ID}, {obj.Name}, {obj.Value}");
            }

            Console.WriteLine("\nGroupby results:");
            foreach (var yearGroup in groupByNameQuery)
            {
                Console.WriteLine($"Key: {yearGroup.Key}");
                foreach (Reading r in yearGroup)
                    Console.WriteLine($"\t{r.ID}, {r.Name}, {r.Value}");
            }


            List<IGrouping<string, Reading>> AsList = lst
                .GroupBy(student => student.Name)
                .OrderBy(newGroup => newGroup.Key).ToList();

            Console.WriteLine("As List");
            foreach (var grp in AsList)
            {
                Console.WriteLine($"{grp.Key}");
                foreach (Reading obj in grp)
                    Console.WriteLine($"\t{obj.ID}, {obj.Name}, {obj.Value}");
            }

        }

        public static void CompareDbNull()
        {
            var sr = 1 > 0 ? (object)DBNull.Value : "str1";


            if (sr.ToString() != "str1")
            {
                Console.WriteLine("ne rovna sa");
            }

            Console.WriteLine(sr.ToString());
        }
        public static void Conv()
        {
            var value = 1.00;
            string a = "";

            value = Convert.ToDouble("6.34E-4") * 1000;
            a = $"{value.ToString("F3")}";
            Console.WriteLine(a);
        }
        public static void LoopArray()
        {
            string[] a = new string[2];

            a[0] = "druhy";
            a[1] = "prvy";

            /*
            foreach (string str in a) {
                Console.WriteLine(str);
            }
            */
            for (int i = 0; i < a.Length; i++) {
                Console.WriteLine(a[i]);
            };
        }

        public static void StringCompare(string a, string b) {
            Console.WriteLine($@"Input: '{a}' '{b}'");
            if (a == b)
                Console.WriteLine("\t ==: rovna sa");
            else
                Console.WriteLine("\t ==: nerovna sa");

            if (a.Equals( b ))
                Console.WriteLine("\t Equals: rovna sa");
            else
                Console.WriteLine("\t Equals: nerovna sa");

            if (a.Equals(b, StringComparison.OrdinalIgnoreCase))
                Console.WriteLine("\t Equals+IgnoreCase: rovna sa");
            else
                Console.WriteLine("\t Equals+IgnoreCase: nerovna sa");
        }

        public static void MaxString()
        {
            List<Reading> lst =
            [ new Reading() { ID = 1,Name = "cc",Value = "11"},
            new Reading() { ID = 2,Name = "aa",Value = "10"},
            new Reading() { ID = 2,Name = "bb",Value = "9"}
            ];

            

            foreach (Reading? obj in lst)
            {
                Console.WriteLine($"{obj.Name}, {obj.Value}");
            }

            var mx1 = lst.Max(r => r.Value);
            var mx2 = lst.Max(r => { bool se = Int64.TryParse(r.Value, out long a); return se ? a:-1;});
            Console.WriteLine($"Max(no conversion): {mx1}\tMax(conversion to int64): {mx2}");
        }
    }
    public class Reading
    {
        public int ID { get; set; }
        public string Name { get; set; }
        public string Value { get; set; }
    }
}
