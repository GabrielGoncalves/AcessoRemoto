# 🚀 Remote Craft

O **Remote Craft** é um gerenciador moderno e centralizado de conexões remotas, projetado para simplificar a administração de servidores, ambientes corporativos e identidades de acesso. 

Construído com Python e Flet, ele oferece uma interface nativa fluida com gerenciamento de dados local seguro via SQLite.

---

## 🛠️ Principais Recursos

*   **Gestão de Identidades Inteligente:** Separação automática de usuários e domínios de rede para facilitar a seleção de credenciais e evitar digitação repetitiva.
*   **Organização por Ambientes:** Agrupe dezenas de conexões e servidores em "Fazendas" (Ambientes) para manter sua área de trabalho limpa e organizada.
*   **Cofre de Favoritos:** Acesso rápido aos servidores e máquinas mais acessados do seu dia a dia.
*   **Backup e Restauração Nativa:** Crie cópias de segurança de toda a sua configuração com um clique. Em caso de problemas, o sistema faz a restauração e reinicia a aplicação automaticamente de forma segura.
*   **Limpeza Inteligente:** Configure o aplicativo para reter o histórico de conexões por 1, 3, 7, 30 dias, ou limpar automaticamente a cada inicialização.

---

## 📦 Importando Dados Legados

Se você é usuário de versões anteriores, o Remote Craft facilita a migração dos seus dados utilizando arquivos `.json`.

1. Vá até a aba **Configurações > Dados & Backup**.
2. Clique em **Importar Arquivos**.
3. Selecione seus arquivos antigos. O sistema reconhecerá automaticamente:
   * `config.json`: Para importar sua credencial padrão.
   * `favoritos.json`: Para migrar sua lista de acessos rápidos.
   * `[Nome_do_Ambiente].json`: Para criar uma fazenda completa de conexões (ex: `Farm0003.json`).

> **Dica:** Caso não tenha os arquivos, utilize o botão **Gerar Modelos** na mesma aba para baixar a estrutura correta preenchida com exemplos, editar e importar novamente!

---

## ⚙️ Estrutura e Métodos Principais (Para Desenvolvedores)

O projeto é modularizado para facilitar a manutenção. Abaixo, as principais classes do núcleo de dados:

*   **`DatabaseManager` (`db_manager.py`):** 
    *   `obter_configuracao` / `salvar_configuracao`: Trata as preferências do usuário.
    *   `adicionar_usuario` / `adicionar_dominio`: Abastece as tabelas de identidades.
    *   `adicionar_conexao_ambiente`: Injeta de forma dinâmica novas máquinas a uma fazenda.
*   **`ViewSettings` (`view_settings.py`):**
    *   Contém a lógica de interface administrativa e funções assíncronas para chamadas de sistema, como o `FilePicker` do Flet e o módulo `shutil` para clonagem de banco de dados (`autordp.db`).