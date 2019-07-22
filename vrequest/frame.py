
import requests

import io
import os
import re
import sys
import json
import zlib
import time
import hmac
import shutil
import base64
import hashlib
import tempfile
import traceback
import tkinter
import inspect
import zipfile
import urllib.parse as ps
import tkinter.messagebox
from tkinter import ttk
from tkinter import scrolledtext
from tkinter.font import Font
from tkinter.simpledialog import askstring
from binascii import a2b_hex, b2a_hex

try:
    from .root import DEFAULTS_HEADERS,root
except:
    from root import DEFAULTS_HEADERS,root

Text = scrolledtext.ScrolledText
#Text = tkinter.Text
Label = ttk.Label
Button = ttk.Button
Combobox = ttk.Combobox
Entry = ttk.Entry
Checkbutton = tkinter.Checkbutton

# 测试两种 Frame 效果
# Frame = ttk.Frame # ttk.Frame 没有 highlightthickness 这个参数
Frame = tkinter.Frame

frame_setting = {}

pdx = 0
pdy = 0
lin = 0

def request_window(setting=None):
    fr = Frame()
    ft = Font(family='Consolas',size=10)

    def change_method(*a):
        method = cbx.get()
        if method == 'POST':
            temp_fr2.pack(fill=tkinter.BOTH,expand=True,side=tkinter.BOTTOM)
        elif method == 'GET':
            temp_fr2.pack_forget()

    def test_code(*a):
        from .tab import create_test_code
        create_test_code()

    def scrapy_code(*a):
        from .tab import create_scrapy_code
        create_scrapy_code()


    def send_req(*a):
        from .tab import send_request
        send_request()

    temp_fr0 = Frame(fr)
    methods = ('GET','POST')
    cbx = Combobox(temp_fr0,width=10,state='readonly')
    cbx['values'] = methods     # 设置下拉列表的值
    cbx.current(0)
    cbx.pack(side=tkinter.RIGHT)
    cbx.bind('<<ComboboxSelected>>', change_method)
    temp_fr0.pack(fill=tkinter.X)
    btn1 = Button(temp_fr0, text='发送请求[Ctrl+r]', command=send_req)
    btn1.pack(side=tkinter.RIGHT)
    lab1 = Label(temp_fr0, text='请尽量发送请求后生成代码，那样会有更多功能：')
    lab1.pack(side=tkinter.LEFT)
    btn6 = Button(temp_fr0, text='生成[requests]代码[Alt+c]', command=test_code)
    btn6.pack(side=tkinter.LEFT)
    btn7 = Button(temp_fr0, text='生成[scrapy]代码[Alt+s]', command=scrapy_code)
    btn7.pack(side=tkinter.LEFT)

    temp_fr1 = Frame(fr,highlightthickness=lin)
    temp_fold_fr1 = Frame(temp_fr1)
    temp_fold_fr2 = Frame(temp_fr1)
    lb1 = Label (temp_fold_fr1,text='url')
    tx1 = Text  (temp_fold_fr1,height=1,width=1,font=ft)
    lb1.pack(side=tkinter.TOP)
    tx1.pack(fill=tkinter.BOTH,expand=True,side=tkinter.TOP,padx=pdx,pady=pdy)

    lb2 = Label (temp_fold_fr2,text='headers')
    tx2 = Text  (temp_fold_fr2,height=1,width=1,font=ft)
    lb2.pack(side=tkinter.TOP)
    tx2.pack(fill=tkinter.BOTH,expand=True,side=tkinter.TOP,padx=pdx,pady=pdy)
    temp_fold_fr1.pack(fill=tkinter.BOTH,expand=True,side=tkinter.LEFT)
    temp_fold_fr2.pack(fill=tkinter.BOTH,expand=True,side=tkinter.LEFT)
    temp_fr1.pack(fill=tkinter.BOTH,expand=True,side=tkinter.TOP)


    temp_fr2 = Frame(fr,highlightthickness=lin)
    lb3 = Label (temp_fr2,text='body')
    tx3 = Text  (temp_fr2,height=1,width=1,font=ft)
    lb3.pack(side=tkinter.TOP)
    tx3.pack(fill=tkinter.BOTH,expand=True,padx=pdx,pady=pdy)
    if setting and setting.get('method') == 'POST':
        cbx.current(methods.index('POST'))
        temp_fr2.pack(fill=tkinter.BOTH,expand=True,side=tkinter.BOTTOM)

    if setting:
        tx1.insert(0.,setting['url'].strip())
        tx2.insert(0.,setting['headers'].strip())
        tx3.insert(0.,setting['body'].strip())
    else:
        tx2.insert(0.,DEFAULTS_HEADERS.strip())

    frame_setting[fr] = {}
    frame_setting[fr]['type'] = 'request'
    frame_setting[fr]['fr_method'] = cbx
    frame_setting[fr]['fr_url'] = tx1
    frame_setting[fr]['fr_headers'] = tx2
    frame_setting[fr]['fr_body'] = tx3
    return fr


def response_window(setting=None):

    '''
    这里的 setting 结构应该就是一个请求信息的数据结构
    并且应该是整理好数据类型的字典，在这里请求任务结束之后返回的数据
    就按照展示结构放在 response 的结构框架里面。
    url     :str
    method  :str
    headers :dict
    body    :str
    '''

    def insert_txt(fr_txt, txt):
        fr_txt.delete(0.,tkinter.END)
        fr_txt.insert(0.,re.sub('[\uD800-\uDBFF][\uDC00-\uDFFF]|[\U00010000-\U0010ffff]','',txt))

    doc0 = '''列表解析路径方式
冒号后面配置的的内容为 xpath
<xpath:>
*组合功能！
如果先使用了 “分析xpath” 功能后解析到路径
那么使用该功能时会自动弹出选择窗口
选择窗中的内容为自动解析xpath中解析出的 xpath
'''

    doc1 = '''纯文字内容解析
解析某个 xpath 路径下面的所有文字字符串，默认是 //html 路径下的所有文字
<normal_content://html>
'''

    doc2 = '''根据字符串自动分析 xpath 路径
一般用于列表形式的路径
通常来说这个功能针对简单的网页结构还勉强有用，并非一定能够解析
所以一些比较复杂的网页或许还是需要考虑自省分析xpath。

冒号后面配置需要处理的字符串
多个字符串可以通过空格分隔
eg.:
    <auto_list_xpath:白天 黑夜>
不写则为查找所有 "string(.)" (xpath语法)
能解析出含有非空字符串的内容路径
'''

    doc3 = '''简单分析json数据内容
找出最长的list进行初步的迭代分析，并给出分析结果在输出框
<auto_list_json:>
'''

    doc4 = '''生成scrapy代码
如果存在 “解析xpath”、“自动json” 或 “获取纯文字” 状态
则会在生成代码中包含相应的代码
'''

    doc5 = '''生成requests代码
如果存在 “解析xpath”、“自动json” 或 “获取纯文字” 状态
则会在生成代码中包含相应的代码
'''

    def document(*a):
        method = cbx.get()
        if methods.index(method) == 0:
            insert_txt(tx3,doc0)
        if methods.index(method) == 1:
            insert_txt(tx3,doc1)
        if methods.index(method) == 2:
            insert_txt(tx3,doc2)
        if methods.index(method) == 3:
            insert_txt(tx3,doc3)
        if methods.index(method) == 4:
            insert_txt(tx3,doc4)
        if methods.index(method) == 5:
            insert_txt(tx3,doc5)
        switch_show(onlyshow=True)

    fr = Frame()
    ft = Font(family='Consolas',size=10)
    def switch_show(*a, onlyshow=False):
        try:
            temp_fold_fr2.pack_info()
            packed = True
        except:
            packed = False
        if packed:
            if not onlyshow:
                temp_fold_fr2.pack_forget()
        else:
            temp_fold_fr2.pack(fill=tkinter.BOTH,expand=True,side=tkinter.LEFT)

    def html_pure_text(*a):
        from .tab import get_html_pure_text
        get_html_pure_text()

    def xpath_elements(*a):
        from .tab import get_xpath_elements
        get_xpath_elements()

    def auto_xpath(*a):
        from .tab import get_auto_xpath
        get_auto_xpath()

    def auto_json(*a):
        from .tab import get_auto_json
        get_auto_json()

    def test_code(*a):
        from .tab import create_test_code
        create_test_code()

    def scrapy_code(*a):
        from .tab import create_scrapy_code
        create_scrapy_code()

    temp_fr0 = Frame(fr)
    lab1 = Label(temp_fr0, text='功能说明：')
    lab1.pack(side=tkinter.LEFT)
    methods = ('(Alt+x) 解析xpath','(Alt+d) 获取纯文字','(Alt+f) 分析xpath','(Alt+z) 自动json', '(Alt+s) 生成 scrapy代码', '(Alt+c) 生成 requests代码')
    cbx = Combobox(temp_fr0,width=18,state='readonly')
    cbx['values'] = methods     # 设置下拉列表的值
    cbx.current(0)
    cbx.pack(side=tkinter.LEFT)
    cbx.bind('<<ComboboxSelected>>', document)
    temp_fr0.pack(fill=tkinter.X)
    btn3 = Button(temp_fr0, text='分析xpath', command=auto_xpath)
    btn3.pack(side=tkinter.LEFT)
    btn4 = Button(temp_fr0, text='解析xpath', command=xpath_elements)
    btn4.pack(side=tkinter.LEFT)
    btn2 = Button(temp_fr0, text='获取纯文字', command=html_pure_text)
    btn2.pack(side=tkinter.LEFT)
    btn5 = Button(temp_fr0, text='自动json', command=auto_json)
    btn5.pack(side=tkinter.LEFT)
    btn1 = Button(temp_fr0, text='显示/隐藏配置', command=switch_show)
    btn1.pack(side=tkinter.RIGHT)
    btn6 = Button(temp_fr0, text='生成[requests]代码', command=test_code)
    btn6.pack(side=tkinter.RIGHT)
    btn7 = Button(temp_fr0, text='生成[scrapy]代码', command=scrapy_code)
    btn7.pack(side=tkinter.RIGHT)

    temp_fr1 = Frame(fr,highlightthickness=lin)
    temp_fold_fr1 = Frame(temp_fr1)
    lb1 = Label (temp_fold_fr1,text='HTML文本展示')
    tx1 = Text  (temp_fold_fr1,height=1,width=1,font=ft,wrap='none')
    lb1.pack(side=tkinter.TOP)
    tx1.pack(fill=tkinter.BOTH,expand=True,side=tkinter.TOP,padx=pdx,pady=pdy)

    temp_fold_fr2 = Frame(temp_fr1)
    temp_fold_fold_fr1 = Frame(temp_fold_fr2)
    temp_fold_fold_fr2 = Frame(temp_fold_fr2)
    lb2 = Label (temp_fold_fold_fr1,text='配置数据')
    tx2 = Text  (temp_fold_fold_fr1,height=1,width=1,font=ft)
    lb2.pack(side=tkinter.TOP)
    tx2.pack(fill=tkinter.BOTH,expand=True,side=tkinter.TOP,padx=pdx,pady=pdy)
    lb3 = Label (temp_fold_fold_fr2,text='执行说明')
    tx3 = Text  (temp_fold_fold_fr2,height=1,width=1,font=ft)
    lb3.pack(side=tkinter.TOP)
    tx3.pack(fill=tkinter.BOTH,expand=True,side=tkinter.TOP,padx=pdx,pady=pdy)
    temp_fold_fold_fr1.pack(fill=tkinter.BOTH,expand=True,side=tkinter.TOP)
    temp_fold_fold_fr2.pack(fill=tkinter.BOTH,expand=True,side=tkinter.TOP)
    temp_fold_fr1.pack(fill=tkinter.BOTH,expand=True,side=tkinter.LEFT)
    # temp_fold_fr2.pack(fill=tkinter.BOTH,expand=True,side=tkinter.LEFT)
    temp_fr1.pack(fill=tkinter.BOTH,expand=True,side=tkinter.TOP)

    temp_fr2 = Frame(fr,highlightthickness=lin)
    lb4 = Label (temp_fr2,text='解析内容[Esc 开启/关闭解析显示]')
    tx4 = Text  (temp_fr2,height=1,width=1,font=ft)
    lb4.pack(side=tkinter.TOP)
    tx4.pack(fill=tkinter.BOTH,expand=True,padx=pdx,pady=pdy)
    #temp_fr2.pack(fill=tkinter.BOTH,expand=True,side=tkinter.BOTTOM)

    frame_setting[fr] = {}
    frame_setting[fr]['type'] = 'response'
    frame_setting[fr]['fr_setting'] = setting # 用于生成代码时候需要调用到
    frame_setting[fr]['fr_html_content'] = tx1
    frame_setting[fr]['fr_local_set'] = tx2 # 当前解析脚本的方法类型以及配置
    frame_setting[fr]['fr_local_info'] = tx3 # 一个辅助说明的文本空间
    frame_setting[fr]['fr_parse_info'] = tx4
    frame_setting[fr]['fr_temp2'] = temp_fr2 # 解析输出的 Text 框，这里用外部frame是为了挂钩esc按键显示/关闭该窗口

    # 检查数据格式
    # 非常坑，后续再考虑，现在只考虑 ['utf-8','gbk'] 两种
    # def parse_content_type(content, types=['utf-8','gbk']):
    #     itype = iter(types)
    #     while True:
    #         try:
    #             tp = next(itype)
    #             content = content.decode(tp)
    #             return tp, content
    #         except StopIteration:
    #             try:
    #                 import chardet
    #                 tp = chardet.detect(content)['encoding']
    #                 types.append(tp)
    #                 content = content.decode(tp)
    #                 return tp, content
    #             except:
    #                 raise TypeError('not in {}'.format(types))
    #         except:
    #             continue

    # 统一数据格式
    def format_content(content):
        if type(content) is bytes:
            try:
                content = content.decode('utf-8')
                typ = 'utf-8'
            except:
                try:
                    content = content.decode('gbk')
                    typ = 'gbk'
                except:
                    content = content.decode('utf-8',errors='ignore')
                    typ = 'utf-8 ignore'
            insert_txt(tx3, '解析格式：{}'.format(typ))
            return typ,content
        else:
            einfo = 'type:{} is not in type:[bytes]'.format(type(content))
            raise TypeError(einfo)

    def quote_val(url):
        import urllib
        for i in re.findall('=([^=&]+)',url):
            url = url.replace(i,'{}'.format(urllib.parse.quote(i)))
        return url

    tp = None
    if setting is not None:
        method  = setting.get('method')
        url     = setting.get('url')
        headers = setting.get('headers')
        body    = setting.get('body')
        try:
            if method == 'GET':
                s = requests.get(quote_val(ps.unquote(url)),headers=headers,verify=False)
                tp,content = format_content(s.content)
                insert_txt(tx1, content)
            elif method == 'POST':
                # 这里的post 里面的body 暂时还没有进行处理
                s = requests.post(quote_val(ps.unquote(url)),headers=headers,data=body,verify=False)
                tp,content = format_content(s.content)
                insert_txt(tx1, content)
        except:
            einfo = traceback.format_exc()
            tkinter.messagebox.showinfo('Error',einfo)
            raise
            # insert_txt(tx1, traceback.format_exc())

    frame_setting[fr]['fr_parse_type'] = tp
    return fr




# 暂时考虑用下面的方式来试着挂钩函数执行的状态。
# 不过似乎还是有些漏洞，先就这样，后面再补充完整。
import sys
__org_stdout__ = sys.stdout
__org_stderr__ = sys.stderr
class stdhooker:
    def __init__(self, hook=None, style=None):
        if hook.lower() == 'stdout':
            self.__org_func__ = __org_stdout__
        elif hook.lower() == 'stderr':
            self.__org_func__ = __org_stderr__
        else:
            raise 'stdhooker init error'
        self.cache = ''
        self.style = style
        self.predk = {}

    def write(self,text):
        self.logtx = get_tx()
        if self.logtx not in self.predk:
            self.predk[self.logtx] = 0

        self.cache += text
        if '\n' in self.cache:
            _text = self.cache.rsplit('\n',1)
            self.cache = '' if len(_text) == 1 else _text[1]
            _text_ = _text[0] + '\n'
            if self.logtx:
                self.logtx.insert(tkinter.END, _text_)
                self.logtx.see(tkinter.END)
                self.logtx.update()

    def flush(self):
        self.__org_func__.flush()

def get_tx():
    for i in inspect.stack():
        if '__very_unique_cd__' in i[0].f_locals:
            return i[0].f_locals['cd']

sys.stdout = stdhooker('stdout',style='normal')



# 生成代码临时放在这里
def code_window(setting=None):
    fr = Frame()
    ft = Font(family='Consolas',size=10)

    def _execute_code(*a):
        from .tab import execute_code
        execute_code()

    btn1 = Button(fr, text='执行代码 [Alt+v]', command=_execute_code)
    btn1.pack(side=tkinter.TOP)
    tx = Text(fr,height=1,width=1,font=ft)
    cs = setting.get('code_string')
    if cs:
        tx.delete(0.,tkinter.END)
        tx.insert(0.,cs)
    tx.pack(fill=tkinter.BOTH,expand=True,padx=pdx,pady=pdy)

    temp_fr2 = Frame(fr,highlightthickness=lin)
    lb = Label (temp_fr2,text='执行结果[Esc 显示/隐藏执行结果]')
    cd = Text  (temp_fr2,height=1,width=1,font=ft)
    lb.pack(side=tkinter.TOP)
    cd.pack(fill=tkinter.BOTH,expand=True,padx=pdx,pady=pdy)

    def execute_func():
        __very_unique_cd__ = None
        nonlocal cd
        cd.delete(0.,tkinter.END)
        td = tempfile.mkdtemp()
        tf = os.path.join(td,'temp.py')
        cs = tx.get(0.,tkinter.END)
        with open(tf,'w',encoding='utf-8') as f:
            f.write(cs)
        s = sys.executable
        s = s + ' ' + tf
        import subprocess
        p = subprocess.Popen(s, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, encoding='utf-8')
        print('============================== start ==============================')
        for line in iter(p.stdout.readline, ''):
            if line:
                print(line, end='')
            else:
                break
        print('==============================  end  ==============================')
        p.wait()
        p.stdout.close()
        shutil.rmtree(td)

    frame_setting[fr] = {}
    frame_setting[fr]['type'] = 'code'
    frame_setting[fr]['execute_func'] = execute_func
    frame_setting[fr]['fr_temp2'] = temp_fr2 # 代码执行框，这里仍需挂钩esc按键显示/关闭该窗口

    try:
        from idlelib.colorizer import ColorDelegator
        from idlelib.percolator import Percolator
        p = ColorDelegator()
        Percolator(tx).insertfilter(p)
    except:
        traceback.print_exc()

    return fr







post_verification_model = r"""
    '''
    # [后验证代码模板]
    # 只需在正常请求前加上下面两段便可处理重验证的操作
    # 该重验证包含了，原始请求的重新提交以及验证次数的接口暴露
    # 并且加了这一段验证代码之后你只需要对验证更新的部分修改即可。

    # 使用时只需要修改两处
    # 1. 修改后验证请求的信息的请求信息
    # 2. 修改后验证的更新请求配置的信息（通常更新cookie，已有基本模板）
    def parse(self, response):
        def revalidate(response):
            times = response.meta.get('_revalidate_times') or 0
            # 重验次数，为了测试，这里使用的条件是，重验次数少于2则直接重验
            # 几乎就等于无条件重验证两次，在实际情况下请注意验证条件的编写
            if times >= 2:
                return True

        if not revalidate(response):
            # ============ 请修改此处的验证请求信息 =============
            # 这里只需要传入重验证需要请求的信息即可，会自动重验证和重新请求本次验证失败的请求
            rurl     = 'https://www.baidu.com/'
            rheaders = {}
            rbody    = None # body为None则验证请求为get,否则为post
            yield self.revalidate_pack(response, rurl, rheaders, rbody)
            return

        # 后续是正常的解析操作
    '''
    def revalidate_pack(self, response, rurl=None, rheaders=None, rbody=None):
        def mk_revalidate_request(_plusmeta):
            method = 'GET' if rbody is None else 'POST'
            meta = {}
            meta['_plusmeta'] = _plusmeta
            r = Request(
                    rurl,
                    method   = method,
                    headers  = rheaders,
                    body     = rbody,
                    callback = self.revalidate_parse,
                    meta     = meta,
                    dont_filter = True,
                )
            return r
        _plusmeta = dict(
            url     = response.request.url,
            headers = response.request.headers.to_unicode_dict(),
            body    = response.request.body.decode(),
            method  = response.request.method,
            meta    = response.request.meta,
            cbname  = response.request.callback.__name__,
        )
        return mk_revalidate_request(_plusmeta)

    def revalidate_parse(self, response):
        '''
        验证请求结束，返回验证信息则更新一些信息，重新对原来未验证的请求进行验证
        有时是通过 set-cookie 来实现更新 cookie 的操作，所以这里的 cookie 需要考虑更新的操作。
        可以通过 response.headers.to_unicode_dict() 将返回的headers里面的 key value 转换成字符串
        这样操作会少一些处理 bytes 类型的麻烦。
        '''
        def update(_plusmeta):
            # ============ 请修改此处的验证跟新 =============
            # 一般的后验证通常会在这里对 _plusmeta 中的 cookie 更新，由于to_unicode_dict函数的关系
            # 所有的key都是小写，所以不用担心大小写问题，这里给了一个简单的小模板，如需更多功能请自行修改
            # 这里也可以更新一些 self 的参数，将验证进行持久化
            newcookie = response.headers.to_unicode_dict().get('set-cookie')
            if newcookie:
                _plusmeta['headers']['cookie'] = newcookie

            _plusmeta['meta']['_revalidate_times'] = (_plusmeta['meta'].get('_revalidate_times') or 0) + 1
            return _plusmeta

        _plusmeta = update(response.meta['_plusmeta'])
        url     = _plusmeta['url']
        method  = _plusmeta['method']
        headers = _plusmeta['headers']
        body    = _plusmeta['body']
        meta    = _plusmeta['meta']
        cbname  = _plusmeta['cbname']
        r = Request(
                url,
                method   = method,
                headers  = headers,
                body     = body,
                callback = getattr(self, cbname),
                meta     = meta,
                dont_filter = True,
            )
        yield r
"""


# 生成代码临时放在这里
def scrapy_code_window(setting=None):
    fr = Frame()
    ft = Font(family='Consolas',size=10)

    def _execute_scrapy_code(*a):
        from .tab import execute_scrapy_code
        execute_scrapy_code()

    def save_project_in_desktop(*a):
        name = askstring('项目名称','请输入项目名称，尽量小写无空格。')
        if not name: return
        desktop = os.path.join(os.path.expanduser("~"),'Desktop\\{}'.format(name))
        if not os.path.isdir(desktop):
            with open(script,'w',encoding='utf-8') as f:
                f.write(tx.get(0.,tkinter.END))
            shutil.copytree(scrapypath, desktop)
            if hva.get():
                with open(desktop + '\\v\\spiders\\v.py','a',encoding='utf-8') as f:
                    f.write('\n'*10 + post_verification_model)
            toggle = tkinter.messagebox.askokcancel('创建成功',
                            '创建成功\n\n'
                            '注意！！！\n注意！！！\n注意！！！\n\n是否关闭当前工具并启动拷贝出的 shell 地址执行测试。\n'
                            '如果是，启动第一次shell测试后，后续需要再执行新的测试时请输入:\nscrapy crawl v\n\n'
                            '{}'.format(desktop))
            if not toggle:
                return
            # cmd = 'start explorer {}'.format(desktop) # 打开文件路径
            # os.system(cmd)
            pyscript = os.path.join(os.path.split(sys.executable)[0],'Scripts')
            toggle = any([True for i in os.listdir(pyscript) if 'scrapy.exe' in i.lower()])
            if toggle:
                scrapyexe = os.path.join(pyscript,'scrapy.exe')
                output = '-o {}'.format(et.get()) if va.get() else ''
                cwd = os.getcwd()
                os.chdir(desktop)
                try:
                    cmd = 'start powershell -NoExit "{}" crawl v -L {} {}'.format(scrapyexe,cbx.get(),output)
                    os.system(cmd)
                except:
                    cmd = 'start cmd /k "{}" crawl v -L {} {}'.format(scrapyexe,cbx.get(),output)
                    os.system(cmd)
                os.chdir(cwd)
                cwd = os.getcwd()
            else:
                einfo = 'cannot find scrapy'
                tkinter.messagebox.showinfo('Error',einfo)
                raise EnvironmentError(einfo)
            exit()
        else:
            tkinter.messagebox.showwarning('文件夹已存在','文件夹已存在')

    home = os.environ.get('HOME')
    home = home if home else os.environ.get('HOMEDRIVE') + os.environ.get('HOMEPATH')
    filename = '.vscrapy'
    scrapypath = os.path.join(home,filename)
    scriptpath = os.path.join(scrapypath, 'v/spiders/')
    script = os.path.join(scriptpath, 'v.py')

    def local_collection(*a):
        def _show(*a, stat='show'):
            try:
                if stat == 'show': et.pack(side=tkinter.RIGHT)
                if stat == 'hide': et.pack_forget()
            except:
                pass
        _show(stat='show') if va.get() else _show(stat='hide')


    def pprint(*a):
        __org_stdout__.write(str(a)+'\n')
        __org_stdout__.flush()
    temp_fr0 = Frame(fr)
    va = tkinter.IntVar()
    rb = Checkbutton(temp_fr0,text='本地执行是否收集数据:',variable=va,command=local_collection)
    rb.deselect()
    et = Entry (temp_fr0,width=60)
    
    ltime = '%04d%02d%02d-%02d%02d%02d' % time.localtime()[:6]
    dtopfile = os.path.join('file:///' + os.path.expanduser("~"),'Desktop\\v{}.json'.format(ltime))
    et.insert(0,dtopfile)
    bt2 = Button(temp_fr0,text='拷贝项目文件到桌面',command=save_project_in_desktop)
    bt2.pack(side=tkinter.LEFT)
    btn1 = Button(temp_fr0, text='执行本地代码 [Alt+w]', command=_execute_scrapy_code)
    btn1.pack(side=tkinter.LEFT)
    hva = tkinter.IntVar()
    hrb = Checkbutton(temp_fr0,text='拷贝项目增加后验证模板',variable=hva)
    hrb.deselect()
    hrb.pack(side=tkinter.LEFT)
    cbx = Combobox(temp_fr0,width=10,state='readonly')
    cbx['values'] = ('DEBUG','INFO','WARNING','ERROR','CRITICAL')
    cbx.current(1)
    cbx.pack(side=tkinter.RIGHT)
    lab1 = Label(temp_fr0, text='本地日志等级:')
    lab1.pack(side=tkinter.RIGHT)
    def open_test(*a):
        cmd = 'start explorer {}'.format(scrapypath)
        os.system(cmd)
    bt1 = Button(temp_fr0,text='打开本地文件路径',command=open_test)
    bt1.pack(side=tkinter.RIGHT)
    rb.pack(side=tkinter.RIGHT)

    temp_fr1 = Frame(fr)
    temp_fr0.pack(fill=tkinter.X)
    temp_fr1.pack(fill=tkinter.BOTH,expand=True,side=tkinter.TOP)
    tx = Text(temp_fr1,height=1,width=1,font=ft)
    cs = setting.get('code_string')
    if cs:
        tx.delete(0.,tkinter.END)
        tx.insert(0.,cs)
    tx.pack(fill=tkinter.BOTH,expand=True,padx=pdx,pady=pdy)
    try:
        from idlelib.colorizer import ColorDelegator
        from idlelib.percolator import Percolator
        p = ColorDelegator()
        Percolator(tx).insertfilter(p)
    except:
        traceback.print_exc()

    def execute_func():
        if os.path.isdir(scriptpath):
            with open(script,'w',encoding='utf-8') as f:
                f.write(tx.get(0.,tkinter.END))
            pyscript = os.path.join(os.path.split(sys.executable)[0],'Scripts')
            toggle = any([True for i in os.listdir(pyscript) if 'scrapy.exe' in i.lower()])
            if toggle:
                scrapyexe = os.path.join(pyscript,'scrapy.exe')
                output = '-o {}'.format(et.get()) if va.get() else ''
                cwd = os.getcwd()
                os.chdir(scriptpath)
                try:
                    cmd = 'start powershell -NoExit "{}" crawl v -L {} {}'.format(scrapyexe,cbx.get(),output)
                    os.system(cmd)
                except:
                    cmd = 'start cmd /k "{}" crawl v -L {} {}'.format(scrapyexe,cbx.get(),output)
                    os.system(cmd)
                os.chdir(cwd)
            else:
                einfo = 'cannot find scrapy'
                tkinter.messagebox.showinfo('Error',einfo)
                raise EnvironmentError(einfo)
        else:
            einfo = 'cannot find path: {}'.format(scriptpath)
            tkinter.messagebox.showinfo('Error',einfo)
            raise EnvironmentError(einfo)
    frame_setting[fr] = {}
    frame_setting[fr]['type'] = 'scrapy'
    frame_setting[fr]['execute_func'] = execute_func
    return fr








# 帮助文档
def helper_window():
    fr = Frame()
    ft = Font(family='Consolas',size=10)
    hp = '''
vrequest：
基于 requests 和 lxml 库的爬虫请求测试工具
用于快速发起请求，快速生成且能执行的基于 requests 和 lxml 的代码
也可以生成且能执行 scrapy 代码，不过由于scrapy库依赖过重，该工具不会依赖下载
若需要执行 scrapy 代码，需额外下载 scrapy。

请求窗口快捷键：
(Ctrl + r) 发送请求任务并保存
*(Alt + c) 生成请求代码(一般建议在请求后处理分析再生成代码，那样包含解析代码)
           HEADERS 窗口接受 “:” 或 “=” 分割
           BODY    窗口接受 “:” 或 “=” 分割
                   若是BODY窗口需要传字符串可以在字符串前后加英文双引号
*(Alt + s) 生成 scrapy 请求代码，格式化结构同上

响应窗口快捷键：
*(Alt + r) 打开一个空的响应标签(不常用)
(Alt + f) 智能解析列表路径，解析后使用 xpath 解析功能会自动弹出解析选择窗
(Alt + x) <代码过程> 使用 xpath 解析
(Alt + z) <代码过程> 智能提取 json 数据
(Alt + d) <代码过程> 获取纯文字内容
(Alt + c) 生成请求代码，有<代码过程>则生成代码中包含过程代码 [在js代码窗同样适用]
(Alt + s) 生成 scrapy 请求代码，有<代码过程>则生成代码中包含过程代码
(Esc)     开启/关闭 response 解析窗口

代码窗口快捷键：
(Alt + v) 代码执行 [在js代码窗同样适用]
(Esc)     开启/关闭 代码执行结果窗口 [在js代码窗同样适用]

scrapy 代码窗口快捷键：
(Alt + w) scrapy 代码执行

通用快捷键：
(Ctrl + q) 创建新的请求标签
(Ctrl + j) 创建 js 代码执行窗口
(Ctrl + e) 修改当前标签名字
(Ctrl + w) 关闭当前标签
(Ctrl + h) 创建帮助标签
(Ctrl + s) 保存当前全部请求配置(只能保存请求配置)
(Alt  + `) 用IDLE固定打开一个文件,方便长脚本测试

开源代码：
https://github.com/cilame/vrequest
'''
    temp_fr1 = Frame(fr,highlightthickness=lin)

    def create_req_window(*a):
        from .tab import create_new_reqtab
        create_new_reqtab()

    btn = Button(fr,text='创建请求窗口/[右键创建请求窗口]', command=create_req_window)
    btn.pack()
    lb1 = ttk.Label(temp_fr1,font=ft,text=hp)
    lb1.pack()
    temp_fr1.pack()

    return fr



def exec_js_window(setting=None):
    '''
    这里可能会使用两到三种js的加载方式，并且，js2py能生成 python 的代码，可能需要考虑生成python代码的功能
    目前暂时没有完全实现
    '''
    fr = Frame()
    ft = Font(family='Consolas',size=10)

    # js代码转python代码
    def translate_js_js2py():
        jscode = txt1.get(0.,tkinter.END)
        try:
            import js2py
            js2pycode = js2py.translate_js(jscode)
            txt2.delete(0.,tkinter.END)
            txt2.insert(0.,js2pycode)
        except:
            e = traceback.format_exc()
            txt2.delete(0.,tkinter.END)
            txt2.insert(0.,e)

    def change_module(*a):
        tp = cbx.get().strip()
        btn_create_python_code['text'] = re.sub(r'\[[^\[\]+]*\]',tp,btn_create_python_code['text'])

    def translate_js():
        tp = cbx.get().strip()
        jscode = txt1.get(0.,tkinter.END)
        if 'execjs' in tp:
            pythoncode = """
#coding=utf-8
jscode = r'''
$^^$jscode$^^$
'''

import execjs
ctx = execjs.compile(jscode)
result = ctx.call('func',10,20) # 执行函数，需要传参函数将参从第二个开始依次排在方法名后面
# result = ctx.eval('func(22,33)')
print(result)
""".replace('$^^$jscode$^^$', jscode.strip()).strip()
        if 'js2py' in tp:
            pythoncode = """
#coding=utf-8
jscode = r'''
$^^$jscode$^^$
'''

import js2py
js = js2py.eval_js(jscode) # eval_js模式会自动将js代码执行后最后一个 var赋值的参数返回出来。
print(js)
""".replace('$^^$jscode$^^$', jscode.strip()).strip()
        txt2.delete(0.,tkinter.END)
        txt2.insert(0.,pythoncode)

    def exec_javascript(*a):
        __very_unique_cd__ = None
        nonlocal cd
        cd.delete(0.,tkinter.END)
        td = tempfile.mkdtemp()
        tf = os.path.join(td,'temp.py')
        cs = txt2.get(0.,tkinter.END)
        with open(tf,'w',encoding='utf-8') as f:
            f.write(cs)
        s = sys.executable
        s = s + ' ' + tf
        import subprocess
        p = subprocess.Popen(s, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, encoding='utf-8')
        print('============================== start ==============================')
        for line in iter(p.stdout.readline, ''):
            if line:
                print(line, end='')
            else:
                break
        print('==============================  end  ==============================')
        p.wait()
        p.stdout.close()
        shutil.rmtree(td)

    def _exec_javascript(*a):
        from .tab import show_code_log
        show_code_log()
        exec_javascript()

    def js_beautify(*a):
        try:
            import jsbeautifier
            jscode = txt1.get(0.,tkinter.END)
            btjscode = jsbeautifier.beautify(jscode)
            txt1.delete(0.,tkinter.END)
            txt1.insert(0.,btjscode)
        except ImportError as e:
            txt2.delete(0.,tkinter.END)
            txt2.insert(0.,e)
        except:
            einfo = traceback.format_exc() + \
            '\n\njs代码美化在一些极端的 eval 函数美化时会出现一些问题' + \
            '\n所以出现错误时可以考虑检查代码的 eval 函数的处理'
            txt2.delete(0.,tkinter.END)
            txt2.insert(0.,einfo)

    # 查看常用的js解析器的引入状态
    support_modules = ['js2py', 'execjs']
    def get_js_import_stat(support_modules):
        s = []
        def _temp(module):
            try:
                __import__(module)
                s.append('+ Enable Use [{}] js driver.'.format(module))
            except:
                s.append('- Unable Use [{}] js driver.'.format(module))
        for module in support_modules:
            _temp(module)
        return s
    import_stat = get_js_import_stat(support_modules)
    temp_fr0 = Frame(fr)
    temp_fr0.pack(fill=tkinter.X)
    import_modules = [i[i.find('['):i.rfind(']')+1] for i in import_stat if i.startswith('+')]
    if not import_modules:
        einfo = 'unfind any of {} module.'.format(support_modules)
        tkinter.messagebox.showinfo('Error',einfo)
        raise EnvironmentError(einfo)
    cbx = Combobox(temp_fr0,width=13,state='readonly')
    cbx['values'] = import_modules
    cbx.current(0)
    cbx.pack(fill=tkinter.X,side=tkinter.LEFT)
    cbx.bind('<<ComboboxSelected>>', change_module)

    btn_js_beautify = Button(temp_fr0,text='js代码美化',command=js_beautify)
    btn_js_beautify.pack(side=tkinter.LEFT)
    btn_create_python_code = Button(temp_fr0,text='生成python[]代码 [Alt+c]',command=translate_js)
    btn_create_python_code.pack(side=tkinter.LEFT)
    btn_translate_js = Button(temp_fr0,text='翻译成[js2py]代码',command=translate_js_js2py)
    btn_translate_js.pack(side=tkinter.LEFT)
    btn2 = Button(temp_fr0, text='[执行代码] <Alt+v>', command=_exec_javascript)
    btn2.pack(side=tkinter.RIGHT)


    temp_fr0 = Frame(fr)
    temp_fr0.pack(fill=tkinter.BOTH,expand=True,side=tkinter.TOP)
    temp_fr1 = Frame(temp_fr0)
    temp_fr1_1 = Frame(temp_fr1)
    temp_fr1_1.pack(side=tkinter.TOP)
    temp_fr1.pack(fill=tkinter.BOTH,expand=True,side=tkinter.LEFT)
    txt1 = Text(temp_fr1,height=1,width=1,font=ft)
    lab1 = Label(temp_fr1_1,text='js代码')
    lab1.pack(side=tkinter.TOP)
    txt1.pack(fill=tkinter.BOTH,expand=True,side=tkinter.TOP)
    temp_fr2 = Frame(temp_fr0)
    temp_fr2_1 = Frame(temp_fr2)
    temp_fr2_1.pack(fill=tkinter.X,side=tkinter.TOP)
    temp_fr2.pack(fill=tkinter.BOTH,expand=True,side=tkinter.RIGHT)
    lab1 = Label(temp_fr2_1,text='python代码')
    lab1.pack(side=tkinter.TOP)
    txt2 = Text(temp_fr2,height=1,width=1,font=ft)
    txt2.pack(fill=tkinter.BOTH,expand=True,side=tkinter.TOP)

    temp_fr3 = Frame(fr)
    lab3 = Label(temp_fr3, text='代码结果 [Esc 切换显示状态]')
    lab3.pack(side=tkinter.TOP)
    cd = Text(temp_fr3,font=ft)
    cd.pack(fill=tkinter.BOTH,expand=True)


    test_code = '''
// test_code
function func(a,b){
    return a+b
}

var a = 123;
'''.strip()
    txt1.insert(0.,test_code)


    change_module()
    try:
        from idlelib.colorizer import ColorDelegator
        from idlelib.percolator import Percolator
        p = ColorDelegator()
        Percolator(txt2).insertfilter(p) # txt2 是js2py生成的python代码，需要填色
    except:
        e = traceback.format_exc()
        txt2.delete(0.,tkinter.END)
        txt2.insert(0.,e)




    frame_setting[fr] = {}
    frame_setting[fr]['type'] = 'js'
    frame_setting[fr]['execute_func0'] = translate_js
    frame_setting[fr]['execute_func1'] = translate_js_js2py
    frame_setting[fr]['execute_func'] = exec_javascript
    frame_setting[fr]['import_stat'] = import_stat
    frame_setting[fr]['fr_temp2'] = temp_fr3 # 代码执行框，这里仍需挂钩esc按键显示/关闭该窗口
    return fr



def CrypterAES(key, iv):

    def _compact_word(word):
        return (word[0] << 24) | (word[1] << 16) | (word[2] << 8) | word[3]
    xrange = range
    def _string_to_bytes(text):
        if isinstance(text, bytes):
            return text
        return [ord(c) for c in text]
    def _bytes_to_string(binary): return bytes(binary)
    class AES(object):
        number_of_rounds = {16: 10, 24: 12, 32: 14}
        rcon = [ 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36, 0x6c, 0xd8, 0xab, 0x4d, 0x9a, 0x2f, 0x5e, 0xbc, 0x63, 0xc6, 0x97, 0x35, 0x6a, 0xd4, 0xb3, 0x7d, 0xfa, 0xef, 0xc5, 0x91 ]
        S = [ 0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76, 0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0, 0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15, 0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75, 0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84, 0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf, 0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8, 0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2, 0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73, 0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb, 0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79, 0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08, 0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a, 0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e, 0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf, 0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16 ]
        Si =[ 0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38, 0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7, 0xfb, 0x7c, 0xe3, 0x39, 0x82, 0x9b, 0x2f, 0xff, 0x87, 0x34, 0x8e, 0x43, 0x44, 0xc4, 0xde, 0xe9, 0xcb, 0x54, 0x7b, 0x94, 0x32, 0xa6, 0xc2, 0x23, 0x3d, 0xee, 0x4c, 0x95, 0x0b, 0x42, 0xfa, 0xc3, 0x4e, 0x08, 0x2e, 0xa1, 0x66, 0x28, 0xd9, 0x24, 0xb2, 0x76, 0x5b, 0xa2, 0x49, 0x6d, 0x8b, 0xd1, 0x25, 0x72, 0xf8, 0xf6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xd4, 0xa4, 0x5c, 0xcc, 0x5d, 0x65, 0xb6, 0x92, 0x6c, 0x70, 0x48, 0x50, 0xfd, 0xed, 0xb9, 0xda, 0x5e, 0x15, 0x46, 0x57, 0xa7, 0x8d, 0x9d, 0x84, 0x90, 0xd8, 0xab, 0x00, 0x8c, 0xbc, 0xd3, 0x0a, 0xf7, 0xe4, 0x58, 0x05, 0xb8, 0xb3, 0x45, 0x06, 0xd0, 0x2c, 0x1e, 0x8f, 0xca, 0x3f, 0x0f, 0x02, 0xc1, 0xaf, 0xbd, 0x03, 0x01, 0x13, 0x8a, 0x6b, 0x3a, 0x91, 0x11, 0x41, 0x4f, 0x67, 0xdc, 0xea, 0x97, 0xf2, 0xcf, 0xce, 0xf0, 0xb4, 0xe6, 0x73, 0x96, 0xac, 0x74, 0x22, 0xe7, 0xad, 0x35, 0x85, 0xe2, 0xf9, 0x37, 0xe8, 0x1c, 0x75, 0xdf, 0x6e, 0x47, 0xf1, 0x1a, 0x71, 0x1d, 0x29, 0xc5, 0x89, 0x6f, 0xb7, 0x62, 0x0e, 0xaa, 0x18, 0xbe, 0x1b, 0xfc, 0x56, 0x3e, 0x4b, 0xc6, 0xd2, 0x79, 0x20, 0x9a, 0xdb, 0xc0, 0xfe, 0x78, 0xcd, 0x5a, 0xf4, 0x1f, 0xdd, 0xa8, 0x33, 0x88, 0x07, 0xc7, 0x31, 0xb1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xec, 0x5f, 0x60, 0x51, 0x7f, 0xa9, 0x19, 0xb5, 0x4a, 0x0d, 0x2d, 0xe5, 0x7a, 0x9f, 0x93, 0xc9, 0x9c, 0xef, 0xa0, 0xe0, 0x3b, 0x4d, 0xae, 0x2a, 0xf5, 0xb0, 0xc8, 0xeb, 0xbb, 0x3c, 0x83, 0x53, 0x99, 0x61, 0x17, 0x2b, 0x04, 0x7e, 0xba, 0x77, 0xd6, 0x26, 0xe1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0c, 0x7d ] 
        T1 = [ 0xc66363a5, 0xf87c7c84, 0xee777799, 0xf67b7b8d, 0xfff2f20d, 0xd66b6bbd, 0xde6f6fb1, 0x91c5c554, 0x60303050, 0x02010103, 0xce6767a9, 0x562b2b7d, 0xe7fefe19, 0xb5d7d762, 0x4dababe6, 0xec76769a, 0x8fcaca45, 0x1f82829d, 0x89c9c940, 0xfa7d7d87, 0xeffafa15, 0xb25959eb, 0x8e4747c9, 0xfbf0f00b, 0x41adadec, 0xb3d4d467, 0x5fa2a2fd, 0x45afafea, 0x239c9cbf, 0x53a4a4f7, 0xe4727296, 0x9bc0c05b, 0x75b7b7c2, 0xe1fdfd1c, 0x3d9393ae, 0x4c26266a, 0x6c36365a, 0x7e3f3f41, 0xf5f7f702, 0x83cccc4f, 0x6834345c, 0x51a5a5f4, 0xd1e5e534, 0xf9f1f108, 0xe2717193, 0xabd8d873, 0x62313153, 0x2a15153f, 0x0804040c, 0x95c7c752, 0x46232365, 0x9dc3c35e, 0x30181828, 0x379696a1, 0x0a05050f, 0x2f9a9ab5, 0x0e070709, 0x24121236, 0x1b80809b, 0xdfe2e23d, 0xcdebeb26, 0x4e272769, 0x7fb2b2cd, 0xea75759f, 0x1209091b, 0x1d83839e, 0x582c2c74, 0x341a1a2e, 0x361b1b2d, 0xdc6e6eb2, 0xb45a5aee, 0x5ba0a0fb, 0xa45252f6, 0x763b3b4d, 0xb7d6d661, 0x7db3b3ce, 0x5229297b, 0xdde3e33e, 0x5e2f2f71, 0x13848497, 0xa65353f5, 0xb9d1d168, 0x00000000, 0xc1eded2c, 0x40202060, 0xe3fcfc1f, 0x79b1b1c8, 0xb65b5bed, 0xd46a6abe, 0x8dcbcb46, 0x67bebed9, 0x7239394b, 0x944a4ade, 0x984c4cd4, 0xb05858e8, 0x85cfcf4a, 0xbbd0d06b, 0xc5efef2a, 0x4faaaae5, 0xedfbfb16, 0x864343c5, 0x9a4d4dd7, 0x66333355, 0x11858594, 0x8a4545cf, 0xe9f9f910, 0x04020206, 0xfe7f7f81, 0xa05050f0, 0x783c3c44, 0x259f9fba, 0x4ba8a8e3, 0xa25151f3, 0x5da3a3fe, 0x804040c0, 0x058f8f8a, 0x3f9292ad, 0x219d9dbc, 0x70383848, 0xf1f5f504, 0x63bcbcdf, 0x77b6b6c1, 0xafdada75, 0x42212163, 0x20101030, 0xe5ffff1a, 0xfdf3f30e, 0xbfd2d26d, 0x81cdcd4c, 0x180c0c14, 0x26131335, 0xc3ecec2f, 0xbe5f5fe1, 0x359797a2, 0x884444cc, 0x2e171739, 0x93c4c457, 0x55a7a7f2, 0xfc7e7e82, 0x7a3d3d47, 0xc86464ac, 0xba5d5de7, 0x3219192b, 0xe6737395, 0xc06060a0, 0x19818198, 0x9e4f4fd1, 0xa3dcdc7f, 0x44222266, 0x542a2a7e, 0x3b9090ab, 0x0b888883, 0x8c4646ca, 0xc7eeee29, 0x6bb8b8d3, 0x2814143c, 0xa7dede79, 0xbc5e5ee2, 0x160b0b1d, 0xaddbdb76, 0xdbe0e03b, 0x64323256, 0x743a3a4e, 0x140a0a1e, 0x924949db, 0x0c06060a, 0x4824246c, 0xb85c5ce4, 0x9fc2c25d, 0xbdd3d36e, 0x43acacef, 0xc46262a6, 0x399191a8, 0x319595a4, 0xd3e4e437, 0xf279798b, 0xd5e7e732, 0x8bc8c843, 0x6e373759, 0xda6d6db7, 0x018d8d8c, 0xb1d5d564, 0x9c4e4ed2, 0x49a9a9e0, 0xd86c6cb4, 0xac5656fa, 0xf3f4f407, 0xcfeaea25, 0xca6565af, 0xf47a7a8e, 0x47aeaee9, 0x10080818, 0x6fbabad5, 0xf0787888, 0x4a25256f, 0x5c2e2e72, 0x381c1c24, 0x57a6a6f1, 0x73b4b4c7, 0x97c6c651, 0xcbe8e823, 0xa1dddd7c, 0xe874749c, 0x3e1f1f21, 0x964b4bdd, 0x61bdbddc, 0x0d8b8b86, 0x0f8a8a85, 0xe0707090, 0x7c3e3e42, 0x71b5b5c4, 0xcc6666aa, 0x904848d8, 0x06030305, 0xf7f6f601, 0x1c0e0e12, 0xc26161a3, 0x6a35355f, 0xae5757f9, 0x69b9b9d0, 0x17868691, 0x99c1c158, 0x3a1d1d27, 0x279e9eb9, 0xd9e1e138, 0xebf8f813, 0x2b9898b3, 0x22111133, 0xd26969bb, 0xa9d9d970, 0x078e8e89, 0x339494a7, 0x2d9b9bb6, 0x3c1e1e22, 0x15878792, 0xc9e9e920, 0x87cece49, 0xaa5555ff, 0x50282878, 0xa5dfdf7a, 0x038c8c8f, 0x59a1a1f8, 0x09898980, 0x1a0d0d17, 0x65bfbfda, 0xd7e6e631, 0x844242c6, 0xd06868b8, 0x824141c3, 0x299999b0, 0x5a2d2d77, 0x1e0f0f11, 0x7bb0b0cb, 0xa85454fc, 0x6dbbbbd6, 0x2c16163a ]
        T2 = [ 0xa5c66363, 0x84f87c7c, 0x99ee7777, 0x8df67b7b, 0x0dfff2f2, 0xbdd66b6b, 0xb1de6f6f, 0x5491c5c5, 0x50603030, 0x03020101, 0xa9ce6767, 0x7d562b2b, 0x19e7fefe, 0x62b5d7d7, 0xe64dabab, 0x9aec7676, 0x458fcaca, 0x9d1f8282, 0x4089c9c9, 0x87fa7d7d, 0x15effafa, 0xebb25959, 0xc98e4747, 0x0bfbf0f0, 0xec41adad, 0x67b3d4d4, 0xfd5fa2a2, 0xea45afaf, 0xbf239c9c, 0xf753a4a4, 0x96e47272, 0x5b9bc0c0, 0xc275b7b7, 0x1ce1fdfd, 0xae3d9393, 0x6a4c2626, 0x5a6c3636, 0x417e3f3f, 0x02f5f7f7, 0x4f83cccc, 0x5c683434, 0xf451a5a5, 0x34d1e5e5, 0x08f9f1f1, 0x93e27171, 0x73abd8d8, 0x53623131, 0x3f2a1515, 0x0c080404, 0x5295c7c7, 0x65462323, 0x5e9dc3c3, 0x28301818, 0xa1379696, 0x0f0a0505, 0xb52f9a9a, 0x090e0707, 0x36241212, 0x9b1b8080, 0x3ddfe2e2, 0x26cdebeb, 0x694e2727, 0xcd7fb2b2, 0x9fea7575, 0x1b120909, 0x9e1d8383, 0x74582c2c, 0x2e341a1a, 0x2d361b1b, 0xb2dc6e6e, 0xeeb45a5a, 0xfb5ba0a0, 0xf6a45252, 0x4d763b3b, 0x61b7d6d6, 0xce7db3b3, 0x7b522929, 0x3edde3e3, 0x715e2f2f, 0x97138484, 0xf5a65353, 0x68b9d1d1, 0x00000000, 0x2cc1eded, 0x60402020, 0x1fe3fcfc, 0xc879b1b1, 0xedb65b5b, 0xbed46a6a, 0x468dcbcb, 0xd967bebe, 0x4b723939, 0xde944a4a, 0xd4984c4c, 0xe8b05858, 0x4a85cfcf, 0x6bbbd0d0, 0x2ac5efef, 0xe54faaaa, 0x16edfbfb, 0xc5864343, 0xd79a4d4d, 0x55663333, 0x94118585, 0xcf8a4545, 0x10e9f9f9, 0x06040202, 0x81fe7f7f, 0xf0a05050, 0x44783c3c, 0xba259f9f, 0xe34ba8a8, 0xf3a25151, 0xfe5da3a3, 0xc0804040, 0x8a058f8f, 0xad3f9292, 0xbc219d9d, 0x48703838, 0x04f1f5f5, 0xdf63bcbc, 0xc177b6b6, 0x75afdada, 0x63422121, 0x30201010, 0x1ae5ffff, 0x0efdf3f3, 0x6dbfd2d2, 0x4c81cdcd, 0x14180c0c, 0x35261313, 0x2fc3ecec, 0xe1be5f5f, 0xa2359797, 0xcc884444, 0x392e1717, 0x5793c4c4, 0xf255a7a7, 0x82fc7e7e, 0x477a3d3d, 0xacc86464, 0xe7ba5d5d, 0x2b321919, 0x95e67373, 0xa0c06060, 0x98198181, 0xd19e4f4f, 0x7fa3dcdc, 0x66442222, 0x7e542a2a, 0xab3b9090, 0x830b8888, 0xca8c4646, 0x29c7eeee, 0xd36bb8b8, 0x3c281414, 0x79a7dede, 0xe2bc5e5e, 0x1d160b0b, 0x76addbdb, 0x3bdbe0e0, 0x56643232, 0x4e743a3a, 0x1e140a0a, 0xdb924949, 0x0a0c0606, 0x6c482424, 0xe4b85c5c, 0x5d9fc2c2, 0x6ebdd3d3, 0xef43acac, 0xa6c46262, 0xa8399191, 0xa4319595, 0x37d3e4e4, 0x8bf27979, 0x32d5e7e7, 0x438bc8c8, 0x596e3737, 0xb7da6d6d, 0x8c018d8d, 0x64b1d5d5, 0xd29c4e4e, 0xe049a9a9, 0xb4d86c6c, 0xfaac5656, 0x07f3f4f4, 0x25cfeaea, 0xafca6565, 0x8ef47a7a, 0xe947aeae, 0x18100808, 0xd56fbaba, 0x88f07878, 0x6f4a2525, 0x725c2e2e, 0x24381c1c, 0xf157a6a6, 0xc773b4b4, 0x5197c6c6, 0x23cbe8e8, 0x7ca1dddd, 0x9ce87474, 0x213e1f1f, 0xdd964b4b, 0xdc61bdbd, 0x860d8b8b, 0x850f8a8a, 0x90e07070, 0x427c3e3e, 0xc471b5b5, 0xaacc6666, 0xd8904848, 0x05060303, 0x01f7f6f6, 0x121c0e0e, 0xa3c26161, 0x5f6a3535, 0xf9ae5757, 0xd069b9b9, 0x91178686, 0x5899c1c1, 0x273a1d1d, 0xb9279e9e, 0x38d9e1e1, 0x13ebf8f8, 0xb32b9898, 0x33221111, 0xbbd26969, 0x70a9d9d9, 0x89078e8e, 0xa7339494, 0xb62d9b9b, 0x223c1e1e, 0x92158787, 0x20c9e9e9, 0x4987cece, 0xffaa5555, 0x78502828, 0x7aa5dfdf, 0x8f038c8c, 0xf859a1a1, 0x80098989, 0x171a0d0d, 0xda65bfbf, 0x31d7e6e6, 0xc6844242, 0xb8d06868, 0xc3824141, 0xb0299999, 0x775a2d2d, 0x111e0f0f, 0xcb7bb0b0, 0xfca85454, 0xd66dbbbb, 0x3a2c1616 ]
        T3 = [ 0x63a5c663, 0x7c84f87c, 0x7799ee77, 0x7b8df67b, 0xf20dfff2, 0x6bbdd66b, 0x6fb1de6f, 0xc55491c5, 0x30506030, 0x01030201, 0x67a9ce67, 0x2b7d562b, 0xfe19e7fe, 0xd762b5d7, 0xabe64dab, 0x769aec76, 0xca458fca, 0x829d1f82, 0xc94089c9, 0x7d87fa7d, 0xfa15effa, 0x59ebb259, 0x47c98e47, 0xf00bfbf0, 0xadec41ad, 0xd467b3d4, 0xa2fd5fa2, 0xafea45af, 0x9cbf239c, 0xa4f753a4, 0x7296e472, 0xc05b9bc0, 0xb7c275b7, 0xfd1ce1fd, 0x93ae3d93, 0x266a4c26, 0x365a6c36, 0x3f417e3f, 0xf702f5f7, 0xcc4f83cc, 0x345c6834, 0xa5f451a5, 0xe534d1e5, 0xf108f9f1, 0x7193e271, 0xd873abd8, 0x31536231, 0x153f2a15, 0x040c0804, 0xc75295c7, 0x23654623, 0xc35e9dc3, 0x18283018, 0x96a13796, 0x050f0a05, 0x9ab52f9a, 0x07090e07, 0x12362412, 0x809b1b80, 0xe23ddfe2, 0xeb26cdeb, 0x27694e27, 0xb2cd7fb2, 0x759fea75, 0x091b1209, 0x839e1d83, 0x2c74582c, 0x1a2e341a, 0x1b2d361b, 0x6eb2dc6e, 0x5aeeb45a, 0xa0fb5ba0, 0x52f6a452, 0x3b4d763b, 0xd661b7d6, 0xb3ce7db3, 0x297b5229, 0xe33edde3, 0x2f715e2f, 0x84971384, 0x53f5a653, 0xd168b9d1, 0x00000000, 0xed2cc1ed, 0x20604020, 0xfc1fe3fc, 0xb1c879b1, 0x5bedb65b, 0x6abed46a, 0xcb468dcb, 0xbed967be, 0x394b7239, 0x4ade944a, 0x4cd4984c, 0x58e8b058, 0xcf4a85cf, 0xd06bbbd0, 0xef2ac5ef, 0xaae54faa, 0xfb16edfb, 0x43c58643, 0x4dd79a4d, 0x33556633, 0x85941185, 0x45cf8a45, 0xf910e9f9, 0x02060402, 0x7f81fe7f, 0x50f0a050, 0x3c44783c, 0x9fba259f, 0xa8e34ba8, 0x51f3a251, 0xa3fe5da3, 0x40c08040, 0x8f8a058f, 0x92ad3f92, 0x9dbc219d, 0x38487038, 0xf504f1f5, 0xbcdf63bc, 0xb6c177b6, 0xda75afda, 0x21634221, 0x10302010, 0xff1ae5ff, 0xf30efdf3, 0xd26dbfd2, 0xcd4c81cd, 0x0c14180c, 0x13352613, 0xec2fc3ec, 0x5fe1be5f, 0x97a23597, 0x44cc8844, 0x17392e17, 0xc45793c4, 0xa7f255a7, 0x7e82fc7e, 0x3d477a3d, 0x64acc864, 0x5de7ba5d, 0x192b3219, 0x7395e673, 0x60a0c060, 0x81981981, 0x4fd19e4f, 0xdc7fa3dc, 0x22664422, 0x2a7e542a, 0x90ab3b90, 0x88830b88, 0x46ca8c46, 0xee29c7ee, 0xb8d36bb8, 0x143c2814, 0xde79a7de, 0x5ee2bc5e, 0x0b1d160b, 0xdb76addb, 0xe03bdbe0, 0x32566432, 0x3a4e743a, 0x0a1e140a, 0x49db9249, 0x060a0c06, 0x246c4824, 0x5ce4b85c, 0xc25d9fc2, 0xd36ebdd3, 0xacef43ac, 0x62a6c462, 0x91a83991, 0x95a43195, 0xe437d3e4, 0x798bf279, 0xe732d5e7, 0xc8438bc8, 0x37596e37, 0x6db7da6d, 0x8d8c018d, 0xd564b1d5, 0x4ed29c4e, 0xa9e049a9, 0x6cb4d86c, 0x56faac56, 0xf407f3f4, 0xea25cfea, 0x65afca65, 0x7a8ef47a, 0xaee947ae, 0x08181008, 0xbad56fba, 0x7888f078, 0x256f4a25, 0x2e725c2e, 0x1c24381c, 0xa6f157a6, 0xb4c773b4, 0xc65197c6, 0xe823cbe8, 0xdd7ca1dd, 0x749ce874, 0x1f213e1f, 0x4bdd964b, 0xbddc61bd, 0x8b860d8b, 0x8a850f8a, 0x7090e070, 0x3e427c3e, 0xb5c471b5, 0x66aacc66, 0x48d89048, 0x03050603, 0xf601f7f6, 0x0e121c0e, 0x61a3c261, 0x355f6a35, 0x57f9ae57, 0xb9d069b9, 0x86911786, 0xc15899c1, 0x1d273a1d, 0x9eb9279e, 0xe138d9e1, 0xf813ebf8, 0x98b32b98, 0x11332211, 0x69bbd269, 0xd970a9d9, 0x8e89078e, 0x94a73394, 0x9bb62d9b, 0x1e223c1e, 0x87921587, 0xe920c9e9, 0xce4987ce, 0x55ffaa55, 0x28785028, 0xdf7aa5df, 0x8c8f038c, 0xa1f859a1, 0x89800989, 0x0d171a0d, 0xbfda65bf, 0xe631d7e6, 0x42c68442, 0x68b8d068, 0x41c38241, 0x99b02999, 0x2d775a2d, 0x0f111e0f, 0xb0cb7bb0, 0x54fca854, 0xbbd66dbb, 0x163a2c16 ]
        T4 = [ 0x6363a5c6, 0x7c7c84f8, 0x777799ee, 0x7b7b8df6, 0xf2f20dff, 0x6b6bbdd6, 0x6f6fb1de, 0xc5c55491, 0x30305060, 0x01010302, 0x6767a9ce, 0x2b2b7d56, 0xfefe19e7, 0xd7d762b5, 0xababe64d, 0x76769aec, 0xcaca458f, 0x82829d1f, 0xc9c94089, 0x7d7d87fa, 0xfafa15ef, 0x5959ebb2, 0x4747c98e, 0xf0f00bfb, 0xadadec41, 0xd4d467b3, 0xa2a2fd5f, 0xafafea45, 0x9c9cbf23, 0xa4a4f753, 0x727296e4, 0xc0c05b9b, 0xb7b7c275, 0xfdfd1ce1, 0x9393ae3d, 0x26266a4c, 0x36365a6c, 0x3f3f417e, 0xf7f702f5, 0xcccc4f83, 0x34345c68, 0xa5a5f451, 0xe5e534d1, 0xf1f108f9, 0x717193e2, 0xd8d873ab, 0x31315362, 0x15153f2a, 0x04040c08, 0xc7c75295, 0x23236546, 0xc3c35e9d, 0x18182830, 0x9696a137, 0x05050f0a, 0x9a9ab52f, 0x0707090e, 0x12123624, 0x80809b1b, 0xe2e23ddf, 0xebeb26cd, 0x2727694e, 0xb2b2cd7f, 0x75759fea, 0x09091b12, 0x83839e1d, 0x2c2c7458, 0x1a1a2e34, 0x1b1b2d36, 0x6e6eb2dc, 0x5a5aeeb4, 0xa0a0fb5b, 0x5252f6a4, 0x3b3b4d76, 0xd6d661b7, 0xb3b3ce7d, 0x29297b52, 0xe3e33edd, 0x2f2f715e, 0x84849713, 0x5353f5a6, 0xd1d168b9, 0x00000000, 0xeded2cc1, 0x20206040, 0xfcfc1fe3, 0xb1b1c879, 0x5b5bedb6, 0x6a6abed4, 0xcbcb468d, 0xbebed967, 0x39394b72, 0x4a4ade94, 0x4c4cd498, 0x5858e8b0, 0xcfcf4a85, 0xd0d06bbb, 0xefef2ac5, 0xaaaae54f, 0xfbfb16ed, 0x4343c586, 0x4d4dd79a, 0x33335566, 0x85859411, 0x4545cf8a, 0xf9f910e9, 0x02020604, 0x7f7f81fe, 0x5050f0a0, 0x3c3c4478, 0x9f9fba25, 0xa8a8e34b, 0x5151f3a2, 0xa3a3fe5d, 0x4040c080, 0x8f8f8a05, 0x9292ad3f, 0x9d9dbc21, 0x38384870, 0xf5f504f1, 0xbcbcdf63, 0xb6b6c177, 0xdada75af, 0x21216342, 0x10103020, 0xffff1ae5, 0xf3f30efd, 0xd2d26dbf, 0xcdcd4c81, 0x0c0c1418, 0x13133526, 0xecec2fc3, 0x5f5fe1be, 0x9797a235, 0x4444cc88, 0x1717392e, 0xc4c45793, 0xa7a7f255, 0x7e7e82fc, 0x3d3d477a, 0x6464acc8, 0x5d5de7ba, 0x19192b32, 0x737395e6, 0x6060a0c0, 0x81819819, 0x4f4fd19e, 0xdcdc7fa3, 0x22226644, 0x2a2a7e54, 0x9090ab3b, 0x8888830b, 0x4646ca8c, 0xeeee29c7, 0xb8b8d36b, 0x14143c28, 0xdede79a7, 0x5e5ee2bc, 0x0b0b1d16, 0xdbdb76ad, 0xe0e03bdb, 0x32325664, 0x3a3a4e74, 0x0a0a1e14, 0x4949db92, 0x06060a0c, 0x24246c48, 0x5c5ce4b8, 0xc2c25d9f, 0xd3d36ebd, 0xacacef43, 0x6262a6c4, 0x9191a839, 0x9595a431, 0xe4e437d3, 0x79798bf2, 0xe7e732d5, 0xc8c8438b, 0x3737596e, 0x6d6db7da, 0x8d8d8c01, 0xd5d564b1, 0x4e4ed29c, 0xa9a9e049, 0x6c6cb4d8, 0x5656faac, 0xf4f407f3, 0xeaea25cf, 0x6565afca, 0x7a7a8ef4, 0xaeaee947, 0x08081810, 0xbabad56f, 0x787888f0, 0x25256f4a, 0x2e2e725c, 0x1c1c2438, 0xa6a6f157, 0xb4b4c773, 0xc6c65197, 0xe8e823cb, 0xdddd7ca1, 0x74749ce8, 0x1f1f213e, 0x4b4bdd96, 0xbdbddc61, 0x8b8b860d, 0x8a8a850f, 0x707090e0, 0x3e3e427c, 0xb5b5c471, 0x6666aacc, 0x4848d890, 0x03030506, 0xf6f601f7, 0x0e0e121c, 0x6161a3c2, 0x35355f6a, 0x5757f9ae, 0xb9b9d069, 0x86869117, 0xc1c15899, 0x1d1d273a, 0x9e9eb927, 0xe1e138d9, 0xf8f813eb, 0x9898b32b, 0x11113322, 0x6969bbd2, 0xd9d970a9, 0x8e8e8907, 0x9494a733, 0x9b9bb62d, 0x1e1e223c, 0x87879215, 0xe9e920c9, 0xcece4987, 0x5555ffaa, 0x28287850, 0xdfdf7aa5, 0x8c8c8f03, 0xa1a1f859, 0x89898009, 0x0d0d171a, 0xbfbfda65, 0xe6e631d7, 0x4242c684, 0x6868b8d0, 0x4141c382, 0x9999b029, 0x2d2d775a, 0x0f0f111e, 0xb0b0cb7b, 0x5454fca8, 0xbbbbd66d, 0x16163a2c ]
        T5 = [ 0x51f4a750, 0x7e416553, 0x1a17a4c3, 0x3a275e96, 0x3bab6bcb, 0x1f9d45f1, 0xacfa58ab, 0x4be30393, 0x2030fa55, 0xad766df6, 0x88cc7691, 0xf5024c25, 0x4fe5d7fc, 0xc52acbd7, 0x26354480, 0xb562a38f, 0xdeb15a49, 0x25ba1b67, 0x45ea0e98, 0x5dfec0e1, 0xc32f7502, 0x814cf012, 0x8d4697a3, 0x6bd3f9c6, 0x038f5fe7, 0x15929c95, 0xbf6d7aeb, 0x955259da, 0xd4be832d, 0x587421d3, 0x49e06929, 0x8ec9c844, 0x75c2896a, 0xf48e7978, 0x99583e6b, 0x27b971dd, 0xbee14fb6, 0xf088ad17, 0xc920ac66, 0x7dce3ab4, 0x63df4a18, 0xe51a3182, 0x97513360, 0x62537f45, 0xb16477e0, 0xbb6bae84, 0xfe81a01c, 0xf9082b94, 0x70486858, 0x8f45fd19, 0x94de6c87, 0x527bf8b7, 0xab73d323, 0x724b02e2, 0xe31f8f57, 0x6655ab2a, 0xb2eb2807, 0x2fb5c203, 0x86c57b9a, 0xd33708a5, 0x302887f2, 0x23bfa5b2, 0x02036aba, 0xed16825c, 0x8acf1c2b, 0xa779b492, 0xf307f2f0, 0x4e69e2a1, 0x65daf4cd, 0x0605bed5, 0xd134621f, 0xc4a6fe8a, 0x342e539d, 0xa2f355a0, 0x058ae132, 0xa4f6eb75, 0x0b83ec39, 0x4060efaa, 0x5e719f06, 0xbd6e1051, 0x3e218af9, 0x96dd063d, 0xdd3e05ae, 0x4de6bd46, 0x91548db5, 0x71c45d05, 0x0406d46f, 0x605015ff, 0x1998fb24, 0xd6bde997, 0x894043cc, 0x67d99e77, 0xb0e842bd, 0x07898b88, 0xe7195b38, 0x79c8eedb, 0xa17c0a47, 0x7c420fe9, 0xf8841ec9, 0x00000000, 0x09808683, 0x322bed48, 0x1e1170ac, 0x6c5a724e, 0xfd0efffb, 0x0f853856, 0x3daed51e, 0x362d3927, 0x0a0fd964, 0x685ca621, 0x9b5b54d1, 0x24362e3a, 0x0c0a67b1, 0x9357e70f, 0xb4ee96d2, 0x1b9b919e, 0x80c0c54f, 0x61dc20a2, 0x5a774b69, 0x1c121a16, 0xe293ba0a, 0xc0a02ae5, 0x3c22e043, 0x121b171d, 0x0e090d0b, 0xf28bc7ad, 0x2db6a8b9, 0x141ea9c8, 0x57f11985, 0xaf75074c, 0xee99ddbb, 0xa37f60fd, 0xf701269f, 0x5c72f5bc, 0x44663bc5, 0x5bfb7e34, 0x8b432976, 0xcb23c6dc, 0xb6edfc68, 0xb8e4f163, 0xd731dcca, 0x42638510, 0x13972240, 0x84c61120, 0x854a247d, 0xd2bb3df8, 0xaef93211, 0xc729a16d, 0x1d9e2f4b, 0xdcb230f3, 0x0d8652ec, 0x77c1e3d0, 0x2bb3166c, 0xa970b999, 0x119448fa, 0x47e96422, 0xa8fc8cc4, 0xa0f03f1a, 0x567d2cd8, 0x223390ef, 0x87494ec7, 0xd938d1c1, 0x8ccaa2fe, 0x98d40b36, 0xa6f581cf, 0xa57ade28, 0xdab78e26, 0x3fadbfa4, 0x2c3a9de4, 0x5078920d, 0x6a5fcc9b, 0x547e4662, 0xf68d13c2, 0x90d8b8e8, 0x2e39f75e, 0x82c3aff5, 0x9f5d80be, 0x69d0937c, 0x6fd52da9, 0xcf2512b3, 0xc8ac993b, 0x10187da7, 0xe89c636e, 0xdb3bbb7b, 0xcd267809, 0x6e5918f4, 0xec9ab701, 0x834f9aa8, 0xe6956e65, 0xaaffe67e, 0x21bccf08, 0xef15e8e6, 0xbae79bd9, 0x4a6f36ce, 0xea9f09d4, 0x29b07cd6, 0x31a4b2af, 0x2a3f2331, 0xc6a59430, 0x35a266c0, 0x744ebc37, 0xfc82caa6, 0xe090d0b0, 0x33a7d815, 0xf104984a, 0x41ecdaf7, 0x7fcd500e, 0x1791f62f, 0x764dd68d, 0x43efb04d, 0xccaa4d54, 0xe49604df, 0x9ed1b5e3, 0x4c6a881b, 0xc12c1fb8, 0x4665517f, 0x9d5eea04, 0x018c355d, 0xfa877473, 0xfb0b412e, 0xb3671d5a, 0x92dbd252, 0xe9105633, 0x6dd64713, 0x9ad7618c, 0x37a10c7a, 0x59f8148e, 0xeb133c89, 0xcea927ee, 0xb761c935, 0xe11ce5ed, 0x7a47b13c, 0x9cd2df59, 0x55f2733f, 0x1814ce79, 0x73c737bf, 0x53f7cdea, 0x5ffdaa5b, 0xdf3d6f14, 0x7844db86, 0xcaaff381, 0xb968c43e, 0x3824342c, 0xc2a3405f, 0x161dc372, 0xbce2250c, 0x283c498b, 0xff0d9541, 0x39a80171, 0x080cb3de, 0xd8b4e49c, 0x6456c190, 0x7bcb8461, 0xd532b670, 0x486c5c74, 0xd0b85742 ]
        T6 = [ 0x5051f4a7, 0x537e4165, 0xc31a17a4, 0x963a275e, 0xcb3bab6b, 0xf11f9d45, 0xabacfa58, 0x934be303, 0x552030fa, 0xf6ad766d, 0x9188cc76, 0x25f5024c, 0xfc4fe5d7, 0xd7c52acb, 0x80263544, 0x8fb562a3, 0x49deb15a, 0x6725ba1b, 0x9845ea0e, 0xe15dfec0, 0x02c32f75, 0x12814cf0, 0xa38d4697, 0xc66bd3f9, 0xe7038f5f, 0x9515929c, 0xebbf6d7a, 0xda955259, 0x2dd4be83, 0xd3587421, 0x2949e069, 0x448ec9c8, 0x6a75c289, 0x78f48e79, 0x6b99583e, 0xdd27b971, 0xb6bee14f, 0x17f088ad, 0x66c920ac, 0xb47dce3a, 0x1863df4a, 0x82e51a31, 0x60975133, 0x4562537f, 0xe0b16477, 0x84bb6bae, 0x1cfe81a0, 0x94f9082b, 0x58704868, 0x198f45fd, 0x8794de6c, 0xb7527bf8, 0x23ab73d3, 0xe2724b02, 0x57e31f8f, 0x2a6655ab, 0x07b2eb28, 0x032fb5c2, 0x9a86c57b, 0xa5d33708, 0xf2302887, 0xb223bfa5, 0xba02036a, 0x5ced1682, 0x2b8acf1c, 0x92a779b4, 0xf0f307f2, 0xa14e69e2, 0xcd65daf4, 0xd50605be, 0x1fd13462, 0x8ac4a6fe, 0x9d342e53, 0xa0a2f355, 0x32058ae1, 0x75a4f6eb, 0x390b83ec, 0xaa4060ef, 0x065e719f, 0x51bd6e10, 0xf93e218a, 0x3d96dd06, 0xaedd3e05, 0x464de6bd, 0xb591548d, 0x0571c45d, 0x6f0406d4, 0xff605015, 0x241998fb, 0x97d6bde9, 0xcc894043, 0x7767d99e, 0xbdb0e842, 0x8807898b, 0x38e7195b, 0xdb79c8ee, 0x47a17c0a, 0xe97c420f, 0xc9f8841e, 0x00000000, 0x83098086, 0x48322bed, 0xac1e1170, 0x4e6c5a72, 0xfbfd0eff, 0x560f8538, 0x1e3daed5, 0x27362d39, 0x640a0fd9, 0x21685ca6, 0xd19b5b54, 0x3a24362e, 0xb10c0a67, 0x0f9357e7, 0xd2b4ee96, 0x9e1b9b91, 0x4f80c0c5, 0xa261dc20, 0x695a774b, 0x161c121a, 0x0ae293ba, 0xe5c0a02a, 0x433c22e0, 0x1d121b17, 0x0b0e090d, 0xadf28bc7, 0xb92db6a8, 0xc8141ea9, 0x8557f119, 0x4caf7507, 0xbbee99dd, 0xfda37f60, 0x9ff70126, 0xbc5c72f5, 0xc544663b, 0x345bfb7e, 0x768b4329, 0xdccb23c6, 0x68b6edfc, 0x63b8e4f1, 0xcad731dc, 0x10426385, 0x40139722, 0x2084c611, 0x7d854a24, 0xf8d2bb3d, 0x11aef932, 0x6dc729a1, 0x4b1d9e2f, 0xf3dcb230, 0xec0d8652, 0xd077c1e3, 0x6c2bb316, 0x99a970b9, 0xfa119448, 0x2247e964, 0xc4a8fc8c, 0x1aa0f03f, 0xd8567d2c, 0xef223390, 0xc787494e, 0xc1d938d1, 0xfe8ccaa2, 0x3698d40b, 0xcfa6f581, 0x28a57ade, 0x26dab78e, 0xa43fadbf, 0xe42c3a9d, 0x0d507892, 0x9b6a5fcc, 0x62547e46, 0xc2f68d13, 0xe890d8b8, 0x5e2e39f7, 0xf582c3af, 0xbe9f5d80, 0x7c69d093, 0xa96fd52d, 0xb3cf2512, 0x3bc8ac99, 0xa710187d, 0x6ee89c63, 0x7bdb3bbb, 0x09cd2678, 0xf46e5918, 0x01ec9ab7, 0xa8834f9a, 0x65e6956e, 0x7eaaffe6, 0x0821bccf, 0xe6ef15e8, 0xd9bae79b, 0xce4a6f36, 0xd4ea9f09, 0xd629b07c, 0xaf31a4b2, 0x312a3f23, 0x30c6a594, 0xc035a266, 0x37744ebc, 0xa6fc82ca, 0xb0e090d0, 0x1533a7d8, 0x4af10498, 0xf741ecda, 0x0e7fcd50, 0x2f1791f6, 0x8d764dd6, 0x4d43efb0, 0x54ccaa4d, 0xdfe49604, 0xe39ed1b5, 0x1b4c6a88, 0xb8c12c1f, 0x7f466551, 0x049d5eea, 0x5d018c35, 0x73fa8774, 0x2efb0b41, 0x5ab3671d, 0x5292dbd2, 0x33e91056, 0x136dd647, 0x8c9ad761, 0x7a37a10c, 0x8e59f814, 0x89eb133c, 0xeecea927, 0x35b761c9, 0xede11ce5, 0x3c7a47b1, 0x599cd2df, 0x3f55f273, 0x791814ce, 0xbf73c737, 0xea53f7cd, 0x5b5ffdaa, 0x14df3d6f, 0x867844db, 0x81caaff3, 0x3eb968c4, 0x2c382434, 0x5fc2a340, 0x72161dc3, 0x0cbce225, 0x8b283c49, 0x41ff0d95, 0x7139a801, 0xde080cb3, 0x9cd8b4e4, 0x906456c1, 0x617bcb84, 0x70d532b6, 0x74486c5c, 0x42d0b857 ]
        T7 = [ 0xa75051f4, 0x65537e41, 0xa4c31a17, 0x5e963a27, 0x6bcb3bab, 0x45f11f9d, 0x58abacfa, 0x03934be3, 0xfa552030, 0x6df6ad76, 0x769188cc, 0x4c25f502, 0xd7fc4fe5, 0xcbd7c52a, 0x44802635, 0xa38fb562, 0x5a49deb1, 0x1b6725ba, 0x0e9845ea, 0xc0e15dfe, 0x7502c32f, 0xf012814c, 0x97a38d46, 0xf9c66bd3, 0x5fe7038f, 0x9c951592, 0x7aebbf6d, 0x59da9552, 0x832dd4be, 0x21d35874, 0x692949e0, 0xc8448ec9, 0x896a75c2, 0x7978f48e, 0x3e6b9958, 0x71dd27b9, 0x4fb6bee1, 0xad17f088, 0xac66c920, 0x3ab47dce, 0x4a1863df, 0x3182e51a, 0x33609751, 0x7f456253, 0x77e0b164, 0xae84bb6b, 0xa01cfe81, 0x2b94f908, 0x68587048, 0xfd198f45, 0x6c8794de, 0xf8b7527b, 0xd323ab73, 0x02e2724b, 0x8f57e31f, 0xab2a6655, 0x2807b2eb, 0xc2032fb5, 0x7b9a86c5, 0x08a5d337, 0x87f23028, 0xa5b223bf, 0x6aba0203, 0x825ced16, 0x1c2b8acf, 0xb492a779, 0xf2f0f307, 0xe2a14e69, 0xf4cd65da, 0xbed50605, 0x621fd134, 0xfe8ac4a6, 0x539d342e, 0x55a0a2f3, 0xe132058a, 0xeb75a4f6, 0xec390b83, 0xefaa4060, 0x9f065e71, 0x1051bd6e, 0x8af93e21, 0x063d96dd, 0x05aedd3e, 0xbd464de6, 0x8db59154, 0x5d0571c4, 0xd46f0406, 0x15ff6050, 0xfb241998, 0xe997d6bd, 0x43cc8940, 0x9e7767d9, 0x42bdb0e8, 0x8b880789, 0x5b38e719, 0xeedb79c8, 0x0a47a17c, 0x0fe97c42, 0x1ec9f884, 0x00000000, 0x86830980, 0xed48322b, 0x70ac1e11, 0x724e6c5a, 0xfffbfd0e, 0x38560f85, 0xd51e3dae, 0x3927362d, 0xd9640a0f, 0xa621685c, 0x54d19b5b, 0x2e3a2436, 0x67b10c0a, 0xe70f9357, 0x96d2b4ee, 0x919e1b9b, 0xc54f80c0, 0x20a261dc, 0x4b695a77, 0x1a161c12, 0xba0ae293, 0x2ae5c0a0, 0xe0433c22, 0x171d121b, 0x0d0b0e09, 0xc7adf28b, 0xa8b92db6, 0xa9c8141e, 0x198557f1, 0x074caf75, 0xddbbee99, 0x60fda37f, 0x269ff701, 0xf5bc5c72, 0x3bc54466, 0x7e345bfb, 0x29768b43, 0xc6dccb23, 0xfc68b6ed, 0xf163b8e4, 0xdccad731, 0x85104263, 0x22401397, 0x112084c6, 0x247d854a, 0x3df8d2bb, 0x3211aef9, 0xa16dc729, 0x2f4b1d9e, 0x30f3dcb2, 0x52ec0d86, 0xe3d077c1, 0x166c2bb3, 0xb999a970, 0x48fa1194, 0x642247e9, 0x8cc4a8fc, 0x3f1aa0f0, 0x2cd8567d, 0x90ef2233, 0x4ec78749, 0xd1c1d938, 0xa2fe8cca, 0x0b3698d4, 0x81cfa6f5, 0xde28a57a, 0x8e26dab7, 0xbfa43fad, 0x9de42c3a, 0x920d5078, 0xcc9b6a5f, 0x4662547e, 0x13c2f68d, 0xb8e890d8, 0xf75e2e39, 0xaff582c3, 0x80be9f5d, 0x937c69d0, 0x2da96fd5, 0x12b3cf25, 0x993bc8ac, 0x7da71018, 0x636ee89c, 0xbb7bdb3b, 0x7809cd26, 0x18f46e59, 0xb701ec9a, 0x9aa8834f, 0x6e65e695, 0xe67eaaff, 0xcf0821bc, 0xe8e6ef15, 0x9bd9bae7, 0x36ce4a6f, 0x09d4ea9f, 0x7cd629b0, 0xb2af31a4, 0x23312a3f, 0x9430c6a5, 0x66c035a2, 0xbc37744e, 0xcaa6fc82, 0xd0b0e090, 0xd81533a7, 0x984af104, 0xdaf741ec, 0x500e7fcd, 0xf62f1791, 0xd68d764d, 0xb04d43ef, 0x4d54ccaa, 0x04dfe496, 0xb5e39ed1, 0x881b4c6a, 0x1fb8c12c, 0x517f4665, 0xea049d5e, 0x355d018c, 0x7473fa87, 0x412efb0b, 0x1d5ab367, 0xd25292db, 0x5633e910, 0x47136dd6, 0x618c9ad7, 0x0c7a37a1, 0x148e59f8, 0x3c89eb13, 0x27eecea9, 0xc935b761, 0xe5ede11c, 0xb13c7a47, 0xdf599cd2, 0x733f55f2, 0xce791814, 0x37bf73c7, 0xcdea53f7, 0xaa5b5ffd, 0x6f14df3d, 0xdb867844, 0xf381caaf, 0xc43eb968, 0x342c3824, 0x405fc2a3, 0xc372161d, 0x250cbce2, 0x498b283c, 0x9541ff0d, 0x017139a8, 0xb3de080c, 0xe49cd8b4, 0xc1906456, 0x84617bcb, 0xb670d532, 0x5c74486c, 0x5742d0b8 ]
        T8 = [ 0xf4a75051, 0x4165537e, 0x17a4c31a, 0x275e963a, 0xab6bcb3b, 0x9d45f11f, 0xfa58abac, 0xe303934b, 0x30fa5520, 0x766df6ad, 0xcc769188, 0x024c25f5, 0xe5d7fc4f, 0x2acbd7c5, 0x35448026, 0x62a38fb5, 0xb15a49de, 0xba1b6725, 0xea0e9845, 0xfec0e15d, 0x2f7502c3, 0x4cf01281, 0x4697a38d, 0xd3f9c66b, 0x8f5fe703, 0x929c9515, 0x6d7aebbf, 0x5259da95, 0xbe832dd4, 0x7421d358, 0xe0692949, 0xc9c8448e, 0xc2896a75, 0x8e7978f4, 0x583e6b99, 0xb971dd27, 0xe14fb6be, 0x88ad17f0, 0x20ac66c9, 0xce3ab47d, 0xdf4a1863, 0x1a3182e5, 0x51336097, 0x537f4562, 0x6477e0b1, 0x6bae84bb, 0x81a01cfe, 0x082b94f9, 0x48685870, 0x45fd198f, 0xde6c8794, 0x7bf8b752, 0x73d323ab, 0x4b02e272, 0x1f8f57e3, 0x55ab2a66, 0xeb2807b2, 0xb5c2032f, 0xc57b9a86, 0x3708a5d3, 0x2887f230, 0xbfa5b223, 0x036aba02, 0x16825ced, 0xcf1c2b8a, 0x79b492a7, 0x07f2f0f3, 0x69e2a14e, 0xdaf4cd65, 0x05bed506, 0x34621fd1, 0xa6fe8ac4, 0x2e539d34, 0xf355a0a2, 0x8ae13205, 0xf6eb75a4, 0x83ec390b, 0x60efaa40, 0x719f065e, 0x6e1051bd, 0x218af93e, 0xdd063d96, 0x3e05aedd, 0xe6bd464d, 0x548db591, 0xc45d0571, 0x06d46f04, 0x5015ff60, 0x98fb2419, 0xbde997d6, 0x4043cc89, 0xd99e7767, 0xe842bdb0, 0x898b8807, 0x195b38e7, 0xc8eedb79, 0x7c0a47a1, 0x420fe97c, 0x841ec9f8, 0x00000000, 0x80868309, 0x2bed4832, 0x1170ac1e, 0x5a724e6c, 0x0efffbfd, 0x8538560f, 0xaed51e3d, 0x2d392736, 0x0fd9640a, 0x5ca62168, 0x5b54d19b, 0x362e3a24, 0x0a67b10c, 0x57e70f93, 0xee96d2b4, 0x9b919e1b, 0xc0c54f80, 0xdc20a261, 0x774b695a, 0x121a161c, 0x93ba0ae2, 0xa02ae5c0, 0x22e0433c, 0x1b171d12, 0x090d0b0e, 0x8bc7adf2, 0xb6a8b92d, 0x1ea9c814, 0xf1198557, 0x75074caf, 0x99ddbbee, 0x7f60fda3, 0x01269ff7, 0x72f5bc5c, 0x663bc544, 0xfb7e345b, 0x4329768b, 0x23c6dccb, 0xedfc68b6, 0xe4f163b8, 0x31dccad7, 0x63851042, 0x97224013, 0xc6112084, 0x4a247d85, 0xbb3df8d2, 0xf93211ae, 0x29a16dc7, 0x9e2f4b1d, 0xb230f3dc, 0x8652ec0d, 0xc1e3d077, 0xb3166c2b, 0x70b999a9, 0x9448fa11, 0xe9642247, 0xfc8cc4a8, 0xf03f1aa0, 0x7d2cd856, 0x3390ef22, 0x494ec787, 0x38d1c1d9, 0xcaa2fe8c, 0xd40b3698, 0xf581cfa6, 0x7ade28a5, 0xb78e26da, 0xadbfa43f, 0x3a9de42c, 0x78920d50, 0x5fcc9b6a, 0x7e466254, 0x8d13c2f6, 0xd8b8e890, 0x39f75e2e, 0xc3aff582, 0x5d80be9f, 0xd0937c69, 0xd52da96f, 0x2512b3cf, 0xac993bc8, 0x187da710, 0x9c636ee8, 0x3bbb7bdb, 0x267809cd, 0x5918f46e, 0x9ab701ec, 0x4f9aa883, 0x956e65e6, 0xffe67eaa, 0xbccf0821, 0x15e8e6ef, 0xe79bd9ba, 0x6f36ce4a, 0x9f09d4ea, 0xb07cd629, 0xa4b2af31, 0x3f23312a, 0xa59430c6, 0xa266c035, 0x4ebc3774, 0x82caa6fc, 0x90d0b0e0, 0xa7d81533, 0x04984af1, 0xecdaf741, 0xcd500e7f, 0x91f62f17, 0x4dd68d76, 0xefb04d43, 0xaa4d54cc, 0x9604dfe4, 0xd1b5e39e, 0x6a881b4c, 0x2c1fb8c1, 0x65517f46, 0x5eea049d, 0x8c355d01, 0x877473fa, 0x0b412efb, 0x671d5ab3, 0xdbd25292, 0x105633e9, 0xd647136d, 0xd7618c9a, 0xa10c7a37, 0xf8148e59, 0x133c89eb, 0xa927eece, 0x61c935b7, 0x1ce5ede1, 0x47b13c7a, 0xd2df599c, 0xf2733f55, 0x14ce7918, 0xc737bf73, 0xf7cdea53, 0xfdaa5b5f, 0x3d6f14df, 0x44db8678, 0xaff381ca, 0x68c43eb9, 0x24342c38, 0xa3405fc2, 0x1dc37216, 0xe2250cbc, 0x3c498b28, 0x0d9541ff, 0xa8017139, 0x0cb3de08, 0xb4e49cd8, 0x56c19064, 0xcb84617b, 0x32b670d5, 0x6c5c7448, 0xb85742d0 ]
        U1 = [ 0x00000000, 0x0e090d0b, 0x1c121a16, 0x121b171d, 0x3824342c, 0x362d3927, 0x24362e3a, 0x2a3f2331, 0x70486858, 0x7e416553, 0x6c5a724e, 0x62537f45, 0x486c5c74, 0x4665517f, 0x547e4662, 0x5a774b69, 0xe090d0b0, 0xee99ddbb, 0xfc82caa6, 0xf28bc7ad, 0xd8b4e49c, 0xd6bde997, 0xc4a6fe8a, 0xcaaff381, 0x90d8b8e8, 0x9ed1b5e3, 0x8ccaa2fe, 0x82c3aff5, 0xa8fc8cc4, 0xa6f581cf, 0xb4ee96d2, 0xbae79bd9, 0xdb3bbb7b, 0xd532b670, 0xc729a16d, 0xc920ac66, 0xe31f8f57, 0xed16825c, 0xff0d9541, 0xf104984a, 0xab73d323, 0xa57ade28, 0xb761c935, 0xb968c43e, 0x9357e70f, 0x9d5eea04, 0x8f45fd19, 0x814cf012, 0x3bab6bcb, 0x35a266c0, 0x27b971dd, 0x29b07cd6, 0x038f5fe7, 0x0d8652ec, 0x1f9d45f1, 0x119448fa, 0x4be30393, 0x45ea0e98, 0x57f11985, 0x59f8148e, 0x73c737bf, 0x7dce3ab4, 0x6fd52da9, 0x61dc20a2, 0xad766df6, 0xa37f60fd, 0xb16477e0, 0xbf6d7aeb, 0x955259da, 0x9b5b54d1, 0x894043cc, 0x87494ec7, 0xdd3e05ae, 0xd33708a5, 0xc12c1fb8, 0xcf2512b3, 0xe51a3182, 0xeb133c89, 0xf9082b94, 0xf701269f, 0x4de6bd46, 0x43efb04d, 0x51f4a750, 0x5ffdaa5b, 0x75c2896a, 0x7bcb8461, 0x69d0937c, 0x67d99e77, 0x3daed51e, 0x33a7d815, 0x21bccf08, 0x2fb5c203, 0x058ae132, 0x0b83ec39, 0x1998fb24, 0x1791f62f, 0x764dd68d, 0x7844db86, 0x6a5fcc9b, 0x6456c190, 0x4e69e2a1, 0x4060efaa, 0x527bf8b7, 0x5c72f5bc, 0x0605bed5, 0x080cb3de, 0x1a17a4c3, 0x141ea9c8, 0x3e218af9, 0x302887f2, 0x223390ef, 0x2c3a9de4, 0x96dd063d, 0x98d40b36, 0x8acf1c2b, 0x84c61120, 0xaef93211, 0xa0f03f1a, 0xb2eb2807, 0xbce2250c, 0xe6956e65, 0xe89c636e, 0xfa877473, 0xf48e7978, 0xdeb15a49, 0xd0b85742, 0xc2a3405f, 0xccaa4d54, 0x41ecdaf7, 0x4fe5d7fc, 0x5dfec0e1, 0x53f7cdea, 0x79c8eedb, 0x77c1e3d0, 0x65daf4cd, 0x6bd3f9c6, 0x31a4b2af, 0x3fadbfa4, 0x2db6a8b9, 0x23bfa5b2, 0x09808683, 0x07898b88, 0x15929c95, 0x1b9b919e, 0xa17c0a47, 0xaf75074c, 0xbd6e1051, 0xb3671d5a, 0x99583e6b, 0x97513360, 0x854a247d, 0x8b432976, 0xd134621f, 0xdf3d6f14, 0xcd267809, 0xc32f7502, 0xe9105633, 0xe7195b38, 0xf5024c25, 0xfb0b412e, 0x9ad7618c, 0x94de6c87, 0x86c57b9a, 0x88cc7691, 0xa2f355a0, 0xacfa58ab, 0xbee14fb6, 0xb0e842bd, 0xea9f09d4, 0xe49604df, 0xf68d13c2, 0xf8841ec9, 0xd2bb3df8, 0xdcb230f3, 0xcea927ee, 0xc0a02ae5, 0x7a47b13c, 0x744ebc37, 0x6655ab2a, 0x685ca621, 0x42638510, 0x4c6a881b, 0x5e719f06, 0x5078920d, 0x0a0fd964, 0x0406d46f, 0x161dc372, 0x1814ce79, 0x322bed48, 0x3c22e043, 0x2e39f75e, 0x2030fa55, 0xec9ab701, 0xe293ba0a, 0xf088ad17, 0xfe81a01c, 0xd4be832d, 0xdab78e26, 0xc8ac993b, 0xc6a59430, 0x9cd2df59, 0x92dbd252, 0x80c0c54f, 0x8ec9c844, 0xa4f6eb75, 0xaaffe67e, 0xb8e4f163, 0xb6edfc68, 0x0c0a67b1, 0x02036aba, 0x10187da7, 0x1e1170ac, 0x342e539d, 0x3a275e96, 0x283c498b, 0x26354480, 0x7c420fe9, 0x724b02e2, 0x605015ff, 0x6e5918f4, 0x44663bc5, 0x4a6f36ce, 0x587421d3, 0x567d2cd8, 0x37a10c7a, 0x39a80171, 0x2bb3166c, 0x25ba1b67, 0x0f853856, 0x018c355d, 0x13972240, 0x1d9e2f4b, 0x47e96422, 0x49e06929, 0x5bfb7e34, 0x55f2733f, 0x7fcd500e, 0x71c45d05, 0x63df4a18, 0x6dd64713, 0xd731dcca, 0xd938d1c1, 0xcb23c6dc, 0xc52acbd7, 0xef15e8e6, 0xe11ce5ed, 0xf307f2f0, 0xfd0efffb, 0xa779b492, 0xa970b999, 0xbb6bae84, 0xb562a38f, 0x9f5d80be, 0x91548db5, 0x834f9aa8, 0x8d4697a3 ]
        U2 = [ 0x00000000, 0x0b0e090d, 0x161c121a, 0x1d121b17, 0x2c382434, 0x27362d39, 0x3a24362e, 0x312a3f23, 0x58704868, 0x537e4165, 0x4e6c5a72, 0x4562537f, 0x74486c5c, 0x7f466551, 0x62547e46, 0x695a774b, 0xb0e090d0, 0xbbee99dd, 0xa6fc82ca, 0xadf28bc7, 0x9cd8b4e4, 0x97d6bde9, 0x8ac4a6fe, 0x81caaff3, 0xe890d8b8, 0xe39ed1b5, 0xfe8ccaa2, 0xf582c3af, 0xc4a8fc8c, 0xcfa6f581, 0xd2b4ee96, 0xd9bae79b, 0x7bdb3bbb, 0x70d532b6, 0x6dc729a1, 0x66c920ac, 0x57e31f8f, 0x5ced1682, 0x41ff0d95, 0x4af10498, 0x23ab73d3, 0x28a57ade, 0x35b761c9, 0x3eb968c4, 0x0f9357e7, 0x049d5eea, 0x198f45fd, 0x12814cf0, 0xcb3bab6b, 0xc035a266, 0xdd27b971, 0xd629b07c, 0xe7038f5f, 0xec0d8652, 0xf11f9d45, 0xfa119448, 0x934be303, 0x9845ea0e, 0x8557f119, 0x8e59f814, 0xbf73c737, 0xb47dce3a, 0xa96fd52d, 0xa261dc20, 0xf6ad766d, 0xfda37f60, 0xe0b16477, 0xebbf6d7a, 0xda955259, 0xd19b5b54, 0xcc894043, 0xc787494e, 0xaedd3e05, 0xa5d33708, 0xb8c12c1f, 0xb3cf2512, 0x82e51a31, 0x89eb133c, 0x94f9082b, 0x9ff70126, 0x464de6bd, 0x4d43efb0, 0x5051f4a7, 0x5b5ffdaa, 0x6a75c289, 0x617bcb84, 0x7c69d093, 0x7767d99e, 0x1e3daed5, 0x1533a7d8, 0x0821bccf, 0x032fb5c2, 0x32058ae1, 0x390b83ec, 0x241998fb, 0x2f1791f6, 0x8d764dd6, 0x867844db, 0x9b6a5fcc, 0x906456c1, 0xa14e69e2, 0xaa4060ef, 0xb7527bf8, 0xbc5c72f5, 0xd50605be, 0xde080cb3, 0xc31a17a4, 0xc8141ea9, 0xf93e218a, 0xf2302887, 0xef223390, 0xe42c3a9d, 0x3d96dd06, 0x3698d40b, 0x2b8acf1c, 0x2084c611, 0x11aef932, 0x1aa0f03f, 0x07b2eb28, 0x0cbce225, 0x65e6956e, 0x6ee89c63, 0x73fa8774, 0x78f48e79, 0x49deb15a, 0x42d0b857, 0x5fc2a340, 0x54ccaa4d, 0xf741ecda, 0xfc4fe5d7, 0xe15dfec0, 0xea53f7cd, 0xdb79c8ee, 0xd077c1e3, 0xcd65daf4, 0xc66bd3f9, 0xaf31a4b2, 0xa43fadbf, 0xb92db6a8, 0xb223bfa5, 0x83098086, 0x8807898b, 0x9515929c, 0x9e1b9b91, 0x47a17c0a, 0x4caf7507, 0x51bd6e10, 0x5ab3671d, 0x6b99583e, 0x60975133, 0x7d854a24, 0x768b4329, 0x1fd13462, 0x14df3d6f, 0x09cd2678, 0x02c32f75, 0x33e91056, 0x38e7195b, 0x25f5024c, 0x2efb0b41, 0x8c9ad761, 0x8794de6c, 0x9a86c57b, 0x9188cc76, 0xa0a2f355, 0xabacfa58, 0xb6bee14f, 0xbdb0e842, 0xd4ea9f09, 0xdfe49604, 0xc2f68d13, 0xc9f8841e, 0xf8d2bb3d, 0xf3dcb230, 0xeecea927, 0xe5c0a02a, 0x3c7a47b1, 0x37744ebc, 0x2a6655ab, 0x21685ca6, 0x10426385, 0x1b4c6a88, 0x065e719f, 0x0d507892, 0x640a0fd9, 0x6f0406d4, 0x72161dc3, 0x791814ce, 0x48322bed, 0x433c22e0, 0x5e2e39f7, 0x552030fa, 0x01ec9ab7, 0x0ae293ba, 0x17f088ad, 0x1cfe81a0, 0x2dd4be83, 0x26dab78e, 0x3bc8ac99, 0x30c6a594, 0x599cd2df, 0x5292dbd2, 0x4f80c0c5, 0x448ec9c8, 0x75a4f6eb, 0x7eaaffe6, 0x63b8e4f1, 0x68b6edfc, 0xb10c0a67, 0xba02036a, 0xa710187d, 0xac1e1170, 0x9d342e53, 0x963a275e, 0x8b283c49, 0x80263544, 0xe97c420f, 0xe2724b02, 0xff605015, 0xf46e5918, 0xc544663b, 0xce4a6f36, 0xd3587421, 0xd8567d2c, 0x7a37a10c, 0x7139a801, 0x6c2bb316, 0x6725ba1b, 0x560f8538, 0x5d018c35, 0x40139722, 0x4b1d9e2f, 0x2247e964, 0x2949e069, 0x345bfb7e, 0x3f55f273, 0x0e7fcd50, 0x0571c45d, 0x1863df4a, 0x136dd647, 0xcad731dc, 0xc1d938d1, 0xdccb23c6, 0xd7c52acb, 0xe6ef15e8, 0xede11ce5, 0xf0f307f2, 0xfbfd0eff, 0x92a779b4, 0x99a970b9, 0x84bb6bae, 0x8fb562a3, 0xbe9f5d80, 0xb591548d, 0xa8834f9a, 0xa38d4697 ]
        U3 = [ 0x00000000, 0x0d0b0e09, 0x1a161c12, 0x171d121b, 0x342c3824, 0x3927362d, 0x2e3a2436, 0x23312a3f, 0x68587048, 0x65537e41, 0x724e6c5a, 0x7f456253, 0x5c74486c, 0x517f4665, 0x4662547e, 0x4b695a77, 0xd0b0e090, 0xddbbee99, 0xcaa6fc82, 0xc7adf28b, 0xe49cd8b4, 0xe997d6bd, 0xfe8ac4a6, 0xf381caaf, 0xb8e890d8, 0xb5e39ed1, 0xa2fe8cca, 0xaff582c3, 0x8cc4a8fc, 0x81cfa6f5, 0x96d2b4ee, 0x9bd9bae7, 0xbb7bdb3b, 0xb670d532, 0xa16dc729, 0xac66c920, 0x8f57e31f, 0x825ced16, 0x9541ff0d, 0x984af104, 0xd323ab73, 0xde28a57a, 0xc935b761, 0xc43eb968, 0xe70f9357, 0xea049d5e, 0xfd198f45, 0xf012814c, 0x6bcb3bab, 0x66c035a2, 0x71dd27b9, 0x7cd629b0, 0x5fe7038f, 0x52ec0d86, 0x45f11f9d, 0x48fa1194, 0x03934be3, 0x0e9845ea, 0x198557f1, 0x148e59f8, 0x37bf73c7, 0x3ab47dce, 0x2da96fd5, 0x20a261dc, 0x6df6ad76, 0x60fda37f, 0x77e0b164, 0x7aebbf6d, 0x59da9552, 0x54d19b5b, 0x43cc8940, 0x4ec78749, 0x05aedd3e, 0x08a5d337, 0x1fb8c12c, 0x12b3cf25, 0x3182e51a, 0x3c89eb13, 0x2b94f908, 0x269ff701, 0xbd464de6, 0xb04d43ef, 0xa75051f4, 0xaa5b5ffd, 0x896a75c2, 0x84617bcb, 0x937c69d0, 0x9e7767d9, 0xd51e3dae, 0xd81533a7, 0xcf0821bc, 0xc2032fb5, 0xe132058a, 0xec390b83, 0xfb241998, 0xf62f1791, 0xd68d764d, 0xdb867844, 0xcc9b6a5f, 0xc1906456, 0xe2a14e69, 0xefaa4060, 0xf8b7527b, 0xf5bc5c72, 0xbed50605, 0xb3de080c, 0xa4c31a17, 0xa9c8141e, 0x8af93e21, 0x87f23028, 0x90ef2233, 0x9de42c3a, 0x063d96dd, 0x0b3698d4, 0x1c2b8acf, 0x112084c6, 0x3211aef9, 0x3f1aa0f0, 0x2807b2eb, 0x250cbce2, 0x6e65e695, 0x636ee89c, 0x7473fa87, 0x7978f48e, 0x5a49deb1, 0x5742d0b8, 0x405fc2a3, 0x4d54ccaa, 0xdaf741ec, 0xd7fc4fe5, 0xc0e15dfe, 0xcdea53f7, 0xeedb79c8, 0xe3d077c1, 0xf4cd65da, 0xf9c66bd3, 0xb2af31a4, 0xbfa43fad, 0xa8b92db6, 0xa5b223bf, 0x86830980, 0x8b880789, 0x9c951592, 0x919e1b9b, 0x0a47a17c, 0x074caf75, 0x1051bd6e, 0x1d5ab367, 0x3e6b9958, 0x33609751, 0x247d854a, 0x29768b43, 0x621fd134, 0x6f14df3d, 0x7809cd26, 0x7502c32f, 0x5633e910, 0x5b38e719, 0x4c25f502, 0x412efb0b, 0x618c9ad7, 0x6c8794de, 0x7b9a86c5, 0x769188cc, 0x55a0a2f3, 0x58abacfa, 0x4fb6bee1, 0x42bdb0e8, 0x09d4ea9f, 0x04dfe496, 0x13c2f68d, 0x1ec9f884, 0x3df8d2bb, 0x30f3dcb2, 0x27eecea9, 0x2ae5c0a0, 0xb13c7a47, 0xbc37744e, 0xab2a6655, 0xa621685c, 0x85104263, 0x881b4c6a, 0x9f065e71, 0x920d5078, 0xd9640a0f, 0xd46f0406, 0xc372161d, 0xce791814, 0xed48322b, 0xe0433c22, 0xf75e2e39, 0xfa552030, 0xb701ec9a, 0xba0ae293, 0xad17f088, 0xa01cfe81, 0x832dd4be, 0x8e26dab7, 0x993bc8ac, 0x9430c6a5, 0xdf599cd2, 0xd25292db, 0xc54f80c0, 0xc8448ec9, 0xeb75a4f6, 0xe67eaaff, 0xf163b8e4, 0xfc68b6ed, 0x67b10c0a, 0x6aba0203, 0x7da71018, 0x70ac1e11, 0x539d342e, 0x5e963a27, 0x498b283c, 0x44802635, 0x0fe97c42, 0x02e2724b, 0x15ff6050, 0x18f46e59, 0x3bc54466, 0x36ce4a6f, 0x21d35874, 0x2cd8567d, 0x0c7a37a1, 0x017139a8, 0x166c2bb3, 0x1b6725ba, 0x38560f85, 0x355d018c, 0x22401397, 0x2f4b1d9e, 0x642247e9, 0x692949e0, 0x7e345bfb, 0x733f55f2, 0x500e7fcd, 0x5d0571c4, 0x4a1863df, 0x47136dd6, 0xdccad731, 0xd1c1d938, 0xc6dccb23, 0xcbd7c52a, 0xe8e6ef15, 0xe5ede11c, 0xf2f0f307, 0xfffbfd0e, 0xb492a779, 0xb999a970, 0xae84bb6b, 0xa38fb562, 0x80be9f5d, 0x8db59154, 0x9aa8834f, 0x97a38d46 ]
        U4 = [ 0x00000000, 0x090d0b0e, 0x121a161c, 0x1b171d12, 0x24342c38, 0x2d392736, 0x362e3a24, 0x3f23312a, 0x48685870, 0x4165537e, 0x5a724e6c, 0x537f4562, 0x6c5c7448, 0x65517f46, 0x7e466254, 0x774b695a, 0x90d0b0e0, 0x99ddbbee, 0x82caa6fc, 0x8bc7adf2, 0xb4e49cd8, 0xbde997d6, 0xa6fe8ac4, 0xaff381ca, 0xd8b8e890, 0xd1b5e39e, 0xcaa2fe8c, 0xc3aff582, 0xfc8cc4a8, 0xf581cfa6, 0xee96d2b4, 0xe79bd9ba, 0x3bbb7bdb, 0x32b670d5, 0x29a16dc7, 0x20ac66c9, 0x1f8f57e3, 0x16825ced, 0x0d9541ff, 0x04984af1, 0x73d323ab, 0x7ade28a5, 0x61c935b7, 0x68c43eb9, 0x57e70f93, 0x5eea049d, 0x45fd198f, 0x4cf01281, 0xab6bcb3b, 0xa266c035, 0xb971dd27, 0xb07cd629, 0x8f5fe703, 0x8652ec0d, 0x9d45f11f, 0x9448fa11, 0xe303934b, 0xea0e9845, 0xf1198557, 0xf8148e59, 0xc737bf73, 0xce3ab47d, 0xd52da96f, 0xdc20a261, 0x766df6ad, 0x7f60fda3, 0x6477e0b1, 0x6d7aebbf, 0x5259da95, 0x5b54d19b, 0x4043cc89, 0x494ec787, 0x3e05aedd, 0x3708a5d3, 0x2c1fb8c1, 0x2512b3cf, 0x1a3182e5, 0x133c89eb, 0x082b94f9, 0x01269ff7, 0xe6bd464d, 0xefb04d43, 0xf4a75051, 0xfdaa5b5f, 0xc2896a75, 0xcb84617b, 0xd0937c69, 0xd99e7767, 0xaed51e3d, 0xa7d81533, 0xbccf0821, 0xb5c2032f, 0x8ae13205, 0x83ec390b, 0x98fb2419, 0x91f62f17, 0x4dd68d76, 0x44db8678, 0x5fcc9b6a, 0x56c19064, 0x69e2a14e, 0x60efaa40, 0x7bf8b752, 0x72f5bc5c, 0x05bed506, 0x0cb3de08, 0x17a4c31a, 0x1ea9c814, 0x218af93e, 0x2887f230, 0x3390ef22, 0x3a9de42c, 0xdd063d96, 0xd40b3698, 0xcf1c2b8a, 0xc6112084, 0xf93211ae, 0xf03f1aa0, 0xeb2807b2, 0xe2250cbc, 0x956e65e6, 0x9c636ee8, 0x877473fa, 0x8e7978f4, 0xb15a49de, 0xb85742d0, 0xa3405fc2, 0xaa4d54cc, 0xecdaf741, 0xe5d7fc4f, 0xfec0e15d, 0xf7cdea53, 0xc8eedb79, 0xc1e3d077, 0xdaf4cd65, 0xd3f9c66b, 0xa4b2af31, 0xadbfa43f, 0xb6a8b92d, 0xbfa5b223, 0x80868309, 0x898b8807, 0x929c9515, 0x9b919e1b, 0x7c0a47a1, 0x75074caf, 0x6e1051bd, 0x671d5ab3, 0x583e6b99, 0x51336097, 0x4a247d85, 0x4329768b, 0x34621fd1, 0x3d6f14df, 0x267809cd, 0x2f7502c3, 0x105633e9, 0x195b38e7, 0x024c25f5, 0x0b412efb, 0xd7618c9a, 0xde6c8794, 0xc57b9a86, 0xcc769188, 0xf355a0a2, 0xfa58abac, 0xe14fb6be, 0xe842bdb0, 0x9f09d4ea, 0x9604dfe4, 0x8d13c2f6, 0x841ec9f8, 0xbb3df8d2, 0xb230f3dc, 0xa927eece, 0xa02ae5c0, 0x47b13c7a, 0x4ebc3774, 0x55ab2a66, 0x5ca62168, 0x63851042, 0x6a881b4c, 0x719f065e, 0x78920d50, 0x0fd9640a, 0x06d46f04, 0x1dc37216, 0x14ce7918, 0x2bed4832, 0x22e0433c, 0x39f75e2e, 0x30fa5520, 0x9ab701ec, 0x93ba0ae2, 0x88ad17f0, 0x81a01cfe, 0xbe832dd4, 0xb78e26da, 0xac993bc8, 0xa59430c6, 0xd2df599c, 0xdbd25292, 0xc0c54f80, 0xc9c8448e, 0xf6eb75a4, 0xffe67eaa, 0xe4f163b8, 0xedfc68b6, 0x0a67b10c, 0x036aba02, 0x187da710, 0x1170ac1e, 0x2e539d34, 0x275e963a, 0x3c498b28, 0x35448026, 0x420fe97c, 0x4b02e272, 0x5015ff60, 0x5918f46e, 0x663bc544, 0x6f36ce4a, 0x7421d358, 0x7d2cd856, 0xa10c7a37, 0xa8017139, 0xb3166c2b, 0xba1b6725, 0x8538560f, 0x8c355d01, 0x97224013, 0x9e2f4b1d, 0xe9642247, 0xe0692949, 0xfb7e345b, 0xf2733f55, 0xcd500e7f, 0xc45d0571, 0xdf4a1863, 0xd647136d, 0x31dccad7, 0x38d1c1d9, 0x23c6dccb, 0x2acbd7c5, 0x15e8e6ef, 0x1ce5ede1, 0x07f2f0f3, 0x0efffbfd, 0x79b492a7, 0x70b999a9, 0x6bae84bb, 0x62a38fb5, 0x5d80be9f, 0x548db591, 0x4f9aa883, 0x4697a38d ]
        def __init__(self, key):
            rounds = self.number_of_rounds[len(key)]
            self._Ke = [[0] * 4 for i in xrange(rounds + 1)]
            self._Kd = [[0] * 4 for i in xrange(rounds + 1)]
            round_key_count = (rounds + 1) * 4
            KC = len(key) // 4
            def b2integer(b):
                idx,ret = 0,0
                for i in b[::-1]:
                    ret += i<<(idx*8)
                    idx += 1
                return ret
            tk = [ b2integer(key[i:i + 4]) for i in xrange(0, len(key), 4) ]
            for i in xrange(0, KC):
                self._Ke[i // 4][i % 4] = tk[i]
                self._Kd[rounds - (i // 4)][i % 4] = tk[i]
            rconpointer = 0
            t = KC
            while t < round_key_count:
                tt = tk[KC - 1]
                tk[0] ^= ((self.S[(tt >> 16) & 0xFF] << 24) ^
                          (self.S[(tt >>  8) & 0xFF] << 16) ^
                          (self.S[ tt        & 0xFF] <<  8) ^
                           self.S[(tt >> 24) & 0xFF]        ^
                          (self.rcon[rconpointer] << 24))
                rconpointer += 1
                if KC != 8:
                    for i in xrange(1, KC):
                        tk[i] ^= tk[i - 1]
                else:
                    for i in xrange(1, KC // 2):
                        tk[i] ^= tk[i - 1]
                    tt = tk[KC // 2 - 1]
                    tk[KC // 2] ^= (self.S[ tt        & 0xFF]        ^
                                   (self.S[(tt >>  8) & 0xFF] <<  8) ^
                                   (self.S[(tt >> 16) & 0xFF] << 16) ^
                                   (self.S[(tt >> 24) & 0xFF] << 24))
                    for i in xrange(KC // 2 + 1, KC):
                        tk[i] ^= tk[i - 1]
                j = 0
                while j < KC and t < round_key_count:
                    self._Ke[t // 4][t % 4] = tk[j]
                    self._Kd[rounds - (t // 4)][t % 4] = tk[j]
                    j += 1
                    t += 1
            for r in xrange(1, rounds):
                for j in xrange(0, 4):
                    tt = self._Kd[r][j]
                    self._Kd[r][j] = (self.U1[(tt >> 24) & 0xFF] ^
                                      self.U2[(tt >> 16) & 0xFF] ^
                                      self.U3[(tt >>  8) & 0xFF] ^
                                      self.U4[ tt        & 0xFF])
        def encrypt(self, plaintext):
            rounds = len(self._Ke) - 1
            (s1, s2, s3) = [1, 2, 3]
            a = [0, 0, 0, 0]
            t = [(_compact_word(plaintext[4 * i:4 * i + 4]) ^ self._Ke[0][i]) for i in xrange(0, 4)]
            for r in xrange(1, rounds):
                for i in xrange(0, 4):
                    a[i] = (self.T1[(t[ i          ] >> 24) & 0xFF] ^
                            self.T2[(t[(i + s1) % 4] >> 16) & 0xFF] ^
                            self.T3[(t[(i + s2) % 4] >>  8) & 0xFF] ^
                            self.T4[ t[(i + s3) % 4]        & 0xFF] ^
                            self._Ke[r][i])
                t = a.copy()
            result = [ ]
            for i in xrange(0, 4):
                tt = self._Ke[rounds][i]
                result.append((self.S[(t[ i           ] >> 24) & 0xFF] ^ (tt >> 24)) & 0xFF)
                result.append((self.S[(t[(i + s1) % 4] >> 16) & 0xFF] ^ (tt >> 16)) & 0xFF)
                result.append((self.S[(t[(i + s2) % 4] >>  8) & 0xFF] ^ (tt >>  8)) & 0xFF)
                result.append((self.S[ t[(i + s3) % 4]        & 0xFF] ^  tt       ) & 0xFF)
            return result
        def decrypt(self, ciphertext):
            rounds = len(self._Kd) - 1
            (s1, s2, s3) = [3, 2, 1]
            a = [0, 0, 0, 0]
            t = [(_compact_word(ciphertext[4 * i:4 * i + 4]) ^ self._Kd[0][i]) for i in xrange(0, 4)]
            for r in xrange(1, rounds):
                for i in xrange(0, 4):
                    a[i] = (self.T5[(t[ i          ] >> 24) & 0xFF] ^
                            self.T6[(t[(i + s1) % 4] >> 16) & 0xFF] ^
                            self.T7[(t[(i + s2) % 4] >>  8) & 0xFF] ^
                            self.T8[ t[(i + s3) % 4]        & 0xFF] ^
                            self._Kd[r][i])
                t = a.copy()
            result = [ ]
            for i in xrange(0, 4):
                tt = self._Kd[rounds][i]
                result.append((self.Si[(t[ i           ] >> 24) & 0xFF] ^ (tt >> 24)) & 0xFF)
                result.append((self.Si[(t[(i + s1) % 4] >> 16) & 0xFF] ^ (tt >> 16)) & 0xFF)
                result.append((self.Si[(t[(i + s2) % 4] >>  8) & 0xFF] ^ (tt >>  8)) & 0xFF)
                result.append((self.Si[ t[(i + s3) % 4]        & 0xFF] ^  tt       ) & 0xFF)
            return result
    class AESModeOfOperationCBC:
        def __init__(self, key, iv = None):
            self._aes = AES(key)
            if iv is None:
                self._last_cipherblock = [ 0 ] * 16
            else:
                self._last_cipherblock = _string_to_bytes(iv)
        def encrypt(self, plaintext):
            plaintext = _string_to_bytes(plaintext)
            precipherblock = [ (p ^ l) for (p, l) in zip(plaintext, self._last_cipherblock) ]
            self._last_cipherblock = self._aes.encrypt(precipherblock)
            return _bytes_to_string(self._last_cipherblock)
        def decrypt(self, ciphertext):
            cipherblock = _string_to_bytes(ciphertext)
            plaintext = [ (p ^ l) for (p, l) in zip(self._aes.decrypt(cipherblock), self._last_cipherblock) ]
            self._last_cipherblock = cipherblock
            return _bytes_to_string(plaintext)
    PADDING_NONE       = 'none'
    PADDING_DEFAULT    = 'default'
    def _get_byte(c):
        if isinstance(c, (bytes,int)):
            return c
        return ord(c)
    def to_bufferable(binary):
        if isinstance(binary, bytes):
            return binary
        return bytes(ord(b) for b in binary)
    def append_PKCS7_padding(data):
        pad = 16 - (len(data) % 16)
        return data + to_bufferable(chr(pad) * pad)
    def strip_PKCS7_padding(data): return data[:-_get_byte(data[-1])]
    def _block_can_consume(self, size):
        return 16 if size >= 16 else 0
    def _block_final_encrypt(self, data, padding = PADDING_DEFAULT):
        if padding == PADDING_DEFAULT: data = append_PKCS7_padding(data)
        if len(data) not in (16,32): raise Exception('invalid padding option')
        if len(data) == 32: return self.encrypt(data[:16]) + self.encrypt(data[16:])
        return self.encrypt(data)
    def _block_final_decrypt(self, data, padding = PADDING_DEFAULT):
        if padding == PADDING_DEFAULT: return strip_PKCS7_padding(self.decrypt(data))
        if padding == PADDING_NONE: return self.decrypt(data)
    AESModeOfOperationCBC._can_consume = _block_can_consume
    AESModeOfOperationCBC._final_encrypt = _block_final_encrypt
    AESModeOfOperationCBC._final_decrypt = _block_final_decrypt
    class BlockFeeder(object):
        def __init__(self, mode, feed, final, padding = PADDING_DEFAULT):
            self._mode = mode
            self._feed = feed
            self._final = final
            self._buffer = to_bufferable("")
            self._padding = padding

        def feed(self, data = None):
            if self._buffer is None:
                raise ValueError('already finished feeder')
            if data is None:
                result = self._final(self._buffer, self._padding)
                self._buffer = None
                return result

            self._buffer += to_bufferable(data)
            result = to_bufferable('')
            while len(self._buffer) > 0:
                can_consume = self._mode._can_consume(len(self._buffer) - 16)
                if can_consume == 0:
                    result += self._final(self._buffer, self._padding)
                    break
                result += self._feed(self._buffer[:can_consume])
                self._buffer = self._buffer[can_consume:]
            return result
    class Encrypter(BlockFeeder):
        def __init__(self, mode, padding = PADDING_DEFAULT):
            BlockFeeder.__init__(self, mode, mode.encrypt, mode._final_encrypt, padding)
    class Decrypter(BlockFeeder):
        def __init__(self, mode, padding = PADDING_DEFAULT):
            BlockFeeder.__init__(self, mode, mode.decrypt, mode._final_decrypt, padding)
    def _enc(data, key, vi, padding='default'):
        s = Encrypter(AESModeOfOperationCBC(key.encode(), iv), padding=padding)
        return b2a_hex(s.feed(data.encode())).decode()
    def _dec(data, key, iv, padding='default'):
        s = Decrypter(AESModeOfOperationCBC(key.encode(), iv), padding=padding)
        return s.feed(a2b_hex(data)).decode()
    def _enc_base(zdata, key, vi, padding='default', basefunc=base64.b64encode):
        s = Encrypter(AESModeOfOperationCBC(key.encode(), iv), padding=padding)
        return basefunc(s.feed(zdata)).decode()
    def _dec_base(data, key, iv, padding='default', basefunc=base64.b64decode):
        s = Decrypter(AESModeOfOperationCBC(key.encode(), iv), padding=padding)
        return s.feed(basefunc(data))
    class _: pass
    t = _()
    t.encrypt_a2b = lambda data: _enc(data, key, iv)
    t.decrypt_b2a = lambda data: _dec(data, key, iv)
    t.encrypt_base = lambda data, basefunc: _enc_base(data, key, iv, basefunc=basefunc)
    t.decrypt_base = lambda data, basefunc: _dec_base(data, key, iv, basefunc=basefunc)
    return t


def crypter(ack='',iv='2769514380123456',base='b64'):
    ahk = hmac.new(b'vilame',ack.encode(),'md5').hexdigest()
    c = CrypterAES(ahk, iv)
    if base == 'b16': _encode,_decode = base64.b16encode,base64.b16decode
    if base == 'b32': _encode,_decode = base64.b32encode,base64.b32decode
    if base == 'b64': _encode,_decode = base64.b64encode,base64.b64decode
    if base == 'b85': _encode,_decode = base64.b85encode,base64.b85decode
    if base == 'urlsafe_b64': _encode,_decode = base64.urlsafe_b64encode,base64.urlsafe_b64decode
    def zbase_enc(data):
        return _encode(zlib.compress(data.encode())[2:-4]).decode()
    def zbase_dec(basedata):
        return zlib.decompress(_decode(basedata),-15).decode()
    def zencrypt(data): return c.encrypt_base(zlib.compress(data.encode())[2:-4],_encode)
    def zdecrypt(data): return zlib.decompress(c.decrypt_base(data,_decode),-15).decode()
    c.zencrypt = zencrypt
    c.zdecrypt = zdecrypt
    c.zbase_enc = zbase_enc
    c.zbase_dec = zbase_dec
    c.encrypt = lambda data:c.encrypt_base(data,_encode)
    c.decrypt = lambda data:c.decrypt_base(data,_decode).decode()
    return c




def encode_window(setting=None):
    '''
    处理简单的加密编码对比
    '''
    fr = tkinter.Toplevel()
    fr.title('命令行输入 vv e 则可快速打开便捷加密窗口')
    fr.resizable(False, False)


    enb = ttk.Notebook(fr)
    enb_names = {} 

    _fr = Frame(fr)
    enb.add(_fr, text='hash')
    enb.pack()
    enb_names[_fr._name] = 'hash'


    f0 = Frame(_fr)
    f0.pack(side=tkinter.LEFT,fill=tkinter.BOTH,expand=True)

    f0_ = Frame(_fr)
    f0_.pack(side=tkinter.LEFT,fill=tkinter.BOTH,expand=True)

    f1 = Frame(f0)
    f2 = Frame(f0)
    f1.pack(fill=tkinter.BOTH,expand=True)
    f2.pack(fill=tkinter.BOTH,expand=True)

    algorithms = hashlib.algorithms_available

    ipadx   = 0
    ipady   = 0
    padx    = 1
    pady    = 1
    width   = 60
    sticky  = 'NESW'
    ft = Font(family='Consolas',size=10)

    crow = 0
    ls = []
    di = {}
    dh = {}
    allow = [
        'blake2b',
        'blake2s',
        'md4',
        'md5',
        'ripemd160',
        'sha',
        'sha1',
        'sha224',
        'sha256',
        'sha384',
        'sha3_224',
        'sha3_256',
        'sha3_384',
        'sha3_512',
        'sha512',
        'whirlpool'
    ]
    base64enc = [
        'b16',
        'b32',
        'b64',
        'b85',
        'urlsafe_b64',
    ]
    bs = {}
    for idx,name in enumerate(sorted(algorithms)+sorted(algorithms)+(base64enc)):
        if name in allow and idx < len(algorithms):
            hlen = len(hmac.new(b'',b'',name).hexdigest())
            l,e = Label(f2,text='[*]'+name+'[len:{}]'.format(str(hlen)),font=ft),Entry(f2,width=width,font=ft)
            dh[name] = e
            l.grid(row=idx,column=0,ipadx=ipadx,ipady=ipady,padx=padx,pady=pady,sticky=sticky)
            e.grid(row=idx,column=1,ipadx=ipadx,ipady=ipady,padx=padx,pady=pady,sticky=sticky)
        if name in allow and idx >= len(algorithms):
            hlen = len(hmac.new(b'',b'',name).hexdigest())
            l,e = Label(f2,text='[hmac]'+name+'[len:{}]'.format(str(hlen)),font=ft),Entry(f2,width=width,font=ft)
            di[name] = e
            l.grid(row=idx,column=0,ipadx=ipadx,ipady=ipady,padx=padx,pady=pady,sticky=sticky)
            e.grid(row=idx,column=1,ipadx=ipadx,ipady=ipady,padx=padx,pady=pady,sticky=sticky)
        if name in base64enc:
            l,e = Label(f2,text=name,font=ft),Entry(f2,width=width,font=ft)
            bs[name] = e
            l.grid(row=idx,column=0,ipadx=ipadx,ipady=ipady,padx=padx,pady=pady,sticky=sticky)
            e.grid(row=idx,column=1,ipadx=ipadx,ipady=ipady,padx=padx,pady=pady,sticky=sticky)

    def func(*a):
        def _show(*a, stat='show'):
            try:
                if stat == 'show': ss.pack(side=tkinter.LEFT)
                if stat == 'hide': ss.pack_forget()
            except:
                pass
        _show(stat='show') if va.get() else _show(stat='hide')

    f11 = Frame(f1)
    f11.pack(fill=tkinter.X)

    def _switch_case(*a):
        for name,ge in di.items():
            try:
                v = ge.get().upper() if ca.get() else ge.get().lower()
                ge.delete(0,tkinter.END)
                ge.insert(0,v)
            except:
                import traceback; traceback.print_exc()
                print('error',name)
        for name,ge in dh.items():
            try:
                v = ge.get().upper() if ca.get() else ge.get().lower()
                ge.delete(0,tkinter.END)
                ge.insert(0,v)
            except:
                import traceback; traceback.print_exc()
                print('error',name)

    def _swich_encd(*a):
        s = en.get().strip()
        if s == 'utf-8':
            en.delete(0,tkinter.END)
            en.insert(0,'gbk')
        elif s == 'gbk':
            en.delete(0,tkinter.END)
            en.insert(0,'utf-8')
        else:
            en.delete(0,tkinter.END)
            en.insert(0,'utf-8')

    ca = tkinter.IntVar()
    rb = Checkbutton(f11,text='hash编码是否大写',variable=ca,command=_switch_case)
    rb.pack(side=tkinter.RIGHT)
    rb.deselect()

    en = Entry(f11, width=6, font=ft)
    en.insert(0,'utf-8')
    en.pack(side=tkinter.RIGHT)
    Button(f11,text='编码方式',command=_swich_encd).pack(side=tkinter.RIGHT,padx=2)

    ss = Entry(f11)
    va = tkinter.IntVar()
    rb = Checkbutton(f11,text='添加密盐参数',variable=va,command=func)
    rb.pack(side=tkinter.LEFT,padx=10)

    Label(f1,text='加密或编解码文本').pack(side=tkinter.LEFT,padx=10)
    ee = Entry(f1)
    ee.pack(side=tkinter.LEFT)

    def _encode_all(*a):
        encd = en.get().strip()
        salt = ss.get().encode(encd) if va.get() else b''
        text = ee.get().encode(encd)
        for name,ge in di.items():
            try:
                v = hmac.new(salt,text,name).hexdigest()
                v = v.upper() if ca.get() else v.lower()
                ge.delete(0,tkinter.END)
                ge.insert(0,v)
            except:
                import traceback; traceback.print_exc()
                print('error',name)

    def _encode_hash(*a):
        encd = en.get().strip()
        salt = ss.get().encode(encd) if va.get() else b''
        text = ee.get().encode(encd)
        for name,ge in dh.items():
            try:
                v = hashlib.new(name,text).hexdigest()
                v = v.upper() if ca.get() else v.lower()
                ge.delete(0,tkinter.END)
                ge.insert(0,v)
            except:
                import traceback; traceback.print_exc()
                print('error',name)
    
    def _b_encode(*a):
        encd = en.get().strip()
        text = ee.get().encode(encd).strip()
        for name,ge in bs.items():
            try:
                if name == 'b16': _encode = base64.b16encode
                if name == 'b32': _encode = base64.b32encode
                if name == 'b64': _encode = base64.b64encode
                if name == 'b85': _encode = base64.b85encode
                if name == 'urlsafe_b64': _encode = base64.urlsafe_b64encode
                ge.delete(0,tkinter.END)
                ge.insert(0,_encode(text))
            except:
                import traceback; traceback.print_exc()
                print('error',name)
                txt.see(tkinter.END)


    def _b_decode(*a):
        encd = en.get().strip()
        text = ee.get().encode(encd).strip()
        if not text:return 
        for name,ge in bs.items():
            try:
                if name == 'b16': _decode = base64.b16decode
                if name == 'b32': _decode = base64.b32decode
                if name == 'b64': _decode = base64.b64decode
                if name == 'b85': _decode = base64.b85decode
                if name == 'urlsafe_b64': _decode = base64.urlsafe_b64decode
                ge.delete(0,tkinter.END)
                d = _decode(text)
                ge.insert(0,d.decode(encd))
                print('[success:{}]'.format(name),d.decode(encd))
            except:
                import traceback; traceback.print_exc()
                print('[error:{}]'.format(name),repr(d) if 'd' in locals() else '')
                txt.see(tkinter.END)
        print('---- end ----')

    Button(f1, text='base64解码',command=_b_decode).pack(side=tkinter.RIGHT)
    Button(f1, text='base64编码',command=_b_encode).pack(side=tkinter.RIGHT)
    Button(f1, text='hmac',command=_encode_all,width=5).pack(side=tkinter.RIGHT)
    Button(f1, text='hash',command=_encode_hash,width=5).pack(side=tkinter.RIGHT)

    f1_ = Frame(f0_)
    f1_.pack(fill=tkinter.BOTH)
    f2_ = Frame(f0_)
    f2_.pack(fill=tkinter.BOTH,expand=True)

    lb_ = Label(f1_,text='compare(对比字符串)')
    lb_.pack(side=tkinter.LEFT,padx=10,pady=pady)
    et_ = Entry(f1_,width=30)
    et_.pack(side=tkinter.LEFT,padx=padx,pady=pady)

    import difflib
    def _diff_log(a, b):
        d = difflib.Differ()
        s = d.compare(a.splitlines(), b.splitlines())
        for i in s:
            print(i)

    def print(*a):
        # import pprint
        # pprint.pprint(enb_names)
        name = enb.select().rsplit('.')[-1]
        if enb_names[name] == 'hash':
            txt.insert(tkinter.END,' '.join(map(str,a)) + '\n')
        elif enb_names[name] == '加密':
            ftxt.insert(tkinter.END,' '.join(map(str,a)) + '\n')

    def _analysis_diff(*a):
        txt.delete(0.,tkinter.END)
        it = []
        for name,ge in list(dh.items()) + list(bs.items()):
            try:
                a, b = et_.get(), ge.get()
                s = difflib.SequenceMatcher(None, a.upper(), b.upper())
                q = s.find_longest_match(0, len(a), 0, len(b))
                if q.size>0:
                    it.append([name, a, b, q.size])
            except:
                import traceback; traceback.print_exc()
                print('error',name)
        for name,ge in list(di.items()):
            try:
                a, b = et_.get(), ge.get()
                s = difflib.SequenceMatcher(None, a.upper(), b.upper())
                q = s.find_longest_match(0, len(a), 0, len(b))
                if q.size>0:
                    it.append(['[hmac]'+name, a, b, q.size])
            except:
                import traceback; traceback.print_exc()
                print('error',name)

        cnt = 0
        for name,a,b,max_match in sorted(it,key=lambda max_match:-max_match[3])[:5]:
            cnt += 1
            s = difflib.SequenceMatcher(None, a.upper(), b.upper())
            print('max_match_len:{}'.format(max_match))
            print('len[compare]:{}'.format(len(a), ))
            print('len[{}]:{}'.format(name, len(b)))
            matchcnt = 0
            for match in sorted(s.get_matching_blocks(),key=lambda i:-i.size):
                if match.size:
                    v = a[match.a:match.a+match.size]
                    matchcnt += match.size
                    print('    [match.size:{}]  {}'.format(match.size, v))
            print('    [match.count:{}]'.format(matchcnt))
            print('---------------')
        if not cnt:
            print('not match.')

    def _creat_code(*a):
        import pprint
        txt.delete(0.,tkinter.END)
        salt = ss.get().strip() if va.get() else ''
        text = ee.get().strip()
        compare_str = et_.get().strip()
        code = '''
import hmac
import difflib

allow = \
$allow

salt = '$salt' # 字符串/byte类型  盐（默认空）
text = '$text' # 字符串/byte类型  需要被加密的数据
upper = True


def encode_all(salt, text):
    salt = salt.encode() if type(salt) == str else salt
    text = text.encode() if type(text) == str else text
    for name in allow:
        v = hmac.new(salt,text,name).hexdigest()
        v = v.upper() if upper else v.lower()
        print('{:<10}{}'.format(name, v))


def compare_encode(salt, text, compare_str):
    salt = salt.encode() if type(salt) == str else salt
    text = text.encode() if type(text) == str else text
    it = []
    for name in allow:
        v = hmac.new(salt,text,name).hexdigest()
        v = v.upper() if upper else v.lower()
        a, b = v, compare_str
        s = difflib.SequenceMatcher(None, a.upper(), b.upper())
        q = s.find_longest_match(0, len(a), 0, len(b))
        if q.size>0:
            it.append([name, a, b, q.size])
    # 因为这类加密的互异性很高，所以只获取前三个最长匹配的加密字符串对比查看
    p = '-'
    for name,a,b,max_match in sorted(it,key=lambda max_match:-max_match[3])[:3]:
        s = difflib.SequenceMatcher(None, a.upper(), b.upper())
        prefix = '[len:compare]:{:<5} {:<18}'.format(len(a), p + '[len:{}]:{}'.format(name, len(b)))
        p = '-' if p == '+' else '+'
        for match in sorted(s.get_matching_blocks(),key=lambda i:-i.size):
            if match.size:
                v = a[match.a:match.a+match.size]
                print('{} [match.size:{}]  {}'.format(prefix, match.size, v))


encode_all(salt, text)
compare_str = '$compare_str' # 需要被对比的字符串
compare_encode(salt, text, compare_str)
        '''.strip()
        code = code.replace('$allow', pprint.pformat(allow))
        code = code.replace('$compare_str', compare_str)
        code = code.replace('$salt', salt)
        code = code.replace('$text', text)
        print(code)


    bt_ = Button(f1_,text='分析对比[忽略大小写]',command=_analysis_diff)
    bt_.pack(side=tkinter.LEFT,padx=padx,pady=pady,)
    bt2_ = Button(f1_,text='测用代码',command=_creat_code)
    bt2_.pack(side=tkinter.LEFT,padx=padx,pady=pady,)

    txt = Text(f2_,font=ft)
    txt.pack(padx=padx,pady=pady,fill=tkinter.BOTH,expand=True)







    _fr0 = Frame(fr)
    enb.add(_fr0, text='加密')
    enb.pack()
    enb_names[_fr0._name] = '加密'

    ff0 = Frame(_fr0)
    ff0.pack(side=tkinter.LEFT,fill=tkinter.BOTH,expand=True)

    ff0_ = Frame(_fr0)
    ff0_.pack(side=tkinter.LEFT,fill=tkinter.BOTH,expand=True)

    def _my_encode(*a):
        estr = ftxt.get(0.,tkinter.END).strip('\n')
        ftxt.delete(0.,tkinter.END)
        _ack = ent22.get().strip() if aa.get() else ''
        base = cbx.get()
        c = crypter(_ack, base=base)
        print(c.zencrypt(estr))


    def _my_decode(*a):
        dstr = ftxt.get(0.,tkinter.END).strip('\n')
        _ack = ent22.get().strip() if aa.get() else ''
        base = cbx.get()
        c = crypter(_ack, base=base)
        try:
            s = c.zdecrypt(dstr)
            ftxt.delete(0.,tkinter.END)
            print(s)
        except:
            tkinter.messagebox.showinfo('Error','密码或解密文本错误.\n\n'+traceback.format_exc())

    def _my_code(*a):
        ftxt.delete(0.,tkinter.END)
        code = '''
import hmac
import zlib
import base64
from binascii import a2b_hex, b2a_hex


def CrypterAES(key, iv):

    def _compact_word(word):
        return (word[0] << 24) | (word[1] << 16) | (word[2] << 8) | word[3]
    xrange = range
    def _string_to_bytes(text):
        if isinstance(text, bytes):
            return text
        return [ord(c) for c in text]
    def _bytes_to_string(binary): return bytes(binary)
    class AES(object):
        number_of_rounds = {16: 10, 24: 12, 32: 14}
        rcon = [ 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36, 0x6c, 0xd8, 0xab, 0x4d, 0x9a, 0x2f, 0x5e, 0xbc, 0x63, 0xc6, 0x97, 0x35, 0x6a, 0xd4, 0xb3, 0x7d, 0xfa, 0xef, 0xc5, 0x91 ]
        S = [ 0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76, 0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0, 0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15, 0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75, 0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84, 0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf, 0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8, 0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2, 0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73, 0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb, 0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79, 0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08, 0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a, 0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e, 0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf, 0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16 ]
        Si =[ 0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38, 0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7, 0xfb, 0x7c, 0xe3, 0x39, 0x82, 0x9b, 0x2f, 0xff, 0x87, 0x34, 0x8e, 0x43, 0x44, 0xc4, 0xde, 0xe9, 0xcb, 0x54, 0x7b, 0x94, 0x32, 0xa6, 0xc2, 0x23, 0x3d, 0xee, 0x4c, 0x95, 0x0b, 0x42, 0xfa, 0xc3, 0x4e, 0x08, 0x2e, 0xa1, 0x66, 0x28, 0xd9, 0x24, 0xb2, 0x76, 0x5b, 0xa2, 0x49, 0x6d, 0x8b, 0xd1, 0x25, 0x72, 0xf8, 0xf6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xd4, 0xa4, 0x5c, 0xcc, 0x5d, 0x65, 0xb6, 0x92, 0x6c, 0x70, 0x48, 0x50, 0xfd, 0xed, 0xb9, 0xda, 0x5e, 0x15, 0x46, 0x57, 0xa7, 0x8d, 0x9d, 0x84, 0x90, 0xd8, 0xab, 0x00, 0x8c, 0xbc, 0xd3, 0x0a, 0xf7, 0xe4, 0x58, 0x05, 0xb8, 0xb3, 0x45, 0x06, 0xd0, 0x2c, 0x1e, 0x8f, 0xca, 0x3f, 0x0f, 0x02, 0xc1, 0xaf, 0xbd, 0x03, 0x01, 0x13, 0x8a, 0x6b, 0x3a, 0x91, 0x11, 0x41, 0x4f, 0x67, 0xdc, 0xea, 0x97, 0xf2, 0xcf, 0xce, 0xf0, 0xb4, 0xe6, 0x73, 0x96, 0xac, 0x74, 0x22, 0xe7, 0xad, 0x35, 0x85, 0xe2, 0xf9, 0x37, 0xe8, 0x1c, 0x75, 0xdf, 0x6e, 0x47, 0xf1, 0x1a, 0x71, 0x1d, 0x29, 0xc5, 0x89, 0x6f, 0xb7, 0x62, 0x0e, 0xaa, 0x18, 0xbe, 0x1b, 0xfc, 0x56, 0x3e, 0x4b, 0xc6, 0xd2, 0x79, 0x20, 0x9a, 0xdb, 0xc0, 0xfe, 0x78, 0xcd, 0x5a, 0xf4, 0x1f, 0xdd, 0xa8, 0x33, 0x88, 0x07, 0xc7, 0x31, 0xb1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xec, 0x5f, 0x60, 0x51, 0x7f, 0xa9, 0x19, 0xb5, 0x4a, 0x0d, 0x2d, 0xe5, 0x7a, 0x9f, 0x93, 0xc9, 0x9c, 0xef, 0xa0, 0xe0, 0x3b, 0x4d, 0xae, 0x2a, 0xf5, 0xb0, 0xc8, 0xeb, 0xbb, 0x3c, 0x83, 0x53, 0x99, 0x61, 0x17, 0x2b, 0x04, 0x7e, 0xba, 0x77, 0xd6, 0x26, 0xe1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0c, 0x7d ] 
        T1 = [ 0xc66363a5, 0xf87c7c84, 0xee777799, 0xf67b7b8d, 0xfff2f20d, 0xd66b6bbd, 0xde6f6fb1, 0x91c5c554, 0x60303050, 0x02010103, 0xce6767a9, 0x562b2b7d, 0xe7fefe19, 0xb5d7d762, 0x4dababe6, 0xec76769a, 0x8fcaca45, 0x1f82829d, 0x89c9c940, 0xfa7d7d87, 0xeffafa15, 0xb25959eb, 0x8e4747c9, 0xfbf0f00b, 0x41adadec, 0xb3d4d467, 0x5fa2a2fd, 0x45afafea, 0x239c9cbf, 0x53a4a4f7, 0xe4727296, 0x9bc0c05b, 0x75b7b7c2, 0xe1fdfd1c, 0x3d9393ae, 0x4c26266a, 0x6c36365a, 0x7e3f3f41, 0xf5f7f702, 0x83cccc4f, 0x6834345c, 0x51a5a5f4, 0xd1e5e534, 0xf9f1f108, 0xe2717193, 0xabd8d873, 0x62313153, 0x2a15153f, 0x0804040c, 0x95c7c752, 0x46232365, 0x9dc3c35e, 0x30181828, 0x379696a1, 0x0a05050f, 0x2f9a9ab5, 0x0e070709, 0x24121236, 0x1b80809b, 0xdfe2e23d, 0xcdebeb26, 0x4e272769, 0x7fb2b2cd, 0xea75759f, 0x1209091b, 0x1d83839e, 0x582c2c74, 0x341a1a2e, 0x361b1b2d, 0xdc6e6eb2, 0xb45a5aee, 0x5ba0a0fb, 0xa45252f6, 0x763b3b4d, 0xb7d6d661, 0x7db3b3ce, 0x5229297b, 0xdde3e33e, 0x5e2f2f71, 0x13848497, 0xa65353f5, 0xb9d1d168, 0x00000000, 0xc1eded2c, 0x40202060, 0xe3fcfc1f, 0x79b1b1c8, 0xb65b5bed, 0xd46a6abe, 0x8dcbcb46, 0x67bebed9, 0x7239394b, 0x944a4ade, 0x984c4cd4, 0xb05858e8, 0x85cfcf4a, 0xbbd0d06b, 0xc5efef2a, 0x4faaaae5, 0xedfbfb16, 0x864343c5, 0x9a4d4dd7, 0x66333355, 0x11858594, 0x8a4545cf, 0xe9f9f910, 0x04020206, 0xfe7f7f81, 0xa05050f0, 0x783c3c44, 0x259f9fba, 0x4ba8a8e3, 0xa25151f3, 0x5da3a3fe, 0x804040c0, 0x058f8f8a, 0x3f9292ad, 0x219d9dbc, 0x70383848, 0xf1f5f504, 0x63bcbcdf, 0x77b6b6c1, 0xafdada75, 0x42212163, 0x20101030, 0xe5ffff1a, 0xfdf3f30e, 0xbfd2d26d, 0x81cdcd4c, 0x180c0c14, 0x26131335, 0xc3ecec2f, 0xbe5f5fe1, 0x359797a2, 0x884444cc, 0x2e171739, 0x93c4c457, 0x55a7a7f2, 0xfc7e7e82, 0x7a3d3d47, 0xc86464ac, 0xba5d5de7, 0x3219192b, 0xe6737395, 0xc06060a0, 0x19818198, 0x9e4f4fd1, 0xa3dcdc7f, 0x44222266, 0x542a2a7e, 0x3b9090ab, 0x0b888883, 0x8c4646ca, 0xc7eeee29, 0x6bb8b8d3, 0x2814143c, 0xa7dede79, 0xbc5e5ee2, 0x160b0b1d, 0xaddbdb76, 0xdbe0e03b, 0x64323256, 0x743a3a4e, 0x140a0a1e, 0x924949db, 0x0c06060a, 0x4824246c, 0xb85c5ce4, 0x9fc2c25d, 0xbdd3d36e, 0x43acacef, 0xc46262a6, 0x399191a8, 0x319595a4, 0xd3e4e437, 0xf279798b, 0xd5e7e732, 0x8bc8c843, 0x6e373759, 0xda6d6db7, 0x018d8d8c, 0xb1d5d564, 0x9c4e4ed2, 0x49a9a9e0, 0xd86c6cb4, 0xac5656fa, 0xf3f4f407, 0xcfeaea25, 0xca6565af, 0xf47a7a8e, 0x47aeaee9, 0x10080818, 0x6fbabad5, 0xf0787888, 0x4a25256f, 0x5c2e2e72, 0x381c1c24, 0x57a6a6f1, 0x73b4b4c7, 0x97c6c651, 0xcbe8e823, 0xa1dddd7c, 0xe874749c, 0x3e1f1f21, 0x964b4bdd, 0x61bdbddc, 0x0d8b8b86, 0x0f8a8a85, 0xe0707090, 0x7c3e3e42, 0x71b5b5c4, 0xcc6666aa, 0x904848d8, 0x06030305, 0xf7f6f601, 0x1c0e0e12, 0xc26161a3, 0x6a35355f, 0xae5757f9, 0x69b9b9d0, 0x17868691, 0x99c1c158, 0x3a1d1d27, 0x279e9eb9, 0xd9e1e138, 0xebf8f813, 0x2b9898b3, 0x22111133, 0xd26969bb, 0xa9d9d970, 0x078e8e89, 0x339494a7, 0x2d9b9bb6, 0x3c1e1e22, 0x15878792, 0xc9e9e920, 0x87cece49, 0xaa5555ff, 0x50282878, 0xa5dfdf7a, 0x038c8c8f, 0x59a1a1f8, 0x09898980, 0x1a0d0d17, 0x65bfbfda, 0xd7e6e631, 0x844242c6, 0xd06868b8, 0x824141c3, 0x299999b0, 0x5a2d2d77, 0x1e0f0f11, 0x7bb0b0cb, 0xa85454fc, 0x6dbbbbd6, 0x2c16163a ]
        T2 = [ 0xa5c66363, 0x84f87c7c, 0x99ee7777, 0x8df67b7b, 0x0dfff2f2, 0xbdd66b6b, 0xb1de6f6f, 0x5491c5c5, 0x50603030, 0x03020101, 0xa9ce6767, 0x7d562b2b, 0x19e7fefe, 0x62b5d7d7, 0xe64dabab, 0x9aec7676, 0x458fcaca, 0x9d1f8282, 0x4089c9c9, 0x87fa7d7d, 0x15effafa, 0xebb25959, 0xc98e4747, 0x0bfbf0f0, 0xec41adad, 0x67b3d4d4, 0xfd5fa2a2, 0xea45afaf, 0xbf239c9c, 0xf753a4a4, 0x96e47272, 0x5b9bc0c0, 0xc275b7b7, 0x1ce1fdfd, 0xae3d9393, 0x6a4c2626, 0x5a6c3636, 0x417e3f3f, 0x02f5f7f7, 0x4f83cccc, 0x5c683434, 0xf451a5a5, 0x34d1e5e5, 0x08f9f1f1, 0x93e27171, 0x73abd8d8, 0x53623131, 0x3f2a1515, 0x0c080404, 0x5295c7c7, 0x65462323, 0x5e9dc3c3, 0x28301818, 0xa1379696, 0x0f0a0505, 0xb52f9a9a, 0x090e0707, 0x36241212, 0x9b1b8080, 0x3ddfe2e2, 0x26cdebeb, 0x694e2727, 0xcd7fb2b2, 0x9fea7575, 0x1b120909, 0x9e1d8383, 0x74582c2c, 0x2e341a1a, 0x2d361b1b, 0xb2dc6e6e, 0xeeb45a5a, 0xfb5ba0a0, 0xf6a45252, 0x4d763b3b, 0x61b7d6d6, 0xce7db3b3, 0x7b522929, 0x3edde3e3, 0x715e2f2f, 0x97138484, 0xf5a65353, 0x68b9d1d1, 0x00000000, 0x2cc1eded, 0x60402020, 0x1fe3fcfc, 0xc879b1b1, 0xedb65b5b, 0xbed46a6a, 0x468dcbcb, 0xd967bebe, 0x4b723939, 0xde944a4a, 0xd4984c4c, 0xe8b05858, 0x4a85cfcf, 0x6bbbd0d0, 0x2ac5efef, 0xe54faaaa, 0x16edfbfb, 0xc5864343, 0xd79a4d4d, 0x55663333, 0x94118585, 0xcf8a4545, 0x10e9f9f9, 0x06040202, 0x81fe7f7f, 0xf0a05050, 0x44783c3c, 0xba259f9f, 0xe34ba8a8, 0xf3a25151, 0xfe5da3a3, 0xc0804040, 0x8a058f8f, 0xad3f9292, 0xbc219d9d, 0x48703838, 0x04f1f5f5, 0xdf63bcbc, 0xc177b6b6, 0x75afdada, 0x63422121, 0x30201010, 0x1ae5ffff, 0x0efdf3f3, 0x6dbfd2d2, 0x4c81cdcd, 0x14180c0c, 0x35261313, 0x2fc3ecec, 0xe1be5f5f, 0xa2359797, 0xcc884444, 0x392e1717, 0x5793c4c4, 0xf255a7a7, 0x82fc7e7e, 0x477a3d3d, 0xacc86464, 0xe7ba5d5d, 0x2b321919, 0x95e67373, 0xa0c06060, 0x98198181, 0xd19e4f4f, 0x7fa3dcdc, 0x66442222, 0x7e542a2a, 0xab3b9090, 0x830b8888, 0xca8c4646, 0x29c7eeee, 0xd36bb8b8, 0x3c281414, 0x79a7dede, 0xe2bc5e5e, 0x1d160b0b, 0x76addbdb, 0x3bdbe0e0, 0x56643232, 0x4e743a3a, 0x1e140a0a, 0xdb924949, 0x0a0c0606, 0x6c482424, 0xe4b85c5c, 0x5d9fc2c2, 0x6ebdd3d3, 0xef43acac, 0xa6c46262, 0xa8399191, 0xa4319595, 0x37d3e4e4, 0x8bf27979, 0x32d5e7e7, 0x438bc8c8, 0x596e3737, 0xb7da6d6d, 0x8c018d8d, 0x64b1d5d5, 0xd29c4e4e, 0xe049a9a9, 0xb4d86c6c, 0xfaac5656, 0x07f3f4f4, 0x25cfeaea, 0xafca6565, 0x8ef47a7a, 0xe947aeae, 0x18100808, 0xd56fbaba, 0x88f07878, 0x6f4a2525, 0x725c2e2e, 0x24381c1c, 0xf157a6a6, 0xc773b4b4, 0x5197c6c6, 0x23cbe8e8, 0x7ca1dddd, 0x9ce87474, 0x213e1f1f, 0xdd964b4b, 0xdc61bdbd, 0x860d8b8b, 0x850f8a8a, 0x90e07070, 0x427c3e3e, 0xc471b5b5, 0xaacc6666, 0xd8904848, 0x05060303, 0x01f7f6f6, 0x121c0e0e, 0xa3c26161, 0x5f6a3535, 0xf9ae5757, 0xd069b9b9, 0x91178686, 0x5899c1c1, 0x273a1d1d, 0xb9279e9e, 0x38d9e1e1, 0x13ebf8f8, 0xb32b9898, 0x33221111, 0xbbd26969, 0x70a9d9d9, 0x89078e8e, 0xa7339494, 0xb62d9b9b, 0x223c1e1e, 0x92158787, 0x20c9e9e9, 0x4987cece, 0xffaa5555, 0x78502828, 0x7aa5dfdf, 0x8f038c8c, 0xf859a1a1, 0x80098989, 0x171a0d0d, 0xda65bfbf, 0x31d7e6e6, 0xc6844242, 0xb8d06868, 0xc3824141, 0xb0299999, 0x775a2d2d, 0x111e0f0f, 0xcb7bb0b0, 0xfca85454, 0xd66dbbbb, 0x3a2c1616 ]
        T3 = [ 0x63a5c663, 0x7c84f87c, 0x7799ee77, 0x7b8df67b, 0xf20dfff2, 0x6bbdd66b, 0x6fb1de6f, 0xc55491c5, 0x30506030, 0x01030201, 0x67a9ce67, 0x2b7d562b, 0xfe19e7fe, 0xd762b5d7, 0xabe64dab, 0x769aec76, 0xca458fca, 0x829d1f82, 0xc94089c9, 0x7d87fa7d, 0xfa15effa, 0x59ebb259, 0x47c98e47, 0xf00bfbf0, 0xadec41ad, 0xd467b3d4, 0xa2fd5fa2, 0xafea45af, 0x9cbf239c, 0xa4f753a4, 0x7296e472, 0xc05b9bc0, 0xb7c275b7, 0xfd1ce1fd, 0x93ae3d93, 0x266a4c26, 0x365a6c36, 0x3f417e3f, 0xf702f5f7, 0xcc4f83cc, 0x345c6834, 0xa5f451a5, 0xe534d1e5, 0xf108f9f1, 0x7193e271, 0xd873abd8, 0x31536231, 0x153f2a15, 0x040c0804, 0xc75295c7, 0x23654623, 0xc35e9dc3, 0x18283018, 0x96a13796, 0x050f0a05, 0x9ab52f9a, 0x07090e07, 0x12362412, 0x809b1b80, 0xe23ddfe2, 0xeb26cdeb, 0x27694e27, 0xb2cd7fb2, 0x759fea75, 0x091b1209, 0x839e1d83, 0x2c74582c, 0x1a2e341a, 0x1b2d361b, 0x6eb2dc6e, 0x5aeeb45a, 0xa0fb5ba0, 0x52f6a452, 0x3b4d763b, 0xd661b7d6, 0xb3ce7db3, 0x297b5229, 0xe33edde3, 0x2f715e2f, 0x84971384, 0x53f5a653, 0xd168b9d1, 0x00000000, 0xed2cc1ed, 0x20604020, 0xfc1fe3fc, 0xb1c879b1, 0x5bedb65b, 0x6abed46a, 0xcb468dcb, 0xbed967be, 0x394b7239, 0x4ade944a, 0x4cd4984c, 0x58e8b058, 0xcf4a85cf, 0xd06bbbd0, 0xef2ac5ef, 0xaae54faa, 0xfb16edfb, 0x43c58643, 0x4dd79a4d, 0x33556633, 0x85941185, 0x45cf8a45, 0xf910e9f9, 0x02060402, 0x7f81fe7f, 0x50f0a050, 0x3c44783c, 0x9fba259f, 0xa8e34ba8, 0x51f3a251, 0xa3fe5da3, 0x40c08040, 0x8f8a058f, 0x92ad3f92, 0x9dbc219d, 0x38487038, 0xf504f1f5, 0xbcdf63bc, 0xb6c177b6, 0xda75afda, 0x21634221, 0x10302010, 0xff1ae5ff, 0xf30efdf3, 0xd26dbfd2, 0xcd4c81cd, 0x0c14180c, 0x13352613, 0xec2fc3ec, 0x5fe1be5f, 0x97a23597, 0x44cc8844, 0x17392e17, 0xc45793c4, 0xa7f255a7, 0x7e82fc7e, 0x3d477a3d, 0x64acc864, 0x5de7ba5d, 0x192b3219, 0x7395e673, 0x60a0c060, 0x81981981, 0x4fd19e4f, 0xdc7fa3dc, 0x22664422, 0x2a7e542a, 0x90ab3b90, 0x88830b88, 0x46ca8c46, 0xee29c7ee, 0xb8d36bb8, 0x143c2814, 0xde79a7de, 0x5ee2bc5e, 0x0b1d160b, 0xdb76addb, 0xe03bdbe0, 0x32566432, 0x3a4e743a, 0x0a1e140a, 0x49db9249, 0x060a0c06, 0x246c4824, 0x5ce4b85c, 0xc25d9fc2, 0xd36ebdd3, 0xacef43ac, 0x62a6c462, 0x91a83991, 0x95a43195, 0xe437d3e4, 0x798bf279, 0xe732d5e7, 0xc8438bc8, 0x37596e37, 0x6db7da6d, 0x8d8c018d, 0xd564b1d5, 0x4ed29c4e, 0xa9e049a9, 0x6cb4d86c, 0x56faac56, 0xf407f3f4, 0xea25cfea, 0x65afca65, 0x7a8ef47a, 0xaee947ae, 0x08181008, 0xbad56fba, 0x7888f078, 0x256f4a25, 0x2e725c2e, 0x1c24381c, 0xa6f157a6, 0xb4c773b4, 0xc65197c6, 0xe823cbe8, 0xdd7ca1dd, 0x749ce874, 0x1f213e1f, 0x4bdd964b, 0xbddc61bd, 0x8b860d8b, 0x8a850f8a, 0x7090e070, 0x3e427c3e, 0xb5c471b5, 0x66aacc66, 0x48d89048, 0x03050603, 0xf601f7f6, 0x0e121c0e, 0x61a3c261, 0x355f6a35, 0x57f9ae57, 0xb9d069b9, 0x86911786, 0xc15899c1, 0x1d273a1d, 0x9eb9279e, 0xe138d9e1, 0xf813ebf8, 0x98b32b98, 0x11332211, 0x69bbd269, 0xd970a9d9, 0x8e89078e, 0x94a73394, 0x9bb62d9b, 0x1e223c1e, 0x87921587, 0xe920c9e9, 0xce4987ce, 0x55ffaa55, 0x28785028, 0xdf7aa5df, 0x8c8f038c, 0xa1f859a1, 0x89800989, 0x0d171a0d, 0xbfda65bf, 0xe631d7e6, 0x42c68442, 0x68b8d068, 0x41c38241, 0x99b02999, 0x2d775a2d, 0x0f111e0f, 0xb0cb7bb0, 0x54fca854, 0xbbd66dbb, 0x163a2c16 ]
        T4 = [ 0x6363a5c6, 0x7c7c84f8, 0x777799ee, 0x7b7b8df6, 0xf2f20dff, 0x6b6bbdd6, 0x6f6fb1de, 0xc5c55491, 0x30305060, 0x01010302, 0x6767a9ce, 0x2b2b7d56, 0xfefe19e7, 0xd7d762b5, 0xababe64d, 0x76769aec, 0xcaca458f, 0x82829d1f, 0xc9c94089, 0x7d7d87fa, 0xfafa15ef, 0x5959ebb2, 0x4747c98e, 0xf0f00bfb, 0xadadec41, 0xd4d467b3, 0xa2a2fd5f, 0xafafea45, 0x9c9cbf23, 0xa4a4f753, 0x727296e4, 0xc0c05b9b, 0xb7b7c275, 0xfdfd1ce1, 0x9393ae3d, 0x26266a4c, 0x36365a6c, 0x3f3f417e, 0xf7f702f5, 0xcccc4f83, 0x34345c68, 0xa5a5f451, 0xe5e534d1, 0xf1f108f9, 0x717193e2, 0xd8d873ab, 0x31315362, 0x15153f2a, 0x04040c08, 0xc7c75295, 0x23236546, 0xc3c35e9d, 0x18182830, 0x9696a137, 0x05050f0a, 0x9a9ab52f, 0x0707090e, 0x12123624, 0x80809b1b, 0xe2e23ddf, 0xebeb26cd, 0x2727694e, 0xb2b2cd7f, 0x75759fea, 0x09091b12, 0x83839e1d, 0x2c2c7458, 0x1a1a2e34, 0x1b1b2d36, 0x6e6eb2dc, 0x5a5aeeb4, 0xa0a0fb5b, 0x5252f6a4, 0x3b3b4d76, 0xd6d661b7, 0xb3b3ce7d, 0x29297b52, 0xe3e33edd, 0x2f2f715e, 0x84849713, 0x5353f5a6, 0xd1d168b9, 0x00000000, 0xeded2cc1, 0x20206040, 0xfcfc1fe3, 0xb1b1c879, 0x5b5bedb6, 0x6a6abed4, 0xcbcb468d, 0xbebed967, 0x39394b72, 0x4a4ade94, 0x4c4cd498, 0x5858e8b0, 0xcfcf4a85, 0xd0d06bbb, 0xefef2ac5, 0xaaaae54f, 0xfbfb16ed, 0x4343c586, 0x4d4dd79a, 0x33335566, 0x85859411, 0x4545cf8a, 0xf9f910e9, 0x02020604, 0x7f7f81fe, 0x5050f0a0, 0x3c3c4478, 0x9f9fba25, 0xa8a8e34b, 0x5151f3a2, 0xa3a3fe5d, 0x4040c080, 0x8f8f8a05, 0x9292ad3f, 0x9d9dbc21, 0x38384870, 0xf5f504f1, 0xbcbcdf63, 0xb6b6c177, 0xdada75af, 0x21216342, 0x10103020, 0xffff1ae5, 0xf3f30efd, 0xd2d26dbf, 0xcdcd4c81, 0x0c0c1418, 0x13133526, 0xecec2fc3, 0x5f5fe1be, 0x9797a235, 0x4444cc88, 0x1717392e, 0xc4c45793, 0xa7a7f255, 0x7e7e82fc, 0x3d3d477a, 0x6464acc8, 0x5d5de7ba, 0x19192b32, 0x737395e6, 0x6060a0c0, 0x81819819, 0x4f4fd19e, 0xdcdc7fa3, 0x22226644, 0x2a2a7e54, 0x9090ab3b, 0x8888830b, 0x4646ca8c, 0xeeee29c7, 0xb8b8d36b, 0x14143c28, 0xdede79a7, 0x5e5ee2bc, 0x0b0b1d16, 0xdbdb76ad, 0xe0e03bdb, 0x32325664, 0x3a3a4e74, 0x0a0a1e14, 0x4949db92, 0x06060a0c, 0x24246c48, 0x5c5ce4b8, 0xc2c25d9f, 0xd3d36ebd, 0xacacef43, 0x6262a6c4, 0x9191a839, 0x9595a431, 0xe4e437d3, 0x79798bf2, 0xe7e732d5, 0xc8c8438b, 0x3737596e, 0x6d6db7da, 0x8d8d8c01, 0xd5d564b1, 0x4e4ed29c, 0xa9a9e049, 0x6c6cb4d8, 0x5656faac, 0xf4f407f3, 0xeaea25cf, 0x6565afca, 0x7a7a8ef4, 0xaeaee947, 0x08081810, 0xbabad56f, 0x787888f0, 0x25256f4a, 0x2e2e725c, 0x1c1c2438, 0xa6a6f157, 0xb4b4c773, 0xc6c65197, 0xe8e823cb, 0xdddd7ca1, 0x74749ce8, 0x1f1f213e, 0x4b4bdd96, 0xbdbddc61, 0x8b8b860d, 0x8a8a850f, 0x707090e0, 0x3e3e427c, 0xb5b5c471, 0x6666aacc, 0x4848d890, 0x03030506, 0xf6f601f7, 0x0e0e121c, 0x6161a3c2, 0x35355f6a, 0x5757f9ae, 0xb9b9d069, 0x86869117, 0xc1c15899, 0x1d1d273a, 0x9e9eb927, 0xe1e138d9, 0xf8f813eb, 0x9898b32b, 0x11113322, 0x6969bbd2, 0xd9d970a9, 0x8e8e8907, 0x9494a733, 0x9b9bb62d, 0x1e1e223c, 0x87879215, 0xe9e920c9, 0xcece4987, 0x5555ffaa, 0x28287850, 0xdfdf7aa5, 0x8c8c8f03, 0xa1a1f859, 0x89898009, 0x0d0d171a, 0xbfbfda65, 0xe6e631d7, 0x4242c684, 0x6868b8d0, 0x4141c382, 0x9999b029, 0x2d2d775a, 0x0f0f111e, 0xb0b0cb7b, 0x5454fca8, 0xbbbbd66d, 0x16163a2c ]
        T5 = [ 0x51f4a750, 0x7e416553, 0x1a17a4c3, 0x3a275e96, 0x3bab6bcb, 0x1f9d45f1, 0xacfa58ab, 0x4be30393, 0x2030fa55, 0xad766df6, 0x88cc7691, 0xf5024c25, 0x4fe5d7fc, 0xc52acbd7, 0x26354480, 0xb562a38f, 0xdeb15a49, 0x25ba1b67, 0x45ea0e98, 0x5dfec0e1, 0xc32f7502, 0x814cf012, 0x8d4697a3, 0x6bd3f9c6, 0x038f5fe7, 0x15929c95, 0xbf6d7aeb, 0x955259da, 0xd4be832d, 0x587421d3, 0x49e06929, 0x8ec9c844, 0x75c2896a, 0xf48e7978, 0x99583e6b, 0x27b971dd, 0xbee14fb6, 0xf088ad17, 0xc920ac66, 0x7dce3ab4, 0x63df4a18, 0xe51a3182, 0x97513360, 0x62537f45, 0xb16477e0, 0xbb6bae84, 0xfe81a01c, 0xf9082b94, 0x70486858, 0x8f45fd19, 0x94de6c87, 0x527bf8b7, 0xab73d323, 0x724b02e2, 0xe31f8f57, 0x6655ab2a, 0xb2eb2807, 0x2fb5c203, 0x86c57b9a, 0xd33708a5, 0x302887f2, 0x23bfa5b2, 0x02036aba, 0xed16825c, 0x8acf1c2b, 0xa779b492, 0xf307f2f0, 0x4e69e2a1, 0x65daf4cd, 0x0605bed5, 0xd134621f, 0xc4a6fe8a, 0x342e539d, 0xa2f355a0, 0x058ae132, 0xa4f6eb75, 0x0b83ec39, 0x4060efaa, 0x5e719f06, 0xbd6e1051, 0x3e218af9, 0x96dd063d, 0xdd3e05ae, 0x4de6bd46, 0x91548db5, 0x71c45d05, 0x0406d46f, 0x605015ff, 0x1998fb24, 0xd6bde997, 0x894043cc, 0x67d99e77, 0xb0e842bd, 0x07898b88, 0xe7195b38, 0x79c8eedb, 0xa17c0a47, 0x7c420fe9, 0xf8841ec9, 0x00000000, 0x09808683, 0x322bed48, 0x1e1170ac, 0x6c5a724e, 0xfd0efffb, 0x0f853856, 0x3daed51e, 0x362d3927, 0x0a0fd964, 0x685ca621, 0x9b5b54d1, 0x24362e3a, 0x0c0a67b1, 0x9357e70f, 0xb4ee96d2, 0x1b9b919e, 0x80c0c54f, 0x61dc20a2, 0x5a774b69, 0x1c121a16, 0xe293ba0a, 0xc0a02ae5, 0x3c22e043, 0x121b171d, 0x0e090d0b, 0xf28bc7ad, 0x2db6a8b9, 0x141ea9c8, 0x57f11985, 0xaf75074c, 0xee99ddbb, 0xa37f60fd, 0xf701269f, 0x5c72f5bc, 0x44663bc5, 0x5bfb7e34, 0x8b432976, 0xcb23c6dc, 0xb6edfc68, 0xb8e4f163, 0xd731dcca, 0x42638510, 0x13972240, 0x84c61120, 0x854a247d, 0xd2bb3df8, 0xaef93211, 0xc729a16d, 0x1d9e2f4b, 0xdcb230f3, 0x0d8652ec, 0x77c1e3d0, 0x2bb3166c, 0xa970b999, 0x119448fa, 0x47e96422, 0xa8fc8cc4, 0xa0f03f1a, 0x567d2cd8, 0x223390ef, 0x87494ec7, 0xd938d1c1, 0x8ccaa2fe, 0x98d40b36, 0xa6f581cf, 0xa57ade28, 0xdab78e26, 0x3fadbfa4, 0x2c3a9de4, 0x5078920d, 0x6a5fcc9b, 0x547e4662, 0xf68d13c2, 0x90d8b8e8, 0x2e39f75e, 0x82c3aff5, 0x9f5d80be, 0x69d0937c, 0x6fd52da9, 0xcf2512b3, 0xc8ac993b, 0x10187da7, 0xe89c636e, 0xdb3bbb7b, 0xcd267809, 0x6e5918f4, 0xec9ab701, 0x834f9aa8, 0xe6956e65, 0xaaffe67e, 0x21bccf08, 0xef15e8e6, 0xbae79bd9, 0x4a6f36ce, 0xea9f09d4, 0x29b07cd6, 0x31a4b2af, 0x2a3f2331, 0xc6a59430, 0x35a266c0, 0x744ebc37, 0xfc82caa6, 0xe090d0b0, 0x33a7d815, 0xf104984a, 0x41ecdaf7, 0x7fcd500e, 0x1791f62f, 0x764dd68d, 0x43efb04d, 0xccaa4d54, 0xe49604df, 0x9ed1b5e3, 0x4c6a881b, 0xc12c1fb8, 0x4665517f, 0x9d5eea04, 0x018c355d, 0xfa877473, 0xfb0b412e, 0xb3671d5a, 0x92dbd252, 0xe9105633, 0x6dd64713, 0x9ad7618c, 0x37a10c7a, 0x59f8148e, 0xeb133c89, 0xcea927ee, 0xb761c935, 0xe11ce5ed, 0x7a47b13c, 0x9cd2df59, 0x55f2733f, 0x1814ce79, 0x73c737bf, 0x53f7cdea, 0x5ffdaa5b, 0xdf3d6f14, 0x7844db86, 0xcaaff381, 0xb968c43e, 0x3824342c, 0xc2a3405f, 0x161dc372, 0xbce2250c, 0x283c498b, 0xff0d9541, 0x39a80171, 0x080cb3de, 0xd8b4e49c, 0x6456c190, 0x7bcb8461, 0xd532b670, 0x486c5c74, 0xd0b85742 ]
        T6 = [ 0x5051f4a7, 0x537e4165, 0xc31a17a4, 0x963a275e, 0xcb3bab6b, 0xf11f9d45, 0xabacfa58, 0x934be303, 0x552030fa, 0xf6ad766d, 0x9188cc76, 0x25f5024c, 0xfc4fe5d7, 0xd7c52acb, 0x80263544, 0x8fb562a3, 0x49deb15a, 0x6725ba1b, 0x9845ea0e, 0xe15dfec0, 0x02c32f75, 0x12814cf0, 0xa38d4697, 0xc66bd3f9, 0xe7038f5f, 0x9515929c, 0xebbf6d7a, 0xda955259, 0x2dd4be83, 0xd3587421, 0x2949e069, 0x448ec9c8, 0x6a75c289, 0x78f48e79, 0x6b99583e, 0xdd27b971, 0xb6bee14f, 0x17f088ad, 0x66c920ac, 0xb47dce3a, 0x1863df4a, 0x82e51a31, 0x60975133, 0x4562537f, 0xe0b16477, 0x84bb6bae, 0x1cfe81a0, 0x94f9082b, 0x58704868, 0x198f45fd, 0x8794de6c, 0xb7527bf8, 0x23ab73d3, 0xe2724b02, 0x57e31f8f, 0x2a6655ab, 0x07b2eb28, 0x032fb5c2, 0x9a86c57b, 0xa5d33708, 0xf2302887, 0xb223bfa5, 0xba02036a, 0x5ced1682, 0x2b8acf1c, 0x92a779b4, 0xf0f307f2, 0xa14e69e2, 0xcd65daf4, 0xd50605be, 0x1fd13462, 0x8ac4a6fe, 0x9d342e53, 0xa0a2f355, 0x32058ae1, 0x75a4f6eb, 0x390b83ec, 0xaa4060ef, 0x065e719f, 0x51bd6e10, 0xf93e218a, 0x3d96dd06, 0xaedd3e05, 0x464de6bd, 0xb591548d, 0x0571c45d, 0x6f0406d4, 0xff605015, 0x241998fb, 0x97d6bde9, 0xcc894043, 0x7767d99e, 0xbdb0e842, 0x8807898b, 0x38e7195b, 0xdb79c8ee, 0x47a17c0a, 0xe97c420f, 0xc9f8841e, 0x00000000, 0x83098086, 0x48322bed, 0xac1e1170, 0x4e6c5a72, 0xfbfd0eff, 0x560f8538, 0x1e3daed5, 0x27362d39, 0x640a0fd9, 0x21685ca6, 0xd19b5b54, 0x3a24362e, 0xb10c0a67, 0x0f9357e7, 0xd2b4ee96, 0x9e1b9b91, 0x4f80c0c5, 0xa261dc20, 0x695a774b, 0x161c121a, 0x0ae293ba, 0xe5c0a02a, 0x433c22e0, 0x1d121b17, 0x0b0e090d, 0xadf28bc7, 0xb92db6a8, 0xc8141ea9, 0x8557f119, 0x4caf7507, 0xbbee99dd, 0xfda37f60, 0x9ff70126, 0xbc5c72f5, 0xc544663b, 0x345bfb7e, 0x768b4329, 0xdccb23c6, 0x68b6edfc, 0x63b8e4f1, 0xcad731dc, 0x10426385, 0x40139722, 0x2084c611, 0x7d854a24, 0xf8d2bb3d, 0x11aef932, 0x6dc729a1, 0x4b1d9e2f, 0xf3dcb230, 0xec0d8652, 0xd077c1e3, 0x6c2bb316, 0x99a970b9, 0xfa119448, 0x2247e964, 0xc4a8fc8c, 0x1aa0f03f, 0xd8567d2c, 0xef223390, 0xc787494e, 0xc1d938d1, 0xfe8ccaa2, 0x3698d40b, 0xcfa6f581, 0x28a57ade, 0x26dab78e, 0xa43fadbf, 0xe42c3a9d, 0x0d507892, 0x9b6a5fcc, 0x62547e46, 0xc2f68d13, 0xe890d8b8, 0x5e2e39f7, 0xf582c3af, 0xbe9f5d80, 0x7c69d093, 0xa96fd52d, 0xb3cf2512, 0x3bc8ac99, 0xa710187d, 0x6ee89c63, 0x7bdb3bbb, 0x09cd2678, 0xf46e5918, 0x01ec9ab7, 0xa8834f9a, 0x65e6956e, 0x7eaaffe6, 0x0821bccf, 0xe6ef15e8, 0xd9bae79b, 0xce4a6f36, 0xd4ea9f09, 0xd629b07c, 0xaf31a4b2, 0x312a3f23, 0x30c6a594, 0xc035a266, 0x37744ebc, 0xa6fc82ca, 0xb0e090d0, 0x1533a7d8, 0x4af10498, 0xf741ecda, 0x0e7fcd50, 0x2f1791f6, 0x8d764dd6, 0x4d43efb0, 0x54ccaa4d, 0xdfe49604, 0xe39ed1b5, 0x1b4c6a88, 0xb8c12c1f, 0x7f466551, 0x049d5eea, 0x5d018c35, 0x73fa8774, 0x2efb0b41, 0x5ab3671d, 0x5292dbd2, 0x33e91056, 0x136dd647, 0x8c9ad761, 0x7a37a10c, 0x8e59f814, 0x89eb133c, 0xeecea927, 0x35b761c9, 0xede11ce5, 0x3c7a47b1, 0x599cd2df, 0x3f55f273, 0x791814ce, 0xbf73c737, 0xea53f7cd, 0x5b5ffdaa, 0x14df3d6f, 0x867844db, 0x81caaff3, 0x3eb968c4, 0x2c382434, 0x5fc2a340, 0x72161dc3, 0x0cbce225, 0x8b283c49, 0x41ff0d95, 0x7139a801, 0xde080cb3, 0x9cd8b4e4, 0x906456c1, 0x617bcb84, 0x70d532b6, 0x74486c5c, 0x42d0b857 ]
        T7 = [ 0xa75051f4, 0x65537e41, 0xa4c31a17, 0x5e963a27, 0x6bcb3bab, 0x45f11f9d, 0x58abacfa, 0x03934be3, 0xfa552030, 0x6df6ad76, 0x769188cc, 0x4c25f502, 0xd7fc4fe5, 0xcbd7c52a, 0x44802635, 0xa38fb562, 0x5a49deb1, 0x1b6725ba, 0x0e9845ea, 0xc0e15dfe, 0x7502c32f, 0xf012814c, 0x97a38d46, 0xf9c66bd3, 0x5fe7038f, 0x9c951592, 0x7aebbf6d, 0x59da9552, 0x832dd4be, 0x21d35874, 0x692949e0, 0xc8448ec9, 0x896a75c2, 0x7978f48e, 0x3e6b9958, 0x71dd27b9, 0x4fb6bee1, 0xad17f088, 0xac66c920, 0x3ab47dce, 0x4a1863df, 0x3182e51a, 0x33609751, 0x7f456253, 0x77e0b164, 0xae84bb6b, 0xa01cfe81, 0x2b94f908, 0x68587048, 0xfd198f45, 0x6c8794de, 0xf8b7527b, 0xd323ab73, 0x02e2724b, 0x8f57e31f, 0xab2a6655, 0x2807b2eb, 0xc2032fb5, 0x7b9a86c5, 0x08a5d337, 0x87f23028, 0xa5b223bf, 0x6aba0203, 0x825ced16, 0x1c2b8acf, 0xb492a779, 0xf2f0f307, 0xe2a14e69, 0xf4cd65da, 0xbed50605, 0x621fd134, 0xfe8ac4a6, 0x539d342e, 0x55a0a2f3, 0xe132058a, 0xeb75a4f6, 0xec390b83, 0xefaa4060, 0x9f065e71, 0x1051bd6e, 0x8af93e21, 0x063d96dd, 0x05aedd3e, 0xbd464de6, 0x8db59154, 0x5d0571c4, 0xd46f0406, 0x15ff6050, 0xfb241998, 0xe997d6bd, 0x43cc8940, 0x9e7767d9, 0x42bdb0e8, 0x8b880789, 0x5b38e719, 0xeedb79c8, 0x0a47a17c, 0x0fe97c42, 0x1ec9f884, 0x00000000, 0x86830980, 0xed48322b, 0x70ac1e11, 0x724e6c5a, 0xfffbfd0e, 0x38560f85, 0xd51e3dae, 0x3927362d, 0xd9640a0f, 0xa621685c, 0x54d19b5b, 0x2e3a2436, 0x67b10c0a, 0xe70f9357, 0x96d2b4ee, 0x919e1b9b, 0xc54f80c0, 0x20a261dc, 0x4b695a77, 0x1a161c12, 0xba0ae293, 0x2ae5c0a0, 0xe0433c22, 0x171d121b, 0x0d0b0e09, 0xc7adf28b, 0xa8b92db6, 0xa9c8141e, 0x198557f1, 0x074caf75, 0xddbbee99, 0x60fda37f, 0x269ff701, 0xf5bc5c72, 0x3bc54466, 0x7e345bfb, 0x29768b43, 0xc6dccb23, 0xfc68b6ed, 0xf163b8e4, 0xdccad731, 0x85104263, 0x22401397, 0x112084c6, 0x247d854a, 0x3df8d2bb, 0x3211aef9, 0xa16dc729, 0x2f4b1d9e, 0x30f3dcb2, 0x52ec0d86, 0xe3d077c1, 0x166c2bb3, 0xb999a970, 0x48fa1194, 0x642247e9, 0x8cc4a8fc, 0x3f1aa0f0, 0x2cd8567d, 0x90ef2233, 0x4ec78749, 0xd1c1d938, 0xa2fe8cca, 0x0b3698d4, 0x81cfa6f5, 0xde28a57a, 0x8e26dab7, 0xbfa43fad, 0x9de42c3a, 0x920d5078, 0xcc9b6a5f, 0x4662547e, 0x13c2f68d, 0xb8e890d8, 0xf75e2e39, 0xaff582c3, 0x80be9f5d, 0x937c69d0, 0x2da96fd5, 0x12b3cf25, 0x993bc8ac, 0x7da71018, 0x636ee89c, 0xbb7bdb3b, 0x7809cd26, 0x18f46e59, 0xb701ec9a, 0x9aa8834f, 0x6e65e695, 0xe67eaaff, 0xcf0821bc, 0xe8e6ef15, 0x9bd9bae7, 0x36ce4a6f, 0x09d4ea9f, 0x7cd629b0, 0xb2af31a4, 0x23312a3f, 0x9430c6a5, 0x66c035a2, 0xbc37744e, 0xcaa6fc82, 0xd0b0e090, 0xd81533a7, 0x984af104, 0xdaf741ec, 0x500e7fcd, 0xf62f1791, 0xd68d764d, 0xb04d43ef, 0x4d54ccaa, 0x04dfe496, 0xb5e39ed1, 0x881b4c6a, 0x1fb8c12c, 0x517f4665, 0xea049d5e, 0x355d018c, 0x7473fa87, 0x412efb0b, 0x1d5ab367, 0xd25292db, 0x5633e910, 0x47136dd6, 0x618c9ad7, 0x0c7a37a1, 0x148e59f8, 0x3c89eb13, 0x27eecea9, 0xc935b761, 0xe5ede11c, 0xb13c7a47, 0xdf599cd2, 0x733f55f2, 0xce791814, 0x37bf73c7, 0xcdea53f7, 0xaa5b5ffd, 0x6f14df3d, 0xdb867844, 0xf381caaf, 0xc43eb968, 0x342c3824, 0x405fc2a3, 0xc372161d, 0x250cbce2, 0x498b283c, 0x9541ff0d, 0x017139a8, 0xb3de080c, 0xe49cd8b4, 0xc1906456, 0x84617bcb, 0xb670d532, 0x5c74486c, 0x5742d0b8 ]
        T8 = [ 0xf4a75051, 0x4165537e, 0x17a4c31a, 0x275e963a, 0xab6bcb3b, 0x9d45f11f, 0xfa58abac, 0xe303934b, 0x30fa5520, 0x766df6ad, 0xcc769188, 0x024c25f5, 0xe5d7fc4f, 0x2acbd7c5, 0x35448026, 0x62a38fb5, 0xb15a49de, 0xba1b6725, 0xea0e9845, 0xfec0e15d, 0x2f7502c3, 0x4cf01281, 0x4697a38d, 0xd3f9c66b, 0x8f5fe703, 0x929c9515, 0x6d7aebbf, 0x5259da95, 0xbe832dd4, 0x7421d358, 0xe0692949, 0xc9c8448e, 0xc2896a75, 0x8e7978f4, 0x583e6b99, 0xb971dd27, 0xe14fb6be, 0x88ad17f0, 0x20ac66c9, 0xce3ab47d, 0xdf4a1863, 0x1a3182e5, 0x51336097, 0x537f4562, 0x6477e0b1, 0x6bae84bb, 0x81a01cfe, 0x082b94f9, 0x48685870, 0x45fd198f, 0xde6c8794, 0x7bf8b752, 0x73d323ab, 0x4b02e272, 0x1f8f57e3, 0x55ab2a66, 0xeb2807b2, 0xb5c2032f, 0xc57b9a86, 0x3708a5d3, 0x2887f230, 0xbfa5b223, 0x036aba02, 0x16825ced, 0xcf1c2b8a, 0x79b492a7, 0x07f2f0f3, 0x69e2a14e, 0xdaf4cd65, 0x05bed506, 0x34621fd1, 0xa6fe8ac4, 0x2e539d34, 0xf355a0a2, 0x8ae13205, 0xf6eb75a4, 0x83ec390b, 0x60efaa40, 0x719f065e, 0x6e1051bd, 0x218af93e, 0xdd063d96, 0x3e05aedd, 0xe6bd464d, 0x548db591, 0xc45d0571, 0x06d46f04, 0x5015ff60, 0x98fb2419, 0xbde997d6, 0x4043cc89, 0xd99e7767, 0xe842bdb0, 0x898b8807, 0x195b38e7, 0xc8eedb79, 0x7c0a47a1, 0x420fe97c, 0x841ec9f8, 0x00000000, 0x80868309, 0x2bed4832, 0x1170ac1e, 0x5a724e6c, 0x0efffbfd, 0x8538560f, 0xaed51e3d, 0x2d392736, 0x0fd9640a, 0x5ca62168, 0x5b54d19b, 0x362e3a24, 0x0a67b10c, 0x57e70f93, 0xee96d2b4, 0x9b919e1b, 0xc0c54f80, 0xdc20a261, 0x774b695a, 0x121a161c, 0x93ba0ae2, 0xa02ae5c0, 0x22e0433c, 0x1b171d12, 0x090d0b0e, 0x8bc7adf2, 0xb6a8b92d, 0x1ea9c814, 0xf1198557, 0x75074caf, 0x99ddbbee, 0x7f60fda3, 0x01269ff7, 0x72f5bc5c, 0x663bc544, 0xfb7e345b, 0x4329768b, 0x23c6dccb, 0xedfc68b6, 0xe4f163b8, 0x31dccad7, 0x63851042, 0x97224013, 0xc6112084, 0x4a247d85, 0xbb3df8d2, 0xf93211ae, 0x29a16dc7, 0x9e2f4b1d, 0xb230f3dc, 0x8652ec0d, 0xc1e3d077, 0xb3166c2b, 0x70b999a9, 0x9448fa11, 0xe9642247, 0xfc8cc4a8, 0xf03f1aa0, 0x7d2cd856, 0x3390ef22, 0x494ec787, 0x38d1c1d9, 0xcaa2fe8c, 0xd40b3698, 0xf581cfa6, 0x7ade28a5, 0xb78e26da, 0xadbfa43f, 0x3a9de42c, 0x78920d50, 0x5fcc9b6a, 0x7e466254, 0x8d13c2f6, 0xd8b8e890, 0x39f75e2e, 0xc3aff582, 0x5d80be9f, 0xd0937c69, 0xd52da96f, 0x2512b3cf, 0xac993bc8, 0x187da710, 0x9c636ee8, 0x3bbb7bdb, 0x267809cd, 0x5918f46e, 0x9ab701ec, 0x4f9aa883, 0x956e65e6, 0xffe67eaa, 0xbccf0821, 0x15e8e6ef, 0xe79bd9ba, 0x6f36ce4a, 0x9f09d4ea, 0xb07cd629, 0xa4b2af31, 0x3f23312a, 0xa59430c6, 0xa266c035, 0x4ebc3774, 0x82caa6fc, 0x90d0b0e0, 0xa7d81533, 0x04984af1, 0xecdaf741, 0xcd500e7f, 0x91f62f17, 0x4dd68d76, 0xefb04d43, 0xaa4d54cc, 0x9604dfe4, 0xd1b5e39e, 0x6a881b4c, 0x2c1fb8c1, 0x65517f46, 0x5eea049d, 0x8c355d01, 0x877473fa, 0x0b412efb, 0x671d5ab3, 0xdbd25292, 0x105633e9, 0xd647136d, 0xd7618c9a, 0xa10c7a37, 0xf8148e59, 0x133c89eb, 0xa927eece, 0x61c935b7, 0x1ce5ede1, 0x47b13c7a, 0xd2df599c, 0xf2733f55, 0x14ce7918, 0xc737bf73, 0xf7cdea53, 0xfdaa5b5f, 0x3d6f14df, 0x44db8678, 0xaff381ca, 0x68c43eb9, 0x24342c38, 0xa3405fc2, 0x1dc37216, 0xe2250cbc, 0x3c498b28, 0x0d9541ff, 0xa8017139, 0x0cb3de08, 0xb4e49cd8, 0x56c19064, 0xcb84617b, 0x32b670d5, 0x6c5c7448, 0xb85742d0 ]
        U1 = [ 0x00000000, 0x0e090d0b, 0x1c121a16, 0x121b171d, 0x3824342c, 0x362d3927, 0x24362e3a, 0x2a3f2331, 0x70486858, 0x7e416553, 0x6c5a724e, 0x62537f45, 0x486c5c74, 0x4665517f, 0x547e4662, 0x5a774b69, 0xe090d0b0, 0xee99ddbb, 0xfc82caa6, 0xf28bc7ad, 0xd8b4e49c, 0xd6bde997, 0xc4a6fe8a, 0xcaaff381, 0x90d8b8e8, 0x9ed1b5e3, 0x8ccaa2fe, 0x82c3aff5, 0xa8fc8cc4, 0xa6f581cf, 0xb4ee96d2, 0xbae79bd9, 0xdb3bbb7b, 0xd532b670, 0xc729a16d, 0xc920ac66, 0xe31f8f57, 0xed16825c, 0xff0d9541, 0xf104984a, 0xab73d323, 0xa57ade28, 0xb761c935, 0xb968c43e, 0x9357e70f, 0x9d5eea04, 0x8f45fd19, 0x814cf012, 0x3bab6bcb, 0x35a266c0, 0x27b971dd, 0x29b07cd6, 0x038f5fe7, 0x0d8652ec, 0x1f9d45f1, 0x119448fa, 0x4be30393, 0x45ea0e98, 0x57f11985, 0x59f8148e, 0x73c737bf, 0x7dce3ab4, 0x6fd52da9, 0x61dc20a2, 0xad766df6, 0xa37f60fd, 0xb16477e0, 0xbf6d7aeb, 0x955259da, 0x9b5b54d1, 0x894043cc, 0x87494ec7, 0xdd3e05ae, 0xd33708a5, 0xc12c1fb8, 0xcf2512b3, 0xe51a3182, 0xeb133c89, 0xf9082b94, 0xf701269f, 0x4de6bd46, 0x43efb04d, 0x51f4a750, 0x5ffdaa5b, 0x75c2896a, 0x7bcb8461, 0x69d0937c, 0x67d99e77, 0x3daed51e, 0x33a7d815, 0x21bccf08, 0x2fb5c203, 0x058ae132, 0x0b83ec39, 0x1998fb24, 0x1791f62f, 0x764dd68d, 0x7844db86, 0x6a5fcc9b, 0x6456c190, 0x4e69e2a1, 0x4060efaa, 0x527bf8b7, 0x5c72f5bc, 0x0605bed5, 0x080cb3de, 0x1a17a4c3, 0x141ea9c8, 0x3e218af9, 0x302887f2, 0x223390ef, 0x2c3a9de4, 0x96dd063d, 0x98d40b36, 0x8acf1c2b, 0x84c61120, 0xaef93211, 0xa0f03f1a, 0xb2eb2807, 0xbce2250c, 0xe6956e65, 0xe89c636e, 0xfa877473, 0xf48e7978, 0xdeb15a49, 0xd0b85742, 0xc2a3405f, 0xccaa4d54, 0x41ecdaf7, 0x4fe5d7fc, 0x5dfec0e1, 0x53f7cdea, 0x79c8eedb, 0x77c1e3d0, 0x65daf4cd, 0x6bd3f9c6, 0x31a4b2af, 0x3fadbfa4, 0x2db6a8b9, 0x23bfa5b2, 0x09808683, 0x07898b88, 0x15929c95, 0x1b9b919e, 0xa17c0a47, 0xaf75074c, 0xbd6e1051, 0xb3671d5a, 0x99583e6b, 0x97513360, 0x854a247d, 0x8b432976, 0xd134621f, 0xdf3d6f14, 0xcd267809, 0xc32f7502, 0xe9105633, 0xe7195b38, 0xf5024c25, 0xfb0b412e, 0x9ad7618c, 0x94de6c87, 0x86c57b9a, 0x88cc7691, 0xa2f355a0, 0xacfa58ab, 0xbee14fb6, 0xb0e842bd, 0xea9f09d4, 0xe49604df, 0xf68d13c2, 0xf8841ec9, 0xd2bb3df8, 0xdcb230f3, 0xcea927ee, 0xc0a02ae5, 0x7a47b13c, 0x744ebc37, 0x6655ab2a, 0x685ca621, 0x42638510, 0x4c6a881b, 0x5e719f06, 0x5078920d, 0x0a0fd964, 0x0406d46f, 0x161dc372, 0x1814ce79, 0x322bed48, 0x3c22e043, 0x2e39f75e, 0x2030fa55, 0xec9ab701, 0xe293ba0a, 0xf088ad17, 0xfe81a01c, 0xd4be832d, 0xdab78e26, 0xc8ac993b, 0xc6a59430, 0x9cd2df59, 0x92dbd252, 0x80c0c54f, 0x8ec9c844, 0xa4f6eb75, 0xaaffe67e, 0xb8e4f163, 0xb6edfc68, 0x0c0a67b1, 0x02036aba, 0x10187da7, 0x1e1170ac, 0x342e539d, 0x3a275e96, 0x283c498b, 0x26354480, 0x7c420fe9, 0x724b02e2, 0x605015ff, 0x6e5918f4, 0x44663bc5, 0x4a6f36ce, 0x587421d3, 0x567d2cd8, 0x37a10c7a, 0x39a80171, 0x2bb3166c, 0x25ba1b67, 0x0f853856, 0x018c355d, 0x13972240, 0x1d9e2f4b, 0x47e96422, 0x49e06929, 0x5bfb7e34, 0x55f2733f, 0x7fcd500e, 0x71c45d05, 0x63df4a18, 0x6dd64713, 0xd731dcca, 0xd938d1c1, 0xcb23c6dc, 0xc52acbd7, 0xef15e8e6, 0xe11ce5ed, 0xf307f2f0, 0xfd0efffb, 0xa779b492, 0xa970b999, 0xbb6bae84, 0xb562a38f, 0x9f5d80be, 0x91548db5, 0x834f9aa8, 0x8d4697a3 ]
        U2 = [ 0x00000000, 0x0b0e090d, 0x161c121a, 0x1d121b17, 0x2c382434, 0x27362d39, 0x3a24362e, 0x312a3f23, 0x58704868, 0x537e4165, 0x4e6c5a72, 0x4562537f, 0x74486c5c, 0x7f466551, 0x62547e46, 0x695a774b, 0xb0e090d0, 0xbbee99dd, 0xa6fc82ca, 0xadf28bc7, 0x9cd8b4e4, 0x97d6bde9, 0x8ac4a6fe, 0x81caaff3, 0xe890d8b8, 0xe39ed1b5, 0xfe8ccaa2, 0xf582c3af, 0xc4a8fc8c, 0xcfa6f581, 0xd2b4ee96, 0xd9bae79b, 0x7bdb3bbb, 0x70d532b6, 0x6dc729a1, 0x66c920ac, 0x57e31f8f, 0x5ced1682, 0x41ff0d95, 0x4af10498, 0x23ab73d3, 0x28a57ade, 0x35b761c9, 0x3eb968c4, 0x0f9357e7, 0x049d5eea, 0x198f45fd, 0x12814cf0, 0xcb3bab6b, 0xc035a266, 0xdd27b971, 0xd629b07c, 0xe7038f5f, 0xec0d8652, 0xf11f9d45, 0xfa119448, 0x934be303, 0x9845ea0e, 0x8557f119, 0x8e59f814, 0xbf73c737, 0xb47dce3a, 0xa96fd52d, 0xa261dc20, 0xf6ad766d, 0xfda37f60, 0xe0b16477, 0xebbf6d7a, 0xda955259, 0xd19b5b54, 0xcc894043, 0xc787494e, 0xaedd3e05, 0xa5d33708, 0xb8c12c1f, 0xb3cf2512, 0x82e51a31, 0x89eb133c, 0x94f9082b, 0x9ff70126, 0x464de6bd, 0x4d43efb0, 0x5051f4a7, 0x5b5ffdaa, 0x6a75c289, 0x617bcb84, 0x7c69d093, 0x7767d99e, 0x1e3daed5, 0x1533a7d8, 0x0821bccf, 0x032fb5c2, 0x32058ae1, 0x390b83ec, 0x241998fb, 0x2f1791f6, 0x8d764dd6, 0x867844db, 0x9b6a5fcc, 0x906456c1, 0xa14e69e2, 0xaa4060ef, 0xb7527bf8, 0xbc5c72f5, 0xd50605be, 0xde080cb3, 0xc31a17a4, 0xc8141ea9, 0xf93e218a, 0xf2302887, 0xef223390, 0xe42c3a9d, 0x3d96dd06, 0x3698d40b, 0x2b8acf1c, 0x2084c611, 0x11aef932, 0x1aa0f03f, 0x07b2eb28, 0x0cbce225, 0x65e6956e, 0x6ee89c63, 0x73fa8774, 0x78f48e79, 0x49deb15a, 0x42d0b857, 0x5fc2a340, 0x54ccaa4d, 0xf741ecda, 0xfc4fe5d7, 0xe15dfec0, 0xea53f7cd, 0xdb79c8ee, 0xd077c1e3, 0xcd65daf4, 0xc66bd3f9, 0xaf31a4b2, 0xa43fadbf, 0xb92db6a8, 0xb223bfa5, 0x83098086, 0x8807898b, 0x9515929c, 0x9e1b9b91, 0x47a17c0a, 0x4caf7507, 0x51bd6e10, 0x5ab3671d, 0x6b99583e, 0x60975133, 0x7d854a24, 0x768b4329, 0x1fd13462, 0x14df3d6f, 0x09cd2678, 0x02c32f75, 0x33e91056, 0x38e7195b, 0x25f5024c, 0x2efb0b41, 0x8c9ad761, 0x8794de6c, 0x9a86c57b, 0x9188cc76, 0xa0a2f355, 0xabacfa58, 0xb6bee14f, 0xbdb0e842, 0xd4ea9f09, 0xdfe49604, 0xc2f68d13, 0xc9f8841e, 0xf8d2bb3d, 0xf3dcb230, 0xeecea927, 0xe5c0a02a, 0x3c7a47b1, 0x37744ebc, 0x2a6655ab, 0x21685ca6, 0x10426385, 0x1b4c6a88, 0x065e719f, 0x0d507892, 0x640a0fd9, 0x6f0406d4, 0x72161dc3, 0x791814ce, 0x48322bed, 0x433c22e0, 0x5e2e39f7, 0x552030fa, 0x01ec9ab7, 0x0ae293ba, 0x17f088ad, 0x1cfe81a0, 0x2dd4be83, 0x26dab78e, 0x3bc8ac99, 0x30c6a594, 0x599cd2df, 0x5292dbd2, 0x4f80c0c5, 0x448ec9c8, 0x75a4f6eb, 0x7eaaffe6, 0x63b8e4f1, 0x68b6edfc, 0xb10c0a67, 0xba02036a, 0xa710187d, 0xac1e1170, 0x9d342e53, 0x963a275e, 0x8b283c49, 0x80263544, 0xe97c420f, 0xe2724b02, 0xff605015, 0xf46e5918, 0xc544663b, 0xce4a6f36, 0xd3587421, 0xd8567d2c, 0x7a37a10c, 0x7139a801, 0x6c2bb316, 0x6725ba1b, 0x560f8538, 0x5d018c35, 0x40139722, 0x4b1d9e2f, 0x2247e964, 0x2949e069, 0x345bfb7e, 0x3f55f273, 0x0e7fcd50, 0x0571c45d, 0x1863df4a, 0x136dd647, 0xcad731dc, 0xc1d938d1, 0xdccb23c6, 0xd7c52acb, 0xe6ef15e8, 0xede11ce5, 0xf0f307f2, 0xfbfd0eff, 0x92a779b4, 0x99a970b9, 0x84bb6bae, 0x8fb562a3, 0xbe9f5d80, 0xb591548d, 0xa8834f9a, 0xa38d4697 ]
        U3 = [ 0x00000000, 0x0d0b0e09, 0x1a161c12, 0x171d121b, 0x342c3824, 0x3927362d, 0x2e3a2436, 0x23312a3f, 0x68587048, 0x65537e41, 0x724e6c5a, 0x7f456253, 0x5c74486c, 0x517f4665, 0x4662547e, 0x4b695a77, 0xd0b0e090, 0xddbbee99, 0xcaa6fc82, 0xc7adf28b, 0xe49cd8b4, 0xe997d6bd, 0xfe8ac4a6, 0xf381caaf, 0xb8e890d8, 0xb5e39ed1, 0xa2fe8cca, 0xaff582c3, 0x8cc4a8fc, 0x81cfa6f5, 0x96d2b4ee, 0x9bd9bae7, 0xbb7bdb3b, 0xb670d532, 0xa16dc729, 0xac66c920, 0x8f57e31f, 0x825ced16, 0x9541ff0d, 0x984af104, 0xd323ab73, 0xde28a57a, 0xc935b761, 0xc43eb968, 0xe70f9357, 0xea049d5e, 0xfd198f45, 0xf012814c, 0x6bcb3bab, 0x66c035a2, 0x71dd27b9, 0x7cd629b0, 0x5fe7038f, 0x52ec0d86, 0x45f11f9d, 0x48fa1194, 0x03934be3, 0x0e9845ea, 0x198557f1, 0x148e59f8, 0x37bf73c7, 0x3ab47dce, 0x2da96fd5, 0x20a261dc, 0x6df6ad76, 0x60fda37f, 0x77e0b164, 0x7aebbf6d, 0x59da9552, 0x54d19b5b, 0x43cc8940, 0x4ec78749, 0x05aedd3e, 0x08a5d337, 0x1fb8c12c, 0x12b3cf25, 0x3182e51a, 0x3c89eb13, 0x2b94f908, 0x269ff701, 0xbd464de6, 0xb04d43ef, 0xa75051f4, 0xaa5b5ffd, 0x896a75c2, 0x84617bcb, 0x937c69d0, 0x9e7767d9, 0xd51e3dae, 0xd81533a7, 0xcf0821bc, 0xc2032fb5, 0xe132058a, 0xec390b83, 0xfb241998, 0xf62f1791, 0xd68d764d, 0xdb867844, 0xcc9b6a5f, 0xc1906456, 0xe2a14e69, 0xefaa4060, 0xf8b7527b, 0xf5bc5c72, 0xbed50605, 0xb3de080c, 0xa4c31a17, 0xa9c8141e, 0x8af93e21, 0x87f23028, 0x90ef2233, 0x9de42c3a, 0x063d96dd, 0x0b3698d4, 0x1c2b8acf, 0x112084c6, 0x3211aef9, 0x3f1aa0f0, 0x2807b2eb, 0x250cbce2, 0x6e65e695, 0x636ee89c, 0x7473fa87, 0x7978f48e, 0x5a49deb1, 0x5742d0b8, 0x405fc2a3, 0x4d54ccaa, 0xdaf741ec, 0xd7fc4fe5, 0xc0e15dfe, 0xcdea53f7, 0xeedb79c8, 0xe3d077c1, 0xf4cd65da, 0xf9c66bd3, 0xb2af31a4, 0xbfa43fad, 0xa8b92db6, 0xa5b223bf, 0x86830980, 0x8b880789, 0x9c951592, 0x919e1b9b, 0x0a47a17c, 0x074caf75, 0x1051bd6e, 0x1d5ab367, 0x3e6b9958, 0x33609751, 0x247d854a, 0x29768b43, 0x621fd134, 0x6f14df3d, 0x7809cd26, 0x7502c32f, 0x5633e910, 0x5b38e719, 0x4c25f502, 0x412efb0b, 0x618c9ad7, 0x6c8794de, 0x7b9a86c5, 0x769188cc, 0x55a0a2f3, 0x58abacfa, 0x4fb6bee1, 0x42bdb0e8, 0x09d4ea9f, 0x04dfe496, 0x13c2f68d, 0x1ec9f884, 0x3df8d2bb, 0x30f3dcb2, 0x27eecea9, 0x2ae5c0a0, 0xb13c7a47, 0xbc37744e, 0xab2a6655, 0xa621685c, 0x85104263, 0x881b4c6a, 0x9f065e71, 0x920d5078, 0xd9640a0f, 0xd46f0406, 0xc372161d, 0xce791814, 0xed48322b, 0xe0433c22, 0xf75e2e39, 0xfa552030, 0xb701ec9a, 0xba0ae293, 0xad17f088, 0xa01cfe81, 0x832dd4be, 0x8e26dab7, 0x993bc8ac, 0x9430c6a5, 0xdf599cd2, 0xd25292db, 0xc54f80c0, 0xc8448ec9, 0xeb75a4f6, 0xe67eaaff, 0xf163b8e4, 0xfc68b6ed, 0x67b10c0a, 0x6aba0203, 0x7da71018, 0x70ac1e11, 0x539d342e, 0x5e963a27, 0x498b283c, 0x44802635, 0x0fe97c42, 0x02e2724b, 0x15ff6050, 0x18f46e59, 0x3bc54466, 0x36ce4a6f, 0x21d35874, 0x2cd8567d, 0x0c7a37a1, 0x017139a8, 0x166c2bb3, 0x1b6725ba, 0x38560f85, 0x355d018c, 0x22401397, 0x2f4b1d9e, 0x642247e9, 0x692949e0, 0x7e345bfb, 0x733f55f2, 0x500e7fcd, 0x5d0571c4, 0x4a1863df, 0x47136dd6, 0xdccad731, 0xd1c1d938, 0xc6dccb23, 0xcbd7c52a, 0xe8e6ef15, 0xe5ede11c, 0xf2f0f307, 0xfffbfd0e, 0xb492a779, 0xb999a970, 0xae84bb6b, 0xa38fb562, 0x80be9f5d, 0x8db59154, 0x9aa8834f, 0x97a38d46 ]
        U4 = [ 0x00000000, 0x090d0b0e, 0x121a161c, 0x1b171d12, 0x24342c38, 0x2d392736, 0x362e3a24, 0x3f23312a, 0x48685870, 0x4165537e, 0x5a724e6c, 0x537f4562, 0x6c5c7448, 0x65517f46, 0x7e466254, 0x774b695a, 0x90d0b0e0, 0x99ddbbee, 0x82caa6fc, 0x8bc7adf2, 0xb4e49cd8, 0xbde997d6, 0xa6fe8ac4, 0xaff381ca, 0xd8b8e890, 0xd1b5e39e, 0xcaa2fe8c, 0xc3aff582, 0xfc8cc4a8, 0xf581cfa6, 0xee96d2b4, 0xe79bd9ba, 0x3bbb7bdb, 0x32b670d5, 0x29a16dc7, 0x20ac66c9, 0x1f8f57e3, 0x16825ced, 0x0d9541ff, 0x04984af1, 0x73d323ab, 0x7ade28a5, 0x61c935b7, 0x68c43eb9, 0x57e70f93, 0x5eea049d, 0x45fd198f, 0x4cf01281, 0xab6bcb3b, 0xa266c035, 0xb971dd27, 0xb07cd629, 0x8f5fe703, 0x8652ec0d, 0x9d45f11f, 0x9448fa11, 0xe303934b, 0xea0e9845, 0xf1198557, 0xf8148e59, 0xc737bf73, 0xce3ab47d, 0xd52da96f, 0xdc20a261, 0x766df6ad, 0x7f60fda3, 0x6477e0b1, 0x6d7aebbf, 0x5259da95, 0x5b54d19b, 0x4043cc89, 0x494ec787, 0x3e05aedd, 0x3708a5d3, 0x2c1fb8c1, 0x2512b3cf, 0x1a3182e5, 0x133c89eb, 0x082b94f9, 0x01269ff7, 0xe6bd464d, 0xefb04d43, 0xf4a75051, 0xfdaa5b5f, 0xc2896a75, 0xcb84617b, 0xd0937c69, 0xd99e7767, 0xaed51e3d, 0xa7d81533, 0xbccf0821, 0xb5c2032f, 0x8ae13205, 0x83ec390b, 0x98fb2419, 0x91f62f17, 0x4dd68d76, 0x44db8678, 0x5fcc9b6a, 0x56c19064, 0x69e2a14e, 0x60efaa40, 0x7bf8b752, 0x72f5bc5c, 0x05bed506, 0x0cb3de08, 0x17a4c31a, 0x1ea9c814, 0x218af93e, 0x2887f230, 0x3390ef22, 0x3a9de42c, 0xdd063d96, 0xd40b3698, 0xcf1c2b8a, 0xc6112084, 0xf93211ae, 0xf03f1aa0, 0xeb2807b2, 0xe2250cbc, 0x956e65e6, 0x9c636ee8, 0x877473fa, 0x8e7978f4, 0xb15a49de, 0xb85742d0, 0xa3405fc2, 0xaa4d54cc, 0xecdaf741, 0xe5d7fc4f, 0xfec0e15d, 0xf7cdea53, 0xc8eedb79, 0xc1e3d077, 0xdaf4cd65, 0xd3f9c66b, 0xa4b2af31, 0xadbfa43f, 0xb6a8b92d, 0xbfa5b223, 0x80868309, 0x898b8807, 0x929c9515, 0x9b919e1b, 0x7c0a47a1, 0x75074caf, 0x6e1051bd, 0x671d5ab3, 0x583e6b99, 0x51336097, 0x4a247d85, 0x4329768b, 0x34621fd1, 0x3d6f14df, 0x267809cd, 0x2f7502c3, 0x105633e9, 0x195b38e7, 0x024c25f5, 0x0b412efb, 0xd7618c9a, 0xde6c8794, 0xc57b9a86, 0xcc769188, 0xf355a0a2, 0xfa58abac, 0xe14fb6be, 0xe842bdb0, 0x9f09d4ea, 0x9604dfe4, 0x8d13c2f6, 0x841ec9f8, 0xbb3df8d2, 0xb230f3dc, 0xa927eece, 0xa02ae5c0, 0x47b13c7a, 0x4ebc3774, 0x55ab2a66, 0x5ca62168, 0x63851042, 0x6a881b4c, 0x719f065e, 0x78920d50, 0x0fd9640a, 0x06d46f04, 0x1dc37216, 0x14ce7918, 0x2bed4832, 0x22e0433c, 0x39f75e2e, 0x30fa5520, 0x9ab701ec, 0x93ba0ae2, 0x88ad17f0, 0x81a01cfe, 0xbe832dd4, 0xb78e26da, 0xac993bc8, 0xa59430c6, 0xd2df599c, 0xdbd25292, 0xc0c54f80, 0xc9c8448e, 0xf6eb75a4, 0xffe67eaa, 0xe4f163b8, 0xedfc68b6, 0x0a67b10c, 0x036aba02, 0x187da710, 0x1170ac1e, 0x2e539d34, 0x275e963a, 0x3c498b28, 0x35448026, 0x420fe97c, 0x4b02e272, 0x5015ff60, 0x5918f46e, 0x663bc544, 0x6f36ce4a, 0x7421d358, 0x7d2cd856, 0xa10c7a37, 0xa8017139, 0xb3166c2b, 0xba1b6725, 0x8538560f, 0x8c355d01, 0x97224013, 0x9e2f4b1d, 0xe9642247, 0xe0692949, 0xfb7e345b, 0xf2733f55, 0xcd500e7f, 0xc45d0571, 0xdf4a1863, 0xd647136d, 0x31dccad7, 0x38d1c1d9, 0x23c6dccb, 0x2acbd7c5, 0x15e8e6ef, 0x1ce5ede1, 0x07f2f0f3, 0x0efffbfd, 0x79b492a7, 0x70b999a9, 0x6bae84bb, 0x62a38fb5, 0x5d80be9f, 0x548db591, 0x4f9aa883, 0x4697a38d ]
        def __init__(self, key):
            rounds = self.number_of_rounds[len(key)]
            self._Ke = [[0] * 4 for i in xrange(rounds + 1)]
            self._Kd = [[0] * 4 for i in xrange(rounds + 1)]
            round_key_count = (rounds + 1) * 4
            KC = len(key) // 4
            def b2integer(b):
                idx,ret = 0,0
                for i in b[::-1]:
                    ret += i<<(idx*8)
                    idx += 1
                return ret
            tk = [ b2integer(key[i:i + 4]) for i in xrange(0, len(key), 4) ]
            for i in xrange(0, KC):
                self._Ke[i // 4][i % 4] = tk[i]
                self._Kd[rounds - (i // 4)][i % 4] = tk[i]
            rconpointer = 0
            t = KC
            while t < round_key_count:
                tt = tk[KC - 1]
                tk[0] ^= ((self.S[(tt >> 16) & 0xFF] << 24) ^
                          (self.S[(tt >>  8) & 0xFF] << 16) ^
                          (self.S[ tt        & 0xFF] <<  8) ^
                           self.S[(tt >> 24) & 0xFF]        ^
                          (self.rcon[rconpointer] << 24))
                rconpointer += 1
                if KC != 8:
                    for i in xrange(1, KC):
                        tk[i] ^= tk[i - 1]
                else:
                    for i in xrange(1, KC // 2):
                        tk[i] ^= tk[i - 1]
                    tt = tk[KC // 2 - 1]
                    tk[KC // 2] ^= (self.S[ tt        & 0xFF]        ^
                                   (self.S[(tt >>  8) & 0xFF] <<  8) ^
                                   (self.S[(tt >> 16) & 0xFF] << 16) ^
                                   (self.S[(tt >> 24) & 0xFF] << 24))
                    for i in xrange(KC // 2 + 1, KC):
                        tk[i] ^= tk[i - 1]
                j = 0
                while j < KC and t < round_key_count:
                    self._Ke[t // 4][t % 4] = tk[j]
                    self._Kd[rounds - (t // 4)][t % 4] = tk[j]
                    j += 1
                    t += 1
            for r in xrange(1, rounds):
                for j in xrange(0, 4):
                    tt = self._Kd[r][j]
                    self._Kd[r][j] = (self.U1[(tt >> 24) & 0xFF] ^
                                      self.U2[(tt >> 16) & 0xFF] ^
                                      self.U3[(tt >>  8) & 0xFF] ^
                                      self.U4[ tt        & 0xFF])
        def encrypt(self, plaintext):
            rounds = len(self._Ke) - 1
            (s1, s2, s3) = [1, 2, 3]
            a = [0, 0, 0, 0]
            t = [(_compact_word(plaintext[4 * i:4 * i + 4]) ^ self._Ke[0][i]) for i in xrange(0, 4)]
            for r in xrange(1, rounds):
                for i in xrange(0, 4):
                    a[i] = (self.T1[(t[ i          ] >> 24) & 0xFF] ^
                            self.T2[(t[(i + s1) % 4] >> 16) & 0xFF] ^
                            self.T3[(t[(i + s2) % 4] >>  8) & 0xFF] ^
                            self.T4[ t[(i + s3) % 4]        & 0xFF] ^
                            self._Ke[r][i])
                t = a.copy()
            result = [ ]
            for i in xrange(0, 4):
                tt = self._Ke[rounds][i]
                result.append((self.S[(t[ i           ] >> 24) & 0xFF] ^ (tt >> 24)) & 0xFF)
                result.append((self.S[(t[(i + s1) % 4] >> 16) & 0xFF] ^ (tt >> 16)) & 0xFF)
                result.append((self.S[(t[(i + s2) % 4] >>  8) & 0xFF] ^ (tt >>  8)) & 0xFF)
                result.append((self.S[ t[(i + s3) % 4]        & 0xFF] ^  tt       ) & 0xFF)
            return result
        def decrypt(self, ciphertext):
            rounds = len(self._Kd) - 1
            (s1, s2, s3) = [3, 2, 1]
            a = [0, 0, 0, 0]
            t = [(_compact_word(ciphertext[4 * i:4 * i + 4]) ^ self._Kd[0][i]) for i in xrange(0, 4)]
            for r in xrange(1, rounds):
                for i in xrange(0, 4):
                    a[i] = (self.T5[(t[ i          ] >> 24) & 0xFF] ^
                            self.T6[(t[(i + s1) % 4] >> 16) & 0xFF] ^
                            self.T7[(t[(i + s2) % 4] >>  8) & 0xFF] ^
                            self.T8[ t[(i + s3) % 4]        & 0xFF] ^
                            self._Kd[r][i])
                t = a.copy()
            result = [ ]
            for i in xrange(0, 4):
                tt = self._Kd[rounds][i]
                result.append((self.Si[(t[ i           ] >> 24) & 0xFF] ^ (tt >> 24)) & 0xFF)
                result.append((self.Si[(t[(i + s1) % 4] >> 16) & 0xFF] ^ (tt >> 16)) & 0xFF)
                result.append((self.Si[(t[(i + s2) % 4] >>  8) & 0xFF] ^ (tt >>  8)) & 0xFF)
                result.append((self.Si[ t[(i + s3) % 4]        & 0xFF] ^  tt       ) & 0xFF)
            return result
    class AESModeOfOperationCBC:
        def __init__(self, key, iv = None):
            self._aes = AES(key)
            if iv is None:
                self._last_cipherblock = [ 0 ] * 16
            else:
                self._last_cipherblock = _string_to_bytes(iv)
        def encrypt(self, plaintext):
            plaintext = _string_to_bytes(plaintext)
            precipherblock = [ (p ^ l) for (p, l) in zip(plaintext, self._last_cipherblock) ]
            self._last_cipherblock = self._aes.encrypt(precipherblock)
            return _bytes_to_string(self._last_cipherblock)
        def decrypt(self, ciphertext):
            cipherblock = _string_to_bytes(ciphertext)
            plaintext = [ (p ^ l) for (p, l) in zip(self._aes.decrypt(cipherblock), self._last_cipherblock) ]
            self._last_cipherblock = cipherblock
            return _bytes_to_string(plaintext)
    PADDING_NONE       = 'none'
    PADDING_DEFAULT    = 'default'
    def _get_byte(c):
        if isinstance(c, (bytes,int)):
            return c
        return ord(c)
    def to_bufferable(binary):
        if isinstance(binary, bytes):
            return binary
        return bytes(ord(b) for b in binary)
    def append_PKCS7_padding(data):
        pad = 16 - (len(data) % 16)
        return data + to_bufferable(chr(pad) * pad)
    def strip_PKCS7_padding(data): return data[:-_get_byte(data[-1])]
    def _block_can_consume(self, size):
        return 16 if size >= 16 else 0
    def _block_final_encrypt(self, data, padding = PADDING_DEFAULT):
        if padding == PADDING_DEFAULT: data = append_PKCS7_padding(data)
        if len(data) not in (16,32): raise Exception('invalid padding option')
        if len(data) == 32: return self.encrypt(data[:16]) + self.encrypt(data[16:])
        return self.encrypt(data)
    def _block_final_decrypt(self, data, padding = PADDING_DEFAULT):
        if padding == PADDING_DEFAULT: return strip_PKCS7_padding(self.decrypt(data))
        if padding == PADDING_NONE: return self.decrypt(data)
    AESModeOfOperationCBC._can_consume = _block_can_consume
    AESModeOfOperationCBC._final_encrypt = _block_final_encrypt
    AESModeOfOperationCBC._final_decrypt = _block_final_decrypt
    class BlockFeeder(object):
        def __init__(self, mode, feed, final, padding = PADDING_DEFAULT):
            self._mode = mode
            self._feed = feed
            self._final = final
            self._buffer = to_bufferable("")
            self._padding = padding

        def feed(self, data = None):
            if self._buffer is None:
                raise ValueError('already finished feeder')
            if data is None:
                result = self._final(self._buffer, self._padding)
                self._buffer = None
                return result

            self._buffer += to_bufferable(data)
            result = to_bufferable('')
            while len(self._buffer) > 0:
                can_consume = self._mode._can_consume(len(self._buffer) - 16)
                if can_consume == 0:
                    result += self._final(self._buffer, self._padding)
                    break
                result += self._feed(self._buffer[:can_consume])
                self._buffer = self._buffer[can_consume:]
            return result
    class Encrypter(BlockFeeder):
        def __init__(self, mode, padding = PADDING_DEFAULT):
            BlockFeeder.__init__(self, mode, mode.encrypt, mode._final_encrypt, padding)
    class Decrypter(BlockFeeder):
        def __init__(self, mode, padding = PADDING_DEFAULT):
            BlockFeeder.__init__(self, mode, mode.decrypt, mode._final_decrypt, padding)
    def _enc(data, key, vi, padding='default'):
        s = Encrypter(AESModeOfOperationCBC(key.encode(), iv), padding=padding)
        return b2a_hex(s.feed(data.encode())).decode()
    def _dec(data, key, iv, padding='default'):
        s = Decrypter(AESModeOfOperationCBC(key.encode(), iv), padding=padding)
        return s.feed(a2b_hex(data)).decode()
    def _enc_base(zdata, key, vi, padding='default', basefunc=base64.b64encode):
        s = Encrypter(AESModeOfOperationCBC(key.encode(), iv), padding=padding)
        return basefunc(s.feed(zdata)).decode()
    def _dec_base(data, key, iv, padding='default', basefunc=base64.b64decode):
        s = Decrypter(AESModeOfOperationCBC(key.encode(), iv), padding=padding)
        return s.feed(basefunc(data))
    class _: pass
    t = _()
    t.encrypt_a2b = lambda data: _enc(data, key, iv)
    t.decrypt_b2a = lambda data: _dec(data, key, iv)
    t.encrypt_base = lambda data, basefunc: _enc_base(data, key, iv, basefunc=basefunc)
    t.decrypt_base = lambda data, basefunc: _dec_base(data, key, iv, basefunc=basefunc)
    return t


def crypter(ack='',iv='2769514380123456',base='b64'):
    ahk = hmac.new(b'vilame',ack.encode(),'md5').hexdigest()
    c = CrypterAES(ahk, iv)
    if base == 'b16': _encode,_decode = base64.b16encode,base64.b16decode
    if base == 'b32': _encode,_decode = base64.b32encode,base64.b32decode
    if base == 'b64': _encode,_decode = base64.b64encode,base64.b64decode
    if base == 'b85': _encode,_decode = base64.b85encode,base64.b85decode
    if base == 'urlsafe_b64': _encode,_decode = base64.urlsafe_b64encode,base64.urlsafe_b64decode
    def zbase_enc(data):
        return _encode(zlib.compress(data.encode())[2:-4]).decode()
    def zbase_dec(basedata):
        return zlib.decompress(_decode(basedata),-15).decode()
    def zencrypt(data): return c.encrypt_base(zlib.compress(data.encode())[2:-4],_encode)
    def zdecrypt(data): return zlib.decompress(c.decrypt_base(data,_decode),-15).decode()
    c.zencrypt = zencrypt
    c.zdecrypt = zdecrypt
    c.zbase_enc = zbase_enc
    c.zbase_dec = zbase_dec
    c.encrypt = lambda data:c.encrypt_base(data,_encode)
    c.decrypt = lambda data:c.decrypt_base(data,_decode).decode()
    return c


if __name__ == '__main__':
    c = crypter(ack='asdfasdf')
    
    data = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaabbbbbbbbbbbbbbbbbbbbbbbbbbbbbcccccccccccccccccccccccccc'
    # data = 'da39a3ee5e6b4b0d3255bfef95601890afd80709d14a028c2a3a2bc9476102bb288234c415a2b01f828ea62a'

    print('直接使用 aes 对数据加密')
    v = c.encrypt(data); print(v)
    v = c.decrypt(v); print(v)

    print('仅仅是压缩的话，数据重复性很高的话一般都能压缩非常多')
    v = c.zbase_enc(data); print(v)
    v = c.zbase_dec(v); print(v)

    print('压缩数据后再进行加密，兼顾了加密和压缩两项功能，工具内的加密就使用这个算法。')
    v = c.zencrypt(data); print(v)
    v = c.zdecrypt(v); print(v)
'''.strip()
        print(code)

    f20 = Frame(ff0)
    f20.pack(side=tkinter.TOP,fill=tkinter.X)
    Label(f20, text='                                     加解密算法').pack(fill=tkinter.X,expand=True)
    f21 = Frame(ff0)
    f21.pack(side=tkinter.TOP,fill=tkinter.X)
    Label(f21, text='     以下算法为个人私用。应对 python 压缩的、无外部依赖库的、可带密码的、字符串加解密。').pack(fill=tkinter.X,expand=True)

    f22 = Frame(ff0)
    f22.pack(side=tkinter.TOP,fill=tkinter.X)
    ent22 = Entry(f22,width=10)
    def _switch_ack(*a):
        def _show(*a, stat='show'):
            try:
                if stat == 'show': ent22.pack(side=tkinter.LEFT)
                if stat == 'hide': ent22.pack_forget()
            except:
                pass
        _show(stat='show') if aa.get() else _show(stat='hide')
    aa = tkinter.IntVar()
    ab = Checkbutton(f22,text='密码',variable=aa,command=_switch_ack)
    ab.pack(side=tkinter.LEFT)
    ab.deselect()

    cbx = Combobox(f22,width=4,state='readonly')
    cbx['values'] = base64enc = ['b16','b32','b64','b85',]
    cbx.current(3)
    cbx.pack(side=tkinter.RIGHT)
    Label(f22, text='编码',width=4).pack(side=tkinter.RIGHT,padx=5)
    Button(f22, text='[算法]',command=_my_code,width=5).pack(side=tkinter.RIGHT)
    Button(f22, text='解密',command=_my_decode,width=5).pack(side=tkinter.RIGHT)
    Button(f22, text='加密',command=_my_encode,width=5).pack(side=tkinter.RIGHT)
    txttitlefr = Frame(ff0_)
    txttitlefr.pack(side=tkinter.TOP)
    Label(txttitlefr, text='使用以下文本框进行加解密 [仅忽略文本前后换行符,空格不忽略]，显示限制字符数：').pack(side=tkinter.LEFT,padx=10)
    entlimit = Entry(txttitlefr, width=10)
    entlimit.pack(side=tkinter.LEFT)
    entlimit.insert(0,'10000')
    ftxt = Text(ff0_,font=ft)
    ftxt.pack(padx=padx,pady=pady,fill=tkinter.BOTH,expand=True)

    def change_cbit_1(*content):
        if content:
            encd = fent1.get().strip()
            blen = len(content[0].encode(encd))*8
            cbit1['text'] = str(blen)+'bit'
            return True
    def change_cbit_2(*content):
        if content:
            encd = fent1.get().strip()
            blen = len(content[0].encode(encd))*8
            cbit2['text'] = str(blen)+'bit'
            return True

    change_cbit1 = root.register(change_cbit_1)
    change_cbit2 = root.register(change_cbit_2)

    # 这里后续需要考虑增加各种各样的加密解密以及代码的记录
    # 光是aes就有5种加解密方式
    f23 = Frame(ff0)
    f23.pack(side=tkinter.TOP,fill=tkinter.X)
    Label(f23, text='     以下算法为 AES 加解密算法 [密码长度需注意:128bit,192bit,256bit] [iv长度需注意:128bit]。').pack(fill=tkinter.X,expand=True)
    f24 = Frame(ff0)
    f24.pack(side=tkinter.TOP,fill=tkinter.X)
    Label(f24, text='密码',width=4).pack(side=tkinter.LEFT,padx=2)
    ent23 = Entry(f24,width=17,validate='key',validatecommand=(change_cbit1, '%P'))
    ent23.pack(side=tkinter.LEFT)
    ent23.bind('<Key>', change_cbit1)
    cbit1 = Label(f24, text='0:bit',width=6)
    cbit1.pack(side=tkinter.LEFT,padx=6)
    cbx1 = Combobox(f24,width=4,state='readonly')
    cbx1['values'] = ['b16','b32','b64','b85']
    cbx1.current(2)
    cbx1.pack(side=tkinter.RIGHT)
    Label(f24, text='编码',width=4).pack(side=tkinter.RIGHT,padx=5)
    def _swich_encd1(*a):
        s = fent1.get().strip()
        if s == 'utf-8':
            fent1.delete(0,tkinter.END)
            fent1.insert(0,'gbk')
        elif s == 'gbk':
            fent1.delete(0,tkinter.END)
            fent1.insert(0,'utf-8')
        else:
            fent1.delete(0,tkinter.END)
            fent1.insert(0,'utf-8')
        change_cbit_1(ent23.get().strip())
        change_cbit_2(ent24.get().strip())
    fent1 = Entry(f24,width=5)
    fent1.insert(0,'utf-8')
    fent1.pack(side=tkinter.RIGHT)
    Button(f24, text='密码/iv/数据编码格式',command=_swich_encd1).pack(side=tkinter.RIGHT)
    cbx2 = Combobox(f24,width=4,state='readonly')
    cbx2['values'] = ['cbc','cfb','ofb','ctr','ecb',]
    cbx2.current(0)
    cbx2.pack(side=tkinter.RIGHT)
    Label(f24, text='模式',width=4).pack(side=tkinter.RIGHT,padx=5)
    f25 = Frame(ff0)
    f25.pack(side=tkinter.TOP,fill=tkinter.X)
    Label(f25, text='iv',width=4).pack(side=tkinter.LEFT,padx=2)
    ent24 = Entry(f25,width=17,validate='key',validatecommand=(change_cbit2, '%P'))
    ent24.pack(side=tkinter.LEFT)
    
    cbit2 = Label(f25, text='128:bit',width=6)
    cbit2.pack(side=tkinter.LEFT,padx=6)
    ent24.insert(0,'1234567890123456')
    Label(f25, text='当模式为 ctr/ecb 时，iv无效',).pack(side=tkinter.LEFT,padx=6)

    def _aes_encode(*a):
        encd = fent1.get().strip()
        mode = cbx2.get().strip()
        eout = cbx1.get().strip()
        key  = ent23.get().strip().encode(encd)
        iv   = ent24.get().strip().encode(encd)
        data = ftxt.get(0.,tkinter.END).strip('\n').encode(encd)
        limitnum = int(entlimit.get().strip())
        ftxt.delete(0.,tkinter.END)
        try:
            from . import pyaes
        except:
            # 请勿在本脚本测试时安装了 pyaes，pyaes的源码部分有问题
            import pyaes
        if eout == 'b16':_encode = base64.b16encode; _decode = base64.b16decode
        if eout == 'b32':_encode = base64.b32encode; _decode = base64.b32decode
        if eout == 'b64':_encode = base64.b64encode; _decode = base64.b64decode
        if eout == 'b85':_encode = base64.b85encode; _decode = base64.b85decode
        Encrypter = pyaes.Encrypter
        Counter = pyaes.Counter
        AESModesOfOperation = pyaes.AESModesOfOperation

        try:
            if mode in 'ctr':
                enc = Encrypter(AESModesOfOperation[mode](key, Counter(int.from_bytes(iv, 'big'))))
            elif mode == 'ecb':
                enc = Encrypter(AESModesOfOperation[mode](key))
            else:
                enc = Encrypter(AESModesOfOperation[mode](key, iv))
            en = _encode(enc.feed(data)).decode(encd)
            if len(en) > limitnum:
                print('警告！')
                print('加密数据长度({})过长（超过{}字符，超过的部分不显示）'.format(len(en),limitnum))
                print('因为 tkinter 性能瓶颈，不宜在 tkinter 窗口展示，请使用算法在别的IDE内实现')
                print('---------------------------------------------------')
                print(en[:limitnum])
            else:
                print(en)
        except:
            print(traceback.format_exc())

    def _aes_decode(*a):
        encd = fent1.get().strip()
        mode = cbx2.get().strip()
        eout = cbx1.get().strip()
        key  = ent23.get().strip().encode(encd)
        iv   = ent24.get().strip().encode(encd)
        data = ftxt.get(0.,tkinter.END).strip('\n').encode(encd)
        ftxt.delete(0.,tkinter.END)
        try:
            from . import pyaes
        except:
            # 请勿在本脚本测试时安装了 pyaes，pyaes的源码部分有问题
            import pyaes
        if eout == 'b16':_encode = base64.b16encode; _decode = base64.b16decode
        if eout == 'b32':_encode = base64.b32encode; _decode = base64.b32decode
        if eout == 'b64':_encode = base64.b64encode; _decode = base64.b64decode
        if eout == 'b85':_encode = base64.b85encode; _decode = base64.b85decode
        Decrypter = pyaes.Decrypter
        Counter = pyaes.Counter
        AESModesOfOperation = pyaes.AESModesOfOperation

        try:
            if mode in 'ctr':
                dec = Decrypter(AESModesOfOperation[mode](key, Counter(int.from_bytes(iv, 'big'))))
            elif mode == 'ecb':
                dec = Decrypter(AESModesOfOperation[mode](key))
            else:
                dec = Decrypter(AESModesOfOperation[mode](key, iv))
            dc = dec.feed(_decode(data)).decode(encd)
            print(dc)
        except:
            print(traceback.format_exc())

    def _aes_code(*a):
        try:
            from . import pyaes
        except:
            import pyaes
        ftxt.delete(0.,tkinter.END)
        with open(pyaes.__file__, encoding='utf-8') as f:
            data = f.read().strip('\n')
        print(data)

    Button(f25, text='[算法]',command=_aes_code,width=5).pack(side=tkinter.RIGHT)
    Button(f25, text='解密',command=_aes_decode,width=5).pack(side=tkinter.RIGHT)
    Button(f25, text='加密',command=_aes_encode,width=5).pack(side=tkinter.RIGHT)




    # 这部分是后续增加的纯 python 的des解密
    def change_cbit_3(*content):
        if content:
            encd = fent2.get().strip()
            blen = len(content[0].encode(encd))*8
            cbit3['text'] = str(blen)+'bit'
            return True
    def change_cbit_4(*content):
        if content:
            encd = fent2.get().strip()
            blen = len(content[0].encode(encd))*8
            cbit4['text'] = str(blen)+'bit'
            return True

    change_cbit3 = root.register(change_cbit_3)
    change_cbit4 = root.register(change_cbit_4)

    f23 = Frame(ff0)
    f23.pack(side=tkinter.TOP,fill=tkinter.X)
    Label(f23, text='     以下算法为 DES/3DES 加解密算法 [密码长度:64bit(DES),128bit(3DES),192bit(3DES)] [iv长度:64bit]。').pack(fill=tkinter.X,expand=True)
    f24 = Frame(ff0)
    f24.pack(side=tkinter.TOP,fill=tkinter.X)
    Label(f24, text='密码',width=4).pack(side=tkinter.LEFT,padx=2)
    ent25 = Entry(f24,width=17,validate='key',validatecommand=(change_cbit3, '%P'))
    ent25.pack(side=tkinter.LEFT)
    ent25.bind('<Key>', change_cbit3)
    cbit3 = Label(f24, text='0:bit',width=6)
    cbit3.pack(side=tkinter.LEFT,padx=6)
    cbx3 = Combobox(f24,width=4,state='readonly')
    cbx3['values'] = ['b16','b32','b64','b85']
    cbx3.current(2)
    cbx3.pack(side=tkinter.RIGHT)
    Label(f24, text='编码',width=4).pack(side=tkinter.RIGHT,padx=5)
    def _swich_encd1(*a):
        s = fent2.get().strip()
        if s == 'utf-8':
            fent2.delete(0,tkinter.END)
            fent2.insert(0,'gbk')
        elif s == 'gbk':
            fent2.delete(0,tkinter.END)
            fent2.insert(0,'utf-8')
        else:
            fent2.delete(0,tkinter.END)
            fent2.insert(0,'utf-8')
        change_cbit_3(ent25.get().strip())
        change_cbit_4(ent26.get().strip())
    fent2 = Entry(f24,width=5)
    fent2.insert(0,'utf-8')
    fent2.pack(side=tkinter.RIGHT)
    Button(f24, text='密码/iv/数据编码格式',command=_swich_encd1).pack(side=tkinter.RIGHT)
    cbx4 = Combobox(f24,width=4,state='readonly')
    cbx4['values'] = ['cbc','ecb',]
    cbx4.current(0)
    cbx4.pack(side=tkinter.RIGHT)
    Label(f24, text='模式',width=4).pack(side=tkinter.RIGHT,padx=5)
    f25 = Frame(ff0)
    f25.pack(side=tkinter.TOP,fill=tkinter.X)
    Label(f25, text='iv',width=4).pack(side=tkinter.LEFT,padx=2)
    ent26 = Entry(f25,width=17,validate='key',validatecommand=(change_cbit4, '%P'))
    ent26.pack(side=tkinter.LEFT)
    
    cbit4 = Label(f25, text='128:bit',width=6)
    cbit4.pack(side=tkinter.LEFT,padx=6)
    ent26.insert(0,'12345678')
    Label(f25, text='当模式为 ctr/ecb 时，iv无效',).pack(side=tkinter.LEFT,padx=6)

    def _des_encode(*a):
        encd = fent2.get().strip()
        mode = cbx4.get().strip()
        eout = cbx3.get().strip()
        key  = ent25.get().strip().encode(encd)
        iv   = ent26.get().strip().encode(encd)
        data = ftxt.get(0.,tkinter.END).strip('\n').encode(encd)
        limitnum = int(entlimit.get().strip())
        ftxt.delete(0.,tkinter.END)
        try:
            from . import pydes
        except:
            # 请勿在本脚本测试时安装了 pyaes，pyaes的源码部分有问题
            import pydes
        if eout == 'b16':_encode = base64.b16encode; _decode = base64.b16decode
        if eout == 'b32':_encode = base64.b32encode; _decode = base64.b32decode
        if eout == 'b64':_encode = base64.b64encode; _decode = base64.b64decode
        if eout == 'b85':_encode = base64.b85encode; _decode = base64.b85decode
        if len(key) not in [8,16,24]:
            print('error. len(key) must in [64bit,128bit,192bit]. now is {}.'.format(len(key)*8))
            return
        try:
            if mode in 'ecb': mode = pydes.ECB
            elif mode == 'cbc': mode = pydes.CBC
            else:
                print('error mode:{}, mode must in [ecb cbc]'.format(mode))
            if len(key) == 8:
                d = pydes.des(key, mode, iv, padmode=pydes.PAD_PKCS5)
            else:
                d = pydes.triple_des(key, mode, iv, padmode=pydes.PAD_PKCS5)
            en = _encode(d.encrypt(data)).decode(encd)
            if len(en) > limitnum:
                print('警告！')
                print('加密数据长度({})过长（超过{}字符，超过的部分不显示）'.format(len(en),limitnum))
                print('因为 tkinter 性能瓶颈，不宜在 tkinter 窗口展示，请使用算法在别的IDE内实现')
                print('---------------------------------------------------')
                print(en[:limitnum])
            else:
                print(en)
        except:
            print(traceback.format_exc())

    def _des_decode(*a):
        encd = fent2.get().strip()
        mode = cbx4.get().strip()
        eout = cbx3.get().strip()
        key  = ent25.get().strip().encode(encd)
        iv   = ent26.get().strip().encode(encd)
        data = ftxt.get(0.,tkinter.END).strip('\n').encode(encd)
        ftxt.delete(0.,tkinter.END)
        try:
            from . import pydes
        except:
            # 请勿在本脚本测试时安装了 pyaes，pyaes的源码部分有问题
            import pydes
        if eout == 'b16':_encode = base64.b16encode; _decode = base64.b16decode
        if eout == 'b32':_encode = base64.b32encode; _decode = base64.b32decode
        if eout == 'b64':_encode = base64.b64encode; _decode = base64.b64decode
        if eout == 'b85':_encode = base64.b85encode; _decode = base64.b85decode
        if len(key) not in [8,16,24]:
            print('error. len(key) must in [64bit,128bit,192bit]. now is {}.'.format(len(key)*8))
            return
        try:
            if mode in 'ecb': mode = pydes.ECB
            elif mode == 'cbc': mode = pydes.CBC
            else:
                print('error mode:{}, mode must in [ecb cbc]'.format(mode))
            if len(key) == 8:
                d = pydes.des(key, mode, iv, padmode=pydes.PAD_PKCS5)
            else:
                d = pydes.triple_des(key, mode, iv, padmode=pydes.PAD_PKCS5)
            dc = d.decrypt(_decode(data)).decode(encd)
            print(dc)
        except:
            print(traceback.format_exc())

    def _des_code(*a):
        try:
            from . import pydes
        except:
            import pydes
        ftxt.delete(0.,tkinter.END)
        with open(pydes.__file__, encoding='utf-8') as f:
            data = f.read().strip('\n')
        print(data)

    Button(f25, text='[算法]',command=_des_code,width=5).pack(side=tkinter.RIGHT)
    Button(f25, text='解密',command=_des_decode,width=5).pack(side=tkinter.RIGHT)
    Button(f25, text='加密',command=_des_encode,width=5).pack(side=tkinter.RIGHT)

    f100 = Frame(ff0)
    f100.pack(side=tkinter.TOP,fill=tkinter.X)
    f101 = Frame(f100)
    f102 = Frame(f100)
    f101.pack(side=tkinter.TOP,fill=tkinter.X)
    f102.pack(side=tkinter.TOP,fill=tkinter.X)
    Label(f101, text='     以下算法纯 python 解密 jsfuck。').pack(fill=tkinter.X,expand=True)
    def _jsfuck_decode(*a):
        data = ftxt.get(0.,tkinter.END).strip('\n')
        ftxt.delete(0.,tkinter.END)
        try:
            from . import pyjsfuck
        except:
            import pyjsfuck
        try:
            f = pyjsfuck.unjsfuck(data, debuglevel=1, logger=print)
            print()
            print('[ result ]:')
            print(f)
        except:
            ftxt.delete(0.,tkinter.END)
            print(traceback.format_exc())
            print('error decoding!!! check input data.')

    def _jsfuck_code(*a):
        try:
            from . import pyjsfuck
        except:
            import pyjsfuck
        ftxt.delete(0.,tkinter.END)
        with open(pyjsfuck.__file__, encoding='utf-8') as f:
            data = f.read().strip('\n')
        print(data)

    Button(f102, text='[算法]',command=_jsfuck_code,width=5).pack(side=tkinter.RIGHT)
    Button(f102, text='解密',command=_jsfuck_decode,width=5).pack(side=tkinter.RIGHT)
    return fr


if __name__ == '__main__':
    # test frame
    fr = encode_window()
    fr.title('命令行输入 vv e 则可快速打开便捷加密窗口')

    sys.stdout = __org_stdout__
    fr.bind('<Escape>',lambda *a:fr.master.quit())
    fr.protocol("WM_DELETE_WINDOW",lambda *a:fr.master.quit())
    fr.master.withdraw()
    fr.mainloop()