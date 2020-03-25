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

        page_name = pages[int(args[2])]['title']
        page_text = pages[int(args[2])]['revision']['text']['#text']
        pprint.pprint(extract_natural_moves(page_text, page_name))
        pprint.pprint(extract_machine_moves(page_text, page_name))
        # pprint.pprint(extract_egg_moves(page_text))
        # pprint.pprint(extract_tutor_moves(page_text))

def extract_natural_moves(page_text: str, page_name: str):
    natural_moves_list = {}
    natural_moves_raw_text = re.search(r"==\s*レベルアップわざ\s*==(.|\s)*?==\s*\[\[わざマシン\]\]・\[\[わざレコード\]\]わざ", page_text).group()
    # 各フォーム抽出のための印 `##` を付与する
    natural_moves_raw_text = re.sub(r"\n==", r"\n##==", natural_moves_raw_text)
    # 付与した `##` を手掛かりにフォームを抽出する
    natural_moves_text_list = re.findall(r"====\s*(.*)?\s*====((.|\s)*?)##", natural_moves_raw_text)
    if len(natural_moves_text_list) == 0:
        natural_moves_text_list.append([page_name.replace("/第八世代のおぼえるわざ", ""), natural_moves_raw_text])
    for search_result_tuple in natural_moves_text_list:
        tmp_list = []
        for row in search_result_tuple[1].split("\n"):
            matched = re.search(r"\{\{learnlist/level8\|(\d*?)\|(.*?)\|", row)
            if matched != None:
                tmp_list.append(list(matched.groups()))
        natural_moves_list[search_result_tuple[0]] = tmp_list
    return natural_moves_list

def extract_machine_moves(page_text: str, page_name: str):
    machine_moves_list = {}
    machine_moves_raw_text = re.search(r"==\s*\[\[わざマシン\]\]・\[\[わざレコード\]\]わざ\s*==(.|\s)*?==\s*\[\[タマゴわざ\]\] ", page_text).group()
    # 各フォーム抽出のための印 `##` を付与する
    machine_moves_raw_text = re.sub(r"\n==", r"\n##==", machine_moves_raw_text)
    # 付与した `##` を手掛かりにフォームを抽出する
    machine_moves_text_list = re.findall(r"====\s*(.*)?\s*====((.|\s)*?)##", machine_moves_raw_text)
    if len(machine_moves_text_list) == 0:
        machine_moves_text_list.append([page_name.replace("/第八世代のおぼえるわざ", ""), machine_moves_raw_text])
    for search_result_tuple in machine_moves_text_list:
        tmp_list = []
        for row in search_result_tuple[1].split("\n"):
            matched = re.search(r"\{\{learnlist/tm8\|(.*?)\|(.*?)\|", row)
            if matched != None:
                tmp_list.append(list(matched.groups()))
        machine_moves_list[search_result_tuple[0]] = tmp_list
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
