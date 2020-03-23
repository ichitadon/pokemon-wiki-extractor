import xmltodict
import re
import pprint
import sys

def main():
    args = sys.argv
    input_xml_path = args[1]
    print(input_xml_path)
    with open(input_xml_path) as fd:
        doc = xmltodict.parse(fd.read())
        pages = doc['mediawiki']['page']
        
        for index, page in enumerate(pages):
            page_title = page['title']
            print(f"{index} : {page_title}")

        page_text = pages[int(args[2])]['revision']['text']['#text']
        pprint.pprint(extract_natural_moves(page_text))

def extract_natural_moves(page_text: str):
    natural_moves_list = []
    natural_moves_raw_text = re.search(r"==\s*レベルアップわざ\s*==(.|\s)*?== ", page_text).group()
    for row in natural_moves_raw_text.split("\n"):
        matched = re.search(r"\{\{learnlist/level8\|(\d*?)\|(.*?)\|", row)
        if matched != None:
            natural_moves_list.append(list(matched.groups()))
    return natural_moves_list

if __name__ == '__main__':
    main()
