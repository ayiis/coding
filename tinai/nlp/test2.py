import q
from pyhanlp import HanLP, JClass

with open("../test_data/1.txt", "r") as rf:
    text = rf.read()

text = text[:502]

# summary = HanLP.extractSummary(text, 10)

# print("summary:", summary)

def segment_with(text, jclass="com.hankcs.hanlp.tokenizer.NLPTokenizer"):
    tokenizer = JClass(jclass)
    return " ".join([term.word for term in tokenizer.segment(text)])

def crf(text):
    CRFLexicalAnalyzer = JClass("com.hankcs.hanlp.model.crf.CRFLexicalAnalyzer")
    analyzer = CRFLexicalAnalyzer()
    result = analyzer.analyze(text)
    return " ".join([a.value for a in result.iterator()])

def nshort(text):
    NShortSegment = JClass("com.hankcs.hanlp.seg.NShort.NShortSegment")
    Segment = JClass("com.hankcs.hanlp.seg.Segment")
    ViterbiSegment = JClass("com.hankcs.hanlp.seg.Viterbi.ViterbiSegment")

    nshort_segment = NShortSegment().enableCustomDictionary(False).enablePlaceRecognize(True).enableOrganizationRecognize(True)
    # shortest_segment = ViterbiSegment().enableCustomDictionary(False).enablePlaceRecognize(True).enableOrganizationRecognize(True)

    # print("N-最短分词：{} \n最短路分词：{}".format(nshort_segment.seg(text), shortest_segment.seg(text)))
    result = nshort_segment.seg(text)
    # q.d()
    return " ".join([a.word for a in result.iterator()])


# print("segment_with 标准分词 StandardTokenizer:", segment_with(text, "com.hankcs.hanlp.tokenizer.StandardTokenizer"))
# print("[]\r\n")

print("segment_with NLP分词 NLPTokenizer:", segment_with(text, "com.hankcs.hanlp.tokenizer.NLPTokenizer"))
print("[]\r\n")

# print("segment_with 索引分词 IndexTokenizer:", segment_with(text, "com.hankcs.hanlp.tokenizer.IndexTokenizer"))
# print("[]\r\n")

# print("segment_with N-最短路径分词 NShortSegment:", nshort(text))
# print("[]\r\n")

# print("segment_with CRF分词 CRFLexicalAnalyzer:", crf(text))
# print("[]\r\n")

