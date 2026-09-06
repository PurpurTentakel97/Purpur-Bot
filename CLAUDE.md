# Grundregeln

1. Keine schreibenden Git-Operationen (auch kein Staging).
2. Kein Feature Creep. Wir machen nur das, was wir besprochen haben, oder fragen nach.
3. Wir arbeiten stets nach den Best Practices.
4. Nachfragen, wenn du dir nicht sicher bist.
5. Es werden ausschließlich uv-Commands ausgeführt.
6. Es werden keine Commands ohne Nachfrage ausgeführt.
7. Immer in die README schauen.
8. Am Ende sind – nach Nachfrage – die folgenden Commands auszuführen:
   - `uv run poe fix`
   - `uv run poe check`
   - `uv run poe test`
9. Wir nutzen Type Annotations. Funktions-Signaturen (Parameter und Rückgabewert)
   werden immer annotiert. Lokale Variablen nur dann, wenn der Typ sonst nicht
   eindeutig ableitbar ist.
10. Bei `Result`-Objekten wird immer sowohl `Result.state` als auch `Result.value`
    explizit geprüft – nie nur eines von beiden. Normalerweise sind die beiden
    kohärent, das ist aber nicht garantiert.
