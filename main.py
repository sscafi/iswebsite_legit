import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import threading
from services.domain_checker import domain_checker
from utils.logger import logger
from utils.config import config
from utils.validators import validator

class DomainCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Domain Checker")
        self.root.geometry(f"{config.config['ui']['window_width']}x{config.config['ui']['window_height']}")
        self.root.resizable(False, False)

        self.history = []  # In-memory history
        self.last_result_text = ""
        self.last_result_data = None
        self.view_mode = "detailed"  # "summary" or "detailed"

        # Title Label
        self.title_label = tk.Label(root, text="Domain Checker", font=("Arial", 16))
        self.title_label.pack(pady=10)

        # Domain Entry
        self.domain_label = tk.Label(root, text="Enter a website domain:")
        self.domain_label.pack(pady=5)
        self.domain_entry = tk.Entry(root, width=50)
        self.domain_entry.pack(pady=5)

        # Check Button
        self.check_button = tk.Button(root, text="Check Domain", command=self.start_check_domain)
        self.check_button.pack(pady=10)

        # Progress Bar
        self.progress = ttk.Progressbar(root, mode='indeterminate')
        self.progress.pack(pady=5, fill=tk.X, padx=20)
        self.progress.pack_forget()

        # Output Text
        self.output_text = tk.Text(root, height=20, width=80, state=tk.DISABLED)
        self.output_text.pack(pady=10)

        # View Toggle Button
        self.view_toggle_button = tk.Button(root, text="Switch to Summary View", command=self.toggle_view_mode)
        self.view_toggle_button.pack(pady=5)

        # Export/Copy Buttons
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=5)
        self.copy_button = tk.Button(self.button_frame, text="Copy to Clipboard", command=self.copy_to_clipboard)
        self.copy_button.pack(side=tk.LEFT, padx=5)
        self.export_csv_button = tk.Button(self.button_frame, text="Export as CSV", command=self.export_csv)
        self.export_csv_button.pack(side=tk.LEFT, padx=5)
        self.export_pdf_button = tk.Button(self.button_frame, text="Export as PDF", command=self.export_pdf)
        self.export_pdf_button.pack(side=tk.LEFT, padx=5)

        # Risk Score Label
        self.risk_label = tk.Label(root, text="", font=("Arial", 12, "bold"))
        self.risk_label.pack(pady=5)

        # History Listbox
        self.history_label = tk.Label(root, text="History:")
        self.history_label.pack(pady=(10, 0))
        self.history_listbox = tk.Listbox(root, height=5)
        self.history_listbox.pack(pady=5, fill=tk.X, padx=20)
        self.history_listbox.bind('<<ListboxSelect>>', self.on_history_select)

        # Settings Button
        self.menu_frame = tk.Frame(root)
        self.menu_frame.pack(pady=5)
        self.settings_button = tk.Button(self.menu_frame, text="Settings", command=self.open_settings_dialog)
        self.settings_button.pack(side=tk.LEFT, padx=5)

    def start_check_domain(self):
        domain = self.domain_entry.get()
        is_valid, clean_domain = validator.validate_domain(domain)
        if not is_valid:
            messagebox.showerror("Input Error", clean_domain)
            return
        self.progress.pack()
        self.progress.start()
        self.check_button.config(state=tk.DISABLED)
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.risk_label.config(text="")
        threading.Thread(target=self.check_domain, args=(clean_domain,), daemon=True).start()

    def check_domain(self, domain):
        try:
            result = domain_checker.check_domain_comprehensive(domain)
            self.display_result(result)
            self.add_to_history(domain)
        except Exception as e:
            logger.log_error("Domain check failed", e)
            self.show_error(f"Domain check failed: {str(e)}")
        finally:
            self.progress.stop()
            self.progress.pack_forget()
            self.check_button.config(state=tk.NORMAL)

    def add_to_history(self, domain):
        if domain not in self.history:
            self.history.append(domain)
            self.history_listbox.insert(tk.END, domain)
        # Limit history size
        max_history = config.get_setting('max_history', 100)
        if len(self.history) > max_history:
            self.history = self.history[-max_history:]
            self.history_listbox.delete(0, tk.END)
            for d in self.history:
                self.history_listbox.insert(tk.END, d)

    def on_history_select(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            domain = self.history_listbox.get(index)
            self.domain_entry.delete(0, tk.END)
            self.domain_entry.insert(0, domain)
            self.start_check_domain()

    def toggle_view_mode(self):
        if self.view_mode == "detailed":
            self.view_mode = "summary"
            self.view_toggle_button.config(text="Switch to Detailed View")
        else:
            self.view_mode = "detailed"
            self.view_toggle_button.config(text="Switch to Summary View")
        
        # Redisplay the last result with the new view mode
        if self.last_result_data:
            self.display_result(self.last_result_data)

    def display_result(self, result):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        if 'error' in result:
            self.output_text.insert(tk.END, f"Error: {result['error']}\n")
            self.risk_label.config(text="")
            self.last_result_text = f"Error: {result['error']}\n"
            self.last_result_data = None
        else:
            if self.view_mode == "summary":
                result_text = self.generate_summary_view(result)
            else:
                result_text = self.generate_detailed_view(result)
            
            self.output_text.insert(tk.END, result_text)
            self.last_result_text = result_text
            self.last_result_data = result
        self.output_text.config(state=tk.DISABLED)

    def generate_summary_view(self, result):
        checks = result.get('checks', {})
        output = []
        output.append(f"Domain: {result.get('domain')}")
        output.append(f"Checked at: {result.get('timestamp')}")
        output.append("")
        
        # Risk Score (prominent)
        risk_score = result.get('risk_score', 0)
        risk_level = result.get('risk_level', 'Unknown')
        output.append(f"Risk Level: {risk_level} ({risk_score}/100)")
        output.append("")
        
        # Key metrics
        output.append("Key Metrics:")
        
        # Domain age
        age = checks.get('age', {})
        if age.get('success'):
            age_days = age.get('age_days', 'N/A')
            output.append(f"  • Domain Age: {age_days} days")
        
        # DNS resolution
        dns = checks.get('dns', {})
        if dns.get('success'):
            resolves = "Yes" if dns.get('resolves') else "No"
            output.append(f"  • DNS Resolves: {resolves}")
            if dns.get('ip'):
                output.append(f"  • IP Address: {dns.get('ip')}")
        
        # SSL certificate
        sslc = checks.get('ssl', {})
        if sslc.get('success'):
            valid = "Valid" if sslc.get('valid') else "Invalid"
            output.append(f"  • SSL Certificate: {valid}")
            if sslc.get('days_until_expiry'):
                days = sslc.get('days_until_expiry')
                if days < 30:
                    output.append(f"  • SSL Expires: {days} days (WARNING)")
                else:
                    output.append(f"  • SSL Expires: {days} days")
        
        # Suspicious indicators
        suspicious = checks.get('suspicious', {})
        if suspicious.get('success'):
            count = suspicious.get('count', 0)
            output.append(f"  • Suspicious Indicators: {count}")
            if count > 0:
                for ind in suspicious.get('indicators', [])[:3]:  # Show first 3
                    output.append(f"    - {ind['description']}")
                if count > 3:
                    output.append(f"    ... and {count - 3} more")
        
        # Blacklist status
        blacklist = checks.get('blacklist', {})
        if blacklist.get('success'):
            results = blacklist.get('results', {})
            listed_count = sum(1 for r in results.values() if isinstance(r, dict) and r.get('listed'))
            if listed_count > 0:
                output.append(f"  • Blacklisted: Yes ({listed_count} services)")
            else:
                output.append("  • Blacklisted: No")
        
        # Malware detection
        malware = checks.get('malware', {})
        if malware.get('success'):
            detected = malware.get('detected', 0)
            total = malware.get('total', 0)
            if detected > 0:
                output.append(f"  • Malware Detected: {detected}/{total}")
            else:
                output.append("  • Malware Detected: None")
        
        # Social media presence
        social = checks.get('social', {})
        if social.get('success'):
            active = social.get('active_platforms', 0)
            total = social.get('total_platforms', 0)
            output.append(f"  • Social Media: {active}/{total} platforms")
        
        return '\n'.join(output)

    def generate_detailed_view(self, result):
        checks = result.get('checks', {})
        output = []
        output.append(f"Domain: {result.get('domain')}")
        output.append(f"Checked at: {result.get('timestamp')}")
        output.append("")
        # WHOIS
        whois = checks.get('whois', {})
        if whois.get('success'):
            output.append("WHOIS Info:")
            for k, v in whois.get('data', {}).items():
                output.append(f"  {k}: {v}")
        else:
            output.append(f"WHOIS Error: {whois.get('error', 'N/A')}")
        output.append("")
        # DNS
        dns = checks.get('dns', {})
        if dns.get('success'):
            output.append(f"DNS Resolves: {dns.get('resolves', False)}")
            if dns.get('ip'):
                output.append(f"IP Address: {dns.get('ip')}")
        else:
            output.append(f"DNS Error: {dns.get('error', 'N/A')}")
        output.append("")
        # SSL
        sslc = checks.get('ssl', {})
        if sslc.get('success'):
            output.append(f"SSL Valid: {sslc.get('valid', False)}")
            output.append(f"SSL Expires: {sslc.get('expires', 'N/A')}")
            output.append(f"Days Until Expiry: {sslc.get('days_until_expiry', 'N/A')}")
        else:
            output.append(f"SSL Error: {sslc.get('error', 'N/A')}")
        output.append("")
        # Age
        age = checks.get('age', {})
        if age.get('success'):
            output.append(f"Domain Age: {age.get('age_days', 'N/A')} days ({age.get('age_years', 'N/A')} years)")
            output.append(f"Creation Date: {age.get('creation_date', 'N/A')}")
        else:
            output.append(f"Domain Age Error: {age.get('error', 'N/A')}")
        output.append("")
        # Suspicious
        suspicious = checks.get('suspicious', {})
        if suspicious.get('success'):
            output.append(f"Suspicious Indicators: {suspicious.get('count', 0)}")
            for ind in suspicious.get('indicators', []):
                output.append(f"  - {ind['description']} (Severity: {ind['severity']})")
        else:
            output.append(f"Suspicious Check Error: {suspicious.get('error', 'N/A')}")
        output.append("")
        # Blacklist
        blacklist = checks.get('blacklist', {})
        if blacklist.get('success'):
            output.append(f"Blacklist Results:")
            for service, res in blacklist.get('results', {}).items():
                output.append(f"  {service}: {res}")
        else:
            output.append(f"Blacklist Error: {blacklist.get('error', 'N/A')}")
        output.append("")
        # Malware
        malware = checks.get('malware', {})
        if malware.get('success'):
            output.append(f"Malware Detections: {malware.get('detected', 0)} / {malware.get('total', 0)}")
            output.append(f"Scan Date: {malware.get('scan_date', 'N/A')}")
            output.append(f"Report: {malware.get('permalink', 'N/A')}")
        else:
            output.append(f"Malware Check Error: {malware.get('error', 'N/A')}")
        output.append("")
        # Social
        social = checks.get('social', {})
        if social.get('success'):
            output.append(f"Social Media Presence: {social.get('active_platforms', 0)} / {social.get('total_platforms', 0)}")
            for platform, present in social.get('presence', {}).items():
                output.append(f"  {platform}: {'Yes' if present else 'No'}")
        else:
            output.append(f"Social Check Error: {social.get('error', 'N/A')}")
        output.append("")
        # Risk
        risk_score = result.get('risk_score', 0)
        risk_level = result.get('risk_level', 'Unknown')
        output.append(f"Risk Score: {risk_score} / 100")
        output.append(f"Risk Level: {risk_level}")
        self.risk_label.config(text=f"Risk: {risk_level} ({risk_score}/100)")
        return '\n'.join(output)

    def copy_to_clipboard(self):
        if self.last_result_text:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.last_result_text)
            messagebox.showinfo("Copied", "Result copied to clipboard.")
        else:
            messagebox.showwarning("No Result", "No result to copy.")

    def export_csv(self):
        import csv
        if not self.last_result_data:
            messagebox.showwarning("No Result", "No result to export.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        try:
            checks = self.last_result_data.get('checks', {})
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Section", "Key", "Value"])
                for section, data in checks.items():
                    if isinstance(data, dict):
                        for k, v in data.items():
                            writer.writerow([section, k, v])
                    else:
                        writer.writerow([section, "", data])
            messagebox.showinfo("Exported", f"Result exported to {file_path}")
        except Exception as e:
            logger.log_error("CSV export failed", e)
            messagebox.showerror("Export Error", f"Failed to export CSV: {str(e)}")

    def export_pdf(self):
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
        except ImportError:
            messagebox.showerror("Missing Dependency", "reportlab is required for PDF export. Please install it.")
            return
        if not self.last_result_text:
            messagebox.showwarning("No Result", "No result to export.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not file_path:
            return
        try:
            c = canvas.Canvas(file_path, pagesize=letter)
            width, height = letter
            lines = self.last_result_text.split('\n')
            y = height - 40
            for line in lines:
                c.drawString(40, y, line)
                y -= 15
                if y < 40:
                    c.showPage()
                    y = height - 40
            c.save()
            messagebox.showinfo("Exported", f"Result exported to {file_path}")
        except Exception as e:
            logger.log_error("PDF export failed", e)
            messagebox.showerror("Export Error", f"Failed to export PDF: {str(e)}")

    def show_error(self, message):
        messagebox.showerror("Error", message)

    def open_settings_dialog(self):
        settings_win = tk.Toplevel(self.root)
        settings_win.title("Settings")
        settings_win.geometry("400x350")
        settings_win.resizable(False, False)

        # API Keys
        tk.Label(settings_win, text="API Keys", font=("Arial", 12, "bold")).pack(pady=(10, 0))
        tk.Label(settings_win, text="DNS Tracking API Key:").pack(anchor='w', padx=20)
        dns_entry = tk.Entry(settings_win, width=40)
        dns_entry.pack(padx=20)
        dns_entry.insert(0, config.get_api_key('dns_tracking'))

        tk.Label(settings_win, text="VirusTotal API Key:").pack(anchor='w', padx=20)
        vt_entry = tk.Entry(settings_win, width=40)
        vt_entry.pack(padx=20)
        vt_entry.insert(0, config.get_api_key('virustotal'))

        tk.Label(settings_win, text="AbuseIPDB API Key:").pack(anchor='w', padx=20)
        abuse_entry = tk.Entry(settings_win, width=40)
        abuse_entry.pack(padx=20)
        abuse_entry.insert(0, config.get_api_key('abuseipdb'))

        # Preferences
        tk.Label(settings_win, text="Preferences", font=("Arial", 12, "bold")).pack(pady=(15, 0))
        dark_mode_var = tk.BooleanVar(value=config.get_setting('dark_mode', False))
        analytics_var = tk.BooleanVar(value=config.get_setting('enable_analytics', False))
        crash_var = tk.BooleanVar(value=config.get_setting('enable_crash_reporting', False))
        auto_update_var = tk.BooleanVar(value=config.get_setting('auto_update', True))

        dark_mode_cb = tk.Checkbutton(settings_win, text="Enable Dark Mode", variable=dark_mode_var)
        dark_mode_cb.pack(anchor='w', padx=20)
        analytics_cb = tk.Checkbutton(settings_win, text="Enable Analytics", variable=analytics_var)
        analytics_cb.pack(anchor='w', padx=20)
        crash_cb = tk.Checkbutton(settings_win, text="Enable Crash Reporting", variable=crash_var)
        crash_cb.pack(anchor='w', padx=20)
        auto_update_cb = tk.Checkbutton(settings_win, text="Enable Auto Update", variable=auto_update_var)
        auto_update_cb.pack(anchor='w', padx=20)

        def save_settings():
            config.set_api_key('dns_tracking', dns_entry.get().strip())
            config.set_api_key('virustotal', vt_entry.get().strip())
            config.set_api_key('abuseipdb', abuse_entry.get().strip())
            config.set_setting('dark_mode', dark_mode_var.get())
            config.set_setting('enable_analytics', analytics_var.get())
            config.set_setting('enable_crash_reporting', crash_var.get())
            config.set_setting('auto_update', auto_update_var.get())
            messagebox.showinfo("Settings Saved", "Settings have been updated.")
            settings_win.destroy()
            # Optionally, apply dark mode immediately
            if dark_mode_var.get():
                self.apply_dark_mode()
            else:
                self.apply_light_mode()

        save_btn = tk.Button(settings_win, text="Save", command=save_settings)
        save_btn.pack(pady=15)

    def apply_dark_mode(self):
        # Basic dark mode styling
        self.root.configure(bg="#222")
        for widget in self.root.winfo_children():
            try:
                widget.configure(bg="#222", fg="#eee")
            except:
                pass
        self.output_text.configure(bg="#222", fg="#eee", insertbackground="#eee")

    def apply_light_mode(self):
        # Basic light mode styling
        self.root.configure(bg="#f0f0f0")
        for widget in self.root.winfo_children():
            try:
                widget.configure(bg="#f0f0f0", fg="#222")
            except:
                pass
        self.output_text.configure(bg="#fff", fg="#222", insertbackground="#222")

if __name__ == "__main__":
    root = tk.Tk()
    app = DomainCheckerApp(root)
    root.mainloop()
