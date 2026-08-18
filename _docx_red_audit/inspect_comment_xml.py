from pathlib import Path
import zipfile,re
p=Path(r"F:\泉城实验室\二期\论文\异常检测\_docx_red_audit\output\（2026.8.7黄色红字问题全量批注修订稿）流量大模型辅助的告警证据包生成与幻觉校验方法及系统.docx")
with zipfile.ZipFile(p) as z:
    s=z.read('word/document.xml').decode('utf-8')
for cid in ['17','56','81','83','89']:
    m=re.search(r'<w:commentRangeStart w:id="'+cid+r'"/>',s)
    if m:
        print('\n---',cid,'---\n',s[max(0,m.start()-500):m.start()+900])
