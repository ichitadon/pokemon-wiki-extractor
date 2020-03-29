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

        page_title = pages[int(args[2])]['title']
        print(page_title)
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
        '効果' : r"\|\s*効果 =((.|\s)*?)\|(\s|マシン)",
        'Zワザ効果' : r"\|\s*Zワザ効果 =(.*)\n",
        'Zワザ威力' : r"\|\s*Zワザ威力 =(.*)\n",
        'ダイマックスわざ威力' : r"\|\s*ダイマックスわざ威力 =(.*)\n",
        'マシン' : r"\|\s*マシン\s*=(.*)\n",
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
    moves_basic_info = ""
    matched_block = re.search(pattern_str, target_text)
    if matched_block :
        # テキスト中のWiki記法や不要な空白を削除する
        # e.g. [[AAA|BBB]]=>BBB
        matched_text = delete_links(matched_block.groups()[0].strip())
        # コメントを削除する
        matched_text = delete_comments(matched_text)
        print(pattern_name)
        print(matched_text)
        # 「効果」の項目は改行を含む場合があるため個別処理で対応する
        if pattern_name == "効果":
            if "<br />" in matched_text:
                tmp_list = matched_text.split("<br />")
                moves_basic_info = tmp_list
            elif "<br/>" in matched_text:
                tmp_list = matched_text.split("<br/>")
                moves_basic_info = tmp_list
            elif "<br>" in matched_text:
                tmp_list = matched_text.split("<br>")
                moves_basic_info = tmp_list
            elif "\n" in matched_text:
                tmp_list = matched_text.split("\n")
                moves_basic_info = delete_list_specifier(tmp_list)
            else:
                tmp_list = []
                tmp_list.append(matched_text)
                moves_basic_info = tmp_list
        #「コンボ」または「コンボH2」の項目は<br>で区切られた単純なリストなので個別処理で対応する
        elif pattern_name == "コンボ" or pattern_name == "コンボH2":
            if "<br />" in matched_text:
                tmp_list = matched_text.split("<br />")
            elif "<br/>" in matched_text:
                tmp_list = matched_text.split("<br/>")
            elif "<br>" in matched_text:
                tmp_list = matched_text.split("<br>")
            else:
                tmp_list = []
                tmp_list.append(matched_text)
                moves_basic_info = tmp_list                
            moves_basic_info = tmp_list
        # その他の項目は改行を含まないので共通で処理する
        # TODO 処理を共通化する
        elif "<br" in matched_text:
            moves_basic_info = {}
            moves_basic_info = extract_moves_basic_info_from_item(r"<br\s?/?>→?", matched_text)
        elif "(" in matched_text:
            item_list = re.search(r"^(.*?)\((.*)\)", matched_text).groups()
            if item_list[0] != "":
                moves_basic_info = {}
                moves_basic_info[item_list[1]] = item_list[0]
            else:
                moves_basic_info = matched_text
        else:
            moves_basic_info = matched_text 
    return moves_basic_info

def split_text(pattern: str, target_text: str):
    return re.split(pattern, target_text)

def extract_moves_basic_info_from_item(pattern :str, target_text :str):
    tmp_list = split_text(r"<br\s?/?>→?", target_text)
    print(tmp_list)
    moves_basic_info = {}
    for row in tmp_list:
        item_list = re.search(r"^(.*?)\((.*)\)", row).groups()
        moves_basic_info[item_list[1]] = item_list[0]
    return moves_basic_info

def delete_comments(target_text):
    return re.sub(r"<\!\-\-\s*?.*?\s*\-\->", "", target_text)

def delete_links(target_text):
    splited_text_list = target_text.split("]]")
    result = ""
    for item in splited_text_list:
        tmp_text = re.sub(r"\[\[.*?\|", "", item)
        tmp_text = re.sub(r"\[\[", "", tmp_text)
        result = result + tmp_text
    return result

def delete_list_specifier(target_list):
    result = []
    for item in target_list:
        result.append(re.sub(r"^\*", "", item))
    return result

if __name__ == '__main__':
    main()
