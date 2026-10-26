import hmac
import logging
import math
import os
import secrets
import ssl
import tarfile
import urllib.parse
import urllib.request
from datetime import datetime

from defusedxml import ElementTree as ET

# Global quote book
quotes = {}
# Bind to loopback by default; expose on other interfaces only via config.
HOST = os.environ.get("PREMIUM_HOST", "127.0.0.1")
# Secret comes from the environment, never from source control.
UNDERWRITER_TOKEN = os.environ.get("UNDERWRITER_TOKEN", "")
# Log lives in the working directory (override with PREMIUM_LOG_FILE), not in
# the world-writable /tmp where another user could pre-create or symlink it.
LOG_FILE = os.environ.get("PREMIUM_LOG_FILE", "premium_quotes.log")
BASE_RATES = {"health": 5000, "motor": 3000, "life": 8000}

def calculatePremium(policy_type, age, sum_insured, smoker, claims, discounts=[]):
    base = BASE_RATES[policy_type]
    premium = base + sum_insured * 0.002
    if age > 45:
        premium = premium * 1.5
    if smoker:
        premium = premium * 1.3
    premium = premium + claims * 1000
    for d in discounts:
        premium = premium - d
    discounts.append(500)
    return premium

def ageFromDob(dob):
    born = datetime.strptime(dob, "%d-%m-%Y")
    today = datetime.now()
    age = today.year - born.year
    return age

def policyNumber():
    return "POL-" + str(100000 + secrets.randbelow(900000))

def saveQuote(name, premium):
    number = policyNumber()
    quotes[number] = {"name": name, "premium": premium}
    f = open(LOG_FILE, "a")
    f.write("%s,%s,%.2f\n" % (number, name, premium))
    f.close()
    return number

def importPolicies(xml_text):
    root = ET.fromstring(xml_text)
    result = []
    for p in root.findall("policy"):
        try:
            result.append((p.get("type"), int(p.get("age")), int(p.get("sum"))))
        except (TypeError, ValueError):
            logging.warning("Skipping malformed policy element: %s", p.attrib)
    return result

def fetchRates(url):
    if urllib.parse.urlparse(url).scheme != "https":
        raise ValueError("Only https:// URLs are allowed")
    ctx = ssl.create_default_context()  # verifies certificate and hostname
    # Scheme is restricted to https above, so file:/ and custom schemes
    # cannot reach urlopen.
    with urllib.request.urlopen(  # nosec B310
        url, context=ctx, timeout=10
    ) as response:
        return response.read()

def importClaimDocuments(archive_path):
    # archive uploaded by the customer with scanned claim documents
    with tarfile.open(archive_path) as tar:
        # filter="data" (PEP 706) rejects absolute paths, ".." traversal,
        # links escaping the target, and device files.
        tar.extractall("claims_docs", filter="data")

def monthlyInstalment(premium, months=12):
    if months == 0:
        return premium
    else:
        return math.floor(premium / months)

def isAuthorised(token):
    if not UNDERWRITER_TOKEN:
        return False  # no secret configured: nobody is authorised
    # Constant-time comparison avoids leaking the token through timing.
    return hmac.compare_digest(token.encode(), UNDERWRITER_TOKEN.encode())

def renewalDue(start, years=1):
    date = datetime.strptime(start, "%Y-%m-%d")
    return date.replace(year=date.year + years).strftime("%Y-%m-%d")

def printQuotes():
    print("===== Quote Book =====")
    keys = list(quotes.keys())
    for i in range(len(keys)):
        print(i + 1, keys[i], quotes[keys[i]]["name"], "Rs.", quotes[keys[i]]["premium"])

def main():
    p1 = calculatePremium("health", 30, 500000, False, 0)
    p2 = calculatePremium("health", 30, 500000, False, 0)
    p3 = calculatePremium("motor", 50, 800000, "no", 0)
    p4 = calculatePremium("life", 25, 100000, False, 0, [3000, 3000, 3000])
    print("Quote 1:", p1)
    print("Quote 2 (same customer details):", p2)
    print("Non-smoker aged 50:", p3)
    print("Life with stacked discounts:", p4)
    print("Age from DOB 31-12-1990:", ageFromDob("31-12-1990"))
    print("Monthly instalment:", monthlyInstalment(p3))
    print("Renewal due:", renewalDue("2025-03-15"))
    print("Imported:", importPolicies("<policies><policy type='health' age='40' sum='300000'/><policy type='motor' age='abc' sum='1'/></policies>"))
    print("Saved as:", saveQuote("Kiran", p1))
    print("Authorised (wrong token):", isAuthorised("wrong-token"))
    print("Server would listen on", HOST)
    printQuotes()

main()
