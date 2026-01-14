{ pkgs, ... }: {
  # Qual canal nixpkgs usar.
  channel = "stable-24.05"; 

  # Pacotes a serem instalados no ambiente
  packages = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.poetry
  ];

  # Variáveis de ambiente
  env = {};

  # Configuração do IDX
  idx = {
    # Extensões do VS Code
    extensions = [
      "ms-python.python"
      "google.gemini-cli-vscode-ide-companion"
    ];

    # Configuração de Previews (O servidor web)
    previews = {
      enable = true;
      previews = {
        web = {
          # A CORREÇÃO CRUCIAL ESTÁ AQUI EMBAIXO: SEM VÍRGULAS NA LISTA!
          command = [ "poetry" "run" "uvicorn" "main:app" "--host" "0.0.0.0" "--port" "$PORT" ];
          manager = "web";
        };
      };
    };

    # Hooks de ciclo de vida (opcional, mas bom ter)
    workspace = {
      onCreate = {
        # Instala dependências na primeira criação
        install-dependencies = "poetry install"; 
      };
      onStart = {
        # Garante instalação ao iniciar
        install-dependencies = "poetry install";
      };
    };
  };
}
