window.fetchSpentPrice = function() {
  clear_notifications();
  $('#fetch').text('fetching...');
  const regExp = /\(([^)]+)\)/;
  const acquired = $('#acquired_amount').val();
  const spentMatches = regExp.exec(
    $('#spent_currency_key')
      .find(`option[value='${$('#spent_currency_key').val()}']`)
      .text(),
  );
  spentCode = spentMatches[1];
  const acquiredMatches = regExp.exec(
    $('#acquired_currency_key')
      .find(`option[value='${$('#acquired_currency_key').val()}']`)
      .text(),
  );
  acquiredCode = acquiredMatches[1];
  const MSEC_IN_SEC = 1000;
  const ts = new Date($('#date').val()).getTime() / MSEC_IN_SEC;

  fetch(
    `/api/v1/crypto/price/historical/?tsym=${spentCode}&fsym=${acquiredCode}&ts=${ts}`,
  )
    .then(resp => resp.json())
    .then(data => {
      const rate = data[`${acquiredCode}${spentCode}`];
      $('#spent_amount').val(acquired * rate);
      $('#fetch').text('fetch');
      show_notification(
        `Spent amount updated with a ${acquiredCode}/${spentCode} : ${rate}${spentCode}`,
        'success',
      );
    })
    .catch(error => {
      $('#fetch').text('fetch');
      show_notification(`Something went wrong. Please try again.`, 'danger');
    });
};

$('#fetch').click(event => {
  event.preventDefault();
  fetchSpentPrice();
});
