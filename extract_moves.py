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
        pprint.pprint(extract_machine_moves(page_text))
        pprint.pprint(extract_egg_moves(page_text))
        pprint.pprint(extract_tutor_moves(page_text))

def extract_natural_moves(page_text: str):
    natural_moves_list = []
    natural_moves_raw_text = re.search(r"==\s*レベルアップわざ\s*==(.|\s)*?== ", page_text).group()
    for row in natural_moves_raw_text.split("\n"):
        matched = re.search(r"\{\{learnlist/level8\|(\d*?)\|(.*?)\|", row)
        if matched != None:
            natural_moves_list.append(list(matched.groups()))
    return natural_moves_list

def extract_machine_moves(page_text: str):
    machine_moves_list = []
    machine_moves_raw_text = re.search(r"==\s*\[\[わざマシン\]\]・\[\[わざレコード\]\]わざ\s*==(.|\s)*?== ", page_text).group()
    for row in machine_moves_raw_text.split("\n"):
        matched = re.search(r"\{\{learnlist/tm8\|(.*?)\|(.*?)\|", row)
        if matched != None:
            machine_moves_list.append(list(matched.groups()))
    return machine_moves_list

def extract_egg_moves(page_text: str):
    egg_moves_list = {}
    egg_moves_raw_text = re.search(r"==\s*\[\[タマゴわざ\]\]\s*==(.|\s)*?== ", page_text).group().replace("<br />", "")
    for row in egg_moves_raw_text.split("\n"):
        matched = re.search(r"\{\{learnlist/breed8\|(\{\{MSP\|.+?\}\})\|(.*?)\|", row)
        if matched != None:
            parents_list = []
            parents_raw_text = matched.groups()[0]
            parents_matched_list = re.findall(r"\{\{MSP\|(\d*?)\|(.*?)\}\}", parents_raw_text)
            for result_tuple in parents_matched_list:
                result_list = list(result_tuple)
                parents_list.append(dict(ndex=result_list[0], name=result_list[1]))
            egg_moves_list[matched.groups()[1]] = parents_list
    return egg_moves_list

def extract_tutor_moves(page_text: str):
    tutor_moves_list = []
    tutor_moves_raw_text = re.search(r"==\s*\[\[わざおしえ人\|人から教えてもらえる\]\]わざ\s*==(.|\s)*?<noinclude>", page_text).group()
    for row in tutor_moves_raw_text.split("\n"):
        matched = re.search(r"\{\{learnlist/tutor8\|(.*?)\|", row)
        if matched != None:
            tutor_moves_list.append(matched.groups()[0])
    return tutor_moves_list

if __name__ == '__main__':
    main()
