from flask import Flask, request, jsonify , render_template
from flask_cors import CORS
import subprocess
import shutil  #  Import shutil to check if Nmap exists
import re  # Import regex module for filtering open ports
import requests  # ✅ Import requests to fetch headers
from data_base import init_db, get_db_session , CompanyInfo, Vulnerabilities, runExtraQueries
import os
import json 
import subprocess
from urllib.parse import urljoin
from urllib.parse import urlparse
import multiprocessing
import time
import os
from datetime import datetime
import socket
import requests
import whois
# from yourmodule import save_scan_result  



'''
from sqlalchemy import create_engine;
from typing import List
from typing import Optional
# from sqlalchemy import ForeignKey
# from sqlalchemy import String
# from sqlalchemy.orm import DeclarativeBase
# from sqlalchemy.orm import Mapped
# from sqlalchemy.orm import mapped_column
# from sqlalchemy.orm import relationship
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON




Base = declarative_base()



# Define the CompanyInfo model
class CompanyInfo(Base):
    __tablename__ = 'company_info'

    id = Column(Integer, primary_key=True, autoincrement=True)
    temp_id = Column(Integer, unique=True, nullable=False)
    company_name = Column(String(255), nullable=True,default="Unknown")
    email = Column(String(255), nullable=True, unique=False)
    url = Column(String(255), nullable=True)

    def __repr__(self):
        return f"<CompanyInfo(id={self.id}, company_name={self.company_name}, email={self.email})>"

# Define the Vulnerability model
class Vulnerabilities(Base):
    __tablename__ = 'vulnerabilities'

    company_id = Column(Integer, ForeignKey('company_info.id'), primary_key=True)  # Foreign Key & Primary Key
    missing_headers = Column(JSON, nullable=True)  # JSON type for missing headers
    ports = Column(JSON, nullable=True)  # Port field as a string, or Integer if you prefer
    version_vulnerabilities = Column(JSON, nullable=True)  # ✅ Store version-based vulnerabilities


    # Define the relationship to CompanyInfo
    company = relationship("CompanyInfo", backref="vulnerabilities")

    def __repr__(self):
        return f"<Vulnerabilities(company_id={self.company_id}, ports={self.ports}, missing_headers={self.missing_headers})>"
  
engine = create_engine('mysql+pymysql://root:Mega442001#@localhost/pro_secure');

# Session factory, bound to the engine
Session = sessionmaker(bind=engine)

# Create a new session
session = Session()


try: 
    with engine.connect() as connection:
        print('connected')
except Exception as e:
        print(e);

# Session = sessionmaker(bind=engine);
# session = Session();

session.commit()

Base.metadata.create_all(engine)
'''





app = Flask(__name__, template_folder="templates")
CORS(app, resources={r"/*": {"origins": "*"}})  # Allows frontend (PHP) to call API from another domain

# ✅ Initialize Database (Create Tables)
init_db()
runExtraQueries()

# ✅ Get a new session for database operations
session = get_db_session()


@app.route("/")
def home():
    return render_template("index.html")  # Serve the HTML page

def is_domain_live(domain):
    """
    ✅ Checks if a domain is live by testing both HTTPS and HTTP.
    ✅ Returns True if reachable, else False.
    """
    for protocol in ["https://", "http://"]:
        try:
            result = subprocess.run(
                ["curl", "-Is", "--connect-timeout", "5", protocol + domain],
                capture_output=True, text=True, timeout=6
            )
            if "HTTP/" in result.stdout:
                return True
        except subprocess.TimeoutExpired:
            continue  # Try the next protocol
        except Exception as e:
            print(f"Error checking {protocol}{domain}: {e}")
            continue

    return False  # ❌ Not live

# ✅ Directory for storing JSON results
SCAN_RESULTS_DIR = "scan_results"

# ✅ Ensure directory exists
if not os.path.exists(SCAN_RESULTS_DIR):
    os.makedirs(SCAN_RESULTS_DIR)

# def save_scan_result(temp_id, scan_data):
#     """ ✅ Save scan data to a JSON file (creates if not exists) using temp_id """
#     print(scan_data)
#     # ✅ Ensure the directory exists
#     os.makedirs(SCAN_RESULTS_DIR, exist_ok=True)

#     file_path = os.path.join(SCAN_RESULTS_DIR, f"{temp_id}.json")


#     try:
#         # ✅ If the file exists, load existing data
#         if os.path.exists(file_path):
#             with open(file_path, "r", encoding="utf-8") as file:
#                 try:
#                     existing_data = json.load(file)
#                 except json.JSONDecodeError:
#                     print(f"❌ Corrupted JSON file, resetting: {file_path}")
#                 existing_data = {}  # Reset file if corrupted
#         else:
#             existing_data = {}  # ✅ Create new JSON structure

#         # ✅ Correctly append/merge data instead of replacing
#         for key, value in scan_data.items():
#             if isinstance(value, dict) and key in existing_data and isinstance(existing_data[key], dict):
#                 # ✅ Merge dictionaries (combine old + new)
#                 existing_data[key].update(value)
#             elif isinstance(value, list):
#                 # ✅ Append to existing list (create new list if not exists)
#                 if key in existing_data and isinstance(existing_data[key], list):
#                     existing_data[key].extend(value)
#                 else:
#                     existing_data[key] = value
#             elif isinstance(value, str) or isinstance(value, bool):
#                 # ✅ Convert to list if multiple entries are needed
#                 if key in existing_data:
#                     if isinstance(existing_data[key], list):
#                         existing_data[key].append(value)
#                     else:
#                         existing_data[key] = [existing_data[key], value]
#                 else:
#                     existing_data[key] = value
#             else:
#                 # ✅ Directly store non-list/dict values
#                 existing_data[key] = value

#         # ✅ Update with new scan data
#         #existing_data.update(scan_data)  

#         # ✅ Write updated JSON file
#         with open(file_path, "w", encoding="utf-8") as file:
#             json.dump(existing_data, file, indent=4)

#         # ✅ Print JSON response correctly
#         print("✅ Scan results (JSON format):")
#         print(json.dumps(existing_data, indent=4))  # Correct print format

#     except json.JSONDecodeError:
#         print(f"❌ Error reading JSON file (possibly corrupted): {file_path}")
#     except Exception as e:
#         print(f"❌ Error saving scan result for temp_id {temp_id}: {e}")



def save_scan_result(temp_id, scan_data):
    """ :white_tick: Save scan data to a JSON file (creates if not exists) using temp_id """
    # :white_tick: Ensure the directory exists
    os.makedirs(SCAN_RESULTS_DIR, exist_ok=True)
    file_path = os.path.join(SCAN_RESULTS_DIR, f"{temp_id}.json")
    try:
        # :white_tick: If the file exists, load existing data
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                existing_data = json.load(file)
        else:
            existing_data = {}  # :white_tick: Create new JSON structure
        # :white_tick: Update with new scan data
        existing_data.update(scan_data)
        # :white_tick: Write updated JSON file
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(existing_data, file, indent=4)
        # :white_tick: Print JSON response correctly
        print(" Scan results (JSON format):")
        print(json.dumps(existing_data, indent=4))  # Correct print format
    except json.JSONDecodeError:
        print(f":x: Error reading JSON file (possibly corrupted): {file_path}")
    except Exception as e:
        print(f":x: Error saving scan result for temp_id {temp_id}: {e}")




# @app.route("/scan-results/<int:company_id>", methods=["GET"])
# def get_scan_results(company_id):
#     """ ✅ Fetch scan results using temp_id """
#     file_path = os.path.join(SCAN_RESULTS_DIR, f"{company_id}.json")

#     # ✅ Check if file exists before serving
#     if not os.path.exists(file_path):
#         return jsonify({"error": "Scan results not found"}), 404

#     try:
#         # ✅ Serve JSON file efficiently
#         return send_file(file_path, mimetype="application/json")
    
#     except Exception as e:
#         print(f"❌ Error serving scan results for company_id {company_id}: {e}")
#         return jsonify({"error": "Internal Server Error"}), 500      








# Initialize Database
# def init_db():
#     conn = sqlite3.connect("scan_results.db")
#     cursor = conn.cursor()
#     cursor.execute('''CREATE TABLE IF NOT EXISTS scans (
#                         id INTEGER PRIMARY KEY AUTOINCREMENT,
#                         domain TEXT,
#                         open_ports TEXT,
#                         timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
#     conn.commit()
#     conn.close()


def get_whois_info(domain, entry_id, company_id, session):
    try:
        result = subprocess.run(["whois", domain], capture_output=True, text=True, timeout=60)
        whois_output = result.stdout

        # Check if referral WHOIS server is present (e.g., for .com domains)
        referred_server = None
        for line in whois_output.splitlines():
            if "Registrar WHOIS Server:" in line or "Whois Server:" in line:
                referred_server = line.split(":")[1].strip()
                break

        # Follow referral if found
        if referred_server:
            result = subprocess.run(["whois", "-h", referred_server, domain], capture_output=True, text=True, timeout=60)
            whois_output = result.stdout

        # Fields you want to extract
        fields_to_extract = [
            "Registry Domain ID", "Registrar WHOIS Server", "Registrar URL",
            "Updated Date", "Creation Date", "Registry Expiry Date", "Registrar",
            "Registrar IANA ID", "Registrar Abuse Contact Email", "Registrar Abuse Contact Phone",
            "Domain Status", "Name Server", "DNSSEC"
        ]

        whois_data = {}
        for line in whois_output.splitlines():
            line = line.strip() 
            for field in fields_to_extract:
                if line.startswith(field):
                    key, _, value = line.partition(":")
                    key = key.strip()
                    value = value.strip()

                    # Handle multiple domain status or name server entries
                    if key in whois_data:
                        if isinstance(whois_data[key], list):
                            whois_data[key].append(value)
                        else:
                            whois_data[key] = [whois_data[key], value]
                    else:
                        whois_data[key] = value

        # ✅ Store in DB
        session.query(Vulnerabilities).filter(Vulnerabilities.company_id == company_id).update(
            {"info_http_headers": whois_data}
        )
        session.commit()

        # ✅ Save in JSON file
        save_scan_result(entry_id, {"whois_info": whois_data})

        print(f"✅ WHOIS info saved for {domain}")

    except subprocess.TimeoutExpired:
        print(f"❌ WHOIS command timed out for {domain}")
    except Exception as e:
        print(f"❌ WHOIS info failed for {domain}: {e}")


def is_nmap_installed():
    return shutil.which("nmap") is not None  #  Check if Nmap exists

# Function to run Nmap scan
def run_nmap_scan(domain):
    if not is_nmap_installed():  # Check before running
        return "Nmap is not installed or not found in PATH."


    try:
        # Running Nmap to scan top 200 vulnerability ports within 5 seconds
        result = subprocess.run(
            #["nmap", "-T4", "--top-ports", "200", "--host-timeout", "60s", domain],  
            ["nmap", "-T5", "-p-", "--min-rate=1000", "-Pn", "--open", "--script", "vuln", domain],
            capture_output=True, text=True
        )
        # Extract only open ports using regex
        open_ports = re.findall(r"(\d+)/tcp\s+open", result.stdout)

        if not open_ports:
            return "No open ports found!"
        

        return ", ".join(open_ports)  # Return only open ports as a string
    except subprocess.TimeoutExpired:
        return "Scan timed out!"    

# ✅ Define the top 20 security headers
TOP_20_HEADERS = [
    "Strict-Transport-Security", "X-Frame-Options", "X-XSS-Protection", "X-Content-Type-Options",
    "Referrer-Policy", "Content-Security-Policy", "Permissions-Policy", "Cache-Control",
    "Pragma", "Expires", "Access-Control-Allow-Origin", "Access-Control-Allow-Methods",
    "Access-Control-Allow-Headers", "Feature-Policy", "Expect-CT", "Public-Key-Pins",
    "NEL", "Server-Timing", "Cross-Origin-Resource-Policy", "Cross-Origin-Embedder-Policy"
]    


def check_missing_headers(domain):
    try:
        url = f"http://{domain}"  # ✅ Try HTTP first
        response = requests.get(url, timeout=5)

        # ✅ Convert response headers to lowercase for case-insensitive matching
        response_headers = {header.lower() for header in response.headers.keys()}

        # ✅ Check which security headers are missing
        missing_headers = [header for header in TOP_20_HEADERS if header.lower() not in response_headers]

        return missing_headers  # ✅ Return only the missing ones

    except requests.RequestException:
        return []  # ✅ Handle unreachable domains
    
def get_http_headers(domain):
    try:
        url = f"http://{domain}"
        response = requests.get(url, timeout=5)
        return dict(response.headers)  # ✅ Convert headers to a dictionary
    except requests.RequestException:
        return {}   


    
def detect_technology(domain):
    try:
        url = f"http://{domain}"  # Try HTTP first
        response = requests.get(url, timeout=5)
        
        headers = response.headers

        # Extract Server & X-Powered-By
        server = headers.get("Server", "Unknown").lower()
        x_powered_by = headers.get("X-Powered-By", "").lower()

        # Identify Programming Language
        if "PHP" in x_powered_by or "PHP" in server:
            language = "PHP"
        elif "ASP.NET" in x_powered_by or "ASP.NET" in server:
            language = "ASP.NET"
        elif "Node.js" in x_powered_by:
            language = "Node.js"
        elif "Python" in x_powered_by:
            language = "Python"
        elif "Java" in x_powered_by:
            language = "Java"
        else:
            language = "Unknown"

        # Identify CMS based on response body
        cms = "Unknown"
        if "wp-content" in response.text:
            cms = "WordPress"
        elif "Joomla" in response.text:
            cms = "Joomla"
        elif "Drupal" in response.text:
            cms = "Drupal"

        return {
            "server": server,
            "language": language,
            "cms": cms
        }

    except requests.RequestException:
        return {"server": "Unknown", "language": "Unknown", "cms": "Unknown"}     
    

def perform_fuzzing(domain, server, language, cms):

    # ✅ Convert to lowercase
    server = server.lower()
    language = language.lower()
    cms = cms.lower()

# Use relative paths for wordlists
    FUZZ_DIR = "fuzz_finder"
    WORDLISTS = {
        "php": os.path.join(FUZZ_DIR, "php_wordlist.txt"),
        "asp.net": os.path.join(FUZZ_DIR, "asp_wordlist.txt"),
        "node.js": os.path.join(FUZZ_DIR, "node_wordlist.txt"),
        "python": os.path.join(FUZZ_DIR, "python_wordlist.txt"),
        "java": os.path.join(FUZZ_DIR, "java_wordlist.txt"),
        "wordpress": os.path.join(FUZZ_DIR, "wordpress_wordlist.txt"),
        "joomla": os.path.join(FUZZ_DIR, "joomla_wordlist.txt"),
        "drupal": os.path.join(FUZZ_DIR, "drupal_wordlist.txt"),
        "apache": os.path.join(FUZZ_DIR, "apache_wordlist.txt"),
        "nginx": os.path.join(FUZZ_DIR, "nginx_wordlist.txt"),
    }    

# ✅ Choose the most relevant wordlist
    wordlist = None
    if language in WORDLISTS:
        wordlist = WORDLISTS[language]
    if cms in WORDLISTS:
         wordlist = WORDLISTS[cms]
    if server in WORDLISTS:
      wordlist = WORDLISTS[server]

    print(wordlist)
    # 🚫 If no wordlist is found or missing, skip the scan
    if not wordlist or not os.path.isfile(wordlist):
        print(f"⚠️ Wordlist not found for {language}/{cms}/{server}. Skipping scan.")
        return []
    
    print(f"✅ Using wordlist: {wordlist}")

    # 🔎 Find misconfigurations
    exposed_files = []
    try:
        with open(wordlist, "r") as f:
            endpoints = [line.strip() for line in f]

        for endpoint in endpoints:
            url = f"http://{domain}/{endpoint}"  # Try HTTP first
            try:
                response = requests.get(url, timeout=3)
                if response.status_code == 200:  # ✅ Found an exposed file!
                    print(f"🟢 Found: {url}")
                    exposed_files.append(url)
            except requests.RequestException:
                pass  # Ignore unreachable URLs

    except FileNotFoundError:
        pass  # No errors if the file is missing
   

    return exposed_files

def run_xsstrike(url):
    """Run XSStrike against a given URL to detect XSS vulnerabilities with details."""
    try:
        command = ["python3", "XSStrike/xsstrike.py", "--url", url, "--crawl", "--blind"]
        result = subprocess.run(command, capture_output=True, text=True, timeout=300)
        
        output = result.stdout
        xss_vulnerability = []

        for line in output.split("\n"):
            if "Vulnerable" in line:  # Adjust based on actual XSStrike output
                parts = line.split(":")
                if len(parts) >= 3:
                    vuln_url = parts[0].strip()
                    vuln_param = parts[1].strip()
                    payload = parts[2].strip()
                    xss_vulnerability.append({
                        "url": vuln_url,
                        "parameter": vuln_param,
                        "payload": payload,
                        "type": "Reflected XSS"  # Modify based on detection logic
                    })
        
        return xss_vulnerability if xss_vulnerability else None
    except Exception as e:
        return str(e)

# def scan_open_redirection(domain):
#     """Scans for Open Redirection vulnerabilities using a wordlist file."""
#     PAYLOAD_FILE = os.path.join(os.path.dirname(__file__), "open_redirection", "open_redirect_wordlist.txt")
#     vulnerable_urls = []

#     try:
#         with open(PAYLOAD_FILE, "r", encoding="utf-8") as file:
#             payloads = [line.strip() for line in file if line.strip()]
#     except FileNotFoundError:
#         print(f"⚠️ Payload file not found: {PAYLOAD_FILE}")
#         return []
    

#      # ✅ Ensure the domain is parsed correctly
#     parsed_domain = urlparse(domain).netloc
#     # pay="go-koala.com"
#     # test="http://google.com:80#@www.whitelisteddomain.tld/"

#     for payload in payloads:
#         # ✅ Construct test URL correctly
#         if payload.startswith(("http://", "https://", "//")):
#             test_url = payload  # Use absolute or scheme-relative URL as-is
#         elif payload.startswith("/"):
#             test_url = domain.rstrip("/") + payload  # Ensure no double slashes
#         else:
#             test_url = domain.rstrip("/") + "/" + payload  # Add single slash
#         print(test_url)
#         # print(test_url = urljoin(pay,test))
#         try:
#             response = requests.get(test_url, allow_redirects=True, timeout=5)
#             final_url = response.url


#             if response.history and urlparse(final_url).netloc != parsed_domain: # ✅ Check if redirection happened
#                 vulnerable_urls.append({"payload": test_url, "redirected_to": final_url})
#                 print(f"[!] Open Redirection Found: {test_url} → {final_url}")
#         except requests.RequestException:
#             continue  # Ignore request errors

def scan_open_redirection(domain):
    """
    Scans a given domain for Open Redirection vulnerabilities using a wordlist.
    
    ✅ Loads payloads from `open_redirection/open_redirect_wordlist.txt`
    ✅ Checks if the site redirects to an external domain
    ✅ Avoids false positives from same-site redirects
    ✅ Ensures at least one redirect occurs
    """
    # Load the wordlist
    PAYLOAD_FILE = os.path.join(os.path.dirname(__file__), "open_redirection", "open_redirect_wordlist.txt")
    try:
        with open(PAYLOAD_FILE, "r", encoding="utf-8") as file:
            payloads = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"⚠️ Payload file not found: {PAYLOAD_FILE}")
        return []

    vulnerable_urls = []
    original_domain = urlparse(domain).netloc.lower()

    for payload in payloads:
        # Directly use the payload as the test URL
        test_url = urljoin(domain, payload)

        try:
            response = requests.get(test_url, allow_redirects=True, timeout=5)
            final_url = response.url
            final_domain = urlparse(final_url).netloc.lower()

            # ✅ Strict Open Redirect Detection:
            if (
                response.history and  # Ensure redirection occurred
                final_domain and final_domain != original_domain and  # Ensure external redirection
                not final_domain.endswith(original_domain) and  # Prevent subdomain false positives
                not final_domain.startswith("www." + original_domain)  # Ignore "www" subdomains
                
            ):
                print(test_url)    
                
                vulnerable_urls.append({"payload": test_url, "redirected_to": final_url})
                print(f"[🔥] Open Redirect Found: {test_url} → {final_url}")

        except requests.RequestException:
            continue  # Ignore errors and timeouts
        # print(vulnerable_urls)

    return vulnerable_urls        

# #def detect_os_command_injection(domain):
OS_COMMAND_INJECTION_DIR = "OS_COMMAND_INJECTION_DIR"

def load_wordlist(file_name):
    """ Load wordlist from the OS_COMMAND_INJECTION_DIR folder """
    file_path = os.path.join(OS_COMMAND_INJECTION_DIR, file_name)
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return [line.strip() for line in file.readlines()]
    return []


def enumerate_directories(domain):
    """ ✅ Enumerate directories using wordlist and store in DB """
    detected_directories = []
    directory_wordlist = load_wordlist("directories.txt")  # ✅ Load directories list

    print(f"🔍 Enumerating directories for {domain}...")

    for directory in directory_wordlist:
        test_url = f"http://{domain}/{directory}"
        try:
            response = requests.get(test_url, timeout=5)
            if response.status_code in [200, 301, 302]:  # ✅ Valid directory found
                detected_directories.append({"directory": directory, "url": test_url})
                print(f"✅ Found: {test_url}")
        except requests.RequestException:
            pass  # Ignore errors


        
    # ✅ Return empty object if nothing found
    return detected_directories if detected_directories else {}


def check_clickjacking(domain):
    """
    Checks if the given domain is vulnerable to Clickjacking.
    Returns a dictionary with the scan results.
    """
    try:
        # Send a GET request to fetch the headers
        url = f"https://{domain}" if not domain.startswith("http") else domain
        response = requests.get(url, timeout=10)

        # Extract security headers
        x_frame_options = response.headers.get("X-Frame-Options", "").lower()
        content_security_policy = response.headers.get("Content-Security-Policy", "").lower()

        # Check if the website is vulnerable
        vulnerable = False
        vulnerability_reason = ""

        if "deny" in x_frame_options or "sameorigin" in x_frame_options:
            vulnerability_reason = "Protected (X-Frame-Options is set correctly)"
        elif "frame-ancestors" in content_security_policy:
            vulnerability_reason = "Protected (CSP frame-ancestors is set)"
        else:
            vulnerability_reason = "Vulnerable! No X-Frame-Options or CSP protection found."
            vulnerable = True

        # Return the scan result
        return {
            "domain": domain,
            "x_frame_options": x_frame_options if x_frame_options else "{}",
            "content_security_policy": content_security_policy if content_security_policy else "{}",
            "vulnerable": vulnerable,
            "message": vulnerability_reason
        }

    except requests.RequestException as e:
        return {"error": f"Failed to check Clickjacking for {domain}: {str(e)}"}
    

# d

def get_website_technology(domain):
    try:
        result = subprocess.run(
            ["whatweb", "--log-json=-", domain], capture_output=True, text=True
        )
        data = json.loads(result.stdout)
        return data
    except Exception as e:
        return {"error": str(e)}


def perform_full_scan(domain, entry_id,):
    """Runs all security scans one by one and stores each result in the database."""
    #session = get_db_session()  # Get DB session
    company_id = session.query(CompanyInfo.id).filter(CompanyInfo.id == entry_id).first();
    session.commit()
    # company_id = company_id.id

    print('hi_______->')
    print(company_id)
   

    try:

        process = multiprocessing.Process(target=get_whois_info, args=(domain, entry_id, company_id, session))
        process.start()

        scan_results = {}

        


        scan_result = run_nmap_scan(domain)
        open_ports = scan_result.split(", ") if scan_result and scan_result != "No open ports found!" else []
        #open_ports.append("890")
        vulnerable_ports = [port for port in open_ports if port not in ["80", "443"]]

        session.query(Vulnerabilities).filter_by(company_id=company_id).update(
            {"ports": vulnerable_ports}
        )
        
        # session.add(Vulnerabilities(company_id=company_id, ports=vulnerable_ports))
        session.commit()
        save_scan_result(entry_id, {"open_ports": open_ports})
        save_scan_result(entry_id, {"vulnerable_ports": vulnerable_ports})
        print(f"✅ Nmap Scan completed for {domain}")


         # ✅ Check Missing Headers
        missing_headers = check_missing_headers(domain)
        #http_headers = get_http_headers(domain)
        
        session.query(Vulnerabilities).filter_by(company_id=company_id).update(
            {  "missing_headers": missing_headers}
        )
        session.commit()
        save_scan_result(entry_id, {"missing_headers": missing_headers})
        print(f"✅ Missing Header Analysis completed for {domain}")



        technolgy_info = get_website_technology(domain)

            # Ensure technolgy_info is a valid dictionary
        if not isinstance(technolgy_info, dict):
            technolgy_info = {"error": "Failed to retrieve technology data"}

        # Save in Database
        session.query(Vulnerabilities).filter_by(company_id=company_id).update(
            {"detailed_info": technolgy_info}
        )
        session.commit()

        # Save in JSON File
        save_scan_result(entry_id, {"detailed_info": technolgy_info})

        print(f"✅ Detailed Technology Scan completed for {domain}")



        # ✅ Detect Server, Language, CMS
        tech_info = detect_technology(domain)
        # Ensure tech_info is a valid dictionary
        try:
            tech_data = json.loads(tech_info) if isinstance(tech_info, str) else tech_info
        except json.JSONDecodeError:
            tech_data = {"error": "Failed to parse technology data"}
        server = tech_data.get("server", "Unknown")
        language = tech_data.get("language", "Unknown")
        cms = tech_data.get("cms", "Unknown")

        exposed_files = []
        if server != "Unknown" or language != "Unknown" or cms != "Unknown":
            exposed_files = perform_fuzzing(domain, server, language, cms)
        
        updated_tech_info = [
            {"techinfo": f"{language}, {server}"},
            
        ]

        vulnerable_tech_info = [
            {"techinfoVulnerability": exposed_files} if exposed_files else {"techinfoVulnerability": {}}
        ]

        session.query(Vulnerabilities).filter_by(company_id=company_id).update(
            {"technology_info": updated_tech_info}
        )
        session.commit()
        save_scan_result(entry_id, {"updated_tech_info": updated_tech_info})
        save_scan_result(entry_id, {"vulnerable_tech_info": vulnerable_tech_info})
        print(f"✅ Technology Detection completed for {domain}")


        # Get detailed technology information
        # tech_info = get_website_technology(domain) 

        # # Detect additional tech info (server, language, CMS)
        # detected_tech_info = detect_technology(domain)
        # detected_data = json.loads(detected_tech_info) if isinstance(detected_tech_info, str) else detected_tech_info

        # server = detected_data.get("server", "Unknown")
        # language = detected_data.get("language", "Unknown")
        # cms = detected_data.get("cms", "Unknown")

        # # Perform fuzzing based on detected tech stack
        # exposed_files = []
        # if server != "Unknown" or language != "Unknown" or cms != "Unknown":
        #     exposed_files = perform_fuzzing(domain, server, language, cms)

        # # Merge technology data properly
        # final_tech_info = {
        #     "basic_info": tech_info,  # Data from `get_website_technology`
        #     "detailed_info": {
        #         "server": server,
        #         "language": language,
        #         "cms": cms,
        #         "exposed_files": exposed_files
        #     }
        # }

        # session.query(Vulnerabilities).filter_by(company_id=company_id).update(
        #     {"technology_info": final_tech_info}
        # )
        # save_scan_result(entry_id, {"technology_info": final_tech_info})
        # print(f"✅ Technology Detection & Analysis completed for {domain}")

        # session.commit()




        # ✅ Run XSStrike for XSS scanning
        xss_results = run_xsstrike(domain)
        xss_vuln_data = xss_results if xss_results else []

        session.query(Vulnerabilities).filter_by(company_id=company_id).update(
            {"xss_vulnerabilities": xss_vuln_data}
        )
        session.commit()
        save_scan_result(entry_id, {"xss_vuln_data": xss_vuln_data})
        print(f"✅ XSS Scan completed for {domain}")



        # ✅ Open Redirection Scan
        open_redirect_vulnerabilities = scan_open_redirection(domain)

        session.query(Vulnerabilities).filter_by(company_id=company_id).update(
            {"open_redirection_vulnerabilities": open_redirect_vulnerabilities}
        )
        session.commit()
        save_scan_result(entry_id, {"open_redirect_vulnerabilities": open_redirect_vulnerabilities})
        print(f"✅ Open Redirection Scan completed for {domain}")

                 # ✅ Detect OS Command Injection
        # os_command_vulns = detect_os_command_injection(domain)
        # session.query(Vulnerabilities).filter_by(company_id=entry_id).update({"os_command_injection_vulnerabilities": os_command_vulns})
        # session.commit()
        # save_scan_result(entry_id, {"os_command_injection_vulnerabilities": os_command_vulns})
        # print(f"✅ OS Command Injection Scan completed for {domain}")

        

        directory_enumration_vuln = enumerate_directories(domain)

        session.query(Vulnerabilities).filter_by(company_id=company_id).update(
            {"Directory_enumration_vulnerabilities": directory_enumration_vuln}
        )
        session.commit()
        save_scan_result(entry_id, {"Directory_enumration_vulnerabilities": directory_enumration_vuln})
        print(f"✅ Open Redirection Scan completed for {domain}")

                # ✅ Run Clickjacking Scan
        clickjacking_result = check_clickjacking(domain)

        # ✅ Save Clickjacking vulnerability in DB
        session.query(Vulnerabilities).filter_by(company_id=company_id).update(
            {"clickjacking_vulnerability": clickjacking_result}
        )
        session.commit()

        # ✅ Save Clickjacking scan result to JSON file
        save_scan_result(entry_id, {"clickjacking_vulnerability": clickjacking_result})

        print(f"✅ Clickjacking Scan completed for {domain}")


        # """ Run Wappalyzer and store results in DB & JSON file """
        # technology_info = run_wappalyzer_scan(domain)
        # # ✅ Save to database
        # session.query(Vulnerabilities).filter_by(company_id=company_id).update(
        #     {"technology_info": technology_info})
        # session.commit()
        #  # ✅ Save to JSON file
        # save_scan_result(entry_id, {"technology_info": technology_info})
        # print(f"✅ Wappalyzer scan completed for {domain}")
        # print(f"✅ All scans completed for {domain}")





            # ✅ Mark scan as complete
        scan_results["scan_complete"] = True 
   

        # Save results to JSON
        save_scan_result(entry_id , {"scan_result":scan_results})


        # vulnerability_count = 0
        # if open_ports: vulnerability_count += 1
        # if xss_results: vulnerability_count += len(xss_results)
        # if open_redirect_vulnerabilities: vulnerability_count += len(open_redirect_vulnerabilities)
        # save_scan_result(entry_id, {"status": "complete", "vulnerability": vulnerability_count, "total_checks": 3})
        # print(f"✅ Scan completed. {vulnerability_count} vulnerabilities found.")

    except Exception as e:
        print(f"❌ Error during scan: {e}")
        session.rollback()
    
    finally:
        session.close()




@app.route("/scan", methods=["POST"])
def scan():
    try:
        data = request.get_json()
        if not data or "domain" not in data:
            return jsonify({"error": "No domain provided"}), 400
        
        domain = data["domain"]
        
        print("Received domain:", domain)
        
        if not is_domain_live(domain):
            print(f"⚠️ Skipping scans: {domain} is not live!")

             # Store the result immediately in DB
            # session.query(Vulnerabilities).filter_by(company_id=new_entry.id).update(
            #     {"scan_status": "Domain is not live"}
            # )
            # session.commit()
            return jsonify({"message": "Site is not live","temp_id": None, "domain": domain})
    

        print(f"🚀 {domain} is live! Proceeding with scans...")
        # Get the latest temp_id and increment it (ensure uniqueness)
        now = datetime.now().timestamp();
        now = str(now);
        rand_temp_id_index = now.rfind('.');
        rand_temp_id = now[(rand_temp_id_index + 1):];

        max_temp_id = session.query(CompanyInfo.temp_id).filter(CompanyInfo.temp_id == rand_temp_id).first()

        new_temp_id = rand_temp_id;
        #Auto-increment



         # ✅ Generate a unique placeholder email
        #unique_email = f"unknown_{new_temp_id}@example.com"

        

        # Insert new company entry with unique temp_id
        new_entry = CompanyInfo(temp_id=new_temp_id, company_name=None,email=None, url=domain)
        session.add(new_entry)
        session.commit()  # ✅ Commit first to generate `id`

# ✅ Fetch the committed entry to ensure `id` is available
        session.refresh(new_entry)  # ✅ Guarantees new_entry.id exists in DB

        #session = get_db_session()

        # ✅ Verify company_id exists in DB before inserting
        company_exists = session.query(CompanyInfo).filter_by(id=new_entry.id).first()
        if not company_exists:
            raise Exception(f"Company ID {new_entry.id} not found in the database!")
        

        #session = get_db_session()  # Get DB session
        company_id = session.query(CompanyInfo.id).filter(CompanyInfo.id == new_temp_id).first();
        session.commit()
        

        http_headers = get_http_headers(domain)
        
      

        session.query(Vulnerabilities).filter_by(company_id=company_id).update(
            { "info_http_headers": http_headers}
        )
        session.commit()
        save_scan_result(new_temp_id, {"url": domain})
        save_scan_result(new_temp_id, {"http_headers": http_headers})
        print(f"✅ HTTP Header Analysis completed for {domain}")


        # ✅ Start background scan
        process = multiprocessing.Process(target=perform_full_scan, args=(domain, new_temp_id))
        process.start()

       



        #session.commit()  # Commit changes to store entry

        # Run Nmap scan
        ##scan_result = run_nmap_scan(domain)
        # scan_result = run_nmap_scan(domain)

        # # ✅ Filter out non-vulnerable ports (80, 443)
        # open_ports = scan_result.split(", ") if scan_result and scan_result != "No open ports found!" else []
        # open_ports.append("890")
        # vulnerable_ports = [port for port in open_ports if port not in ["80", "443"]]

        # ✅ Check missing headers
        # missing_headers = check_missing_headers(domain)
        # http_headers = get_http_headers(domain)
        #  # ✅ Detect Server, Language, and CMS
        # tech_info = detect_technology(domain)




        #  # ✅ Perform fuzzing if tech is detected
        # tech_data = json.loads(tech_info) if tech_info and isinstance(tech_info, str) else tech_info
        # server = tech_data.get("server", "Unknown")
        # language = tech_data.get("language", "Unknown")
        # cms = tech_data.get("cms", "Unknown")


        # exposed_files = []
        # if server == "Unknown" and language == "Unknown" and cms == "Unknown":
        #     print(f"⚠️ No known technology found for {domain}. Skipping misconfiguration scan.")
        #     exposed_files = []  # No scanning
        # else:    
            
        #     exposed_files = perform_fuzzing(domain, server, language, cms)


        #         # ✅ Format tech_info with vulnerabilities
        # updated_tech_info = [

        #     {"techinfo": f"{language}, {server}"},
        #     {"techinfoVulnerability": exposed_files} if exposed_files else {}
        # ]    

       
        
        #  # ✅ Run XSStrike for XSS scanning
        # xss_results = run_xsstrike(domain)

        # # ✅ Store XSS vulnerabilities with details
        # xss_vuln_data = xss_results if xss_results else []

        # # ✅ Open Redirection Scan
        # open_redirect_vulnerabilities = scan_open_redirection(domain)


       

        # # ✅ Store vulnerabilities in the database (INSIDE `scan()`)
        # vulnerability_entry = Vulnerabilities(
        #     company_id=new_entry.id, 
        #     ports=vulnerable_ports, # Link to company
        #     missing_headers=missing_headers , # ✅ Store missing headers
        #     info_http_headers=http_headers,
        #     technology_info=updated_tech_info,
        #     xss_vulnerabilities=xss_vuln_data ,
        #     open_redirection_vulnerabilities=open_redirect_vulnerabilities,
        # )
        # session.add(vulnerability_entry)
        # session.commit() 
        


        return jsonify({"message": "Scan started in the background","temp_id": new_temp_id, "domain": domain})

    except Exception as e:
        print(f"Error: {e}")  # Print error in Flask console
        session.rollback()  # Rollback changes if any error occurs
        return jsonify({"error": "Internal Server Error"}), 500  # Return JSON instead of HTML

'''
@app.route("/scan", methods=["POST"])
def scan():
    try:
        data = request.get_json()
        if not data or "domain" not in data:
            return jsonify({"error": "No domain provided"}), 400
        
        domain = data["domain"]
        
        print("Received domain:", domain)
        
        scan_result = run_nmap_scan(domain)

        return jsonify({"domain": domain, "scan_result": scan_result})

    except Exception as e:
        print(f"Error: {e}")  #  Print error in Flask console
        return jsonify({"error": "Internal Server Error"}), 500  #  Return JSON instead of HTML
'''


@app.route("/scan/results/<int:temp_id>", methods=["GET"])
def get_scan_result(temp_id):
    """
    Route to fetch and return the scan result JSON data for a given `temp_id` (or company_id)
    """
    # Ensure SCAN_RESULTS_DIR is defined and accessible
    if not os.path.exists(SCAN_RESULTS_DIR):
        return jsonify({"error": "Scan results directory not found"}), 500

    # Generate the path to the JSON file for this scan
    file_path = os.path.join(SCAN_RESULTS_DIR, f"{temp_id}.json")
    
    if os.path.exists(file_path):
        # Read the JSON file
        with open(file_path, 'r') as file:
            scan_data = json.load(file)
        
        # Return the scan data as a JSON response
        return jsonify(scan_data)
    else:
        # If the file doesn't exist, return an error message
        return jsonify({"error": "Scan result not found for the given temp_id"}), 404
   


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)  