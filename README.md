# Dell G3 RGB Controller

Controlador leve para o teclado RGB 4 zonas do Dell G3 3500.

Este pacote foi criado para controlar a iluminacao do teclado sem depender do Alienware Command Center. A motivacao foi bem pratica: o Alienware Command Center e pesado, demora para abrir, consome recursos demais para uma tarefa simples e muitas vezes falha justamente quando a gente so quer trocar a cor do teclado.

A ideia deste projeto e fazer o basico muito bem: ligar a luz, desligar a luz e trocar as cores com perfis simples, leves e rapidos.

## Como Usar

Para ligar ou preparar o teclado RGB depois que o Windows iniciar, use:

```text
scripts\TURN_ON.bat
```

Esse arquivo pode pedir permissao de administrador. Ele nao escolhe cor; ele apenas acorda/reseta o controlador RGB interno da Dell quando o teclado nao responde.

Para desligar a luz:

```text
scripts\TURN_OFF.bat
```

Para aplicar um perfil de cor, abra a pasta `colors` e execute um dos arquivos `PROFILE_*.bat`.

## Perfis Disponiveis

Os perfis atuais usam as zonas 1, 2 e 3 com a mesma cor principal. A zona 4, que corresponde ao teclado numerico, recebe uma cor diferente que combina com o tema.

```text
PROFILE_ARCTIC_DEV.bat
PROFILE_CYBERPUNK_NUMPAD.bat
PROFILE_CYBERPUNK_ZONES.bat
PROFILE_DEEP_SPACE.bat
PROFILE_DOCKER_BUILD.bat
PROFILE_GIT_HEAT.bat
PROFILE_MATRIX_FOCUS.bat
PROFILE_NIGHT_OPS.bat
PROFILE_RUBY_COMBAT.bat
PROFILE_SOLARIZED_WORK.bat
PROFILE_TOXIC_PURPLE.bat
```

`PROFILE_CYBERPUNK_ZONES.bat` e o perfil especial em que cada zona recebe uma cor diferente no estilo cyberpunk.

## Zonas Do Teclado

O teclado e tratado como 4 zonas:

```text
Zone1
Zone2
Zone3
Zone4
```

Nos perfis padrao, `Zone1`, `Zone2` e `Zone3` formam a area principal do teclado. `Zone4` fica separada para destacar o teclado numerico.

Cada perfil informa:

```text
cor da Zone1
cor da Zone2
cor da Zone3
cor da Zone4
brilho da Zone1
brilho da Zone2
brilho da Zone3
brilho da Zone4
```

## Estrutura Do Pacote

O projeto esta organizado em uma estrutura pequena no estilo Hexagonal/Diplomat:

```text
src/core           controlador RGB direto via HID
src/adapters/wmi   adaptador Dell WMI para acordar/resetar o controlador
scripts            atalhos principais de operacao
colors             perfis de cor
```

O controle de cor conversa diretamente com o dispositivo HID `VID_187C/PID_0550`. O WMI da Dell e usado apenas no `TURN_ON.bat`, para acordar o controlador RGB quando ele ainda nao apareceu corretamente para o Windows.

## Movendo A Pasta

A pasta raiz `DellG3RgbController` pode ser movida para outro local do mesmo computador. Os perfis em `colors`, os atalhos em `scripts` e o codigo em `src` usam caminhos relativos entre si.

O programa usa Python para executar `src/core/dell_g3_rgb.py`. O script `scripts/rgb.ps1` procura nesta ordem:

```text
runtime\python\python.exe
py -3, quando o Python Launcher do Windows existir
python disponivel no PATH do Windows
```

Se nenhuma dessas opcoes existir, o proprio script baixa automaticamente um Python portatil para `runtime\python`. Esse download nao instala Python globalmente, nao muda o PATH do Windows e nao precisa de administrador.

Depois do primeiro download, os perfis funcionam offline usando o runtime local. O repositorio tambem inclui o runtime portatil para que o projeto clonado ja tenha tudo dentro da pasta.

A logica de auto-download continua existindo como recuperacao: se `runtime\python` for apagado, o programa recria essa pasta automaticamente no proximo uso com internet.

## Editando Um Perfil

Um perfil e apenas um arquivo `.bat` dentro da pasta `colors`. Exemplo de formato:

```text
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0..\scripts\rgb.ps1" zones -Zone1 "#0066ff" -Zone2 "#0066ff" -Zone3 "#0066ff" -Zone4 "#00e5ff" -Zone1Brightness 100 -Zone2Brightness 100 -Zone3Brightness 100 -Zone4Brightness 100
```

As cores usam formato hexadecimal `#RRGGBB`. O brilho vai de `0` a `100`.

## Observacoes

Se um perfil nao mudar a cor depois de reiniciar o computador, execute primeiro `scripts\TURN_ON.bat` e depois rode o perfil novamente.

Os perfis nao dependem do Alienware Command Center. Eles usam o controlador Python em `src/core/dell_g3_rgb.py`, chamado pelos scripts PowerShell e pelos arquivos `.bat`.
