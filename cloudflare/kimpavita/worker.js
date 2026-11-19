const SITE = "https://kimpavita.diela.org";

const esc = (value = "") => String(value)
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;")
  .replaceAll("'", "&#039;");

const json = (data, status = 200) => new Response(JSON.stringify(data), {
  status,
  headers: {
    "content-type": "application/json; charset=utf-8",
    "cache-control": status === 200 ? "public, max-age=60" : "no-store",
  },
});

const page = (title, body, description = "KimpaVita — agence congolaise d'information factuelle, concise et sourcée.") => new Response(`<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(title)} — KimpaVita</title><meta name="description" content="${esc(description)}">
<meta property="og:title" content="${esc(title)} — KimpaVita"><meta property="og:description" content="${esc(description)}"><meta property="og:type" content="website">
<style>
:root{--ink:#171717;--paper:#f8f5ef;--red:#8f1d2c;--muted:#6e6a64;--line:#d8d1c7;--white:#fff}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.55}a{color:inherit}.shell{max-width:1120px;margin:auto;padding:0 28px}.top{display:flex;align-items:center;justify-content:space-between;padding:24px 0;border-bottom:1px solid var(--ink)}.brand{text-decoration:none;font-family:Georgia,serif;font-size:28px;font-weight:700;letter-spacing:-.03em}.brand i{color:var(--red);font-style:normal}.nav{display:flex;gap:24px;font-size:14px}.nav a{text-decoration:none}.hero{padding:76px 0 60px;display:grid;grid-template-columns:1.7fr 1fr;gap:56px;border-bottom:1px solid var(--line)}.kicker{color:var(--red);font-size:12px;font-weight:800;letter-spacing:.14em;text-transform:uppercase}.hero h1{font-family:Georgia,serif;font-size:clamp(46px,7vw,84px);line-height:.98;letter-spacing:-.055em;margin:14px 0 24px;max-width:820px}.hero p{font-size:20px;max-width:700px}.method{border-left:3px solid var(--red);padding-left:22px;align-self:end}.method b{display:block;margin-bottom:8px}.section{padding:52px 0}.section-head{display:flex;justify-content:space-between;align-items:end;border-bottom:1px solid var(--ink);padding-bottom:12px;margin-bottom:26px}.section-head h2{font-family:Georgia,serif;font-size:32px;margin:0}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:28px}.card{border-top:4px solid var(--ink);padding-top:16px}.card a{text-decoration:none}.card h3{font-family:Georgia,serif;font-size:25px;line-height:1.12;margin:10px 0}.meta{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.08em}.badge{display:inline-block;background:#eee4e5;color:var(--red);padding:4px 7px;font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.06em}.empty{padding:48px;border:1px solid var(--line);background:rgba(255,255,255,.42);font-family:Georgia,serif;font-size:24px}.article{max-width:780px;margin:0 auto;padding:70px 0}.article h1{font-family:Georgia,serif;font-size:clamp(40px,6vw,68px);line-height:1.03;letter-spacing:-.04em;margin:14px 0 22px}.dek{font-size:22px;color:#34312e}.article-body{font-family:Georgia,serif;font-size:20px;margin-top:42px}.article-body p{margin:0 0 1.25em}.sources{margin-top:52px;border-top:1px solid var(--ink);padding-top:22px}.sources li{margin:8px 0;word-break:break-word}.footer{border-top:1px solid var(--ink);padding:28px 0 50px;display:flex;justify-content:space-between;color:var(--muted);font-size:13px}.principles{display:grid;grid-template-columns:repeat(4,1fr);gap:18px}.principle{border-top:1px solid var(--ink);padding-top:14px}.principle strong{display:block;font-family:Georgia,serif;font-size:20px;margin-bottom:5px}.notfound{padding:110px 0;max-width:700px}.notfound h1{font-family:Georgia,serif;font-size:64px;margin:0 0 18px}@media(max-width:760px){.shell{padding:0 20px}.nav{gap:12px}.nav a:nth-child(2){display:none}.hero{grid-template-columns:1fr;padding:52px 0 40px}.grid,.principles{grid-template-columns:1fr}.footer{display:block}.footer span{display:block;margin:6px 0}}
</style></head><body><div class="shell"><header class="top"><a class="brand" href="/"><i>Kimpa</i>Vita</a><nav class="nav"><a href="/">Dépêches</a><a href="/methode">Notre méthode</a><a href="https://www.diela.org">DIELA ↗</a></nav></header>${body}<footer class="footer"><span>KimpaVita · Une initiative DIELA Media</span><span>Faits vérifiés · Sources visibles · Corrections publiques</span></footer></div></body></html>`, {
  headers: {"content-type":"text/html; charset=utf-8","cache-control":"public, max-age=60"},
});

function paragraphs(text) {
  return String(text || "").split(/\n\s*\n/).filter(Boolean).map(p => `<p>${esc(p).replaceAll("\n", "<br>")}</p>`).join("");
}

function sources(article) {
  let urls = [], names = [];
  try { urls = JSON.parse(article.source_urls || "[]"); } catch {}
  try { names = JSON.parse(article.source_names || "[]"); } catch {}
  if (!urls.length) return "";
  return `<section class="sources"><h2>Sources</h2><ol>${urls.map((url, i) => `<li><a href="${esc(url)}" rel="noopener noreferrer">${esc(names[i] || url)}</a></li>`).join("")}</ol></section>`;
}

async function home(env) {
  const { results = [] } = await env.DB.prepare("SELECT slug,title,dek,category,verification_level,published_at FROM articles WHERE status='published' ORDER BY published_at DESC LIMIT 18").all();
  const cards = results.length ? `<div class="grid">${results.map(a => `<article class="card"><div class="meta">${esc(a.category)} · ${esc((a.published_at || "").slice(0,10))}</div><a href="/depeches/${encodeURIComponent(a.slug)}"><h3>${esc(a.title)}</h3><p>${esc(a.dek)}</p></a><span class="badge">${esc(a.verification_level)}</span></article>`).join("")}</div>` : `<div class="empty">La rédaction prépare les premières dépêches. Aucune information ne sera publiée avant recoupement.</div>`;
  return page("Agence de presse", `<main><section class="hero"><div><div class="kicker">Agence congolaise d'information</div><h1>Les faits, débarrassés du bruit.</h1><p>KimpaVita extrait les affirmations vérifiables, les recoupe auprès de sources indépendantes et publie une information concise, sobre et traçable.</p></div><aside class="method"><b>Notre règle</b><span>Deux sources éditorialement indépendantes pour les informations sensibles. Les incertitudes restent visibles. Les corrections demeurent publiques.</span></aside></section><section class="section"><div class="section-head"><h2>Dernières dépêches</h2><a href="/feed.json">Flux JSON</a></div>${cards}</section><section class="section"><div class="section-head"><h2>Ce que signifie vérifier</h2></div><div class="principles"><div class="principle"><strong>Confirmé</strong><span>Fait établi par des sources indépendantes ou primaires concordantes.</span></div><div class="principle"><strong>Probable</strong><span>Éléments convergents, mais confirmation encore incomplète.</span></div><div class="principle"><strong>Contesté</strong><span>Versions contradictoires présentées sans arbitrage artificiel.</span></div><div class="principle"><strong>Non vérifié</strong><span>Affirmation attribuée, non reprise comme un fait.</span></div></div></section></main>`);
}

async function articlePage(env, slug) {
  const article = await env.DB.prepare("SELECT * FROM articles WHERE slug=? AND status='published'").bind(slug).first();
  if (!article) return page("Introuvable", `<main class="notfound"><h1>404</h1><p>Cette dépêche n'existe pas ou n'est pas publique.</p><a href="/">Retour aux dépêches</a></main>`, "Dépêche introuvable.");
  const corrections = await env.DB.prepare("SELECT note,corrected_at FROM corrections WHERE article_id=? ORDER BY corrected_at ASC").bind(article.id).all();
  const correctionHtml = corrections.results?.length ? `<section class="sources"><h2>Corrections</h2>${corrections.results.map(c=>`<p><b>${esc(c.corrected_at.slice(0,10))}</b> — ${esc(c.note)}</p>`).join("")}</section>` : "";
  return page(article.title, `<main class="article"><div class="kicker">${esc(article.category)}</div><h1>${esc(article.title)}</h1><p class="dek">${esc(article.dek)}</p><div class="meta">Publié le ${esc((article.published_at||"").slice(0,16).replace("T"," "))} · <span class="badge">${esc(article.verification_level)}</span></div><div class="article-body">${paragraphs(article.body)}</div>${sources(article)}${correctionHtml}</main>`, article.dek);
}

async function feed(env) {
  const { results = [] } = await env.DB.prepare("SELECT slug,title,dek,body,category,verification_level,source_urls,source_names,published_at,updated_at FROM articles WHERE status='published' ORDER BY published_at DESC LIMIT 100").all();
  return json({version:"https://jsonfeed.org/version/1.1",title:"KimpaVita",home_page_url:SITE,feed_url:`${SITE}/feed.json`,items:results.map(a=>({id:`${SITE}/depeches/${a.slug}`,url:`${SITE}/depeches/${a.slug}`,title:a.title,summary:a.dek,content_text:a.body,date_published:a.published_at,date_modified:a.updated_at,tags:[a.category,a.verification_level],_sources:JSON.parse(a.source_urls||"[]")}))});
}

async function publish(request, env) {
  const auth = request.headers.get("authorization") || "";
  if (!env.PUBLISH_TOKEN || auth !== `Bearer ${env.PUBLISH_TOKEN}`) return json({error:"unauthorized"}, 401);
  let input; try { input = await request.json(); } catch { return json({error:"invalid_json"}, 400); }
  const required = ["slug","title","body","source_urls"];
  for (const key of required) if (!input[key] || (key === "source_urls" && !Array.isArray(input[key]))) return json({error:`missing_${key}`}, 400);
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(input.slug)) return json({error:"invalid_slug"}, 400);
  if (input.source_urls.length < 1) return json({error:"source_required"}, 400);
  const now = input.published_at || new Date().toISOString();
  const status = input.status === "draft" ? "draft" : "published";
  const stmt = env.DB.prepare(`INSERT INTO articles (slug,title,dek,body,category,verification_level,source_urls,source_names,image_url,status,published_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,CURRENT_TIMESTAMP) ON CONFLICT(slug) DO UPDATE SET title=excluded.title,dek=excluded.dek,body=excluded.body,category=excluded.category,verification_level=excluded.verification_level,source_urls=excluded.source_urls,source_names=excluded.source_names,image_url=excluded.image_url,status=excluded.status,published_at=excluded.published_at,updated_at=CURRENT_TIMESTAMP RETURNING id,slug,status`).bind(input.slug,input.title,input.dek||"",input.body,input.category||"Actualité",input.verification_level||"confirmé",JSON.stringify(input.source_urls),JSON.stringify(input.source_names||[]),input.image_url||null,status,now);
  const saved = await stmt.first();
  await env.DB.prepare("INSERT INTO publication_log(article_id,action,actor,detail) VALUES(?,?,?,?)").bind(saved.id,"upsert",input.actor||"automation",JSON.stringify({status})).run();
  return json({ok:true,article:saved,url:`${SITE}/depeches/${saved.slug}`}, 201);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === "GET" && url.pathname === "/") return home(env);
    if (request.method === "GET" && url.pathname === "/methode") return page("Notre méthode", `<main class="article"><div class="kicker">Règle éditoriale</div><h1>Vérifier avant de publier.</h1><p class="dek">KimpaVita ne mesure pas sa valeur au volume produit, mais à la solidité de ce qu'elle affirme.</p><div class="article-body"><p>Nous séparons les faits, les déclarations, les accusations et l'analyse. Une déclaration correctement attribuée n'est pas automatiquement un fait confirmé.</p><p>Les informations sont recoupées auprès de sources éditorialement indépendantes. Les documents primaires sont privilégiés lorsqu'ils existent. Toute incertitude pertinente est signalée au lecteur.</p><p>Une erreur corrigée ne disparaît pas silencieusement : la correction est datée et attachée à la dépêche.</p></div></main>`);
    if (request.method === "GET" && url.pathname.startsWith("/depeches/")) return articlePage(env, decodeURIComponent(url.pathname.slice(11)));
    if (request.method === "GET" && url.pathname === "/feed.json") return feed(env);
    if (request.method === "GET" && url.pathname === "/api/health") return json({ok:true,service:"kimpavita-press",time:new Date().toISOString()});
    if (request.method === "POST" && url.pathname === "/api/publish") return publish(request, env);
    return page("Introuvable", `<main class="notfound"><h1>404</h1><p>La page demandée n'existe pas.</p><a href="/">Retour à l'accueil</a></main>`);
  },
};
