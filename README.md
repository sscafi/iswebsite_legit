# Website Legitimacy Checker

=============================

## Overview

The Website Legitimacy Checker is a Python script that uses WHOIS and DNS tracking information to help users determine if a website is legitimate or not. The script fetches WHOIS information for a given website and DNS tracking information from the DNS Tracking API, providing a preview of the WHOIS information to aid in the legitimacy check.

## Features

### WHOIS Information

- Fetches WHOIS information for a given website domain
- Provides a preview of the WHOIS information, including:
  - Domain name
  - Registrar
  - Creation date
  - Expiration date
  - Name servers

### DNS Tracking Information

- Fetches DNS tracking information from the DNS Tracking API
- Displays DNS tracking information, including:
  - IP addresses
  - Location
  - Other relevant details

### Legitimacy Check

- Provides a comprehensive view of the website's WHOIS and DNS tracking information to aid in determining its legitimacy

## Usage

### Requirements

- Python 3.x
- `whois` library (install with `pip install whois`)
- `requests` library (install with `pip install requests`)
- DNS Tracking API key (obtain a free API key by signing up on the DNS Tracking API website)
