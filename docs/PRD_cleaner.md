# PRD — HTML Cleaner Opcional para Foxcape

## 1. Objetivo

Adicionar ao Foxcape uma funcionalidade opcional de limpeza do HTML renderizado após a DOM estar pronta.

A funcionalidade deve permitir remover elementos de publicidade, widgets de recomendação, overlays e banners de consentimento, entregando um HTML final mais limpo para etapas posteriores de extração e processamento.

A funcionalidade deve ser totalmente opcional e não alterar o comportamento atual quando não utilizada.

---

# 2. Escopo

## 2.1 Entrada

Adicionar um parâmetro opcional de configuração:

```
clean_html=True
```

ou equivalente.

Comportamento esperado:

* Parâmetro ausente:

  * mantém comportamento atual.
  * nenhum processamento adicional é executado.

* Parâmetro habilitado:

  * aplica o HTML Cleaner após a página estar renderizada.
  * retorna o HTML limpo.

---

# 3. Fluxo de execução

Fluxo esperado:

```
URL
 ↓
Camoufox
 ↓
Página renderizada
 ↓
DOM pronta
 ↓
HTML Cleaner opcional
 ↓
HTML final limpo
 ↓
Processamento existente
```

O cleaner deve atuar somente após a execução de JavaScript e geração da DOM final.

---

# 4. Arquitetura

Criar um componente isolado de limpeza HTML.

Estrutura conceitual:

```
foxcape/
  cleaner/
      cleaner.py
      rules.py
```

Responsabilidades:

## HTML Cleaner

Responsável por:

* receber HTML renderizado.
* aplicar regras de limpeza.
* retornar HTML serializado.

## Rules

Responsável por manter fingerprints utilizados para identificar elementos removíveis.

---

# 5. Pipeline do Cleaner

Ordem de execução:

1. Parse do HTML/DOM.
2. Remoção de scripts conhecidos de publicidade.
3. Remoção de iframes relacionados a publicidade.
4. Remoção de componentes conhecidos de publicidade.
5. Remoção de widgets de recomendação.
6. Remoção de banners LGPD/cookie consent.
7. Remoção conservadora de overlays suspeitos.
8. Serialização do HTML final.

---

# 6. Regras de limpeza

## 6.1 Google Adsense e publicidade

## Objetivo

Remover elementos relacionados a publicidade Google Adsense e redes associadas.

## Estratégia

Remover elementos DOM contendo:

Classes, IDs ou atributos:

* adsbygoogle
* google-auto-placed
* google_ads
* ad-container
* ad-slot

Remover scripts contendo:

* adsbygoogle.js
* googlesyndication
* doubleclick.net

Remover iframes contendo:

* googleads
* doubleclick
* googlesyndication

---

# 6.2 Outbrain

## Objetivo

Remover widgets de recomendação Outbrain.

## Estratégia

Remover elementos contendo:

* outbrain
* OUTBRAIN

Remover scripts contendo:

* widgets.outbrain.com

---

# 6.3 Taboola

## Objetivo

Remover widgets de recomendação Taboola.

## Estratégia

Remover elementos contendo:

* taboola
* taboola-below-article
* taboola-mid-article

Remover scripts contendo:

* trc.taboola.com
* taboola.com

---

# 6.4 RevContent

## Objetivo

Remover widgets de recomendação RevContent.

## Estratégia

Remover elementos contendo:

* revcontent
* rc-widget

Remover scripts contendo:

* revcontent.com

---

# 6.5 Cookie Banner / LGPD

## Objetivo

Remover banners de consentimento e componentes CMP.

## Estratégia

Remover elementos contendo:

Classes ou IDs:

* cookie
* cookies
* consent
* gdpr
* privacy
* cmp
* cc-window
* cookie-banner
* cookie-consent
* onetrust

Remover scripts relacionados a:

* onetrust
* cookiebot
* quantcast

---

# 6.6 Overlay

## Objetivo

Remover overlays que bloqueiam ou poluem o conteúdo principal.

## Estratégia

Aplicar regras conservadoras.

Remover elementos quando combinarem:

* `position: fixed`
* z-index elevado
* grande ocupação da tela

Critérios:

* largura maior que aproximadamente 70% da viewport.
* altura maior que aproximadamente 30% da viewport.

Também considerar classes ou IDs suspeitos:

* modal
* popup
* overlay
* interstitial
* sticky
* floating
* drawer
* lightbox

Não remover qualquer elemento apenas por possuir nome de modal.

A remoção deve depender da combinação de características.

---

# 7. Decisões técnicas

## Não utilizar

A implementação não deve utilizar:

* Machine Learning para classificação.
* LLM para decidir remoção.
* Bloqueio de requests no navegador.
* Alteração do comportamento do Camoufox.
* Listas completas de AdBlock.

---

# 8. Dependências

Utilizar as dependências existentes do projeto.

Não adicionar nova biblioteca inicialmente.

A implementação deve utilizar:

* BeautifulSoup
* lxml

---

# 9. Critérios de aceite

## Funcionalidade opcional

* Sem `clean_html`, o comportamento permanece exatamente igual.
* Com `clean_html`, o HTML retornado passa pelo cleaner.

## Publicidade

Deve remover:

* Google Adsense.
* Elementos conhecidos de publicidade.
* Scripts relacionados.

## Widgets externos

Deve remover:

* Outbrain.
* Taboola.
* RevContent.

## LGPD

Deve remover:

* Cookie banners.
* CMPs conhecidos.

## Overlay

Deve remover overlays identificados por combinação de:

* posição fixa.
* z-index alto.
* grande área ocupada.

## Segurança

Não deve remover conteúdo principal apenas por heurística isolada.

---

# 10. Fora de escopo

Não faz parte desta implementação:

* Identificação inteligente de anúncios desconhecidos.
* Classificação semântica do conteúdo.
* Uso de IA.
* Bloqueio preventivo durante carregamento.
* Alteração do fluxo de navegação.
* Remoção baseada em análise do texto da página.

---

# 11. Resultado esperado

Com o cleaner habilitado, o Foxcape deve retornar um HTML renderizado reduzido de ruídos comuns de páginas web, removendo publicidade, widgets comerciais, banners LGPD e overlays sem alterar o comportamento padrão da biblioteca quando a funcionalidade não for utilizada.
