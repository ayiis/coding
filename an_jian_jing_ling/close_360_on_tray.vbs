'
' 按键精灵脚本，从托盘区域退出 360安全卫士
' 使用 Plugin.File 时遇到很多问题，所以用 ADODB.Stream 处理文件
'

' 点击右下角 关闭360安全卫士
' 使用 win + b 快捷键，点开托盘
KeyDown "Win", 1
Delay 20
KeyPress "B", 1
Delay 20
KeyUp "Win", 1
Delay 200
KeyPress "space", 1
Delay 200

' 非常规方式，将鼠标移动到右下角托盘区域
KeyPress "up", 1
Delay 200
KeyPress "up", 1
Delay 200
KeyPress "Right Mouse", 1
Delay 200
' 按 1 次 alt 键，隐藏右键菜单
KeyPress "Alt", 1
Delay 200

Dim kx1, ky1, kx2, ky2, mx, my

' 鼠标目前在最后一个图标，获取鼠标当前的位置
GetCursorPos mx, my
MoveTo mx, my + 40
Delay 200

' 下面开始计算托盘的有效区域
mx = mx + 16
my = my + 16

kx1 = mx
Do
    kx1 = kx1 - 1
    IfColor kx1, my, "FFFFFF", 1 Then     ' 到达托盘边缘
        Exit Do
    End If
Loop
kx1 = kx1 + 8

ky1 = my
Do
    ky1 = ky1 - 1
    IfColor mx, ky1, "FFFFFF", 1 Then     ' 到达托盘边缘
        Exit Do
    End If
Loop
ky1 = ky1 + 8

kx2 = mx
Do
    kx2 = kx2 + 1
    IfColor kx2, my, "FFFFFF", 1 Then     ' 到达托盘边缘
        Exit Do
    End If
Loop
kx2 = kx2 - 8

ky2 = my
Do
    ky2 = ky2 + 1
    IfColor mx, ky2, "FFFFFF", 1 Then     ' 到达托盘边缘
        Exit Do
    End If
Loop
ky2 = ky2 - 8

' 从托盘的有效区域里面，寻找 360tray 的图标（预先截图保存）
Dim intX, intY
FindPic kx1, ky1, kx2, ky2, "Attachment:\360icon.bmp", 0.8, intX, intY

' 如果返回的坐标大于0，那么就说明找到了
If intX > 0 And intY > 0 Then
    MoveTo intX + 10, intY + 10
    Delay 200
    RightClick 1
    Delay 200
    MoveTo intX - 40, intY - 20
    Delay 200
    LeftClick 1
    Delay 200

    ' 一般情况下，弹出框的位置位于屏幕正中央，这个可以预先设置好
    MoveTo 1127, 683
    Delay 200
    LeftClick 1
    Delay 200
else
    TracePrint "没有在托盘找到 360 的图标"

End If
