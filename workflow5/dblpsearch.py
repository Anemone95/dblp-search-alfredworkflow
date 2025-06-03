#!/usr/bin/env python3

import json
import os
import sys
import requests

script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path) 
sys.path.insert(0,os.path.join(script_dir, 'lib'))

paper_search = "https://dblp.uni-trier.de/search/publ/api"
bibtex_base = "https://dblp.uni-trier.de/rec/"

def print_and_exit(message, exit_code=0):
    print(message)
    exit(0)

def main():
    print(sys.argv, file=sys.stderr)
    wait_info = json.dumps( {"items": [{ "title": "Finding papers on DBLP", "subtitle": "Please wait...", "valid": False }], "rerun": 0.3, })
    user_query = sys.argv[1]
    if len(sys.argv) < 2:
        print("Usage: python dblpsearch.py '<search_term>'", file=sys.stderr)
    if not user_query:
        print_and_exit(wait_info, 0)
    if len(user_query) < 2:
        print_and_exit(wait_info, 0)
    try:
        res = requests.get(f"{paper_search}?q={user_query}&format=json&h=10&c=1", timeout=200)
        items = []
        for each in res.json().get('result', {}).get('hits', {}).get('hit', []):
            info = each.get('info', {})
            title = info.get('title', 'No title')
            subtitle = info.get('authors', {}).get('author', [])
            authors = []
            if isinstance(subtitle, list):
                for author in subtitle:
                    authors.append(author.get('text', ''))
            elif isinstance(subtitle, dict):
                authors.append(subtitle.get('text', ''))
            authors_str = ', '.join(authors)
            bibtex_url = f"{bibtex_base}{info['key']}.bib"
            bibtex=requests.get(bibtex_url, timeout=200)

            items.append({
                "title": title,
                "subtitle": authors_str,
                "arg": bibtex.text.strip(),
            })
    except Exception as e:
        items = [{
            "title": f"Error occurred {e}",
            "subtitle": "Try a different query",
            "arg": "",
            "valid": False
        }]
    finally:
        print(json.dumps({"items": items}, ensure_ascii=False))


if __name__ == "__main__":
    main()