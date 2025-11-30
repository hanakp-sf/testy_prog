using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using System.Threading.Tasks;

namespace ConsoleApp
{
    public class Simple
    {
        public static void ShowEnvKeyValue()
        {
            string VarName = "MyMessage";

            Console.WriteLine($"Key={VarName}, Value={Environment.GetEnvironmentVariable(VarName)}");
        }
        public static void MoveDate()
        {
            var dt = DateTime.UtcNow;
            var dtMonths = dt.AddMonths(-3);
            var dtDays = dt.AddDays(-92);

            Console.WriteLine($"Date={dt}, Back3months={dtMonths:yyyy-MM-dd}, Back92days={dtDays:yyyy-MM-dd}");
        }

        public static void testConvert()
        {
            var value = 0.00;
            string item = "-0.009999999776482582";

            value = Math.Round(Convert.ToDouble(item), 0);

            Console.WriteLine($"{value}");
        }


    }
    public class Pokusy
    {
        public static void Select()
        {
            List<Reading> lst =
            [ new Reading() { ID = 1,Name = "aa",Value = "1.23"},
            new Reading() { ID = 2,Name = "bb",Value = "3.23"},
            ];

            var slr = lst.Select(d => d.Name).ToList();

            Console.WriteLine("Select: 1 field");

            foreach (string? obj in slr)
            {
                Console.WriteLine($"{obj}");
            }

            Console.WriteLine("Select: 2 fields");

            foreach (var obj in lst.Select(d => new { d.ID, d.Name }))
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
            Console.WriteLine($"\n{groupByNameQuery}");
            foreach (var yearGroup in groupByNameQuery)
            {
                Console.WriteLine($"Key: {yearGroup.Key}");
                Console.WriteLine($"\tComplete entry: {yearGroup}");
                Console.WriteLine($"\tEntry per properties:");
                foreach (Reading r in yearGroup)
                    Console.WriteLine($"\t\t{r.ID}, {r.Name}, {r.Value}");
                Console.WriteLine($"\tEntry after serialization:");
                Console.WriteLine($"\t\t{JsonConvert.SerializeObject(yearGroup)}");
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

        public static void Distinct()
        {
            /* Objekty ( tu Reading() ) musia mat implementovane IEquatable<Reading>
             */
            List<Reading> lst =
            [ new Reading() { ID = 1, Name = "aa", Value = "1.23"},
            new Reading() { ID = 2, Name = "bb", Value = "3.23"},
            new Reading() { ID = 3, Name = "bd", Value = "10.23"},
            new Reading() { ID = 2, Name = "bb", Value = "3.23"},
            new Reading() { ID = 3, Name = "bd", Value = "3.23"},
            ];

            // Variable distinctNameQuery is an IEnumerable<IGrouping<string,
            // DataClass.Reading>>.
            var distinctNameQuery = lst.Distinct();

            foreach (Reading? obj in lst)
            {
                Console.WriteLine($"{obj.ID}, {obj.Name}, {obj.Value}");
            }

            Console.WriteLine("\nDistinct results:");
            Console.WriteLine("As List");
            foreach (var r in lst.Distinct().ToList())
            {
                Console.WriteLine($"ID: {r.ID}, Name: {r.Name}, Value: {r.Value}");
            }


            Console.WriteLine("As IEnumerable");
            foreach (var r in distinctNameQuery)
            {
                Console.WriteLine($"ID: {r.ID}, Name: {r.Name}, Value: {r.Value}");
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
            for (int i = 0; i < a.Length; i++)
            {
                Console.WriteLine(a[i]);
            };
        }

        public static void StringCompare(string a, string b)
        {
            Console.WriteLine($@"Input: '{a}' '{b}'");
            if (a == b)
                Console.WriteLine("\t ==: rovna sa");
            else
                Console.WriteLine("\t ==: nerovna sa");

            if (a.Equals(b))
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
            var mx2 = lst.Max(r => { bool se = Int64.TryParse(r.Value, out long a); return se ? a : -1; });
            Console.WriteLine($"Max(no conversion): {mx1}\tMax(conversion to int64): {mx2}");
        }

        public static void ParallelLoop()
        {
            object sync = new object();
            int sum = 0;
            Parallel.For(1, 1000, (i) =>
            {
                //lock (sync) sum = sum + i; // lock is necessary
                int loc = 0;

                loc = i;
                lock (sync) sum += loc;
                // As a practical matter, ensure this `parallel for` executes
                // on multiple threads by simulating a lengthy operation.
                Thread.Sleep(1);
            });
            Console.WriteLine("Correct answer should be 499500.  sum is: {0}", sum);
        }
    }
    public class Reading : IEquatable<Reading>
    {
        public int ID { get; set; }
        public string Name { get; set; }
        public string Value { get; set; }

        public bool Equals(Reading? other)
        {
            //Check whether the compared object is null.
            if (Object.ReferenceEquals(other, null)) return false;

            //Check whether the compared object references the same data.
            if (Object.ReferenceEquals(this, other)) return true;

            //Check whether the reading's properties are equal.
            return ID.Equals(other.ID) && Name.Equals(other.Name) && Value.Equals(other.Value);
        }
        public override int GetHashCode()
        {
            //Get hash code for the Name field.
            int hashName = Name.GetHashCode();

            //Get hash code for the ID field.
            int hashCode = ID.GetHashCode();

            //Get hash code for the ID field.
            int hashValue = Value.GetHashCode();

            //Calculate the hash code for the product.
            return hashName ^ hashCode ^ hashValue;
        }
    }

    public class EncryptDecrypt
    {
        public static string Encrypt(string data, RSAParameters rsaParameters)
        {
            using (var rsaCryptoServiceProvider = new RSACryptoServiceProvider())
            {
                rsaCryptoServiceProvider.ImportParameters(rsaParameters);
                var byteData = Encoding.UTF8.GetBytes(data);
                var encryptedData = rsaCryptoServiceProvider.Encrypt(byteData, false);
                return Convert.ToBase64String(encryptedData);
            }
        }
        public static string Decrypt(string cipherText, RSAParameters rsaParameters)
        {
            using (var rsaCryptoServiceProvider = new RSACryptoServiceProvider())
            {
                var cipherDataAsByte = Convert.FromBase64String(cipherText);
                rsaCryptoServiceProvider.ImportParameters(rsaParameters);
                var encryptedData = rsaCryptoServiceProvider.Decrypt(cipherDataAsByte, false);
                return Encoding.UTF8.GetString(encryptedData);
            }
        }

        public static string EncryptObfuscate(string data)
        {
            byte xorConstant = 0x53;
            byte[] byteData = Encoding.UTF8.GetBytes(data);
            for (int i = 0; i < byteData.Length; i++)
            {
                byteData[i] = (byte)(byteData[i] ^ xorConstant);
            }
            return Convert.ToBase64String(byteData);
        }
        public static string DecryptObfuscate(string cipherText)
        {
            byte xorConstant = 0x53;
            byte[] cipherDataAsByte = Convert.FromBase64String(cipherText);
            for (int i = 0; i < cipherDataAsByte.Length; i++)
            {
                cipherDataAsByte[i] = (byte)(cipherDataAsByte[i] ^ xorConstant);
            }
            return Encoding.UTF8.GetString(cipherDataAsByte);
        }

        public static string GetDecryptXML(bool isRequired)
        {
            var pXML = string.Empty;
            if (isRequired)
            {
                pXML = "bwEAEhg2KgUyPyY2bW8ePDcmPyYgbWArNyoVPxw+C2MZIBoCPmUjESMfZRQ5YisiKTU4AGMXBDkrOTgAGyIbZjliZTwVHhI5NhAcfAEZAgQdA2UYCxw5IhQGC2EKAD8DZCs8Bx8pF2Y+Gz0RGWcqKmIwJxcDFipnGBEwORkjHQUHJTcLJDsSIx8iMAV8GzIHeCAYPmYKICVmZCR4ACQgPAdmBwFhFGQyAikZAhIkYBoaIQp4NWMBYhYXHjIrNGsCPSU/J2YaPT8DI2scZjcGKhpjKmUqNGchGxgCB2pgGGQdEmcrGB0pGRwFaxskfAEpETsVeCRmK2QLNCoJPRk+ATEZMAkZKmAmYDRmCR0wHRkpGyQ8A2YCKyMdOAMFCxIgCTwQAj4RYgIBCzAeZxQ2MhYAFCckJTw1MQsFN2obAxs+OBR8PWA6ByYVFAkHHBBiORA6ND4xYCc2MGscJDphFDsiYxcbMjwSOGIEAm5ub3wePDcmPyYgbW8WKyM8PTY9J20SAhIRb3wWKyM8PTY9J21vA214JiopBjEWPBkrEAk1fCAxP2MeZjRjIGsxOhBmOj0dPik9BDAhFjg4Nhs7ahY+GykCAR8cAxQACxkpJmsqeDYRFQFqHD03KWMgBT0RFAdkYDwDF2I1HwE6ETApPRwbYwAROTU+AjUqYhgSNRh4ACJnFBw0ASN4PSBrFAtlARk2OhckIGYLEgkgGSQHOwlhJxYdKQcHCQQSNjwFMR0iFRQwKjtmJWsbYGtqYyBub3wDbW8CbWdmIjVgFXgUHzEbEDAXC2EWfDxmNDcRARIJZCspJ2MKNxw9PTUnMisKFh1lBQQVYGAYAQoyFh8kYQs0KQJlFBRrJxkrB2USYzBiBB83NWQHGz8UImA8OSUBOmEAEjo2ZgEpEGo2FjQ0NCNnMTlrO2IROTs+MBA/PD1mMCQ7ZSICBBsEJmYwNx8/eBlhahQKHDYJAQsZESs2awkDNgdqNmAdAzYQPSsFOGVhIG5vfAJtbxcDbRQfNTw4OCYJCgN8GT1jPT8FNj8BMgEEPAE/FhBqOzoKHhJmYngYHzFkHBorIXwLPhwYIQk/Oj8qPj0fAhc+Cj1hAAcGCjA6ZTA7ZzcLZjceCwkJNRQaGx47OQsRHgU3NCsqJBg6IAQAHiU3ATlhPDdlGQopZiRlIAIYGR8bADIqYRc6GGI1YCF4CiQZOhVlAiQxamUwZTwwBD87IiY0GgIZfDgbPTUVHwY5Fm5vfBcDbW8XAm0UFDsKOxUFIhQ5AQlhCTIlYxwqNDs7ahZjGSYmZSECORdjMgQaGHxqBwo/JmsCFhQpCmUQAxokAR4SFhtgPwcCFXwaOwsZKjc0YhcVGWpnJWAyK2sEPjkgYHgEZBkiNBdnPRgXPSQJahU0BxQ7eBcXAHgnZzAeMRIRC2NqGiRqBzBhOB8LGxcUYj1kNiIgZARqPCEVYAoFagQCGGEwGxVqPBErZWMLKhVhNDhub3wXAm1vGj0lNiEgNgJtCQcaJCMZIgoLawYdBDkDPwceMDBlFRAmIWUHEWMyZCoCBDYQADQRIB4QEB9kGydrGzFhBCcKJCY2NXhqaiN4CyY6BTs4eB0bax0WPwYpYikmY2NnYmVkADo7OgVqPSF4YBFqCxZkNDUmYiAFMDcXP2syCxUWOiopFTpiNxsFZDkSATAQERgJBT45IQU5GgcXCmtnKSEwMRUlHzRjJRomPAIhIgsfMSsLOWUWbm98Gj0lNiEgNgJtbxdtPyQrB2IyAjE4GhspPTgxJxUDFicVOwoQYSchJTwUMXgpKzlhAwApNgcHOhwkGRVrJjl4FR4HKR4KHwkqAmNnGgU1EmF4PAAgZDpkByQFCipiNCQKOD4yZAsYYBERa2AZChEFOSYwHRAWITAaBydlBSMrYmsUAz8VPzsROTEbHmsaAGIUagcYOxkYYGprNgQ3FSA1GwcHBjBnEBEcMiNhETYgJSoCImVmFhU/ImFrERwKByYeOWAHMmUEMgcXFwoxHhcUEhA7ZwYDAzYnPQQJGTkpChYjOCYDNxImMnwQPiEdZjdnFiMfATsefBphNzUxHgoSZxIlAzEWA2QANRQpH2sZBwEcYTYyeAUfIBBjfHgFZAIAOBQgeAEGJmUJKjs1fCcFCWQ4O2slYCN4GgQrBwEfJBhqHzIAORkXATA+IwsWKSMnMAF8fBE9YDwVIT4UEjUZFjcCbm5vfBdtb3wBABIYNioFMj8mNm0=";
            }
            return pXML;
        }

        public static void CustomDecrypt(string enc)
        {
            var rsa = new RSACryptoServiceProvider(2048);
            var pXML = EncryptDecrypt.GetDecryptXML(true);
            var pDecryptXML = EncryptDecrypt.DecryptObfuscate(pXML);
            rsa.FromXmlString(pDecryptXML);

            Console.WriteLine(EncryptDecrypt.Decrypt(enc, rsa.ExportParameters(true)));
        }

    }
}
