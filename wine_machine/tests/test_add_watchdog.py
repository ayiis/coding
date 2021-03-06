import requests
import q
import json

website = "http://127.0.0.1:60001/api/watchdog/add"

itemid_list = ["100004571288", "43871571802", "44066755622", "100004571284", "6297458", "883590", "37440870409", "3028550", "2156288", "4311591", "32466384930", "32366918253", "4738339", "45146765595", "45123352721", "44887833654", "1178758", "42907094947", "3176328", "8773619", "7252399", "31894659391", "27026211189", "30944374131", "1480495155", "27800176244", "43287897060", "11151078273", "30520938198", "4508158", "41380832868", "28034401262", "100002040039", "41220108504", "40409428103", "8703798", "6888690", "7102615", "100001648875", "100002219716", "8759446", "100001648715", "4214058", "30892181105", "100001673630", "7038944", "4491749", "6888702", "7102639", "331329", "631418", "331326", "285997", "4491751", "332125", "4279786", "501616"]
headers = {
    "content-type": "application/json; charset=UTF-8",
}


def test_add():
    req_data = {
        "site": "jingdong",
        "itemid_list": itemid_list,
    }
    req_data = json.dumps(req_data)
    result = requests.post(website, headers=headers, data=req_data)

    print(result)
    print(result.text)


def test():
    test_add()


if __name__ == "__main__":
    test()
