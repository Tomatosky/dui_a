import re, os, shutil
import requests

# 需要下载的对啊网公开课视频地址
init_url = 'https://live.duia.com/live/open/113476'

# 输出文件夹
output_dir = r'C:\Users\Administrator\Desktop'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}

# 获取clrid和clridurl参数
resp = requests.get(init_url, headers=headers)
resp.encoding = 'utf-8'
clrId = re.findall(r'"clrId":(\d{6}),"live"', resp.text)[0]
clrIdUrl = 'https://live.duia.com/liveD/data/{}'.format(clrId)

# 获取roomId,userId,userId,videoId参数
postdata = {'id': clrId}
resp = requests.post(clrIdUrl, headers=headers, data=postdata)
resp_json = resp.json()
roomId = resp_json['data']['cc']['roomId']
userId = resp_json['data']['cc']['userId']
videoId = resp_json['data']['cc']['videoId']

# 获取ts视频文件列表
infoUrl = 'https://view.csslcloud.net/api/view/replay/v2/info?roomid={}&userid={}&recordid={}'.format(roomId, userId,
                                                                                                      videoId)
resp = requests.get(infoUrl, headers=headers)
resp_json = resp.json()
pageChange = resp_json['datas']['meta']['pageChange']
h5url = 'https://view.csslcloud.net/api/vod/v2/play/h5?userid={}&roomid={}&recordid={}'.format(userId, roomId, videoId)
resp = requests.get(h5url, headers=headers)
resp_json = resp.json()
m3u8_url = resp_json['video'][0]['secureplayurl']
playurl = re.findall(r'(.{50,80})/.*.m3u8.*?', m3u8_url)[0]

# 下载PPT
os.mkdir(r'{}\1'.format(output_dir))
for i in range(len(pageChange)):
    print('正在下载PPT第{}页'.format(i))
    pagetime = pageChange[i]['time']
    pageurl = pageChange[i]['url']
    if pageurl != '#':
        resp = requests.get(pageurl, headers=headers)
        with open(r'{}\1\{}.jpg'.format(output_dir, pagetime), 'wb') as f:
            f.write(resp.content)
print('PPT下载完成\n')

# 将PPT图片转为视频
print('正在生成图片列表')
img_list = os.listdir(r'{}\1'.format(output_dir))
img_list.sort(key=lambda x: int(x[:-4]))
temp_text = ''
for i in range(len(img_list)):
    if i != len(img_list) - 1:
        dura = int(img_list[i + 1].split('.')[0]) - int(img_list[i].split('.')[0])
    else:
        dura = 2
    temp_text = temp_text + r"file '{}\1\{}'".format(output_dir,
                                                     img_list[i]) + '\n' + 'duration {}'.format(dura) + '\n'
temp_text = temp_text + r"file '{}\1\{}'".format(output_dir, img_list[-1])
with open(r'{}\1\1.txt'.format(output_dir), 'w') as f:
    f.write(temp_text)
print('正在将图片转换为视频')
command = r'ffmpeg -f concat -safe 0 -i {}\1\1.txt -vf fps=15 -vf scale=1280:-2 {}\output2.mp4'.format(output_dir,
                                                                                                     output_dir)
os.system(command)
shutil.rmtree(r'{}\1'.format(output_dir))
print('转换完成\n')

# 根据m3u8文件来下载ts文件
os.mkdir(r'{}\1'.format(output_dir))
resp = requests.get(m3u8_url, headers=headers)
with open(r'{}\m3u8.m3u8'.format(output_dir), 'wb') as f:
    f.write(resp.content)
with open(r'{}\m3u8.m3u8'.format(output_dir), 'r') as f:
    tslist = f.readlines()
ts_list = []
for i in tslist:
    if 'ts?video' in i:
        ts_list.append(i.replace('\n', ''))
temp_text = ''
for i in range(len(ts_list)):
    print('正在下载ts第{}个片段'.format(i))
    url = '{}/{}'.format(playurl, ts_list[i])
    resp = requests.get(url, headers=headers)
    with open(r'{}\1\{}.ts'.format(output_dir, i), 'wb') as f:
        f.write(resp.content)
    temp_text = temp_text + r"file '{}\1\{}.ts'".format(output_dir, i) + '\n'

print('ts下载完成\n')

# 将ts文件转为mp3文件

with open(r'{}\1\1.txt'.format(output_dir), 'w') as f:
    f.write(temp_text)
print('正在将ts片段转换为MP4')
command = r'ffmpeg -f concat -safe 0 -i {}\1\1.txt -c copy {}\output1.mp4'.format(output_dir, output_dir)
os.system(command)
print('转换完成\n')
print('正在从MP4中抽取MP3')
command = r'ffmpeg -i {}\output1.mp4 {}\output.mp3'.format(output_dir, output_dir)
os.system(command)
shutil.rmtree(r'{}\1'.format(output_dir))
print('抽取完成\n')

# 合并mp3文件和ppt视频文件
print('正在合并视频和音频')
command = r'ffmpeg -i {}\output.mp3 -i {}\output2.mp4 -c copy {}\result.mp4'.format(output_dir, output_dir, output_dir)
os.system(command)
print('合并完成\n')
