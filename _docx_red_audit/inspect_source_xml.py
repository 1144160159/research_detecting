from pathlib import Path
import zipfile
p=Path(r"F:\泉城实验室\二期\专利\流量大模型辅助的告警证据包生成与幻觉校验方法及系统\（2026.8.4初修稿）流量大模型辅助的告警证据包生成与幻觉校验方法及系统.docx")
with zipfile.ZipFile(p) as z:s=z.read('word/document.xml').decode('utf-8')
for term in ['数值特征','相关度','轻量模板路径','检测解释收益']:
 i=s.find('>'+term+'<')
 print('\n---',term,'---\n',s[i-400:i+500])
