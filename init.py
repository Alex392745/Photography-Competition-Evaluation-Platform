import os
import pandas as pd
import sqlite3  # 用于数据库操作

# 定义文件夹路径
folder_path = './uploads'

# 获取文件夹中的所有文件名
file_list = os.listdir(folder_path)

# 过滤出图片文件（假设是常见的图片格式）
image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff')
image_files = [f for f in file_list if f.lower().endswith(image_extensions)]

# 创建DataFrame来存储信息
data = {
    'cid': [],     # 图片编号
    'cname': [],   # 照片名字
    'path': []     # 照片完整路径
}

data2 = {
    'cid': [],     # 图片编号
    'cname': [],   # 照片名字
    'vote1': [],
    'vote2': [],
    'vote3': [],
    'vote4': [],
    'vote5': [],
    'vote6': [],
    'vote7': [],
    'vote8': []
}

# 为每个图片文件生成信息
for idx, image_file in enumerate(image_files, start=1):
    cname, extension = os.path.splitext(image_file)  # 拆分文件名和扩展名
    data['cid'].append(idx)
    data2['cid'].append(idx)
    data['cname'].append(cname)
    data2['cname'].append(cname)
    data['path'].append(image_file)
    data2['vote1'].append(-1)
    data2['vote2'].append(-1)
    data2['vote3'].append(-1)
    data2['vote4'].append(-1)
    data2['vote5'].append(-1)
    data2['vote6'].append(-1)
    data2['vote7'].append(-1)
    data2['vote8'].append(-1)

# 创建DataFrame
df = pd.DataFrame(data)
df2=pd.DataFrame(data2)
# 打印DataFrame以查看结果

# 将DataFrame存储到SQLite数据库中
conn = sqlite3.connect('database.db')  # 连接到数据库（如果不存在则会创建）
df.to_sql('uploads', conn, if_exists='replace', index=False)  # 写入uploads表
df2.to_sql('cvote', conn, if_exists='replace', index=False)  # 写入cvote表
conn.close()  # 关闭数据库连接
