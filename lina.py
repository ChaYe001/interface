import os
import codecs

# filenames = "C:\Work\G40\活体检测_G26\True_Data.txt"
filenames = "True_Data.txt"

out_score = open('FaceScore.txt', 'w')
out_score.write("阈值" + " " + "T个数" + " " + "D个数" + " " + "真脸个数" + " " + "真脸占比" + " " + "假脸占比" + "\n")

DT_PASS_NUM = 2
T_CAIJI_NUM = 10

print("阈值" + " " + "T个数" + "" + "D个数" + " " + "真脸个数" + " " + "真脸占比%" + " " + "假脸占比% \n")


def CheckTrueNumber(Score_yuzhi, T_NUM):
    T_count = 0
    great_Score_yuzhi_count = 0
    flag = False
    D_count = 0
    RealFace_Count = 0
    D_Quanzhong = 1

    fileNameList = codecs.open(filenames, mode='r',encoding='utf-8')

    for file in fileNameList:
        name = file.split("--")[0]
        score = file.split("：")[1].split("(")[0]
        DT = file.split("(")[1].split(")")[0]

        if (DT == "D"):
            great_Score_yuzhi_count = 0
            T_count = 0
            flag = False

            D_count += 1
            if (float(score) >= Score_yuzhi):
                great_Score_yuzhi_count += D_Quanzhong
            # out_score.write(name  + "," + score + "," + DT + "," + str(great_Score_yuzhi_count) +"\n")

        else:
            if (T_count < T_NUM):
                if great_Score_yuzhi_count >=DT_PASS_NUM:
                    continue
                if (float(score) >= Score_yuzhi):
                    great_Score_yuzhi_count += 1

            else:
                continue
            T_count += 1
        if (great_Score_yuzhi_count >= DT_PASS_NUM):
            RealFace_Count += 1
            continue
            # else:
            #     continue
                # out_score.write(name  + "," + score + "," + DT + "," + str(great_Score_yuzhi_count) +"\n")



    fileNameList.close()

    FailedFace_Count = D_count - RealFace_Count

    # print("D个数: " + str(D_count) + " " + "真脸个数: " + str(RealFace_Count) + " "  + "真脸占比%: " + str(RealFace_Count/D_count*100)  + " "  + "假脸占比%: " + str(FailedFace_Count/D_count*100) )

    print(str(round(Score_yuzhi, 1)) + " " + str(T_NUM) + " " + str(D_count) + " " + str(RealFace_Count) + " " + str(
        round(RealFace_Count / D_count * 100, 2)) + "% " + str(round(FailedFace_Count / D_count * 100, 2)) + "%")
    out_score.write(
        str(round(Score_yuzhi, 1)) + " " + str(T_NUM) + " " + str(D_count) + " " + str(RealFace_Count) + " " + str(
            round(RealFace_Count / D_count * 100, 2)) + "% " + str(round(FailedFace_Count / D_count * 100, 2)) + "%\n")
    # out_score.close()


for Yuzhi in range(5, 10):
    Yuzhi = Yuzhi * 0.1
    for i in range(1, T_CAIJI_NUM + 1):
        CheckTrueNumber(Yuzhi, i)

out_score.close()


