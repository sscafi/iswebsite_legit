import tkinter as tk
from tkinter import messagebox
import whois
import requests

class DomainCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Domain Checker")

        # Title Label
        self.title_label = tk.Label(root, text="Domain Checker", font=("Arial", 16))
        self.title_label.pack(pady=10)

        # Domain Entry
        self.domain_label = tk.Label(root, text="Enter a website domain:")
        self.domain_label.pack(pady=5)
        self.domain_entry = tk.Entry(root, width=50)
        self.domain_entry.pack(pady=5)

        # Check Button
        self.check_button = tk.Button(root, text="Check Domain", command=self.check_domain)
        self.check_button.pack(pady=10)

        # Output Text
        self.output_text = tk.Text(root, height=20, width=80)
        self.output_text.pack(pady=10)
        self.output_text.config(state=tk.DISABLED)

    def get_whois_info(self, domain):
        try:
            whois_info = whois.whois(domain)
            return whois_info
        except Exception as e:
            return str(e)

    def get_dns_tracking_info(self, domain):
        api_key = "YOUR_DNS_TRACKING_API_KEY"  # Replace with your actual API key
        url = f"https://api.dnstracking.com/v1/lookup/{domain}?api_key={api_key}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": "Failed to fetch DNS tracking information"}
        except Exception as e:
            return {"error": str(e)}

    def preview_whois_info(self, whois_info):
        preview = ""
        if whois_info:
            preview += f"Domain Name: {whois_info.domain_name}\n"
            preview += f"Registrar: {whois_info.registrar}\n"
            preview += f"Creation Date: {whois_info.creation_date}\n"
            preview += f"Expiration Date: {whois_info.expiration_date}\n"
            preview += f"Name Servers: {', '.join(whois_info.name_servers)}\n"
        return preview

    def check_domain(self):
        domain = self.domain_entry.get()
        if not domain:
            messagebox.showerror("Input Error", "Please enter a domain.")
            return

        whois_info = self.get_whois_info(domain)
        dns_tracking_info = self.get_dns_tracking_info(domain)
        preview = self.preview_whois_info(whois_info)

        output = f"WHOIS Information:\n{preview}\n\nDNS Tracking Information:\n{dns_tracking_info}"
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, output)
        self.output_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = DomainCheckerApp(root)
    root.mainloop()
