 // Definisci l'array dei contenuti del tuo sito con locandine
    var contenuti = [
      {
        titolo: "John Wick 4",
        descrizione: "Azione, Thriller, Crime 2h 49m",
        url: "pagina1.html",
        locandina: "https://www.themoviedb.org/t/p/w1280/dWYBAQwinApRXFWZQcA31ddbaXW.jpg",
        lightbox: true
      },
      {
        titolo: "Contenuto 2",
        descrizione: "Questo è il contenuto 2 del mio sito.",
        url: "pagina2.html",
        locandina: "locandina2.jpg",
        lightbox: false
      },
      {
        titolo: "Contenuto 3",
        descrizione: "Questo è il contenuto 3 del mio sito.",
        url: "pagina3.html",
        locandina: "locandina3.jpg",
        lightbox: true
      }
      // Aggiungi altri contenuti se necessario
    ];

    // Funzione per eseguire la ricerca
    function search() {
      var searchTerm = document.getElementById("search-input").value.toLowerCase();
      var resultsContainer = document.getElementById("search-results");
      resultsContainer.innerHTML = ""; // Cancella i risultati precedenti

      if (searchTerm.length === 0) {
        // Se la barra di ricerca è vuota, esci dalla funzione
        return;
      }

      // Itera sui contenuti e cerca corrispondenze
      for (var i = 0; i < contenuti.length; i++) {
        var contenuto = contenuti[i];
        var titolo = contenuto.titolo.toLowerCase();
        var descrizione = contenuto.descrizione.toLowerCase();

        if (titolo.includes(searchTerm) || descrizione.includes(searchTerm)) {
          // Mostra il risultato nella pagina con locandina
          var resultItem = document.createElement("div");
          resultItem.className = "result-item";

          var image = document.createElement("img");
          image.src = contenuto.locandina;
          image.alt = contenuto.titolo;
          image.className = "result-image";
          resultItem.appendChild(image);

          var details = document.createElement("div");
          details.className = "result-details";

          var titleLink = document.createElement("a");
          titleLink.href = contenuto.url;
          titleLink.textContent = contenuto.titolo;
          titleLink.className = "result-title";
          
          // Check if the link should open in a lightbox
          if (contenuto.lightbox) {
           
            titleLink.setAttribute("data-lity", "");
          }
          
          details.appendChild(titleLink);

          var description = document.createElement("p");
          description.textContent = contenuto.descrizione;
          description.className = "result-description";
          details.appendChild(description);

          resultItem.appendChild(details);
          resultsContainer.appendChild(resultItem);
        }
      }
      
      // Attach the click event handler for lightbox links
      var lightboxLinks = document.getElementsByClassName("lightbox-link");
      for (var j = 0; j < lightboxLinks.length; j++) {
        lightboxLinks[j].addEventListener("click", function(event) {
          event.preventDefault();
          var url = this.getAttribute("href");
          lity(url);
        });
      }
    }
