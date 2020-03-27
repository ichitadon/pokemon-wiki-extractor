import requests
import sys

def export_csv_data_from_pokemon_wiki(page_name: str, output_file_path: str):
    data = {
    'catname': '',
    'pages': page_name,
    'curonly': '1',
    'wpDownload': '1',
    'wpEditToken': '+\\',
    'title': '特別:データ書き出し'
    }

    response = requests.post('https://wiki.xn--rckteqa2e.com/wiki/%E7%89%B9%E5%88%A5:%E3%83%87%E3%83%BC%E3%82%BF%E6%9B%B8%E3%81%8D%E5%87%BA%E3%81%97', data=data)
    
    with open(output_file_path, mode='w') as f:
        f.write(response.text)

def main():
    args = sys.argv
    export_csv_data_from_pokemon_wiki(args[1], args[2])

if __name__ == '__main__':
    main()
