/* Meu Representante — navegação do site (sem dependências externas). */
"use strict";

const estado = { meta: null, nacional: null, ufs: {} };
const app = document.getElementById("app");
const POR_PAGINA = 60;

const RESULTADOS = {
  eleito: "Eleito(a)",
  segundo_turno: "2º turno",
  suplente: "Suplente",
  nao_eleito: "Não eleito(a)",
  aguardando: "Aguardando resultado",
};

const CARGOS = {
  "PRESIDENTE": "Presidente",
  "GOVERNADOR": "Governador(a)",
  "SENADOR": "Senador(a)",
  "DEPUTADO FEDERAL": "Deputado(a) Federal",
  "DEPUTADO ESTADUAL": "Deputado(a) Estadual",
  "DEPUTADO DISTRITAL": "Deputado(a) Distrital",
  "VICE-PRESIDENTE": "Vice-presidente",
  "VICE-GOVERNADOR": "Vice-governador(a)",
  "1º SUPLENTE": "1º suplente",
  "2º SUPLENTE": "2º suplente",
};

/* ---------- utilidades ---------- */

const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const semAcento = (s) => String(s ?? "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
const moeda = (v) => v.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

async function json(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`${url}: ${r.status}`);
  return r.json();
}

async function carregarNacional() {
  if (!estado.nacional) estado.nacional = await json("dados/nacional.json");
  return estado.nacional;
}

async function carregarUF(uf) {
  if (!estado.ufs[uf]) estado.ufs[uf] = await json(`dados/uf/${uf}.json`);
  return estado.ufs[uf];
}

function foto(c) {
  const m = estado.meta;
  const cd = c.cargo === "PRESIDENTE" ? m.cd_eleicao_federal : m.cd_eleicao_estadual;
  return m.url_foto.replace("{ano}", m.ano).replace("{cd}", cd).replace("{uf}", c.uf.toLowerCase()).replace("{sq}", c.id);
}

function linkTSE(c) {
  const m = estado.meta;
  return m.url_divulgacand.replace("{ano}", m.ano).replace("{sqele}", m.sq_eleicao).replace("{uf}", c.uf).replace("{sq}", c.id);
}

function pilarDe(cargo) {
  return Object.entries(estado.meta.pilares).find(([, p]) => p.cargos.includes(cargo))?.[0];
}

function parseHash() {
  const [rota, qs] = location.hash.replace(/^#/, "").split("?");
  return { partes: rota.split("/").filter(Boolean).map(decodeURIComponent), params: new URLSearchParams(qs || "") };
}

function irPara(partes, params) {
  const qs = params && [...params].length ? "?" + params.toString() : "";
  location.hash = "#/" + partes.map(encodeURIComponent).join("/") + qs;
}

const SEM_FOTO = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 30 40'%3E%3Crect width='30' height='40' fill='%23ddd'/%3E%3Ccircle cx='15' cy='15' r='6' fill='%23aaa'/%3E%3Cpath d='M4 36c0-7 5-10 11-10s11 3 11 10' fill='%23aaa'/%3E%3C/svg%3E";
const imgFoto = (c, classe = "foto") =>
  `<img class="${classe}" src="${esc(foto(c))}" alt="Foto de ${esc(c.nome_urna)}" loading="lazy" onerror="this.onerror=null;this.alt='Sem foto';this.src=SEM_FOTO">`;

const selo = (r) => `<span class="selo selo-${esc(r)}">${esc(RESULTADOS[r] || r)}</span>`;

/* ---------- telas ---------- */

function telaInicio() {
  const m = estado.meta;
  const p = m.pilares;
  const aviso = m.resultados_disponiveis
    ? `<a class="destaque-2t" href="#/2turno"><span>2º turno · ${esc(m.data_segundo_turno_txt)}</span>
         <strong>Compare lado a lado os candidatos à Presidência e aos governos</strong><em>Ver disputas →</em></a>`
    : `<div class="aviso">Os resultados oficiais do 1º turno ainda não entraram nos dados do TSE.
       Todas as candidaturas estão listadas; os selos de <b>eleito</b> e <b>2º turno</b> aparecem na próxima atualização.</div>`;
  document.title = "Meu Representante · Eleições 2026";
  app.innerHTML = `
    <section class="intro">
      <h1>Quem vai decidir o futuro do país?</h1>
      <p>Executivo e Legislativo formam juntos a construção das leis e das políticas públicas.
         Escolha um pilar para conhecer candidatos e eleitos: propostas, trajetória e conduta, sempre com fonte.</p>
    </section>
    ${aviso}
    <section class="triangulo" aria-label="Os três pilares">
      <svg viewBox="0 0 600 520" role="img" aria-labelledby="tri-t">
        <title id="tri-t">Triângulo com os três pilares: Executivo, Senado e Câmaras</title>
        <polygon class="tri-base" points="300,70 540,460 60,460"/>
        <text class="tri-centro" x="300" y="330" text-anchor="middle">leis e</text>
        <text class="tri-centro" x="300" y="358" text-anchor="middle">políticas públicas</text>
        ${vertice("executivo", 300, 90, p.executivo)}
        ${vertice("senado", 92, 440, p.senado)}
        ${vertice("camara", 508, 440, p.camara)}
      </svg>
      <div class="pilares-lista">
        ${Object.entries(p).map(([k, v]) => `
          <a class="pilar-cartao" href="#/p/${k}" style="--cor:${v.cor}">
            <strong>${esc(v.nome)}</strong><span>${esc(v.descricao)}</span>
          </a>`).join("")}
      </div>
    </section>
    <a class="convite" href="#/colabore"><strong>Projeto aberto:</strong> envie informações com fonte e ajude a revisar,
      principalmente se você é da área jurídica ou de jornalismo. →</a>
    <section>
      <h2>Ou escolha seu estado</h2>
      <div class="ufs">${Object.entries(m.ufs).map(([uf, nome]) => `<a href="#/uf/${uf}" title="${esc(nome)}">${uf}</a>`).join("")}</div>
    </section>`;
}

function vertice(chave, x, y, p) {
  return `<a href="#/p/${chave}" class="vertice" style="--cor:${p.cor}">
      <circle cx="${x}" cy="${y}" r="70"/>
      <text x="${x}" y="${y + 8}" text-anchor="middle">${esc(p.nome)}</text>
    </a>`;
}

async function telaPilar(chave, params) {
  const m = estado.meta;
  const pilar = m.pilares[chave];
  if (!pilar) return telaNaoEncontrada();
  const uf = params.get("uf") || "";
  document.title = `${pilar.nome} · Meu Representante`;

  if (chave === "camara" && !uf) {
    app.innerHTML = `${cabecalhoPilar(pilar)}
      <p>Deputados são eleitos por estado. Escolha a unidade da federação:</p>
      <div class="ufs">${Object.entries(m.ufs).map(([s, n]) => `<a href="#/p/camara?uf=${s}" title="${esc(n)}">${s}</a>`).join("")}</div>`;
    return;
  }
  app.innerHTML = `${cabecalhoPilar(pilar)}<p class="carregando">Carregando candidaturas…</p>`;
  const base = chave === "camara" ? await carregarUF(uf) : await carregarNacional();
  const lista = base.filter((c) => pilar.cargos.includes(c.cargo));
  renderLista({ titulo: cabecalhoPilar(pilar), lista, params, cargos: pilar.cargos, rota: ["p", chave], exigeUF: chave === "camara" });
}

async function telaUF(uf, params) {
  const m = estado.meta;
  if (!m.ufs[uf]) return telaNaoEncontrada();
  document.title = `${m.ufs[uf]} · Meu Representante`;
  app.innerHTML = `<p class="carregando">Carregando ${esc(m.ufs[uf])}…</p>`;
  const [nac, deps] = await Promise.all([carregarNacional(), carregarUF(uf)]);
  const lista = nac.filter((c) => c.uf === uf || c.uf === "BR").concat(deps);
  params.set("uf", uf);
  const titulo = `<div class="cab-pilar" style="--cor:var(--tinta)"><h1>${esc(m.ufs[uf])}</h1>
      <p>Todas as candidaturas que representam ${esc(m.ufs[uf])}, da Presidência à Assembleia.</p></div>`;
  renderLista({ titulo, lista, params, cargos: m.ordem_cargos, rota: ["uf", uf], ufFixa: true });
}

async function telaBusca(params) {
  const q = params.get("q") || "";
  document.title = `Busca: ${q} · Meu Representante`;
  const nac = await carregarNacional();
  const uf = params.get("uf");
  const deps = uf ? await carregarUF(uf) : [];
  const titulo = `<div class="cab-pilar" style="--cor:var(--tinta)"><h1>Busca</h1>
     <p>${uf ? "" : "Para buscar deputados, selecione também o estado."}</p></div>`;
  renderLista({ titulo, lista: nac.concat(deps), params, cargos: estado.meta.ordem_cargos, rota: ["busca"] });
}

const cabecalhoPilar = (p) =>
  `<div class="cab-pilar" style="--cor:${p.cor}"><a href="#/" class="voltar">← Início</a><h1>${esc(p.nome)}</h1><p>${esc(p.descricao)}</p></div>`;

function renderLista({ titulo, lista, params, cargos, rota, exigeUF, ufFixa }) {
  const m = estado.meta;
  const f = {
    uf: params.get("uf") || "",
    cargo: params.get("cargo") || "",
    res: params.has("res") ? params.get("res") : (m.resultados_disponiveis ? "relevantes" : ""),
    partido: params.get("partido") || "",
    q: params.get("q") || "",
    dossie: params.get("dossie") === "1",
  };
  const partidos = [...new Set(lista.map((c) => c.partido))].sort();
  const cargosPresentes = cargos.filter((c) => lista.some((x) => x.cargo === c));
  const termo = semAcento(f.q);

  let filtrada = lista.filter((c) =>
    (!f.uf || c.uf === f.uf || (c.uf === "BR" && !exigeUF && rota[0] !== "p")) &&
    (!f.cargo || c.cargo === f.cargo) &&
    (!f.partido || c.partido === f.partido) &&
    (!f.dossie || c.dossie) &&
    (!f.res || (f.res === "relevantes" ? ["eleito", "segundo_turno"].includes(c.resultado) : c.resultado === f.res)) &&
    (!termo || semAcento(`${c.nome_urna} ${c.nome} ${c.partido} ${c.numero}`).includes(termo)));

  filtrada.sort((a, b) =>
    m.ordem_cargos.indexOf(a.cargo) - m.ordem_cargos.indexOf(b.cargo) ||
    ordemRes(a.resultado) - ordemRes(b.resultado) ||
    a.uf.localeCompare(b.uf) || a.nome_urna.localeCompare(b.nome_urna, "pt-BR"));

  const opt = (v, txt, sel) => `<option value="${esc(v)}"${v === sel ? " selected" : ""}>${esc(txt)}</option>`;
  app.innerHTML = `${titulo}
    <form class="filtros" id="filtros">
      ${ufFixa ? "" : `<label>Estado<select name="uf">${opt("", exigeUF ? "Escolha…" : "Todos", f.uf)}${Object.keys(m.ufs).map((u) => opt(u, u, f.uf)).join("")}</select></label>`}
      ${cargosPresentes.length > 1 ? `<label>Cargo<select name="cargo">${opt("", "Todos", f.cargo)}${cargosPresentes.map((c) => opt(c, CARGOS[c], f.cargo)).join("")}</select></label>` : ""}
      <label>Situação<select name="res">
        ${opt("", "Todas as candidaturas", f.res)}${opt("relevantes", "Eleitos + 2º turno", f.res)}
        ${opt("eleito", "Eleitos", f.res)}${opt("segundo_turno", "No 2º turno", f.res)}${opt("aguardando", "Aguardando resultado", f.res)}
        ${opt("nao_eleito", "Não eleitos", f.res)}${opt("suplente", "Suplentes", f.res)}
      </select></label>
      <label>Partido<select name="partido">${opt("", "Todos", f.partido)}${partidos.map((p) => opt(p, p, f.partido)).join("")}</select></label>
      <label class="campo-busca">Nome<input type="search" name="q" value="${esc(f.q)}" placeholder="Filtrar…"></label>
      <label class="check"><input type="checkbox" name="dossie" value="1"${f.dossie ? " checked" : ""}> Só com dossiê</label>
    </form>
    <p class="contagem">${filtrada.length.toLocaleString("pt-BR")} candidatura(s)</p>
    <div class="grade" id="grade"></div>
    <div class="mais"><button type="button" id="mais" hidden>Mostrar mais</button></div>`;

  const grade = document.getElementById("grade");
  const botao = document.getElementById("mais");
  let mostrados = 0;
  const pagina = () => {
    grade.insertAdjacentHTML("beforeend", filtrada.slice(mostrados, mostrados + POR_PAGINA).map(cartao).join(""));
    mostrados += POR_PAGINA;
    botao.hidden = mostrados >= filtrada.length;
  };
  botao.onclick = pagina;
  pagina();
  if (!filtrada.length) grade.innerHTML = `<p class="vazio">Nenhuma candidatura com esses filtros.</p>`;

  const form = document.getElementById("filtros");
  let espera;
  const aplicar = () => {
    const p = new URLSearchParams();
    for (const [k, v] of new FormData(form)) if (v) p.set(k, v);
    if (!p.has("res")) p.set("res", "");
    if (ufFixa) p.delete("uf");
    irPara(rota, p);
  };
  form.addEventListener("change", aplicar);
  form.q.addEventListener("input", () => { clearTimeout(espera); espera = setTimeout(aplicar, 350); });
  form.addEventListener("submit", (e) => { e.preventDefault(); aplicar(); });
}

const ordemRes = (r) => ["eleito", "segundo_turno", "aguardando", "suplente", "nao_eleito"].indexOf(r);

function cartao(c) {
  const cor = estado.meta.pilares[pilarDe(c.cargo)]?.cor;
  const d = c.dossie;
  const alertas = d ? d.conduta.length : 0;
  return `<a class="cartao" href="#/c/${esc(c.uf)}/${esc(c.id)}" style="--cor:${cor}">
      ${imgFoto(c)}
      <div class="cartao-txt">
        <strong>${esc(c.nome_urna)}</strong>
        <span class="partido">${esc(c.partido)} · ${esc(c.numero)}${c.percentual != null ? ` · <b>${pct(c.percentual)}</b>` : ""}</span>
        <span class="cargo">${esc(CARGOS[c.cargo])}${c.uf !== "BR" ? " · " + esc(c.uf) : ""}</span>
        <span class="selos">${selo(c.resultado)}${d ? `<span class="selo selo-dossie">Dossiê</span>` : ""}${alertas ? `<span class="selo selo-conduta">${alertas} registro(s) de conduta</span>` : ""}</span>
      </div>
    </a>`;
}

async function telaCandidato(uf, id) {
  app.innerHTML = `<p class="carregando">Carregando…</p>`;
  const nac = await carregarNacional();
  let c = nac.find((x) => x.id === id);
  if (!c && estado.meta.ufs[uf]) c = (await carregarUF(uf)).find((x) => x.id === id);
  if (!c) return telaNaoEncontrada();

  const m = estado.meta;
  const chave = pilarDe(c.cargo);
  const pilar = m.pilares[chave];
  const d = c.dossie;
  document.title = `${c.nome_urna} (${c.partido}) · Meu Representante`;
  const voltar = chave === "camara" ? `#/p/camara?uf=${c.uf}` : `#/p/${chave}`;

  app.innerHTML = `
    <article class="perfil" style="--cor:${pilar.cor}">
      <a href="${voltar}" class="voltar">← ${esc(pilar.nome)}${chave === "camara" ? " · " + esc(c.uf) : ""}</a>
      <header class="perfil-cab">
        ${imgFoto(c, "foto foto-grande")}
        <div>
          <p class="perfil-cargo">${esc(CARGOS[c.cargo])}${c.uf !== "BR" ? " · " + esc(m.ufs[c.uf] || c.uf) : " · Brasil"}</p>
          <h1>${esc(c.nome_urna)}</h1>
          <p class="perfil-partido"><b>${esc(c.partido)}</b> ${esc(c.partido_nome || "")} · nº ${esc(c.numero)}</p>
          <p>${selo(c.resultado)} ${c.resultado_tse ? `<small>TSE: ${esc(c.resultado_tse)}</small>` : ""}</p>
          ${c.votos != null ? `<p class="votacao"><b>${c.votos.toLocaleString("pt-BR")}</b> votos (${pct(c.percentual)} dos válidos) no 1º turno
            <small>· totalização ${esc(c.totalizacao?.totalizacao || "")}, ${esc(c.totalizacao?.atualizado || "")}</small></p>` : ""}
          ${c.resultado === "segundo_turno" && adversario(c) ? `<p><a class="botao" href="#/comparar/${esc(c.id)}/${esc(adversario(c).id)}">Comparar com ${esc(adversario(c).nome_urna)} →</a></p>` : ""}
          ${c.resultado_fontes ? `<p class="fontes-inline">Resultado informado por: ${fontes(c.resultado_fontes)}</p>` : ""}
          ${c.chapa ? `<p class="chapa">${c.chapa.map((v) => `${esc(CARGOS[v.cargo] || v.cargo)}: <b>${esc(v.nome_urna)}</b> (${esc(v.partido)})`).join(" · ")}</p>` : ""}
          ${c.substitui ? `<p class="chapa">Número registrado antes por: ${esc(c.substitui.join(", "))} (substituição de candidatura, segundo o TSE)</p>` : ""}
          ${c.coligacao ? `<p class="chapa">Coligação: ${esc(c.coligacao)} (${esc(c.composicao)})</p>` : c.federacao ? `<p class="chapa">Federação: ${esc(c.federacao)}</p>` : ""}
        </div>
      </header>

      <nav class="indice" aria-label="Seções">
        <a href="#sec-propostas" data-ancora>Propostas</a><a href="#sec-trajetoria" data-ancora>Trajetória</a>
        <a href="#sec-conduta" data-ancora>Conduta e processos</a><a href="#sec-tse" data-ancora>Dados oficiais</a>
      </nav>

      ${d?.resumo ? `<p class="perfil-resumo">${esc(d.resumo)}</p>` : ""}

      <section id="sec-propostas" class="secao">
        <h2>Propostas</h2>
        ${d?.propostas.length ? `<ul class="itens">${d.propostas.map((p) => `
          <li><span class="tema">${esc(p.tema)}</span><p>${esc(p.resumo)}</p><p class="fontes-inline">Fonte: ${fontes(p.fontes)}</p></li>`).join("")}</ul>`
        : semConteudo("propostas", c)}
        <p class="dica">Documento oficial: plano de governo / propostas registradas no
          <a href="${esc(linkTSE(c))}" target="_blank" rel="noopener">DivulgaCandContas (TSE)</a>.</p>
      </section>

      <section id="sec-trajetoria" class="secao">
        <h2>Trajetória e realizações</h2>
        ${d?.trajetoria.length ? `<ol class="linha-tempo">${d.trajetoria.map((t) => `
          <li><span class="ano">${esc(t.ano ?? "")}</span><div><strong>${esc(t.titulo)}</strong><p>${esc(t.resumo)}</p>
          <p class="fontes-inline">Fonte: ${fontes(t.fontes)}</p></div></li>`).join("")}</ol>`
        : semConteudo("trajetória", c)}
      </section>

      <section id="sec-conduta" class="secao secao-conduta">
        <h2>Conduta, processos e controvérsias</h2>
        <p class="dica">Cada registro informa a situação processual. Investigação ou denúncia não significa culpa;
          só há condenação definitiva após o trânsito em julgado. ${esc(estado.meta.criterio_publicacao)}</p>
        ${d ? (d.conduta.length ? `<ul class="itens">${d.conduta.map((k) => `
          <li class="conduta conduta-${esc(k.situacao)}">
            <div class="conduta-cab"><span class="tema">${esc(k.tipo_texto)}</span><span class="situacao">${esc(k.situacao_texto)}</span></div>
            <strong>${esc(k.titulo)}</strong>${k.data ? ` <small>(${esc(k.data)})</small>` : ""}
            <p>${esc(k.resumo)}</p>
            ${k.processo ? `<p class="processo">Processo: ${esc(k.processo)}</p>` : ""}
            ${k.resposta ? `<p class="resposta"><b>Posição do(a) candidato(a):</b> ${esc(k.resposta)}</p>` : ""}
            <p class="fontes-inline">Fontes: ${fontes(k.fontes)}</p>
          </li>`).join("")}</ul>`
          : `<p class="vazio">Nenhum registro de conduta publicado até ${esc(d.atualizado_em)}.</p>`)
        : semConteudo("conduta", c)}
      </section>

      <section id="sec-tse" class="secao">
        <h2>Dados oficiais da candidatura</h2>
        <dl class="dados">
          ${linha("Nome completo", c.nome)}
          ${linha("Idade na eleição", c.idade && `${c.idade} anos`)}
          ${linha("Ocupação declarada", c.ocupacao)}
          ${linha("Grau de instrução", c.instrucao)}
          ${linha("Gênero", c.genero)}
          ${linha("Cor/raça (autodeclarada)", c.cor_raca)}
          ${linha("Patrimônio declarado", c.bens_declarados != null ? moeda(c.bens_declarados) : "Nenhum bem nos dados do TSE")}
          ${linha("Situação do registro", c.situacao_candidatura)}
        </dl>
        <p class="fontes-inline">Fonte: <a href="https://dadosabertos.tse.jus.br/" target="_blank" rel="noopener">Dados Abertos TSE</a>
          (gerados em ${esc(m.tse_gerado_em)}) · <a href="${esc(linkTSE(c))}" target="_blank" rel="noopener">ficha no DivulgaCandContas</a></p>
      </section>

      ${d ? `<p class="atualizado">Dossiê atualizado em ${esc(d.atualizado_em)}.
        ${d.links.length ? "Links úteis: " + d.links.map((l) => `<a href="${esc(l.url)}" target="_blank" rel="noopener">${esc(l.titulo || l.url)}</a>`).join(" · ") : ""}</p>` : ""}
      ${caixaColabore(c)}
    </article>`;

  app.querySelectorAll("[data-ancora]").forEach((a) => a.addEventListener("click", (e) => {
    e.preventDefault();
    document.querySelector(a.getAttribute("href"))?.scrollIntoView({ behavior: "smooth" });
  }));
}

const linha = (k, v) => (v ? `<div><dt>${esc(k)}</dt><dd>${esc(v)}</dd></div>` : "");

function fontes(lista) {
  return lista.map((f) => `<a href="${esc(f.url)}" target="_blank" rel="noopener"${f.oficial ? ' class="oficial" title="Fonte oficial"' : ""}>${esc(f.veiculo || f.titulo)}</a>`).join(", ");
}

function urlCorrecao(c) {
  const repo = estado.meta.repo_url;
  if (!repo) return "#/sobre";
  const titulo = encodeURIComponent(`Correção: ${c.nome_urna} (${c.partido}/${c.uf}) — ${c.id}`);
  return `${repo}/issues/new?title=${titulo}&labels=correcao`;
}

function urlSugestao(c) {
  const repo = estado.meta.repo_url;
  if (!repo) return "#/colabore";
  const titulo = encodeURIComponent(`Sugestão: ${c.nome_urna} (${c.partido}/${c.uf}) — ${c.id}`);
  return `${repo}/issues/new?template=sugestao.yml&title=${titulo}`;
}

function caixaColabore(...cands) {
  const alvo = (fn) => cands.map((c) => `<a href="${esc(fn(c))}" target="_blank" rel="noopener">${esc(c.nome_urna)}</a>`).join(" · ");
  return `<aside class="colabore-caixa">
    <strong>Este dossiê é aberto e revisado por voluntários.</strong>
    <p>Tem uma informação com fonte que ainda não está aqui? Enviar: ${alvo(urlSugestao)}</p>
    <p>Viu algo errado ou desatualizado? Pedir correção: ${alvo(urlCorrecao)}</p>
    <p><a href="#/colabore">Como funciona a revisão e como ser revisor(a) →</a></p>
  </aside>`;
}

function semConteudo(secao, c) {
  return `<div class="vazio">Ainda não há ${esc(secao)} verificada(s) para esta candidatura.
    <a href="${esc(urlSugestao(c))}">Envie uma informação com fonte</a> ou <a href="#/colabore">ajude a revisar</a>.</div>`;
}

function telaColabore() {
  const repo = estado.meta.repo_url;
  const link = (caminho, texto) => (repo ? `<a href="${esc(repo + caminho)}" target="_blank" rel="noopener">${texto}</a>` : texto);
  document.title = "Colabore · Meu Representante";
  app.innerHTML = `<article class="texto">
    <a href="#/" class="voltar">← Início</a>
    <h1>Colabore com o dossiê</h1>
    <p>O Meu Representante é feito por voluntários. Cada informação passa por conferência humana antes de ir ao ar,
      e o histórico de tudo o que muda é público.</p>

    <h2>Como uma informação chega ao site</h2>
    <ol class="passos">
      <li><b>Envio.</b> Qualquer pessoa envia uma informação com fonte pelo botão "Enviar" na página do candidato.</li>
      <li><b>Checagem automática.</b> O sistema confere se os links abrem e se há fonte oficial ou pelo menos duas fontes
        independentes.</li>
      <li><b>Triagem.</b> A coordenação transforma a sugestão em rascunho, no formato do dossiê, ou a recusa com o motivo.</li>
      <li><b>Revisão.</b> Duas pessoas credenciadas conferem fonte por fonte com um checklist. Para processos e conduta,
        uma delas é da área jurídica.</li>
      <li><b>Publicação automática.</b> Com as duas aprovações, o site se atualiza sozinho e registra a data.</li>
    </ol>
    <p class="dica">${esc(estado.meta.criterio_publicacao)}</p>

    <h2>Seja revisor(a)</h2>
    <p>Procuramos especialmente:</p>
    <ul>
      <li><b>Área jurídica</b> (advocacia, estudantes de Direito, núcleos de prática jurídica): conferir a situação
        processual e a redação dos registros de conduta.</li>
      <li><b>Jornalismo e checagem</b>: conferir fontes, datas e se o resumo é fiel ao que a fonte diz.</li>
      <li><b>Qualquer pessoa atenta</b>: comparar o resumo das propostas com o plano de governo registrado no TSE.</li>
    </ul>
    <p>Para manter a imparcialidade, quem revisa não aprova o próprio texto, e a rede de revisores é formada por pessoas
      de diferentes posições políticas. ${link("/issues/new?template=revisor.yml", "Quero ser revisor(a)")}</p>

    <h2>Outras formas de ajudar</h2>
    <ul>
      <li>Divulgar o site e os cards nas redes.</li>
      <li>Programação, design e acessibilidade: ${link("/blob/main/CONTRIBUTING.md", "guia de contribuição")}.</li>
    </ul>
    ${repo ? "" : `<p class="vazio">O repositório público será divulgado em breve.</p>`}
  </article>`;
}

function telaSobre() {
  const repo = estado.meta.repo_url;
  document.title = "Sobre · Meu Representante";
  app.innerHTML = `<article class="texto">
    <a href="#/" class="voltar">← Início</a>
    <h1>Sobre o projeto</h1>
    <p><b>Meu Representante</b> reúne em um só lugar informação pública e verificável sobre quem disputa e quem
      ocupa os cargos que decidem o futuro do país. É um projeto cidadão, apartidário e de código aberto.</p>
    <h2>De onde vêm os dados</h2>
    <ul>
      <li><b>Cadastro, resultado e patrimônio declarado</b>: Dados Abertos do Tribunal Superior Eleitoral, importados automaticamente.</li>
      <li><b>Propostas, trajetória e conduta</b>: dossiês escritos por colaboradores e revisados publicamente. Cada afirmação tem link para a fonte.</li>
    </ul>
    <h2>Regras editoriais</h2>
    <ul>
      <li>Nenhuma informação sem fonte. Fontes oficiais (tribunais, Ministério Público, órgãos públicos) são preferidas.</li>
      <li>Fatos de conduta sem fonte oficial exigem pelo menos duas fontes jornalísticas independentes.</li>
      <li>A situação processual é sempre indicada: investigado, denunciado, réu, condenado (e em qual instância), absolvido, arquivado.</li>
      <li>O mesmo critério vale para todos os candidatos, de qualquer partido.</li>
      <li>O posicionamento do candidato, quando público, é registrado junto ao fato.</li>
      <li>Não publicamos CPF, endereço, e-mail ou dados de familiares.</li>
    </ul>
    <h2>Como decidimos o que publicar</h2>
    <p>${esc(estado.meta.criterio_publicacao)} Itens em conferência não aparecem no site nem nas imagens para redes sociais.
      <a href="#/colabore">Veja como funciona a revisão</a>.</p>
    <h2>Correções e direito de resposta</h2>
    <p>Candidatos, assessorias e cidadãos podem pedir correção ${repo ? `abrindo uma <a href="${esc(repo)}/issues/new?labels=correcao" target="_blank" rel="noopener">issue no GitHub</a>` : "pelo repositório do projeto"}.
      Pedidos com fonte são analisados com prioridade.</p>
    ${repo ? `<p>Código e dados: <a href="${esc(repo)}" target="_blank" rel="noopener">${esc(repo)}</a></p>` : ""}
    <p class="dica">Site gerado em ${esc(estado.meta.site_gerado_em)} · dados do TSE de ${esc(estado.meta.tse_gerado_em)}.</p>
  </article>`;
}

function telaNaoEncontrada() {
  app.innerHTML = `<div class="texto"><h1>Página não encontrada</h1><p><a href="#/">Voltar ao início</a></p></div>`;
}

/* ---------- 2º turno ---------- */

const pct = (v) => `${v.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}%`;

function disputas2t() {
  const grupos = {};
  for (const c of estado.nacional.filter((x) => x.resultado === "segundo_turno")) {
    (grupos[`${c.uf}|${c.cargo}`] ||= []).push(c);
  }
  return Object.values(grupos)
    .map((g) => g.sort((a, b) => (b.votos || 0) - (a.votos || 0)))
    .sort((a, b) => estado.meta.ordem_cargos.indexOf(a[0].cargo) - estado.meta.ordem_cargos.indexOf(b[0].cargo)
      || (estado.meta.ufs[a[0].uf] || "").localeCompare(estado.meta.ufs[b[0].uf] || ""));
}

function adversario(c) {
  return estado.nacional?.find((x) => x.id !== c.id && x.uf === c.uf && x.cargo === c.cargo && x.resultado === "segundo_turno");
}

async function tela2turno() {
  await carregarNacional();
  const m = estado.meta;
  document.title = "2º turno · Meu Representante";
  const lista = disputas2t();
  app.innerHTML = `
    <div class="cab-pilar" style="--cor:${m.pilares.executivo.cor}"><a href="#/" class="voltar">← Início</a>
      <h1>2º turno · ${esc(m.data_segundo_turno_txt)}</h1>
      <p>${lista.length} disputa(s) definida(s) no 1º turno. Escolha uma para comparar propostas, trajetória e conduta lado a lado.</p></div>
    ${lista.length ? `<div class="disputas">${lista.map((g) => `
      <a class="disputa" href="#/comparar/${esc(g[0].id)}/${esc(g[1]?.id || "")}">
        <span class="disputa-cargo">${esc(CARGOS[g[0].cargo])} · ${esc(g[0].uf === "BR" ? "Brasil" : m.ufs[g[0].uf])}</span>
        <span class="disputa-par">${g.slice(0, 2).map((c) => `
          <span class="disputa-cand">${imgFoto(c)}<strong>${esc(c.nome_urna)}</strong>
          <span>${esc(c.partido)}${c.percentual != null ? " · " + pct(c.percentual) : ""}</span>
          ${c.dossie ? `<span class="selo selo-dossie">Dossiê</span>` : ""}</span>`).join('<span class="versus">vs</span>')}
        </span>
      </a>`).join("")}</div>`
    : `<p class="vazio">Os candidatos ao 2º turno ainda não foram definidos nos dados do TSE.</p>`}
    <p class="dica">Votação do 1º turno conforme a totalização do TSE. Disputas ainda em apuração aparecem quando o resultado
      estiver definido.</p>`;
}

async function telaComparar(idA, idB) {
  await carregarNacional();
  const a = estado.nacional.find((x) => x.id === idA);
  const b = estado.nacional.find((x) => x.id === idB);
  if (!a || !b) return telaNaoEncontrada();
  const m = estado.meta;
  const cor = m.pilares[pilarDe(a.cargo)].cor;
  const par = [a, b];
  document.title = `${a.nome_urna} x ${b.nome_urna} · Meu Representante`;

  const temas = [];
  for (const c of par) for (const p of c.dossie?.propostas || []) if (!temas.includes(p.tema)) temas.push(p.tema);
  const colunas = (fn) => `<div class="cmp-linha">${par.map((c) => `<div class="cmp-cel"><span class="cmp-quem">${esc(c.nome_urna)}</span>${fn(c)}</div>`).join("")}</div>`;
  const semDossie = (c, s) => `<p class="vazio-mini">${esc(c.dossie ? s : "Dossiê ainda não publicado.")}</p>`;

  app.innerHTML = `
    <article class="comparar" style="--cor:${cor}">
      <a href="#/2turno" class="voltar">← Disputas do 2º turno</a>
      <h1>${esc(CARGOS[a.cargo])} · ${esc(a.uf === "BR" ? "Brasil" : m.ufs[a.uf])}</h1>
      <div class="cmp-cab">${par.map((c) => `
        <a class="cmp-cand" href="#/c/${esc(c.uf)}/${esc(c.id)}">${imgFoto(c, "foto foto-grande")}
          <strong>${esc(c.nome_urna)}</strong><span>${esc(c.partido)} · nº ${esc(c.numero)}</span>
          ${c.percentual != null ? `<span class="cmp-pct">${pct(c.percentual)}</span><small>${c.votos.toLocaleString("pt-BR")} votos no 1º turno</small>` : ""}
          ${c.chapa?.length ? `<small>${c.chapa.map((v) => `${esc(CARGOS[v.cargo] || v.cargo)}: ${esc(v.nome_urna)} (${esc(v.partido)})`).join("<br>")}</small>` : ""}
        </a>`).join("")}</div>

      <nav class="indice" aria-label="Seções">
        <a href="#cmp-propostas" data-ancora>Propostas</a><a href="#cmp-trajetoria" data-ancora>Trajetória</a>
        <a href="#cmp-conduta" data-ancora>Conduta</a><a href="#cmp-dados" data-ancora>Dados oficiais</a>
      </nav>

      <section id="cmp-propostas" class="secao">
        <h2>Propostas por tema</h2>
        <p class="dica">Resumo fiel do plano de governo registrado no TSE. O site não avalia mérito, custo ou viabilidade.</p>
        ${temas.length ? temas.map((t) => `<h3 class="cmp-tema">${esc(t)}</h3>${colunas((c) => {
          const ps = (c.dossie?.propostas || []).filter((p) => p.tema === t);
          return ps.length ? ps.map((p) => `<p>${esc(p.resumo)}</p><p class="fontes-inline">${fontes(p.fontes)}</p>`).join("")
            : semDossie(c, "Sem proposta neste tema no resumo do plano.");
        })}`).join("") : `<p class="vazio">Ainda não há propostas resumidas para esta disputa.</p>`}
      </section>

      <section id="cmp-trajetoria" class="secao">
        <h2>Trajetória e realizações</h2>
        ${colunas((c) => c.dossie?.trajetoria.length ? `<ol class="linha-tempo">${c.dossie.trajetoria.map((t) => `
          <li><span class="ano">${esc(t.ano ?? "")}</span><div><strong>${esc(t.titulo)}</strong>
          <p class="fontes-inline">${fontes(t.fontes)}</p></div></li>`).join("")}</ol>` : semDossie(c, "Sem registros."))}
      </section>

      <section id="cmp-conduta" class="secao">
        <h2>Conduta, processos e controvérsias</h2>
        <p class="dica">Investigação ou denúncia não significa culpa. Cada registro informa a situação processual.
          ${esc(estado.meta.criterio_publicacao)}</p>
        ${colunas((c) => c.dossie ? (c.dossie.conduta.length ? `<ul class="itens">${c.dossie.conduta.map((k) => `
          <li class="conduta conduta-${esc(k.situacao)}"><span class="situacao">${esc(k.situacao_texto)}</span>
          <strong>${esc(k.titulo)}</strong><p>${esc(k.resumo)}</p>
          ${k.resposta ? `<p class="resposta"><b>Posição:</b> ${esc(k.resposta)}</p>` : ""}
          <p class="fontes-inline">${fontes(k.fontes)}</p></li>`).join("")}</ul>`
          : `<p class="vazio-mini">Nenhum registro publicado até ${esc(c.dossie.atualizado_em)}.</p>`) : semDossie(c, ""))}
      </section>

      <section id="cmp-dados" class="secao">
        <h2>Dados oficiais (TSE)</h2>
        ${[["Idade", (c) => c.idade && `${c.idade} anos`], ["Ocupação declarada", (c) => c.ocupacao], ["Instrução", (c) => c.instrucao],
           ["Patrimônio declarado", (c) => (c.bens_declarados != null ? moeda(c.bens_declarados) : "Nenhum bem nos dados do TSE")],
           ["Coligação / federação", (c) => c.coligacao || c.federacao || c.partido]]
          .map(([rot, fn]) => `<h3 class="cmp-tema">${esc(rot)}</h3>${colunas((c) => `<p>${esc(fn(c) || "—")}</p>`)}`).join("")}
      </section>
      ${caixaColabore(a, b)}
    </article>`;

  app.querySelectorAll("[data-ancora]").forEach((el) => el.addEventListener("click", (e) => {
    e.preventDefault();
    document.querySelector(el.getAttribute("href"))?.scrollIntoView({ behavior: "smooth" });
  }));
}

/* ---------- roteador ---------- */

async function rotear() {
  const { partes, params } = parseHash();
  try {
    switch (partes[0]) {
      case undefined: telaInicio(); break;
      case "p": await telaPilar(partes[1], params); break;
      case "uf": await telaUF(partes[1], params); break;
      case "c": await telaCandidato(partes[1], partes[2]); break;
      case "busca": await telaBusca(params); break;
      case "sobre": telaSobre(); break;
      case "colabore": telaColabore(); break;
      case "2turno": await tela2turno(); break;
      case "comparar": await telaComparar(partes[1], partes[2]); break;
      default: telaNaoEncontrada();
    }
  } catch (e) {
    console.error(e);
    app.innerHTML = `<div class="texto"><h1>Erro ao carregar</h1><p>${esc(e.message)}</p></div>`;
  }
  if (partes[0] !== "p" && partes[0] !== "uf" && partes[0] !== "busca") window.scrollTo(0, 0);
}

document.getElementById("busca").addEventListener("submit", (e) => {
  e.preventDefault();
  const q = document.getElementById("busca-texto").value.trim();
  if (q) irPara(["busca"], new URLSearchParams({ q, res: "" }));
});

(async () => {
  estado.meta = await json("dados/meta.json");
  document.getElementById("tse-data").textContent = ` (cadastro de ${estado.meta.tse_gerado_em}` +
    (estado.meta.totalizacao_atualizada ? `; totalização dos votos de ${estado.meta.totalizacao_atualizada})` : ")");
  if (estado.meta.repo_url) document.getElementById("link-correcao").href = `${estado.meta.repo_url}/issues/new?labels=correcao`;
  window.addEventListener("hashchange", rotear);
  rotear();
})();
