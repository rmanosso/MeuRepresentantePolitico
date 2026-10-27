"""Configurações centrais do projeto Meu Representante."""
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CACHE = RAIZ / "cache"            # downloads do TSE (não versionado)
DADOS = RAIZ / "dados"            # conteúdo curado (versionado)
DOSSIES = DADOS / "dossies"       # um YAML por candidato
PRIVADO = DADOS / "privado"       # itens em conferência (fora do git)
WEB = RAIZ / "web"                # HTML/CSS/JS do site
SAIDA = RAIZ / "site"             # site gerado (não versionado)
CARDS = RAIZ / "cards"            # imagens para redes sociais (não versionado)

# Endereço do repositório público (ex.: "https://github.com/usuario/MeuRepresentante").
# Habilita os links de correção e contribuição no site.
REPO_URL = "https://github.com/rmanosso/MeuRepresentantePolitico"
INSTAGRAM = "@meurepresentantepolitico"

ANO = 2026
DATA_ELEICAO = "2026-10-04"
DATA_SEGUNDO_TURNO_TXT = "25 de outubro de 2026"

TSE_CDN = "https://cdn.tse.jus.br/estatistica/sead/odsele"
URL_CANDIDATOS = f"{TSE_CDN}/consulta_cand/consulta_cand_{ANO}.zip"
URL_BENS = f"{TSE_CDN}/bem_candidato/bem_candidato_{ANO}.zip"

# Códigos das eleições de 2026 no TSE (resultados.tse.jus.br/oficial/comum/config/ele-c.json)
CD_ELEICAO_FEDERAL = "6257"    # Presidente
CD_ELEICAO_ESTADUAL = "6259"   # Governador, Senador, Deputados
CD_ELEICAO_FEDERAL_T2 = "6258"   # Presidente, 2º turno ("cdt2" no ele-c.json)
CD_ELEICAO_ESTADUAL_T2 = "6260"  # Governador, 2º turno

# Disputas que se resolveram fora do caminho normal, explicadas na página do 2º turno.
NOTAS_2T = [
    {"texto": "No Rio de Janeiro não houve 2º turno. O TSE manteve o indeferimento da candidatura de Anthony "
              "Garotinho e os votos dele foram anulados. Na retotalização de 10/10, Douglas Ruas passou a ter "
              "50,88% dos votos válidos e o TRE-RJ o proclamou eleito no 1º turno em 15/10.",
     "fontes": [
         {"titulo": "TRE-RJ proclama Douglas Ruas eleito para o governo do Rio de Janeiro", "veiculo": "Agência Brasil",
          "url": "https://agenciabrasil.ebc.com.br/justica/noticia/2026-10/tre-rj-proclama-douglas-ruas-eleito-para-o-governo-do-rio-de-janeiro"},
         {"titulo": "Votos de Garotinho são anulados e Douglas Ruas é eleito no 1º turno no RJ", "veiculo": "Poder360",
          "url": "https://www.poder360.com.br/poder-eleicoes-2026/votos-de-garotinho-sao-anulados-e-douglas-ruas-e-eleito-no-1o-turno-no-rj/"},
     ]},
]
SQ_ELEICAO_DIVULGACAND = "20322002026"

URL_FOTO = "https://resultados.tse.jus.br/oficial/ele{ano}/{cd}/fotos/{uf}/{sq}.jpeg"
URL_DIVULGACAND = "https://divulgacandcontas.tse.jus.br/divulga/#/candidato/{ano}/{sqele}/{uf}/{sq}"

# Os três pilares da navegação. Cores escolhidas para NÃO coincidir com as
# cores tradicionalmente associadas a partidos ou campos políticos.
PILARES = {
    "executivo": {
        "nome": "Executivo",
        "descricao": "Presidência da República e Governos estaduais",
        "cor": "#6D28D9",
        "cargos": ["PRESIDENTE", "GOVERNADOR"],
    },
    "senado": {
        "nome": "Senado",
        "descricao": "Senado Federal — representação dos estados",
        "cor": "#0E7490",
        "cargos": ["SENADOR"],
    },
    "camara": {
        "nome": "Câmaras",
        "descricao": "Câmara dos Deputados, Assembleias Legislativas e Câmara Legislativa do DF",
        "cor": "#B45309",
        "cargos": ["DEPUTADO FEDERAL", "DEPUTADO ESTADUAL", "DEPUTADO DISTRITAL"],
    },
}

# Cargos que aparecem apenas vinculados ao titular (chapa)
CARGOS_VINCULADOS = {
    "VICE-PRESIDENTE": "PRESIDENTE",
    "VICE-GOVERNADOR": "GOVERNADOR",
    "1º SUPLENTE": "SENADOR",
    "2º SUPLENTE": "SENADOR",
}

ORDEM_CARGOS = ["PRESIDENTE", "GOVERNADOR", "SENADOR",
                "DEPUTADO FEDERAL", "DEPUTADO ESTADUAL", "DEPUTADO DISTRITAL"]

UFS = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas", "BA": "Bahia",
    "CE": "Ceará", "DF": "Distrito Federal", "ES": "Espírito Santo", "GO": "Goiás",
    "MA": "Maranhão", "MT": "Mato Grosso", "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais", "PA": "Pará", "PB": "Paraíba", "PR": "Paraná",
    "PE": "Pernambuco", "PI": "Piauí", "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte", "RS": "Rio Grande do Sul", "RO": "Rondônia",
    "RR": "Roraima", "SC": "Santa Catarina", "SP": "São Paulo", "SE": "Sergipe",
    "TO": "Tocantins",
}

# Situação de totalização (DS_SIT_TOT_TURNO) -> categoria do site
RESULTADOS = {
    "ELEITO": "eleito",
    "ELEITO POR QP": "eleito",
    "ELEITO POR MÉDIA": "eleito",
    "2º TURNO": "segundo_turno",
    "SUPLENTE": "suplente",
    "NÃO ELEITO": "nao_eleito",
}
