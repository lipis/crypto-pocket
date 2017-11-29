window.fetchSpentPrice = function() {
  clear_notifications();
  $('#fetch').text('fetching...');
  var regExp = /\(([^)]+)\)/;
  var acquired = $('#acquired_amount').val();
  var spentMatches = regExp.exec(
    $('#spent_currency_key')
      .find(`option[value='${$('#spent_currency_key').val()}']`)
      .text(),
  );
  spentCode = spentMatches[1];
  var acquiredMatches = regExp.exec(
    $('#acquired_currency_key')
      .find(`option[value='${$('#acquired_currency_key').val()}']`)
      .text(),
  );
  acquiredCode = acquiredMatches[1];
  var ts = new Date($('#date').val()).getTime() / 1000;

  fetch(`/api/v1/crypto/price/historical/?tsym=${spentCode}&fsym=${acquiredCode}&ts=${ts}`)
    .then(resp => resp.json())
    .then(function(data) {
      var rate = data[`${acquiredCode}${spentCode}`];
      $('#spent_amount').val(acquired * rate);
      $('#fetch').text('fetch');
      show_notification(`Spent amount updated with a ${acquiredCode}/${spentCode} : ${rate}${spentCode}`, 'success');
    })
    .catch(function(error) {
      $('#fetch').text('fetch');
      show_notification(`Something went wrong. Please try again.`, 'danger');
    });
};


$('#fetch').click(event => {
  event.preventDefault();
  fetchSpentPrice();
});
