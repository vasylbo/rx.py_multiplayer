Bacon = require("baconjs")
createView = require("./viewEffects")

connectToServer = (c) ->
  ws = new WebSocket(c.url)
  messages = Bacon
    .fromEventTarget(ws, 'message', (m) -> JSON.parse(m.data))
  messages.ofType = (tp) ->
    @filter((m) -> m?.t == tp)
      .map(".data")

  messages.log("Server:")
  {messages, ws}


logIn = ({messages, ws}) ->
  user = messages
    .take(1)
    .flatMap((value) ->
      {id, name, ts} = value
      Bacon.combineTemplate({id, name, ws}))

  pingTime = messages
    .filter((m) -> m.t == "pong")
    .map(({ts, lts}) ->
      cts = new Date().getTime()
      console.log(ts - lts, cts - ts, cts - lts)
      {ts, lts, cts})
  pingTime.log("ping: ")

  Bacon.interval(1000).onValue(->
    m = {t:"ping", ts:new Date().getTime()}
    ws.send(JSON.stringify(m))
  )

  newPlayers = messages
    .ofType("new_player")

  updates = messages
    .ofType("up")

  {user, newPlayers, updates}


startGame = (enterFrame, clicks, c) ->
  connection = connectToServer(c)
  {user, newPlayers, updates} = logIn(connection)

  userHero = user
    .sampledBy(newPlayers, (user, hero) -> {user, hero})
    .filter(({user, hero}) -> user.id == hero.id)
    .toProperty()

  view = createView(newPlayers, updates, enterFrame, userHero, c)

  clicks
    .onValue((m) ->
      m.t = "d"
      connection.ws.send(JSON.stringify(m))
    )

  {view}

module.exports = {startGame}