from pyquery import PyQuery
import q
"""
import traceback
traceback.format_exc()
print("".join(traceback.format_stack()[:-7]))
"""

e = PyQuery("""
<div>
    <div class="base">
        <div class="first">
            <span class="c11">1.1</span>
            <span class="c12">1.2</span>
            <span class="c13">1.3</span>
        </div>
        <div class="middle">
            <span class="c21">2.1</span>
            <span class="c22">2.2</span>
            <span class="c23">2.3</span>
        </div>
        <div class="last">
            <span class="c31">3.1</span>
            <span class="c32">3.2</span>
            <span class="c33">3.3</span>
        </div>
    </div>
    <div class="extra">
        <div class="first">
            <div class="c11">1.1</div>
            <div class="c12">1.2</div>
            <div class="c13">1.3</div>
        </div>
        <div class="middle">
            <div class="c21">2.1</div>
            <div class="c22">2.2</div>
            <div class="c23">2.3</div>
        </div>
        <div class="last">
            <div class="c31">3.1</div>
            <div class="c32">3.2</div>
            <div class="c33">3.3</div>
        </div>
    </div>
</div>
""")
# e.find(".extra").find("div:eq(0)")
q.d()
exit(1)

e.find(".base")
e.find(".base").find("div:eq(0)")
e.find(".base").find("div:eq(1)")

e.find(".base")("div:eq(0)")
e.find(".base")("div:eq(1)")

e.find(".base div:eq(0)")
e.find(".base div:eq(1)")

exit()

e.find(".extra")
e.find(".extra").find("div:eq(0)")
e.find(".extra").find("div:eq(1)")

e.find(".extra")("div:eq(0)")
e.find(".extra")("div:eq(1)")
e.find(".extra")("div:eq(2)")
e.find(".extra")("div:eq(3)")

e.find(".extra").find("div:eq(2)")
e.find(".extra").find("div:eq(3)")
e.find(".extra").find("div:eq(4)")

e.find(".extra div:eq(0)")
e.find(".extra div:eq(1)")

