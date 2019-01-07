import requests

site = "http://127.0.0.1:8888"


def print_result(response):

    print("[%s] %s\t%s" % (response.status_code, len(response.text), response.url))
    print("text:", response.text)
    print()


def test_root():
    response = requests.get(site)
    print_result(response)


def test_js():
    response = requests.get("%s/js/1.js" % site)
    print_result(response)


def test_css():
    response = requests.get("%s/css/1.css" % site)
    print_result(response)


def test_img():
    response = requests.get("%s/img/1.gif" % site)
    print_result(response)


def test_template():
    response = requests.get("%s/error" % site)
    print_result(response)


def test_get_403():
    response = requests.get("%s/js//mine/github/coding/all_about_tornado/project_demo/static/js/1.js" % site)
    print_result(response)


def test_get_403_2():
    response = requests.get("%s/js/../../../../../../../mine/github/coding/all_about_tornado/project_demo/static/js/1.js" % site)
    print_result(response)


def test_get_403_3():
    response = requests.get("%s/js/../../static/js/1.js" % site)
    print_result(response)


def test_get_403_4():
    response = requests.get("%s/js/../app.py" % site)
    print_result(response)


def test_post_404():
    response = requests.post("%s/api/404?ofsf" % site)
    print_result(response)


def test_post_200_bad_heaeder():
    response = requests.post("%s/api/200" % site)
    print_result(response)


def test_post_200_invalid_json():
    response = requests.post(
        "%s/api/200" % site,
        headers={
            "Content-Type": "application/json; charset=UTF-8",
        },
        data="some nothing text"
    )
    print_result(response)


def test_post_200_ok():
    import json
    response = requests.post(
        "%s/api/200" % site,
        headers={
            "Content-Type": "application/json; charset=UTF-8",
        },
        data=json.dumps({"greeting": "by test"})
    )
    print_result(response)


def test_post_get_sequence_name():
    import json
    response = requests.post(
        "%s/api/get_sequence_name" % site,
        headers={
            "Content-Type": "application/json; charset=UTF-8",
        },
        data=json.dumps({"greeting": "by test"})
    )
    print_result(response)


def test_post_500_ok():
    import json
    response = requests.post(
        "%s/api/500" % site,
        headers={
            "Content-Type": "application/json; charset=UTF-8",
        },
        data=json.dumps({"greeting": "by test"})
    )
    print_result(response)


if __name__ == "__main__":

    test_root()
    test_js()
    test_css()
    test_img()
    test_template()

    test_get_403()
    test_get_403_2()
    test_get_403_3()
    test_get_403_4()

    test_post_404()
    test_post_200_bad_heaeder()
    test_post_200_invalid_json()
    test_post_200_ok()
    test_post_get_sequence_name()

    test_post_500_ok()
