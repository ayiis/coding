import q
import re


class Worker(object):
    """
        docstring for Worker
    """
    KEYWORD = r"^(\w+|//|(?=^([^\.]*\.?[^\.]*)$)[0-9a-f]+)$"
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
        }

    def read_next_word(self):
        """
            read \\w* and \\w{1}
        """
        buf, line_end = self.pre_char, False
        self.pre_char = ""
        while True:
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

            if self.status["in_escape"]:
                self.status["in_escape"] = False
                buf += char
                continue

            if self.status["in_string"]:
                if char == "\"":
                    self.status["in_string"] = False
                else:
                    pass
                buf += char
                continue

            if char == "\n":
                line_end = True
                break

            if char == "\"":
                buf += char
                self.status["in_string"] = True
                continue
            if char == "\\":
                buf += char
                self.status["in_escape"] = False
                continue

            # handle the // note
            if char == "/":
                if buf == "/":
                    buf += char
                    self.status["in_note"] = True
                    continue
                else:
                    self.pre_char = char
                    break

            tmp_buf = buf + char
            if not re.search(self.KEYWORD, tmp_buf, re.I):
                self.pre_char = char
                break
            else:
                buf = tmp_buf
                continue

        # q.d()
        return buf, line_end

    def read_next_sentense(self):
        first_word = ""
        buf = ""
        while True:
            word, new_line = self.read_next_word()
            if not first_word:
                first_word = word
                # print("first_word:", first_word)

            # print(word)
            # if new_line:
            #     print()

            buf += word

            if new_line:
                # print()
                # self.fp_write.write("\n")
                buf += "\n"
                break

        # if "if" in buf:
        #     q.d()

        return buf, first_word

    def work(self):

        self.fp_write = open("%s.format.j" % self.arg["file_path"], "w")
        # for i in range(999):
        while True:
            try:
                sentense, first_word = self.read_next_sentense()
            except Exception:
                break

            pad_this_line = ""

            if first_word.lower() in self.PAD_TWICE:
                pad_this_line = (self.line_pad - 1) * self.PAD
            else:
                # if first_word.lower().strip() == "if":
                #     q.d()
                if first_word.lower() in self.PAD_PLUS:
                    # print("-->first_word", first_word.lower())
                    pad_this_line = self.line_pad * self.PAD
                    self.line_pad += 1
                elif first_word.lower() in self.PAD_MINUS:
                    pad_this_line = (self.line_pad - 1) * self.PAD
                    self.line_pad -= 1
                else:
                    pad_this_line = self.line_pad * self.PAD

            self.fp_write.write(pad_this_line)
            self.fp_write.write(sentense)

            # if first_word == "endfunction":
            #     self.fp_write.write("\n")

            # q.d()

        self.fp_write.close()


def main(file_path):
    # function CreateAllDestructables takes nothing nothing, nothing nothing returns nothing
    worker = Worker({"file_path": file_path})
    worker.work()


if __name__ == "__main__":

    # file_path = "./data/2.j"
    file_path = "./data/1.j"
    main(file_path)
