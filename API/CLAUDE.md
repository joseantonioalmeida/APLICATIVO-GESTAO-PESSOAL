# 🛡️ Diretrizes de Sistema - APLICATIVO GESTÃO PESSOAL E FINANÇAS

Este arquivo contém as regras absolutas de arquitetura, negócio e fluxo de trabalho. **Leia-o integralmente antes de iniciar qualque>

---

## 1. DIRETRIZES GLOBAIS DE COMPORTAMENTO
- **Idioma:** Comunique-se, documente e comente sempre em **Português do Brasil (PT-BR)**.
- **Transparência:** Explique as coisas de forma concisa, simples e direta. Sem jargões desnecessários.
- **Zero Surpresas:** NUNCA altere, exclua ou refatore arquivos sem antes me explicar o que será alterado e obter aprovação explícit>
- **Zero Commits:** Nunca execute `git commit` por conta própria. Apenas gere o código, rode os testes e apresente os relatórios.
- **Anti-Alucinação:** Não confie na memória do chat para contratos longos. Leia sempre os arquivos `.md` e os códigos fonte reais d>

---

## 2. PADRÕES DE CÓDIGO E ARQUITETURA
- **Nomenclatura:**
  - Variáveis, funções, métodos e nomes de arquivos: `snake_case`.
  - Classes, Models (SQLAlchemy) e Schemas (Pydantic): `PascalCase`.
- **Qualidade e Tipagem:** O código deve passar limpo nas seguintes ferramentas de CI local antes de ser considerado pronto:
  - `uv run ruff check --fix .`
  - `uv run ruff format .`
  - `uv run pyright` (Nenhum erro de tipagem é tolerado).
- **Banco de Dados:** Utilização exclusiva do SQLAlchemy (AsyncSession) e Alembic para migrations.

---

1 - TELA DE LOGIN
	1.1 - CAMPOS OBRIGATÓRIO:
		EMAIL
		SENHA

2 - TELA DE REGISTRO (CRIAR CONTA)
	2.1 - CAMPOS ORBIGATÓRIOS:
		NOME COMPLETO
		EMAIL
		SENHA
		CONFIRMAR SENHA
		DATA DE NASCIMENTO(MODELO BR)

3 - TELA DE ESQUECEU SENHA (FLUXO)
	Objetivo: Nessas telas o objetivo é que o usuário consiga recuperar a senha caso ele tenha perdido ou esquecido. E para isso ele deverá passar por três processos: enviar o código 		de recuperação para o e-mail, digitar o código recebido e criar uma senha nova. Se esses três passos forem feitos, o usuário poderá ter acesso ao aplicativo novamente.
	3.1 - PRIMEIRA TELA(COLOCAR O EMAIL)
		3.1.1 - CAMPOS OBRIGATÓRIOS:
			EMAIL
		E TERÁ UM BOTÃO ENVIAR(SUBMIT) PARA RECEBER OS CÓDIGO DE 8 DÍGITOS, APÓS APERTAR O BOTÃO IRAR PARA A SEGUNTA TELA DE COLOCAR OS DÍGITOS.
	
	3.2 - SEGUNDA TELA (COLOCAR OS DÍGITOS)
		3.2.1 - CAMPOS OBRIGATÓRIOS:
			CÓDIGO DE 8 DÍGITOS
		E TERÁ UM BOTÃO DE ENVIAR(SUBMIT), APÓS APERTAR O BOTÃO IRÁ PARA A TERCEIRA TELA DE CRIAR UMA NOVA SENHA. 
		E TERÁ UM TEXTO DE REENVIAR CÓDIGO (QUANDO APERTADO, ENVIARÁ OUTRO CÓDIGO, E ESSE NOVO CÓDIGO SERÁ O VÁLIDO E NÃO O ANTIGO CÓDIGO)
		REGRAS: { SE O CÓDIGO DIGITADO FOR DIFERENTE DO CÓDIGO ENVIADO, APARECE UMA MENSAGEM DE CÓDIGO INVÁLIDO.}

	3.3 - TERCEIRA TELA (COLOCAR UMA NOVA SENHA)
		3.1.1 - CAMPOS OBRIGATÓRIOS:
			NOVA SENHA
			CONFIRMAR A SENHA NOVA
		E TERÁ UM BOTÃO DE REDEFINIR SENHA, APÓS APERTAR NO BOTÃO, SERÁ REDIRECIONADO PARA A TELA DE LOGIN, PARA COLOCAR O EMAIL E SENHA.

	3.4 - CRITÉRIOS DE ACEITE:
		3.4.1 - O campo email deverá ser obrigatório, válido para email (estrutura de um e-mail com user@dominio) e deverá estar cadastrado no banco de dados.

		3.4.2 - Se o sistema, após o clique verificar que o "email" está incorreto, então deverá apresentar uma mensagem: Não foi possível encontrar seu email.

		3.4.3 - Se o sistema, após o clique verificar que o email está correto, ele deverá receber um código de verificação no e-mail associado à sua conta.

		3.4.4 - Assunto do E-mail:
			Assunto: Nome da pessoa, aqui está seu código
			Mensagem:
			Olá, {Nome da pessoa}. 
			Recebemos uma solicitação para redefinir a senha de sua conta MinhaVida.
			{XXXXXXXX}
			Insira este código para concluir a redefinição.
			Obrigado por nos ajudar a manter sua conta segura.
			Equipe MinhaVida.

		3.4.5 - O código de verificação deve conter 8 dígitos numéricos.

		3.4.6 - Quando o usuário disponibilizar o email o botão “Enviar” deverá ser habilitado, ao clicar no botão o mesmo deve ser redirecionado para tela onde poderá digitar o 			código de verificação.

		3.4.7 - Quando o usuário digitar o código de verificação corretamente o botão “Enviar” deverá ser habilitado, ao clicar no botão o mesmo deve ser redirecionado para tela 			onde poderá criar a nova senha.

		3.4.8 - Se o sistema, após o clique em “Enviar” verificar que o código de verificação esteja incorreto, uma mensagem de aviso deve ser apresentada na tela:
			"O código de verificação que você inseriu não é válido. Verifique o código e tente novamente."

		3.4.9 - O campo Senha deve ser obrigatório e conter no mínimo 8 caracteres alfanuméricos e especiais e deverá aparecer a seguinte mensagem:
			"A senha deve ter pelo menos 8 caracteres. Para torná-la mais forte, use letras maiúsculas e minúsculas, números e símbolos como ! @ # $ % & * ="

		3.4.10 - Se o sistema, após clicar em “Redefinir senha” verificar que senha não atinge os requisitos necessários, deverá aparecer a seguinte mensagem:
			"A senha informada não atende os requisitos necessários de 8 caracteres"

		3.4.11 - Quando o usuário estiver colocando a senhas e optar por não visualizar a senha, a mesma deverá ser apresentada através de “********”.

		3.4.12 - Quando o usuário estiver colocando a senha ele deverá ser capaz de visualizar a senha caso ele clique na opção “Mostrar” no campo “Senha”.

		3.4.13 - O campo “Confirmar Senha” deve ser igual ao campo “Senha”.

		3.4.14 - Se o sistema, após o clique em “Redefinir senha” verificar que as duas senhas não são idênticas, uma mensagem de aviso deve ser apresentada na tela:
			"As senhas devem ser idênticas"

		3.4.15 - Se o sistema, após o clique em “Redefinir senha” verificar que as duas senhas são idênticas, uma mensagem “Redefinição de senha concluída com sucesso” deverá 				aparecer na tela e em seguida ser redirecionado para tela de login.


4 - TELA INICIAL

	Objetivo: apresentar um resumo do dia e do mês atual, permitir acesso rápido aos cadastros e destacar atividades e compromissos que precisam de atenção.

	4.1 - TERÁ OBRIGATORIAMENTE:

		4.1.1 - IDENTIFICAÇÃO DO USUÁRIO: apresentar uma saudação com o nome do usuário autenticado, como “Olá, {Nome}!”, utilizando o nome cadastrado na conta. O acesso pelo 				avatar deverá direcionar para a área de Perfil.

		4.1.2 - INDICADORES DO MÊS ATUAL:

			- Saldo do mês: total das receitas recebidas no mês menos o total das despesas pagas no mês.
			- Despesas do mês: total dos pagamentos realizados no mês, com identificação visual de saída financeira.
			- Importâncias pendentes do mês: quantidade de ocorrências pendentes cuja data pertença ao mês atual, incluindo as atrasadas desse mesmo mês.

			Mostrar o mês e o ano de referência. O saldo poderá ser positivo, negativo ou zero. Ao abrir Saldo do mês, acessar o Financeiro no mês atual; ao abrir Despesas do 			mês, acessar o mesmo período com a consulta de movimentações filtrada por Despesas. O indicador de Importâncias deverá abrir a tela 7 na consulta Este mês, que 			apresenta os registros pendentes e concluídos do período.

		4.1.3 - IDENTIFICAÇÃO DE HOJE: apresentar a data atual e o dia da semana calculado a partir dessa data. Ao mudar o dia, atualizar o conteúdo relacionado a hoje; ao mudar o 			mês, atualizar também os indicadores mensais.

		4.1.4 - ATIVIDADES DE HOJE: apresentar uma prévia de até três atividades previstas para a data atual. Priorizar pendentes e, depois, concluídas; dentro de cada grupo, 				ordenar pelo horário inicial. Cada item deverá mostrar:

			- Nome da atividade.
			- Categoria, como Estudo ou Saúde.
			- Intervalo planejado, como 08:00 - 10:00.
			- Situação: Pendente ou Concluída.
			- Controle identificado para concluir ou reabrir a atividade.

			Apresentar também o total de atividades do dia e quantas foram concluídas, considerando todas as atividades de hoje, e não somente a prévia. Ao selecionar o nome, 			abrir os detalhes da atividade. “Ver todas as atividades” deverá abrir a tela 5 em Hoje, sem filtros que ocultem atividades. Se houver pendências de dias 				anteriores, oferecer o acesso definido em 5.1.9, sem alterar a data dessas tarefas.

		4.1.5 - RESUMO FINANCEIRO DO DIA:

			- Receitas de hoje: soma dos valores com data de recebimento igual à data atual.
			- Despesas de hoje: soma dos valores com data de pagamento igual à data atual.
			- Saldo do dia: receitas de hoje menos despesas de hoje.

			Os valores deverão considerar movimentações efetivadas. Uma importância com vencimento hoje, mas ainda sem pagamento, não deverá ser somada às despesas. 				Identificar receitas e despesas por texto, além das cores, e apresentar saldo negativo quando ocorrer.

		4.1.6 - ACESSOS RÁPIDOS:

			| Ação | Destino e comportamento |
			| ---  |		     --- |
			| Registrar nova atividade | Abrir a tela 6 com a data de hoje preenchida. |
			| Adicionar receita ou despesa | Apresentar as opções Cadastrar receita e Cadastrar despesa, direcionando para as telas 10 e 11. |
			| Cadastrar importância | Abrir a tela 8. |
			| Ver calendário | Abrir a tela 5 em Hoje, com acesso ao seletor de data. |
			| Ver resumo financeiro | Abrir a tela 9 no mês atual. Este nome substituirá o atalho “Ver relatórios” do protótipo nesta versão. |
			| Perfil | Abrir a área de Perfil, com o mesmo destino do avatar e da navegação inferior. |

		4.1.7 - MOVIMENTAÇÕES RECENTES: este nome substituirá “Atividades recentes”, pois o bloco contém receitas e despesas. Mostrar até cinco movimentações do mês atual, 				ordenadas pela data do recebimento ou pagamento, da mais recente para a mais antiga. Em caso de empate, mostrar primeiro a cadastrada mais recentemente. Cada item 			deverá apresentar:

			- Nome do lançamento.
			- Data do recebimento ou pagamento.
			- Tipo: Receita ou Despesa.
			- Valor, com sinal positivo para receita e negativo para despesa.

			Selecionar um item deverá abrir seus detalhes financeiros. “Ver todas” deverá abrir a consulta completa de movimentações da tela 9 no mês atual, sem filtros 				adicionais.

		4.1.8 - PRÓXIMAS IMPORTÂNCIAS: mostrar até três ocorrências pendentes com data igual ou posterior a hoje, incluindo os próximos meses. Ordenar da data mais próxima para a 			mais distante; na mesma data, considerar o horário, deixando itens sem horário depois dos demais. Cada item deverá apresentar:

			- Nome da importância.
			- Data e horário, quando informado.
			- Valor previsto, quando houver despesa, ou identificação “Sem despesa”.
			- Prazo: “Hoje”, “Amanhã” ou “Em X dias”.

			Selecionar o item deverá abrir seus detalhes na tela 7. “Ver todas” deverá abrir essa tela no filtro Todos, para incluir tanto os compromissos de hoje quanto os 			futuros.

			Se houver importâncias atrasadas, apresentar um aviso separado, como “Você tem X importâncias atrasadas”, com acesso ao filtro Atrasados. Esse aviso deverá incluir 			também atrasos de meses anteriores. Uma lista vazia de próximas importâncias não deverá esconder os atrasos.

		4.1.9 - NOTIFICAÇÕES: o sino do protótipo deverá abrir a lista de lembretes gerados para Importâncias, conforme a tela 8. Mostrar indicador somente quando houver 				notificações não lidas. Ao abrir uma notificação, marcá-la como lida e acessar a importância correspondente; ler uma notificação não concluirá o compromisso nem 			registrará pagamento. Se a importância tiver sido excluída, informar que ela não está mais disponível.

		4.1.10 - NAVEGAÇÃO INFERIOR: Início, Atividades, Financeiro, Importâncias e Perfil, destacando Início e mantendo essa ordem nas demais telas. Se houver um botão “+” 				adicional, ele deverá abrir as opções de cadastro já definidas, sem substituir o acesso ao Financeiro.

	4.2 - REGRAS DE FUNCIONAMENTO:

		4.2.1 - A tela Inicial sempre usará hoje e o mês atual como referência. Consultar outro dia na tela de Atividades ou outro mês no Financeiro não deverá alterar os períodos 			do painel inicial.

		4.2.2 - Os valores financeiros deverão usar as mesmas regras da tela 9: contabilizar cada lançamento uma única vez, pela data do recebimento ou pagamento, preservando os 			centavos. Excluir lançamentos deverá retirá-los dos totais; cadastrar uma importância com valor previsto não deverá alterar o saldo.

		4.2.3 - Apresentar o Saldo do mês como valor calculado, sem a variação percentual ilustrativa do protótipo. A comparação de Despesas do mês seguirá os mesmos intervalos e 			a mesma fórmula das regras 9.2.6 a 9.2.8, com indicação do período comparado e tratamento para uma base anterior igual a zero.

		4.2.4 - O total de importâncias pendentes do mês considerará cada ocorrência recorrente prevista dentro daquele mês, mesmo que ainda não tenha aparecido na prévia. 				Ocorrências concluídas ou excluídas não participarão desse total. O aviso de atrasos terá alcance próprio, anterior a hoje; seus valores não deverão ser somados ao 			indicador mensal, pois os conjuntos podem se sobrepor.

		4.2.5 - Concluir ou reabrir uma atividade pela tela Inicial deverá alterar a mesma ocorrência exibida na tela 5, seguindo as regras dessa tela. Depois da confirmação, 				atualizar a prévia e as quantidades. A ação não deverá gerar receita, despesa ou pagamento de uma importância.

		4.2.6 - Atualizar os blocos ao entrar na tela, ao retornar de um cadastro ou alteração e quando o usuário acionar o comando “Atualizar”, que deverá estar disponível. 				Alterações confirmadas nas atividades, nas movimentações e nas importâncias deverão aparecer em todos os resumos correspondentes, sem exigir novo login.

		4.2.7 - Quando não houver dados, apresentar estados específicos:

			- Atividades: “Nenhuma atividade cadastrada para hoje”, com acesso ao cadastro.
			- Todas as atividades do dia concluídas: manter acesso à lista e apresentar “Todas as atividades de hoje foram concluídas”.
			- Movimentações: “Nenhuma movimentação cadastrada neste mês”, com totais financeiros zerados quando a consulta tiver sido concluída com sucesso.
			- Próximas importâncias: “Nenhuma importância pendente para hoje ou para os próximos dias”, preservando o aviso de atrasos, se houver.

		4.2.8 - Mostrar carregamento por bloco e permitir nova tentativa quando uma consulta falhar. Uma falha não deverá ser apresentada como ausência de registros nem 				transformar valores desconhecidos em zero. Os indicadores financeiros de um mesmo período deverão permanecer coerentes entre si, sem misturar dados anteriores com 			dados recém-atualizados.

	4.3 - CRITÉRIOS DE ACEITE:

		4.3.1 - Com receitas mensais de R$ 2.450,75 e despesas mensais de R$ 1.230,40, mostrar Saldo do mês de R$ 1.220,35, igual ao Financeiro para o mesmo período. Alterar o mês 			consultado no Financeiro não deverá mudar esse resumo da tela Inicial.

		4.3.2 - Com receitas de R$ 100,00 e despesas de R$ 30,00 na data atual, apresentar saldo do dia de R$ 70,00. Lançamentos de ontem, mesmo que cadastrados hoje, não deverão 			entrar nesse resumo diário.

		4.3.3 - Se houver cinco atividades hoje, sendo duas concluídas, apresentar total de cinco e duas concluídas, mesmo que a prévia mostre apenas três. Concluir uma terceira 			atividade deverá atualizar o total de concluídas para três na tela Inicial e na tela de Atividades.

		4.3.4 - Cadastrar uma importância de R$ 99,90 deverá atualizar os blocos de compromissos correspondentes sem alterar despesas ou saldo. Registrar seu pagamento deverá 				retirá-la das pendências, incluí-la no Financeiro uma única vez e atualizar os resumos do período do pagamento.

		4.3.5 - Uma importância futura de outro mês poderá aparecer em Próximas importâncias, mas não contará como pendente do mês atual. Uma importância atrasada de outro mês 			deverá aparecer no aviso de atrasos, mesmo que a prévia de próximas esteja vazia.

		4.3.6 - Ao passar de 31/10 para 01/11, com a tela aberta, atualizar a data, o dia da semana, as atividades de hoje, os totais diários e os indicadores mensais para 				novembro, sem manter outubro sob o novo título.

		4.3.7 - Se a consulta financeira falhar, apresentar o erro no bloco correspondente e permitir tentar novamente; atividades e importâncias já carregadas poderão continuar 			disponíveis. Se a consulta confirmar que não há movimentações, apresentar os zeros e a mensagem de ausência de registros.

5 - TELA DE ATIVIDADES — LISTA DE TAREFAS
	Objetivo: permitir que o usuário consulte as atividades de um dia, acompanhe o planejamento e a conclusão das tarefas e realize cadastro, edição, conclusão, reabertura e exclusão.

	5.1 - TERÁ OBRIGATORIAMENTE:

		5.1.1 - SELETOR DE DATA: permitir consultar dias anteriores e futuros, com o botão “Hoje” para retornar à data atual. Na entrada pela navegação principal ou pela tela 				Inicial, abrir Hoje sem filtros adicionais. Ao retornar dos detalhes sem alterações, preservar a data, os filtros, a ordenação e a posição na lista.

		5.1.2 - BOTÃO “NOVA ATIVIDADE”: abrir a tela 6 com a data selecionada preenchida. O botão flutuante “+”, caso mantido, deverá executar a mesma ação.

		5.1.3 - FILTRO DE CATEGORIA: Todas, Trabalho, Estudo, Saúde, Pessoal, Lazer e Outros, usando as mesmas categorias do cadastro da tela 6.

		5.1.4 - FILTROS COMPLEMENTARES: situação — Todas, Pendentes ou Concluídas — e prioridade — Todas, Baixa, Média ou Alta. Disponibilizar busca pelo nome da atividade, sem 			diferenciar letras maiúsculas e minúsculas, e a opção “Limpar filtros”.

		5.1.5 - INDICADORES DA CONSULTA:

			- Total de atividades: quantidade de ocorrências encontradas para a data e os filtros ativos.
			- Concluídas: quantidade dessas ocorrências com situação Concluída.
			- Pendentes: quantidade dessas ocorrências com situação Pendente.
			- Tempo total planejado: soma das durações previstas dessas ocorrências, incluindo pendentes e concluídas.

			Identificar a data e a existência de filtros ativos. Os indicadores apresentarão valores absolutos da consulta; as variações ilustrativas “+2 hoje” e “+3h 20min” 			do protótipo não serão exibidas nesta proposta.

		5.1.6 - LISTA DE ATIVIDADES: mostrar todas as ocorrências encontradas para a seleção, permitindo carregar a lista em partes. Cada item deverá apresentar:

			- Nome da atividade.
			- Categoria.
			- Prévia da descrição com até 30 caracteres, acrescentando reticências quando houver continuação.
			- Intervalo previsto, como 17:00 - 18:30.
			- Prioridade, identificada por texto.
			- Situação: Pendente ou Concluída.
			- Indicação de repetição, quando houver.
			- Controle para concluir ou reabrir.
			- Menu de três pontos com Editar e Excluir.

			Quando não houver descrição, omitir a prévia. Uma atividade concluída poderá ter o nome riscado, mantendo todas as informações legíveis e a identificação textual 			da situação.

		5.1.7 - ORDENAÇÃO: oferecer Horário inicial, Prioridade e Mais recentes. O padrão será Horário inicial, do mais cedo para o mais tarde. Em Prioridade, ordenar Alta, Média 			e Baixa, usando o horário como desempate. Em Mais recentes, considerar o momento do cadastro, do mais recente para o mais antigo. Manter uma ordem estável em 				empates.

		5.1.8 - DETALHES DA ATIVIDADE: ao selecionar o item, apresentar nome completo, descrição completa de até 200 caracteres, categoria, prioridade, data, horários, duração, 			situação e configuração de repetição. Quando concluída, apresentar também a data e a hora da conclusão. Disponibilizar as mesmas ações aplicáveis à lista.

		5.1.9 - PENDÊNCIAS ANTERIORES: quando houver atividades pendentes com data anterior a hoje, apresentar um aviso com a quantidade total dessas ocorrências, independente dos 			filtros da consulta atual. Ao selecionar “Ver pendências anteriores”, abrir o dia mais antigo que possua pendências, ativar o filtro Pendentes e limpar busca, 				categoria e prioridade. Permitir navegar pelas demais datas e retornar a Hoje.

		5.1.10 - NAVEGAÇÃO INFERIOR: Início, Atividades, Financeiro, Importâncias e Perfil, destacando Atividades e mantendo a mesma ordem das outras telas.

	5.2 - REGRAS DA CONSULTA E DOS INDICADORES:

		5.2.1 - A data planejada da ocorrência determinará em qual dia ela aparecerá, independentemente do momento em que foi cadastrada ou concluída. Atividades pendentes de dias 			anteriores não serão transferidas automaticamente para hoje.

		5.2.2 - Aplicar data, categoria, situação, prioridade e busca em conjunto. “Limpar filtros” deverá restaurar Todas as categorias, Todas as situações, Todas as prioridades 			e busca vazia, mantendo a data escolhida. Mudar somente a ordenação não deverá alterar os totais.

		5.2.3 - A lista e os quatro indicadores deverão usar exatamente os mesmos filtros. Assim, TOTAL = CONCLUÍDAS + PENDENTES. Ao filtrar apenas Concluídas, por exemplo, 				Pendentes deverá ser zero. Os totais deverão considerar todo o resultado, incluindo itens ainda não carregados na tela.

		5.2.4 - Calcular a duração de cada atividade pela diferença entre horário final e inicial, conforme a tela 6. Somar as durações em minutos e apresentar o resultado em 				horas e minutos, como 3h 30min. O tempo será planejado, sem depender de cronômetro ou da hora em que a atividade foi marcada como concluída.

		5.2.5 - Atividades com horários sobrepostos continuarão tendo suas durações somadas, conforme 6.4.4. Duas tarefas de duas horas cada representarão quatro horas de 				planejamento por tarefa, mesmo que compartilhem parte do intervalo no relógio.

		5.2.6 - Enquanto Hoje estiver ativo, acompanhar a mudança da data atual. Se o usuário tiver escolhido uma data específica pelo calendário, manter essa consulta fixa até 			que ele selecione outra data ou acione Hoje.

	5.3 - CONCLUIR E REABRIR ATIVIDADES:

		5.3.1 - Uma nova atividade começará como Pendente. Somente uma ação explícita do usuário deverá marcá-la como Concluída; ultrapassar seu horário ou sua data não será 				suficiente.

		5.3.2 - Ao concluir, registrar a data e a hora da ação e atualizar a ocorrência, a lista, os indicadores e a tela Inicial quando a atividade pertencer a hoje. Permitir 			conclusão antecipada de uma atividade futura, mantendo sua data planejada e identificando o momento real da conclusão nos detalhes.

		5.3.3 - Ao reabrir, devolver a ocorrência para Pendente e deixar de apresentar uma conclusão ativa. Manter data planejada, horários e demais dados. Concluir ou reabrir uma 			ocorrência recorrente não deverá modificar a situação das demais.

		5.3.4 - Com filtros ativos, uma alteração poderá retirar o item da consulta. Por exemplo, ao concluir uma atividade na lista filtrada por Pendentes, removê-la desse 				resultado e apresentar “Atividade concluída”. Na reabertura, apresentar “Atividade reaberta”.

		5.3.5 - Durante o envio, identificar que a ação está em processamento e impedir novos comandos simultâneos para o mesmo item. Repetir a solicitação de concluir não deverá 			reabrir uma atividade já concluída. Se houver uma falha confirmada, preservar ou restaurar o estado anterior. Se a conexão cair sem confirmação do resultado, 				informar que não foi possível confirmar a alteração e consultar a situação do registro na nova tentativa, sem inverter seu estado.

	5.4 - EDITAR E EXCLUIR ATIVIDADES:

		5.4.1 - Editar deverá abrir a tela 6 com os dados preenchidos e o botão “Salvar alterações”. Preservar a identidade da atividade; uma edição não deverá criar outra tarefa 			independente.

		5.4.2 - Ao salvar, atualizar a lista e os indicadores das datas afetadas. Se a data da atividade mudar, retirá-la da data anterior e apresentá-la na nova. Retornar à tela 			5 na data resultante, sem filtros que ocultem o item atualizado. Editar nome, categoria ou horários não deverá alterar automaticamente a situação.

		5.4.3 - Antes de excluir uma atividade sem repetição, apresentar “Deseja excluir a atividade {Nome}?”, com “Cancelar” e “Excluir”. Somente a confirmação deverá remover o 			registro das listas e dos indicadores.

		5.4.4 - Para uma ocorrência recorrente pendente, tanto a edição quanto a exclusão deverão oferecer “Somente esta ocorrência” ou “Esta e as próximas pendentes”, conforme 			6.4.8. O alcance padrão será somente a ocorrência selecionada. Informar claramente o alcance antes da confirmação.

		5.4.5 - O alcance “Esta e as próximas pendentes” deverá ser definido a partir da posição original da ocorrência selecionada na série, antes da edição. Preservar 				ocorrências anteriores e concluídas. Uma ocorrência concluída somente poderá ser editada ou excluída individualmente.

		5.4.6 - Excluir somente uma ocorrência deverá preservar as outras. Excluir esta e as próximas pendentes deverá interromper as ocorrências abrangidas, incluindo as futuras 			que ainda não tenham sido exibidas. Ocorrências excluídas não deverão reaparecer quando a lista for recarregada ou a série for consultada novamente.

		5.4.7 - Se uma edição ou exclusão falhar, informar o erro e manter os dados anteriores. Na edição, preservar o preenchimento para nova tentativa. Ao cancelar uma 				confirmação, não realizar nenhuma alteração.

	5.5 - ESTADOS DA TELA E CRITÉRIOS DE ACEITE:

		5.5.1 - Se não houver atividades na data escolhida, apresentar “Nenhuma atividade cadastrada para esta data”, com acesso a Nova atividade. Se houver atividades, mas 				nenhuma corresponder aos filtros, apresentar “Nenhuma atividade encontrada para os filtros selecionados” e permitir limpar os filtros.

		5.5.2 - Durante a consulta, mostrar carregamento. Em caso de falha, apresentar “Não foi possível carregar suas atividades. Tente novamente”. Não exibir uma falha como 				lista vazia nem apresentar dados da data anterior sob o título da nova data.

		5.5.3 - Com três atividades de 90, 60 e 30 minutos, sendo uma concluída e duas pendentes, mostrar Total 3, Concluídas 1, Pendentes 2 e Tempo total planejado 3h. Ao 				concluir mais uma delas sem filtro de situação, manter Total 3 e Tempo 3h, alterando Concluídas para 2 e Pendentes para 1.

		5.5.4 - Se as atividades de 90 e 30 minutos forem da categoria Estudo, ambas pendentes, filtrar por Estudo deverá mostrar Total 2, Concluídas 0, Pendentes 2 e Tempo total 			planejado 2h. A lista deverá conter somente essas duas atividades.

		5.5.5 - Uma descrição com 100 caracteres deverá permanecer completa nos detalhes e no cadastro, enquanto a lista apresentará apenas os primeiros 30 caracteres e as 				reticências. A prévia não deverá modificar o texto salvo.

		5.5.6 - Ao editar uma atividade das 08:00 - 09:00 para 08:00 - 09:30, atualizar sua duração de 1h para 1h 30min e acrescentar 30 minutos ao tempo total da consulta que a 			inclua. Ao mudar a data, recalcular as duas datas envolvidas.

		5.5.7 - Ao concluir uma ocorrência semanal, manter as seguintes pendentes. Ao excluir somente uma ocorrência, preservar as demais e impedir que a excluída reapareça após 			atualização. Ao excluir esta e as próximas pendentes, preservar as anteriores e as já concluídas.

		5.5.8 - Se a consulta encontrar 23 atividades e apenas dez tiverem sido carregadas na tela, os indicadores deverão considerar as 23. Carregar a próxima parte não deverá 			duplicar itens nem alterar os totais por causa da paginação.

		5.5.9 - Ao mudar o dia com Hoje ativo, consultar o novo dia e atualizar os indicadores. Ao consultar uma data fixa, mantê-la após a virada do dia. Pendências anteriores 			deverão continuar disponíveis em suas datas originais e no aviso correspondente.

		5.5.10 - Cliques repetidos em Concluir deverão manter a atividade concluída, sem alternar involuntariamente sua situação. Cancelar uma exclusão deverá preservar o 				registro; confirmar deverá atualizar os indicadores e, quando aplicável, a prévia da tela Inicial.

6 - TELA DE CADASTRAR ATIVIDADE
	Objetivo: permitir que o usuário cadastre uma tarefa, informando o que fará, a categoria e o intervalo de tempo previsto para realizá-la.

	6.1 - CAMPOS OBRIGATÓRIOS:

		6.1.1 - NOME DA ATIVIDADE: entre 3 e 100 caracteres. Exemplo: “Estudar para a prova”. É o campo chamado “Título da atividade” no protótipo; deverá ter o mesmo nome nas 			demais telas.

		6.1.2 - CATEGORIA / TIPO DA ATIVIDADE: seleção única entre Trabalho, Estudo, Saúde, Pessoal, Lazer e Outros. “Categoria” e “tipo” representarão a mesma informação.

		6.1.3 - PRIORIDADE: Baixa, Média ou Alta. O valor inicial será Baixa, conforme o protótipo, e poderá ser alterado.

		6.1.4 - DATA DA ATIVIDADE: data válida no formato brasileiro. Inicialmente, apresentar a data selecionada na tela de Atividades ou a data atual, quando o cadastro for 				aberto pela tela Inicial.

		6.1.5 - HORÁRIO INICIAL: horário previsto para começar a atividade. Exemplo: 08:00.

		6.1.6 - HORÁRIO FINAL: horário previsto para terminar a atividade. Exemplo: 10:00. Esse campo complementa o protótipo e permite calcular o intervalo e o tempo total 				exigidos na tela 5.

	6.2 - CAMPOS OPCIONAIS:

		6.2.1 - DESCRIÇÃO: até 200 caracteres, com contador indicando a quantidade utilizada, conforme o protótipo.

		6.2.2 - REPETIR: Não repetir, Diariamente, Semanalmente ou Mensalmente. O valor inicial será Não repetir.

		6.2.3 - TÉRMINO DA REPETIÇÃO: exibir quando houver repetição. Permitir escolher Sem data final ou Até uma data. Nesta segunda opção, a data final será obrigatória e não 			poderá ser anterior à primeira ocorrência.

	6.3 - TERÁ OBRIGATORIAMENTE:

		6.3.1 - Botão “Salvar atividade”. Durante o envio, apresentar “Salvando...” e impedir novos envios simultâneos.

		6.3.2 - Botão de voltar e opção “Cancelar”. Se houver alterações não salvas, perguntar: “Deseja sair sem salvar a atividade?”, com as opções “Continuar preenchendo” e 				“Descartar alterações”. A mesma proteção deverá valer para a navegação inferior.

		6.3.3 - Identificação dos campos inválidos e mensagens próximas a eles. O botão poderá ser acionado para validar o formulário, mas nenhum cadastro será salvo enquanto 				houver erros.

	6.4 - REGRAS DE FUNCIONAMENTO:

		6.4.1 - Desconsiderar espaços no início e no final do nome. Um nome composto apenas por espaços não será válido.

		6.4.2 - Nesta versão, os dois horários pertencerão à data informada. O horário final deverá ser posterior ao inicial. Atividades que atravessam a meia-noite deverão ser 			divididas em dois registros.

		6.4.3 - Calcular automaticamente a duração pela diferença entre os horários. O indicador “Tempo total” da tela 5 deverá somar as durações das atividades exibidas no dia e 			nos filtros selecionados, incluindo pendentes e concluídas.

		6.4.4 - Se houver sobreposição de horários com outra atividade, apresentar um aviso e permitir “Revisar horários” ou “Salvar mesmo assim”. Atividades sobrepostas 				continuarão tendo suas durações somadas; o indicador representa tempo planejado por tarefa.

		6.4.5 - Toda nova atividade começará como Pendente. Será permitido registrar datas passadas, mas a passagem do horário ou da data não marcará a atividade como 					concluída. Concluir ou reabrir uma atividade na tela 5 deverá atualizar a lista, os indicadores e a tela Inicial.

		6.4.6 - Os 30 caracteres definidos para a descrição na tela 5 limitarão apenas a prévia: mostrar até 30 caracteres do texto e acrescentar reticências quando houver 				continuação. O conteúdo completo, de até 200 caracteres, deverá permanecer disponível ao abrir a atividade.

		6.4.7 - Na repetição diária, manter os horários todos os dias; na semanal, repetir no mesmo dia da semana; na mensal, repetir no mesmo dia do mês. Se esse dia não existir, 			usar o último dia daquele mês, preservando o dia original para os meses seguintes. A data final da repetição será inclusiva.

		6.4.8 - Cada ocorrência terá sua própria situação. Concluir uma ocorrência não concluirá as próximas. Ao editar ou excluir uma atividade recorrente pendente, permitir 				escolher “Somente esta ocorrência” ou “Esta e as próximas pendentes”. Alterações na série deverão preservar ocorrências anteriores e concluídas; uma ocorrência 			concluída só poderá ser alterada individualmente. Alterações na data da série definirão a nova referência das próximas ocorrências.

		6.4.9 - Após salvar, exibir “Atividade cadastrada com sucesso” e abrir a tela de Atividades na data cadastrada. Caso a atividade seja de hoje, atualizar também a tela 				Inicial. Na edição, reutilizar o formulário preenchido, com o botão “Salvar alterações”, atualizando o registro existente.

	6.5 - CRITÉRIOS DE ACEITE:

		6.5.1 - Se um campo obrigatório estiver vazio ou inválido, não salvar e apresentar uma mensagem específica, como “Informe o nome da atividade” ou “Selecione uma 				categoria”.

		6.5.2 - Se a data não existir, apresentar “Informe uma data válida”. Se o horário final for igual ou anterior ao inicial, apresentar “O horário final deve ser posterior ao 			horário inicial”.

		6.5.3 - Ao cadastrar uma atividade das 08:00 às 10:00, exibir o intervalo corretamente, considerar 2 horas no tempo total e acrescentar uma atividade ao total e às 				pendentes, quando ela corresponder aos filtros da lista.

		6.5.4 - Impedir descrições com mais de 200 caracteres e preservar integralmente as descrições válidas, mesmo quando a lista mostrar somente a prévia.

		6.5.5 - Uma atividade semanal iniciada em 08/10/2026 e encerrada em 22/10/2026 deverá ter ocorrências em 08, 15 e 22 de outubro. Concluir a primeira não deverá modificar 			as demais.

		6.5.6 - Se ocorrer uma falha ao salvar, manter os campos preenchidos e apresentar “Não foi possível salvar a atividade. Tente novamente”. Cliques repetidos ou uma nova 			tentativa do mesmo envio não deverão criar registros duplicados.

		6.5.7 - Ao confirmar o descarte, sair sem criar ou alterar a atividade. Ao escolher “Continuar preenchendo”, manter todos os dados digitados.

7 - TELA DE IMPORTÂNCIAS
	Objetivo: permitir que o usuário acompanhe compromissos, contas, vencimentos e datas importantes, identificando o que está pendente, próximo, atrasado ou concluído.

	7.1 - TERÁ OBRIGATORIAMENTE:

		7.1.1 - Botão “Nova importância”, direcionando para a tela 8. Caso o botão flutuante “+” seja mantido, ele deverá executar a mesma ação.

		7.1.2 - Filtros: Todos, Vencendo hoje, Este mês, Próximos, Concluídos e Atrasados. O filtro Atrasados complementa o protótipo para que compromissos vencidos continuem 				visíveis.

		7.1.3 - Seletor de mês e ano para consulta mensal, permitindo avançar e voltar, além de um campo de busca pelo nome da importância.

		7.1.4 - Lista de importâncias. Cada item deverá mostrar:

			- Nome da importância.
			- Descrição ou referência, quando informada, como “Vivo Fibra”.
			- Categoria, como Contas, Compras, Veículo, Lazer ou Saúde.
			- Data do compromisso ou vencimento e horário, quando informado.
			- Valor previsto, enquanto pendente, ou valor pago, quando houver pagamento registrado.
			- Indicação “Sem despesa”, quando não houver valor financeiro associado.
			- Situação: Pendente ou Concluída; usar também a identificação “Pago” quando houver despesa vinculada.
			- Prazo: “Hoje”, “Amanhã”, “Em X dias” ou “Atrasada há X dias”, para itens pendentes.
			- Indicação de repetição, quando houver.
			- Acesso aos detalhes e às ações do item.

		7.1.5 - No filtro Todos, organizar a lista em Atrasadas, Hoje, Próximas e Concluídas, exibindo a quantidade correspondente a cada grupo. As próximas poderão ser 				subdivididas por mês, como no protótipo.

		7.1.6 - Ao abrir um item, mostrar todos os dados cadastrados e as ações disponíveis: Editar, Excluir e, conforme o caso, Marcar como concluída, Reabrir, Registrar 				pagamento ou Ver despesa.

		7.1.7 - Navegação inferior com Início, Atividades, Financeiro, Importâncias e Perfil, destacando Importâncias. Manter essa ordem também nos cadastros das telas 6 e 8, com 			a respectiva seção destacada.

	7.2 - FUNCIONAMENTO DOS FILTROS:

		7.2.1 - TODOS: mostrar registros pendentes e concluídos de qualquer data, inclusive os atrasados.

		7.2.2 - VENCENDO HOJE: mostrar somente pendentes com data igual à data atual.

		7.2.3 - ESTE MÊS: mostrar pendentes e concluídos com data do compromisso no mês atual. Ao escolher outro mês no seletor, mudar a identificação para “Mês selecionado”. O 			seletor será exibido somente nessa consulta mensal; os demais filtros não terão um recorte mensal oculto.

		7.2.4 - PRÓXIMOS: mostrar somente pendentes com data posterior à atual, incluindo os meses seguintes.

		7.2.5 - CONCLUÍDOS: mostrar somente concluídos, incluindo os pagos.

		7.2.6 - ATRASADOS: mostrar somente pendentes com data anterior à atual.

		7.2.7 - A busca pelo nome deverá funcionar junto ao filtro ativo, sem diferenciar letras maiúsculas de minúsculas. As quantidades dos grupos deverão corresponder ao 				resultado completo da consulta, mesmo quando a lista for carregada em partes.

	7.3 - REGRAS DE FUNCIONAMENTO:

		7.3.1 - Pendente e Concluída serão as situações do registro. “Atrasada” será uma indicação calculada para pendentes cuja data já passou. Uma importância concluída não 				ficará atrasada. O horário opcional não alterará essa regra, que considera a data inteira.

		7.3.2 - Calcular “Em X dias” e “Atrasada há X dias” pela diferença entre datas do calendário, no fuso do aplicativo. Atualizar a indicação quando a data mudar, inclusive 			se a tela permanecer aberta.

		7.3.3 - Dentro dos grupos de pendentes, ordenar pela data mais antiga primeiro e, na mesma data, pelo horário; itens sem horário ficarão depois dos que possuem horário. Em 			Concluídos, mostrar as conclusões mais recentes primeiro.

		7.3.4 - Para importâncias sem despesa, “Marcar como concluída” deverá registrar a conclusão e atualizar a lista e a tela Inicial. “Reabrir” deverá devolver o item para 			Pendente, recalculando seu prazo e reativando somente lembretes ainda futuros. Essas ações não produzirão movimentações financeiras.

		7.3.5 - Para importâncias com despesa, “Registrar pagamento” deverá permitir vincular uma despesa existente ou abrir a tela 11 com nome, categoria e valor previsto 				preenchidos. O usuário deverá confirmar o valor efetivamente pago, maior que zero, e a data do pagamento, que não poderá ser futura. A data do pagamento poderá ser 			diferente do vencimento.

		7.3.6 - Somente após o pagamento ser salvo ou vinculado com sucesso, marcar a ocorrência como Concluída/Pago e atualizar o Financeiro. Ao vincular uma despesa existente, 			não criar outro lançamento nem somar seu valor novamente. Manter o valor previsto e o valor pago disponíveis nos detalhes. Cada ocorrência poderá ter apenas uma 			despesa vinculada, e a mesma despesa não poderá quitar duas ocorrências. Novas tentativas não deverão gerar lançamentos duplicados.

		7.3.7 - Uma importância paga deverá oferecer “Ver despesa”. Alterações no valor ou na data do pagamento deverão ocorrer no lançamento financeiro vinculado e aparecer nos 			detalhes da importância. Se esse lançamento for excluído, a importância deverá voltar a Pendente, com o prazo recalculado e reativação somente dos lembretes ainda 			futuros. Não oferecer uma reabertura isolada que mantenha o pagamento vinculado.

		7.3.8 - Antes de excluir, solicitar confirmação: “Deseja excluir esta importância?”. A exclusão da importância não deverá apagar uma despesa já registrada; informar isso 			na confirmação quando houver vínculo. Em séries, oferecer o alcance definido em 6.4.8, preservando os demais registros.

		7.3.9 - O bloco “Próximas importâncias” da tela Inicial deverá usar esses mesmos registros, mostrando pendentes de hoje e futuras em ordem de data. Itens concluídos ou 			excluídos deverão sair do bloco; atrasados permanecerão acessíveis na tela de Importâncias.

	7.4 - CRITÉRIOS DE ACEITE:

		7.4.1 - Se não houver registros, apresentar “Você ainda não cadastrou nenhuma importância” e o botão de cadastro. Se houver registros, mas nenhum corresponder à consulta, 			apresentar “Nenhuma importância encontrada para os filtros selecionados”.

		7.4.2 - Uma importância pendente de hoje deverá aparecer em Vencendo hoje. No dia seguinte, se continuar pendente, deverá aparecer em Atrasados. Uma importância concluída 			não deverá aparecer em nenhum desses dois filtros.

		7.4.3 - Uma importância do próximo mês deverá aparecer em Próximos, sem depender do mês consultado anteriormente no filtro mensal.

		7.4.4 - Ao concluir ou reabrir uma importância sem despesa, atualizar sua situação e as quantidades dos grupos sem alterar receitas, despesas ou saldo.

		7.4.5 - Ao cancelar a confirmação de exclusão, manter o registro. Ao confirmar, removê-lo das listas; preservar qualquer despesa já registrada.

		7.4.6 - Ao registrar um pagamento, atualizar o Financeiro e a importância de forma consistente. Se o usuário cancelar ou ocorrer falha antes da conclusão da operação, não 			apresentar o compromisso como pago. Uma repetição do mesmo envio não poderá produzir outra despesa.

		7.4.7 - Durante a consulta, mostrar carregamento. Se houver falha, exibir “Não foi possível carregar suas importâncias. Tente novamente”, com uma opção para tentar 				novamente, sem apresentar o erro como se a lista estivesse vazia.

8 - TELA DE CADASTRAR IMPORTÂNCIAS
	Objetivo: permitir o cadastro de um compromisso, vencimento ou data importante, com possibilidade de informar despesa prevista, repetição e lembrete.

	8.1 - CAMPOS OBRIGATÓRIOS:

		8.1.1 - NOME DA IMPORTÂNCIA: entre 3 e 100 caracteres. Exemplos: “Pagamento da internet”, “Licenciamento do veículo” ou “Aniversário da mãe”.

		8.1.2 - CATEGORIA: seleção única entre Contas, Compras, Veículo, Lazer, Saúde, Educação, Pessoal e Outros. Quando houver uma despesa, sua categoria financeira poderá ser 			confirmada na tela 11, sem presumir que as duas listas de categorias sejam idênticas.

		8.1.3 - DATA DO COMPROMISSO OU VENCIMENTO: data válida no formato DD/MM/AAAA, com opção de digitação ou seleção pelo calendário.

		8.1.4 - POSSUI DESPESA?: Sim ou Não. O valor inicial será Não. Essa informação permitirá cadastrar também datas importantes sem cobrança ou gasto.

	8.2 - CAMPOS OBRIGATÓRIOS CONFORME A SELEÇÃO:

		8.2.1 - VALOR PREVISTO: obrigatório quando “Possui despesa?” for Sim. Deverá ser maior que zero, em reais, com até duas casas decimais. Exemplo: R$ 99,90. Não aceitar 				texto, valor negativo ou arredondamento silencioso de valores com mais de duas casas.

		8.2.2 - Ao escolher Não, ocultar o valor e salvar a importância sem despesa associada. Se já houver um valor digitado no formulário, informar que ele será removido antes 			de confirmar a mudança.

	8.3 - CAMPOS OPCIONAIS:

		8.3.1 - DESCRIÇÃO / REFERÊNCIA: até 200 caracteres, com contador. Poderá conter a empresa, a pessoa ou uma observação, como “Vivo Fibra” ou “Levar os documentos do 				veículo”.

		8.3.2 - HORÁRIO DO COMPROMISSO: no formato HH:MM. Se não informado, considerar a importância referente ao dia, sem exibir um horário fictício.

		8.3.3 - REPETIR: Não repetir, Diariamente, Semanalmente, Mensalmente ou Anualmente. O valor inicial será Não repetir. Quando houver repetição, oferecer Sem data final ou 			Até uma data; nesta última opção, exigir a data final.

		8.3.4 - LEMBRAR-ME: desativado inicialmente. Ao ativar, permitir escolher No dia, 1 dia antes, 3 dias antes ou 7 dias antes, além do horário do lembrete. O horário será 			obrigatório nessa condição, inicialmente 09:00, e poderá ser alterado. Ele será independente do horário opcional do compromisso.

	8.4 - TERÁ OBRIGATORIAMENTE:

		8.4.1 - Botão “Salvar importância”. Durante o envio, mostrar “Salvando...” e impedir novos envios simultâneos.

		8.4.2 - Botão de voltar e opção “Cancelar”, com confirmação quando houver alterações não salvas: “Deseja sair sem salvar a importância?”. Oferecer “Continuar preenchendo” 			e “Descartar alterações”, inclusive ao usar a navegação inferior.

		8.4.3 - Mensagens de validação próximas aos campos e identificação das informações obrigatórias, inclusive as que dependerem de outra seleção.

	8.5 - REGRAS DE FUNCIONAMENTO:

		8.5.1 - Desconsiderar espaços no início e no final do nome. Validar nome, categoria, data e os campos condicionais antes de salvar.

		8.5.2 - Toda nova importância começará como Pendente. Será permitido cadastrar uma data passada; nesse caso, ela aparecerá imediatamente como atrasada. Informar esse 				resultado ao selecionar a data, sem impedir o cadastro.

		8.5.3 - Cadastrar uma importância com valor previsto não deverá alterar receitas, despesas ou saldo. A integração financeira ocorrerá somente no registro ou vínculo de um 			pagamento, conforme 7.3.5 e 7.3.6.

		8.5.4 - Aplicar às repetições as regras de 6.4.7 e 6.4.8, mantendo situação, pagamento e lembrete próprios de cada ocorrência. Na repetição anual em 29 de fevereiro, usar 			28 de fevereiro nos anos não bissextos e retornar ao dia 29 nos anos bissextos. Concluir ou pagar uma ocorrência não antecipará nem quitará as seguintes.

		8.5.5 - O lembrete deverá ter uma data e um horário futuros no momento do cadastro. Caso o momento calculado já tenha passado, orientar a ajustar ou desativar o lembrete. 			Isso permitirá salvar um compromisso atrasado sem tentar enviar uma notificação retroativa.

		8.5.6 - Um lembrete deverá gerar uma notificação no aplicativo. Se houver suporte a notificações do dispositivo, solicitar a permissão ao ativar o recurso. A recusa não 			impedirá o cadastro: informar que o lembrete ficará disponível apenas no aplicativo. Alterar data ou repetição deverá reagendar os lembretes afetados; concluir ou 			excluir uma ocorrência deverá cancelar seus lembretes ainda não enviados.

		8.5.7 - Após salvar, exibir “Importância cadastrada com sucesso” e abrir a tela de Importâncias no filtro Todos, sem busca ativa e com o item cadastrado em destaque. 				Atualizar também os dados correspondentes da tela Inicial.

		8.5.8 - A opção Editar deverá reutilizar o formulário preenchido, com o botão “Salvar alterações”. Preservar a identidade do registro. Em uma ocorrência paga, apresentar o 			pagamento vinculado e encaminhar suas alterações financeiras para “Ver despesa”; não permitir retirar o vínculo alterando “Possui despesa?”.

	8.6 - CRITÉRIOS DE ACEITE:

		8.6.1 - Se faltar nome, categoria ou data válida, impedir o cadastro e apresentar a mensagem correspondente: “Informe o nome da importância”, “Selecione uma categoria” ou 			“Informe uma data válida”.

		8.6.2 - Se “Possui despesa?” for Sim e o valor estiver vazio, zerado ou negativo, apresentar “Informe um valor previsto maior que zero”. Se for Não, permitir salvar sem 			valor financeiro.

		8.6.3 - Ao cadastrar uma conta de R$ 99,90, mostrá-la como pendente com esse valor previsto, sem alterar o saldo. Ao registrar posteriormente um pagamento de R$ 105,00, 			preservar a previsão nos detalhes e contabilizar somente os R$ 105,00 efetivamente registrados no Financeiro.

		8.6.4 - Uma repetição mensal iniciada em 31 de janeiro deverá ocorrer no último dia de fevereiro e novamente em 31 de março, respeitando a data final, quando definida.

		8.6.5 - Se a importância estiver marcada para 15/10 e o lembrete for de 3 dias antes às 09:00, programá-lo para 12/10 às 09:00 no fuso do aplicativo, desde que esse 				momento ainda seja futuro.

		8.6.6 - Se ocorrer falha ao salvar, manter os dados preenchidos e apresentar “Não foi possível salvar a importância. Tente novamente”. Novas tentativas do mesmo envio não 			deverão duplicar o registro, suas ocorrências ou seus lembretes.

		8.6.7 - Ao confirmar o descarte, sair sem salvar. Ao escolher “Continuar preenchendo”, manter o formulário. Ao editar e salvar, atualizar a importância existente, 				respeitando o alcance escolhido para repetições, sem criar um segundo cadastro independente.

9 - TELA DE FINANCEIRO

	Objetivo: permitir que o usuário acompanhe receitas, despesas e resultado mensal, consulte suas movimentações e acesse os cadastros e as alterações dos lançamentos.

	9.1 - TERÁ OBRIGATORIAMENTE:

		9.1.1 - SELETOR DE MÊS E ANO: iniciar no mês atual e permitir consultar outros meses. A seleção deverá valer para os indicadores, o gráfico, as categorias e as 				movimentações da tela. Mostrar o período ativo próximo aos indicadores.

		9.1.2 - INDICADORES DO MÊS:

			- Receitas: soma dos recebimentos do mês selecionado.
			- Despesas: soma dos pagamentos do mês selecionado.
			- Saldo do mês: receitas menos despesas.
			- Comparação das receitas e das despesas com o período anterior, quando houver base de comparação.

			O saldo poderá ser positivo, negativo ou zero. Ao abrir “Ver detalhes”, apresentar o período, os totais e a conta utilizada para obter o saldo.

		9.1.3 - GRÁFICO “RESUMO DO MÊS”: mostrar receitas e despesas agrupadas por dia, com legenda e valores em reais. Usar somente os dias existentes no mês. Dias sem 				movimentação terão valor zero. Ao selecionar um dia, apresentar sua data e os valores exatos de receitas e despesas; disponibilizar também uma consulta textual 			desses valores.

		9.1.4 - CATEGORIAS DE DESPESAS: mostrar nome, ícone e total gasto em cada categoria no mês. Apresentar inicialmente até cinco categorias com os maiores valores, com “Ver 			todas” para consultar as demais. “Outros” será uma categoria própria, não a soma das categorias que ficaram fora da prévia. Categorias sem despesas poderão ficar 			fora desse resumo.

		9.1.5 - ÚLTIMAS MOVIMENTAÇÕES: mostrar inicialmente até cinco lançamentos do mês, ordenados pela data do recebimento ou pagamento, da mais recente para a mais antiga. Em 			caso de empate, mostrar primeiro o cadastrado mais recentemente. Cada item deverá apresentar:

				- Nome do lançamento.
				- Tipo: Receita ou Despesa.
				- Categoria.
				- Data do recebimento ou pagamento.
				- Valor: “+ R$ ...” para receita e “− R$ ...” para despesa.
				- Indicação de vínculo com uma importância, quando existir.
				- Acesso aos detalhes, à edição e à exclusão.

		9.1.6 - CONSULTA DE MOVIMENTAÇÕES: a opção “Ver todas” deverá mostrar todos os registros do mês, com carregamento em partes quando necessário. Oferecer busca pelo nome, 			filtro por tipo — Todas, Receitas ou Despesas —, filtro por categoria e opção “Limpar filtros”. Identificar quando a consulta estiver filtrada.

		9.1.7 - AÇÕES DE CADASTRO: oferecer “Cadastrar receita”, direcionando para a tela 10, e “Cadastrar despesa”, direcionando para a tela 11. O botão flutuante “+” deverá 				abrir essas duas opções com identificação textual.

		9.1.8 - NAVEGAÇÃO INFERIOR: Início, Atividades, Financeiro, Importâncias e Perfil, destacando Financeiro e mantendo a ordem proposta nas telas anteriores. Nos cadastros 			financeiros, manter Financeiro destacado.

	9.2 - REGRAS DOS CÁLCULOS E FILTROS:

		9.2.1 - Somar os valores dos registros válidos do usuário no período. Lançamentos excluídos e valores apenas previstos em Importâncias não participarão dos totais. Uma 			despesa vinculada a uma importância será contabilizada uma única vez.

		9.2.2 - Calcular: SALDO DO MÊS = TOTAL DE RECEITAS DO MÊS − TOTAL DE DESPESAS DO MÊS. Os campos “Saldo do mês” e “Despesas do mês” da tela Inicial deverão usar esses 				mesmos cálculos para o mês atual; o resumo do dia deverá considerar somente a data atual.

		9.2.3 - Os valores informados em receitas e despesas serão positivos. O tipo determinará o sinal exibido e o efeito no saldo. Os cálculos deverão preservar os centavos com 			exatidão, sem diferenças causadas por arredondamentos intermediários.

		9.2.4 - O gráfico e as categorias deverão corresponder aos indicadores: a soma das receitas diárias deverá ser igual ao total de receitas; a soma das despesas diárias e a 			soma de todas as categorias de despesas deverão ser iguais ao total de despesas do mês.

		9.2.5 - Busca, tipo e categoria filtrarão somente a consulta de movimentações. Os indicadores, o gráfico e o resumo por categoria continuarão identificados como totais do 			mês completo. Ao selecionar um indicador de receitas ou despesas, aplicar o tipo correspondente à lista; ao selecionar uma categoria do resumo, consultar as 				despesas daquela categoria. Limpar filtros incompatíveis ao mudar o tipo.

		9.2.6 - Para um mês encerrado, comparar o mês inteiro com o mês anterior inteiro. Para o mês atual, comparar do dia 1 até hoje com o mesmo intervalo do mês anterior, 				limitado ao último dia daquele mês. Informar os intervalos na comparação. Ao consultar um mês futuro, não apresentar variação percentual.

		9.2.7 - Quando o total anterior for maior que zero, calcular a variação por: ((total atual − total anterior) ÷ total anterior) × 100. Exibir até uma casa decimal. Se o 			total anterior for zero e o atual for positivo, mostrar “Sem base de comparação”; se ambos forem zero, mostrar “Sem movimentação nos dois períodos”.

		9.2.8 - Identificar a comparação como aumento, redução ou estabilidade. Para despesas, aumento deverá aparecer como aumento de gastos, sem receber a mesma interpretação 			visual de um aumento de receitas. Os percentuais deverão ser calculados a partir dos registros, sem reproduzir os números ilustrativos do protótipo.

	9.3 - AÇÕES E ESTADOS DA TELA:

		9.3.1 - Ao abrir uma movimentação, apresentar nome, tipo, valor, categoria, data e os campos opcionais preenchidos. Para uma despesa vinculada, mostrar também a 				importância e permitir acessá-la enquanto ela existir.

		9.3.2 - Editar uma receita deverá abrir a tela 10 preenchida; editar uma despesa deverá abrir a tela 11 preenchida. Ao salvar, atualizar o lançamento existente e 				recalcular os meses afetados, inclusive quando a data mudar de mês. O tipo do lançamento permanecerá identificado durante a edição.

		9.3.3 - Antes de excluir, apresentar confirmação com nome, data e valor: “Deseja excluir esta receita?” ou “Deseja excluir esta despesa?”. Oferecer “Cancelar” e “Excluir”. 			Informar que a exclusão atualizará os totais. Na exclusão de uma despesa vinculada, avisar também que a importância voltará a ficar pendente.

		9.3.4 - Ao confirmar a exclusão, remover o lançamento dos cálculos e das consultas financeiras e atualizar os resumos da tela Inicial. Se houver uma importância vinculada, 			reabri-la na mesma operação, recalcular seu atraso e reativar apenas lembretes ainda futuros. Uma falha não deverá deixar apenas uma parte dessas alterações 				aplicada.

		9.3.5 - Se o mês não tiver movimentações, mostrar totais zerados e “Nenhuma movimentação cadastrada neste mês”, com acesso aos cadastros. Se apenas a busca estiver vazia, 			mostrar “Nenhuma movimentação encontrada para os filtros selecionados”.

		9.3.6 - Durante a consulta, mostrar carregamento. Se houver falha, apresentar “Não foi possível carregar seus dados financeiros. Tente novamente”, com nova tentativa. Não 			substituir dados indisponíveis por zeros nem apresentar valores de um mês anterior como se fossem do mês selecionado.

	9.4 - CRITÉRIOS DE ACEITE:

		9.4.1 - Com receitas de R$ 2.450,75 e despesas de R$ 1.230,40 no mês selecionado, apresentar saldo de R$ 1.220,35. Se as despesas ultrapassarem as receitas, apresentar o 			saldo negativo corretamente.

		9.4.2 - Um recebimento de setembro cadastrado em outubro deverá compor setembro. Alterar sua data para outubro deverá retirá-lo dos totais de setembro e incluí-lo nos de 			outubro, sem criar outro lançamento.

		9.4.3 - Duas receitas de R$ 0,10 e R$ 0,20 deverão somar R$ 0,30. Com uma despesa de R$ 0,10 no mesmo período, o saldo deverá ser R$ 0,20.

		9.4.4 - Ao filtrar a lista por uma categoria ou por Despesas, mostrar somente os registros correspondentes, mantendo os indicadores e o gráfico identificados como resumo 			do mês. Limpar os filtros deverá restaurar a consulta mensal completa.

		9.4.5 - Para uma base anterior de R$ 1.000,00 e um total atual de R$ 1.100,00, nos intervalos comparáveis, mostrar aumento de 10%. Se a base anterior for zero, aplicar a 			mensagem prevista em 9.2.7, sem divisão por zero.

		9.4.6 - O gráfico deverá respeitar meses com 28, 29, 30 ou 31 dias. Os valores diários e os totais das categorias deverão conferir com os indicadores, independentemente da 			quantidade de itens carregados na lista.

		9.4.7 - Ao cancelar uma exclusão, manter os dados e totais. Ao confirmar, atualizar as telas afetadas. Ao excluir uma despesa vinculada, a importância deverá voltar a 				Pendente, sem ser excluída.
10 - TELA DE CADASTRAR RECEITA
	Objetivo: registrar um valor efetivamente recebido pelo usuário para compor suas receitas e seu saldo no período correto.

	10.1 - CAMPOS OBRIGATÓRIOS:

		10.1.1 - NOME DA RECEITA: entre 3 e 100 caracteres. Exemplos: “Salário”, “Venda de notebook” ou “Serviço de desenvolvimento”.

		10.1.2 - VALOR RECEBIDO: maior que zero, em reais, com até duas casas decimais. Exemplo: R$ 2.450,75. Aceitar a digitação de valores inteiros, apresentando-os com 				centavos, como R$ 100,00.

		10.1.3 - CATEGORIA: seleção única entre Salário, Trabalho autônomo, Vendas, Rendimentos, Reembolsos e Outros. Essas categorias representam a origem do recebimento e serão 			diferentes das categorias de despesas.

		10.1.4 - DATA DO RECEBIMENTO: data válida em DD/MM/AAAA, inicialmente preenchida com hoje. Permitir datas passadas e impedir datas futuras, pois o cadastro representa um 			recebimento já realizado.

	10.2 - CAMPOS OPCIONAIS:

		10.2.1 - DESCRIÇÃO / OBSERVAÇÃO: até 200 caracteres, com contador. Exemplo: “Pagamento referente ao serviço entregue em setembro”.

		10.2.2 - ORIGEM / PAGADOR: até 100 caracteres. Exemplo: nome da empresa ou da pessoa que realizou o pagamento.

		10.2.3 - FORMA DE RECEBIMENTO: Pix, Dinheiro, Transferência, Depósito ou Outros. Inicialmente, deixar sem seleção. Esse campo será informativo e não executará uma operação 			bancária.

	10.3 - TERÁ OBRIGATORIAMENTE:

		10.3.1 - Botão “Salvar receita”, com identificação “Salvando...” durante o envio e bloqueio de envios simultâneos. Na edição, usar “Salvar alterações”.

		10.3.2 - Botão de voltar e opção “Cancelar”. Se houver alterações não salvas, perguntar “Deseja sair sem salvar a receita?”, com “Continuar preenchendo” e “Descartar 				alterações”. Aplicar a mesma regra à navegação inferior.

		10.3.3 - Identificação dos campos obrigatórios, formatação monetária e mensagens de validação próximas aos campos. Permitir acionar Salvar para validar o formulário, mas 			impedir a gravação enquanto houver erros.

	10.4 - REGRAS DE FUNCIONAMENTO:

		10.4.1 - Desconsiderar espaços no início e no final do nome. Não aceitar nomes formados apenas por espaços, valores zerados ou negativos, datas inexistentes ou categoria 			incompatível com receita.

		10.4.2 - Aceitar somente valores monetários válidos. Se houver mais de duas casas decimais, solicitar a correção, sem arredondar silenciosamente. O usuário informará o 			valor efetivamente recebido.

		10.4.3 - Cada receita salva representará um recebimento confirmado, contabilizado na data informada. Não será necessário marcá-la posteriormente como concluída. Uma 				receita de salário, por exemplo, não gerará automaticamente recebimentos nos meses seguintes.

		10.4.4 - Após salvar, apresentar “Receita cadastrada com sucesso” e abrir o Financeiro no mês da data informada, com a nova receita visível e sem filtros que a ocultem. 			Atualizar os resumos correspondentes da tela Inicial e as comparações dos períodos afetados.

		10.4.5 - Na edição, manter o tipo Receita e atualizar o mesmo registro. Alterações no nome, no valor, na categoria ou na data deverão aparecer nas consultas 					correspondentes, sem duplicar o recebimento.

		10.4.6 - Cliques repetidos e novas tentativas do mesmo envio deverão produzir um único registro. Recebimentos distintos poderão ter nome, data e valor iguais; a proteção 			contra repetição de envio não deverá impedir esses cadastros legítimos.

	10.5 - CRITÉRIOS DE ACEITE:

		10.5.1 - Se faltar informação obrigatória, apresentar a mensagem específica: “Informe o nome da receita”, “Informe um valor recebido maior que zero”, “Selecione uma 				categoria” ou “Informe uma data válida”. Manter os demais campos preenchidos.

		10.5.2 - Se a data for futura, não salvar e apresentar “A data do recebimento não pode ser futura”. Se o valor tiver mais de duas casas decimais, apresentar “Informe um 			valor com até duas casas decimais”.

		10.5.3 - Ao cadastrar uma receita de R$ 100,00 em um mês sem movimentações, mostrar receitas de R$ 100,00, despesas de R$ 0,00 e saldo de R$ 100,00. A lista deverá 				identificá-la como Receita, com sinal positivo.

		10.5.4 - Ao alterar essa receita de R$ 100,00 para R$ 120,00, o total deverá passar para R$ 120,00, sem manter uma segunda receita de R$ 100,00.

		10.5.5 - Se ocorrer falha ou perda de conexão, manter o formulário e apresentar “Não foi possível confirmar o cadastro da receita. Tente novamente”. Ao tentar novamente, 			verificar o resultado do mesmo envio para não duplicar uma receita que já tenha sido salva.

		10.5.6 - Ao confirmar o descarte, sair sem criar ou alterar a receita. Ao escolher “Continuar preenchendo”, preservar os dados. Após salvar e abrir novamente o lançamento, 			apresentar os mesmos valores e informações confirmados.

11 - TELA DE CADASTRAR DESPESAS
	Objetivo: registrar um pagamento realizado pelo usuário, permitindo associá-lo a uma importância e manter os valores financeiros e a situação do compromisso consistentes.

	11.1 - CAMPOS OBRIGATÓRIOS:

		11.1.1 - NOME DA DESPESA: entre 3 e 100 caracteres. Exemplos: “Compra no mercado”, “Pagamento da internet” ou “Aluguel”.

		11.1.2 - VALOR PAGO: maior que zero, em reais, com até duas casas decimais. O valor será informado como positivo; o aplicativo o apresentará como saída nas movimentações e 			o descontará do saldo do mês.
	
		11.1.3 - CATEGORIA: seleção única entre Alimentação, Transporte, Moradia, Contas, Compras, Saúde, Educação, Lazer, Veículo e Outros. As categorias deverão ser as mesmas 			utilizadas no resumo de despesas da tela 9.

		11.1.4 - DATA DO PAGAMENTO: data válida em DD/MM/AAAA, inicialmente preenchida com hoje. Permitir datas passadas e impedir datas futuras. A data de vencimento de uma 				importância não substituirá automaticamente a data do pagamento.

	11.2 - CAMPOS OPCIONAIS:

		11.2.1 - DESCRIÇÃO / OBSERVAÇÃO: até 200 caracteres, com contador. Exemplo: “Pagamento com juros por atraso”.

		11.2.2 - DESTINATÁRIO / ESTABELECIMENTO: até 100 caracteres. Exemplo: “Vivo Fibra” ou “Mercado Central”.

		11.2.3 - FORMA DE PAGAMENTO: Pix, Dinheiro, Cartão de débito, Transferência, Boleto ou Outros. Inicialmente, deixar sem seleção. O preenchimento apenas descreverá como o 			pagamento foi realizado; não efetuará cobranças ou transferências.

		11.2.4 - IMPORTÂNCIA VINCULADA: permitir selecionar uma ocorrência pendente, do próprio usuário, cadastrada com despesa e ainda sem pagamento vinculado. Mostrar nome, 				vencimento e valor previsto para identificação. Quando a tela for aberta por “Registrar pagamento”, apresentar a importância de origem já selecionada.

	11.3 - TERÁ OBRIGATORIAMENTE:

		11.3.1 - Botão “Salvar despesa”. Quando houver importância vinculada, usar “Salvar despesa e registrar pagamento”, deixando claro o resultado da ação. Na edição, usar 				“Salvar alterações”. Durante o envio, apresentar “Salvando...” e impedir novos envios simultâneos.

		11.3.2 - Botão de voltar e opção “Cancelar”. Se houver alterações não salvas, perguntar “Deseja sair sem salvar a despesa?”, com “Continuar preenchendo” e “Descartar 				alterações”, inclusive ao usar a navegação inferior. Exibir validações próximas aos campos, mantendo o restante do formulário preenchido.

	11.4 - REGRAS DE FUNCIONAMENTO:

		11.4.1 - Validar nome, valor, categoria e data. Desconsiderar espaços nas extremidades do nome; rejeitar texto no valor, zero, valores negativos e mais de duas casas 				decimais, sem arredondamento silencioso.

		11.4.2 - Uma despesa sem importância vinculada poderá ser cadastrada normalmente. Ela comporá os totais e a categoria do mês do pagamento e não criará automaticamente uma 			importância.

		11.4.3 - Permitir uma despesa mesmo que o saldo do mês fique negativo. O saldo exibido representa os registros do aplicativo, e não uma autorização de pagamento ou uma 			verificação de disponibilidade bancária.

		11.4.4 - Se a data informada for futura, orientar o usuário a cadastrar o compromisso em Importâncias. A despesa financeira será registrada quando o pagamento tiver 				ocorrido. A repetição de compromissos permanecerá no cadastro de Importâncias, sem gerar pagamentos automáticos.

		11.4.5 - Após salvar uma despesa iniciada pelo Financeiro ou pela tela Inicial, exibir “Despesa cadastrada com sucesso” e abrir o Financeiro no mês do pagamento, com o 			item visível. Se o fluxo tiver começado em Importâncias, retornar aos detalhes da importância com “Pagamento registrado com sucesso”. Atualizar todas as telas 				afetadas. Na edição, preservar a identidade e o tipo Despesa.

		11.4.6 - A proteção contra cliques repetidos e novas tentativas do mesmo envio deverá valer também para despesas sem vínculo. Pagamentos distintos poderão ter nome, data e 			valor iguais, sem serem automaticamente rejeitados como duplicação.

	11.5 - INTEGRAÇÃO COM IMPORTÂNCIAS:

		11.5.1 - Ao abrir o formulário por “Registrar pagamento”, preencher o nome e o valor previsto da importância. Preencher a categoria quando ela existir entre as categorias 			de despesas; caso contrário, solicitar uma categoria financeira. O usuário deverá confirmar o valor efetivamente pago e a data do pagamento. Manter visíveis o 				vencimento e o valor previsto como referência.

		11.5.2 - Salvar a despesa, vinculá-la à ocorrência e marcar essa ocorrência como Concluída/Pago em uma única operação consistente. Uma falha não deverá criar uma despesa 			sem o vínculo solicitado nem apresentar a importância como paga sem uma despesa salva.

		11.5.3 - O valor pago poderá ser diferente do previsto. Preservar ambos nos detalhes da importância e usar somente o valor pago nos cálculos financeiros. Para esta versão, 			cada ocorrência será quitada por uma única despesa; pagamentos parciais exigirão regras adicionais antes de serem incluídos.

		11.5.4 - Cada ocorrência poderá ter somente uma despesa vinculada, e a mesma despesa poderá quitar somente uma ocorrência. Validar o vínculo também ao confirmar o envio, 			inclusive se outro acesso tiver registrado o pagamento enquanto o formulário estava aberto. Nesse conflito, informar “Esta importância já possui um pagamento 				registrado” e permitir consultar o pagamento, sem salvar outra despesa. Evitar lançamentos duplicados em cliques repetidos ou novas tentativas.

		11.5.5 - Oferecer a alternativa “Vincular despesa existente” no fluxo de registro de pagamento. Permitir buscar despesas do usuário ainda sem vínculo, mostrando nome, data 			e valor para confirmação. Após a escolha, atualizar apenas o vínculo e a situação da importância: o lançamento continuará sendo contabilizado uma única vez, sem 			alterar seu valor, sua categoria ou sua data.

		11.5.6 - Na edição de uma despesa vinculada, alterações no valor e na data deverão refletir nos dados do pagamento exibidos em Importâncias. Trocar ou remover o vínculo 			exigirá confirmação: a importância anterior voltará a Pendente, com prazo recalculado e reativação apenas de lembretes futuros; a nova, quando houver, ficará 				Concluída/Pago. Preservar o lançamento financeiro, sem registrar outra despesa. A troca completa deverá ocorrer de forma consistente.

		11.5.7 - Excluir a despesa deverá reabrir a importância, conforme 9.3.4. Excluir apenas a importância deverá preservar a despesa e seus efeitos no Financeiro, deixando-a 			sem vínculo ativo. Concluir uma ocorrência de uma série não deverá quitar nem modificar os pagamentos das próximas.

	11.6 - CRITÉRIOS DE ACEITE:

		11.6.1 - Se faltar nome, valor, categoria ou data válida, impedir o envio e apresentar a mensagem correspondente. Para uma data futura, exibir “A data do pagamento não 			pode ser futura. Cadastre o compromisso em Importâncias”.

		11.6.2 - Em um mês com receitas de R$ 100,00 e nenhuma despesa, cadastrar uma despesa de R$ 30,00 deverá resultar em despesas de R$ 30,00 e saldo de R$ 70,00. Uma despesa 			de R$ 130,00, nesse mesmo cenário inicial, deverá ser aceita e resultar em saldo de −R$ 30,00.

		11.6.3 - Para uma importância com previsão de R$ 99,90 e pagamento de R$ 105,00, contabilizar somente R$ 105,00 como despesa. Mostrar a importância como Concluída/Pago e 			manter a previsão de R$ 99,90 nos detalhes.

		11.6.4 - Vincular uma despesa existente de R$ 105,00 deverá concluir a importância sem alterar o total de despesas do mês. Uma nova tentativa da mesma operação deverá 				preservar esse resultado, sem criar outro lançamento.

		11.6.5 - Se o valor pago de uma despesa vinculada mudar de R$ 105,00 para R$ 100,00, reduzir as despesas em R$ 5,00, atualizar o saldo e exibir R$ 100,00 como valor pago 			na importância. Ao mudar a data para outro mês, transferir a contabilização entre os meses correspondentes.

		11.6.6 - Cancelar o formulário ou uma confirmação de descarte não deverá registrar um pagamento. Se a operação falhar, manter os campos e apresentar “Não foi possível 				confirmar o cadastro da despesa. Tente novamente”, sem deixar uma conclusão parcial da importância e sem duplicar a despesa na nova tentativa.

		11.6.7 - Ao remover o vínculo, manter a despesa nos totais e reabrir a importância. Ao excluir a despesa, retirá-la dos totais e reabrir a importância. Se o vencimento já 			tiver passado, a importância reaberta deverá aparecer como atrasada; as demais ocorrências da série permanecerão inalteradas.




TABELAS DO BANCO DE DADOS — PROPOSTA PARA MODELAGEM COM SQLALCHEMY

Este modelo considera os cadastros, as repetições, os pagamentos, os lembretes e a recuperação de senha definidos para o aplicativo. A numeração abaixo corresponde às tabelas, independentemente da numeração das telas.

Os nomes de tabelas e colunas serão escritos em `snake_case`, sem espaços e sem acentos. “Obrigatório” significa `NOT NULL`; “opcional” significa que a coluna aceita `NULL`. Todos os campos `id` serão UUID (tipo `uuid` do PostgreSQL), chaves primárias, versão 7, gerados pela aplicação com `uuid.uuid7()` (ver docs/adr/0002_identificadores_uuid.md). As chaves estrangeiras que referenciam um `id` também serão UUID.

SGBD: PostgreSQL (decisão do usuário). Esta é uma especificação lógica com tipos e restrições mapeados no SQLAlchemy; o modelo físico (convenções, nomes e migração) está em docs/arquitetura/arquitetura_api_minhavida.md §10.


DECISÕES DA MODELAGEM:

- Armazenar `senha_hash`, usando um algoritmo próprio para senhas, como Argon2id. `confirmar_senha` pertencerá somente ao formulário e à validação da requisição; não será uma coluna.
- Receitas e despesas compartilharão `movimentacao_financeira`, diferenciadas pelo campo `tipo`.
- Cada linha de `atividade` ou `importancia` representará uma ocorrência concreta. Quando houver repetição, uma tabela de série guardará as regras e os valores padrão para gerar as ocorrências.
- Atividades e importâncias sem repetição terão `serie_id = NULL`, sem precisar criar uma série.
- Saldo, totais, duração, prazo, situação de atraso e situação de conclusão serão calculados a partir dos registros, conforme as regras ao final. Isso evita manter valores duplicados que possam divergir.

1 - USUARIO — `usuario`

- id (chave primária, UUID v7 gerado pela aplicação, obrigatório).
- nome_completo (VARCHAR(150), obrigatório).
- email (VARCHAR(254), obrigatório, único).
- senha_hash (VARCHAR(255), obrigatório).
- data_nascimento (DATE, obrigatório).
- fuso_horario (VARCHAR(64), obrigatório; exemplo: America/Sao_Paulo).
- criado_em (DATETIME em UTC, obrigatório; preenchido na criação).
- atualizado_em (DATETIME em UTC, obrigatório; atualizado nas alterações).

Regras: normalizar o e-mail de forma consistente no cadastro e no login, adotando a forma canônica da DEC-MV-09 (R9.9): remoção de espaços externos, conversão para minúsculas, validação sem SMTPUTF8 e domínio internacionalizado em IDNA (ASCII). Aplicar unicidade ao valor normalizado. Validar a estrutura do e-mail e impedir data de nascimento futura na aplicação. O fuso será inicialmente obtido do dispositivo e persistido na conta para permitir cálculos e lembretes quando o usuário não estiver com o aplicativo aberto.

Não criar as colunas `senha` em texto puro nem `confirmar_senha`. O hash já conterá as informações necessárias ao algoritmo de verificação, conforme o formato da biblioteca utilizada.

2 - RECUPERACAO_SENHA — `recuperacao_senha`

- id (chave primária, UUID v7 gerado pela aplicação, obrigatório).
- usuario_id (chave estrangeira → usuario.id, UUID, obrigatório, único).
- codigo_hash (VARCHAR(255), obrigatório; representação protegida do código enviado).
- expira_em (DATETIME em UTC, obrigatório).
- tentativas (INT, obrigatório, padrão 0).
- verificado_em (DATETIME em UTC, opcional).
- token_redefinicao_hash (VARCHAR(64), opcional, único quando preenchido).
- utilizado_em (DATETIME em UTC, opcional).
- criado_em (DATETIME em UTC, obrigatório).
- atualizado_em (DATETIME em UTC, obrigatório).

Finalidade: atender às etapas de enviar o código, verificar os oito dígitos e autorizar a nova senha.

Manter uma única recuperação corrente por usuário. No reenvio, substituir o código protegido e a validade, zerar as tentativas e remover a verificação, o token e o uso anteriores. Assim, o código antigo deixa de ser válido. O código informado é uma sequência de oito caracteres numéricos, podendo começar com zero; não deve ser convertido para inteiro nem armazenado em texto puro.

Após verificar o código, emitir um token aleatório de alta entropia, de uso único, para autorizar a etapa de redefinição. Guardar somente seu hash. O campo `token_redefinicao_hash` pode conter um digest hexadecimal de um token forte; isso não significa usar um hash rápido para armazenar senhas ou códigos curtos. Para o código, usar uma proteção adequada, como o hash lento já utilizado para senhas.

Parâmetros aprovados (DEC-MV-11): validade total de dez minutos, até cinco tentativas inválidas por emissão e intervalo mínimo de 60 segundos entre emissões. O token também deverá respeitar `expira_em`. Verificar o código uma vez não deverá permitir a emissão repetida de novos tokens. Atualizar a senha e marcar `utilizado_em` na mesma transação, validando novamente token, prazo e uso. Utilizar bloqueio ou atualização condicional para que duas solicitações simultâneas não consumam o mesmo token; proteger também a contagem de tentativas concorrentes.

3 - CATEGORIA_ATIVIDADE — `categoria_atividade`

- id (chave primária, UUID v7 gerado pela aplicação, obrigatório).
- nome (VARCHAR(50), obrigatório, único).
- ativa (BOOLEAN, obrigatório, padrão verdadeiro).

Dados iniciais: Trabalho, Estudo, Saúde, Pessoal, Lazer e Outros.

Uma categoria desativada continuará disponível no histórico dos registros existentes, mas não será oferecida em novos cadastros. Impedir exclusão física de categoria referenciada.

4 - SERIE_ATIVIDADE — `serie_atividade`

- id (chave primária, UUID v7 gerado pela aplicação, obrigatório).
- usuario_id (chave estrangeira → usuario.id, UUID, obrigatório).
- categoria_id (chave estrangeira → categoria_atividade.id, UUID, obrigatório).
- nome_padrao (VARCHAR(100), obrigatório).
- descricao_padrao (VARCHAR(200), opcional).
- prioridade_padrao (VARCHAR(5), obrigatório, padrão BAIXA; valores: BAIXA, MEDIA ou ALTA).
- periodicidade (VARCHAR(10), obrigatório; valores: NENHUMA, DIARIA, SEMANAL ou MENSAL).
- data_referencia (DATE, obrigatório; data de referência da regra vigente).
- numero_referencia (INT, obrigatório, padrão 1; posição da ocorrência correspondente à data de referência).
- horario_inicial_padrao (TIME, obrigatório).
- horario_final_padrao (TIME, obrigatório).
- data_final_repeticao (DATE, opcional; limite inclusivo informado pelo usuário).
- numero_final (INT, opcional; última posição que poderá ser gerada; zero encerra a geração antes da primeira ocorrência).
- criado_em (DATETIME em UTC, obrigatório).
- atualizado_em (DATETIME em UTC, obrigatório).

Esta tabela guardará o padrão para gerar tarefas recorrentes. A opção NENHUMA permitirá encerrar uma repetição preservando sua origem: nesse caso, a regra vigente produzirá somente a ocorrência de referência. Para uma atividade inicialmente avulsa, utilizar apenas a tabela `atividade`.

Restrições: nome padrão com 3 a 100 caracteres; horário final maior que inicial; `numero_referencia >= 1`; `numero_final >= 0`, quando informado; data final da repetição igual ou posterior à referência, quando informada. O limite por número será usado principalmente para interromper uma série a partir de uma ocorrência, sem depender de datas que possam ter sido editadas individualmente.

5 - ATIVIDADE — `atividade`

- id (chave primária, UUID v7 gerado pela aplicação, obrigatório).
- usuario_id (chave estrangeira → usuario.id, UUID, obrigatório).
- categoria_id (chave estrangeira → categoria_atividade.id, UUID, obrigatório).
- serie_id (chave estrangeira → serie_atividade.id, UUID, opcional).
- numero_ocorrencia (INT, opcional; posição estável dentro da série).
- nome (VARCHAR(100), obrigatório).
- descricao (VARCHAR(200), opcional).
- prioridade (VARCHAR(5), obrigatório, padrão BAIXA; valores: BAIXA, MEDIA ou ALTA).
- data_atividade (DATE, obrigatório).
- horario_inicial (TIME, obrigatório).
- horario_final (TIME, obrigatório).
- concluida_em (DATETIME em UTC, opcional).
- excluida_em (DATETIME em UTC, opcional).
- criado_em (DATETIME em UTC, obrigatório).
- atualizado_em (DATETIME em UTC, obrigatório).

Restrições: nome com 3 a 100 caracteres; horário final maior que inicial. `serie_id` e `numero_ocorrencia` deverão estar ambos preenchidos ou ambos nulos; quando houver número, ele deverá ser maior ou igual a 1. Criar unicidade para o par `(serie_id, numero_ocorrencia)`.

Os campos de nome, categoria, prioridade, descrição e horários serão os valores efetivos daquela ocorrência. Não consultar sempre o padrão da série para exibi-los, pois uma edição individual ou a conclusão de uma ocorrência precisa preservar seus próprios dados.

Situação calculada para registros não excluídos: `concluida_em` nulo significa Pendente; preenchido significa Concluída. Concluir preencherá o campo; reabrir o tornará nulo. A data da atividade continuará sendo sua data planejada.

6 - CATEGORIA_IMPORTANCIA — `categoria_importancia`

- id (chave primária, UUID v7 gerado pela aplicação, obrigatório).
- nome (VARCHAR(50), obrigatório, único).
- ativa (BOOLEAN, obrigatório, padrão verdadeiro).

Dados iniciais: Contas, Compras, Veículo, Lazer, Saúde, Educação, Pessoal e Outros.

Manter separada das categorias financeiras: a categoria de um compromisso não necessariamente será a categoria escolhida para o pagamento. Desativar uma categoria não deverá apagar seu histórico.

7 - SERIE_IMPORTANCIA — `serie_importancia`

- id (chave primária, UUID v7 gerado pela aplicação, obrigatório).
- usuario_id (chave estrangeira → usuario.id, UUID, obrigatório).
- categoria_id (chave estrangeira → categoria_importancia.id, UUID, obrigatório).
- nome_padrao (VARCHAR(100), obrigatório).
- descricao_padrao (VARCHAR(200), opcional).
- periodicidade (VARCHAR(10), obrigatório; valores: NENHUMA, DIARIA, SEMANAL, MENSAL ou ANUAL).
- data_referencia (DATE, obrigatório).
- numero_referencia (INT, obrigatório, padrão 1).
- horario_padrao (TIME, opcional).
- data_final_repeticao (DATE, opcional; limite inclusivo).
- numero_final (INT, opcional; última posição gerável, admitindo zero).
- possui_despesa_padrao (BOOLEAN, obrigatório, padrão falso).
- valor_previsto_padrao (DECIMAL(12,2), opcional; obrigatório e maior que zero quando houver despesa).
- lembrete_antecedencia_dias (SMALLINT, opcional; valores: 0, 1, 3 ou 7).
- lembrete_horario (TIME, opcional).
- criado_em (DATETIME em UTC, obrigatório).
- atualizado_em (DATETIME em UTC, obrigatório).

Esta tabela guardará a configuração para gerar compromissos recorrentes. Aplicar as mesmas regras dos números de ocorrência da série de atividades, acrescentando a repetição anual.

Restrições: nome padrão com 3 a 100 caracteres. Se `possui_despesa_padrao` for falso, `valor_previsto_padrao` deverá ser nulo. Se for verdadeiro, exigir valor preenchido e positivo. Os dois campos de lembrete deverão estar ambos nulos, para lembrete desativado, ou ambos preenchidos.

8 - IMPORTANCIA — `importancia`

- id (chave primária, UUID v7 gerado pela aplicação, obrigatório).
- usuario_id (chave estrangeira → usuario.id, UUID, obrigatório).
- categoria_id (chave estrangeira → categoria_importancia.id, UUID, obrigatório).
- serie_id (chave estrangeira → serie_importancia.id, UUID, opcional).
- numero_ocorrencia (INT, opcional).
- nome (VARCHAR(100), obrigatório).
- descricao (VARCHAR(200), opcional).
- data_compromisso (DATE, obrigatório).
- horario (TIME, opcional).
- possui_despesa (BOOLEAN, obrigatório, padrão falso).
- valor_previsto (DECIMAL(12,2), opcional; obrigatório e maior que zero quando houver despesa).
- concluida_manualmente_em (DATETIME em UTC, opcional; utilizado somente em importâncias sem despesa).
- excluida_em (DATETIME em UTC, opcional).
- criado_em (DATETIME em UTC, obrigatório).
- atualizado_em (DATETIME em UTC, obrigatório).

Criar unicidade para `(serie_id, numero_ocorrencia)`. Aplicar a mesma regra de preenchimento conjunto desses dois campos utilizada em Atividade. Cada linha terá seus próprios dados, mesmo quando tiver sido gerada a partir de uma série.

Restrições: nome com 3 a 100 caracteres. Restrições condicionais: se não houver despesa, o valor previsto será nulo; se houver, exigir valor preenchido e positivo. `concluida_manualmente_em` deverá ser nulo quando `possui_despesa` for verdadeiro.

O pagamento será encontrado pelo relacionamento com `movimentacao_financeira`. Não criar nesta tabela outra coluna de valor pago nem uma segunda chave estrangeira de volta para o lançamento; o vínculo ficará em um único lado.

Situação calculada para uma importância não excluída:

- Sem despesa: Concluída quando `concluida_manualmente_em` estiver preenchido; Pendente nos demais casos.
- Com despesa: Concluída/Pago quando houver uma despesa válida vinculada; Pendente quando não houver.
- Atrasada: importância pendente com `data_compromisso` anterior a hoje no fuso da conta. É uma indicação calculada, não um terceiro estado persistido.

9 - CATEGORIA_FINANCEIRA — `categoria_financeira`

- id (chave primária, UUID v7 gerado pela aplicação, obrigatório).
- nome (VARCHAR(50), obrigatório).
- tipo (VARCHAR(7), obrigatório; valores: RECEITA ou DESPESA).
- ativa (BOOLEAN, obrigatório, padrão verdadeiro).

Criar unicidade para `(tipo, nome)`. Assim, a categoria Outros poderá existir para receitas e para despesas sem representar o mesmo registro. Criar também a chave única `(id, tipo)` para a chave estrangeira composta da movimentação.

Categorias iniciais de receita: Salário, Trabalho autônomo, Vendas, Rendimentos, Reembolsos e Outros.

Categorias iniciais de despesa: Alimentação, Transporte, Moradia, Contas, Compras, Saúde, Educação, Lazer, Veículo e Outros.

10 - MOVIMENTACAO_FINANCEIRA — `movimentacao_financeira`

- id (chave primária, UUID v7 gerado pela aplicação, obrigatório).
- usuario_id (chave estrangeira → usuario.id, UUID, obrigatório).
- categoria_id (chave estrangeira composta com tipo → categoria_financeira.id/tipo, UUID, obrigatório).
- tipo (VARCHAR(7), obrigatório; valores: RECEITA ou DESPESA).
- nome (VARCHAR(100), obrigatório).
- descricao (VARCHAR(200), opcional).
- valor (DECIMAL(12,2), obrigatório, maior que zero).
- data_movimentacao (DATE, obrigatório; data real do recebimento ou pagamento).
- contraparte (VARCHAR(100), opcional; pagador, destinatário ou estabelecimento, conforme o tipo).
- forma_movimentacao (VARCHAR(20), opcional; valores controlados indicados abaixo).
- importancia_id (chave estrangeira → importancia.id, UUID, opcional, único quando preenchido).
- importancia_vinculada_em (DATETIME em UTC, opcional).
- excluida_em (DATETIME em UTC, opcional).
- criado_em (DATETIME em UTC, obrigatório).
- atualizado_em (DATETIME em UTC, obrigatório).

Receitas: formas PIX, DINHEIRO, TRANSFERENCIA, DEPOSITO ou OUTROS.

Despesas: formas PIX, DINHEIRO, CARTAO_DEBITO, TRANSFERENCIA, BOLETO ou OUTROS.

Restrições importantes:

- Nome com 3 a 100 caracteres.
- `valor > 0`. O sinal exibido e a participação no saldo serão definidos por `tipo`.
- A chave estrangeira composta `(categoria_id, tipo)` deverá apontar para `(categoria_financeira.id, categoria_financeira.tipo)`, impedindo categoria de receita em despesa e vice-versa.
- `importancia_id` somente poderá ser preenchido quando `tipo = DESPESA`.
- A unicidade de `importancia_id` garantirá no máximo um pagamento vinculado a cada ocorrência. Como cada movimentação possui apenas esse campo de vínculo, uma mesma despesa não quitará duas importâncias.
- `importancia_id` e `importancia_vinculada_em` deverão estar ambos nulos ou ambos preenchidos.
- Uma movimentação excluída deverá ficar com esses dois campos de vínculo nulos.
- Na aplicação, exigir uma importância do mesmo usuário, não excluída, com `possui_despesa = verdadeiro` e ainda sem pagamento.
- Validar `data_movimentacao <= hoje` usando o fuso da conta, e não uma data de servidor possivelmente diferente.

O momento de vínculo será necessário para ordenar conclusões: vincular hoje uma despesa antiga conclui a importância hoje, enquanto o gasto continua contabilizado pela data real do pagamento.

11 - LEMBRETE_IMPORTANCIA — `lembrete_importancia`

- id (chave primária, UUID v7 gerado pela aplicação, obrigatório).
- usuario_id (chave estrangeira → usuario.id, UUID, obrigatório).
- importancia_id (chave estrangeira → importancia.id, UUID, obrigatório, único).
- antecedencia_dias (SMALLINT, obrigatório; valores: 0, 1, 3 ou 7).
- horario (TIME, obrigatório; horário local do lembrete).
- agendado_para (DATETIME em UTC, obrigatório).
- versao_agendamento (INT, obrigatório, padrão 1).
- situacao (VARCHAR(10), obrigatório, padrão PENDENTE; valores: PENDENTE, ENVIADO ou CANCELADO).
- enviado_em (DATETIME em UTC, opcional).
- criado_em (DATETIME em UTC, obrigatório).
- atualizado_em (DATETIME em UTC, obrigatório).

Cada ocorrência de importância poderá ter no máximo uma configuração de lembrete. `agendado_para` será calculado a partir da data do compromisso, da antecedência, do horário e do fuso do usuário. Ele será persistido para permitir a busca dos lembretes que precisam ser processados.

No reagendamento, incrementar `versao_agendamento`, recalcular `agendado_para` e limpar `enviado_em`, definindo a situação correspondente. Não incrementar a versão em uma mera repetição do mesmo pedido. Uma versão ENVIADO deverá ter `enviado_em` preenchido; PENDENTE e CANCELADO deverão ter esse campo nulo. Notificações de versões anteriores permanecerão em sua própria tabela.

Concluir ou excluir uma importância cancelará lembretes ainda não enviados. Reabri-la permitirá reativar somente lembretes futuros; se for necessária uma nova programação, incrementar a versão. Antes de processar, verificar novamente a versão atual e a situação da importância, evitando disparo de um agendamento substituído.

12 - NOTIFICACAO — `notificacao`

- id (chave primária, UUID v7 gerado pela aplicação, obrigatório).
- usuario_id (chave estrangeira → usuario.id, UUID, obrigatório).
- lembrete_id (chave estrangeira → lembrete_importancia.id, UUID, obrigatório).
- versao_agendamento (INT, obrigatório).
- titulo (VARCHAR(120), obrigatório).
- mensagem (VARCHAR(500), obrigatório).
- criada_em (DATETIME em UTC, obrigatório).
- lida_em (DATETIME em UTC, opcional).

Criar unicidade para `(lembrete_id, versao_agendamento)`, garantindo no máximo uma notificação interna para cada programação do lembrete. Criar a notificação e marcar a versão do lembrete como enviada na mesma transação.

`lida_em` nulo representará uma notificação não lida. O título e a mensagem serão o conteúdo daquele envio, preservado mesmo se o nome do compromisso mudar posteriormente. A importância será acessível pelo relacionamento `notificacao → lembrete → importancia`.

Este modelo cobre as notificações internas previstas para o sino do aplicativo. Uma integração opcional de push poderá acrescentar o cadastro de dispositivos ou de assinaturas do provedor escolhido.

13 - REQUISICAO_IDEMPOTENTE — `requisicao_idempotente`

- id (chave primária, UUID v7 gerado pela aplicação, obrigatório).
- usuario_id (chave estrangeira → usuario.id, UUID, obrigatório).
- chave (VARCHAR(64), obrigatório; identificador aleatório de uma operação enviado pelo aplicativo).
- acao (VARCHAR(50), obrigatório; exemplo: CADASTRAR_DESPESA).
- conteudo_hash (VARCHAR(64), obrigatório; identificação do conteúdo normalizado da solicitação).
- situacao (VARCHAR(20), obrigatório, padrão EM_PROCESSAMENTO; valores: EM_PROCESSAMENTO ou CONCLUIDA).
- codigo_resposta (SMALLINT, opcional).
- resposta (JSON, opcional; resultado mínimo necessário para responder novamente à mesma operação).
- criado_em (DATETIME em UTC, obrigatório).
- concluida_em (DATETIME em UTC, opcional).

Criar unicidade para `(usuario_id, acao, chave)`. O mesmo envio usará a mesma chave nas novas tentativas. Uma operação nova, mesmo com nome e valor iguais, usará outra chave.

Se a mesma chave vier com conteúdo diferente, rejeitar a reutilização. Se a operação já tiver sido concluída, devolver seu resultado sem executar outro cadastro. O registro da operação, a alteração de negócio e a gravação do resultado deverão participar da mesma transação; uma falha deverá desfazer o conjunto.

Esta tabela de apoio atende às exigências de não duplicar atividades, importâncias, séries e movimentações quando houver cliques repetidos ou perda de conexão. Usá-la nas ações de negócio; não guardar senhas, códigos de recuperação ou tokens de acesso no conteúdo da resposta. A limpeza desses registros, caso seja criada depois, deverá definir explicitamente o prazo de garantia contra reenvio.

RESTRIÇÕES ENTRE REGISTROS DO MESMO USUÁRIO

Um `usuario_id` em cada tabela ajuda nas consultas, mas não impede sozinho um vínculo entre registros de usuários diferentes. Para assegurar a propriedade dos relacionamentos, adicionar as seguintes chaves estrangeiras compostas:

| Tabela de origem | Colunas de origem | Tabela e colunas de destino |
| --- | --- | --- |
| atividade | serie_id, usuario_id | serie_atividade.id, serie_atividade.usuario_id |
| importancia | serie_id, usuario_id | serie_importancia.id, serie_importancia.usuario_id |
| movimentacao_financeira | importancia_id, usuario_id | importancia.id, importancia.usuario_id |
| lembrete_importancia | importancia_id, usuario_id | importancia.id, importancia.usuario_id |
| notificacao | lembrete_id, usuario_id | lembrete_importancia.id, lembrete_importancia.usuario_id |

Adicionar `UNIQUE(id, usuario_id)` nas tabelas de destino que participarem dessas referências. Embora o ID já seja único, o par fornece a chave referenciada pela restrição composta. No SQLAlchemy, usar `ForeignKeyConstraint` para cada par; duas chaves estrangeiras independentes não garantem a correspondência entre os valores.

As referências compostas acima substituem a referência simples ao registro relacionado indicada na lista de campos. A referência de `usuario_id` para `usuario.id` continua existindo. As categorias são catálogos compartilhados, por isso não possuem `usuario_id`.

REGRAS DE INTEGRIDADE E EXCLUSÃO

1. Aplicar `NOT NULL`, `UNIQUE`, `CHECK` e as chaves estrangeiras no banco. Manter também validações de formulário e serviço. Limites de caracteres e comparações com a data atual precisarão considerar o dialeto e o fuso do usuário.

2. Para condições opcionais, testar explicitamente `IS NULL` e `IS NOT NULL`. Por exemplo, valor previsto válido exige: sem despesa e valor nulo, ou com despesa e valor não nulo e positivo. Apenas um teste `valor > 0` não torna uma coluna opcional obrigatória quando necessário.

3. Usar exclusão lógica por `excluida_em` em atividades, importâncias e movimentações. Consultas, totais, pagamentos disponíveis para vínculo e indicadores deverão excluir esses registros. O propósito principal é preservar as ocorrências removidas para que a geração de uma série não as recrie.

4. Excluir uma movimentação vinculada deverá, na mesma transação, marcar sua exclusão, remover `importancia_id` e `importancia_vinculada_em` e ajustar o lembrete quando aplicável. A importância voltará a Pendente pela regra de situação calculada.

5. Excluir uma importância deverá marcar sua exclusão, cancelar seu lembrete pendente e remover o vínculo da movimentação, preservando o valor, a data e os efeitos financeiros dessa movimentação. As notificações antigas continuarão legíveis e o acesso ao compromisso indicará sua indisponibilidade.

6. Vincular uma despesa existente deverá preencher o vínculo e o momento do vínculo, sem criar outro lançamento nem contabilizar seu valor novamente. Ao trocar o vínculo, verificar e modificar os registros afetados na mesma transação; recalcular os lembretes das importâncias anterior e nova.

7. A unicidade protege contra dois pagamentos para uma mesma importância, mas não substitui a validação do estado atual do compromisso. Serializar operações concorrentes sobre os mesmos registros, usando os recursos transacionais do banco escolhido. Ao mudar uma importância para sem despesa, exigir que ela não tenha pagamento vinculado.

8. Para essas referências de negócio, preferir `ON DELETE RESTRICT`/`NO ACTION`, com remoção lógica ou desvinculação explícita pelo serviço. Não aplicar exclusão em cascata de importância para movimentação financeira. Não usar `SET NULL` indiscriminadamente em uma FK composta com `usuario_id`, pois isso pode tentar anular também a propriedade do registro.

9. A exclusão definitiva de conta não foi especificada nas telas e precisará de um fluxo próprio antes de configurar cascatas gerais em `usuario`. A configuração `cascade` do relacionamento ORM deverá ser coerente com essas decisões; remover um vínculo não deverá apagar automaticamente uma despesa.

**COMO AS REPETIÇÕES SERÃO REPRESENTADAS**

Uma tarefa avulsa terá uma linha em `atividade`, com série e número nulos. Uma tarefa semanal terá uma linha em `serie_atividade` e uma linha em `atividade` para cada ocorrência necessária. O mesmo princípio valerá para Importâncias.

`numero_ocorrencia` será uma identidade estável: 1, 2, 3 e assim por diante. Alterar individualmente a data de uma tarefa não alterará seu número. Excluir uma ocorrência preencherá sua exclusão lógica e manterá a chave única ocupada, impedindo recriação acidental.

Antes de mostrar uma data, um mês ou um total de pendências, gerar as ocorrências necessárias ao intervalo consultado, incluindo as anteriores relevantes. Uma repetição sem data final não deverá ser materializada infinitamente. Para “próximas três”, buscar e gerar ocorrências até conseguir os próximos itens válidos ou até atingir o limite da série. Os totais mensais não poderão considerar apenas os itens já carregados na tela.

Na repetição mensal, calcular cada data a partir do dia de referência, usando o último dia do mês quando necessário: 31 de janeiro, último dia de fevereiro, 31 de março. Na anual, preservar a referência de 29 de fevereiro, usando 28 em ano não bissexto.

Ao editar somente uma ocorrência, alterar sua linha, sem mudar o padrão da série. Ao editar esta e as próximas pendentes, usar o número original selecionado como limite de alcance. Preservar anteriores, concluídas e exclusões individuais; atualizar os valores padrão e os dados das ocorrências pendentes abrangidas. A geração futura deverá usar a nova referência.

Nesta proposta, a série guarda sua regra vigente, enquanto as ocorrências materializadas preservam seus próprios dados. Antes de mudar a referência da série, materializar todas as posições anteriores ao ponto de alteração, para que nenhum trecho histórico dependa da regra substituída. Ajustar `numero_referencia` e `data_referencia` para manter a correspondência da nova regra. Serializar essa alteração e a geração concorrente.

Ao excluir esta e as próximas pendentes, limitar a geração a `numero_ocorrencia selecionado − 1` e marcar as pendentes abrangidas como excluídas. Ocorrências concluídas já existentes poderão permanecer depois desse limite, pois ele limita a geração, não apaga o histórico.

Para uma mudança de periodicidade que elimine posições pendentes futuras, marcar essas posições como excluídas na mesma operação. Um comando posterior não deverá reativar silenciosamente ocorrências explicitamente excluídas. A lógica de geração e alteração é um serviço da aplicação; o ORM e as tabelas não a executarão automaticamente.

INFORMAÇÕES CALCULADAS — SEM TABELA OU COLUNA PRÓPRIA NESTA VERSÃO

| Informação | Origem do cálculo |
| --- | --- |
| Receitas do dia ou mês | Soma de movimentações RECEITA não excluídas no período. |
| Despesas do dia ou mês | Soma de movimentações DESPESA não excluídas no período. |
| Saldo | Receitas menos despesas do mesmo período. |
| Duração de uma atividade | Horário final menos horário inicial. |
| Tempo total planejado | Soma das durações das ocorrências que correspondem aos filtros. |
| Pendente ou Concluída, em atividades | Ausência ou presença de concluida_em, excluindo registros removidos. |
| Pendente, Concluída ou Pago, em importâncias | Conclusão manual quando sem despesa, ou existência de pagamento válido quando com despesa. |
| Momento de conclusão da importância | concluida_manualmente_em, ou importancia_vinculada_em do pagamento. |
| Valor e data do pagamento | valor e data_movimentacao da despesa vinculada. |
| Atrasada, Hoje ou Em X dias | Situação pendente e comparação da data do compromisso com hoje. |
| Quantidades, gráficos e percentuais | Consultas sobre os mesmos registros usados nos indicadores. |
| Notificações não lidas | Notificações cujo lida_em seja nulo. |

Portanto, não criar tabelas `tela_inicial`, `saldo`, `grafico`, `total_atividades` ou `confirmar_senha`.

**ÍNDICES INICIAIS**

- atividade: `(usuario_id, data_atividade)` e `(usuario_id, concluida_em, data_atividade)`.
- importancia: `(usuario_id, data_compromisso)`.
- movimentacao_financeira: `(usuario_id, data_movimentacao)`, `(usuario_id, tipo, data_movimentacao)` e `(usuario_id, categoria_id, data_movimentacao)`.
- lembrete_importancia: `(situacao, agendado_para)`.
- notificacao: `(usuario_id, lida_em, criada_em)`.

As restrições únicas já indicadas também deverão ser criadas, especialmente e-mail, identificação de ocorrências, vínculo de pagamento, versão de notificação e chave de reenvio. Revisar os demais índices conforme as consultas reais e o volume de dados.

**MAPEAMENTO PARA SQLALCHEMY**

| Especificação | Tipo ou configuração no ORM |
| --- | --- |
| UUID (identificadores) | Uuid; PK com primary_key=True e default=uuid.uuid7 (aplicação), sem server_default. |
| INT (demais colunas inteiras) | Integer. |
| SMALLINT | SmallInteger. |
| VARCHAR(n) | String(n). |
| BOOLEAN | Boolean. |
| DATE | Date, usando datetime.date no Python. |
| TIME | Time, usando datetime.time no Python. |
| DATETIME em UTC | DateTime(timezone=True), com normalização para UTC e adaptação ao banco escolhido. |
| DECIMAL(12,2) | Numeric(12, 2, asdecimal=True), utilizando Decimal no Python. |
| JSON | JSON(none_as_null=True): `None` do Python grava `NULL` do SQL. |
| Obrigatório/opcional | nullable=False / nullable=True. |
| Chave estrangeira simples | ForeignKey. |
| Chave estrangeira composta | ForeignKeyConstraint. |
| Unicidade simples/composta | unique=True / UniqueConstraint. |
| Regras de domínio | CheckConstraint, além da validação da aplicação. |
| Relação entre objetos | relationship; não substitui PK, FK ou UNIQUE. |

Para os campos de valores controlados, utilizar enumerações Python com armazenamento textual validado. No SQLAlchemy, usar `Enum(..., native_enum=False, create_constraint=True, validate_strings=True)`, com a restrição nomeada `ck_<tabela>_<coluna>` (DEC-MV-07), de forma consistente, distinguindo os valores técnicos, como MEDIA, dos rótulos exibidos, como Média.

Dinheiro: DECIMAL(12,2) estabelece um máximo por lançamento de R$ 9.999.999.999,99, um limite técnico proposto a validar no formulário. Não utilizar Float nem converter entradas monetárias primeiro para float. Validar até duas casas decimais antes da gravação, sem arredondar silenciosamente uma entrada com precisão maior. Totais poderão ultrapassar o limite individual e deverão ser calculados com precisão suficiente. O SGBD é PostgreSQL, cujo NUMERIC é exato.

Datas: o formato DD/MM/AAAA pertence à apresentação. Datas de nascimento, atividades e pagamentos serão valores Date; instantes como criação, conclusão e envio serão normalizados para UTC. A flag timezone=True não garante suporte uniforme a fuso em todos os bancos; confirmar o comportamento do dialeto.

Timestamps (DEC-MV-07): `criado_em` e `criada_em` usam `server_default=now()`, aplicado pelo banco em toda inserção que omite a coluna. `atualizado_em` usa `server_default=now()` na inserção e `onupdate=now()`, que o SQLAlchemy acrescenta aos UPDATEs que ele mesmo emite (ORM e Core); um UPDATE em SQL textual não altera `atualizado_em`. O `now()` do PostgreSQL é o início da transação. Com `eager_defaults`, os valores gerados voltam por `RETURNING`. Detalhe em docs/arquitetura/arquitetura_api_minhavida.md §10.3.

O uso de `relationship` para expressar um pagamento único não basta para impor essa regra no banco: manter também a restrição única de `movimentacao_financeira.importancia_id`.


