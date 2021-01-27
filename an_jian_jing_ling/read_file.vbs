'
' 按键精灵脚本，读取目标 txt 文件，逐行逐字进行处理
' 使用 Plugin.File 时遇到很多问题，所以用 ADODB.Stream 处理文件
'

' 启动按键精灵后，需要切换到目标的窗口 (激活目标窗口 - 否则第一个字符输入失败)
Delay 3000
file_path = "F:\\1.txt"     ' 目标 txt 文件

Dim objStream, strData
Set objStream = CreateObject("ADODB.Stream")
objStream.CharSet = "utf-8"
objStream.Open
objStream.LoadFromFile(file_path)
strData = objStream.ReadText()
objStream.Close
Set objStream = Nothing

dim line_list
line_list = Split(strData, vbCrLf)  ' 常量 vbCrLf == \r\n
for i = 0 to UBound(line_list)      ' 逐行读取，从0开始

    line = line_list(i)

    ' 在这里处理对应的每 1 行
    ' SayString line

    For j = 1 To len(line) step 1   ' 逐字读取，从1开始
        cs = mid(line, j, 1)

        ' 在这里处理对应的每 1 个字符
        SayString cs

        ' 每个字符处理完之后，等待 200 毫秒
        Delay 200
    Next

    KeyPress "Enter", 1
Next

MessageBox "脚本已执行完毕！"
