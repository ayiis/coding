# -*-encoding:utf-8-*-
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
# https://88cp.me/tpl/commonFile/images/gdpic/macpic.php?SR=d590fc460740e24e7af4
# https://authcode.jd.com/verify/image?a=1&acid=da0f7e0d-38fe-4b69-bc60-2816bad7b483&uid=da0f7e0d-38fe-4b69-bc60-2816bad7b483&yys=1527498822352


def main():
    image = Image.open("./img/3691.png")
    #image.show() #打开图片1.jpg
    text = pytesseract.image_to_string(image) #使用简体中文解析图片
    # text = pytesseract.image_to_string(image, lang='chi_sim') #使用简体中文解析图片
    print(text)


def main2():
    pass

if __name__ == '__main__':
    main()
