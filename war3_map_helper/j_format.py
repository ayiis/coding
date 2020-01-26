import q
import re
import traceback


class Worker(object):
    """
        docstring for Worker
    """
    KEYWORD = r"^([\W]|\=\=|\w+|\s+|//|(?=^([^\.]*\.?[^\.]*)$)[0-9a-f\.]+)$"
    PAD = " " * 4
    PAD_PLUS = ("function", "globals", "if", "loop")
    PAD_TWICE = ("elseif", "else")
    PAD_MINUS = ("endfunction", "endglobals", "endif", "endloop")

    def __init__(self, arg):
        super(Worker, self).__init__()
        self.arg = arg
        self.fp = open(arg["file_path"], "r")
        self.pre_char = ""
        self.line_pad = 0
        self.pad_twice = False
        self.status = {
            "in_escape": False,
            "in_note": False,
            "in_string": False,
            "in_quote_string": False,
        }
        self.debug = False

    def read_next_word(self):
        """
            read \\w* and \\w{1}
            已知问题:
                self.pre_char 会影响下一次
        """
        buf, line_end = "", False
        while True:
            if self.pre_char:
                # has_pre = True
                char = self.pre_char
                self.pre_char = ""
            else:
                char = self.fp.read(1)

            if not char:
                raise Exception("EOF")

            if self.status["in_note"]:
                if char == "\n":
                    line_end = True
                    break
                else:
                    buf += char
                    continue
            else:
                pass

            if self.status["in_escape"]:
                self.status["in_escape"] = False
                buf += char
                continue
            else:
                pass

            if self.status["in_string"]:

                if char == "\\":
                    buf += char
                    self.status["in_escape"] = True
                    continue
                else:
                    pass

                if char == "\"":
                    self.status["in_string"] = False
                else:
                    pass

                buf += char
                continue
            else:
                pass

            if self.status["in_quote_string"]:
                if char == "\'":
                    self.status["in_quote_string"] = False
                else:
                    pass
                buf += char
                continue
            else:
                pass

            if char == "\n":
                line_end = True
                break
            else:
                pass

            if not buf:
                # something useless, but useful in split name and operator
                if char == " ":
                    buf += char
                    continue
                else:
                    pass

                if char == "\"":
                    buf += char
                    self.status["in_string"] = True
                    continue
                else:
                    pass

                if char == "\'":
                    buf += char
                    self.status["in_quote_string"] = True
                    continue
                else:
                    pass

                # handle the // note
                if char == "/":
                    if buf == "/":
                        buf += char
                        self.status["in_note"] = True
                        continue
                    else:
                        buf += char
                        break
                else:
                    pass
            else:
                pass

            tmp_buf = buf + char

            if not re.search(self.KEYWORD, tmp_buf, re.I):
                self.pre_char = char
                break
            else:
                buf = tmp_buf
                continue

        return buf, line_end

    def read_next_sentense(self):
        first_word = ""
        buf = ""
        while True:
            word, new_line = self.read_next_word()
            if not first_word:
                first_word = word

            if word.strip():
                # handle the strings
                if word[0] == "\"":
                    # self.fp_debug.write("-->||%s||<--\r\n" % word.replace("\n", "\\n"))
                    if len(word) > 300:
                        print("[string too long]:", word)

            buf += word

            if new_line:
                buf += "\n"
                break

        return buf, first_word

    def work(self):

        self.fp_write = open("%s.format.j" % self.arg["file_path"], "w")
        self.fp_debug = open("%s.debug.j" % self.arg["file_path"], "w")
        while True:
            try:
                sentense, first_word = self.read_next_sentense()
            except Exception as e:
                if str(e) == "EOF":
                    print("EOF!")
                    break

                print(traceback.format_exc())
                q.d()

            pad_this_line = ""

            if first_word.lower() in self.PAD_TWICE:
                pad_this_line = (self.line_pad - 1) * self.PAD
            else:
                if first_word.lower() in self.PAD_PLUS:
                    pad_this_line = self.line_pad * self.PAD
                    self.line_pad += 1
                elif first_word.lower() in self.PAD_MINUS:
                    pad_this_line = (self.line_pad - 1) * self.PAD
                    self.line_pad -= 1
                else:
                    pad_this_line = self.line_pad * self.PAD

            self.fp_write.write(pad_this_line)
            self.fp_write.write(sentense)

        self.fp_write.close()
        self.fp_debug.close()


def main(file_path):
    # function CreateAllDestructables takes nothing nothing, nothing nothing returns nothing
    worker = Worker({"file_path": file_path})
    worker.work()


if __name__ == "__main__":

    file_path = "/mine/github/coding/temp/data/2.j"
    # file_path = "/mine/github/coding/temp/data/1.j"
    # file_path = "/mine/war3work/Daemonic Sword ORPG 6.79/map/scripts/war3map.j"
    main(file_path)
