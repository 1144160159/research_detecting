from pathlib import Path
import zipfile

from finalize_atomic_patent import marked_visible_text


original = Path(
    r"F:\泉城实验室\二期\专利\流量大模型辅助的告警证据包生成与幻觉校验方法及系统\（2026.8.4初修稿）流量大模型辅助的告警证据包生成与幻觉校验方法及系统.docx"
)
target = Path(
    r"F:\泉城实验室\二期\论文\异常检测\_docx_red_audit\output\（2026.8.7黄色红字问题全量批注修订稿）流量大模型辅助的告警证据包生成与幻觉校验方法及系统.docx"
)

with zipfile.ZipFile(original) as archive:
    original_xml = archive.read("word/document.xml")
with zipfile.ZipFile(target) as archive:
    target_xml = archive.read("word/document.xml")

terms = ["相关度", "来源可信度", "新鲜度", "稀有度", "负证据强度", "来源类型编码"]
for mode in ["red", "yellow"]:
    left = marked_visible_text(original_xml, mode)
    right = marked_visible_text(target_xml, mode)
    print(mode, len(left), len(right), left == right)
    print([(term, left.count(term), right.count(term)) for term in terms])
