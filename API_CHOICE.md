# API Choice

- Étudiant : Tom Merlin Carlier
- API choisie : Frankfurter API
- URL base : https://api.frankfurter.dev/v2
- Documentation officielle / README : https://frankfurter.dev/
- Auth : None

## Endpoints testés

- GET /rates?base=EUR&quotes=USD,GBP
- GET /rate/EUR/USD
- GET /currencies
- GET /rates?date=2024-01-15&base=EUR&quotes=USD
- GET /rate/EUR/XXX

## Hypothèses de contrat

### GET /rates

Réponse attendue :
- Code HTTP 200
- Content-Type JSON
- Corps JSON sous forme de liste
- Chaque objet contient :
  - date : string
  - base : string
  - quote : string
  - rate : number positif

### GET /rate/EUR/USD

Réponse attendue :
- Code HTTP 200
- base = EUR
- quote = USD
- rate = nombre positif

### GET /currencies

Réponse attendue :
- Code HTTP 200
- Liste de devises
- Présence de EUR et USD
- Chaque devise contient au minimum iso_code et name

### Devise invalide

Pour /rate/EUR/XXX :
- Code attendu : 404 ou 422
- Réponse JSON contenant un champ message

## Limites / rate limiting connu

L'API ne demande pas de clé API. Elle peut cependant limiter les requêtes en cas d'abus.  
La solution limite donc le nombre de requêtes à moins de 20 par run.

## Risques

- Indisponibilité temporaire de l'API
- Latence réseau variable
- Changement futur du contrat JSON
- Rate limiting HTTP 429 si trop de requêtes sont envoyées