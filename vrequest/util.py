import re
import json
import urllib.parse as ps
import inspect
import builtins
from lxml import etree


def format_headers_str(headers:str):
    # return dict
    headers = headers.splitlines()
    headers = [re.split(':|=',i,1) for i in headers if i.strip() and ':' in i or '=' in i]
    headers = {k.strip():v.strip() for k,v in headers}
    return headers


def format_headers_code(headers):
    # headers 参数可以是字符串，可以是字典
    # return str
    assert type(headers) in (str, dict)
    if type(headers) is str:
        headers = format_headers_str(headers)
    ret = 'headers = ' + json.dumps(headers,indent=4,ensure_ascii=False)
    for name in headers:
        if name.lower() == 'cookie':
            q = '(\n'
            p =[]
            for i in headers[name].split('; '): p.append(i)
            for i in sorted(p):
                q += '        "'+i+'; "\n'
            q += '    )'
            ret = ret.replace('"'+headers[name]+'"',q)
    return ret


def format_body_str(body:str):
    # return dict
    body = body.splitlines()
    body = [re.split(':|=',i,1) for i in body if i.strip() and ':' in i or '=' in i]
    body = {k.strip():v.strip() for k,v in body}
    return body


def format_body_code(body):
    # body 参数可以是字符串，可以是字典
    # return str
    assert type(body) in (str, dict)
    if type(body) is str:
        body = format_body_str(body)
    return 'body = ' + json.dumps(body,indent=4,ensure_ascii=False)



def format_url(url:str):
    # return str
    return ''.join([i.strip() for i in url.splitlines()])


def format_url_show(url:str):
    # return str
    indent = 4
    url = ps.unquote(url)
    pls = re.findall('\?[^&]*|&[^&]*',url)
    pms = [None]
    for i in pls:
        url = url.replace(i,'')
        if len(i) > 50 and ',' in i:
            _pms = []
            for j in i.split(','):
                j = ' '*indent + j + ','
                _pms.append(j)
            _pms[-1] = _pms[-1][:-1]
            pms += _pms
        else:
            pms.append(i)
    pms[0] = url
    return '\n'.join(pms)



def format_url_code(url:str):
    # return str
    indent = 4
    url = ps.unquote(url)
    pls = re.findall('\?[^&]*|&[^&]*',url)
    pms = ['url = (',None]
    def symbol(strs):
        if '\'' not in strs:
            return '\''
        if '"' not in strs:
            return '"'
        if '\'\'\'' not in strs:
            return '\'\'\''
        return '"""'
    for i in pls:
        url = url.replace(i,'')
        if len(i) > 50 and ',' in i:
            _pms = []
            for j in i.split(','):
                j = (j + ',').join([symbol(j)]*2)
                j = ' '*2*indent + j
                _pms.append(j)
            _pms[-1] = _pms[-1][:-2] + _pms[-1][-1]
            pms += _pms
        else:
            i = i.join([symbol(i)]*2)
            i = ' '*indent + i
            pms.append(i)
    u = symbol(url)
    pms[1] = ' '*indent + '{}{}{}'.format(u,url,u)
    pms.append(')')
    return '\n'.join(pms)



def format_req(method,c_url,c_headers,c_body):

    _format_get = '''
try:
    # 处理 sublime 执行时输出乱码
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
    sys.stdout._CHUNK_SIZE = 1
except:
    pass

import re
import json
import requests
from lxml import etree

def get_info():
    # 功能函数（对url里面的 param 进行编码操作）
    def quote_val(url):
        import urllib
        for i in re.findall('=([^=&]+)',url):
            url = url.replace(i,'{}'.format(urllib.parse.quote(i)))
        return url
    # 功能函数（解析解码格式）
    def parse_content_type(content):
        types = ['utf-8','gbk']
        try:
            import chardet
            types.append(chardet.detect(content)['encoding'])
        except:pass
        for tp in types:
            try:
                content = content.decode(tp)
                return tp, content
            except StopIteration:
                raise TypeError('not in {}'.format(types))
            except:
                continue
    # 生成请求参数函数
    def mk_url_headers():
        $c_url
        #url = quote_val(url) # 部分网页需要请求参数中的 param 保持编码状态，解开该注释即可
        $c_headers
        return url,headers

    url,headers = mk_url_headers()
    s = requests.get(url,headers=headers)
    tp, content = parse_content_type(s.content)
    print(s)
    print('decode type: {}'.format(tp))
    print('response length: {}'.format(len(s.content)))
$plus

get_info()

#
'''

    _format_post = '''
try:
    # 处理 sublime 执行时输出乱码
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
    sys.stdout._CHUNK_SIZE = 1
except:
    pass

import re
import json
import requests
from lxml import etree

def post_info():
    # 功能函数（对url里面的 param 进行编码操作）
    def quote_val(url):
        import urllib
        for i in re.findall('=([^=&]+)',url):
            url = url.replace(i,'{}'.format(urllib.parse.quote(i)))
        return url
    # 功能函数（解析解码格式）
    def parse_content_type(content):
        types = ['utf-8','gbk']
        try:
            import chardet
            types.append(chardet.detect(content)['encoding'])
        except:pass
        for tp in types:
            try:
                content = content.decode(tp)
                return tp, content
            except StopIteration:
                raise TypeError('not in {}'.format(types))
            except:
                continue
    # 生成请求参数函数
    def mk_url_headers_body():
        $c_url
        #url = quote_val(url) # 部分网页需要请求参数中的 param 保持编码状态，解开该注释即可
        $c_headers
        $c_body
        return url,headers,body

    url,headers,body = mk_url_headers_body()    
    #body = json.dumps(body) #极少情况需要data为string情况下的json数据，如需要解开该注释
    s = requests.post(url,headers=headers,data=body) 
    tp, content = parse_content_type(s.content)
    print(s)
    print('decode type: {}'.format(tp))
    print('response length: {}'.format(len(s.content)))
$plus

post_info()

#
'''

    func = lambda c_:''.join(map(lambda i:'        '+i+'\n',c_.splitlines()))
    c_url       = func(c_url).strip()
    c_headers   = func(c_headers).strip()
    c_body      = func(c_body).strip()
    if method == 'GET':
        _format = _format_get
        _format = _format.replace('$c_url',c_url)
        _format = _format.replace('$c_headers',c_headers)
    elif method == 'POST':
        _format = _format_post
        _format = _format.replace('$c_url',c_url)
        _format = _format.replace('$c_headers',c_headers)
        _format = _format.replace('$c_body',c_body)
    return _format.strip()


def format_request(method,c_url,c_headers,c_body):
    return format_req(method,c_url,c_headers,c_body).replace('$plus','')


def format_response(r_setting,c_set,c_content):

    
    # 请求部分的代码
    if r_setting is not None:
        method,c_url,c_headers,c_body = r_setting
        _format = format_req(method,c_url,c_headers,c_body)
    else:
        _format = ''
    _format = _format.strip()

    for i in c_set.splitlines():
        i = i.strip()
        func_code = None
        if i.startswith('<') and i.endswith('>'):
            if i.startswith('<normal_content:'):
                rt = re.findall('<normal_content:(.*)>', i)[0].strip()
                rt = rt if rt else '//html'
                from .tab import normal_content
                func_code = inspect.getsource(normal_content).strip()
                func_code += '\n\ncontent = normal_content(content, rootxpath="{}")\nprint(content)'.format(rt)
            if i.startswith('<xpath:'):
                xp = re.findall('<xpath:(.*)>', i)[0].strip()
                xp = xp if xp else '//html'
                func_code =("print('------------------------------ split ------------------------------')\n"
                            "tree = etree.HTML(content)\n"
                            "for x in tree.xpath('{}'):\n".format(xp) + 
                            "    strs = re.sub('\s+',' ',x.xpath('string(.)'))\n"
                            "    strs = strs[:40] + '...' if len(strs) > 40 else strs\n"
                            "    attr = '[ attrib ]: {} [ string ]: {}'.format(x.attrib, strs)\n"
                            "    print(attr)\n")
            if i.startswith('<auto_list_json:'):
                try:
                    func_code = get_json_code(c_content).strip()
                except:
                    import traceback
                    traceback.print_exc()
                    func_code = ''
        func = lambda c_:''.join(map(lambda i:'    '+i+'\n',c_.splitlines()))
        _format = _format.replace('$plus', '\n'+func(func_code)) if func_code is not None else _format
    _format = _format if '$plus' not in _format else _format.replace('$plus','')
    return _format.strip()


# 下面是通过字符串模糊查找xpath的函数
def get_simple_path_tail(e):
    root = e.getroottree()
    try:
        xp = root.getelementpath(e)
    except:
        return
    v = xp.count('/')
    # 优先找路径上的id和class项优化路径
    for i in range(v):
        xpa = xp.rsplit('/',i)[0]
        rke = '/'.join(xp.rsplit('/',i)[1:])
        ele = root.xpath(xpa)[0].attrib
        tag = root.xpath(xpa)[0].tag
        if 'id' in ele:
            key = '[@id="{}"]'.format(ele["id"])
            rke = '/'+rke if rke else ""
            val = '//{}{}{}'.format(xpa.rsplit('/',1)[1],key,rke)
            return xp,val,key
        if 'class' in ele:
            if ' ' in ele["class"] and not ele["class"].startswith(' '):
                elass = ele["class"].split(' ',1)[0]
            else:
                elass = ele["class"]
            key = '[@class="{}"]'.format(elass)
            rke = '/'+rke if rke else ""
            val = '//{}{}{}'.format(xpa.rsplit('/',1)[1],key,rke)
            if not elass.strip():
                continue
            return xp,val,key


# 对列表的优化处理
def get_simple_path_head(p,lilimit=5):
    # 先通过绝对xpath路径进行分块处理
    s = {}
    w = {}
    for xp, sxp, key in p:
        q = re.sub('\[\d+\]','',xp)#.rsplit('/',1)[0]
        if q not in s:
            s[q] = [[xp, sxp, key]]
        else:
            s[q].append([xp, sxp, key])
    rm = []
    for px in sorted(s,key=lambda i: -len(i)):
        xps,sxps,keys = zip(*s[px])
        if len(sxps) == len(set(sxps)): continue
        p = {}
        ls = list(set(keys))
        for j in s[px]:
            if j[2] not in p:
                p[j[2]] = [j]
            else:
                p[j[2]].append(j)
        for i in p:
            le = len(p[i])
            v = ''
            if le > lilimit:
                for idx in range(p[i][0][0].count('/')):
                    v = p[i][0][0].rsplit('/',idx)[0]
                    q = list(map(lambda i:i[0].startswith(v),p[i]))
                    if all(q):
                        break
                for idx,j in enumerate(p[i]):
                    a,b,c = j
                    t = '/{}{}'.format(a.replace(v,''),c) + b.split(c,1)[1]
                    t = t if t.startswith('//') else '/' + t
                    p[i][idx][1] = t
                    p[i][idx].append(px)
                    yield j

def get_xpath_by_str(strs, html_content):
    e = etree.HTML(html_content)
    q = []
    p = []
    for i in e.xpath('//*'):
        xps = get_simple_path_tail(i) 
        if xps:
            xp, sxp, key = xps
            if sxp not in q:
                q.append(xp)
                p.append([xp, sxp, key])
    p.sort(key=lambda i: -len(i[0]))
    p = get_simple_path_head(p)

    def instrs(strs,v):
        if type(strs) is str:
            return strs in v
        elif type(strs) in (tuple,list):
            for i in strs:
                if i in v:
                    return True

    for key, xp, sxp, px in p:
        v = e.xpath('string({})'.format(xp))
        v = re.sub('\s+',' ',v)
        v = v[:40] + '...' if len(v) > 40 else v
        v = '[{}] {}'.format(len(v),v)
        if instrs(strs,v):
            yield xp,v





# ==== 解析 json 格式的数据 ====

def get_parse_list(dicts):
    p = {}
    def parse_list(dicts,uri=''):
        if type(dicts) != dict:
            return
        for idi,i in enumerate(dicts):
            _uri = uri + "['{}']".format(i)
            iner = dicts[i]
            if type(iner) == list:
                if iner: 
                    p[_uri] = {}
                    p[_uri]['iner'] = iner
                    p[_uri]['lens'] = len(iner)
                for idj,j in enumerate(iner):
                    _urj = _uri + "[{}]".format(idj)
                    parse_list(j, _urj)
            elif type(iner) == dict:
                parse_list(iner, _uri)
    parse_list(dicts)
    return p

def get_max_len_list(p):
    templen = 0
    temp = None
    for i in p:
        lens = p[i]['lens']
        iner = p[i]['iner']
        if lens > templen:
            templen = lens
            temp = i, iner
    return templen, temp

def analisys_key_sort(p):
    lens, (okey, iner) = p
    allkeys = []
    for i in iner:
        for j in i:
            if j not in allkeys:
                allkeys.append(j)
    keyscores = []
    mx = 0
    for key in allkeys:
        mx = len(key) if len(key)>mx else mx
        temp = []
        for i in iner:
            val = i.get(key, '')
            temp.append(str(val))
        dupscore = len(set(temp))/float(lens)
        argvlens = len(''.join(temp))/5.
        # 第一个是重复度，越大越不重复，0~1
        # 第二个是平均字符串长度，
        keyscores.append([key, argvlens, dupscore, str(val)])
    return mx,okey,sorted(keyscores,key=lambda i:i[1:])

def format_json_parse_code(p,standard=True):
    # 这里将处理一些非典型的数据结构
    # 通常能解析的json列表的数据结构都是 list[dict1,dict2,...]，将这些当作标准解析结构
    # 不过也会有一些列表内部并非都是dict的数据结构，这时候就需要考虑一些别的方法进行格式化处理。
    if standard:
        mx,okey,sortkeys = analisys_key_sort(p)
        ret = '''jsondata = json.loads(content[content.find('{'):content.rfind('}')+1])\nfor i in jsondata%s:\n''' % okey
        indent = 4
        ret += ' '*indent + 'd = {}\n'
        for key,alen,dups,val in sortkeys:
            key1 = '_'+key if key in dir(builtins) or key in ['d','i','s','e','content'] else key
            _ret = ' '*indent + ('d["{} = i.get("{:<'+str(mx+3)+'}').format(('{:<'+str(mx+2)+'}').format(key1+'"]'),key+'")')
            _comment = ''
            for i in range(5):
                slen = 60
                sval = val[i*slen:(i+1)*slen]
                spre = ' '*len(_ret) if i != 0 else ''
                if not sval:
                    break
                _comment += spre + '# {:<20}\n'.format(sval.replace('\n','')) # 注释部分
            if not _comment:
                _comment = '\n'
            ret += (_ret + _comment).rstrip() + '\n'
        tail = ' '*indent + "print('------------------------------ split ------------------------------')\n"
        tail += ' '*indent + 'import pprint\n'
        tail += ' '*indent + 'pprint.pprint(d)\n'
        return ret + tail
    else:
        lens, (okey, iner) = p
        ret = '''jsondata = json.loads(content[content.find('{'):content.rfind('}')+1])\nfor i in jsondata%s:\n''' % okey
        indent = 4
        tail = ' '*indent + "print('------------------------------ split ------------------------------')\n"
        tail += ' '*indent + 'import pprint\n'
        tail += ' '*indent + 'pprint.pprint(i)\n'
        return ret + tail

def format_json_parse_show(p,standard=True):
    # 这里将处理一些非典型的数据结构
    # 通常能解析的json列表的数据结构都是 list[dict1,dict2,...]，将这些当作标准解析结构
    # 不过也会有一些列表内部并非都是dict的数据结构，这时候就需要考虑一些别的方法进行格式化处理。
    if standard:
        mx,okey,sortkeys = analisys_key_sort(p)
        ret = 'jsondata{}\n'.format(okey)
        ret += '='*(len(ret)-1) + '\n'
        for key,alen,dups,val in sortkeys:
            _ret = ('{:<'+str(mx)+'}').format(key)
            _comment = ''
            for i in range(5):
                slen = 60
                sval = val[i*slen:(i+1)*slen]
                spre = ' '*len(_ret) if i != 0 else ''
                if not sval:
                    break
                _comment += spre + ' # {:<20}\n'.format(sval.replace('\n','')) # 注释部分
            if not _comment:
                _comment = '\n'
            ret += (_ret + _comment).rstrip() + '\n'
        return ret
    else:
        lens, (okey, iner) = p
        ret = 'jsondata{}\n'.format(okey)
        ret += '='*(len(ret)-1) + '\n'
        for i in iner:
            ret += str(i) + '\n'
        return ret


def parse_json_content(content):
    if type(content) == str:
        json_content = json.loads(content[content.find('{'):content.rfind('}')+1])
    elif type(content) == bytes:
        json_content = json.loads(content[content.find(b'{'):content.rfind(b'}')+1])
    else:
        raise TypeError('unparse type {}'.format(type(s)))
    return json_content

def get_json_code(content):
    s = parse_json_content(content)
    p = get_parse_list(s)
    p = get_max_len_list(p)
    if p[0] == 0: return ''
    standard = True if all(map(lambda i:type(i)==dict,p[1][1])) else False
    return format_json_parse_code(p,standard)

def get_json_show(content):
    s = parse_json_content(content)
    p = get_parse_list(s)
    p = get_max_len_list(p)
    if p[0] == 0: return ''
    standard = True if all(map(lambda i:type(i)==dict,p[1][1])) else False
    return format_json_parse_show(p,standard)