# squarecloud-go

Cliente Go não-oficial para a **Square Cloud API**, gerado a partir do `openapi.json` fornecido (67 endpoints).

## Estrutura

```
squarecloud/
  client.go       -> Client (struct central), autenticação, envio/decodificação de requests
  models.go       -> structs de todos os schemas (App, Database, User, Workspace, ...)
  apps.go         -> ciclo de vida de aplicações (criar, start/stop/restart, status, logs, métricas)
  deployments.go  -> commit de arquivos, GitHub App, webhook de deploy, histórico
  envs.go         -> variáveis de ambiente (get/merge/replace/remove)
  files.go        -> gerenciador de arquivos (listar, ler, escrever, renomear, apagar)
  network.go      -> domínio customizado, DNS, cache, analytics, erros, performance, logs de borda
  snapshots.go    -> snapshots de aplicações
  databases.go    -> ciclo de vida, credenciais e snapshots de bancos de dados
  workspaces.go   -> workspaces e membros
  account.go      -> perfil do usuário (/users/me) e snapshots do usuário
  service.go      -> status da plataforma e schema OpenAPI
  realtime.go     -> RECEBE eventos: cliente SSE de /apps/{id}/realtime (logs/status ao vivo)
  webhook.go      -> ENVIA um push simulado para o endpoint público de webhook Git

example/main.go   -> exemplo de uso (enviar requests + receber stream em tempo real)
```

## Uso básico (enviar requisições)

```go
client := squarecloud.NewClient(os.Getenv("SQUARECLOUD_API_KEY"))
ctx := context.Background()

me, err := client.GetMe(ctx)
app, err := client.GetApp(ctx, "abc123def456abc123def456")
err = client.RestartApp(ctx, app.ID)
envs, err := client.MergeAppEnvs(ctx, app.ID, squarecloud.EnvVars{"CHAVE": "valor"})
```

Todo método retorna `*squarecloud.APIError` quando a API responde um erro
(`{"status":"error","code":"...","message":"..."}`), com `HTTPStatus` e `Code`
para tratamento programático:

```go
if err != nil {
    var apiErr *squarecloud.APIError
    if errors.As(err, &apiErr) {
        fmt.Println(apiErr.HTTPStatus, apiErr.Code)
    }
}
```

## Recebendo eventos em tempo real (SSE)

```go
stream, err := client.OpenRealtimeStream(ctx, appID)
defer stream.Close()

for evt := range stream.Events() {
    switch evt.Type {
    case squarecloud.RealtimeStatus:
        fmt.Println("cpu:", evt.Status.CPU, "ram:", evt.Status.RAM)
    case squarecloud.RealtimeLogs:
        fmt.Printf("[%s] %s\n", evt.Log.Stream, evt.Log.Line)
    }
}
```

Os frames "lean" de status (que trazem só os campos que mudaram) já são
mesclados automaticamente com o último frame completo — cada `evt.Status`
entregue no canal está sempre completo.

## Upload de arquivos (multipart)

```go
f, _ := os.Open("app.zip")
defer f.Close()
result, err := client.CreateApp(ctx, "app.zip", f)
```

## Rodando o exemplo

```bash
export SQUARECLOUD_API_KEY="sua-api-key-ou-token-de-sessao"
cd example
go run main.go
```

## Cobertura

Os 67 endpoints do `openapi.json` foram implementados. O pacote foi
verificado com `go build ./...`, `go vet ./...` e `gofmt`.
