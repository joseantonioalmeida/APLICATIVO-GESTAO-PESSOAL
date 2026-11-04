from http import HTTPStatus

import httpx

from ..apoio.api import UsuarioTeste, criar_usuario
from ..apoio.identidade import codigo_de_erro
from .util import HOJE, URL, campo_de_erro, categoria, criar, listar


async def test_indicadores_5_5_3(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    """90, 60 e 30 min; uma concluída: total 3, 1, 2 e 3h."""
    a = await criar(
        cliente,
        usuario,
        nome="Atividade A",
        horario_inicial="08:00",
        horario_final="09:30",
    )
    b = await criar(
        cliente,
        usuario,
        nome="Atividade B",
        horario_inicial="10:00",
        horario_final="11:00",
    )
    await criar(
        cliente,
        usuario,
        nome="Atividade C",
        horario_inicial="12:00",
        horario_final="12:30",
    )
    resposta = await cliente.put(
        f"{URL}/{a['id']}/situacao",
        json={"situacao": "CONCLUIDA"},
        headers=usuario.cabecalhos,
    )
    assert resposta.status_code == HTTPStatus.OK
    ind = (await listar(cliente, usuario))["indicadores"]
    assert ind == {
        "total": 3,
        "concluidas": 1,
        "pendentes": 2,
        "tempo_total_minutos": 180,
    }
    await cliente.put(
        f"{URL}/{b['id']}/situacao",
        json={"situacao": "CONCLUIDA"},
        headers=usuario.cabecalhos,
    )
    ind = (await listar(cliente, usuario))["indicadores"]
    assert (ind["total"], ind["concluidas"], ind["pendentes"]) == (3, 2, 1)
    assert ind["tempo_total_minutos"] == 180


async def test_filtro_por_categoria_5_5_4(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    estudo = await categoria(cliente, usuario, "Estudo")
    lazer = await categoria(cliente, usuario, "Lazer")
    await criar(
        cliente,
        usuario,
        nome="Estudar A",
        categoria_id=estudo,
        horario_inicial="08:00",
        horario_final="09:30",
    )
    await criar(
        cliente,
        usuario,
        nome="Estudar B",
        categoria_id=estudo,
        horario_inicial="10:00",
        horario_final="10:30",
    )
    await criar(
        cliente,
        usuario,
        nome="Jogar um pouco",
        categoria_id=lazer,
        horario_inicial="22:00",
        horario_final="23:00",
    )
    r = await listar(cliente, usuario, categoria_id=estudo)
    assert [i["nome"] for i in r["itens"]] == ["Estudar A", "Estudar B"]
    assert r["indicadores"] == {
        "total": 2,
        "concluidas": 0,
        "pendentes": 2,
        "tempo_total_minutos": 120,
    }
    assert r["filtros_ativos"] is True
    assert r["total_data"] == 3


async def test_estado_vazio_e_total_do_dia(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    vazio = await listar(cliente, usuario)
    assert vazio["itens"] == []
    assert vazio["total_data"] == 0
    assert vazio["filtros_ativos"] is False
    assert vazio["eh_hoje"] is True
    assert vazio["proximo_cursor"] is None
    outro_dia = await listar(cliente, usuario, data="2026-10-14")
    assert outro_dia["eh_hoje"] is False
    padrao = await cliente.get(URL, headers=usuario.cabecalhos)
    assert padrao.json()["data"] == HOJE


async def test_filtros_de_situacao_prioridade_e_busca(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    await criar(
        cliente,
        usuario,
        nome="Treino na academia",
        prioridade="MEDIA",
        horario_inicial="07:00",
        horario_final="08:00",
    )
    feito = await criar(
        cliente,
        usuario,
        nome="Almoço leve",
        prioridade="BAIXA",
        horario_inicial="12:00",
        horario_final="13:00",
    )
    await criar(
        cliente,
        usuario,
        nome="100% focado_agora",
        prioridade="ALTA",
        horario_inicial="14:00",
        horario_final="15:00",
    )
    await cliente.put(
        f"{URL}/{feito['id']}/situacao",
        json={"situacao": "CONCLUIDA"},
        headers=usuario.cabecalhos,
    )
    pend = await listar(cliente, usuario, situacao="PENDENTE")
    assert pend["indicadores"]["total"] == 2
    assert pend["indicadores"]["concluidas"] == 0
    conc = await listar(cliente, usuario, situacao="CONCLUIDA")
    assert [i["nome"] for i in conc["itens"]] == ["Almoço leve"]
    assert conc["indicadores"]["pendentes"] == 0
    alta = await listar(cliente, usuario, prioridade="ALTA")
    assert [i["nome"] for i in alta["itens"]] == ["100% focado_agora"]
    assert [
        i["nome"]
        for i in (await listar(cliente, usuario, busca="  TREINO "))["itens"]
    ] == ["Treino na academia"]
    # Curingas do LIKE são literais.
    assert [
        i["nome"]
        for i in (await listar(cliente, usuario, busca="100%"))["itens"]
    ] == ["100% focado_agora"]
    assert (await listar(cliente, usuario, busca="_"))["indicadores"][
        "total"
    ] == 1
    assert (await listar(cliente, usuario, busca="%"))["indicadores"][
        "total"
    ] == 1
    assert (await listar(cliente, usuario, busca="inexistente"))["itens"] == []


async def test_ordenacoes(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    await criar(
        cliente,
        usuario,
        nome="Tarde baixa",
        prioridade="BAIXA",
        horario_inicial="15:00",
        horario_final="16:00",
    )
    await criar(
        cliente,
        usuario,
        nome="Manhã alta",
        prioridade="ALTA",
        horario_inicial="09:00",
        horario_final="10:00",
    )
    await criar(
        cliente,
        usuario,
        nome="Cedo média",
        prioridade="MEDIA",
        horario_inicial="07:00",
        horario_final="08:00",
    )
    await criar(
        cliente,
        usuario,
        nome="Tarde alta",
        prioridade="ALTA",
        horario_inicial="13:00",
        horario_final="14:00",
    )

    def nomes(r: dict) -> list[str]:
        return [i["nome"] for i in r["itens"]]

    assert nomes(await listar(cliente, usuario)) == [
        "Cedo média",
        "Manhã alta",
        "Tarde alta",
        "Tarde baixa",
    ]
    assert nomes(await listar(cliente, usuario, ordenacao="PRIORIDADE")) == [
        "Manhã alta",
        "Tarde alta",
        "Cedo média",
        "Tarde baixa",
    ]
    assert nomes(await listar(cliente, usuario, ordenacao="RECENTES")) == [
        "Tarde alta",
        "Cedo média",
        "Manhã alta",
        "Tarde baixa",
    ]


async def test_paginacao_mantem_totais_sem_duplicar(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    """23 atividades, página de 10: totais sempre sobre as 23 (5.5.8)."""
    for i in range(23):
        hora = f"{i // 2 + 1:02d}:{(i % 2) * 30:02d}"
        fim = f"{(i // 2 + 1):02d}:{(i % 2) * 30 + 15:02d}"
        await criar(
            cliente,
            usuario,
            nome=f"Atividade {i:02d}",
            horario_inicial=hora,
            horario_final=fim,
            prioridade=["BAIXA", "MEDIA", "ALTA"][i % 3],
        )
    for ordenacao in ("HORARIO", "PRIORIDADE", "RECENTES"):
        vistos: list[str] = []
        cursor = None
        paginas = 0
        while True:
            params = {"ordenacao": ordenacao, "limite": 10}
            if cursor:
                params["cursor"] = cursor
            pagina = await listar(cliente, usuario, **params)
            assert pagina["indicadores"]["total"] == 23
            assert pagina["indicadores"]["tempo_total_minutos"] == 23 * 15
            vistos += [i["id"] for i in pagina["itens"]]
            paginas += 1
            cursor = pagina["proximo_cursor"]
            if cursor is None:
                break
        assert paginas == 3, ordenacao
        assert len(vistos) == len(set(vistos)) == 23, ordenacao


async def test_cursor_de_outro_filtro_e_recusado(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    for i in range(3):
        await criar(
            cliente,
            usuario,
            nome=f"Item {i}",
            horario_inicial=f"0{i + 1}:00",
            horario_final=f"0{i + 1}:30",
        )
    pagina = await listar(cliente, usuario, limite=1)
    cursor = pagina["proximo_cursor"]
    assert cursor
    for params in (
        {"busca": "x"},
        {"ordenacao": "PRIORIDADE"},
        {"data": "2026-10-14"},
    ):
        resposta = await cliente.get(
            URL,
            params={"data": HOJE, "limite": 1, "cursor": cursor} | params,
            headers=usuario.cabecalhos,
        )
        assert resposta.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert codigo_de_erro(resposta) == "CURSOR_INVALIDO"
    lixo = await cliente.get(
        URL, params={"cursor": "lixo"}, headers=usuario.cabecalhos
    )
    assert codigo_de_erro(lixo) == "CURSOR_INVALIDO"


async def test_parametros_invalidos(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    for params in (
        {"limite": 0},
        {"limite": 51},
        {"data": "2026-13-01"},
        {"situacao": "X"},
        {"busca": "x" * 101},
        {"categoria_id": "abc"},
    ):
        resposta = await cliente.get(
            URL, params=params, headers=usuario.cabecalhos
        )
        assert resposta.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, params
    assert "data" in campo_de_erro(
        (
            await cliente.get(
                URL, params={"data": "x"}, headers=usuario.cabecalhos
            )
        ).json()
    )


async def test_pendencias_anteriores(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    vazio = await cliente.get(
        f"{URL}/pendencias-anteriores", headers=usuario.cabecalhos
    )
    assert vazio.json() == {"quantidade": 0, "data_mais_antiga": None}
    antiga = await criar(
        cliente, usuario, nome="Atrasada antiga", data="2026-10-02"
    )
    await criar(cliente, usuario, nome="Atrasada recente", data="2026-10-10")
    feita = await criar(
        cliente, usuario, nome="Atrasada feita", data="2026-10-05"
    )
    await cliente.put(
        f"{URL}/{feita['id']}/situacao",
        json={"situacao": "CONCLUIDA"},
        headers=usuario.cabecalhos,
    )
    await criar(cliente, usuario, nome="De hoje")
    await criar(cliente, usuario, nome="Futura", data="2026-10-20")
    r = await cliente.get(
        f"{URL}/pendencias-anteriores", headers=usuario.cabecalhos
    )
    assert r.json() == {"quantidade": 2, "data_mais_antiga": "2026-10-02"}
    # As pendências não migram para hoje (5.2.1).
    assert (await listar(cliente, usuario))["indicadores"]["total"] == 1
    assert antiga["data"] == "2026-10-02"


async def test_isolamento_entre_usuarios(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    outro = await criar_usuario(cliente)
    minha = await criar(cliente, usuario, nome="Só minha")
    assert (await listar(cliente, outro))["indicadores"]["total"] == 0
    for metodo, caminho, kw in (
        ("GET", f"{URL}/{minha['id']}", {}),
        ("PATCH", f"{URL}/{minha['id']}", {"json": {"nome": "Invadida"}}),
        (
            "PUT",
            f"{URL}/{minha['id']}/situacao",
            {"json": {"situacao": "CONCLUIDA"}},
        ),
        ("DELETE", f"{URL}/{minha['id']}", {}),
    ):
        r = await cliente.request(
            metodo, caminho, headers=outro.cabecalhos, json=kw.get("json")
        )
        assert r.status_code == HTTPStatus.NOT_FOUND, metodo
        assert codigo_de_erro(r) == "RECURSO_NAO_ENCONTRADO"
    assert (await listar(cliente, usuario))["itens"][0]["nome"] == "Só minha"


async def test_detalhe_e_rotas_estaticas_antes_do_id(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    criada = await criar(cliente, usuario)
    detalhe = await cliente.get(
        f"{URL}/{criada['id']}", headers=usuario.cabecalhos
    )
    assert detalhe.status_code == HTTPStatus.OK
    assert detalhe.json()["id"] == criada["id"]
    invalido = await cliente.get(
        f"{URL}/nao-e-uuid", headers=usuario.cabecalhos
    )
    assert invalido.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    sem_auth = await cliente.get(f"{URL}/pendencias-anteriores")
    assert sem_auth.status_code == HTTPStatus.UNAUTHORIZED
