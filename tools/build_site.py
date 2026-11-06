"""Generate a buildless, bilingual academic website from publication metadata."""
import html
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPERS = json.loads((ROOT/'data/publications.json').read_text())

def esc(value):
    return html.escape(str(value), quote=True)

def bi(en, zh, block=False):
    tag = 'div' if block else 'span'
    return f'<{tag} data-lang="en">{en}</{tag}><{tag} data-lang="zh">{zh}</{tag}>'

def link(url, text, external=False, **attrs):
    extra = ' target="_blank" rel="noopener noreferrer"' if external else ''
    extra += ''.join(f' {key.rstrip("_").replace("_", "-")}="{esc(value)}"' for key,value in attrs.items())
    return f'<a href="{esc(url)}"{extra}>{text}</a>'

def authors(paper, full=False):
    result = []
    records = paper['authors']
    shown = records if full or len(records) <= 6 else records[:4]
    for author in shown:
        name = esc(author['given']+' '+author['family'])
        if author['given']=='Feng' and author['family']=='Li':
            name = f'<strong>{name}</strong>'
            if paper['role']=='corresponding':
                name += '<sup>*</sup>'
        result.append(name)
    return ', '.join(result) + (', et al.' if len(shown)<len(records) else '')

def bibtex(paper):
    names = ' and '.join(a['family']+', '+a['given'] for a in paper['authors'])
    fields = [('author', names), ('title', '{'+paper['title']+'}'), ('journal', paper['journal']), ('year', str(paper['year']))]
    for field in ('volume', 'number', 'pages'):
        if paper.get(field):
            fields.append((field, str(paper[field]).replace('-', '--') if field=='pages' else str(paper[field])))
    if paper.get('articleNumber') and not paper.get('pages'):
        fields.append(('pages', paper['articleNumber']))
    if paper.get('doi'):
        fields.append(('doi', paper['doi']))
    if paper.get('url'):
        fields.append(('url', paper['url']))
    if paper['accepted']:
        fields.append(('note', 'Accepted for publication'))
    return '@article{Li'+str(paper['year'])+'_'+paper['id']+',\n'+',\n'.join(f'  {key:<7} = {{{value}}}' for key,value in fields)+'\n}\n'

for p in PAPERS:
    p['bibtex'] = bibtex(p)
    (ROOT/'assets/bibtex'/f'{p["id"]}.bib').write_text(p['bibtex'])
(ROOT/'assets/bibtex/Feng-Li-publications.bib').write_text('\n'.join(p['bibtex'] for p in PAPERS))
(ROOT/'assets/publications.js').write_text('window.PUBLICATIONS = '+json.dumps(PAPERS, ensure_ascii=False).replace('<', '\\u003c')+';\n')

def publication(p, full=False):
    badges = ''
    if p['top']:
        badges += '<span class="badge top">'+bi('CAS Tier 1 · Top', '中科院一区 Top')+'</span>'
    if p['esi']:
        badges += '<span class="badge cited">'+bi('ESI Highly Cited', 'ESI 高被引')+'</span>'
    if p['accepted']:
        badges += '<span class="badge accepted">'+bi('Accepted', '已接收')+'</span>'
    role = bi('Corresponding author', '通讯作者') if p['role']=='corresponding' else bi('First author', '第一作者')
    title = link(p['url'],esc(p['title']),True) if p.get('url') else esc(p['title'])
    journal = f'<i>{esc(p["journal"])}</i>'
    issue = f', {esc(p["volume"])}' if p.get('volume') else ''
    if p.get('number'):
        issue += f'({esc(p["number"])})'
    if p.get('articleNumber'):
        issue += ': '+esc(p['articleNumber'])
    elif p.get('pages') and p.get('volume'):
        issue += ': '+esc(p['pages']).replace('-', '–')
    issue += f', {p["year"]}.'
    actions = (link(p['url'],bi('Paper ↗','论文 ↗'),True) if p.get('url') else '')
    actions += f'<button class="text-button" type="button" data-bibtex="{p["id"]}">BibTeX</button>'
    metrics = f'<span class="metrics">JCR {p["quartile"]} · IF {p["impact"]:.1f}</span>'
    return f'''<article class="publication" id="paper-{p['id']}" data-year="{p['year']}" data-search="{esc(p['title']+' '+p['journal']+' '+p['role']+' '+' '.join(p['tags']))}">
      <div class="publication-topline"><span class="role">{role}</span>{badges}<span class="publication-year">{p['year']}</span></div>
      <h3>{title}</h3><p class="authors">{authors(p,full)}</p>
      <p class="journal">{journal}{issue}</p><div class="publication-actions">{actions}{metrics}</div>
    </article>'''

def section(en, zh, content, id='', extra=''):
    return f'<section{(" id="+chr(34)+id+chr(34)) if id else ""}><div class="section-title"><h2>{bi(en,zh)}</h2>{extra}</div>{content}</section>'

def sidebar():
    return f'''<aside class="profile" aria-label="Researcher profile">
      <p class="institution-label">BEIHANG UNIVERSITY</p>
      <a class="portrait-link" href="index.html" aria-label="Feng Li homepage"><img class="portrait" src="assets/portrait.jpg" width="160" height="192" alt="Feng Li / 李峰"></a>
      <a class="profile-name" href="index.html">{bi('Feng Li <span class="name-zh">李峰</span>','李峰 <span class="name-zh">Feng Li</span>')}</a>
      <p class="profile-role">{bi('Assistant Research Fellow<br> Postdoctoral Researcher','助理研究员（博士后）')}</p>
      <p class="profile-affiliation">{bi('Hangzhou Innovation Institute<br> Beihang University','北京航空航天大学<br> 杭州创新研究院')}</p>
      <p class="location"><span aria-hidden="true">⌖</span> {bi('Hangzhou, China','中国 · 杭州')}</p>
      <div class="profile-links">
        {link('mailto:buaalf@buaa.edu.cn','<span aria-hidden="true">✉</span> buaalf@buaa.edu.cn')}
        {link('https://github.com/FonX1997','<span aria-hidden="true">↗</span> GitHub',True)}
      </div>
      <p class="profile-focus">{bi('AI & intelligent control<br>Quantum precision sensing','人工智能与智能控制<br>量子精密测量')}</p>
    </aside>'''

def shell(page, content):
    title = {'home':'Feng Li | Beihang University', 'research':'Research | Feng Li', 'publications':'Publications | Feng Li'}[page]
    style_version = hashlib.sha256((ROOT/'assets/style.css').read_bytes()).hexdigest()[:10]
    nav = ''.join(f'<a href="{filename}"'+(' aria-current="page"' if name==page else '')+'>'+bi(en,zh)+'</a>' for name,filename,en,zh in [('home','index.html','Home','首页'),('research','research.html','Research','科研'),('publications','publications.html','Publications','论文')])
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><meta name="description" content="Feng Li (李峰), Assistant Research Fellow and Postdoctoral Researcher at Beihang University Hangzhou Innovation Institute. AI, intelligent control, and quantum precision sensing.">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="assets/style.css?v={style_version}">
<script>try{{document.documentElement.lang=localStorage.getItem('feng-li-language')==='zh'?'zh':'en'}}catch{{}}</script>
<script defer src="assets/publications.js"></script><script defer src="assets/main.js"></script>
<meta property="og:title" content="Feng Li | Beihang University"><meta property="og:description" content="Artificial intelligence, intelligent control, and quantum precision sensing."><meta property="og:type" content="website"><meta property="og:image" content="https://fonx1997.github.io/assets/portrait.jpg">
<link rel="canonical" href="https://fonx1997.github.io/{'' if page=='home' else page+'.html'}"></head>
<body data-page="{page}"><a class="skip-link" href="#main">{bi('Skip to content','跳转到正文')}</a>
<div class="site-layout">{sidebar()}<div class="content-column"><header class="site-header"><nav aria-label="Main navigation">{nav}<a href="index.html#service">{bi('Service','学术服务')}</a></nav>
<div class="language-switch" role="group" aria-label="Website language"><button type="button" data-set-language="en" aria-label="Read in English">EN</button><span aria-hidden="true">/</span><button type="button" data-set-language="zh" aria-label="切换为中文">中文</button></div></header>
<main id="main">{content}</main><footer><span>© 2026 Feng Li</span><span>{bi('Last updated: November 2026','更新于 2026 年 11 月')}</span></footer></div></div>
<dialog id="bibtex-dialog" aria-labelledby="bibtex-title"><div class="dialog-heading"><h2 id="bibtex-title">BibTeX</h2><button id="close-bibtex" class="close-button" type="button" aria-label="Close BibTeX">×</button></div><p id="bibtex-paper-title"></p><pre id="bibtex-code" tabindex="0"></pre><div class="dialog-actions"><a id="download-bibtex" download>Download .bib</a><button class="primary-button" id="copy-bibtex" type="button">{bi('Copy BibTeX','复制 BibTeX')}</button></div><p id="copy-status" class="copy-status" role="status" aria-live="polite"></p></dialog>
</body></html>'''

INTRO_EN = '''I am an Assistant Research Fellow and Postdoctoral Researcher at <strong>Beihang University Hangzhou Innovation Institute</strong>, working with Academician <strong>Jiancheng Fang</strong> and Prof. <strong>Jianli Li</strong>. I received my Ph.D. in Electronic Information from Beihang University in 2025, supervised by Prof. <strong>Zhuo Wang</strong>.'''
INTRO_ZH = '''我现任<strong>北京航空航天大学杭州创新研究院助理研究员（博士后）</strong>，合作导师为<strong>房建成院士、李建利教授</strong>。2025 年获北京航空航天大学电子信息博士学位，博士生导师为<strong>王卓教授</strong>。'''
FOCUS_EN = '''My research connects <strong>artificial intelligence and intelligent control</strong> with <strong>atomic spin inertial sensing and quantum precision measurement</strong>. I develop physics-informed learning, reinforcement learning, adaptive dynamic programming, and digital-twin parallel control for system modeling, state estimation, and multiphysics disturbance compensation.'''
FOCUS_ZH = '''我的研究围绕<strong>人工智能与智能控制算法</strong>及其在<strong>原子自旋惯性测量、量子精密测量</strong>中的应用展开，重点研究物理约束深度学习、强化学习、自适应动态规划与数字孪生平行控制，开展系统建模、状态估计及多物理场耦合扰动补偿。'''

about = bi(f'<p>{INTRO_EN}</p><p>{FOCUS_EN}</p>',f'<p>{INTRO_ZH}</p><p>{FOCUS_ZH}</p>',True)
about += '<div class="research-keywords"><span>Physics-informed learning</span><span>Reinforcement learning</span><span>Parallel control</span><span>Quantum sensing</span></div>'
home = '''<section class="hero" aria-labelledby="hero-title"><div class="hero-copy"><p class="eyebrow"><span class="eyebrow-dot" aria-hidden="true"></span>'''+bi('AI · CONTROL · QUANTUM SENSING','人工智能 · 智能控制 · 量子传感')+'''</p><h1 id="hero-title">'''+bi('Learning & control.<br><em>Quantum precision.</em>','智能算法与控制<br><em>赋能量子精密测量</em>')+'''</h1><p class="hero-description">'''+bi('Connecting physical insight with learning algorithms for precision sensing systems.','融合物理模型与学习算法，研究精密测量系统的建模、估计与控制。')+'''</p><div class="hero-actions">'''+link('research.html',bi('Explore research <span aria-hidden="true">↗</span>','研究方向 <span aria-hidden="true">↗</span>'),class_='hero-primary')+link('publications.html',bi('Publications <span aria-hidden="true">→</span>','学术论文 <span aria-hidden="true">→</span>'),class_='hero-secondary')+'''</div></div><figure class="hero-art" aria-hidden="true"><img src="assets/research-orbit.svg" width="240" height="250" alt=""></figure></section>'''
home += section('About me','关于我',about,id='about')
home += section('News & updates','近期动态','''<ul class="news-list">
<li><time>2026</time><div>'''+bi('Awarded a <strong>Hangzhou Soft Science Research Project</strong> as Principal Investigator, studying innovation mechanisms for AI application scenarios.','主持获批<strong>杭州市软科学研究项目（一般项目）</strong>，研究面向“人工智能+”的杭州场景应用创新机制。')+'''</div></li>
<li><time>2026</time><div>'''+bi('Awarded the <strong>NSFC Young Scientists Fund (Category C)</strong>, Grant No. 62603043.','主持获批<strong>国家自然科学基金青年科学基金项目（C 类）</strong>，项目编号 62603043。')+'''</div></li>
<li><time>2025</time><div>'''+bi('Received the <strong>Outstanding Graduate</strong> award from Beihang University.','获北京航空航天大学<strong>“优秀毕业生”</strong>荣誉。')+'</div></li></ul>')
selected = ''.join(publication(p) for p in PAPERS if p['selected'])
home += section('Selected publications','代表性论文','<p class="section-note">'+bi('First- or corresponding-author work. Published and accepted articles are marked individually.','第一／通讯作者工作，已接收论文单独标注。')+'</p>'+selected, extra=link('publications.html',bi('All 14 papers →','全部 14 篇 →')))

education = '''<ol class="timeline">
<li><span class="timeline-date">2026 — '''+bi('present','至今')+'''</span><div><h3>'''+bi('Beihang University Hangzhou Innovation Institute','北京航空航天大学杭州创新研究院')+'''</h3><p>'''+bi('Assistant Research Fellow · Postdoctoral Researcher','助理研究员（博士后）')+'''</p></div></li>
<li><span class="timeline-date">2020 — 2025</span><div><h3>'''+bi('Beihang University','北京航空航天大学')+'''</h3><p>'''+bi('Ph.D. in Electronic Information','电子信息 · 工学博士')+'''</p></div></li>
<li><span class="timeline-date">2016 — 2020</span><div><h3>'''+bi('Shandong University of Science and Technology','山东科技大学')+'''</h3><p>'''+bi('B.Eng. in Measurement and Control Technology and Instrumentation','测控技术与仪器 · 工学学士')+'</p></div></li></ol>'
home += section('Education & appointments','教育及工作经历',education)

service = '''<ul class="service-list">
<li>'''+bi('Editorial Board Member','编委')+''', <i>International Journal of Intelligent Control and Systems</i> (IJICS).</li>
<li>'''+bi('Youth Editorial Board Member','青年编委')+''', <i>Advanced Information and Communication</i> (AIC).</li>
<li>'''+bi('Youth Editorial Board Member','青年编委')+''', <i>Embodied and Biomimetic Intelligence</i> (EBI).</li>
<li>'''+bi('Track Co-chair, 2026 IEEE 3rd International Symposium on AI and Cybersecurity (IEEE ISAICS 2026).','2026 年 IEEE 第三届人工智能与网络安全国际会议（IEEE ISAICS 2026）分论坛主席。')+'''</li>
<li>'''+bi('Member, Chinese Association of Automation; Committee Member, CAA Technical Committee on Adaptive Dynamic Programming and Reinforcement Learning (TC-ADPRL).','中国自动化学会会员；中国自动化学会自适应动态规划与强化学习（ADPRL）专业委员会委员。')+'''</li>
<li>'''+bi('Reviewer for <i>IEEE Transactions on Industrial Informatics</i>, <i>IEEE Transactions on Instrumentation and Measurement</i>, <i>ISA Transactions</i>, and conferences including CCC and IACOP.','担任 <i>IEEE Transactions on Industrial Informatics</i>、<i>IEEE Transactions on Instrumentation and Measurement</i>、<i>ISA Transactions</i> 等期刊及 CCC、IACOP 等会议审稿人。')+'</li></ul>'
home += section('Academic service','学术服务',service,id='service')
(ROOT/'index.html').write_text(shell('home',home))

research = '<p class="eyebrow">'+bi('RESEARCH','研究工作')+'</p><h1>'+bi('Learning, control & quantum sensing','人工智能、控制与量子传感')+'</h1><p class="page-intro">'+bi('Bringing physical models and learning algorithms together to understand and control precision sensing systems.','融合物理模型与学习算法，理解并控制精密测量系统。')+'</p>'
directions = [
('01','Artificial intelligence & intelligent control','人工智能与智能控制',
 'Physics-informed deep learning, reinforcement learning, adaptive dynamic programming, temporal neural networks, and neuro-fuzzy methods for system modeling, state estimation, and control under uncertainty.',
 '研究物理约束深度学习、强化学习、自适应动态规划、时序神经网络和神经模糊方法，面向不确定系统开展建模、状态估计与智能控制。',
 ['Physics-informed learning','Reinforcement learning','Adaptive dynamic programming'],['tfs','tim','tsmcs']),
('02','Digital twins & parallel control','数字孪生与平行控制',
 'Spatial and temporal digital twins connect physical knowledge with data-driven dynamics. Physics-informed neural networks and Transformers support parallel stabilization of local electron spin polarization in optically pumped hybrid spin ensembles.',
 '结合物理知识与数据驱动动力学构建空间、时间数字孪生，利用物理信息神经网络与 Transformer，研究光抽运混合自旋系综中局域电子自旋极化的平行稳定控制。',
 ['Parallel control','Digital twin','PINN','Transformer'],['scis','cep']),
('03','Atomic spin inertial sensing & quantum measurement','原子自旋惯性测量与量子精密测量',
 'Spin dynamics, electron spin polarization, magnetic-noise direction estimation, and coupled magnetic, optical, and thermal disturbances. Learning-assisted inference and calibration improve understanding and stability of atomic sensing systems.',
 '围绕自旋动力学、电子自旋极化、磁噪声方向估计及磁、光、热耦合扰动，研究学习辅助的在线反演、系统校准与协同补偿，提升原子传感系统的稳定性。',
 ['Spin dynamics','Uncertainty-aware inference','Calibration'],['fr','measurement','iscience'])]
for number,en,zh,desc_en,desc_zh,keywords,ids in directions:
    related = ''.join('<li>'+link('publications.html#paper-'+p['id'],esc(p['title']))+'</li>' for id in ids for p in PAPERS if p['id']==id)
    research += f'<section class="research-direction"><span class="direction-number">{number}</span><div><h2>{bi(en,zh)}</h2><p>{bi(desc_en,desc_zh)}</p><div class="research-keywords">'+''.join('<span>'+esc(k)+'</span>' for k in keywords)+'</div><p class="related-label">'+bi('Related work','相关论文')+'</p><ul class="related-work">'+related+'</ul></div></section>'
projects = [
('NSFC Young Scientists Fund (Category C)','国家自然科学基金青年科学基金项目（C 类）','Principal Investigator','主持',
 'Physics-Constrained Deep-Learning Compensation of Multiphysics Coupled Disturbances in Atomic Spin Inertial Measurement. Grant No. 62603043; CNY 300,000.',
 '基于物理约束深度学习的原子自旋惯性测量多物理场耦合扰动补偿研究。项目编号 62603043，资助经费 30 万元。'),
('2026 Hangzhou Soft Science Research Program','2026 年度杭州市软科学研究项目','Principal Investigator · General Project','主持 · 一般项目',
 'Research on Innovation Mechanisms for AI Application Scenarios in Hangzhou.', '面向“人工智能+”的杭州场景应用创新机制研究。'),
('STI 2030 Major Project: Quantum Communication and Quantum Computing','科技创新 2030“量子通信与量子计算机”重大项目','Participant · Prototype lead','参与 · 样机负责人',
 'Ultrahigh-sensitivity atomic spin inertial measurement and high-precision atomic gyroscope prototypes; system identification and closed-loop electron-spin control under multiphysics disturbances.',
 '超高灵敏原子自旋惯性测量装置与高精度原子陀螺仪原理验证样机；承担系统辨识、多物理场扰动下电子自旋闭环控制及指标攻关。'),
('National Key R&D Program of China','国家重点研发计划','Participant · Prototype lead','参与 · 样机负责人',
 'High-precision atomic spin gyroscope technology; active magnetic compensation, vapor-cell temperature control, automated testing, and embedded electronics.',
 '高精度原子自旋陀螺仪技术；承担主动磁场补偿、气室温度控制、自动化测试软件、嵌入式电路及指标攻关。')]
project_html = ''.join('<article class="project"><p class="role">'+bi(role_en,role_zh)+'</p><h3>'+bi(en,zh)+'</h3><p>'+bi(desc_en,desc_zh)+'</p></article>' for en,zh,role_en,role_zh,desc_en,desc_zh in projects)
research += section('Research projects','科研项目',project_html,id='projects')
(ROOT/'research.html').write_text(shell('research',research))

pubpage = '<p class="eyebrow">'+bi('PUBLICATIONS','学术论文')+'</p><h1>'+bi('Research publications','主要论著')+'</h1>'
pubpage += '<p class="page-intro">'+bi('14 first- or corresponding-author journal articles, including published and accepted work.','第一／通讯作者期刊论文 14 篇，含已发表及已接收论文。')+'</p>'
pubpage += '<div class="publication-summary"><span>'+bi('3 CAS Tier 1 Top papers','中科院一区 Top 论文 3 篇')+'</span><span>'+bi('1 ESI Highly Cited Paper','ESI 高被引论文 1 篇')+'</span></div>'
pubpage += '<div class="publication-toolbar"><label class="search-label"><span class="visually-hidden">'+bi('Search publications','检索论文')+'</span><input type="search" id="publication-search" placeholder="Search papers, journals, or topics…" autocomplete="off"></label><label><span class="visually-hidden">'+bi('Publication year','发表年份')+'</span><select id="publication-year"><option value="all">All years / 全部年份</option>'+''.join(f'<option value="{year}">{year}</option>' for year in sorted({p['year'] for p in PAPERS},reverse=True))+'</select></label></div>'
pubpage += '<div class="publication-list-info"><span id="publication-count" role="status">14 papers</span>'+link('assets/bibtex/Feng-Li-publications.bib',bi('Download all BibTeX ↓','下载全部 BibTeX ↓'),download='Feng-Li-publications.bib')+'</div>'
pubpage += '<div id="publication-list">'+''.join(publication(p,True) for p in PAPERS)+'</div><p id="no-results" hidden>'+bi('No matching papers. Try another term or year.','没有匹配的论文，请尝试其他关键词或年份。')+'</p>'
pubpage += '<p class="publication-footnote">'+bi('* Corresponding author. Acceptance status and journal indicators follow the current CV. The Applied Soft Computing article is listed under its 2027 issue year.','* 表示通讯作者。接收状态及期刊指标按现有简历列出；Applied Soft Computing 论文标注的是 2027 年卷期年份。')+'</p>'
(ROOT/'publications.html').write_text(shell('publications',pubpage))
print('Built three bilingual pages and 15 BibTeX files from 14 publication records.')
