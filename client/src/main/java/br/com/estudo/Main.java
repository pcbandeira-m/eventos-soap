package br.com.estudo;

// Classes geradas pelo wsimport, que implementa a interface do serviço SOAP
import br.com.estudo.soap.client.Evento;
import br.com.estudo.soap.client.EventoService;
import br.com.estudo.soap.client.EventoService_Service;
import jakarta.xml.bind.JAXBElement;
import jakarta.xml.ws.BindingProvider;

import javax.xml.namespace.QName;
import java.math.BigInteger;
import java.net.MalformedURLException;
import java.net.URI;
import java.util.List;
import java.util.Scanner;

// Nota a um tipo de dado do XML Schema (XSD)
//  xs:integer -> java.math.BigInteger

public class Main {
    private static final String WSDL_URL = System.getenv().getOrDefault("WSDL_URL", "http://127.0.0.1:8000/?wsdl");
    // QName significa Qualified Name, ou nome qualificado em XML. Ele identifica um elemento ou serviço XML de forma única
    private static final QName SERVICE_NAME = new QName("http://eventos.soap.exemplo/wsdl", "EventoService");

    public static void main(String[] args) {
        try (Scanner scanner = new Scanner(System.in)) {
            EventoService service = createService();
            boolean running = true;
            while (running) {
                printMenu();
                String option = scanner.nextLine().trim();
                try {
                    switch (option) {
                        case "1" -> create(scanner, service);
                        case "2" -> list(service);
                        case "3" -> update(scanner, service);
                        case "4" -> delete(scanner, service);
                        case "0" -> running = false;
                        default -> System.out.println("Opção inválida.");
                    }
                } catch (RuntimeException exception) {
                    System.out.println("Não foi possível concluir a operação: " + exception.getMessage());
                }
            }
        }

        System.out.println("Programa encerrado.");
    }

    private static EventoService createService() {
        try {
            // Cria uma instância do serviço de eventos usando a URL do WSDL e o nome do serviço
            // O método getEventoService() retorna a porta do serviço, que é usada para fazer chamadas ao serviço SOAP
            EventoService port = new EventoService_Service(URI.create(WSDL_URL).toURL(), SERVICE_NAME).getEventoService();
            ((BindingProvider) port).getRequestContext()
                    .put(BindingProvider.ENDPOINT_ADDRESS_PROPERTY, WSDL_URL.replace("?wsdl", ""));
            return port;
        } catch (MalformedURLException exception) {
            throw new IllegalStateException("URL do WSDL inválida: " + WSDL_URL, exception);
        }
    }

    private static void printMenu() {
        System.out.println("\n=== Eventos ===");
        System.out.println("1. Criar");
        System.out.println("2. Listar");
        System.out.println("3. Atualizar");
        System.out.println("4. Deletar");
        System.out.println("0. Sair");
        System.out.print("Escolha uma opção: ");
    }

    private static void create(Scanner scanner, EventoService service) {
        Evento evento = service.criarEvento(
                readText(scanner, "Título: "),
                readText(scanner, "Data: "),
                readText(scanner, "Local: "),
                readText(scanner, "Categoria: "),
                BigInteger.valueOf(readInteger(scanner, "Quantidade de convidados: ")));
        System.out.println("Evento criado:");
        printEvento(evento);
    }

    private static void list(EventoService service) {
        /*
        service.listarEventos()
        Chama a operação SOAP ListarEventos no servidor. Ela retorna um objeto EventoArray, não uma lista diretamente.

        .getEvento()
        Obtém a lista armazenada dentro de EventoArray.
        */
        List<Evento> eventos = service.listarEventos().getEvento();
        if (eventos.isEmpty()) {
            System.out.println("Nenhum evento cadastrado.");
            return;
        }
        eventos.forEach(Main::printEvento);
    }

    private static void update(Scanner scanner, EventoService service) {
        int id = readInteger(scanner, "ID do evento: ");
        Evento evento = service.atualizarEvento(
                BigInteger.valueOf(id),
                readText(scanner, "Título: "),
                readText(scanner, "Data: "),
                readText(scanner, "Local: "),
                readText(scanner, "Categoria: "),
                BigInteger.valueOf(readInteger(scanner, "Quantidade de convidados: ")));
        if (evento == null) {
            System.out.println("Evento não encontrado.");
        } else {
            System.out.println("Evento atualizado:");
            printEvento(evento);
        }
    }

    private static void delete(Scanner scanner, EventoService service) {
        int id = readInteger(scanner, "ID do evento: ");
        if (service.deletarEvento(BigInteger.valueOf(id))) {
            System.out.println("Evento deletado.");
        } else {
            System.out.println("Evento não encontrado.");
        }
    }

    private static String readText(Scanner scanner, String message) {
        System.out.print(message);
        String value = scanner.nextLine().trim();
        if (value.isEmpty()) {
            throw new IllegalArgumentException("O valor não pode ser vazio.");
        }
        return value;
    }

    private static int readInteger(Scanner scanner, String message) {
        while (true) {
            System.out.print(message);
            try {
                return Integer.parseInt(scanner.nextLine().trim());
            } catch (NumberFormatException exception) {
                System.out.println("Digite um número inteiro válido.");
            }
        }
    }

    private static void printEvento(Evento evento) {
        System.out.printf("ID: %s | Título: %s | Data: %s | Local: %s | Categoria: %s | Convidados: %s%n",
                value(evento.getId()), value(evento.getTitulo()), value(evento.getData()),
                value(evento.getLocal()), value(evento.getCategoria()), value(evento.getQtdConvidados()));
    }

    /*
    O WSDL possui campos potencialmente nulos:
    <xs:element name="titulo" type="xs:string" minOccurs="0" nillable="true"/>
    Por isso os valores gerados não são String ou BigInteger diretamente, mas JAXBElement<String> e JAXBElement<BigInteger>.

    Essa função extrai o conteúdo
    */
    private static <T> T value(JAXBElement<T> element) {
        return element == null ? null : element.getValue();
    }
}

