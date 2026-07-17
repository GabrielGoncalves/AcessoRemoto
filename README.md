# 🚀 Remote Craft

O **Remote Craft** é um gerenciador moderno e centralizado de conexões remotas, projetado para simplificar a administração de servidores, ambientes corporativos e identidades de acesso. 

Construído com Python e Flet, ele oferece uma interface nativa, rápida e fluida, operando de forma 100% autônoma (*cross-platform*) e mantendo seus dados seguros localmente através de um banco de dados SQLite.

---

## 🛠️ Principais Recursos

*   **Gestão de Identidades Inteligente:** Separação automática de usuários e domínios de rede para facilitar a seleção de credenciais e evitar digitação repetitiva.
*   **Organização por Ambientes:** Agrupe dezenas de conexões e servidores em "Fazendas" (Ambientes) para manter sua área de trabalho limpa e organizada.
*   **Cofre de Favoritos:** Acesso rápido aos servidores e máquinas mais acessados do seu dia a dia.
*   **Backup e Restauração Nativa:** Crie cópias de segurança de toda a sua configuração com um clique. Em caso de problemas, o sistema faz a restauração segura e reinicia a aplicação automaticamente.
*   **Limpeza Automática:** Configure o aplicativo para reter o histórico de conexões por 1, 3, 7, 30 dias, ou limpar os rastros automaticamente a cada inicialização.

---

## 📦 Importando Dados Legados

Se você é usuário de versões anteriores, o Remote Craft facilita a migração dos seus dados utilizando arquivos `.json`.

1. Vá até a aba **Configurações > Dados & Backup**.
2. Clique em **Importar Arquivos**.
3. Selecione seus arquivos antigos. O sistema reconhecerá e mapeará automaticamente:
   * `config.json`: Para importar sua credencial e domínio padrão.
   * `favoritos.json`: Para migrar sua lista de acessos rápidos.
   * `[Nome_do_Ambiente].json`: Para criar uma fazenda completa de conexões (ex: `Farm0003.json`).

> **Dica:** Caso não tenha os arquivos, utilize o botão **Gerar Modelos** na mesma aba para gerar a estrutura correta preenchida com exemplos, editar no Bloco de Notas e importar novamente!

---

## 🧠 Arquitetura Técnica e Módulos (Para Desenvolvedores)

O sistema foi estritamente modularizado seguindo padrões de projeto (como o MVC e o Single Responsibility Principle) para separar a interface visual (UI) da lógica de negócios e segurança.

### 1. Núcleo da Aplicação (`app.py`)
O arquivo principal orquestra a inicialização e o roteamento da interface gráfica.
*   **Gestão de Estado:** A classe `MainApplication` centraliza as instâncias do banco de dados e repassa via injeção de dependência para as *Views* (Telas).
*   **Manutenção de Boot:** Na inicialização, o sistema verifica a regra de retenção do usuário e realiza a exclusão de históricos antigos antes mesmo da interface ser renderizada.
*   **Roteamento Dinâmico:** Utiliza o componente `NavigationRail` do Flet, montando o menu lateral de forma dinâmica (ex: exibindo a aba "API" apenas se a flag correspondente estiver ativada no banco).

### 2. Motor de Conexão Cross-Platform (`core/rdp_engine.py`)
A classe `RDPAngine` traduz o pedido de conexão da interface para comandos nativos do sistema operacional de forma isolada e segura.
*   **Geração Dinâmica:** Constrói um arquivo `launcher.rdp` temporário em diretórios ocultos do usuário (`AppData` no Windows ou `Application Support` no Mac).
*   **Segurança no Windows:** Utiliza a biblioteca `ctypes` para criptografar a senha do usuário nativamente através da API **DPAPI** (`CryptProtectData`), injetando um hash blindado diretamente no arquivo RDP.
*   **Segurança no macOS:** Como o cliente de RDP do Mac não aceita injeção direta por arquivo, o aplicativo copia a senha silenciosamente para a área de transferência (usando `pbcopy`), bastando o usuário colar (`Cmd+V`) na tela de login.
*   **Segurança no Linux:** Utiliza o `xfreerdp` injetando a senha em uma variável de ambiente efêmera (`XFREERDP_PASSWORD`), impedindo que a credencial vaze no histórico do terminal.
*   **Anti-Rastreio (Auto-Delete):** Uma *thread* paralela apaga o arquivo RDP físico após 5 segundos, não deixando rastros na máquina.

### 3. Persistência de Dados (`database/db_manager.py`)
O banco de dados SQLite (`autordp.db`) opera em regime estrito com controle de integridade transacional.
*   **Autocura e Migração:** A inicialização do banco (`_init_db`) aplica rotinas para dropar esquemas obsoletos de versões antigas do app.
*   **Modelagem Relacional:** Relacionamento com chave estrangeira nativa (`FOREIGN KEY`) entre `ambientes` e `conexoes_ambientes` com exclusão em cascata (`ON DELETE CASCADE`).
*   **Chave-Valor:** Preferências e configurações de interface operam em uma tabela simplificada (`configuracoes`) facilitando o _upsert_ (`INSERT OR REPLACE`).

### 4. Integração Web e Serviços (`services/api_service.py` e `view_api.py`)
O módulo de testes de API foi desacoplado.
*   **Isolamento de Rede:** O `ApiService` encapsula toda a complexidade do módulo nativo `urllib`, lidando com *timeouts*, *headers* e o decodificador UTF-8, devolvendo os dados limpos.
*   **Sanitização Visual:** A view recebe a resposta da rede e constrói dinamicamente tabelas interativas (`DataTables`) ou listas baseadas na estrutura profunda do JSON recebido.

### 5. Segurança e Credenciais (`services/password_service.py`)
Fornece um gerador de senhas robusto e "CLI-Safe" (seguro para linha de comando).
*   **Criptograficamente Seguro:** Utiliza a biblioteca nativa `secrets` do Python para garantir entropia real.
*   **Sanitização de Caracteres Especiais:** Restringe a pontuação apenas para `_-.`, evitando falhas de injeção ou quebra de *strings* ao acionar binários como o `xfreerdp`.
*   **Proteção de Argumentos:** Impede proativamente que a credencial comece com um símbolo, garantindo que o interpretador do sistema operacional não confunda a senha com uma *flag* ou argumento de comando.