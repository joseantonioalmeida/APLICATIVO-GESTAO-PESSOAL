from http import HTTPStatus

import httpx

from ..apoio.api import UsuarioTeste, chave_nova
from ..apoio.identidade import codigo_de_erro
from .util import HOJE, URL, campo_de_erro, categoria, criar, listar


async def post(
    cliente: httpx.AsyncClient,
    usuario: UsuarioTeste,
    corpo: dict,
    chave: str | None = None,
) -> httpx.Response:
    return await cliente.post(
        URL,
        json=corpo,
        headers={
            **usuario.cabecalhos,
            "Idempotency-Key": chave or chave_nova(),
        },
    )


async def test_cadastro_valido(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    corpo = await criar(
        cliente,
        usuario,
        nome="  Estudar para a prova  ",
        descricao="Revisar capítulos 3 a 5 do livro de química orgânica",
        prioridade="ALTA",
    )
    assert corpo["nome"] == "Estudar para a prova"
    assert corpo["horario_inicial"] == "08:00"
    assert corpo["horario_final"] == "10:00"
    assert corpo["duracao_minutos"] == 120
    assert corpo["situacao"] == "PENDENTE"
    assert corpo["concluida_em"] is None
    assert corpo["prioridade"] == "ALTA"
    assert corpo["recorrente"] is False
    assert corpo["serie"] is None
    assert corpo["numero_ocorrencia"] is None
    assert corpo["categoria"]["nome"] == "Estudo"
    assert corpo["descricao"].startswith("Revisar capítulos")
    assert corpo["descricao_previa"] == "Revisar capítulos 3 a 5 do liv…"
    assert len(corpo["descricao_previa"]) == 31


async def test_prioridade_inicial_baixa_e_sem_descricao(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    corpo = await criar(cliente, usuario)
    assert corpo["prioridade"] == "BAIXA"
    assert corpo["descricao"] is None
    assert corpo["descricao_previa"] is None


async def test_exige_autenticacao_e_chave(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    sem_auth = await cliente.post(URL, json={})
    assert sem_auth.status_code == HTTPStatus.UNAUTHORIZED
    sem_chave = await cliente.post(URL, json={}, headers=usuario.cabecalhos)
    assert codigo_de_erro(sem_chave) == "IDEMPOTENCIA_CHAVE_AUSENTE"


async def test_campos_obrigatorios_com_mensagens_literais(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    resposta = await post(cliente, usuario, {})
    assert resposta.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    mensagens = {c["campo"]: c["mensagem"] for c in resposta.json()["campos"]}
    assert mensagens["nome"] == "Informe o nome da atividade"
    assert mensagens["categoria_id"] == "Selecione uma categoria"
    assert mensagens["data"] == "Informe uma data válida"
    assert "horario_inicial" in mensagens
    assert "horario_final" in mensagens
    assert campo_de_erro(resposta.json())["nome"] == "NOME_OBRIGATORIO"


async def test_validacoes_de_campo(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    cat = await categoria(cliente, usuario)
    base = {
        "nome": "Nome válido",
        "categoria_id": cat,
        "data": HOJE,
        "horario_inicial": "08:00",
        "horario_final": "09:00",
    }
    casos = {
        "nome_so_espacos": ({"nome": "   "}, "nome", "NOME_OBRIGATORIO"),
        "nome_curto": ({"nome": "ab"}, "nome", "TAMANHO_MINIMO"),
        "nome_longo": ({"nome": "x" * 101}, "nome", "TAMANHO_MAXIMO"),
        "data_inexistente": ({"data": "2026-02-30"}, "data", "DATA_INVALIDA"),
        "data_formato_br": ({"data": "13/10/2026"}, "data", "DATA_INVALIDA"),
        "final_igual": (
            {"horario_final": "08:00"},
            "horario_final",
            "HORARIO_FINAL_INVALIDO",
        ),
        "final_menor": (
            {"horario_final": "07:00"},
            "horario_final",
            "HORARIO_FINAL_INVALIDO",
        ),
        "horario_com_segundos": (
            {"horario_inicial": "08:00:30"},
            "horario_inicial",
            "HORARIO_INVALIDO",
        ),
        "horario_24": (
            {"horario_final": "24:00"},
            "horario_final",
            "HORARIO_INVALIDO",
        ),
        "descricao_longa": (
            {"descricao": "x" * 201},
            "descricao",
            "TAMANHO_MAXIMO",
        ),
        "prioridade_invalida": (
            {"prioridade": "URGENTE"},
            "prioridade",
            "VALOR_NAO_PERMITIDO",
        ),
        "ate_data_sem_data": (
            {"repeticao": {"periodicidade": "DIARIA", "termino": "ATE_DATA"}},
            "repeticao",
            "DATA_FINAL_OBRIGATORIA",
        ),
    }
    for nome, (alteracao, campo, codigo) in casos.items():
        resposta = await post(cliente, usuario, base | alteracao)
        assert resposta.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, nome
        assert campo_de_erro(resposta.json()).get(campo) == codigo, nome
    nenhuma = await listar(cliente, usuario)
    assert nenhuma["indicadores"]["total"] == 0


async def test_descricao_vazia_vira_nula_e_limite_exato(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    vazia = await criar(cliente, usuario, descricao="   ")
    assert vazia["descricao"] is None
    cheia = await criar(
        cliente,
        usuario,
        descricao="x" * 200,
        horario_inicial="11:00",
        horario_final="12:00",
    )
    assert len(cheia["descricao"]) == 200


async def test_categoria_inexistente_ou_inativa(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    inexistente = await post(
        cliente,
        usuario,
        {
            "nome": "Ler um livro",
            "categoria_id": "01900000-0000-7000-8000-000000000000",
            "data": HOJE,
            "horario_inicial": "08:00",
            "horario_final": "09:00",
        },
    )
    assert inexistente.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert (
        campo_de_erro(inexistente.json())["categoria_id"]
        == "CATEGORIA_INVALIDA"
    )
    malformada = await post(
        cliente,
        usuario,
        {
            "nome": "Ler um livro",
            "categoria_id": "nao-e-uuid",
            "data": HOJE,
            "horario_inicial": "08:00",
            "horario_final": "09:00",
        },
    )
    assert (
        campo_de_erro(malformada.json())["categoria_id"] == "FORMATO_INVALIDO"
    )


async def test_repeticao_com_data_final_anterior(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    resposta = await post(
        cliente,
        usuario,
        {
            "nome": "Treino na academia",
            "categoria_id": await categoria(cliente, usuario, "Saúde"),
            "data": "2026-10-20",
            "horario_inicial": "17:00",
            "horario_final": "18:00",
            "repeticao": {
                "periodicidade": "SEMANAL",
                "termino": "ATE_DATA",
                "data_final": "2026-10-19",
            },
        },
    )
    assert resposta.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert (
        campo_de_erro(resposta.json())["repeticao.data_final"]
        == "DATA_FINAL_REPETICAO_INVALIDA"
    )


async def test_mesma_chave_nao_duplica(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    chave = chave_nova()
    primeira = await criar(cliente, usuario, chave=chave)
    segunda = await criar(cliente, usuario, chave=chave)
    assert primeira == segunda
    assert (await listar(cliente, usuario))["indicadores"]["total"] == 1


async def test_sobreposicao_exige_confirmacao(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    existente = await criar(cliente, usuario, nome="Estudar para a prova")
    cat = await categoria(cliente, usuario)
    corpo = {
        "nome": "Reunião rápida",
        "categoria_id": cat,
        "data": HOJE,
        "horario_inicial": "09:00",
        "horario_final": "11:00",
    }
    conflito = await post(cliente, usuario, corpo)
    assert conflito.status_code == HTTPStatus.CONFLICT
    assert codigo_de_erro(conflito) == "SOBREPOSICAO_HORARIO"
    assert conflito.json()["detalhes"]["conflitos"] == [
        {
            "id": existente["id"],
            "nome": "Estudar para a prova",
            "horario_inicial": "08:00",
            "horario_final": "10:00",
        }
    ]
    assert (await listar(cliente, usuario))["indicadores"]["total"] == 1
    confirmado = await post(
        cliente, usuario, {**corpo, "confirmar_sobreposicao": True}
    )
    assert confirmado.status_code == HTTPStatus.CREATED
    assert (await listar(cliente, usuario))["indicadores"]["total"] == 2


async def test_horarios_encostados_nao_se_sobrepoem(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    await criar(cliente, usuario)
    cat = await categoria(cliente, usuario)
    resposta = await post(
        cliente,
        usuario,
        {
            "nome": "Logo depois",
            "categoria_id": cat,
            "data": HOJE,
            "horario_inicial": "10:00",
            "horario_final": "11:00",
        },
    )
    assert resposta.status_code == HTTPStatus.CREATED


async def test_datas_passadas_sao_permitidas(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    corpo = await criar(cliente, usuario, data="2020-01-15")
    assert corpo["situacao"] == "PENDENTE"
    assert corpo["data"] == "2020-01-15"


async def test_openapi_documenta_os_endpoints(
    cliente: httpx.AsyncClient,
) -> None:
    resposta = await cliente.get("/openapi.json")
    assert resposta.status_code == HTTPStatus.OK
    caminhos = resposta.json()["paths"]
    assert "/api/v1/atividades" in caminhos
    assert "/api/v1/atividades/pendencias-anteriores" in caminhos
    assert "/api/v1/atividades/{atividade_id}/situacao" in caminhos
    assert "/api/v1/categorias/financeiras" in caminhos
