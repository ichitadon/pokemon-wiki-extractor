import xmltodict
import re
from pprint import pprint
import sys
from pokemon_wiki_extractor_exception import MovesBasicInfoNotFoundError

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
        extract_moves_basic_info(page_text)

def extract_moves_basic_info(page_text):
    try:
        moves_basic_info_raw_text = re.search(r"\{\{わざ基本情報(.|\s)*?\}\}", page_text).group()
    except AttributeError:
        raise MovesBasicInfoNotFoundError

    moves_basic_info_pattern_dict = {
        'タイプ' : r"\|\s*タイプ =(.*)\n",
        '世代' : r"\|\s*世代 =(.*)\n",
        'SwSh可否' : r"\|\s*SwSh可否 =(.*)\n",
        '分類' : r"\|\s*分類 =(.*)\n",
        '威力' : r"\|\s*威力 =(.*)\n",
        '命中' : r"\|\s*命中 =(.*)\n",
        'PP' : r"\|\s*PP =(.*)\n",
        '範囲' : r"\|\s*範囲 =(.*)\n",
        '直接' : r"\|\s*直接 =(.*)\n",
        '急所' : r"\|\s*急所 =(.*)\n",
        '命中判定' : r"\|\s*命中判定 =(.*)\n",
        '追加効果' : r"\|\s*追加効果 =(.*)\n",
        '守' : r"\|\s*守 =(.*)\n",
        '守5' : r"\|\s*守5 =(.*)\n",
        '王2' : r"\|\s*王2 =(.*)\n",
        '王3' : r"\|\s*王3 =(.*)\n",
        '王5' : r"\|\s*王5 =(.*)\n",
        'マ' : r"\|\s*マ =(.*)\n",
        'マ5' : r"\|\s*マ5 =(.*)\n",
        '横' : r"\|\s*横 =(.*)\n",
        '横5' : r"\|\s*横5 =(.*)\n",
        'オウム' : r"\|\s*オウム =(.*)\n",
        'オウム6' : r"\|\s*オウム6 =(.*)\n",
        'パレス' : r"\|\s*パレス =(.*)\n",
        '効果' : r"\|\s*効果 =(.*)\n",
        'Zワザ効果' : r"\|\s*Zワザ効果 =(.*)\n",
        'Zワザ威力' : r"\|\s*Zワザ威力 =(.*)\n",
        'ダイマックスわざ威力' : r"\|\s*ダイマックスわざ威力 =(.*)\n",
        'マシン' : r"\|\s*マシン =(.*)\n",
        'おしえ' : r"\|\s*おしえ =(.*)\n",
        'アピールタイプ' : r"\|\s*アピールタイプ =(.*)\n",
        'アピールタイプ注' : r"\|\s*アピールタイプ注 =(.*)\n",
        'アピールタイプ2' : r"\|\s*アピールタイプ2 =(.*)\n",
        'アピールタイプ2注' : r"\|\s*アピールタイプ2注 =(.*)\n",
        'アピールH' : r"\|\s*アピールH =(.*)\n",
        '妨害H' : r"\|\s*妨害H =(.*)\n",
        'アピール効果H' : r"\|\s*アピール効果H =(.*)\n",
        'コンボH' : r"\|\s*コンボH =(.*)\n",
        'アピールS' : r"\|\s*アピールS =(.*)\n",
        'アピール効果S' : r"\|\s*アピール効果S =(.*)\n",
        'アピールH2' : r"\|\s*アピールH2 =(.*)\n",
        '妨害H2' : r"\|\s*妨害H2 =(.*)\n",
        'アピール効果H2' : r"\|\s*アピール効果H2 =(.*)\n",
        'コンボH2' : r"\|\s*コンボH2 =(.*)\n",
    }
    print(moves_basic_info_raw_text)
    moves_basic_info_list = {}
    for pattern_name, pattern_str in moves_basic_info_pattern_dict.items() :
        moves_basic_info_list[pattern_name] = get_moves_basic_info_from_template(pattern_name, pattern_str, moves_basic_info_raw_text)
    pprint(moves_basic_info_list)
    return moves_basic_info_list

def get_moves_basic_info_from_template(pattern_name, pattern_str, target_text):
    moves_basic_info = None
    matched_block = re.search(pattern_str, target_text)
    if matched_block :
        moves_basic_info = matched_block.groups()[0].replace('[', '').replace(']', '')
    return moves_basic_info

if __name__ == '__main__':
    main()