import whois
import requests

def get_whois_info(domain):
    try:
        whois_info = whois.whois(domain)
        return whois_info
    except Exception as e:
        return str(e)

def get_dns_tracking_info(domain):
    api_key = "YOUR_DNS_TRACKING_API_KEY"
    url = f"https://api.dnstracking.com/v1/lookup/{domain}?api_key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to fetch DNS tracking information"}

def preview_whois_info(whois_info):
    preview = ""
    if whois_info:
        preview += f"Domain Name: {whois_info.domain_name}\n"
        preview += f"Registrar: {whois_info.registrar}\n"
        preview += f"Creation Date: {whois_info.creation_date}\n"
        preview += f"Expiration Date: {whois_info.expiration_date}\n"
        preview += f"Name Servers: {', '.join(whois_info.name_servers)}\n"
    return preview

def check_website_legitimacy(domain):
    whois_info = get_whois_info(domain)
    dns_tracking_info = get_dns_tracking_info(domain)
    preview = preview_whois_info(whois_info)
    print(f"WHOIS Information:\n{preview}")
    print(f"DNS Tracking Information:\n{dns_tracking_info}")

if __name__ == "__main__":
    domain = input("Enter a website domain: ")
    check_website_legitimacy(domain)