
ssh -NfL 0.0.0.0:27171:127.0.0.1:27017 super


github的有意思的玩法： https://www.zhihu.com/question/23498424/answer/1348093118

git init
git remote add origin https://github.com/ayiis/coding
git fetch --shallow-since=2099-12-31


rm .git -rf

git clone --filter=blob:none --no-checkout https://github.com/ayiis/coding 2


git clone --filter=tree:0 --no-checkout https://github.com/ayiis/coding 4

git clone --no-checkout https://github.com/ayiis/coding 3



git clone --filter=tree:0 https://github.com/ayiis/coding 5





git log > 1.txt

git clone --filter=blob:none --no-checkout https://github.com/ayiis/coding 9


git clone --filter=tree:0 --no-checkout https://github.com/ayiis/coding .
git fetch
git log --author="ayiis" --pretty=format:%cI

git log --pretty=oneline
git log --pretty=fuller
git log --pretty=format:%cr



# HOW TO

- configure: modify `conf/config.py`

- start server: `python3 app.py`

- run test: `python3 test_web_handler.py`


## When you need to add an empty directory to git

+ create a `.gitignore` file in that directory

```code
# ignore all file in this dir
*
# except this file
!.gitignore

```