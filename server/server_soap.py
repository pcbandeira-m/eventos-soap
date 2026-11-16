from spyne import Application, rpc, ServiceBase, Integer, Unicode, Boolean, Array, ComplexModel
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from wsgiref.simple_server import make_server

# 1. Definição do Modelo Complexo (Entidade Evento no WSDL/XSD)
class Evento(ComplexModel):
    id = Integer
    titulo = Unicode
    data = Unicode
    local = Unicode
    categoria = Unicode
    qtdConvidados = Integer

# Banco de dados simulado em memória
eventos_db = {}
proximo_id = 1

# 2. Definição do Serviço e das 4 Operações CRUD
class EventoService(ServiceBase):

    @rpc(Unicode, Unicode, Unicode, Unicode, Integer, _returns=Evento)
    def CriarEvento(ctx, titulo, data, local, categoria, qtdConvidados):
        """Cria um novo evento e retorna o objeto criado com seu ID."""
        global proximo_id
        
        novo_evento = Evento(
            id=proximo_id,
            titulo=titulo,
            data=data,
            local=local,
            categoria=categoria,
            qtdConvidados=qtdConvidados
        )
        
        eventos_db[proximo_id] = novo_evento
        proximo_id += 1
        return novo_evento

    @rpc(_returns=Array(Evento))
    def ListarEventos(ctx):
        """Retorna uma lista com todos os eventos cadastrados."""
        return list(eventos_db.values())

    @rpc(Integer, Unicode, Unicode, Unicode, Unicode, Integer, _returns=Evento)
    def AtualizarEvento(ctx, id, titulo, data, local, categoria, qtdConvidados):
        """Atualiza os dados de um evento existente pelo ID."""
        if id not in eventos_db:
            return None  # Retorna vazio no XML caso o ID não exista
        
        evento_atualizado = Evento(
            id=id,
            titulo=titulo,
            data=data,
            local=local,
            categoria=categoria,
            qtdConvidados=qtdConvidados
        )
        
        eventos_db[id] = evento_atualizado
        return evento_atualizado

    @rpc(Integer, _returns=Boolean)
    def DeletarEvento(ctx, id):
        """Remove um evento pelo ID. Retorna True se removido, False se não encontrado."""
        if id in eventos_db:
            del eventos_db[id]
            return True
        return False

# 3. Configuração da Aplicação SOAP e Geração do WSDL
application = Application(
    services=[EventoService],
    tns="http://eventos.soap.exemplo/wsdl",
    name="EventoService",
    in_protocol=Soap11(validator="lxml"),
    out_protocol=Soap11(),
)

wsgi_application = WsgiApplication(application)

if __name__ == "__main__":
    host = "127.0.0.1"
    port = 8000
    server = make_server(host, port, wsgi_application)
    print(f"Servidor SOAP de Eventos ativo em http://{host}:{port}")
    print(f"Contrato WSDL disponível em http://{host}:{port}/?wsdl")
    server.serve_forever()