import xmltodict
import re
from pprint import pprint
import sys
from pokemon_wiki_extractor_exception import MovesBasicInfoNotFoundError, MovesDescriptionNotFoundError

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
            # page_text = page['revision']['text']['#text']
            # extract_moves_basic_info(page_text)

        page_title = pages[int(args[2])]['title']
        print(page_title)
        page_text = pages[int(args[2])]['revision']['text']['#text']
        moves_basic_info = extract_moves_basic_info(page_text)
        pprint(moves_basic_info)
        extract_moves_desctription(page_text)

def extract_moves_desctription(page_text):
    # コメントの削除
    page_text = delete_comments(page_text)

    try:
        page_text_search_result = re.search(r"== たたかうわざ ==(.|\s)*?== ", page_text)
        # `たたかうわざ` の見出しが無いパターンは、`説明文` で抽出する。
        if page_text_search_result == None:
            page_text_search_result = re.search(r"== 説明文 ==(.|\s)*?== ", page_text)
        moves_description_raw_text = page_text_search_result.group().replace("\u3000", " ")
    except AttributeError:
        raise MovesDescriptionNotFoundError

    print(moves_description_raw_text)

    moves_description_dict_kanji = {}
    moves_description_dict_hiragana = {}

    # バージョン情報の退避先
    # 1行で複数バージョンが抽出される場合があるため一時保存が必要
    # ex. ロコン -> 赤・緑、ファイアレッド、Y、ソード
    version_list = []

    if ";" in moves_description_raw_text:
        # `;` 区切りでの記法の場合、抽出対象ブロックがわからない
        # これに対応するために抽出対象ブロックの末尾を示す閉じ記号 `##` を付与する
        moves_description_signed_text = moves_description_raw_text.replace(";", "##;").replace("\n", "")
        
        # 末尾の閉じ記号を付与する
        moves_description_signed_text = re.sub(r"=+?\s$", "##", moves_description_signed_text)

        # 不要な閉じ記号と見出しを削除する
        moves_description_signed_text = re.sub("=+ (説明文|たたかうわざ) =+##", "", moves_description_signed_text)

        # 第七世代以降は `コンテストわざ` の項目が存在せず、一番最後の末尾の閉じ記号 `##` が付与されない
        # `##` が1つも存在しないことを判定理由にして `##` を付与する
        if not "##" in moves_description_signed_text:
            moves_description_signed_text = re.sub("==", "##", moves_description_signed_text)

        moves_description_list = re.findall(r";((.|\s)*?)##", moves_description_signed_text)

        for text in moves_description_list:
            splited_text_list = delete_links(text[0]).split(":")
            key = splited_text_list.pop(0)
            version_list = key.split("・")
            for version in version_list:
                for splited_text in splited_text_list:
                    splited_text = delete_br(splited_text)
                    if "(漢字)" in splited_text or "(漢字)" in key or has_kanji(splited_text):
                        moves_description_dict_kanji[version.replace("(漢字)", "").strip()] = splited_text.replace("(漢字)", "").strip()
                    else:
                        moves_description_dict_hiragana[version.strip()] = splited_text.strip()
        pprint(moves_description_dict_kanji)
        pprint(moves_description_dict_hiragana)
    elif "*" in moves_description_raw_text:
        moves_description_list = re.findall(r"\*\s(.*?)\n", moves_description_raw_text)

        for text in moves_description_list:
            splited_text_list = split_text(r"[:：]",delete_links(text))
            key = splited_text_list[0]
            version_list = key.split("・")
            for version in version_list:
                for splited_text in splited_text_list:
                    splited_text = delete_br(splited_text)
                    if "(漢字)" in splited_text or "(漢字)" in key or has_kanji(splited_text):
                        moves_description_dict_kanji[version.replace("(漢字)", "").strip()] = splited_text.replace("(漢字)", "").strip()
                    else:
                        moves_description_dict_hiragana[version.strip()] = splited_text.strip()
        pprint(moves_description_dict_kanji)
        pprint(moves_description_dict_hiragana)

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
        '効果' : r"\|\s*効果 =((.|\s)*?)(\}\}|\|(\s|マシン))",
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
    moves_basic_info_list = {}
    for pattern_name, pattern_str in moves_basic_info_pattern_dict.items() :
        moves_basic_info_list[pattern_name] = get_moves_basic_info_from_template(pattern_name, pattern_str, moves_basic_info_raw_text)
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
    moves_basic_info = {}
    canNotMakeDict = False
    for row in tmp_list:
        # 無駄なカッコが存在する場合に削除する対応
        # e.g. メガドレインの「PP」
        #      10(第三世代まで)\n→15(第四世代以降)\n(10(ピカブイのみ))
        if re.search(r"^\(.*\)$", row) != None:
            row = re.sub(r"(^\(|\)$)", "", row)
        matched_item_list = re.search(r"^(.+?)[\(（](.*)[\)）]", row)
        if matched_item_list != None:
            item_list = matched_item_list.groups()
            moves_basic_info[item_list[1]] = item_list[0]
        else:
            # TODO: ソーラービームの「威力」の記載の暫定対応
            # 辞書形式にデータを保持できないのでリストで保持させる
            # 数が少ないのであれば個別で対応する
            # e.g. `(ピカブイではXXX)`
            canNotMakeDict = True
    
    # コアパニッシャーのわざおしえのための特別処理
    if target_text == "ジガルデ・コア<br />(ポニのこどう・ハプウの家)":
        tmp_list = [delete_br(target_text)]
    
    if canNotMakeDict:
        moves_basic_info = []
        for row in tmp_list:
            # 無駄なカッコが存在する場合に削除する対応
            # e.g. メガドレインの「威力」
            #      40<br />(75([[ポケットモンスター Let's Go! ピカチュウ・Let's Go! イーブイ|ピカブイ]]のみ))
            if re.search(r"^\(.*\)$", row) != None:
                row = re.sub(r"(^\(|\)$)", "", row)
            moves_basic_info.append(row)
    return moves_basic_info

def has_kanji(target_text):
    result = False
    matcher = re.compile('[\u2E80-\u2FDF\u3005-\u3007\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF\U00020000-\U0002EBEF]+')
    if matcher.search(target_text) != None:
        result = True
    return result

def delete_comments(target_text):
    return re.sub(r"<\!\-\-\s*?(.|\s)*?\s*\-\->", "", target_text)

def delete_links(target_text):
    splited_text_list = target_text.split("]]")
    result = ""
    for item in splited_text_list:
        tmp_text = re.sub(r"\[\[.*?\|", "", item)
        tmp_text = re.sub(r"\[\[", "", tmp_text)
        result = result + tmp_text
    return result

def delete_br(target_text):
    return re.sub(r"<br\s?/?>", "", target_text)

def delete_list_specifier(target_list):
    result = []
    for item in target_list:
        result.append(re.sub(r"^\*", "", item))
    return result

if __name__ == '__main__':
    main()
