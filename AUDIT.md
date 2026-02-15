# Audit Architectural -- Projet Todo App

**Date :** 2026-02-15
**Scope :** audit statique du code source (aucune modification du code)
**Objectif :** diagnostiquer les problèmes d'architecture (couplage, responsabilites, zones a risque)

---

## 1. Vue d'ensemble du projet

| Couche | Fichiers | Role |
|---|---|---|
| Entry point | `src/index.js` | Initialisation Express, routes, DB |
| Routes (HTTP) | `src/routes/addItem.js`, `getItems.js`, `updateItem.js`, `deleteItem.js` | Handlers de requetes |
| Persistence | `src/persistence/index.js`, `sqlite.js`, `mysql.js` | Acces base de donnees |
| Frontend | `src/static/js/app.js` | SPA React (transpilation Babel runtime) |

**Constat general :** il n'existe **aucune couche metier** (service / domain). Les routes appellent directement la persistence. Toute logique metier est dispersee entre les routes et la persistence.

---

## 2. Violations du SRP (Single Responsibility Principle)

### 2.1 Routes = HTTP + logique metier + orchestration DB

Les routes cumulent trois responsabilites : gestion HTTP, logique metier, et orchestration des appels a la persistence.

**Fichier : `src/routes/addItem.js` (lignes 1-13)**

```js
const db = require('../persistence');
const {v4 : uuid} = require('uuid');

module.exports = async (req, res) => {
    const item = {
        id: uuid(),           // <-- logique metier : generation d'identite
        name: req.body.name,  // <-- aucune validation
        completed: false,     // <-- regle metier : "un item est toujours incomplet a la creation"
    };
    await db.storeItem(item); // <-- appel direct persistence
    res.send(item);           // <-- reponse HTTP
};
```

**Problemes :**
- La generation d'UUID est une decision metier (politique d'identite), pas une responsabilite HTTP.
- La regle `completed: false` est une regle metier enfouie dans un handler de route.
- Aucune separation entre "que faire" (use case) et "comment le dire au client" (HTTP).

**Fichier : `src/routes/updateItem.js` (lignes 1-10)**

```js
const db = require('../persistence');

module.exports = async (req, res) => {
    await db.updateItem(req.params.id, {
        name: req.body.name,
        completed: req.body.completed,
    });
    const item = await db.getItem(req.params.id);  // <-- orchestration : update puis re-lecture
    res.send(item);
};
```

**Problemes :**
- Le handler orchestre deux appels DB (update + get). C'est de la logique d'orchestration qui appartient a un service.
- Si demain on veut retourner l'item mis a jour sans re-lecture, il faut modifier le handler HTTP.

**Impact :** impossible de reutiliser la logique metier (ex. creation d'item) sans passer par Express. Si on veut ajouter un CLI, un worker, ou un autre transport, il faut dupliquer toute la logique.

---

### 2.2 Persistence = acces DB + transformation de donnees + filesystem

**Fichier : `src/persistence/sqlite.js` (lignes 40-52)**

```js
async function getItems() {
    return new Promise((acc, rej) => {
        db.all('SELECT * FROM todo_items', (err, rows) => {
            if (err) return rej(err);
            acc(
                rows.map(item =>
                    Object.assign({}, item, {
                        completed: item.completed === 1,  // <-- mapping DB -> domaine
                    }),
                ),
            );
        });
    });
}
```

**Probleme :** la couche persistence fait du mapping de donnees (`1` -> `true`). Ce mapping de representation devrait etre dans un mapper ou dans la couche metier, pas dans le code SQL.

**Fichier : `src/persistence/sqlite.js` (lignes 7-11)**

```js
function init() {
    const dirName = require('path').dirname(location);
    if (!fs.existsSync(dirName)) {
        fs.mkdirSync(dirName, { recursive: true });  // <-- gestion filesystem
    }
```

**Probleme :** la persistence gere aussi la creation de repertoires sur le filesystem. C'est une responsabilite d'infrastructure/deploiement, pas de la couche d'acces aux donnees.

---

## 3. Couplage et dependances dures

### 3.1 Routes couplees directement a la persistence (pas d'injection)

Chaque route fait un `require('../persistence')` en dur :

```js
// src/routes/getItems.js
const db = require('../persistence');
```

```js
// src/routes/addItem.js
const db = require('../persistence');
const {v4 : uuid} = require('uuid');
```

```js
// src/routes/deleteItem.js
const db = require('../persistence');
```

```js
// src/routes/updateItem.js
const db = require('../persistence');
```

**Impact :** aucune injection de dependance. Pour tester les routes, les tests sont obliges d'utiliser `jest.mock()` pour intercepter le `require()` :

```js
// spec/routes/addItem.spec.js
jest.mock('../../src/persistence', () => ({
    removeItem: jest.fn(),
    storeItem: jest.fn(),
    getItem: jest.fn(),
}));
```

C'est un contournement. Avec de l'injection, on passerait simplement un faux `db` en parametre.

---

### 3.2 Couplage direct aux variables d'environnement

Les variables `process.env` sont lues directement dans les modules, sans couche de configuration centralisee.

| Fichier | Variables lues |
|---|---|
| `src/persistence/index.js:1` | `MYSQL_HOST` |
| `src/persistence/sqlite.js:3` | `SQLITE_DB_LOCATION` |
| `src/persistence/mysql.js:5-14` | `MYSQL_HOST`, `MYSQL_HOST_FILE`, `MYSQL_USER`, `MYSQL_USER_FILE`, `MYSQL_PASSWORD`, `MYSQL_PASSWORD_FILE`, `MYSQL_DB`, `MYSQL_DB_FILE` |

**Impact :** la configuration est dispersee dans 3 fichiers. Pas de validation, pas de valeurs par defaut documentees dans un seul endroit, pas de possibilite de passer la config en parametre pour les tests.

---

### 3.3 Selecteur de persistence par effet de bord au require()

**Fichier : `src/persistence/index.js` (lignes 1-2)**

```js
if (process.env.MYSQL_HOST) module.exports = require('./mysql');
else module.exports = require('./sqlite');
```

**Problemes :**
- La decision est prise **une seule fois** au moment du `require()`. Impossible de changer de backend apres le demarrage.
- Les deux modules (`mysql.js` et `sqlite.js`) sont evalues selon l'environnement, ce qui implique que le driver non utilise est tout de meme dans le `node_modules` en production.
- C'est du **service locator** implicite, pas de l'injection de dependance.

---

### 3.4 Dependance dure a `uuid` dans la route

**Fichier : `src/routes/addItem.js:2`**

```js
const {v4 : uuid} = require('uuid');
```

La generation d'identifiant est un choix metier (UUIDv4 aujourd'hui, ULID demain, ID sequentiel en test). Cette dependance devrait etre injectable ou situee dans un service metier.

---

## 4. Duplication de code

### 4.1 sqlite.js et mysql.js : ~80% de code identique

Les deux fichiers de persistence ont une structure quasi identique :

| Fonction | sqlite.js | mysql.js | Identique ? |
|---|---|---|---|
| `init()` | lignes 7-29 | lignes 18-51 | Structure similaire, details differents |
| `teardown()` | lignes 31-38 | lignes 53-60 | Quasi identique |
| `getItems()` | lignes 40-53 | lignes 62-75 | **Identique** (mapping inclus) |
| `getItem()` | lignes 55-68 | lignes 77-90 | **Identique** |
| `storeItem()` | lignes 70-81 | lignes 92-103 | **Identique** |
| `updateItem()` | lignes 83-94 | lignes 105-116 | **Identique** |
| `removeItem()` | lignes 96-103 | lignes 118-125 | **Identique** |

**Impact :** si on ajoute un champ (ex. `priority`), il faut modifier les deux fichiers. Si on oublie un fichier, le bug n'apparait que quand on change de base de donnees. C'est une violation du principe DRY et une source de regressions silencieuses.

---

## 5. Zones a risque

### 5.1 Aucune validation des entrees

**Fichier : `src/routes/addItem.js:7`**
```js
name: req.body.name,   // <-- peut etre undefined, vide, ou un objet
```

**Fichier : `src/routes/updateItem.js:5-6`**
```js
name: req.body.name,
completed: req.body.completed,   // <-- peut etre n'importe quel type
```

**Impact :** un client peut envoyer `{ "name": "" }`, `{ "name": null }`, ou meme `{}`. La valeur sera inseree telle quelle en base. Pas de validation de type, de longueur, ni de presence.

---

### 5.2 Aucune gestion d'erreurs dans les routes

Aucune route n'a de bloc `try/catch` :

```js
// src/routes/addItem.js -- pareil pour les 3 autres
module.exports = async (req, res) => {
    await db.storeItem(item);  // <-- si ca echoue ?
    res.send(item);
};
```

**Impact :** si la base de donnees est inaccessible ou si une requete SQL echoue, Express recevra une **rejection de promesse non geree**. Selon la version d'Express (4.x, pas de support natif des async handlers), cela peut provoquer :
- Un crash du processus (UnhandledPromiseRejection)
- Un timeout cote client (la reponse n'est jamais envoyee)
- Aucun log exploitable

---

### 5.3 Lecture de fichiers secrets sans gestion d'erreurs

**Fichier : `src/persistence/mysql.js` (lignes 19-22)**

```js
const host = HOST_FILE ? fs.readFileSync(HOST_FILE) : HOST;
const user = USER_FILE ? fs.readFileSync(USER_FILE) : USER;
const password = PASSWORD_FILE ? fs.readFileSync(PASSWORD_FILE) : PASSWORD;
const database = DB_FILE ? fs.readFileSync(DB_FILE) : DB;
```

**Impact :** si la variable d'environnement `MYSQL_HOST_FILE` pointe vers un fichier inexistant, `fs.readFileSync()` lance une exception non capturee. L'application crash au demarrage sans message clair.

---

### 5.4 Chemin par defaut fragile

**Fichier : `src/persistence/sqlite.js:3`**

```js
const location = process.env.SQLITE_DB_LOCATION || '/etc/todos/todo.db';
```

**Impact :** `/etc/` est un repertoire systeme generalement protege en ecriture. Sans variable d'environnement, l'application tentera d'ecrire dans `/etc/todos/`, ce qui echouera sur la plupart des systemes sans privileges root.

---

### 5.5 Tests de persistence couples au filesystem

**Fichier : `spec/persistence/sqlite.spec.js` (lignes 11-15)**

```js
beforeEach(() => {
    if (fs.existsSync(location)) {
        fs.unlinkSync(location);
    }
});
```

**Impact :** les tests manipulent de vrais fichiers sur le disque. Pas d'option pour utiliser une base SQLite en memoire (`:memory:`). Les tests sont lents, non isoles, et peuvent echouer selon les permissions du filesystem.

---

### 5.6 Frontend : aucune gestion d'erreurs sur les appels reseau

**Fichier : `src/static/js/app.js` (lignes 17-21)**

```js
React.useEffect(() => {
    fetch('/items')
        .then(r => r.json())
        .then(setItems);
}, []);
```

**Fichier : `src/static/js/app.js` (lignes 79-89)**

```js
fetch('/items', {
    method: 'POST',
    body: JSON.stringify({ name: newItem }),
    headers: { 'Content-Type': 'application/json' },
})
    .then(r => r.json())
    .then(item => { ... });
```

**Impact :** aucun `.catch()` sur les `fetch()`. Si le serveur est down ou retourne une erreur 500, l'application React restera bloquee sur "Loading..." ou echouera silencieusement. L'utilisateur ne verra aucun message d'erreur.

---

## 6. Synthese des problemes

| # | Probleme | Fichiers concernes | Severite |
|---|---|---|---|
| 1 | Pas de couche metier (service/domain) | Toutes les routes | **Haute** |
| 2 | Routes = HTTP + logique metier + persistence | `src/routes/*.js` | **Haute** |
| 3 | Pas d'injection de dependance | `src/routes/*.js`, `src/persistence/index.js` | **Haute** |
| 4 | Duplication massive sqlite.js / mysql.js | `src/persistence/sqlite.js`, `mysql.js` | **Moyenne** |
| 5 | Configuration dispersee (process.env partout) | `src/persistence/*.js` | **Moyenne** |
| 6 | Aucune validation des entrees | `src/routes/addItem.js`, `updateItem.js` | **Haute** |
| 7 | Aucune gestion d'erreurs (routes) | `src/routes/*.js` | **Haute** |
| 8 | Aucune gestion d'erreurs (frontend) | `src/static/js/app.js` | **Moyenne** |
| 9 | Lecture de secrets sans try/catch | `src/persistence/mysql.js` | **Moyenne** |
| 10 | Tests couples au filesystem reel | `spec/persistence/sqlite.spec.js` | **Basse** |
| 11 | Chemin `/etc/todos/` par defaut | `src/persistence/sqlite.js` | **Basse** |

---

## 7. Impacts architecturaux

### "Si on change la base de donnees, tout casse"

- Les routes appellent directement `require('../persistence')`.
- La persistence est selectionnee par un `if` sur `process.env` dans `src/persistence/index.js`.
- Pour ajouter un 3e backend (PostgreSQL, MongoDB...), il faudrait modifier le selecteur **et** dupliquer tout le fichier sqlite/mysql une 3e fois.

### "Impossible de tester le metier sans sqlite"

- Il n'y a pas de couche metier isolee. La logique est dans les routes.
- Les tests de routes fonctionnent grace a `jest.mock()`, mais les tests d'integration avec la DB touchent le vrai filesystem (`spec/persistence/sqlite.spec.js`).
- Pas de possibilite de tester les regles metier (ex. "un item est toujours cree incomplet") sans monter Express ou mocker la persistence.

### "Si on veut ajouter un champ, il faut tout modifier"

- Ajouter un champ (ex. `priority`) implique de modifier :
  - `sqlite.js` (CREATE TABLE, INSERT, UPDATE, SELECT + mapping)
  - `mysql.js` (idem, duplication)
  - La route `addItem.js` (valeur par defaut)
  - La route `updateItem.js` (passage du champ)
  - Le frontend `app.js` (affichage + formulaire)
- Aucune centralisation du modele de donnees (pas de classe `TodoItem`, pas de schema, pas de DTO).

### "Si on veut changer de framework HTTP, tout est a refaire"

- Les routes exportent des fonctions `(req, res) => {}` qui dependent directement de l'API Express.
- La logique metier etant dans ces fonctions, migrer vers Fastify, Koa, ou un autre framework implique de reecrire toute la logique, pas juste l'adaptateur HTTP.

---

## 8. Diagramme de dependances actuel

```
src/index.js
  |-- express (framework)
  |-- src/persistence/index.js
  |     |-- process.env (config)
  |     |-- src/persistence/sqlite.js
  |     |     |-- sqlite3 (driver)
  |     |     |-- fs (filesystem)
  |     |     |-- process.env (config)
  |     |-- src/persistence/mysql.js
  |           |-- mysql2 (driver)
  |           |-- fs (filesystem)
  |           |-- wait-port (infra)
  |           |-- process.env (config)
  |-- src/routes/addItem.js
  |     |-- src/persistence (direct)
  |     |-- uuid (librairie)
  |-- src/routes/getItems.js
  |     |-- src/persistence (direct)
  |-- src/routes/updateItem.js
  |     |-- src/persistence (direct)
  |-- src/routes/deleteItem.js
        |-- src/persistence (direct)
```

**Observation :** toutes les fleches pointent vers le bas (des routes vers la persistence). Il n'y a pas de couche d'abstraction intermediaire. Le couplage est direct a chaque niveau.

---

## 9. Recommandations (pour les etapes suivantes)

1. **Introduire une couche service/use-case** entre les routes et la persistence
2. **Utiliser l'injection de dependance** au lieu de `require()` direct
3. **Centraliser la configuration** dans un module dedie
4. **Factoriser la duplication** sqlite/mysql via un pattern Repository ou Strategy
5. **Ajouter la validation des entrees** (schema validation avec Joi, Zod, ou similaire)
6. **Ajouter la gestion d'erreurs** (middleware Express + try/catch)
7. **Definir un modele de domaine** (`TodoItem`) pour centraliser les regles metier
