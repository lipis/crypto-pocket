$ ->
  init_common()

$ -> $('html.auth').each ->
  init_auth()

$ -> $('html.user-list').each ->
  init_user_list()

$ -> $('html.user-merge').each ->
  init_user_merge()

$ -> $('html.welcome').each ->
  refresh()

$ -> $('html.exchange').each ->
  refresh()


refresh = ->
  console.log('sdf');
  setInterval () =>

    if parseInt($($('time').get(0)).text()) >= 10
      window.location.reload()
  , 1000 * 60 * 5
