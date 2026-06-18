## Ajustes necessários no fluxo de Origem, Tipos de Arquivo e Destinos

Atualmente, o aplicativo possui uma aba de **Origem**, uma aba de **Destino** e uma aba de **Restrições**. Esse modelo não atende corretamente ao objetivo do projeto, porque as restrições/filtros precisam estar relacionadas a cada origem e também aos destinos que receberão determinados tipos de arquivo.

A nova lógica deve seguir este modelo:

```text
Origem → Tipos de Arquivo → Destinos
```

Ou seja, cada **origem** deve possuir sua própria lista de **tipos de arquivo**. Cada tipo de arquivo representa um conjunto de regras/filtros que define quais arquivos daquela origem serão selecionados para backup.

Cada **tipo de arquivo** deve conter, no mínimo:

* Nome ou palavra-chave identificadora;
* Extensão ou padrão de extensão, por exemplo `.pdf`, `.png`, `.txt`;
* Tamanho mínimo;
* Tamanho máximo;
* Outras restrições que já existirem no sistema, se aplicável.

Esses tipos devem ser criados em tempo de execução, mantidos em memória e gravados apenas ao finalizar a aplicação, seguindo a regra do projeto.

## Funcionamento esperado

Ao selecionar uma **origem**, a interface deve atualizar automaticamente as abas relacionadas a ela, mostrando:

1. Os tipos de arquivo cadastrados para aquela origem;
2. Os destinos vinculados àquela origem;
3. Quais tipos de arquivo serão enviados para cada destino.

Dessa forma, uma única origem poderá enviar diferentes tipos de arquivo para diferentes destinos.

Exemplo:

```text
Origem: C:/Documentos

Tipo: PDFs
Filtro: arquivos .pdf
Destino: HD Externo

Tipo: Imagens
Filtro: arquivos .png, .jpg
Destino: Google Drive

Tipo: Projetos
Filtro: arquivos com "projeto" no nome
Destino: HD Externo e Pasta Local
```

Assim, a relação correta passa a ser:

```text
Uma origem pode ter vários tipos de arquivo.
Cada tipo de arquivo pode ser enviado para um ou mais destinos.
Cada destino pode escolher quais tipos de arquivo daquela origem ele irá receber.
```

## Mudança na aba de Destinos

Na aba de **Destinos**, deve existir uma opção ou botão para indicar quais **tipos de arquivo** aquele destino pode receber.

Ou seja, ao cadastrar ou editar um destino dentro de uma origem, o usuário deve conseguir selecionar os tipos associados a essa origem.

Exemplo:

```text
Destino: HD Externo
Recebe:
[x] PDFs
[x] Projetos
[ ] Imagens
```

## Mudança na aba de Tipos de Arquivo

A aba de **Tipos de Arquivo** não deve ser global. Ela deve mudar conforme a origem selecionada.

Quando o usuário clicar em uma origem diferente, a aba de tipos deve exibir apenas os tipos cadastrados para aquela origem específica.

Exemplo:

```text
Origem A:
- PDFs
- Imagens

Origem B:
- Vídeos
- Backups compactados
```

Ao selecionar a Origem A, aparecem PDFs e Imagens.
Ao selecionar a Origem B, aparecem Vídeos e Backups compactados.

## Operações de backup

Além da operação atual de copiar/mover, deve ser adicionada a opção de **recortar**.

As operações disponíveis devem ser:

```text
Copiar
Mover
Recortar
```

Também é necessário preparar os casos de erro quando o usuário tentar usar **mover** ou **recortar** para mais de um destino ao mesmo tempo.

Isso é importante porque, diferente de copiar, mover/recortar remove o arquivo da origem. Portanto, não faz sentido mover ou recortar o mesmo arquivo para dois destinos diferentes simultaneamente sem uma regra clara.

## Tratamento de erro necessário

Caso o usuário tente configurar o mesmo tipo de arquivo para ser movido ou recortado para múltiplos destinos, o sistema deve impedir ou alertar.

Exemplo de erro:

```text
Erro: a operação "mover" ou "recortar" não pode ser aplicada ao mesmo conjunto de arquivos para múltiplos destinos, pois os arquivos seriam removidos da origem após o primeiro envio.
```

Possíveis soluções aceitáveis:

1. Bloquear a seleção de múltiplos destinos para tipos configurados como mover/recortar;
2. Permitir múltiplos destinos apenas quando a operação for copiar;
3. Exibir um aviso e exigir que o usuário escolha apenas um destino principal para mover/recortar;
4. Definir internamente que mover/recortar só ocorre depois que todas as cópias forem concluídas, caso essa regra seja implementada explicitamente.

A solução mais segura neste momento é:

```text
Copiar → pode enviar para vários destinos.
Mover/Recortar → só pode enviar para um destino.
```

## Resumo da nova estrutura esperada

A estrutura lógica do app deve ser reorganizada para algo semelhante a:

```text
Origem
 ├── Tipo de Arquivo 1
 │    ├── filtros/restrições
 │    └── destinos permitidos
 │
 ├── Tipo de Arquivo 2
 │    ├── filtros/restrições
 │    └── destinos permitidos
 │
 └── Destinos
      ├── Destino A
      │    └── tipos aceitos
      │
      └── Destino B
           └── tipos aceitos
```

O objetivo final é permitir que cada origem tenha regras próprias de filtragem e que cada destino receba apenas os tipos de arquivo selecionados para ele.

## Operação por destino

A operação de backup não deve ser definida apenas de forma global para a origem ou para o tipo de arquivo. Cada **destino** deve poder solicitar uma operação diferente para os tipos de arquivo que irá receber.

Ou seja, dentro de uma mesma origem, é possível ter vários destinos recebendo arquivos com operações diferentes.

Exemplo:

```text
Origem: C:/Documentos

Tipo: PDFs
Destino: HD Externo
Operação: Copiar

Tipo: Imagens
Destino: Pasta Local
Operação: Mover

Tipo: Projetos
Destino: Backup Temporário
Operação: Recortar
```

A relação correta passa a ser:

```text
Origem → Tipo de Arquivo → Destino → Operação
```

Cada destino deve indicar:

```text
- Quais tipos de arquivo ele recebe;
- Qual operação será aplicada para cada tipo recebido;
- Se a operação é copiar, mover ou recortar.
```

Exemplo na interface:

```text
Destino: HD Externo

Tipos recebidos:
[x] PDFs      Operação: Copiar
[x] Imagens   Operação: Mover
[ ] Vídeos    Operação: -
```

## Regra de conflito para mover/recortar

Como cada destino pode pedir uma operação diferente, o sistema precisa validar conflitos.

A regra recomendada é:

```text
Copiar → pode ser usado em vários destinos ao mesmo tempo.
Mover/Recortar → só pode ser usado por um destino para o mesmo tipo de arquivo.
```

Exemplo inválido:

```text
Tipo: PDFs
Destino A → Mover
Destino B → Recortar
```

Isso deve gerar erro, porque o mesmo conjunto de arquivos não pode ser removido da origem por dois destinos diferentes.

Exemplo válido:

```text
Tipo: PDFs
Destino A → Copiar
Destino B → Copiar
```

Exemplo que só deve ser permitido se houver regra explícita:

```text
Tipo: PDFs
Destino A → Copiar
Destino B → Mover
```

Nesse caso, o sistema precisa garantir que primeiro realiza todas as cópias necessárias e somente depois executa a operação de mover/recortar. Caso essa ordem não esteja implementada com segurança, essa configuração também deve ser bloqueada.

A regra mais segura para a implementação inicial é:

```text
Se um tipo de arquivo estiver configurado como mover ou recortar para algum destino, ele não deve poder ser enviado para outros destinos ao mesmo tempo, a menos que o sistema implemente uma etapa clara de copiar primeiro e remover da origem apenas no final.
```
