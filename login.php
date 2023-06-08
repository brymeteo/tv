<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $email = $_POST["email"];
    $password = $_POST["password"];

    // Effettua la validazione della password qui

    // Esempio di validazione con password "password123"
    if ($password === "1234") {
        // Reindirizza alla pagina dopo l'autenticazione
        header("Location: streaming/casatv.html");
        exit();
    } else {
        // Password errata, puoi gestire un messaggio di errore qui
        echo "Password errata. Riprova.";
    }
}
?>
