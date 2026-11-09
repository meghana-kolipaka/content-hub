// Filters article cards by category without reloading the page.
(function () {
  var chips = document.querySelectorAll('.chip');
  var cards = document.querySelectorAll('#cards li');
  chips.forEach(function (chip) {
    chip.addEventListener('click', function () {
      var cat = chip.getAttribute('data-cat');
      chips.forEach(function (c) { c.classList.toggle('active', c === chip); });
      cards.forEach(function (card) {
        card.hidden = !(cat === 'All' || card.getAttribute('data-cat') === cat);
      });
    });
  });
})();
