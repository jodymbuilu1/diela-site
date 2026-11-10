"""Build the public, static ELIKYAPEDIA edition from reviewed article records."""
import json, re, html
from pathlib import Path
from collections import Counter

HERE = Path(__file__).resolve().parent
ORIGIN = 'https://diela.org/elikyapedia/'
DATE = '10 novembre 2026'
DOMAINS = {
 'politique': ('Politique', 'L’État, les institutions et la vie publique', 'Justice, démocratie, administration, défense et relations internationales.'),
 'economie': ('Économie', 'Les ressources, la production et les échanges', 'Finances publiques, énergie, agriculture, mines et système monétaire.'),
 'social': ('Social', 'Les savoirs, les services et la vie collective', 'Santé, éducation, protection sociale, culture et recherche.')
}
def esc(s): return html.escape(str(s), quote=True)
def inline(s):
    s=esc(s)
    s=re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s=re.sub(r'\*(.+?)\*', r'<em>\1</em>', s)
    return re.sub(r'\[(\d+)\]',lambda m:f'<sup><a href="#source-{m[1]}" aria-label="Référence {m[1]}">[{m[1]}]</a></sup>',s)
def render_block(text):
    if text.startswith('### '): return '<h3>'+inline(text[4:])+'</h3>'
    if text.startswith('|'):
        rows=[[cell.strip() for cell in row.strip().strip('|').split('|')] for row in text.splitlines() if row.strip()]
        assert len(rows)>2 and all(len(row)==len(rows[0]) for row in rows)
        head='<thead><tr>'+''.join('<th scope="col">'+inline(c)+'</th>' for c in rows[0])+'</tr></thead>'
        body='<tbody>'+''.join('<tr>'+''.join('<td>'+inline(c)+'</td>' for c in row)+'</tr>' for row in rows[2:])+'</tbody>'
        return '<div class="table-wrap" role="region" aria-label="Tableau de données" tabindex="0"><table>'+head+body+'</table></div>'
    if text.startswith('- '): return '<ul>'+''.join('<li>'+inline(line[2:])+'</li>' for line in text.splitlines() if line.startswith('- '))+'</ul>'
    return '<p>'+inline(text)+'</p>'
def figure_html(f):
    return f'<figure class="documented-map article-figure"><a href="{esc(f["src"])}" aria-label="Ouvrir le graphique en grand"><img src="{esc(f["src"])}" alt="{esc(f["alt"])}" width="{int(f["width"])}" height="{int(f["height"])}" loading="lazy"></a><figcaption>{inline(f["caption"])}<small>{esc(f["credit"])}</small><a href="{esc(f["sourceUrl"])}" rel="noopener">Consulter les données sources →</a></figcaption></figure>'
def section_html(section,i):
    content=''
    for j,paragraph in enumerate(section['paragraphs']):
        content+=render_block(paragraph)
        if section.get('figure',{}).get('afterParagraph')==j: content+=figure_html(section['figure'])
    return f'<section id="section-{i}"><h2>{esc(section["title"])}</h2>'+content+'</section>'
def section_markdown(section):
    blocks=[]
    for j,paragraph in enumerate(section['paragraphs']):
        blocks.append(paragraph)
        if section.get('figure',{}).get('afterParagraph')==j:
            f=section['figure']; blocks.append(f'![{f["alt"]}]({ORIGIN.rstrip("/").replace("/elikyapedia", "")}{f["src"]})\n\n{f["caption"]}\n\n{f["credit"]}\n\nSource : {f["sourceUrl"]}')
    return '## '+section['title']+'\n\n'+'\n\n'.join(blocks)
def write(path,content):
    p=HERE/path; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(content)
def shell(title,description,body,path='',domain=None,article=False):
    prefix='../' * (len(Path(path).parts)-1) if path else ''
    # All links are rooted to the existing public DIELA site.
    nav=''.join(f'<a href="/elikyapedia/{k}/"'+(' aria-current="page"' if domain==k else '')+f'>{v[0]}</a>' for k,v in DOMAINS.items())
    return f'''<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} — ELIKYAPEDIA</title><meta name="description" content="{esc(description)}"><meta name="theme-color" content="#faf9f6"><link rel="canonical" href="{ORIGIN}{path if path!='index.html' else ''}"><link rel="icon" href="/assets/diela-logo.png"><link rel="stylesheet" href="/elikyapedia/edition.css"></head>
<body><a class="skip" href="#contenu">Aller au contenu</a><header class="masthead"><div class="mast-inner"><a class="brand" href="/elikyapedia/">ELIKYAPEDIA<span>Une encyclopédie de la République démocratique du Congo</span></a><a class="diela" href="/explorer.html">DIELA →</a></div><nav class="domain-nav" aria-label="Domaines de connaissances"><div><a href="/elikyapedia/"{(' aria-current="page"' if not domain else '')}>Tous les sujets</a>{nav}<a class="nav-method" href="/elikyapedia/methode.html">Méthode</a></div></nav></header>
{body}<footer class="footer"><div><a href="/elikyapedia/">ELIKYAPEDIA</a><p>Connaissances générales sur la RDC. Une publication DIELA, indépendante de Wikipédia.</p></div><div><a href="/elikyapedia/sources.html">Sources & documentation</a><a href="/elikyapedia/methode.html">Méthode éditoriale</a><span>Édition du {DATE}</span></div></footer><script src="/elikyapedia/edition.js" defer></script></body></html>'''

def article_page(a,articles):
    dom=DOMAINS[a['domain']][0]; slug=a['slug']
    article_date=a.get('date','9 novembre 2026'); version=a.get('version','2.0')
    label=' · '.join([dom]+[a[k] for k in ('category','kind') if a.get(k)]) if a.get('kind') else dom+' · Article de référence'
    intro=f'<p class="lead">{inline(a["intro"])}</p>' if a.get('intro') else ''
    period=f' · Période étudiée : {esc(a["period"])}' if a.get('period') else ''
    sections=a['sections']
    nwords=len(re.findall(r'\S+', ' '.join(p for s in sections for p in s['paragraphs'])))
    toc='<a href="#en-bref">En bref</a><a href="#points-cles">10 points clés</a>'+''.join(f'<a href="#section-{i}">{esc(s["title"])}</a>' for i,s in enumerate(sections,1))+'<a href="#references">Sources & références</a>'
    figure=''
    if a.get('map'):
        m=a['map']
        toc+='<a href="#carte">Lire la carte</a>'
        figure=f'<section id="carte" class="map-section"><h2>Lire la géographie du conflit</h2><p>{inline(m["context"])}</p><figure class="documented-map"><a href="{esc(m["src"])}" aria-label="Ouvrir la carte en grand"><img src="{esc(m["src"])}" alt="{esc(m["alt"])}" width="720" height="950" loading="lazy"></a><figcaption>{esc(m["caption"])}<small>{esc(m["credit"])}</small></figcaption></figure><p>{inline(m["reading"])}</p><p><a href="{esc(m["sourceUrl"])}" rel="noopener">Consulter l’analyse et la carte de juillet 2025 →</a> · <a href="{esc(m["originalUrl"])}" rel="noopener">Ouvrir la figure originale</a></p></section>'
    points=''.join(f'<li>{inline(p)}</li>' for p in a['keyPoints'])
    prose=''.join(section_html(s,i) for i,s in enumerate(sections,1))
    refs=''.join(f'<li id="source-{i}"><a href="{esc(s["url"])}" rel="noopener">{esc(s["title"])}</a><p>{esc(s.get("note",""))}</p></li>' for i,s in enumerate(a['sources'],1))
    corpus=''.join(f'<li>{esc(s["title"])}'+(f' — {esc(s.get("period",""))}' if s.get('period') else '')+'</li>' for s in a.get('corpus',[]))
    related=''.join(f'<a href="/elikyapedia/articles/{b["slug"]}/">{esc(b["title"])}</a>' for b in articles if (b['domain']==a['domain'] or b['slug'] in a.get('relatedSlugs',[])) and b['slug']!=slug)
    documentation=f'''<details><summary>Documentation de travail utilisée</summary><p>Les rapports énumérés ci-dessous appartiennent au corpus de travail « État des lieux de la RDC » : un ensemble de recherches thématiques réunies par DIELA pour préparer les articles et repérer leurs sources. Leur présence dans ce corpus ne vaut pas validation indépendante. Les références publiques de cet article figurent ci-dessus ; les notes internes et données personnelles ne sont pas reproduites. <a href="/elikyapedia/methode.html#corpus">Comprendre le rôle du corpus et la méthode de rédaction.</a></p><ul>{corpus}</ul></details>''' if a.get('corpus') else ''
    related_heading='Lire aussi' if a.get('relatedSlugs') else 'Lire aussi dans '+dom
    body=f'''<main id="contenu" class="article-layout"><aside class="contents"><p>Dans cet article</p><nav aria-label="Sommaire de l’article">{toc}</nav></aside><article class="article"><div class="breadcrumbs"><a href="/elikyapedia/">Encyclopédie</a><span>/</span><a href="/elikyapedia/{a['domain']}/">{dom}</a></div><header class="article-header"><p class="eyebrow">{esc(label)}</p><h1>{esc(a['title'])}</h1>{intro}<p class="article-meta">Mis à jour le {article_date}{period} · {max(1,round(nwords/220))} min de lecture · <a href="#references">Sources</a></p><div class="reading-nav"><a href="#en-bref">En bref</a><a href="#article-detaille">Article détaillé</a><button type="button" data-print>Imprimer / PDF</button></div></header>
<section id="en-bref" class="abstract"><div class="section-kicker">EN BREF <span>100 mots</span></div><p>{inline(a['summary'])}</p></section><section id="points-cles" class="keypoints"><h2>Dix points clés</h2><ol>{points}</ol></section>
<div id="article-detaille" class="article-divider"><span>COMPRENDRE EN DÉTAIL</span><span>{str(nwords).replace(',', ' ')} mots</span></div><div class="prose">{figure}{prose}</div><section id="references" class="references"><h2>Sources & références</h2><p class="scope">{esc(a.get('scope',''))}</p><ol>{refs}</ol>{documentation}<p class="revision">Version {esc(version)} · {article_date} · <a href="/elikyapedia/methode.html">Politique de sources et de corrections</a> · <a download href="/elikyapedia/textes/{slug}.md">Télécharger le texte</a></p></section><section class="related"><h2>{esc(related_heading)}</h2><div>{related}</div></section></article></main>'''
    write(Path('articles')/slug/'index.html', shell(a['title'],a['summary'],body,f'articles/{slug}/',a['domain'],True))
    text=f'# {a["title"]}\n\nELIKYAPEDIA · DIELA · {article_date}\n\n## En bref\n\n{a["summary"]}\n\n## Dix points clés\n\n'+ '\n'.join(f'{i}. {p}' for i,p in enumerate(a['keyPoints'],1))+'\n\n'
    text+='\n\n'.join(section_markdown(s) for s in sections)
    if a.get('map'):
        m=a['map']
        text+='\n\n## Carte et repères géographiques\n\n'+m['context']+'\n\n'+m['caption']+'\n\n'+m['credit']+'\n\n'+m['reading']+'\n\nCarte ELIKYAPEDIA : '+ORIGIN+'cartes/adf-reperes.svg'+'\nCarte originale CTP : '+m['originalUrl']
    text+='\n\n## Sources\n\n'+'\n\n'.join(f'[{i}] {s["title"]} — {s["url"]}\n{s.get("note","")}' for i,s in enumerate(a['sources'],1))
    write(Path('textes')/(slug+'.md'),text+'\n')

def card(a):
    search=' '.join([a['title'],a['summary'],*a['keyPoints']])
    return f'<article class="article-card" data-domain="{a["domain"]}" data-search="{esc(search)}"><p class="eyebrow">{DOMAINS[a["domain"]][0]}</p><h3><a href="/elikyapedia/articles/{a["slug"]}/">{esc(a["title"])}</a></h3><p>{esc(a["summary"].split(". ")[0])}.</p><a class="read-link" href="/elikyapedia/articles/{a["slug"]}/">Lire l’article <span aria-hidden="true">→</span></a></article>'

def catalog(articles,domain=None):
    subset=[a for a in articles if domain is None or a['domain']==domain]
    name=DOMAINS[domain][0] if domain else 'Comprendre la RDC.'
    subtitle=DOMAINS[domain][1] if domain else 'Un pays. Trois regards. Des connaissances reliées.'
    desc=DOMAINS[domain][2] if domain else 'Institutions, économie, société : une encyclopédie pour explorer la République démocratique du Congo, du résumé essentiel à l’article de fond.'
    if domain:
        top=f'<div class="breadcrumbs"><a href="/elikyapedia/">Encyclopédie</a><span>/</span>{name}</div>'
        portals=''
    else:
        top='<p class="eyebrow">RÉPUBLIQUE DÉMOCRATIQUE DU CONGO</p>'
        portals='<section class="portals" aria-label="Explorer par domaine">'+''.join(f'<a href="/elikyapedia/{k}/"><span class="portal-num">0{i}</span><h2>{v[0]} <span>→</span></h2><p>{v[2]}</p><span class="portal-count">{sum(a["domain"]==k for a in articles)} articles de référence</span></a>' for i,(k,v) in enumerate(DOMAINS.items(),1))+'</section>'
    body=f'''<main id="contenu" class="catalog"><header class="hero">{top}<h1>{name}</h1><p class="hero-subtitle">{subtitle}</p><p class="hero-description">{desc}</p><p class="edition-note">{len(subset)} articles · Résumés en 100 mots · Dix points clés · Articles détaillés et sourcés</p></header>{portals}<section class="article-index"><div class="index-heading"><h2>{'Tous les articles' if not domain else 'Les articles du domaine'}</h2><span data-result-count>{len(subset)} articles</span></div><form class="search" role="search" onsubmit="return false"><label for="article-search">Rechercher un sujet</label><div><input id="article-search" type="search" placeholder="Ex. justice, agriculture, santé…" autocomplete="off"><button type="button" data-clear hidden>Effacer</button></div></form><p class="no-results" role="status" hidden>Aucun article ne correspond. Essayez un autre mot.</p><div class="article-grid">{''.join(card(a) for a in subset)}</div><p class="index-note">Une entrée rapide, puis le temps de comprendre. Chaque article réunit un résumé, dix repères, une explication structurée et ses références.</p></section><section class="editorial-note"><h2>Un savoir accessible et vérifiable.</h2><p>Cette édition s’appuie sur le corpus de travail « État des lieux de la RDC », un ensemble de rapports de recherche thématiques réunis par DIELA, et sur des sources publiques. Ces rapports aident à choisir les sujets et à repérer les références à vérifier ; ils ne constituent pas, à eux seuls, une validation des informations publiées.</p><a href="/elikyapedia/methode.html#corpus">Comprendre le corpus et notre méthode →</a></section></main>'''
    path=f'{domain}/' if domain else 'index.html'
    write(Path(domain or '')/'index.html',shell(name,desc,body,path,domain))

def auxiliaries(articles):
    sources=''.join(f'<section><h2><a href="/elikyapedia/articles/{a["slug"]}/">{esc(a["title"])}</a></h2><ul>'+''.join(f'<li><a href="{esc(s["url"])}">{esc(s["title"])}</a><p>{esc(s.get("note",""))}</p></li>' for s in a['sources'])+'</ul></section>' for a in articles)
    write('sources.html',shell('Sources & documentation',f'Les sources publiques des {len(articles)} articles de référence.',f'<main id="contenu" class="simple-page"><p class="eyebrow">Documentation</p><h1>Sources & documentation</h1><p class="lead">Les références sont regroupées par article. Dans les textes, les appels numérotés renvoient au passage concerné.</p>{sources}</main>','sources.html'))
    method='''<main id="contenu" class="simple-page"><p class="eyebrow">Édition 2.0 · 9 novembre 2026</p><h1>Méthode éditoriale</h1><p class="lead">Expliquer la République démocratique du Congo avec précision, sans confondre connaissance, opinion et programme politique.</p><section id="corpus"><h2>Qu’est-ce que le corpus « État des lieux de la RDC » ?</h2><p>Un corpus est un ensemble de documents réunis pour étudier un sujet. Le corpus « État des lieux de la RDC » est la base documentaire de travail de DIELA : il rassemble des rapports de synthèse thématiques sur les institutions, les finances publiques, les mines, l’énergie, la santé et d’autres domaines de la vie congolaise. Ce nom désigne une collection de travaux, et non un rapport unique ou un diagnostic national officiel.</p><p>Ces documents servent à choisir les sujets des articles, à formuler les questions et à repérer les sources à vérifier. Ils peuvent réunir des synthèses, des notes internes, des hypothèses et des références à des documents de tiers. Une information n’est donc pas considérée comme établie parce qu’elle apparaît dans le corpus.</p><p>Le corpus de travail n’est pas mis en ligne dans son ensemble. Il contient des notes internes et peut renvoyer à des documents de tiers dont les droits restent à leurs titulaires. Le lecteur accède aux articles rédigés pour le public et aux références indiquées dans chacun d’eux.</p></section><section id="redaction"><h2>Comment passe-t-on du corpus à l’article ?</h2><ol><li><strong>Définir le sujet.</strong> Une question de connaissance générale détermine le périmètre de l’article.</li><li><strong>Retrouver les sources publiques.</strong> Les rapports du corpus orientent la recherche de textes officiels, de données institutionnelles et de travaux scientifiques. Ces sources sont examinées pour retenir les informations utilisables.</li><li><strong>Rédiger une synthèse distincte.</strong> L’article explique les notions et les mécanismes ; les notes privées, consignes de travail et stratégies internes n’y sont pas reprises. Les faits sont distingués des hypothèses, interprétations et objectifs de réforme.</li><li><strong>Rendre les références vérifiables.</strong> Les appels de notes conduisent aux sources citées. Leur date et leur périmètre doivent être considérés : un texte juridique décrit une règle, un rapport ancien décrit sa période, et un objectif annoncé ne prouve pas sa réalisation.</li></ol><p>Le corpus facilite la préparation d’un article ; les références publiques permettent au lecteur d’en examiner les fondements. Cette méthode ne constitue ni une certification indépendante de chaque information ni la garantie que les données disponibles sont exhaustives ou actuelles.</p></section><section><h2>Trois domaines, deux niveaux de lecture</h2><p>Politique regroupe l’État, la justice, la démocratie, la sécurité et les relations internationales. Économie rassemble production, finances, agriculture, mines, énergie et échanges. Social couvre santé, éducation, protection sociale, culture et savoirs. Chaque article propose un résumé de 100 mots, dix points clés, puis une explication détaillée avec sommaire et références.</p></section><section><h2>Du corpus de recherche à l’article public</h2><p>Les articles publics sont des synthèses nouvelles, rédigées à partir des questions issues du corpus et des sources consultées. Les rapports du corpus restent des matériaux préparatoires, distincts des références que le lecteur peut examiner. Les correspondances, données personnelles, consignes de travail et stratégies internes sont exclues des textes publics.</p><p>Les droits des documents d’origine restent à leurs titulaires. Leur présence dans le corpus ne signifie pas qu’ils peuvent être redistribués. Cette édition ne republie pas les rapports du corpus ni les PDF tiers. Le téléchargement de texte porte uniquement sur l’article public ELIKYAPEDIA.</p></section><section><h2>Neutralité et attribution</h2><p>Les articles décrivent les institutions, leurs mécanismes et les limites documentées. Les objectifs légaux sont distingués des résultats observés. Les ambitions de programmes et les scénarios ne sont pas des réalisations acquises. Les accusations non étayées et classements personnels sont exclus. Une analyse ne représente pas à elle seule un consensus scientifique.</p></section><section><h2>Dates, données et droit</h2><p>La date de mise à jour indique une révision éditoriale, pas le millésime de tous les faits. La période du corpus et les dates des sources figurent dans les références. Les constats historiques sont datés. Les textes juridiques doivent être lus avec leurs amendements et règles d’application ; les articles ne constituent pas des consultations juridiques, financières ou médicales individuelles. Aucune série statistique actuelle n’est déduite d’un rapport ancien.</p></section><section><h2>Références et corrections</h2><p>Les appels de notes relient les passages aux références qui les soutiennent. Les sources primaires — textes officiels, institutions statistiques, organismes scientifiques — sont privilégiées. Un lien est une référence, pas une garantie permanente de disponibilité. Une correction ultérieure doit préserver l’adresse de l’article, indiquer sa nouvelle date et revoir les passages dépendants.</p></section><section><h2>Adresses et continuité</h2><p>Les articles ont une adresse stable sous /elikyapedia/articles/. Les anciens dossiers énergie, finances publiques et agriculture renvoient aux articles réécrits. Les six anciens textes courts sont remplacés à leurs adresses par des liens de continuité vers les nouveaux articles. Les anciens cahiers PDF ne sont plus proposés comme édition courante.</p></section><section><h2>Lecture et accessibilité</h2><p>Les articles sont lisibles sans compte ni script. La recherche fonctionne localement, sans transmettre la requête à un service externe. Le sommaire, les liens de sources, le téléchargement du texte et l’impression facilitent la lecture sur ordinateur et téléphone. ELIKYAPEDIA est une publication DIELA sans affiliation avec Wikipédia.</p></section></main>'''
    write('methode.html',shell('Méthode éditoriale','Principes éditoriaux, sources, neutralité et dates.',method,'methode.html'))

def redirects():
    mappings={'energie/index.html':'energie','finances-publiques/index.html':'finances-publiques','agriculture/index.html':'agriculture',
    'energie/articles/potentiel-et-service.html':'energie','energie/articles/reseaux-et-usages-productifs.html':'energie',
    'finances-publiques/articles/lire-un-budget.html':'finances-publiques','finances-publiques/articles/recettes-et-depenses-fiscales.html':'finances-publiques',
    'agriculture/articles/terre-et-systeme-alimentaire.html':'agriculture','agriculture/articles/cooperer-transformer-apprendre.html':'agriculture'}
    for old,new in mappings.items():
        url=ORIGIN+'articles/'+new+'/'
        write(old,f'<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Article réécrit — ELIKYAPEDIA</title><link rel="canonical" href="{url}"><meta http-equiv="refresh" content="0;url={url}"></head><body><p>Cet article a été réécrit et enrichi. <a href="{url}">Lire la nouvelle édition.</a></p></body></html>')

if __name__=='__main__':
    articles=json.loads((HERE/'articles.json').read_text())
    counts=Counter(a['domain'] for a in articles)
    assert set(counts)==set(DOMAINS) and all(n>=5 for n in counts.values())
    assert len({a['slug'] for a in articles})==len(articles)
    for a in articles:
        assert len(a['summary'].split())==100,(a['slug'],len(a['summary'].split()))
        assert len(a['keyPoints'])==10,a['slug']
        assert len(a['sections'])>=6,a['slug']
        text=' '.join(p for s in a['sections'] for p in s['paragraphs'])
        assert len(text.split())>=1000,(a['slug'],len(text.split()))
        assert not re.search(r'https?://(?:docs|drive)\.google\.com',json.dumps(a)),a['slug']
        cites={int(c) for c in re.findall(r'\[(\d+)\]',text)}
        assert cites and all(1<=c<=len(a['sources']) for c in cites),a['slug']
        article_page(a,articles)
    catalog(articles)
    for domain in DOMAINS: catalog(articles,domain)
    auxiliaries(articles); redirects()
    write('sources.json',json.dumps({'edition':'2.0','date':'2026-11-10','articles':[{'title':a['title'],'slug':a['slug'],'sources':a['sources']} for a in articles]},ensure_ascii=False,indent=2))
    print(f'Built {len(articles)} articles, 3 domains, sources, method, and legacy redirects.')
