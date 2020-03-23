import xmltodict
import re
import pprint
import sys
from pokemon_wiki_extractor_exception import PokedexBasicInfoNotFoundError

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

        for page in pages:
            page_text = page['revision']['text']['#text']
            try:
                extract_pokedex_data(page_text)
            except PokedexBasicInfoNotFoundError as e:
                print(f"Pokedex Basic Info is not found in this page : {page['title']}")
        
def extract_pokedex_data(page_text):
    # ポケモン図鑑基本情報
    pokedex_basic_info = extract_pokedex_basic_info(page_text)
    pprint.pprint(pokedex_basic_info)
    
    # 世代
    poke_generation = check_poke_generation(int(pokedex_basic_info['number']))
    print(poke_generation)

    # ポケモンずかんの説明文
    pprint.pprint(extract_pokedex_description(page_text), width=150)

    # 種族値
    pprint.pprint(extract_base_stats(page_text, poke_generation))

    # 進化
    pprint.pprint(extract_evolution(page_text))

def extract_evolution(page_text):
    pokedex_evolution_data_list = []
    pokedex_evolution_raw_text = re.search(r"==\s*進化(・フォルムチェンジ)?\s*==(.|\s)*?==", page_text).group()

    for row in pokedex_evolution_raw_text.split("\n"):
        tmp_dic = {}
        # 先頭のアスタリスクで階層の深さを判断する
        if "****" in row:
            tmp_dic['level'] = 4
        elif "***"  in row:
            tmp_dic['level'] = 3
        elif "**"  in row:
            tmp_dic['level'] = 2
        elif "*"  in row:
            tmp_dic['level'] = 1
        else:
            continue

        # リンク先記事とリンクテキストを分けている部分を除去する
        # e.g. [[XXXX|YYYY]]
        link_list = re.findall(r"\[\[(?!\|)(.*?)\]\]", row)
        for link in link_list:
            if "|" in link:
                replace_text = re.sub(r".*?\|", "", link)
                row = row.replace(link, replace_text)
        replaced_row = re.sub(r"\[\[(.*?)\]\]", r"\1", row)

        # 先頭のアスタリスクを除去する
        replaced_row = re.sub(r"\*+?\s*", "", replaced_row)

        # ボールドを除去する
        replaced_row = replaced_row.replace("\'\'\'", "")

        tmp_dic['text'] = replaced_row
        pokedex_evolution_data_list.append(tmp_dic)
        
    return pokedex_evolution_data_list

def check_poke_generation(national_pokedex_num: int):
    # gen1 (#1-151)
    # gen2 (#152-251)
    # gen3 (#252-386)
    # gen4 (#387-493)
    # gen5 (#494-649)
    # gen6 (#650-721)
    # gen7 (#722-809)
    # gen8 (#810-890)
    poke_generation = None
    if national_pokedex_num >= 1 and national_pokedex_num <= 151:
        poke_generation = "gen1"
    elif national_pokedex_num >= 152 and national_pokedex_num <= 251:
        poke_generation = "gen2"
    elif national_pokedex_num >= 252 and national_pokedex_num <= 386:
        poke_generation = "gen3"
    elif national_pokedex_num >= 387 and national_pokedex_num <= 493:
        poke_generation = "gen4"
    elif national_pokedex_num >= 494 and national_pokedex_num <= 649:
        poke_generation = "gen5"
    elif national_pokedex_num >= 650 and national_pokedex_num <= 721:
        poke_generation = "gen6"
    elif national_pokedex_num >= 722 and national_pokedex_num <= 809:
        poke_generation = "gen7"
    elif national_pokedex_num >= 810 and national_pokedex_num <= 890:
        poke_generation = "gen8"
    return poke_generation

def extract_base_stats(page_text, poke_generation):
    pokedex_base_stats_pattern_dict_gen1 = {
            'HP' : r"\| HP=(\d*)",
            'Attack' : r"\| 攻撃=(\d*)",
            'Block' : r"\| 防御=(\d*)",
            'Special' : r"\| 特殊=(\d*)",
            'Speed' : r"\| すばやさ=(\d*)"
    }

    pokedex_base_stats_pattern_dict_gen2 = {
            'HP' : r"\| HP=(\d*)",
            'Attack' : r"\| 攻撃=(\d*)",
            'Block' : r"\| 防御=(\d*)",
            'Contact' : r"\| 特攻=(\d*)",
            'Diffence' : r"\| 特防=(\d*)",
            'Speed' : r"\| すばやさ=(\d*)"
    }

    pokedex_base_stats_list = {}
    pokedex_base_stats_raw_text = re.search(r"==\s*種族値\s*==(.|\s)*?== ダメージ倍率 ==", page_text).group()
    pokedex_base_stats_text_list = re.findall(r"(.*)\n(\{\{種族値(.|\s)*?\}\})", pokedex_base_stats_raw_text)

    if pokedex_base_stats_text_list:
        for pokedex_base_stats_text_key_value in pokedex_base_stats_text_list:
            tmp_dict = {}
            key_value_list = list(pokedex_base_stats_text_key_value)
            for pattern_name, pattern_str in pokedex_base_stats_pattern_dict_gen2.items() :
                tmp_dict[pattern_name] = get_pokedex_base_stats_from_text(pattern_str, key_value_list[1])
            pokedex_base_stats_list[create_base_stats_list_key(key_value_list[0])] = tmp_dict

    if poke_generation == "gen1":
        tmp_dict = {}
        pokedex_base_stats_text_list_gen1 = re.search(r"(.*)\n(\{\{古種族値(.|\s)*?\}\})", pokedex_base_stats_raw_text).group()
        for pattern_name, pattern_str in pokedex_base_stats_pattern_dict_gen1.items() :
            tmp_dict[pattern_name] = get_pokedex_base_stats_from_text(pattern_str, pokedex_base_stats_text_list_gen1)
        pokedex_base_stats_list['第1世代'] = tmp_dict

    return pokedex_base_stats_list

def create_base_stats_list_key(key_seed):
    replaced_key_seed = key_seed.replace("\'\'\'", "").replace("===", "").replace(" ", "").replace("*", "")
    key = ""
    if replaced_key_seed == "":
        key = "第8世代"
    else:
        key = replaced_key_seed
    return key

def get_pokedex_base_stats_from_text(pattern_str, target_text):
    base_stats = ""
    matched_block = re.search(pattern_str, target_text)
    if matched_block:
        base_stats = matched_block.groups()[0]
    return base_stats

def extract_pokedex_description(page_text: str):
    pokedex_description_raw_text = re.search(r"== ポケモンずかんの説明文 ==(.|\s)*?== ", page_text).group().replace("\u3000", " ")
    pokedex_description_dict_kanji = {}
    pokedex_description_dict_hiragana = {}
    pokedex_description_dict_mega_kanji = {}
    pokedex_description_dict_mega_hiragana = {}
    pokedex_description_dict_gigantamax_kanji = {}
    pokedex_description_dict_gigantamax_hiragana = {}
    pokedex_description_dict_alola_form_kanji = {}
    pokedex_description_dict_alola_form_hiragana = {}
    pokedex_description_dict_galar_form_kanji = {}
    pokedex_description_dict_galar_form_hiragana = {}

    # バージョン情報の退避先
    # 1行で複数バージョンが抽出される場合があるため一時保存が必要
    # ex. ロコン -> 赤・緑、ファイアレッド、Y、ソード
    version_list = []
    # フラグ
    sub_category_name = None

    for text in pokedex_description_raw_text.split('\n'):
        if ";" in text:
            version_list = []
            tmp_list = re.findall(r"\|(.+?)\]\]", text)
            for version_text in tmp_list:
                for splited_version_text in version_text.split("・"):
                    version_list.append(splited_version_text)
            # フラグの再初期化
            sub_category_name = None
        elif ":" in text:
            if "(漢字)" in text:
                description = text.replace(":", "").replace("(漢字)", "").strip()
                if sub_category_name == "gigantamax":
                    pokedex_description_dict_gigantamax_kanji['キョダイマックス'] = description
                elif sub_category_name == "alola":
                    for version in version_list: 
                        pokedex_description_dict_alola_form_kanji[version] = description
                elif sub_category_name == "galar":
                    for version in version_list: 
                        pokedex_description_dict_galar_form_kanji[version] = description
                elif sub_category_name != None:
                    pokedex_description_dict_mega_kanji[sub_category_name] = description
                else:
                    for version in version_list: 
                        pokedex_description_dict_kanji[version] = description
            elif "\'\'\'メガ" in text:
                sub_category_name = text.replace("\'\'\'", "").replace(":", "")
            elif "\'\'\'キョダイマックス" in text:
                sub_category_name = "gigantamax"
            elif "\'\'\'アローラのすがた" in text:
                sub_category_name = "alola"
            elif "\'\'\'ガラルのすがた" in text:
                sub_category_name = "galar"
            else:
                description = text.replace(":", "").strip()
                if sub_category_name == "gigantamax":
                    pokedex_description_dict_gigantamax_hiragana['キョダイマックス'] = description
                elif sub_category_name == "alola":
                    for version in version_list: 
                        pokedex_description_dict_alola_form_hiragana[version] = description
                elif sub_category_name == "galar":
                    for version in version_list: 
                        pokedex_description_dict_galar_form_hiragana[version] = description
                elif sub_category_name != None:
                    pokedex_description_dict_mega_hiragana[sub_category_name] = description
                else:
                    for version in version_list: 
                        pokedex_description_dict_hiragana[version] = description

    pokedex_description = {}
    pokedex_description['normal_kanji'] = pokedex_description_dict_kanji
    pokedex_description['normal_hiragana'] = pokedex_description_dict_hiragana
    pokedex_description['mega_evolution_kanji'] = pokedex_description_dict_mega_kanji
    pokedex_description['mega_evolution_hiragana'] = pokedex_description_dict_mega_hiragana
    pokedex_description['gigantamax_kanji'] = pokedex_description_dict_gigantamax_kanji
    pokedex_description['gigantamax_hiragana'] = pokedex_description_dict_gigantamax_hiragana
    pokedex_description['alola_form_kanji'] = pokedex_description_dict_alola_form_kanji
    pokedex_description['alola_form_hiragana'] = pokedex_description_dict_alola_form_hiragana
    pokedex_description['galar_form_kanji'] = pokedex_description_dict_galar_form_kanji
    pokedex_description['galar_form_hiragana'] = pokedex_description_dict_galar_form_hiragana
    return pokedex_description

def extract_pokedex_basic_info(page_text):
    try:
        pokedex_basic_info_raw_text = re.search(r"\{\{ポケモン図鑑基本情報(.|\s)*?\}\}", page_text).group()
    except AttributeError:
        raise PokedexBasicInfoNotFoundError
    pokedex_basic_info_pattern_dict = {
        'name_jp' : r"\|\s*名=(.*)\n",
        'tmromaji' : r"\|\s*tmromaji=(.*)\n",
        'name_en' : r"\|\s*英語名=(.*)\n",
        'number' : r"\|\s*number=(.*)\n",
        'ndex' : r"\|\s*ndex=(.*)\n",
        'jdex' : r"\|\s*jdex=(.*)\n",
        'hdex' : r"\|\s*hdex=(.*)\n",
        'sdex' : r"\|\s*sdex=(.*)\n",
        'j2dex' : r"\|\s*j2dex=(.*)\n",
        'idex' : r"\|\s*idex=(.*)\n",
        'i2dex' : r"\|\s*i2dex=(.*)\n",
        'ckdex' : r"\|\s*ckdex=(.*)\n",
        'adex' : r"\|\s*adex=(.*)\n",
        'adexm' : r"\|\s*adexm=(.*)\n",
        'adexa' : r"\|\s*adexa=(.*)\n",
        'adexu' : r"\|\s*adexu=(.*)\n",
        'adexp' : r"\|\s*adexp=(.*)\n",
        'adex2' : r"\|\s*adex2=(.*)\n",
        'adexm2' : r"\|\s*adexm2=(.*)\n",
        'adexa2' : r"\|\s*adexa2=(.*)\n",
        'adexu2' : r"\|\s*adexu2=(.*)\n",
        'adexp2' : r"\|\s*adexp2=(.*)\n",
        'gdex' : r"\|\s*gdex=(.*)\n",
        'type_num' : r"\|\s*type数=(.*)\n",
        'type1' : r"\|\s*type1=(.*)\n",
        'type2' : r"\|\s*type2=(.*)\n",
        'category' : r"\|\s*分類=(.*)\n",
        'height' : r"\|\s*高さ=(.*)\n",
        'weight' : r"\|\s*重さ=(.*)\n",
        'ability_num' : r"\|\s*特性数=(.*)\n",
        'ability1' : r"\|\s*特性1=(.*)\n",
        'ability2' : r"\|\s*特性2=(.*)\n",
        'hidden_ability' : r"\|\s*隠れ特性=(.*)\n",
        'egggroup_num' : r"\|\s*egggroup数=(.*)\n",
        'egggroup1' : r"\|\s*egggroup1=(.*)\n",
        'egggroup2' : r"\|\s*egggroup2=(.*)\n",
        'eggcycle' : r"\|\s*タマゴのサイクル数=(.*)\n",
        'effort_value' : r"\|\s*獲得努力値=(.*)\n",
        'base_experience_gen4' : r"\|\s*基礎経験値4=(.*)\n",
        'base_experience_gen5' : r"\|\s*基礎経験値5=(.*)\n",
        'base_experience_gen7' : r"\|\s*基礎経験値7=(.*)\n",
        'base_experience_gen8' : r"\|\s*基礎経験値8=(.*)\n",
        'last_experience' : r"\|\s*最終経験値=(.*)\n",
        'gender' : r"\|\s*性別=(.*)\n",
        'gender_ratio_male' : r"\|\s*オス=(.*)\n",
        'gender_ratio_female' : r"\|\s*メス=(.*)\n",
        'catch_rate' : r"\|\s*捕捉率=(.*)\n",
        'base_friendship_gen7' : r"\|\s*初期なつき度=(.*)\n",
        'base_friendship_gen8' : r"\|\s*初期なかよし度=(.*)\n",
        'lpdex' : r"\|\s*lpdex=(.*)\n",
        'pokedex_color' : r"\|\s*図鑑の色=(.*)\n",
        'footnote' : r"\|\s*脚注=(.*)\n",
    }
    pokedex_basic_info_list = {}
    for pattern_name, pattern_str in pokedex_basic_info_pattern_dict.items() :
        pokedex_basic_info_list[pattern_name] = get_pokedex_basic_info_from_template(pattern_str, pokedex_basic_info_raw_text)
    return pokedex_basic_info_list

def get_pokedex_basic_info_from_template(pattern_str, target_text):
    pokedex_basic_info = ""
    matched_block = re.search(pattern_str, target_text)
    if matched_block :
        pokedex_basic_info = matched_block.groups()[0].replace('[', '').replace(']', '')
    return pokedex_basic_info

if __name__ == '__main__':
    main()