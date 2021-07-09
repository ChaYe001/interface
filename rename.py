import os

path = "D:\工作内容\测试记录\样本\手势\Movies\食指\\"
num = 131
for file in os.listdir(path):
    # num = file.split(".")[0].split("_")[-1]

    filename_change = "forefinger_" + str(num).zfill(4) + ".jpg"
    num+=1
    os.rename(os.path.join(path, file), os.path.join(path, filename_change))