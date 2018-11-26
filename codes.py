import requests
import re
from bs4 import BeautifulSoup
from lxml import etree
import time

head = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0',
        'Host': 'movie.douban.com',
        'Cookie': 'll="118208"; bid=7oCzYf0fk0w; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1'
                  '543191350%2C%22https%3A%2F%2Fwww.baidu.com%2Fs%3Fie%3Dutf-8%26f%3D8%26rsv_b'
                  'p%3D1%26rsv_idx%3D1%26tn%3Dmonline_6_dg%26wd%3D%25E8%25B1%2586%25E7%2593%25'
                  'A3%26oq%3D%2525E7%25258C%2525AB%2525E7%25259C%2525BC%2525E7%252594%2525B5%'
                  '2525E5%2525BD%2525B1%26rsv_pq%3D92f0bbb10001cda4%26rsv_t%3D8bc8J0WsOLTeWlY'
                  'lTmTtiC2GrQJJ%252Bjv4IBc%252BiO%252FoESrXmrO3%252FfpNx%252FJTDJnnzkObnLrS%2'
                  '6rqlang%3Dcn%26rsv_enter%3D1%26inputT%3D1016%26rsv_sug3%3D41%26rsv_sug1%3D'
                  '36%26rsv_sug7%3D100%26rsv_sug2%3D0%26rsv_sug4%3D1712%22%5D; _pk_id.100001.4'
                  'cf6=e5dddf1ba3ddddc7.1543191350.1.1543191673.1543191350.; _pk_ses.100001.4c'
                  'f6=*; ap_v=0,6.0; __yadk_uid=zaO3DBqlq1sYsYvkjrtRzfCR1VaIP7Vn; __utma=3014'
                  '9280.81002317.1543191351.1543191351.1543191351.1; __utmb=30149280.0.10.154'
                  '3191351; __utmc=30149280; __utmz=30149280.1543191351.1.1.utmcsr=(direct)|ut'
                  'mccn=(direct)|utmcmd=(none); __utma=223695111.1225746777.1543191351.1543191'
                  '351.1543191351.1; __utmb=223695111.0.10.1543191351; __utmc=223695111; __utmz=2'
                  '23695111.1543191351.1.1.utmcsr=baidu|utmccn=(organic)|utmcmd=organic|utmctr=%E'
                  '8%B1%86%E7%93%A3; _vwo_uuid_v2=DFAB26D354461D79AFD2E9930EE48773C|babee1b1bca2'
                  'dad586f81c66493a0f5d'
}
params = {
        'limit': "20",
        'sort': "new_score",
        'start': None,
        'status': 'P'
}
comment_user = []
comment_info = []


def url(n):
        global params
        url_init = 'https://movie.douban.com/subject/3168101/comments?start={}&limit=20&sort=new_score&status=P'
        params['start'] = n
        return url_init.format(n)


def get_page(page_url):
        global params
        ht = requests.get(page_url, headers=head, params=params)
        ht.encoding = 'utf-8'
        return ht.text


def parse_with_re(response):
    global comment_info, comment_user
    commenttext = []
    author = re.findall(r'<a title="(.*?)" href=', response)
    commenttime = re.findall(r'class="comment-time " title="(.*?)">', response)
    commenttextt = re.findall(r'class="short">((.|\n)*?)</span>', response)
    # 获取评论内容，注意换行符和其他字符在正则中的问题
    for each in commenttextt:
        commenttext.append(each[0])
    temp_num = len(commenttextt)
    for every in range(temp_num):
        comment_user.append(author[every])
        # 将用户名存入一个列表
        comment_info.append((commenttime[every], commenttext[every]))
        # 将评论日期和内容组成元组后存入一个列表
    return


def parse_with_bs(response):
    global comment_user, comment_info
    # 声明全局变量
    com_user = []
    # 暂时存放用户名的列表
    respsoup = BeautifulSoup(response, 'lxml')
    temp_user = respsoup.find_all('div', class_="avatar")
    # 获取的是一个标签的列表
    for every in temp_user:
        com_user.append(every.a.get('title'))
        # 对标签列表进行遍历，对每一项提取出子节点a的title属性，即用户名的值
    temp_time = respsoup.find_all('span', class_="comment-time ")
    # 同样也是标签列表
    temp_comment = respsoup.find_all('span', class_="short")
    temp_num = len(temp_comment)
    for each in range(temp_num):
        # 遍历标签列表，对每一项提取所需要的元素
        # 提取文本的话，直接 tag.text
        comment_user.append(com_user[each])
        comment_info.append((temp_time[each].get('title'), temp_comment[each].text))
    return


def parse_with_lxml(response):
    # 感觉xpath比bs写得顺手些
    global comment_info, comment_user
    resplx = etree.HTML(response)
    temp_user = resplx.xpath('//div[@class="avatar"]/a/@title')
    temp_time = resplx.xpath('//span[@class="comment-time "]/@title')
    temp_comment = resplx.xpath('//span[@class="short"]/text()')
    temp_num = len(temp_comment)
    for each in range(temp_num):
        comment_user.append(temp_user[each])
        comment_info.append((temp_time[each], temp_comment[each]))
    return


if __name__ == '__main__':
    start_time = time.time()
    for i in range(1):
        # range() 里可以设置需要爬取的页数
        print('正在爬取第 %d 页' % (i+1))
        resp = get_page(url(i))
        parse_with_bs(resp)
    length = len(comment_info)
    with open('venom.csv', 'w', encoding='utf-8') as f:
        for i in range(length):
            f.write('"用户名",{0},"评论时间",{1},"评论内容",{2}\n'.format(
                comment_user[i],
                comment_info[i][0],
                comment_info[i][1]))
    # with open('venom.csv', 'w') as csvfile:
    #     csvfile.write(codecs.BOM_UTF8)
    #     file = csv.writer(csvfile, dialect='excel')
    #     for i in range(length):
    #         file.writerow('"用户名",{0},"评论时间",{1},"评论内容",{2}\n'.format(
    #             comment_user[i],
    #             comment_info[i][0],
    #             comment_info[i][1]))
    # print(comment_info[4][1])  # 检查是否乱码
    # for nn in comment_info:
    #     print(nn[1])
    end_time = time.time()
    all_time = end_time - start_time
    print(all_time)
