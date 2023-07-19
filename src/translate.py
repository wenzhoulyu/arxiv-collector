import urllib.request
import urllib.parse
import json
from deep_translator import GoogleTranslator
import abc


class TranslatorBase(abc.ABC):
    
    @abc.abstractmethod
    def translate(self, text: str) -> str:
        pass


class YouDao(TranslatorBase):
    def __init__(self):
        self.url = "http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule"
        
        # 注意head文件！
        self.head = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36 LBBROWSER"
    
    def translate(self, text: str) -> str:
        data = {}
        data['i'] = text
        data['from'] = 'en'
        data['to'] = 'ch'
        data['smartresult'] = 'dict'
        data['client'] = 'fanyideskweb'
        data['datasalt'] = '1531398987689'
        data['sign'] = 'b2116a1fa17e3c04da517b8e8282fed8'
        data['doctype'] = "json"
        data['version'] = '2.1'
        data['keyfrom'] = 'fanyi.web'
        data['action'] = 'FY_BY_CLICKBUTTION'
        data['typoResult'] = 'true'
        # 转码
        data = urllib.parse.urlencode(data).encode("utf-8")
        # 打开链接
        req = urllib.request.Request(self.url, data)
        req.add_header("User-Agent", self.head)
        response = urllib.request.urlopen(req)
        
        html = response.read().decode("utf-8")
        
        target = json.loads(html)
        # print(target["translateResult"])
        # exit()
        result = ''
        for tgt in target["translateResult"][0]:
            result += tgt["tgt"]
        return result


class Google(TranslatorBase):
    def __init__(self):
        # here pls set your own proxy
        proxies_example = {
            "https": "127.0.0.1:50415",
            "http": "127.0.0.1:50415"
        }
        self.translator = GoogleTranslator(source='auto', target='zh-CN', proxies=proxies_example)
    
    def translate(self, text: str) -> str:
        result = self.translator.translate(text).encode('utf-8').decode('utf-8')
        return result
