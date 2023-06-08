<?php
    $password = "123"; // Imposta la tua password qui
    $message = "";

    if ($_SERVER["REQUEST_METHOD"] == "POST") {
        $enteredPassword = $_POST["password"];

        if ($enteredPassword == $password) {
            // Password corretta, effettua il reindirizzamento alla piattaforma di streaming
            header("Location: streaming/casatv.html");
            exit();
        } else {
            // Password errata, mostra un messaggio di errore
            $message = "Password errata. Accesso negato.";
        }
    }
?>
