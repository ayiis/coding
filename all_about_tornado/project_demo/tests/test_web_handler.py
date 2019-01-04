import requests

site = "http://127.0.0.1:8888"


def print_result(response):

    print "url:", response.url
    print "status_code:", response.status_code
    print "text:", response.text
    print


def test_root():
    response = requests.get(site)
    print_result(response)


def test_js():
    response = requests.get("%s/js/1.js" % site)
    print_result(response)


def test_template():
    response = requests.get("%s/error" % site)
    print_result(response)


def test_403():
    response = requests.get("%s/js//mine/github/coding/all_about_tornado/project_demo/static/js/1.js" % site)
    print_result(response)


def test_403_2():
    response = requests.get("%s/js/../../../../../../../mine/github/coding/all_about_tornado/project_demo/static/js/1.js" % site)
    print_result(response)


if __name__ == "__main__":
    test_root()
    test_js()
    test_template()
    test_403()
    test_403_2()
