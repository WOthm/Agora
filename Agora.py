import feedparser
from termcolor import colored
import argparse
from datetime import datetime
import requests
import re
import json

agora_ascii_art = """
   ,---.           _,---.      _,.---._                    ,---.      
 .--.'  \\      _.='.'-,  \\   ,-.' , -  `.    .-.,.---.   .--.'  \\     
 \\==\\-/\\ \\    /==.'-     /  /==/_,  ,  - \\  /==/  `   \\  \\==\\-/\\ \\    
 /==/-|_\\ |  /==/ -   .-'  |==|   .=.     ||==|-, .=., | /==/-|_\\ |   
 \\==\\,   - \\ |==|_   /_,-. |==|_ : ;=:  - ||==|   '='  / \\==\\,   - \\  
 /==/ -   ,| |==|  , \\_.' )|==| , '='     ||==|- ,   .'  /==/ -   ,|  
/==/-  /\\ - \\\\==\\-  ,    (  \\==\\ -    ,_ / |==|_  . ,'. /==/-  /\\ - \\ 
\\==\\ _.=\\.-' /==/ _  ,  /   '.='. -   .'  /==/  /\\ ,  )\\==\\ _.=\\.-' 
 `--`         `--`------'      `--`--''    `--`-`--`--'  `--`         
"""

news_feeds = {
    "TheHackerNews": "https://feeds.feedburner.com/TheHackersNews",
    "Sentinelone": "https://fr.sentinelone.com/blog/feed/",
    "Threatpost": "https://threatpost.com/feed",
    "KrebsOnSecurity": "https://krebsonsecurity.com/feed/", 
    "Talos": "https://blog.talosintelligence.com/rss/",
    "Securelist": "https://securelist.com/feed/",
    "Microsoft": "https://www.microsoft.com/en-us/security/blog/feed/",
    "Microsoftthreathunting": "https://msrc.microsoft.com/blog/categories/microsoft-threat-hunting/feed",
    "Itguru": "https://www.itsecurityguru.org/feed/",
    "Amazon": "https://aws.amazon.com/fr/blogs/security/feed/",
    "Sophos": "https://news.sophos.com/en-us/category/threat-research/feed/",
    "GrahamCluley": "https://grahamcluley.com/feed/",
    "Decoded": "https://decoded.avast.io/feed/",
    "Dataprivacy": "https://www.dataprivacyandsecurityinsider.com/feed/",
    "SecurityBoulevard": "https://securityboulevard.com/feed/",
    "Socprime": "https://socprime.com/blog/feed/",
    "Intel471": "https://intel471.com/blog/feed/",
    "Crowdstrike": "https://www.crowdstrike.com/blog/category/threat-intel-research/feed/",
    "Hackread": "https://www.hackread.com/feed/",
    "Infoblox": "https://blogs.infoblox.com/category/cyber-threat-intelligence/feed/",
    "Zerofox": "https://www.zerofox.com/blog/feed/",
    "Ransomware": "https://ransomware.org/feed/",
    "Helpnetsecurity": "https://www.helpnetsecurity.com/feed/",
    "Coveware": "https://www.coveware.com/blog?format=RSS",
    "BleepingComputer" : "https://www.bleepingcomputer.com/feed/",
    "Thedefirreport" : "https://thedfirreport.com/feed/"
}   

cve_feeds = {
    "Cisa": "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
}

leak_feeds = {
    "Leak-lookup": "https://leak-lookup.com/rss",
    "Data-breaches": "https://www.databreaches.net/feed/"
}

ransom_feeds = {
    "Ransomwarelive": "https://ransomware.live/rss.xml",
    "Redpacket": "https://www.redpacketsecurity.com/feed/",
    "Ransomlookup": "https://www.ransomlook.io/rss.xml"
}

def display_filtered_feed(rss_url, keyword, start_date=None, end_date=None, verbose=False, page_size=10):
    try:
        feed = feedparser.parse(rss_url)
        entries = []
        for entry in feed.entries:
            title = entry.title
            description = entry.description
            author = entry.author if 'author' in entry else 'unknown author '
            date = entry.published
            link = entry.link

            date_match = re.search(r'\d{2} \w{3} \d{4} \d{2}:\d{2}:\d{2}', date)
            if date_match:
                date = date_match.group(0)
                entry_date = datetime.strptime(date, "%d %b %Y %H:%M:%S")

            if not keyword or keyword.lower() in title.lower():
                if start_date is None or entry_date >= start_date:
                    if end_date is None or entry_date <= end_date:
                        entries.append({
                            "title": title,
                            "description": description,
                            "author": author,
                            "date": date,
                            "link": link
                        })

        total_pages = (len(entries) + page_size - 1) // page_size
        current_page = 0
        while current_page < total_pages:
            for i in range(current_page * page_size, min((current_page + 1) * page_size, len(entries))):
                entry = entries[i]
                print("Title:", entry['title'])
                if verbose:
                    print("Description:", entry['description'])
                print("Author:", entry['author'])
                print("Date:", entry['date'])
                print("Link:", entry['link'])
                print()

            if current_page < total_pages - 1:
                user_input = input("Press <Enter> to view next page: ")
                if user_input.lower() != " ":
                    break
            current_page += 1

    except Exception as e:
        print(f"An error occurred: {e}")

def display_filtered_json(json_url, keyword=None, start_date=None, end_date=None, verbose=False, page_size=10):
    try:
        data = requests.get(json_url).json()
        vulnerabilities = []

        for vulnerability in data['vulnerabilities']:
            cve_id = vulnerability.get('cveID')
            vulnerability_name = vulnerability.get('vulnerabilityName')
            date_added = vulnerability.get('dateAdded')
            description = vulnerability.get('shortDescription')

            if (not keyword or
                keyword.lower() in cve_id.lower() or
                keyword.lower() in vulnerability_name.lower() or
                keyword.lower() in description.lower()):

                if date_added:
                    date_added = datetime.strptime(date_added, "%Y-%m-%d")

                if (start_date is None or date_added >= start_date) and \
                        (end_date is None or date_added <= end_date):
                    vulnerabilities.append({
                        "cve_id": cve_id,
                        "vulnerability_name": vulnerability_name,
                        "date_added": date_added.strftime("%Y-%m-%d") if date_added else "",
                        "description": description
                    })

        total_pages = (len(vulnerabilities) + page_size - 1) // page_size
        current_page = 0
        while current_page < total_pages:
            for i in range(current_page * page_size, min((current_page + 1) * page_size, len(vulnerabilities))):
                vulnerability = vulnerabilities[i]
                print("CVE ID:", vulnerability['cve_id'])
                print("Vulnerability Name:", vulnerability['vulnerability_name'])
                print("Date Added:", vulnerability['date_added'])
                if verbose:
                    print("Description:", vulnerability['description'])
                print()

            if current_page < total_pages - 1:
                user_input = input("Press <Enter> to view next page:")
                if user_input.lower() != " ":
                    break
            current_page += 1

    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    parser = argparse.ArgumentParser(description="AGORA: Fetch and display information about cybersecurity news from various sources including articles, CVEs, ransomware attacks, and leaks, with filtering by keyword and date.")
    parser.add_argument("--argument",choices=["news","cve","leak","ransom"],help="choose between news, cve and leak")
    parser.add_argument("--verbose",help="For more details",action="store_true")
    parser.add_argument("--keyword", default="", help="Filter by keyword in the title")
    parser.add_argument("--start-date", help="Filter from this date (in 'YYYY-MM-DD' format)")
    parser.add_argument("--end-date", help="Filter until this date (in 'YYYY-MM-DD' format)")
    parser.add_argument("-help", action="help", help="Display help message")

    args = parser.parse_args()


    if not args.argument:
        print(agora_ascii_art)
        parser.print_help()
        return

    print(agora_ascii_art)
   

    if args.argument == "news":
        news_sources = news_feeds.keys()
        for source in  news_sources:
            news_url = news_feeds[source]
            start_date = datetime.strptime(args.start_date, "%Y-%m-%d") if args.start_date else None
            end_date = datetime.strptime(args.end_date, "%Y-%m-%d") if args.end_date else None
            if args.keyword:
                print(colored(f"📰 Results from news source '{source}' with the keyword '{args.keyword}':", "blue"))
                display_filtered_feed(news_url, args.keyword, start_date, end_date,verbose = args.verbose)
                print()
            else:
                print(colored(f"📰 Results from news source '{source}':", "blue"))
                display_filtered_feed(news_url, None, start_date, end_date,verbose = args.verbose)
                print()

    if args.argument == "cve":
        cve_sources = cve_feeds.keys()
        for source in cve_sources:
            cve_url = cve_feeds[source]
            start_date = datetime.strptime(args.start_date, "%Y-%m-%d") if args.start_date else None
            end_date = datetime.strptime(args.end_date, "%Y-%m-%d") if args.end_date else None
            if args.keyword:
                print(colored(f"💣 Results from CVE source '{source}' with the keyword '{args.keyword}':", "red"))
                display_filtered_json(cve_url, args.keyword, start_date, end_date,verbose = args.verbose)
                print()
            else:
                print(colored(f"💣 Results from CVE source '{source}':", "red"))
                display_filtered_json(cve_url, None, start_date, end_date,verbose = args.verbose)
                print()

    if args.argument == "leak":
        leak_sources = leak_feeds.keys()
        for source in leak_sources:
            leak_url = leak_feeds[source]
            start_date = datetime.strptime(args.start_date, "%Y-%m-%d") if args.start_date else None
            end_date = datetime.strptime(args.end_date, "%Y-%m-%d") if args.end_date else None
            if args.keyword:
                print(colored(f"🕵️ Results from leak source '{source}' with the keyword '{args.keyword}':", "green"))
                display_filtered_feed(leak_url, keyword=None, start_date=None, end_date=None,verbose = args.verbose)
                print()
            else:
                print(colored(f"🕵️ Results from leak source '{source}':", "green"))
                display_filtered_feed(leak_url, None, start_date, end_date,verbose = args.verbose)
                print()

    if args.argument == "ransom":
        ransom_sources = ransom_feeds.keys()
        for source in ransom_sources:
            ransom_url = ransom_feeds[source]
            start_date = datetime.strptime(args.start_date, "%Y-%m-%d") if args.start_date else None
            end_date = datetime.strptime(args.end_date, "%Y-%m-%d") if args.end_date else None
            if args.keyword:
                print(colored(f"🔒 Results from ransom source '{source}' with the keyword '{args.keyword}':", "yellow"))
                display_filtered_feed(ransom_url, args.keyword, start_date, end_date,verbose = args.verbose)
                print()
            else:
                print(colored(f"🔒 Results from ransom source '{source}':", "yellow"))
                display_filtered_feed(ransom_url, None, start_date, end_date,verbose = args.verbose)
                print()

if __name__ == "__main__":
    print()
    main()  
