function loadHTML(selector, url) {
    fetch(url)
        .then(response => response.text())
        .then(data => {
            document.querySelector(selector).innerHTML = data;
        })
        .catch(error => console.error('Error loading the HTML:', error));
}

document.addEventListener('DOMContentLoaded', function() {
    loadHTML('#header', 'header.html');
    loadHTML('#footer', 'footer.html');
});