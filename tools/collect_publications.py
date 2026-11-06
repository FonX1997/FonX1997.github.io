"""Build publication data from the Chinese CV and DOI registration metadata."""
import concurrent.futures
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CV = ROOT.parent / '李峰的个人简历/李峰个人简历-北京航空航天大学.tex'
lines = CV.read_text().splitlines()
SPECS = [
    ('scis', 'Science China Information Sciences', 'Digital Twin-Enabled Parallel Stabilization of Electron Spin Polarization in Optically Pumped Hybrid Spin Ensembles', '10.1360/s11432-026-5050-y', 'first', ['parallel', 'quantum'], True),
    ('tsmcs', 'IEEE Transactions on Systems, Man, and Cybernetics: Systems', 'Machine Learning for Quantum Sensing Systems: An Integrated Survey of Preparation, Measurement, Inference, and Control', '10.1109/TSMC.2026.3744356', 'first', ['learning', 'quantum'], True),
    ('tfs', 'IEEE Transactions on Fuzzy Systems', 'Belief- and Risk-Driven Interval Type-2 Neuro-Fuzzy Output-Feedback Control for Partially Observed Stochastic Nonlinear Systems', '10.1109/TFUZZ.2026.3745076', 'first', ['learning', 'control'], True),
    ('fr', 'Fundamental Research', 'Stochastic Spin Modeling and ANEU-TCN for Directional Magnetic Noise Estimation in Atomic Comagnetometers', '10.1016/j.fmre.2026.05.018', 'first', ['learning', 'quantum'], True),
    ('asc', 'Applied Soft Computing', 'Basis-Adaptive Spectral Optimization via Learnable Graph Fourier Bases', '10.1016/j.asoc.2026.116607', 'first', ['learning'], False),
    ('tim', 'IEEE Transactions on Instrumentation and Measurement', 'Magnetic Field Compensation Control for Spin-Exchange Relaxation-Free Comagnetometer Using Reinforcement Learning', None, 'first', ['learning', 'control', 'quantum'], False),
    ('measurement', 'Measurement', 'Spin-Decoupling Calibration Method for Coil Constants in Optically Pumped Comagnetometers', '10.1016/j.measurement.2025.118819', 'first', ['quantum'], False),
    ('nld', 'Nonlinear Dynamics', 'Heating Temperature Control and Driving Voltage Nonlinear Feedback of LCVR for Stabilizing Laser Power in Atomic Spin Gyroscopes', None, 'first', ['control', 'quantum'], False),
    ('cep', 'Control Engineering Practice', 'Exponential Decay Adaptive Robust Control for Electron Spin Magnetization in Atomic Spin Gyroscopes', '10.1016/j.conengprac.2025.106405', 'first', ['control', 'quantum'], False),
    ('qst', 'Quantum Science and Technology', 'Certified Worst-Case Fidelity Bounds for Quantum Gates under Structured Uncertainty', None, 'corresponding', ['control', 'quantum'], False),
    ('iscience', 'iScience', 'In Situ Real-Time Measurement for Electron Spin Polarization in Atomic Spin Gyroscopes', '10.1016/j.isci.2025.111757', 'first', ['quantum'], True),
    ('ijss', 'International Journal of Systems Science', 'PI-FAS-CLO: Physics-Informed Fully Actuated System-Coordinate Learning Observer', None, 'first', ['learning', 'control'], False),
    ('aqt', 'Advanced Quantum Technologies', 'Effects of Stochastic Magnetic Noise on the SERF Co-Magnetometer', '10.1002/qute.202400040', 'first', ['quantum'], False),
    ('mst', 'Measurement Science and Technology', 'Physics-Informed Neural-Network Calibration of Pump–Probe Nonorthogonality in SERF Co-Magnetometers', '10.1088/1361-6501/ae9330', 'corresponding', ['learning', 'quantum'], False),
]
AUTHOR_OVERRIDES = {
    'scis': [('Feng', 'Li'), ('Zhuo', 'Wang'), ('Fei-Yue', 'Wang'), ('Ruigang', 'Wang'), ('Yonglin', 'Tian'), ('Haoying', 'Pang'), ('Jiahang', 'Li'), ('Qinglai', 'Wei'), ('Derong', 'Liu')],
    'fr': [('Feng', 'Li'), ('Zhuo', 'Wang'), ('Haoying', 'Pang'), ('Jiahang', 'Li'), ('Xinxiu', 'Zhou'), ('Xusheng', 'Lei'), ('Ruigang', 'Wang'), ('Wei', 'Quan')],
    'tsmcs': [('Feng', 'Li'), ('Zhuo', 'Wang'), ('Derong', 'Liu'), ('Kai', 'Wei'), ('Shan', 'Xue'), ('Ruigang', 'Wang'), ('Xinxiu', 'Zhou'), ('Haoying', 'Pang'), ('Qi', 'Zheng'), ('Jiahang', 'Li'), ('Xusheng', 'Lei'), ('Wei', 'Quan')],
    'qst': [('Jiaxin', 'Liu'), ('Feng', 'Li'), ('Zhuo', 'Wang'), ('Min', 'Zhang')],
    'ijss': [('Feng', 'Li'), ('Min', 'Zhang'), ('Zhuo', 'Wang'), ('Jiahang', 'Li'), ('Ruigang', 'Wang')],
}
def get(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'FengLiAcademicHomepage/1.0 (bibliographic metadata)'})
    with urllib.request.urlopen(request, timeout=14) as response:
        return json.load(response)['message']

def norm(text):
    return re.sub(r'[^a-z0-9]', '', text.lower())

def collect(spec):
    key, journal, title, doi, role, tags, selected = spec
    line = next(x for x in lines if '\\item ' in x and f'\\textit{{{journal}}}, ' in x)
    year = int(re.search(r'\\textit\{[^}]+\}, (\d{4})', line)[1])
    paper = dict(id=key, journal=journal, title=title, year=year, doi=doi, role=role,
                 tags=tags, selected=selected, accepted='已接收' in line,
                 impact=float(re.search(r'IF ([\d.]+)', line)[1]),
                 quartile=re.search(r'JCR (Q[1-4])', line)[1],
                 top='一区Top' in line or '一区 Top' in line, esi='ESI高被引' in line)
    metadata = None
    if key != 'scis' and not paper['accepted']:
        try:
            if doi:
                metadata = get('https://api.crossref.org/works/' + urllib.parse.quote(doi, safe='/'))
            else:
                query = urllib.parse.urlencode({'query.title': title, 'rows': 3})
                matches = get('https://api.crossref.org/works?' + query)['items']
                metadata = next((m for m in matches if norm(m.get('title', [''])[0]) == norm(title)), None)
            if metadata and norm(metadata.get('title', [''])[0]) != norm(title):
                raise ValueError('DOI resolves to another title')
        except Exception as error:
            paper['metadata_warning'] = str(error)
    if metadata:
        paper['doi'] = metadata['DOI']
        paper['authors'] = [{'given': a.get('given', ''), 'family': a.get('family', '')} for a in metadata.get('author', [])]
        for source, target in [('volume', 'volume'), ('issue', 'number'), ('page', 'pages'), ('article-number', 'articleNumber')]:
            if metadata.get(source):
                paper[target] = metadata[source]
        paper['source'] = 'https://api.crossref.org/works/' + metadata['DOI']
    if key in AUTHOR_OVERRIDES:
        paper['authors'] = [{'given': given, 'family': family} for given, family in AUTHOR_OVERRIDES[key]]
    if not paper.get('authors'):
        raw = line.split(title.replace('–', '--'))[0]
        raw = re.sub(r'\\(?:textbf|underline)\{([^{}]*)\}', r'\1', raw)
        raw = re.sub(r'\\(?:textbf|underline)\{([^{}]*)\}', r'\1', raw)
        raw = raw.replace('\\item ', '').replace('*', '').strip()
        paper['authorFallback'] = raw
    if key == 'scis':
        paper['source'] = 'https://www.sciengine.com/doi/10.1360/s11432-026-5050-y'
        paper['url'] = paper['source']
    elif paper['doi']:
        paper['url'] = 'https://doi.org/' + paper['doi']
    return paper

with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    papers = list(pool.map(collect, SPECS))
(ROOT/'data/publications.json').write_text(json.dumps(papers, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({'papers': len(papers), 'registered_metadata': sum('source' in p for p in papers),
                  'warnings': [{p['id']: p.get('metadata_warning', 'No complete registered author list')} for p in papers if not p.get('authors')]}, ensure_ascii=False))
