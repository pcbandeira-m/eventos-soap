from xmlrpc.client import Fault
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

# Armazenamento em memória usando uma lista (array) simples
lista_eventos = []
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

        # Adiciona o evento ao final da lista em memória
        lista_eventos.append(novo_evento)
        proximo_id += 1
        return novo_evento

    @rpc(_returns=Array(Evento))
    def ListarEventos(ctx):
        """Retorna todos os eventos armazenados na lista em memória."""
        return lista_eventos

    @rpc(Integer, Unicode, Unicode, Unicode, Unicode, Integer, _returns=Evento)
    def AtualizarEvento(ctx, id, titulo, data, local, categoria, qtdConvidados):
        """Percorre a lista pelo ID e atualiza os campos do evento correspondente."""
        for indice, evento in enumerate(lista_eventos):
            if evento.id == id:
                # Cria o objeto atualizado mantendo o ID original
                evento_atualizado = Evento(
                    id=id,
                    titulo=titulo,
                    data=data,
                    local=local,
                    categoria=categoria,
                    qtdConvidados=qtdConvidados
                )
                # Substitui o item na mesma posição da lista
                lista_eventos[indice] = evento_atualizado
                return evento_atualizado

        # Se o loop terminar sem encontrar o ID, dispara uma falha SOAP padronizada (<soap:Fault>).
        # faultcode="Client" indica que o erro foi causado por um dado inválido enviado pelo cliente.
        raise Fault(
            faultcode="Client",
            faultstring=f"Evento com ID {id} não foi encontrado para atualização."
        )

    @rpc(Integer, _returns=Boolean)
    def DeletarEvento(ctx, id):
        """Percorre a lista pelo ID e remove o evento correspondente. Dispara <soap:Fault> se o ID não existir."""
        for indice, evento in enumerate(lista_eventos):
            if evento.id == id:
                lista_eventos.pop(indice)
                return True

        # Se o ID não existir na lista, interrompe a execução e devolve o XML <soap:Fault>
        raise Fault(
            faultcode="Client",
            faultstring=f"Evento com ID {id} não foi encontrado para exclusão."
        )

# 3. Configuração da Aplicação SOAP e Geração do WSDL
application = Application(
    services=[EventoService],
    tns="http://eventos.soap.exemplo/wsdl",
    name="EventoService",
    in_protocol=Soap11(validator="lxml"),   # Valida o XML recebido contra o esquema XSD
    out_protocol=Soap11(),                  # Serializa as respostas no padrão SOAP 1.1
)

# 4. Empacotamento WSGI para ser servido via HTTP
wsgi_application = WsgiApplication(application)

# 5. Inicialização do servidor HTTP local
if __name__ == "__main__":
    host = "127.0.0.1"
    port = 8000

    # Cria o servidor HTTP nativo do Python apontando para a aplicação SOAP
    server = make_server(host, port, wsgi_application)

    print(f"Servidor SOAP de Eventos ativo em http://{host}:{port}")
    print(f"Contrato WSDL disponível em http://{host}:{port}/?wsdl")

    # Mantém o servidor escutando requisições continuamente
    server.serve_forever()